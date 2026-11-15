import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RoadmapItem
from app.schemas import RoadmapItemCreateRequest, RoadmapRiceUpdateRequest

router = APIRouter(prefix="/api/roadmap", tags=["Product Roadmap & Jira Operations"])


def _serialize_roadmap(it: RoadmapItem) -> dict:
    return {
        "id": it.id,
        "jira_key": it.jira_key,
        "epic_name": it.epic_name,
        "title": it.title,
        "problem_evidence": it.problem_evidence,
        "user_story": it.user_story,
        "acceptance_criteria": json.loads(it.acceptance_criteria_json or "[]"),
        "reach_score": it.reach_score,
        "impact_score": it.impact_score,
        "confidence_pct": it.confidence_pct,
        "effort_person_weeks": it.effort_person_weeks,
        "rice_score": it.rice_score,
        "customer_impact": it.customer_impact,
        "business_impact": it.business_impact,
        "status": it.status,
        "sprint": it.sprint,
        "owner": it.owner,
    }


@router.get("")
def list_roadmap_items(db: Session = Depends(get_db)):
    items = db.query(RoadmapItem).order_by(RoadmapItem.rice_score.desc()).all()
    return {
        "formula": "RICE = (Reach × Impact × (Confidence % / 100)) / Effort (Person-Weeks)",
        "items": [_serialize_roadmap(it) for it in items],
    }


@router.post("")
def create_roadmap_item(
    req: RoadmapItemCreateRequest,
    db: Session = Depends(get_db),
):
    existing = db.query(RoadmapItem).filter(RoadmapItem.jira_key == req.jira_key).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Jira key '{req.jira_key}' already exists")

    rice = round(
        (req.reach_score * req.impact_score * (req.confidence_pct / 100.0)) / req.effort_person_weeks,
        1,
    )
    item = RoadmapItem(
        id=f"rm_{uuid.uuid4().hex[:8]}",
        jira_key=req.jira_key,
        epic_name=req.epic_name,
        title=req.title,
        problem_evidence=req.problem_evidence,
        user_story=req.user_story,
        acceptance_criteria_json=json.dumps(req.acceptance_criteria),
        reach_score=req.reach_score,
        impact_score=req.impact_score,
        confidence_pct=req.confidence_pct,
        effort_person_weeks=req.effort_person_weeks,
        rice_score=rice,
        customer_impact=req.customer_impact,
        business_impact=req.business_impact,
        status=req.status,
        sprint=req.sprint,
        owner=req.owner,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize_roadmap(item)


@router.patch("/{item_id}")
def update_roadmap_rice_score(
    item_id: str,
    req: RoadmapRiceUpdateRequest,
    db: Session = Depends(get_db),
):
    item = db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found")

    item.reach_score = req.reach_score
    item.impact_score = req.impact_score
    item.confidence_pct = req.confidence_pct
    item.effort_person_weeks = req.effort_person_weeks
    item.rice_score = round(
        (req.reach_score * req.impact_score * (req.confidence_pct / 100.0)) / req.effort_person_weeks,
        1,
    )
    if req.status:
        item.status = req.status

    db.commit()
    db.refresh(item)
    return _serialize_roadmap(item)
