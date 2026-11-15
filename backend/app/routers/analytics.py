from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import (
    NAMED_SQL_QUERIES,
    execute_named_sql_query,
    get_cohort_retention,
    get_funnel_analytics,
    get_overview_metrics,
    get_search_intelligence,
)

router = APIRouter(prefix="/api/analytics", tags=["Product Manager Analytics"])


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db)):
    return get_overview_metrics(db)


@router.get("/funnel")
def analytics_funnel(
    device_type: Optional[str] = Query(default="all"),
    acquisition_channel: Optional[str] = Query(default="all"),
    experiment_variant: Optional[str] = Query(default="all"),
    db: Session = Depends(get_db),
):
    return get_funnel_analytics(
        db=db,
        device_type=device_type,
        acquisition_channel=acquisition_channel,
        experiment_variant=experiment_variant,
    )


@router.get("/cohorts")
def analytics_cohorts(db: Session = Depends(get_db)):
    return {"cohorts": get_cohort_retention(db)}


@router.get("/search-intelligence")
def analytics_search_intelligence(db: Session = Depends(get_db)):
    return get_search_intelligence(db)


@router.get("/sql-queries")
def list_and_run_sql_queries(
    query_key: str = Query(default="conversion_funnel"),
    db: Session = Depends(get_db),
):
    try:
        active_result = execute_named_sql_query(db, query_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    catalog = [
        {"key": k, "title": v["title"], "description": v["description"]}
        for k, v in NAMED_SQL_QUERIES.items()
    ]
    return {
        "available_queries": catalog,
        "active_query": active_result,
    }


@router.get("/tableau-views")
def inspect_tableau_views(
    view_name: str = Query(default="vw_tableau_daily_funnel"),
    db: Session = Depends(get_db),
):
    allowed_views = {
        "vw_tableau_daily_funnel": "Daily session funnel & conversion breakdown by device, channel, and variant.",
        "vw_tableau_search_intelligence": "Query-level volume, CTR, zero-result rate, and search-to-order conversion.",
        "vw_tableau_category_merchandising": "SKU & category gross revenue, PDP views, Add-to-Carts, and return rates.",
        "vw_tableau_feedback_intelligence": "Customer review sentiment, complaint taxonomy, and buyer fit consensus.",
    }
    if view_name not in allowed_views:
        raise HTTPException(status_code=400, detail="Invalid Tableau SQL view name")

    rows = db.execute(text(f"SELECT * FROM {view_name} LIMIT 50")).mappings().all()
    data = [dict(r) for r in rows]
    columns = list(data[0].keys()) if data else []

    return {
        "view_name": view_name,
        "description": allowed_views[view_name],
        "available_views": [{"name": k, "description": d} for k, d in allowed_views.items()],
        "columns": columns,
        "row_count": len(data),
        "rows": data,
    }
