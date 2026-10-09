from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas_db import TerrainModel
from app.schemas.schemas import TerrainModelOut

router = APIRouter(prefix="/terrain", tags=["Terrain Models & DEM"])

@router.get("", response_model=List[TerrainModelOut])
def list_terrains(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(TerrainModel)
    if site_id is not None:
        query = query.filter(TerrainModel.site_id == site_id)
    return query.order_by(TerrainModel.created_at.desc()).all()

@router.get("/{terrain_id}", response_model=TerrainModelOut)
def get_terrain(terrain_id: int, db: Session = Depends(get_db)):
    terrain = db.query(TerrainModel).filter(TerrainModel.id == terrain_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain model not found")
    return terrain

@router.get("/{terrain_id}/elevation-matrix")
def get_elevation_matrix(terrain_id: int, db: Session = Depends(get_db)):
    terrain = db.query(TerrainModel).filter(TerrainModel.id == terrain_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain model not found")
    return {
        "terrain_id": terrain.id,
        "name": terrain.name,
        "grid_resolution_m": terrain.grid_resolution_m,
        "elevation_min": terrain.elevation_min,
        "elevation_max": terrain.elevation_max,
        "mean_elevation": terrain.mean_elevation,
        "matrix": terrain.dem_matrix_json
    }
