"""
Configuration management for AutoFactoryScope API.

Uses pydantic-settings for environment variable support and validation.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="AFS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AutoFactoryScope"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Model Configuration
    model_path: Path = Path("models/robot_detector.onnx")
    tile_size: int = 512
    tile_overlap: float = 0.1
    confidence_threshold: float = 0.25
    nms_iou_threshold: float = 0.5

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Database (Optional)
    database_enabled: bool = False
    database_url: str = "postgresql+asyncpg://localhost/autofactoryscope"

    # Metrics
    metrics_enabled: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    def get_model_path(self) -> Path:
        """Get absolute model path, resolving relative paths from repo root."""
        if self.model_path.is_absolute():
            return self.model_path
        # Resolve relative to repo root (3 levels up from this file)
        repo_root = Path(__file__).parent.parent.parent.parent
        return repo_root / self.model_path


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
