from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PORT: int = 8005
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["*"]

    # Background agent settings
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8004"
    PROMETHEUS_URL: str = "http://prometheus-server.amadop.svc.cluster.local"
    SCAN_INTERVAL_SECONDS: int = 30
    ADMIN_USER_IDS: List[int] = [1]
    ALERT_COOLDOWN_SECONDS: int = 300  # Don't re-alert same threat within 5 min

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
