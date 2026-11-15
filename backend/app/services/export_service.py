import csv
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Product, Review, RoadmapItem, User
from app.services.analytics_service import (
    get_cohort_retention,
    get_funnel_analytics,
    get_overview_metrics,
    get_search_intelligence,
)
from app.services.experiment_service import list_experiments_with_stats


def _rows_to_csv_bytes(headers: List[str], rows: List[List[Any]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for r in rows:
        writer.writerow(r)
    return buf.getvalue().encode("utf-8-sig")


def _sheets_to_xlsx_bytes(sheets: List[Tuple[str, List[str], List[List[Any]]]]) -> bytes:
    wb = Workbook()
    # remove default sheet
    default_ws = wb.active
    wb.remove(default_ws)

    header_fill = PatternFill(start_color="181615", end_color="181615", fill_type="solid")
    header_font = Font(color="FAF8F5", bold=True, name="Calibri", size=11)

    for sheet_title, headers, rows in sheets:
        ws = wb.create_sheet(title=sheet_title[:31])
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="left", vertical="center")

        for r in rows:
            ws.append(r)

        # Auto-fit column widths
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=12)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 55)

    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def generate_dataset_export(db: Session, dataset: str, fmt: str = "xlsx") -> Tuple[bytes, str, str]:
    """
    Returns (file_bytes, media_type, filename) for dataset in ('kpi_report', 'customer_feedback',
    'search_analysis', 'experiment_template', 'jira_backlog', 'tableau_funnel', 'tableau_merchandising').
    """
    fmt_clean = fmt.lower().strip()
    is_xlsx = fmt_clean == "xlsx"

    if dataset == "kpi_report":
        overview = get_overview_metrics(db)
        funnel = get_funnel_analytics(db)
        cohorts = get_cohort_retention(db)

        kpi_headers = ["Metric Key", "Value"]
        kpi_rows = [[k, v] for k, v in overview["kpis"].items()]

        funnel_headers = [
            "Step Label",
            "Canonical Event",
            "Sessions",
            "Conversion from Top (%)",
            "Step-to-Step Conversion (%)",
            "Drop-Off (%)",
        ]
        funnel_rows = [
            [
                s["step_label"],
                s["event_name"],
                s["sessions"],
                s["conversion_from_top_pct"],
                s["step_to_step_conversion_pct"],
                s["drop_off_pct"],
            ]
            for s in funnel["steps"]
        ]

        cohort_headers = ["Cohort Month", "Cohort Size", "M0 (%)", "M1 (%)", "M2 (%)", "M3 (%)", "M4 (%)"]
        cohort_rows = [
            [
                c["cohort_month"],
                c["cohort_size"],
                c["retention"].get("M0", ""),
                c["retention"].get("M1", ""),
                c["retention"].get("M2", ""),
                c["retention"].get("M3", ""),
                c["retention"].get("M4", ""),
            ]
            for c in cohorts
        ]

        if is_xlsx:
            data = _sheets_to_xlsx_bytes(
                [
                    ("Executive KPIs", kpi_headers, kpi_rows),
                    ("Conversion Funnel", funnel_headers, funnel_rows),
                    ("Cohort Retention", cohort_headers, cohort_rows),
                ]
            )
            return (
                data,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_KPI_and_Funnel_Report.xlsx",
            )
        else:
            data = _rows_to_csv_bytes(funnel_headers, funnel_rows)
            return data, "text/csv", "THREADLINE_KPI_and_Funnel_Report.csv"

    elif dataset == "customer_feedback":
        revs = db.query(Review).order_by(Review.created_at.desc()).all()
        headers = [
            "Review ID",
            "Date",
            "SKU",
            "Product Title",
            "Category",
            "Customer Name",
            "Persona Segment",
            "Rating",
            "Sentiment",
            "Complaint Category",
            "Fit Feedback",
            "Review Title",
            "Comment Text",
            "Verified Purchase",
        ]
        rows = [
            [
                r.id,
                r.created_at.strftime("%Y-%m-%d"),
                r.product.sku if r.product else "",
                r.product.title if r.product else "",
                r.product.category.name if (r.product and r.product.category) else "",
                r.user.full_name if r.user else "",
                r.user.persona_segment if r.user else "",
                r.rating,
                r.sentiment,
                r.complaint_category,
                r.fit_feedback,
                r.title,
                r.comment_text,
                "Yes" if r.verified_purchase else "No",
            ]
            for r in revs
        ]
        if is_xlsx:
            return (
                _sheets_to_xlsx_bytes([("Customer Feedback Log", headers, rows)]),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_Customer_Feedback_Intelligence.xlsx",
            )
        return _rows_to_csv_bytes(headers, rows), "text/csv", "THREADLINE_Customer_Feedback_Intelligence.csv"

    elif dataset == "search_analysis":
        si = get_search_intelligence(db)
        headers = [
            "Normalized Query",
            "Search Volume",
            "Avg Results Returned",
            "Zero-Result Hits",
            "Clicked Searches",
            "Abandoned Searches",
            "Bag Conversions",
            "Order Conversions",
            "Search CTR (%)",
            "Abandonment Rate (%)",
            "Search-to-Order CVR (%)",
        ]
        rows = [
            [
                q["query"],
                q["volume"],
                q["avg_results"],
                q["zero_result_hits"],
                q["clicks"],
                q["abandoned"],
                q["bag_conversions"],
                q["order_conversions"],
                q["ctr_pct"],
                q["abandonment_pct"],
                q["order_cvr_pct"],
            ]
            for q in si["top_queries"]
        ]
        if is_xlsx:
            return (
                _sheets_to_xlsx_bytes([("Search Query Intelligence", headers, rows)]),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_Search_Intelligence_Report.xlsx",
            )
        return _rows_to_csv_bytes(headers, rows), "text/csv", "THREADLINE_Search_Intelligence_Report.csv"

    elif dataset == "experiment_template":
        exps = list_experiments_with_stats(db)
        headers = [
            "Experiment Key",
            "Experiment Name",
            "Status",
            "Hypothesis",
            "Primary Metric",
            "Control Users",
            "Treatment Users",
            "Target Sample Size",
            "Control Rate (%)",
            "Treatment Rate (%)",
            "Relative Lift (%)",
            "95% CI Low (%)",
            "95% CI High (%)",
            "Z-Score",
            "P-Value",
            "Statistical Classification",
            "Owner",
        ]
        rows = []
        for e in exps:
            pm = e["primary_metric_summary"]
            rows.append(
                [
                    e["key"],
                    e["name"],
                    e["status"],
                    e["hypothesis"],
                    e["primary_metric"],
                    e["sample_sizes"]["control_users"],
                    e["sample_sizes"]["treatment_users"],
                    e["target_sample_size"],
                    pm["control_rate_pct"],
                    pm["treatment_rate_pct"],
                    pm["relative_lift_pct"],
                    pm["ci_95_low_pct"],
                    pm["ci_95_high_pct"],
                    pm["z_score"],
                    pm["p_value"],
                    e["decision_classification"],
                    e["owner"],
                ]
            )
        if is_xlsx:
            return (
                _sheets_to_xlsx_bytes([("Experimentation Tracker", headers, rows)]),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_Experiment_Tracking_Template.xlsx",
            )
        return _rows_to_csv_bytes(headers, rows), "text/csv", "THREADLINE_Experiment_Tracking_Template.csv"

    elif dataset == "jira_backlog":
        items = db.query(RoadmapItem).order_by(RoadmapItem.rice_score.desc()).all()
        headers = [
            "Issue Type",
            "Issue Key",
            "Epoch / Epic Name",
            "Summary",
            "Description (User Story & Problem Evidence)",
            "Acceptance Criteria",
            "RICE Reach",
            "RICE Impact",
            "RICE Confidence (%)",
            "Effort (Person-Weeks)",
            "RICE Priority Score",
            "Priority",
            "Status",
            "Sprint",
            "Assignee",
        ]
        rows = []
        for it in items:
            ac_list = json.loads(it.acceptance_criteria_json)
            ac_formatted = " | ".join(f"{i+1}. {c}" for i, c in enumerate(ac_list))
            rows.append(
                [
                    "Story",
                    it.jira_key,
                    it.epic_name,
                    it.title,
                    f"User Story: {it.user_story}\n\nEvidence: {it.problem_evidence}\n\nBusiness Impact: {it.business_impact}",
                    ac_formatted,
                    it.reach_score,
                    it.impact_score,
                    it.confidence_pct,
                    it.effort_person_weeks,
                    it.rice_score,
                    it.customer_impact,
                    it.status,
                    it.sprint,
                    it.owner,
                ]
            )
        if is_xlsx:
            return (
                _sheets_to_xlsx_bytes([("Jira Backlog Import", headers, rows)]),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_Jira_Backlog_RICE.xlsx",
            )
        return _rows_to_csv_bytes(headers, rows), "text/csv", "THREADLINE_Jira_Backlog_Import.csv"

    elif dataset == "tableau_extract":
        funnel_vw = db.execute(text("SELECT * FROM vw_tableau_daily_funnel")).mappings().all()
        search_vw = db.execute(text("SELECT * FROM vw_tableau_search_intelligence")).mappings().all()
        merch_vw = db.execute(text("SELECT * FROM vw_tableau_category_merchandising")).mappings().all()
        fb_vw = db.execute(text("SELECT * FROM vw_tableau_feedback_intelligence")).mappings().all()

        def _extract_to_sheet(title: str, mapping_rows: list) -> Tuple[str, List[str], List[List[Any]]]:
            if not mapping_rows:
                return title, ["Empty"], []
            cols = list(mapping_rows[0].keys())
            r_list = [[row[c] for c in cols] for row in mapping_rows]
            return title, cols, r_list

        sheets = [
            _extract_to_sheet("vw_daily_funnel", funnel_vw),
            _extract_to_sheet("vw_search_intelligence", search_vw),
            _extract_to_sheet("vw_category_merchandising", merch_vw),
            _extract_to_sheet("vw_feedback_intelligence", fb_vw),
        ]
        if is_xlsx:
            return (
                _sheets_to_xlsx_bytes(sheets),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "THREADLINE_Tableau_BI_Extracts.xlsx",
            )
        _, cols, r_list = sheets[0]
        return _rows_to_csv_bytes(cols, r_list), "text/csv", "THREADLINE_Tableau_Daily_Funnel_Extract.csv"

    raise ValueError(f"Unsupported export dataset: {dataset}")


def import_research_feedback_file(db: Session, filename: str, content: bytes) -> Dict[str, Any]:
    """
    Import structured customer research / feedback rows from CSV or XLSX into `reviews`.
    Expected columns (case-insensitive flexible matching):
    product_id or sku, rating, title, comment_text, complaint_category, fit_feedback
    """
    rows_dicts: List[Dict[str, Any]] = []
    fname_lower = (filename or "").lower()

    if fname_lower.endswith(".xlsx"):
        wb = load_workbook(io.BytesIO(content), data_only=True)
        ws = wb.active
        all_rows = list(ws.iter_rows(values_only=True))
        if len(all_rows) < 2:
            raise ValueError("Uploaded XLSX file must contain a header row and at least one data row.")
        headers = [str(h or "").strip().lower() for h in all_rows[0]]
        for r in all_rows[1:]:
            if not any(r):
                continue
            rows_dicts.append({headers[i]: r[i] for i in range(min(len(headers), len(r)))})
    else:
        text_content = content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(text_content))
        for r in reader:
            rows_dicts.append({(k or "").strip().lower(): v for k, v in r.items()})

    products_by_sku = {p.sku.lower(): p for p in db.query(Product).all()}
    products_by_id = {p.id.lower(): p for p in db.query(Product).all()}
    default_product = db.query(Product).first()
    default_user = db.query(User).first()

    imported_ids = []
    for item in rows_dicts:
        prod_ref = str(item.get("product_id") or item.get("sku") or "prd_001").strip().lower()
        prod_obj = products_by_id.get(prod_ref) or products_by_sku.get(prod_ref) or default_product

        try:
            rating = int(float(item.get("rating") or 3))
        except Exception:
            rating = 3
        rating = max(1, min(5, rating))

        sentiment = str(item.get("sentiment") or "").strip().lower()
        if sentiment not in ("positive", "neutral", "negative"):
            sentiment = "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")

        title = str(item.get("title") or item.get("review title") or "Imported Customer Research Note").strip()
        comment = str(
            item.get("comment_text")
            or item.get("comment")
            or item.get("feedback")
            or "Structured research feedback imported via PM Workspace."
        ).strip()
        complaint_cat = str(
            item.get("complaint_category") or item.get("complaint category") or "Size and fit"
        ).strip()
        fit_fb = str(item.get("fit_feedback") or item.get("fit feedback") or "True to Size").strip()

        new_rev = Review(
            id=f"rev_imp_{uuid.uuid4().hex[:7]}",
            product_id=prod_obj.id,
            user_id=default_user.id if default_user else "usr_demo_001",
            order_id=None,
            rating=rating,
            title=title[:200],
            comment_text=comment,
            sentiment=sentiment,
            complaint_category=complaint_cat,
            fit_feedback=fit_fb,
            verified_purchase=True,
            helpful_votes=1,
            created_at=datetime.utcnow(),
        )
        db.add(new_rev)
        imported_ids.append(new_rev.id)

    db.commit()
    return {
        "status": "imported",
        "filename": filename,
        "rows_imported": len(imported_ids),
        "sample_review_ids": imported_ids[:5],
    }


def write_deliverable_extracts_to_disk(db: Session) -> None:
    """Materialize Tableau CSV/XLSX extracts and Jira CSV import file into deliverables/."""
    project_root = Path(__file__).resolve().parent.parent.parent
    tableau_dir = project_root / "deliverables" / "tableau" / "extracts"
    jira_dir = project_root / "deliverables" / "jira"
    tableau_dir.mkdir(parents=True, exist_ok=True)
    jira_dir.mkdir(parents=True, exist_ok=True)

    # 1. Jira CSV & XLSX
    jira_csv_bytes, _, _ = generate_dataset_export(db, "jira_backlog", "csv")
    (jira_dir / "jira_backlog_import.csv").write_bytes(jira_csv_bytes)

    # 2. Tableau Views CSVs & Multi-tab XLSX
    tableau_xlsx_bytes, _, _ = generate_dataset_export(db, "tableau_extract", "xlsx")
    (tableau_dir / "THREADLINE_Tableau_BI_Extracts.xlsx").write_bytes(tableau_xlsx_bytes)

    views = [
        ("vw_tableau_daily_funnel", "vw_tableau_daily_funnel.csv"),
        ("vw_tableau_search_intelligence", "vw_tableau_search_intelligence.csv"),
        ("vw_tableau_category_merchandising", "vw_tableau_category_merchandising.csv"),
        ("vw_tableau_feedback_intelligence", "vw_tableau_feedback_intelligence.csv"),
    ]
    for view_name, file_name in views:
        rows = db.execute(text(f"SELECT * FROM {view_name}")).mappings().all()
        if rows:
            cols = list(rows[0].keys())
            r_data = [[r[c] for c in cols] for r in rows]
            (tableau_dir / file_name).write_bytes(_rows_to_csv_bytes(cols, r_data))
