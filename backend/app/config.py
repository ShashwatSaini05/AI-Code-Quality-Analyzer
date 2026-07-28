"""
CodeSage AI — Application Configuration
Centralized settings management using pydantic-settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = "CodeSage AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    api_version: str = "v1"

    # ── Database ─────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./codesage.db"
    database_url_sync: str = "sqlite:///./codesage.db"
    sqlite_url: str = "sqlite+aiosqlite:///./codesage.db"

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Qdrant ───────────────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ── JWT ──────────────────────────────────────────────────
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    # ── OAuth — GitHub ───────────────────────────────────────
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_redirect_uri: str = "http://localhost:8000/api/v1/auth/github/callback"

    # ── OAuth — Google ───────────────────────────────────────
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # ── Frontend ─────────────────────────────────────────────
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── ML Models ────────────────────────────────────────────
    ml_model_path: str = "./ml/models"
    embeddings_model: str = "all-MiniLM-L6-v2"

    # ── LLM (Optional) ──────────────────────────────────────
    llm_provider: str = "none"
    openai_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
