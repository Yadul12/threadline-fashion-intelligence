from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import ACTIVE_DB_MODE, Base, SessionLocal, apply_sql_views, engine
from app.routers import (
    analytics,
    events,
    experiments,
    exports,
    feedback,
    roadmap,
    storefront,
)
from app.seed import SYNTHETIC_DATASET_NOTICE, seed_database
from app.services.export_service import write_deliverable_extracts_to_disk


def init_db_and_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        apply_sql_views()
        write_deliverable_extracts_to_disk(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_and_seed()
    yield


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=(
        "Production-grade Fashion Discovery & Customer Experience Intelligence API "
        "powering the THREADLINE Customer Storefront and Product Manager Workspace."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(storefront.router)
app.include_router(events.router)
app.include_router(analytics.router)
app.include_router(feedback.router)
app.include_router(experiments.router)
app.include_router(roadmap.router)
app.include_router(exports.router)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.project_name,
        "version": settings.version,
        "synthetic_data_notice": SYNTHETIC_DATASET_NOTICE,
        "integrations": {
            "database_engine": ACTIVE_DB_MODE,
            "mixpanel_sdk_configured": bool(settings.mixpanel_token),
            "gemini_api_configured": bool(settings.gemini_api_key),
            "gemini_model": settings.gemini_model,
            "tableau_views_ready": True,
            "jira_csv_export_ready": True,
        },
    }
