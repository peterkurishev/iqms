from pydantic_settings import BaseSettings

from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@db:5432/monitor"
    AGENT_KEY_EXPIRE_DAYS: int = 365
    
    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
