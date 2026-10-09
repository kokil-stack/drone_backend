from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.schemas_db import ProductionForecast, RiskCalendarEntry, MineSite
from app.schemas.schemas import ForecastOut, RiskCalendarOut
from app.services.production_forecast import generate_14day_xgboost_forecast

router = APIRouter(prefix="/forecast", tags=["AI Shortfall Forecasting & Risk Calendar"])

@router.get("/14-day", response_model=ForecastOut)
def get_latest_forecast(site_id: int, db: Session = Depends(get_db)):
    fc = db.query(ProductionForecast).filter(
        ProductionForecast.site_id == site_id
    ).order_by(ProductionForecast.created_at.desc()).first()

    if not fc:
        # Generate on the fly
        site = db.query(MineSite).filter(MineSite.id == site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail="Mine site not found")
        data = generate_14day_xgboost_forecast()
        fc = ProductionForecast(
            site_id=site_id,
            model_version=data["model_version"],
            forecast_date=datetime.now(timezone.utc),
            horizon_days=14,
            baseline_target_tonnes=data["baseline_target_tonnes"],
            predicted_tonnes=data["predicted_tonnes"],
            predicted_shortfall_tonnes=data["predicted_shortfall_tonnes"],
            shortfall_pct=data["shortfall_pct"],
            risk_level=data["risk_level"],
            daily_forecasts_json=data["daily_forecasts"],
            contributing_factors_json=data["contributing_factors"],
            action_recommendations_json=data["action_recommendations"]
        )
        db.add(fc)
        db.commit()
        db.refresh(fc)

    return fc

@router.get("/risk-calendar", response_model=List[RiskCalendarOut])
def get_risk_calendar(site_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    query = db.query(RiskCalendarEntry)
    if site_id is not None:
        query = query.filter(RiskCalendarEntry.site_id == site_id)
    return query.order_by(RiskCalendarEntry.risk_date.asc()).all()
