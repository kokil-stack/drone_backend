from fastapi import APIRouter
from app.schemas.schemas import WhatIfScenarioRequest, WhatIfScenarioResponse
from app.services.simulation_service import run_what_if_simulation

router = APIRouter(prefix="/simulations", tags=["What-If Simulator"])

@router.post("/run", response_model=WhatIfScenarioResponse)
def run_simulation(req: WhatIfScenarioRequest):
    return run_what_if_simulation(
        baseline_production_tonnes_day=15000.0,
        rainfall_mm=req.rainfall_mm,
        loss_ratio_pct=req.loss_ratio_pct,
        shovels_breakdown_count=req.shovels_breakdown_count,
        haul_trucks_breakdown_count=req.haul_trucks_breakdown_count,
        fuel_price_hike_pct=req.fuel_price_hike_pct
    )
