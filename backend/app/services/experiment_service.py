import hashlib
import json
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.models import Experiment, ExperimentAssignment
from app.schemas import ExperimentCreateRequest
from app.services.analytics_service import ensure_user_and_session


def deterministic_variant_for_user(experiment_key: str, user_id: str) -> str:
    """
    Deterministic SHA-256 hashing so a user always receives a consistent variant
    for a given experiment across sessions and devices.
    """
    digest = hashlib.sha256(f"{experiment_key}:{user_id}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 100
    return "treatment" if bucket < 50 else "control"


def _two_proportion_z_test(succ_c: int, n_c: int, succ_t: int, n_t: int) -> Dict[str, Any]:
    if n_c == 0 or n_t == 0:
        return {
            "control_rate_pct": 0.0,
            "treatment_rate_pct": 0.0,
            "absolute_lift_pct": 0.0,
            "relative_lift_pct": 0.0,
            "z_score": 0.0,
            "p_value": 1.0,
            "ci_95_low_pct": 0.0,
            "ci_95_high_pct": 0.0,
            "statistically_significant": False,
        }

    p_c = succ_c / n_c
    p_t = succ_t / n_t
    diff = p_t - p_c
    rel_lift = ((p_t - p_c) / p_c * 100.0) if p_c > 0 else 0.0

    # Pooled proportion for Z-score
    p_pool = (succ_c + succ_t) / (n_c + n_t)
    se_pool = math.sqrt(max(1e-12, p_pool * (1.0 - p_pool) * (1.0 / n_c + 1.0 / n_t)))
    z_score = diff / se_pool if se_pool > 1e-9 else 0.0
    p_value = math.erfc(abs(z_score) / math.sqrt(2.0))

    # Unpooled standard error for 95% confidence interval of difference
    se_unpooled = math.sqrt(max(1e-12, (p_c * (1.0 - p_c) / n_c) + (p_t * (1.0 - p_t) / n_t)))
    ci_low = (diff - 1.96 * se_unpooled) * 100.0
    ci_high = (diff + 1.96 * se_unpooled) * 100.0

    return {
        "control_conversions": succ_c,
        "treatment_conversions": succ_t,
        "control_rate_pct": round(p_c * 100.0, 2),
        "treatment_rate_pct": round(p_t * 100.0, 2),
        "absolute_lift_pct": round(diff * 100.0, 2),
        "relative_lift_pct": round(rel_lift, 1),
        "z_score": round(z_score, 2),
        "p_value": round(p_value, 4),
        "ci_95_low_pct": round(ci_low, 2),
        "ci_95_high_pct": round(ci_high, 2),
        "statistically_significant": p_value < 0.05,
    }


def evaluate_experiment(db: Session, exp: Experiment) -> Dict[str, Any]:
    assignments = (
        db.query(ExperimentAssignment)
        .filter(ExperimentAssignment.experiment_id == exp.id)
        .all()
    )
    control_rows = [a for a in assignments if a.variant == "control"]
    treatment_rows = [a for a in assignments if a.variant == "treatment"]

    n_c = len(control_rows)
    n_t = len(treatment_rows)
    total_exposed = n_c + n_t

    metrics_spec = [
        ("search_ctr", "Search Click-Through Rate (CTR)", lambda r: bool(r.search_clicked)),
        ("product_view_rate", "Product Detail View Rate", lambda r: bool(r.product_viewed)),
        ("add_to_cart_rate", "Add-to-Bag Conversion Rate", lambda r: bool(r.added_to_cart)),
        ("purchase_conversion", "Order Purchase Conversion Rate", lambda r: bool(r.order_completed)),
    ]

    metrics_analysis = {}
    for m_key, m_label, predicate in metrics_spec:
        succ_c = sum(1 for r in control_rows if predicate(r))
        succ_t = sum(1 for r in treatment_rows if predicate(r))
        stats = _two_proportion_z_test(succ_c, n_c, succ_t, n_t)
        stats["metric_key"] = m_key
        stats["metric_label"] = m_label
        stats["is_primary"] = m_key == exp.primary_metric
        metrics_analysis[m_key] = stats

    primary_stats = metrics_analysis.get(exp.primary_metric) or metrics_analysis["add_to_cart_rate"]
    sample_adequacy_pct = round(100.0 * total_exposed / max(1, exp.target_sample_size), 1)
    is_adequately_powered = total_exposed >= exp.target_sample_size

    if not is_adequately_powered:
        decision_badge = "Exploratory — Under-Powered Sample Size"
        decision_recommendation = (
            f"Current exposure ({total_exposed} users) is below the required target sample size "
            f"({exp.target_sample_size} users, {sample_adequacy_pct}% complete). Treat observed lift "
            f"({primary_stats['relative_lift_pct']:+.1f}%) as directional/exploratory only; continue running."
        )
    elif primary_stats["statistically_significant"] and primary_stats["absolute_lift_pct"] > 0:
        decision_badge = "Statistically Supported Winner (p < 0.05)"
        decision_recommendation = (
            f"Treatment outperforms Control on primary metric ({exp.primary_metric}) by "
            f"{primary_stats['relative_lift_pct']:+.1f}% relative lift (p = {primary_stats['p_value']}, "
            f"95% CI [{primary_stats['ci_95_low_pct']:+.2f}%, {primary_stats['ci_95_high_pct']:+.2f}%]). "
            f"Recommend 100% production rollout."
        )
    else:
        decision_badge = "Inconclusive — Null Hypothesis Not Rejected"
        decision_recommendation = (
            f"Observed difference on {exp.primary_metric} has p = {primary_stats['p_value']} (>= 0.05). "
            f"Do not ship treatment without further iteration."
        )

    control_rev = round(sum(r.order_revenue for r in control_rows), 0)
    treatment_rev = round(sum(r.order_revenue for r in treatment_rows), 0)

    return {
        "id": exp.id,
        "key": exp.key,
        "name": exp.name,
        "problem_statement": exp.problem_statement,
        "hypothesis": exp.hypothesis,
        "primary_metric": exp.primary_metric,
        "secondary_metrics": json.loads(exp.secondary_metrics_json),
        "control_description": exp.control_description,
        "treatment_description": exp.treatment_description,
        "status": exp.status,
        "traffic_allocation_pct": exp.traffic_allocation_pct,
        "target_sample_size": exp.target_sample_size,
        "sample_adequacy_pct": min(100.0, sample_adequacy_pct),
        "is_adequately_powered": is_adequately_powered,
        "start_date": exp.start_date.strftime("%Y-%m-%d"),
        "end_date": exp.end_date.strftime("%Y-%m-%d") if exp.end_date else None,
        "owner": exp.owner,
        "sample_sizes": {
            "total_exposed": total_exposed,
            "control_users": n_c,
            "treatment_users": n_t,
            "control_revenue_inr": control_rev,
            "treatment_revenue_inr": treatment_rev,
        },
        "decision_classification": decision_badge,
        "decision_recommendation": decision_recommendation,
        "primary_metric_summary": primary_stats,
        "metrics_breakdown": list(metrics_analysis.values()),
    }


def list_experiments_with_stats(db: Session) -> List[Dict[str, Any]]:
    exps = db.query(Experiment).order_by(Experiment.start_date.desc()).all()
    return [evaluate_experiment(db, exp) for exp in exps]


def assign_user_to_experiment(
    db: Session, experiment_key: str, user_id: str, session_id: str | None = None
) -> Dict[str, Any]:
    exp = db.query(Experiment).filter(Experiment.key == experiment_key).first()
    if not exp:
        raise ValueError(f"Experiment '{experiment_key}' not found")

    ensure_user_and_session(db, user_id=user_id, session_id=session_id or "sess_live_001")

    existing = (
        db.query(ExperimentAssignment)
        .filter(
            ExperimentAssignment.experiment_id == exp.id,
            ExperimentAssignment.user_id == user_id,
        )
        .first()
    )
    if existing:
        return {
            "experiment_id": exp.id,
            "experiment_key": exp.key,
            "user_id": user_id,
            "variant": existing.variant,
            "assignment_method": "existing_sticky_assignment",
            "hash_Preview": hashlib.sha256(f"{exp.key}:{user_id}".encode("utf-8")).hexdigest()[:12],
        }

    variant = deterministic_variant_for_user(exp.key, user_id)
    new_assign = ExperimentAssignment(
        id=f"ea_live_{uuid.uuid4().hex[:8]}",
        experiment_id=exp.id,
        user_id=user_id,
        session_id=session_id,
        variant=variant,
        exposed_at=datetime.utcnow(),
        search_submitted=False,
        search_clicked=False,
        product_viewed=False,
        added_to_cart=False,
        order_completed=False,
        order_revenue=0.0,
    )
    db.add(new_assign)
    db.commit()
    return {
        "experiment_id": exp.id,
        "experiment_key": exp.key,
        "user_id": user_id,
        "variant": variant,
        "assignment_method": "sha256_deterministic_bucketing",
        "hash_preview": hashlib.sha256(f"{exp.key}:{user_id}".encode("utf-8")).hexdigest()[:12],
    }


def create_experiment(db: Session, req: ExperimentCreateRequest) -> Dict[str, Any]:
    existing = db.query(Experiment).filter(Experiment.key == req.key).first()
    if existing:
        raise ValueError(f"Experiment with key '{req.key}' already exists")

    exp = Experiment(
        id=f"exp_{uuid.uuid4().hex[:8]}",
        key=req.key,
        name=req.name,
        problem_statement=req.problem_statement,
        hypothesis=req.hypothesis,
        primary_metric=req.primary_metric,
        secondary_metrics_json=json.dumps(req.secondary_metrics),
        control_description=req.control_description,
        treatment_description=req.treatment_description,
        status="running",
        traffic_allocation_pct=req.traffic_allocation_pct,
        target_sample_size=req.target_sample_size,
        start_date=datetime.utcnow(),
        end_date=None,
        owner=req.owner,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return evaluate_experiment(db, exp)
