from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # core -> app -> backend
ENV_FILE = BASE_DIR / ".env"

print(f"Loading .env from: {ENV_FILE}")
print(f"File exists: {ENV_FILE.exists()}")

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GEMINI_API_KEY: Optional[str] = None
    TAVILY_API_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_ENV: str = "development"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"

settings = Settings()