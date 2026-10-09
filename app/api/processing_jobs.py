from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas_db import ProcessingJob, Survey, TerrainModel
from app.schemas.schemas import ProcessingJobOut, ProcessingJobCreate
from app.services.point_cloud import simulate_lidar_filtering_and_dem

router = APIRouter(prefix="/processing-jobs", tags=["LiDAR & DEM Processing Jobs"])

@router.get("", response_model=List[ProcessingJobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(ProcessingJob).order_by(ProcessingJob.started_at.desc()).all()

@router.get("/{job_id}", response_model=ProcessingJobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job

@router.post("", response_model=ProcessingJobOut)
def submit_job(job_in: ProcessingJobCreate, db: Session = Depends(get_db)):
    survey = db.query(Survey).filter(Survey.id == job_in.survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    # Run electromechanical noise filtering and DEM creation
    filtered_count, dev_cm, dem_meta, dem_matrix = simulate_lidar_filtering_and_dem(
        area_sq_km=survey.flight_area_sq_km,
        point_density_pts_m2=survey.point_density_pts_m2,
        base_elevation=218.0
    )

    now = datetime.now(timezone.utc)
    log_text = (
        f"Processing completed for {survey.name}.\n"
        f"1. Raw point-cloud parsed: {dem_meta['total_raw_points']:,} points.\n"
        f"2. Electromechanical equipment automatic filtering: {filtered_count} heavy machines (dumpers, shovels) removed.\n"
        f"3. Vegetation filtered: {dem_meta['vegetation_filtered']:,} points.\n"
        f"4. Elevation deviation verified: {dev_cm} cm without GCPs.\n"
        f"5. DEM generated: min {dem_meta['elevation_min_m']}m, max {dem_meta['elevation_max_m']}m, mean {dem_meta['mean_elevation_m']}m."
    )

    job = ProcessingJob(
        survey_id=survey.id,
        job_type=job_in.job_type,
        status="completed",
        progress_pct=100.0,
        machinery_filtered_count=filtered_count,
        elevation_deviation_cm=dev_cm,
        log=log_text,
        started_at=now,
        completed_at=now
    )
    db.add(job)

    # Save generated Terrain Model
    terrain = TerrainModel(
        site_id=survey.site_id,
        survey_id=survey.id,
        name=f"Processed DEM - {survey.name}",
        grid_resolution_m=0.25,
        elevation_min=dem_meta["elevation_min_m"],
        elevation_max=dem_meta["elevation_max_m"],
        mean_elevation=dem_meta["mean_elevation_m"],
        dem_matrix_json=dem_matrix,
        stage_label="stage_2_current"
    )
    db.add(terrain)
    db.commit()
    db.refresh(job)
    return job
