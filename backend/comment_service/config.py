from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/amadop_db"
    AUTH_SERVICE_URL: str = "http://auth_service:8001"
    POST_SERVICE_URL: str = "http://post_service:8002"
    NOTIFICATION_SERVICE_URL: str = "http://notification_service:8004"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"


settings = Settings()
