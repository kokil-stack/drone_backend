from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas_db import ProductionRecord, MineSite
from app.schemas.schemas import ProductionRecordOut, ProductionDashboardKPI

router = APIRouter(prefix="/production", tags=["Mine Production & Operational Intelligence"])

@router.get("", response_model=List[ProductionRecordOut])
def list_production(site_id: Optional[int] = Query(None), limit: int = 30, db: Session = Depends(get_db)):
    query = db.query(ProductionRecord)
    if site_id is not None:
        query = query.filter(ProductionRecord.site_id == site_id)
    return query.order_by(ProductionRecord.record_date.desc()).limit(limit).all()

@router.get("/dashboard-kpi", response_model=ProductionDashboardKPI)
def get_production_kpi(site_id: int, db: Session = Depends(get_db)):
    site = db.query(MineSite).filter(MineSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Mine site not found")

    records = db.query(ProductionRecord).filter(
        ProductionRecord.site_id == site_id
    ).order_by(ProductionRecord.record_date.desc()).limit(14).all()

    if not records:
        raise HTTPException(status_code=404, detail="No production records for this site")

    tot_planned = sum(r.planned_ore_tonnes for r in records)
    tot_actual = sum(r.actual_ore_tonnes for r in records)
    tot_shortfall = sum(r.shortfall_tonnes for r in records)
    tot_fuel = sum(r.fuel_consumed_liters for r in records)
    tot_cost = sum(r.operational_cost_inr for r in records)
    tot_waste = sum(r.actual_waste_tonnes for r in records)

    compliance_rate = round((tot_actual / tot_planned) * 100.0, 2) if tot_planned > 0 else 100.0
    actual_sr = round(tot_waste / tot_actual, 2) if tot_actual > 0 else 0.0
    cost_per_ton = round(tot_cost / tot_actual, 2) if tot_actual > 0 else 0.0
    fuel_eff = round(tot_actual / tot_fuel, 2) if tot_fuel > 0 else 0.0

    return ProductionDashboardKPI(
        site_name=site.name,
        date_range="Last 14 Operational Days",
        total_planned_ore_tonnes=round(tot_planned, 1),
        total_actual_ore_tonnes=round(tot_actual, 1),
        total_shortfall_tonnes=round(tot_shortfall, 1),
        compliance_rate_pct=compliance_rate,
        actual_stripping_ratio=actual_sr,
        target_stripping_ratio=site.target_stripping_ratio,
        active_fleet_count=records[0].active_trucks + records[0].active_shovels + records[0].active_pumps,
        fuel_efficiency_t_per_l=fuel_eff,
        total_operational_cost_inr=round(tot_cost, 2),
        cost_per_ton_inr=cost_per_ton,
        recent_records=records
    )
