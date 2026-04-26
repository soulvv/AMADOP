from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import logging
from pythonjsonlogger import jsonlogger

from config import settings
from scheduler import BackgroundScheduler

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Initialize the background scheduler
scheduler = BackgroundScheduler(
    interval_seconds=settings.SCAN_INTERVAL_SECONDS,
    admin_user_ids=settings.ADMIN_USER_IDS,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the lifecycle of background agents."""
    logger.info("🚀 AMADOP AI Service starting up...")
    logger.info(f"   Scan interval: {settings.SCAN_INTERVAL_SECONDS}s")
    logger.info(f"   Admin user IDs: {settings.ADMIN_USER_IDS}")
    logger.info(f"   Alert cooldown: {settings.ALERT_COOLDOWN_SECONDS}s")

    # Start background agents
    await scheduler.start()

    yield  # App is running

    # Shutdown background agents
    logger.info("Shutting down background agents...")
    await scheduler.stop()


app = FastAPI(title="AMADOP AI Service", version="2.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai_service",
        "agents": {
            "background_scheduler": scheduler.get_status(),
        },
    }


# Include AI routers
from routes import router

app.include_router(router, prefix="/api/v1/ai", tags=["AI"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
