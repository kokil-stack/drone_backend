from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas_db import EquipmentFleet
from app.schemas.schemas import EquipmentFleetOut

router = APIRouter(prefix="/equipment", tags=["Equipment Fleet & Dispatching"])

@router.get("", response_model=List[EquipmentFleetOut])
def list_equipment(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(EquipmentFleet)
    if site_id is not None:
        query = query.filter(EquipmentFleet.site_id == site_id)
    return query.all()

@router.patch("/{equipment_id}/status", response_model=EquipmentFleetOut)
def update_equipment_status(equipment_id: int, new_status: str, db: Session = Depends(get_db)):
    eq = db.query(EquipmentFleet).filter(EquipmentFleet.id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    eq.status = new_status
    db.commit()
    db.refresh(eq)
    return eq
