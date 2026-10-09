from fastapi import APIRouter, Query, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.earth_engine import earth_engine_service

router = APIRouter(prefix="/earth-engine", tags=["Google Earth Engine & Satellite"])

class AuthRequest(BaseModel):
    project_id: Optional[str] = None
    service_account: Optional[str] = None
    key_file: Optional[str] = None

@router.get("/status")
def get_gee_status():
    """
    Returns Google Earth Engine initialization, authentication, and dataset status.
    """
    return earth_engine_service.get_status()

@router.get("/layers")
def get_gee_layers(
    lat: float = Query(23.762, description="Mine center latitude"),
    lng: float = Query(86.422, description="Mine center longitude")
):
    """
    Returns map tile layer configurations for Google Earth Satellite, Hybrid,
    Terrain basemaps and GEE multispectral layers.
    """
    return earth_engine_service.get_map_layers(site_lat=lat, site_lng=lng)

@router.get("/inspect")
def inspect_gee_pixel(
    lat: float = Query(..., description="Target latitude"),
    lng: float = Query(..., description="Target longitude"),
    site_id: int = Query(1, description="Target mine site ID")
):
    """
    Inspects Google Earth Engine multispectral bands and radiometric indices (NDVI,
    SRTM elevation, mineral index, thermal hazard) at given point coordinates.
    """
    return earth_engine_service.inspect_pixel(lat=lat, lng=lng, site_id=site_id)

@router.get("/thermal-hazards")
def get_thermal_hazards(
    lat: float = Query(23.762, description="Mine center latitude"),
    lng: float = Query(86.422, description="Mine center longitude"),
    radius_km: float = Query(2.5, description="Search radius in kilometers")
):
    """
    Scans for subsurface coal fire hotspots and thermal anomalies using
    Landsat-9 TIRS and MODIS radiometric sensors.
    """
    return earth_engine_service.get_thermal_hazards(site_lat=lat, site_lng=lng, radius_km=radius_km)

@router.get("/reclamation")
def get_environmental_reclamation(
    site_id: int = Query(1, description="Target mine site ID"),
    lat: float = Query(23.762, description="Mine center latitude"),
    lng: float = Query(86.422, description="Mine center longitude")
):
    """
    Returns progressive environmental mine reclamation, overburden greening,
    and NDVI afforestation progress.
    """
    return earth_engine_service.get_environmental_reclamation(site_id=site_id, site_lat=lat, site_lng=lng)

@router.get("/ndvi-timeseries")
def get_ndvi_timeseries(
    site_id: int = Query(1, description="Target mine site ID"),
    lat: float = Query(23.762, description="Mine center latitude"),
    lng: float = Query(86.422, description="Mine center longitude"),
    months: int = Query(12, description="Analysis window in months")
):
    """
    Returns multi-temporal Sentinel-2 NDVI trend progression and green cover reclamation timeline.
    """
    return earth_engine_service.get_ndvi_timeseries(site_id=site_id, site_lat=lat, site_lng=lng, months=months)

@router.post("/authenticate")
def authenticate_gee(req: Optional[AuthRequest] = None):
    """
    Allows setting custom Google Cloud Project ID or service account credentials
    for Google Earth Engine.
    """
    p_id = req.project_id if req else None
    sa = req.service_account if req else None
    kf = req.key_file if req else None
    return earth_engine_service.authenticate(project_id=p_id, service_account=sa, key_file=kf)

