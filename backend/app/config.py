import os
from dataclasses import dataclass, field
from typing import List


def _parse_cors(raw: str) -> List[str]:
    if not raw:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass
class Settings:
    project_name: str = "THREADLINE — Fashion Discovery & Customer Experience Intelligence"
    version: str = "1.0.0"
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "").strip())
    mixpanel_token: str = field(default_factory=lambda: os.getenv("MIXPANEL_TOKEN", "").strip())
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", "").strip())
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-4-hydrogen").strip())
    cors_origins: List[str] = field(
        default_factory=lambda: _parse_cors(os.getenv("BACKEND_CORS_ORIGINS", ""))
    )


settings = Settings()
