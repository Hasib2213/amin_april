from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "heritage_ai"
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    UPLOAD_TEMP_DIR: Path = Path("./uploads/temp")

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
settings.UPLOAD_TEMP_DIR.mkdir(parents=True, exist_ok=True)