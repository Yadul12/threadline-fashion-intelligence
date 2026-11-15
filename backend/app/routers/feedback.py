from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import GenAIAnalyzeRequest
from app.services.genai_service import (
    generate_genai_feedback_intelligence,
    get_feedback_overview,
)

router = APIRouter(prefix="/api/feedback", tags=["Customer Feedback & GenAI Intelligence"])


@router.get("")
def feedback_dashboard(
    category_id: Optional[str] = Query(default="all"),
    complaint_category: Optional[str] = Query(default="all"),
    sentiment: Optional[str] = Query(default="all"),
    db: Session = Depends(get_db),
):
    overview = get_feedback_overview(
        db=db,
        category_id=category_id,
        complaint_category=complaint_category,
        sentiment=sentiment,
    )
    ai_synthesis = generate_genai_feedback_intelligence(
        db=db,
        category_filter=category_id,
        complaint_filter=complaint_category,
    )
    return {
        **overview,
        "genai_intelligence": ai_synthesis,
    }


@router.post("/analyze")
def run_custom_genai_analysis(
    req: GenAIAnalyzeRequest,
    db: Session = Depends(get_db),
):
    return generate_genai_feedback_intelligence(
        db=db,
        category_filter=req.category_filter,
        complaint_filter=req.complaint_filter,
        custom_question=req.custom_question,
    )
