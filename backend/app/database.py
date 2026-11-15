import os
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = BASE_DIR / "threadline.db"


def resolve_database_url() -> tuple[str, str]:
    """
    Resolve the active SQLAlchemy database URL and engine mode.
    Uses PostgreSQL when DATABASE_URL is configured; falls back transparently
    to a local relational SQLite file when PostgreSQL is not configured.
    On serverless read-only filesystems (e.g. Vercel), uses /tmp/threadline.db.
    """
    configured_url = os.getenv("DATABASE_URL", "").strip() or settings.database_url
    if configured_url:
        mode = "postgresql" if "postgres" in configured_url.lower() else "custom_sql"
        return configured_url, mode
    if os.getenv("VERCEL") or not os.access(BASE_DIR, os.W_OK):
        sqlite_path = Path("/tmp/threadline.db")
    else:
        sqlite_path = DEFAULT_SQLITE_PATH
    return f"sqlite:///{sqlite_path.as_posix()}", "sqlite_local_fallback"


ACTIVE_DATABASE_URL, ACTIVE_DB_MODE = resolve_database_url()

connect_args = {"check_same_thread": False} if ACTIVE_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    ACTIVE_DATABASE_URL,
    connect_args=connect_args,
    future=True,
    echo=False,
)

if ACTIVE_DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def apply_sql_views() -> None:
    """Create Tableau-ready SQL views defined in migrations/002_tableau_views.sql."""
    views_file = BASE_DIR / "migrations" / "002_tableau_views.sql"
    if not views_file.exists():
        return
    sql_script = views_file.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
