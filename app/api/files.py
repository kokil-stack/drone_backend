from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
from pathlib import Path
from app.core.config import settings
from app.core.database import get_db
from app.models.schemas_db import SurveyFile, Survey
from app.schemas.schemas import SurveyFileOut

router = APIRouter(prefix="/files", tags=["Survey Source Files"])

@router.get("", response_model=List[SurveyFileOut])
def list_files(survey_id: int, db: Session = Depends(get_db)):
    return db.query(SurveyFile).filter(SurveyFile.survey_id == survey_id).all()

@router.post("/upload", response_model=SurveyFileOut)
async def upload_file(
    survey_id: int = Form(...),
    file_type: str = Form("las"),  # las, laz, geotiff, dem, orthophoto
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    dest_path = settings.UPLOADS_DIR / f"survey_{survey_id}_{file.filename}"
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = dest_path.stat().st_size

    survey_file = SurveyFile(
        survey_id=survey_id,
        filename=file.filename,
        file_type=file_type,
        file_size_bytes=file_size,
        storage_path=str(dest_path),
        crs=survey.site.crs if survey.site else "EPSG:32644",
        bounds_json={"survey_id": survey_id}
    )
    db.add(survey_file)
    db.commit()
    db.refresh(survey_file)
    return survey_file
