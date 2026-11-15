import json
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import EventRecord
from app.schemas import EventTrackRequest
from app.services.analytics_service import CANONICAL_EVENTS, track_event

router = APIRouter(prefix="/api/events", tags=["Product Analytics & Mixpanel"])


@router.post("/track")
def track_single_event(
    req: EventTrackRequest,
    db: Session = Depends(get_db),
):
    ev = track_event(db, req)
    return {
        "status": "recorded",
        "event_id": ev.id,
        "event_name": ev.event_name,
        "mixpanel_dispatched": ev.mixpanel_dispatched,
        "adapter_mode": "mixpanel_cloud_and_sql" if ev.mixpanel_dispatched else "local_sql_adapter",
        "timestamp": ev.event_timestamp.isoformat(),
    }


@router.get("/recent")
def list_recent_events(
    limit: int = Query(default=35, ge=5, le=200),
    event_name: str = Query(default="all"),
    db: Session = Depends(get_db),
):
    q = db.query(EventRecord)
    if event_name and event_name != "all":
        q = q.filter(EventRecord.event_name == event_name)
    rows = q.order_by(EventRecord.event_timestamp.desc()).limit(limit).all()

    return {
        "canonical_events": CANONICAL_EVENTS,
        "mixpanel_configured": bool(settings.mixpanel_token),
        "events": [
            {
                "id": r.id,
                "event_name": r.event_name,
                "user_id": r.user_id,
                "session_id": r.session_id,
                "product_id": r.product_id,
                "category": r.category,
                "price": r.price,
                "brand": r.brand,
                "device_type": r.device_type,
                "acquisition_channel": r.acquisition_channel,
                "experiment_variant": r.experiment_variant,
                "properties": json.loads(r.properties_json or "{}"),
                "mixpanel_dispatched": r.mixpanel_dispatched,
                "event_timestamp": r.event_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for r in rows
        ],
    }
