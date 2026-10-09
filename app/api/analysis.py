from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas_db import (
    TerrainModel, VolumeComparison, TerrainProfile, RoadProfile, Survey
)
from app.schemas.schemas import (
    TerrainProfileRequest, TerrainProfileOut,
    RoadProfileRequest, RoadProfileOut,
    CutFillRequest, CutFillOut,
    VolumeComparisonRequest, VolumeComparisonOut,
    VolumeAcceptanceAction
)
from app.services.terrain_profile import calculate_terrain_profile
from app.services.road_profile import calculate_road_profile
from app.services.cut_fill import calculate_cut_and_fill
from app.services.volume_comparison import compute_two_stage_differential_demodulation

router = APIRouter(prefix="/analysis", tags=["Geospatial & Volume Analysis"])

# 1. Terrain Profile
@router.post("/terrain-profile", response_model=TerrainProfileOut)
def profile_transect(req: TerrainProfileRequest, db: Session = Depends(get_db)):
    terrain = db.query(TerrainModel).filter(TerrainModel.id == req.terrain_model_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain model not found")

    matrix = terrain.dem_matrix_json or []
    res = calculate_terrain_profile(
        matrix,
        req.line_geojson,
        samples_count=req.samples_count,
        elevation_min=terrain.elevation_min,
        elevation_max=terrain.elevation_max
    )

    t_prof = TerrainProfile(
        terrain_model_id=terrain.id,
        name=req.name,
        line_geojson=req.line_geojson,
        distance_total_m=res["distance_total_m"],
        elevation_min=res["elevation_min"],
        elevation_max=res["elevation_max"],
        max_slope_deg=res["max_slope_deg"],
        samples_json=res["samples"]
    )
    db.add(t_prof)
    db.commit()
    db.refresh(t_prof)
    return t_prof

@router.get("/terrain-profile/{profile_id}", response_model=TerrainProfileOut)
def get_terrain_profile(profile_id: int, db: Session = Depends(get_db)):
    t_prof = db.query(TerrainProfile).filter(TerrainProfile.id == profile_id).first()
    if not t_prof:
        raise HTTPException(status_code=404, detail="Terrain profile not found")
    return t_prof

# 2. Road Profile & DGMS Slope Inspection
@router.post("/road-profile", response_model=RoadProfileOut)
def analyze_road(req: RoadProfileRequest, db: Session = Depends(get_db)):
    terrain = db.query(TerrainModel).filter(TerrainModel.id == req.terrain_model_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain model not found")

    res = calculate_road_profile(
        req.alignment_geojson,
        max_allowed_slope_pct=req.max_allowed_slope_pct,
        min_safety_berm_m=req.min_safety_berm_m
    )

    r_prof = RoadProfile(
        terrain_model_id=terrain.id,
        name=req.name,
        alignment_geojson=req.alignment_geojson,
        length_m=res["length_m"],
        avg_slope_pct=res["avg_slope_pct"],
        max_slope_pct=res["max_slope_pct"],
        max_allowed_slope_pct=req.max_allowed_slope_pct,
        safety_berm_height_m=req.min_safety_berm_m,
        violations_count=res["violations_count"],
        violations_json=res["violations"],
        safety_status=res["safety_status"]
    )
    db.add(r_prof)
    db.commit()
    db.refresh(r_prof)
    return r_prof

# 3. Cut & Fill
@router.post("/cut-fill", response_model=CutFillOut)
def cut_fill_analysis(req: CutFillRequest, db: Session = Depends(get_db)):
    terrain = db.query(TerrainModel).filter(TerrainModel.id == req.terrain_model_id).first()
    if not terrain:
        raise HTTPException(status_code=404, detail="Terrain model not found")

    return calculate_cut_and_fill(
        name=req.name,
        reference_elevation_m=req.reference_elevation_m,
        polygon_geojson=req.polygon_geojson
    )

# 4. Two-Stage Differential Demodulation Volume Comparison
@router.get("/volume-comparisons", response_model=List[VolumeComparisonOut])
def list_volume_comparisons(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(VolumeComparison)
    if site_id is not None:
        query = query.filter(VolumeComparison.site_id == site_id)
    return query.order_by(VolumeComparison.created_at.desc()).all()

@router.post("/volume-comparison", response_model=VolumeComparisonOut)
def compute_volume_comparison(req: VolumeComparisonRequest, db: Session = Depends(get_db)):
    curr_survey = db.query(Survey).filter(Survey.id == req.current_survey_id).first()
    prev_survey = db.query(Survey).filter(Survey.id == req.previous_survey_id).first()
    if not curr_survey or not prev_survey:
        raise HTTPException(status_code=404, detail="Current or Previous survey not found")

    res = compute_two_stage_differential_demodulation(
        current_survey_name=curr_survey.name,
        previous_survey_name=prev_survey.name,
        area_name=req.area_name,
        ore_density_t_m3=req.ore_density_t_m3,
        polygon_geojson=req.polygon_geojson
    )

    vol_comp = VolumeComparison(
        site_id=req.site_id,
        current_survey_id=req.current_survey_id,
        previous_survey_id=req.previous_survey_id,
        area_name=req.area_name,
        comparison_method=res["comparison_method"],
        cut_volume_m3=res["cut_volume_m3"],
        fill_volume_m3=res["fill_volume_m3"],
        net_volume_m3=res["net_volume_m3"],
        stripping_volume_m3=res["stripping_volume_m3"],
        ore_extracted_volume_m3=res["ore_extracted_volume_m3"],
        ore_density_t_m3=req.ore_density_t_m3,
        total_ore_tonnage_t=res["total_ore_tonnage_t"],
        waste_tonnage_t=res["waste_tonnage_t"],
        elevation_deviation_cm=res["elevation_deviation_cm"],
        acceptance_status="ACCEPTED",
        accepted_by="Chief Mine Surveyor",
        accepted_at=datetime.now(timezone.utc),
        remarks=f"Verified 6cm precision with dual RTK GPS. GCPs not required. {res['compliance']}"
    )
    db.add(vol_comp)
    db.commit()
    db.refresh(vol_comp)
    return vol_comp

@router.patch("/volume-comparison/{comp_id}/acceptance", response_model=VolumeComparisonOut)
def action_volume_acceptance(
    comp_id: int,
    action: VolumeAcceptanceAction,
    db: Session = Depends(get_db)
):
    comp = db.query(VolumeComparison).filter(VolumeComparison.id == comp_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Volume comparison not found")

    comp.acceptance_status = action.status
    comp.accepted_by = action.accepted_by
    comp.accepted_at = datetime.now(timezone.utc)
    if action.remarks:
        comp.remarks = action.remarks

    db.commit()
    db.refresh(comp)
    return comp
