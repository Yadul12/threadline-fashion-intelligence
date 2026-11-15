from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ExperimentAssignRequest, ExperimentCreateRequest
from app.services.experiment_service import (
    assign_user_to_experiment,
    create_experiment,
    list_experiments_with_stats,
)

router = APIRouter(prefix="/api/experiments", tags=["Experimentation Centre"])


@router.get("")
def get_all_experiments(db: Session = Depends(get_db)):
    return {
        "experiments": list_experiments_with_stats(db),
        "statistical_method_note": (
            "Two-proportion Z-test (two-tailed, alpha = 0.05) with unpooled 95% confidence intervals "
            "for absolute lift. Experiments below target sample size are flagged as Exploratory."
        ),
    }


@router.post("")
def create_new_experiment(
    req: ExperimentCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        exp_data = create_experiment(db, req)
        return {"status": "created", "experiment": exp_data}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/assign")
def assign_user_variant(
    req: ExperimentAssignRequest,
    db: Session = Depends(get_db),
):
    try:
        return assign_user_to_experiment(
            db=db,
            experiment_key=req.experiment_key,
            user_id=req.user_id,
            session_id=req.session_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
