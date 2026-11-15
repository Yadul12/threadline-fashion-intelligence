import base64
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import ACTIVE_DB_MODE
from app.models import (
    EventRecord,
    Order,
    OrderItem,
    Product,
    Review,
    SearchRecord,
    SessionModel,
    User,
)
from app.schemas import EventTrackRequest

CANONICAL_EVENTS = [
    "homepage_viewed",
    "search_submitted",
    "search_result_clicked",
    "filter_applied",
    "product_viewed",
    "wishlist_added",
    "add_to_cart",
    "checkout_started",
    "order_placed",
    "product_reviewed",
]

SYNONYM_MAP = {
    "haldi guest outfit": ["occasion", "Evening Editorial", "Weekend Resort", "Terracotta", "Gold", "midi", "maxi"],
    "kurta set silk": ["silk", "popover", "tunic", "mandarin", "occasion"],
    "petite friendly maxi": ["midi", "pleated", "column", "ankle"],
    "vegan suede tote": ["tote", "bag", "shoulder", "accessories"],
    "breathable summer office wear": ["linen", "work", "atelier", "blazer", "shirt", "trouser", "poplin"],
    "linen co-ord set": ["linen", "blazer", "trouser", "waistcoat"],
    "wedding guest": ["occasion", "silk", "gown", "midi", "evening"],
    "office wear": ["work", "atelier", "blazer", "trouser", "shirt", "loafers"],
}


def ensure_user_and_session(
    db: Session,
    user_id: str,
    session_id: str,
    device_type: str = "desktop_web",
    acquisition_channel: str = "direct",
    experiment_variant: str = "control",
) -> tuple[User, SessionModel]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id,
            email=f"{user_id}@threadline-visitor.in",
            full_name=f"Visitor {user_id[-4:]}",
            persona_segment="Fit-Conscious Minimalist",
            preferred_size="M",
            acquisition_channel=acquisition_channel or "direct",
            primary_device=device_type or "desktop_web",
            city_tier="Metro Tier-1",
            cohort_month="2026-11",
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.flush()

    sess = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not sess:
        sess = SessionModel(
            id=session_id,
            user_id=user.id,
            device_type=device_type or user.primary_device,
            acquisition_channel=acquisition_channel or user.acquisition_channel,
            experiment_variant=experiment_variant or "control",
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            duration_seconds=30,
            converted=False,
        )
        db.add(sess)
        db.flush()
    else:
        sess.ended_at = datetime.utcnow()
        sess.duration_seconds = max(
            sess.duration_seconds,
            int((sess.ended_at - sess.started_at).total_seconds()),
        )

    return user, sess


def _dispatch_to_mixpanel(event_name: str, payload: Dict[str, Any]) -> bool:
    """
    Send event to Mixpanel HTTP Ingestion API if MIXPANEL_TOKEN is configured.
    Never fakes success: returns True only if Mixpanel is configured and returns HTTP 200 '1'.
    """
    token = settings.mixpanel_token
    if not token:
        return False
    try:
        mp_event = {
            "event": event_name,
            "properties": {
                "token": token,
                "distinct_id": payload.get("user_id", "anonymous"),
                "time": int(datetime.utcnow().timestamp()),
                **payload,
            },
        }
        encoded = base64.b64encode(json.dumps([mp_event]).encode("utf-8")).decode("utf-8")
        resp = httpx.post(
            "https://api.mixpanel.com/track",
            data={"data": encoded},
            timeout=2.5,
        )
        return resp.status_code == 200 and resp.text.strip() == "1"
    except Exception:
        return False


def track_event(db: Session, req: EventTrackRequest) -> EventRecord:
    user, sess = ensure_user_and_session(
        db=db,
        user_id=req.user_id,
        session_id=req.session_id,
        device_type=req.device_type,
        acquisition_channel=req.acquisition_channel,
        experiment_variant=req.experiment_variant or "control",
    )

    product = None
    if req.product_id:
        product = db.query(Product).filter(Product.id == req.product_id).first()

    cat_name = req.category
    price_val = req.price
    brand_val = req.brand
    if product:
        if price_val is None:
            price_val = product.price
        if brand_val is None:
            brand_val = product.brand
        if cat_name is None and product.category:
            cat_name = product.category.name

    structured_props = {
        "user_id": user.id,
        "session_id": sess.id,
        "product_id": product.id if product else None,
        "category": cat_name,
        "price": price_val,
        "brand": brand_val,
        "device_type": req.device_type or user.primary_device,
        "acquisition_channel": req.acquisition_channel or user.acquisition_channel,
        "experiment_variant": req.experiment_variant or sess.experiment_variant,
        "event_timestamp": datetime.utcnow().isoformat(),
        **(req.properties or {}),
    }

    mp_sent = _dispatch_to_mixpanel(req.event_name, structured_props)

    ev = EventRecord(
        id=f"evt_live_{uuid.uuid4().hex[:10]}",
        event_name=req.event_name,
        user_id=user.id,
        session_id=sess.id,
        product_id=product.id if product else None,
        category=cat_name,
        price=price_val,
        brand=brand_val,
        device_type=req.device_type or user.primary_device,
        acquisition_channel=req.acquisition_channel or user.acquisition_channel,
        experiment_variant=req.experiment_variant or sess.experiment_variant,
        properties_json=json.dumps(req.properties or {}),
        mixpanel_dispatched=mp_sent,
        event_timestamp=datetime.utcnow(),
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def get_overview_metrics(db: Session) -> Dict[str, Any]:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_searches = db.query(func.count(SearchRecord.id)).scalar() or 0
    total_events = db.query(func.count(EventRecord.id)).scalar() or 0
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    gross_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0.0)).scalar() or 0.0

    pdp_sessions = (
        db.query(func.count(func.distinct(EventRecord.session_id)))
        .filter(EventRecord.event_name == "product_viewed")
        .scalar()
        or 0
    )
    atc_sessions = (
        db.query(func.count(func.distinct(EventRecord.session_id)))
        .filter(EventRecord.event_name == "add_to_cart")
        .scalar()
        or 0
    )
    order_sessions = (
        db.query(func.count(func.distinct(EventRecord.session_id)))
        .filter(EventRecord.event_name == "order_placed")
        .scalar()
        or 0
    )

    pdp_engagement_rate = round(100.0 * pdp_sessions / max(1, total_sessions), 1)
    add_to_cart_rate = round(100.0 * atc_sessions / max(1, total_sessions), 1)
    conversion_rate = round(100.0 * order_sessions / max(1, total_sessions), 1)
    avg_order_value = round(gross_revenue / max(1, total_orders), 0)

    # Repeat purchase rate & retention summary
    user_order_counts = (
        db.query(Order.user_id, func.count(Order.id).label("cnt"))
        .group_by(Order.user_id)
        .all()
    )
    buyers_count = len(user_order_counts)
    repeat_buyers_count = sum(1 for _, cnt in user_order_counts if cnt >= 2)
    repeat_purchase_rate = round(100.0 * repeat_buyers_count / max(1, buyers_count), 1)

    # Daily trend (last 21 days of activity)
    daily_rows = db.execute(
        text(
            """
            SELECT
                SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10) AS date,
                COUNT(DISTINCT user_id) AS dau,
                COUNT(DISTINCT session_id) AS sessions,
                SUM(CASE WHEN event_name = 'search_submitted' THEN 1 ELSE 0 END) AS searches,
                SUM(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS cart_adds,
                SUM(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS orders
            FROM events
            GROUP BY SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10)
            ORDER BY date DESC
            LIMIT 21
            """
        )
    ).mappings().all()
    daily_trend = [dict(r) for r in reversed(daily_rows)]

    # Category revenue & return rate breakdown
    cat_rows = db.execute(
        text(
            """
            SELECT
                c.name AS category,
                c.parent_department AS department,
                COALESCE(SUM(oi.quantity), 0) AS units_sold,
                ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 0) AS revenue,
                ROUND(AVG(p.return_rate_pct), 1) AS avg_return_rate_pct
            FROM categories c
            JOIN products p ON p.category_id = c.id
            LEFT JOIN order_items oi ON oi.product_id = p.id
            GROUP BY c.name, c.parent_department
            ORDER BY revenue DESC
            """
        )
    ).mappings().all()

    # User persona segmentation
    persona_rows = db.execute(
        text(
            """
            SELECT
                u.persona_segment AS persona,
                COUNT(DISTINCT u.id) AS users,
                COUNT(DISTINCT s.id) AS sessions,
                COUNT(DISTINCT o.id) AS orders,
                ROUND(COALESCE(SUM(o.total_amount), 0), 0) AS revenue,
                ROUND(100.0 * COUNT(DISTINCT o.id) / NULLIF(COUNT(DISTINCT s.id), 0), 1) AS session_cvr_pct
            FROM users u
            LEFT JOIN sessions s ON s.user_id = u.id
            LEFT JOIN orders o ON o.user_id = u.id
            GROUP BY u.persona_segment
            ORDER BY revenue DESC
            """
        )
    ).mappings().all()

    # Feature adoption rates
    wishlist_users = (
        db.query(func.count(func.distinct(EventRecord.user_id)))
        .filter(EventRecord.event_name == "wishlist_added")
        .scalar()
        or 0
    )
    filter_users = (
        db.query(func.count(func.distinct(EventRecord.user_id)))
        .filter(EventRecord.event_name == "filter_applied")
        .scalar()
        or 0
    )
    search_users = (
        db.query(func.count(func.distinct(EventRecord.user_id)))
        .filter(EventRecord.event_name == "search_submitted")
        .scalar()
        or 0
    )

    return {
        "kpis": {
            "active_users_mau": total_users,
            "avg_dau": round(sum(d["dau"] for d in daily_trend) / max(1, len(daily_trend)), 1),
            "estimated_wau": min(total_users, int(round(sum(d["dau"] for d in daily_trend[-7:]) * 0.85))),
            "total_sessions": total_sessions,
            "search_volume": total_searches,
            "total_events_tracked": total_events,
            "pdp_engagement_rate_pct": pdp_engagement_rate,
            "add_to_cart_rate_pct": add_to_cart_rate,
            "conversion_rate_pct": conversion_rate,
            "gross_revenue_inr": round(gross_revenue, 0),
            "total_orders": total_orders,
            "avg_order_value_inr": avg_order_value,
            "repeat_purchase_rate_pct": repeat_purchase_rate,
        },
        "feature_adoption": [
            {
                "feature": "Search & Autocomplete Discovery",
                "adopted_users": search_users,
                "adoption_rate_pct": round(100.0 * search_users / max(1, total_users), 1),
            },
            {
                "feature": "Size & Fit Facet Filtering",
                "adopted_users": filter_users,
                "adoption_rate_pct": round(100.0 * filter_users / max(1, total_users), 1),
            },
            {
                "feature": "Editorial Wishlist Curation",
                "adopted_users": wishlist_users,
                "adoption_rate_pct": round(100.0 * wishlist_users / max(1, total_users), 1),
            },
        ],
        "daily_trend": daily_trend,
        "category_performance": [dict(r) for r in cat_rows],
        "persona_segments": [dict(r) for r in persona_rows],
        "integrations": {
            "database_mode": ACTIVE_DB_MODE,
            "mixpanel_configured": bool(settings.mixpanel_token),
            "mixpanel_status": (
                "Mixpanel Cloud + PostgreSQL Dual-Write Active"
                if settings.mixpanel_token
                else "Local Relational Event Adapter Active (MIXPANEL_TOKEN not set)"
            ),
            "gemini_configured": bool(settings.gemini_api_key),
            "gemini_model": settings.gemini_model,
        },
    }


def get_funnel_analytics(
    db: Session,
    device_type: Optional[str] = None,
    acquisition_channel: Optional[str] = None,
    experiment_variant: Optional[str] = None,
) -> Dict[str, Any]:
    where_clauses = []
    params: Dict[str, Any] = {}
    if device_type and device_type != "all":
        where_clauses.append("device_type = :device_type")
        params["device_type"] = device_type
    if acquisition_channel and acquisition_channel != "all":
        where_clauses.append("acquisition_channel = :acquisition_channel")
        params["acquisition_channel"] = acquisition_channel
    if experiment_variant and experiment_variant != "all":
        where_clauses.append("experiment_variant = :experiment_variant")
        params["experiment_variant"] = experiment_variant

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    row = db.execute(
        text(
            f"""
            WITH session_steps AS (
                SELECT
                    session_id,
                    MAX(CASE WHEN event_name = 'homepage_viewed' THEN 1 ELSE 0 END) AS s1_homepage,
                    MAX(CASE WHEN event_name = 'search_submitted' THEN 1 ELSE 0 END) AS s2_search,
                    MAX(CASE WHEN event_name = 'search_result_clicked' THEN 1 ELSE 0 END) AS s3_click,
                    MAX(CASE WHEN event_name = 'product_viewed' THEN 1 ELSE 0 END) AS s4_pdp,
                    MAX(CASE WHEN event_name = 'wishlist_added' THEN 1 ELSE 0 END) AS s5_wishlist,
                    MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS s6_cart,
                    MAX(CASE WHEN event_name = 'checkout_started' THEN 1 ELSE 0 END) AS s7_checkout,
                    MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS s8_order
                FROM events
                {where_sql}
                GROUP BY session_id
            )
            SELECT
                COUNT(*) AS total_sessions,
                COALESCE(SUM(s1_homepage), 0) AS homepage_viewed,
                COALESCE(SUM(s2_search), 0) AS search_submitted,
                COALESCE(SUM(s3_click), 0) AS search_result_clicked,
                COALESCE(SUM(s4_pdp), 0) AS product_viewed,
                COALESCE(SUM(s5_wishlist), 0) AS wishlist_added,
                COALESCE(SUM(s6_cart), 0) AS add_to_cart,
                COALESCE(SUM(s7_checkout), 0) AS checkout_started,
                COALESCE(SUM(s8_order), 0) AS order_placed
            FROM session_steps
            """
        ),
        params,
    ).mappings().first()

    counts = dict(row) if row else {}
    top_count = max(1, counts.get("homepage_viewed") or counts.get("total_sessions") or 1)

    steps_meta = [
        ("homepage_viewed", "1. Homepage Visit", "Storefront landing & editorial discovery"),
        ("search_submitted", "2. Search Submitted", "Keyword or category search initiated"),
        ("search_result_clicked", "3. Search Result Clicked", "Clicked a SKU card from search results"),
        ("product_viewed", "4. Product Viewed (PDP)", "Inspected product photos, fabric & size guide"),
        ("wishlist_added", "5. Added to Wishlist", "Saved item to personal curation (optional micro-conversion)"),
        ("add_to_cart", "6. Added to Bag", "Selected size & colorway and added to shopping bag"),
        ("checkout_started", "7. Checkout Started", "Entered shipping address & payment selection"),
        ("order_placed", "8. Purchase Completed", "Confirmed order with order number generated"),
    ]

    funnel_steps = []
    # For sequential conversion calculation, wishlist is a parallel micro-conversion so step 6 compares against step 4 (product_viewed)
    prev_primary_sessions = top_count
    for key, label, desc in steps_meta:
        val = int(counts.get(key, 0))
        pct_of_top = round(100.0 * val / top_count, 1)
        if key == "homepage_viewed":
            step_conv = 100.0
            dropoff = 0.0
            prev_primary_sessions = max(1, val)
        elif key == "wishlist_added":
            pdp_val = max(1, int(counts.get("product_viewed", 1)))
            step_conv = round(100.0 * val / pdp_val, 1)
            dropoff = round(100.0 - step_conv, 1)
        else:
            step_conv = round(100.0 * val / max(1, prev_primary_sessions), 1)
            dropoff = round(max(0.0, 100.0 - step_conv), 1)
            prev_primary_sessions = max(1, val)

        funnel_steps.append(
            {
                "event_name": key,
                "step_label": label,
                "description": desc,
                "sessions": val,
                "conversion_from_top_pct": pct_of_top,
                "step_to_step_conversion_pct": min(100.0, step_conv),
                "drop_off_pct": dropoff,
                "is_micro_conversion": key == "wishlist_added",
            }
        )

    # Device comparison table
    device_rows = db.execute(
        text(
            """
            SELECT
                s.device_type,
                COUNT(DISTINCT s.id) AS sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN s.id END) AS pdp_sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN s.id END) AS cart_sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'order_placed' THEN s.id END) AS order_sessions,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'order_placed' THEN s.id END) / NULLIF(COUNT(DISTINCT s.id), 0), 1) AS cvr_pct
            FROM sessions s
            LEFT JOIN events e ON e.session_id = s.id
            GROUP BY s.device_type
            ORDER BY sessions DESC
            """
        )
    ).mappings().all()

    # Channel comparison table
    channel_rows = db.execute(
        text(
            """
            SELECT
                s.acquisition_channel,
                COUNT(DISTINCT s.id) AS sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'search_submitted' THEN s.id END) AS search_sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN s.id END) AS cart_sessions,
                COUNT(DISTINCT CASE WHEN e.event_name = 'order_placed' THEN s.id END) AS order_sessions,
                ROUND(100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'order_placed' THEN s.id END) / NULLIF(COUNT(DISTINCT s.id), 0), 1) AS cvr_pct
            FROM sessions s
            LEFT JOIN events e ON e.session_id = s.id
            GROUP BY s.acquisition_channel
            ORDER BY sessions DESC
            """
        )
    ).mappings().all()

    return {
        "filters_applied": {
            "device_type": device_type or "all",
            "acquisition_channel": acquisition_channel or "all",
            "experiment_variant": experiment_variant or "all",
        },
        "steps": funnel_steps,
        "by_device": [dict(r) for r in device_rows],
        "by_channel": [dict(r) for r in channel_rows],
    }


def get_cohort_retention(db: Session) -> List[Dict[str, Any]]:
    cohorts = ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]
    results = []
    for c_month in cohorts:
        cohort_size = db.query(func.count(User.id)).filter(User.cohort_month == c_month).scalar() or 0
        if cohort_size == 0:
            continue
        activity_rows = db.execute(
            text(
                """
                SELECT
                    SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7) AS act_month,
                    COUNT(DISTINCT e.user_id) AS active_users
                FROM users u
                JOIN events e ON e.user_id = u.id
                WHERE u.cohort_month = :c_month
                GROUP BY SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7)
                ORDER BY act_month ASC
                """
            ),
            {"c_month": c_month},
        ).mappings().all()

        month_map = {r["act_month"]: int(r["active_users"]) for r in activity_rows}
        c_idx = cohorts.index(c_month)
        months_retention = {}
        for offset in range(len(cohorts) - c_idx):
            target_m = cohorts[c_idx + offset]
            active_u = month_map.get(target_m, 0)
            if offset == 0:
                active_u = cohort_size
            months_retention[f"M{offset}"] = round(100.0 * active_u / cohort_size, 1)

        results.append(
            {
                "cohort_month": c_month,
                "cohort_size": cohort_size,
                "retention": months_retention,
            }
        )
    return results


def get_search_intelligence(db: Session) -> Dict[str, Any]:
    total_searches = db.query(func.count(SearchRecord.id)).scalar() or 0
    zero_result_searches = (
        db.query(func.count(SearchRecord.id)).filter(SearchRecord.results_count == 0).scalar() or 0
    )
    clicked_searches = (
        db.query(func.count(SearchRecord.id)).filter(SearchRecord.clicked_product_id.isnot(None)).scalar() or 0
    )
    abandoned_searches = (
        db.query(func.count(SearchRecord.id)).filter(SearchRecord.search_abandoned.is_(True)).scalar() or 0
    )
    bag_converted = (
        db.query(func.count(SearchRecord.id)).filter(SearchRecord.converted_to_bag.is_(True)).scalar() or 0
    )
    order_converted = (
        db.query(func.count(SearchRecord.id)).filter(SearchRecord.converted_to_order.is_(True)).scalar() or 0
    )

    query_rows = db.execute(
        text(
            """
            SELECT
                normalized_query AS query,
                COUNT(*) AS volume,
                ROUND(AVG(results_count), 1) AS avg_results,
                SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_result_hits,
                SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) AS clicks,
                SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) AS abandoned,
                SUM(CASE WHEN converted_to_bag = 1 OR converted_to_bag = TRUE THEN 1 ELSE 0 END) AS bag_conversions,
                SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) AS order_conversions,
                ROUND(100.0 * SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ctr_pct,
                ROUND(100.0 * SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS abandonment_pct,
                ROUND(100.0 * SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS order_cvr_pct
            FROM searches
            GROUP BY normalized_query
            ORDER BY volume DESC
            """
        )
    ).mappings().all()

    all_queries = [dict(r) for r in query_rows]
    zero_queries = [q for q in all_queries if q["zero_result_hits"] > 0]

    # Compare Control vs Treatment search performance
    variant_rows = db.execute(
        text(
            """
            SELECT
                experiment_variant AS variant,
                COUNT(*) AS searches,
                SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_results,
                ROUND(100.0 * SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS zero_result_rate_pct,
                ROUND(100.0 * SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS search_ctr_pct,
                ROUND(100.0 * SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS abandonment_rate_pct,
                ROUND(100.0 * SUM(CASE WHEN converted_to_bag = 1 OR converted_to_bag = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS search_to_bag_pct,
                ROUND(100.0 * SUM(CASE WHEN converted_to_order = 1 OR converted_to_order = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS search_to_order_pct
            FROM searches
            GROUP BY experiment_variant
            """
        )
    ).mappings().all()

    return {
        "summary": {
            "total_searches": total_searches,
            "zero_result_searches": zero_result_searches,
            "zero_result_rate_pct": round(100.0 * zero_result_searches / max(1, total_searches), 1),
            "search_ctr_pct": round(100.0 * clicked_searches / max(1, total_searches), 1),
            "search_abandonment_rate_pct": round(100.0 * abandoned_searches / max(1, total_searches), 1),
            "search_to_bag_rate_pct": round(100.0 * bag_converted / max(1, total_searches), 1),
            "search_to_purchase_cvr_pct": round(100.0 * order_converted / max(1, total_searches), 1),
        },
        "top_queries": all_queries,
        "zero_result_queries": zero_queries,
        "variant_comparison": [dict(r) for r in variant_rows],
        "synonym_dictionary": [
            {"user_query": k, "mapped_catalog_tokens": v} for k, v in SYNONYM_MAP.items()
        ],
    }


NAMED_SQL_QUERIES: Dict[str, Dict[str, str]] = {
    "conversion_funnel": {
        "title": "1. 8-Step Customer Conversion Funnel",
        "description": "Session-level progression from Homepage Visit through Purchase Completed.",
        "sql": """WITH session_steps AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_name = 'homepage_viewed' THEN 1 ELSE 0 END) AS step_1_homepage,
        MAX(CASE WHEN event_name = 'search_submitted' THEN 1 ELSE 0 END) AS step_2_search,
        MAX(CASE WHEN event_name = 'search_result_clicked' THEN 1 ELSE 0 END) AS step_3_search_click,
        MAX(CASE WHEN event_name = 'product_viewed' THEN 1 ELSE 0 END) AS step_4_pdp_view,
        MAX(CASE WHEN event_name = 'wishlist_added' THEN 1 ELSE 0 END) AS step_5_wishlist,
        MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS step_6_add_to_cart,
        MAX(CASE WHEN event_name = 'checkout_started' THEN 1 ELSE 0 END) AS step_7_checkout,
        MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS step_8_order
    FROM events
    GROUP BY session_id
)
SELECT
    COUNT(*) AS total_sessions,
    SUM(step_1_homepage) AS homepage_sessions,
    SUM(step_2_search) AS search_sessions,
    SUM(step_3_search_click) AS search_click_sessions,
    SUM(step_4_pdp_view) AS pdp_view_sessions,
    SUM(step_5_wishlist) AS wishlist_sessions,
    SUM(step_6_add_to_cart) AS add_to_cart_sessions,
    SUM(step_7_checkout) AS checkout_sessions,
    SUM(step_8_order) AS order_placed_sessions,
    ROUND(100.0 * SUM(step_8_order) / NULLIF(SUM(step_1_homepage), 0), 2) AS overall_cvr_pct
FROM session_steps""",
    },
    "daily_active_users": {
        "title": "2. Daily Active Users (DAU) & Event Velocity",
        "description": "Daily unique active users, sessions, and orders placed over the last 21 days.",
        "sql": """SELECT
    SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10) AS activity_date,
    COUNT(DISTINCT user_id) AS dau,
    COUNT(DISTINCT session_id) AS daily_sessions,
    COUNT(*) AS total_events,
    SUM(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS daily_orders
FROM events
GROUP BY SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10)
ORDER BY activity_date DESC
LIMIT 21""",
    },
    "wau_mau_stickiness": {
        "title": "3. Weekly & Monthly Active Users (WAU / MAU Stickiness)",
        "description": "Monthly active users, average DAU, and DAU/MAU stickiness ratio by month.",
        "sql": """WITH mau_calc AS (
    SELECT
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7) AS activity_month,
        COUNT(DISTINCT user_id) AS mau,
        COUNT(DISTINCT session_id) AS monthly_sessions
    FROM events
    GROUP BY SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7)
),
daily_by_month AS (
    SELECT
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7) AS activity_month,
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10) AS activity_date,
        COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 7),
        SUBSTR(CAST(event_timestamp AS VARCHAR), 1, 10)
)
SELECT
    m.activity_month,
    m.mau,
    m.monthly_sessions,
    ROUND(AVG(d.dau), 1) AS avg_dau,
    ROUND(100.0 * AVG(d.dau) / NULLIF(m.mau, 0), 1) AS stickiness_ratio_pct
FROM mau_calc m
JOIN daily_by_month d ON m.activity_month = d.activity_month
GROUP BY m.activity_month, m.mau, m.monthly_sessions
ORDER BY m.activity_month ASC""",
    },
    "customer_cohorts": {
        "title": "4. Customer Acquisition Cohort Retention",
        "description": "Cohort retention matrix tracking repeat active engagement by acquisition month.",
        "sql": """SELECT
    u.cohort_month,
    SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7) AS activity_month,
    COUNT(DISTINCT e.user_id) AS retained_users,
    (SELECT COUNT(*) FROM users u2 WHERE u2.cohort_month = u.cohort_month) AS cohort_size,
    ROUND(
        100.0 * COUNT(DISTINCT e.user_id) /
        NULLIF((SELECT COUNT(*) FROM users u2 WHERE u2.cohort_month = u.cohort_month), 0),
        1
    ) AS retention_rate_pct
FROM users u
JOIN events e ON u.id = e.user_id
GROUP BY u.cohort_month, SUBSTR(CAST(e.event_timestamp AS VARCHAR), 1, 7)
ORDER BY u.cohort_month ASC, activity_month ASC""",
    },
    "repeat_purchases": {
        "title": "5. Repeat Purchases & LTV by Persona Segment",
        "description": "Evaluates repeat buyer rate and average lifetime value across customer personas.",
        "sql": """WITH user_order_summary AS (
    SELECT
        u.id AS user_id,
        u.persona_segment,
        COUNT(o.id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS lifetime_spend
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.persona_segment
)
SELECT
    persona_segment,
    COUNT(*) AS total_users,
    SUM(CASE WHEN total_orders >= 1 THEN 1 ELSE 0 END) AS buyers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        100.0 * SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN total_orders >= 1 THEN 1 ELSE 0 END), 0),
        1
    ) AS repeat_purchase_rate_pct,
    ROUND(AVG(CASE WHEN total_orders >= 1 THEN lifetime_spend END), 0) AS avg_buyer_ltv_inr
FROM user_order_summary
GROUP BY persona_segment
ORDER BY repeat_purchase_rate_pct DESC""",
    },
    "product_ctr": {
        "title": "6. Product CTR, PDP Views & Add-to-Cart Efficiency",
        "description": "SKU-level discovery and merchandising performance across the catalog.",
        "sql": """SELECT
    p.sku,
    p.title,
    p.brand,
    p.fit_profile,
    p.price,
    COUNT(DISTINCT CASE WHEN s.clicked_product_id = p.id THEN s.id END) AS search_clicks,
    COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN e.id END) AS pdp_views,
    COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN e.id END) AS add_to_carts,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN e.id END) /
        NULLIF(COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN e.id END), 0),
        1
    ) AS pdp_to_cart_rate_pct,
    p.return_rate_pct
FROM products p
LEFT JOIN events e ON e.product_id = p.id
LEFT JOIN searches s ON s.clicked_product_id = p.id
GROUP BY p.id, p.sku, p.title, p.brand, p.fit_profile, p.price, p.return_rate_pct
ORDER BY pdp_views DESC
LIMIT 15""",
    },
    "search_abandonment": {
        "title": "7. Search Abandonment & Zero-Result Query Diagnostics",
        "description": "Identifies high-abandonment and zero-result queries requiring synonym or catalog remedies.",
        "sql": """SELECT
    normalized_query,
    COUNT(*) AS total_searches,
    ROUND(AVG(results_count), 1) AS avg_results,
    SUM(CASE WHEN results_count = 0 THEN 1 ELSE 0 END) AS zero_result_count,
    SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) AS clicked_count,
    SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) AS abandoned_count,
    ROUND(100.0 * SUM(CASE WHEN clicked_product_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS ctr_pct,
    ROUND(100.0 * SUM(CASE WHEN search_abandoned = 1 OR search_abandoned = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS abandonment_pct
FROM searches
GROUP BY normalized_query
ORDER BY abandonment_pct DESC, total_searches DESC""",
    },
    "category_revenue": {
        "title": "8. Category-Wise Revenue, Units Sold & Return Rate Exposure",
        "description": "Financial and merchandising summary across all 6 fashion categories.",
        "sql": """SELECT
    c.name AS category_name,
    c.parent_department,
    COUNT(DISTINCT o.id) AS orders_count,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 0) AS gross_revenue_inr,
    ROUND(AVG(p.price), 0) AS avg_sku_price_inr,
    ROUND(AVG(p.return_rate_pct), 1) AS avg_return_rate_pct
FROM categories c
JOIN products p ON p.category_id = c.id
LEFT JOIN order_items oi ON oi.product_id = p.id
LEFT JOIN orders o ON oi.order_id = o.id
GROUP BY c.name, c.parent_department
ORDER BY gross_revenue_inr DESC""",
    },
    "device_performance": {
        "title": "9. Device-Wise Funnel & Revenue Performance",
        "description": "Compares Mobile iOS, Mobile Android, and Desktop Web conversion and duration.",
        "sql": """SELECT
    s.device_type,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(DISTINCT s.user_id) AS unique_users,
    ROUND(AVG(s.duration_seconds), 0) AS avg_duration_sec,
    COUNT(DISTINCT CASE WHEN e.event_name = 'product_viewed' THEN s.id END) AS pdp_sessions,
    COUNT(DISTINCT CASE WHEN e.event_name = 'add_to_cart' THEN s.id END) AS cart_sessions,
    COUNT(DISTINCT o.id) AS completed_orders,
    ROUND(COALESCE(SUM(o.total_amount), 0), 0) AS total_revenue_inr,
    ROUND(100.0 * COUNT(DISTINCT o.id) / NULLIF(COUNT(DISTINCT s.id), 0), 2) AS session_cvr_pct
FROM sessions s
LEFT JOIN events e ON e.session_id = s.id
LEFT JOIN orders o ON o.session_id = s.id
GROUP BY s.device_type
ORDER BY total_sessions DESC""",
    },
}


def execute_named_sql_query(db: Session, query_key: str) -> Dict[str, Any]:
    meta = NAMED_SQL_QUERIES.get(query_key)
    if not meta:
        raise ValueError(f"Unknown SQL query key: {query_key}")
    rows = db.execute(text(meta["sql"])).mappings().all()
    data = [dict(r) for r in rows]
    columns = list(data[0].keys()) if data else []
    return {
        "query_key": query_key,
        "title": meta["title"],
        "description": meta["description"],
        "sql": meta["sql"],
        "columns": columns,
        "row_count": len(data),
        "rows": data,
    }
