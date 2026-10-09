from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import seed_database_if_empty

# Routers
from app.api.auth import router as auth_router
from app.api.sites import router as sites_router
from app.api.sensors import router as sensors_router
from app.api.surveys import router as surveys_router
from app.api.files import router as files_router
from app.api.processing_jobs import router as jobs_router
from app.api.terrain import router as terrain_router
from app.api.analysis import router as analysis_router
from app.api.production import router as production_router
from app.api.equipment import router as equipment_router
from app.api.forecast import router as forecast_router
from app.api.simulations import router as simulations_router
from app.api.reports import router as reports_router
from app.api.earth_engine import router as earth_engine_router

# Ensure tables exist and seeded
Base.metadata.create_all(bind=engine)
_seed_db = SessionLocal()
try:
    seed_database_if_empty(_seed_db)
finally:
    _seed_db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Intelligent Drone-Based Mining and Digital Mine Platform. Supports VTOL UAV flight planning, multi-sensor suite (LiDAR 1350m range, 5-lens oblique, EO/IR thermal, inspectometer, RGB), 6cm elevation deviation LiDAR processing, electromechanical noise filtering, two-stage differential demodulation volume acceptance, 14-day shortfall prediction, DGMS haul road safety compliance, and automated PDF reporting.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(sites_router, prefix=settings.API_V1_STR)
app.include_router(sensors_router, prefix=settings.API_V1_STR)
app.include_router(surveys_router, prefix=settings.API_V1_STR)
app.include_router(files_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(terrain_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(production_router, prefix=settings.API_V1_STR)
app.include_router(equipment_router, prefix=settings.API_V1_STR)
app.include_router(forecast_router, prefix=settings.API_V1_STR)
app.include_router(simulations_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(earth_engine_router, prefix=settings.API_V1_STR)

from pathlib import Path
from fastapi.staticfiles import StaticFiles

@app.get("/api/info")
def root_info():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "uav_system": "JOUAV CW-25E / DJI Enterprise VTOL Hybrid",
        "lidar_precision": "6cm elevation deviation (zero GCP)",
        "sensors": [
            "LiDAR 1350m range",
            "Five-lens oblique camera",
            "EO/IR stabilized gimbal",
            "Image inspectometer",
            "RGB mapping camera"
        ]
    }

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

