import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AutoFactoryScope"
    MODEL_PATH: str = os.path.join("models", "best.onnx")
    TILE_SIZE: int = 640
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45

    class Config:
        env_file = ".env"

settings = Settings()
