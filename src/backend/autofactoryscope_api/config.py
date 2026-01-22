from pathlib import Path
from pydantic_settings import BaseSettings


def _find_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "models").exists():
            return parent
    return current.parents[3]

class Settings(BaseSettings):
    APP_NAME: str = "AutoFactoryScope"
    MODEL_PATH: str = str(_find_repo_root() / "models" / "robot_detector.onnx")
    TILE_SIZE: int = 512
    TILE_OVERLAP: float = 0.1
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    PDF_DPI: int = 300

    class Config:
        env_file = ".env"

settings = Settings()
