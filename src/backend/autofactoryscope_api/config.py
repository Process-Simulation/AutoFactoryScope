from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "models").exists():
            return parent
    return current.parents[3]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    APP_NAME: str = "AutoFactoryScope"
    MODEL_PATH: str = Field(default_factory=lambda: str(_find_repo_root() / "models" / "robot_detector.onnx"))
    TILE_SIZE: int = 512
    TILE_OVERLAP: float = 0.1
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    PDF_DPI: int = 600
    PDF_MAX_PIXELS: Optional[int] = None
    PDF_AUTO_CROP: bool = True
    PDF_CROP_WHITE_THRESHOLD: int = 245
    PDF_CROP_PADDING_PX: int = 12
    PDF_MIN_CONTENT_RATIO: float = 0.02
    CROP_MIN_SIZE_PX: int = 48
    PDF_DEBUG_SAVE_DIR: Optional[str] = Field(
        default_factory=lambda: str(
            _find_repo_root()
            / "src"
            / "backend"
            / "autofactoryscope_api"
            / "tests"
            / "pdf_output"
        )
    )

settings = Settings()
