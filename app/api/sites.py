from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas_db import MineSite
from app.schemas.schemas import MineSiteOut, MineSiteCreate

router = APIRouter(prefix="/sites", tags=["Mine Sites"])

@router.get("", response_model=List[MineSiteOut])
def get_sites(db: Session = Depends(get_db)):
    return db.query(MineSite).all()

@router.get("/{site_id}", response_model=MineSiteOut)
def get_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(MineSite).filter(MineSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Mine site not found")
    return site

@router.post("", response_model=MineSiteOut)
def create_site(site_in: MineSiteCreate, db: Session = Depends(get_db)):
    site = MineSite(**site_in.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site
