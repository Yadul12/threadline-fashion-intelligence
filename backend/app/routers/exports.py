from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.export_service import (
    generate_dataset_export,
    import_research_feedback_file,
)

router = APIRouter(prefix="/api/exports", tags=["Excel, Google Sheets & Tableau Exports"])


@router.get("/download")
def download_dataset_file(
    dataset: str = Query(
        ...,
        description="One of: kpi_report, customer_feedback, search_analysis, experiment_template, jira_backlog, tableau_extract",
    ),
    format: str = Query(default="xlsx", description="xlsx or csv"),
    db: Session = Depends(get_db),
):
    try:
        file_bytes, media_type, filename = generate_dataset_export(db, dataset=dataset, fmt=format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.post("/import-feedback")
async def upload_structured_research_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    try:
        result = import_research_feedback_file(db, filename=file.filename or "upload.csv", content=content)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
