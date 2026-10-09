from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

def generate_14day_xgboost_forecast(
    daily_target_tonnes: float = 15000.0,
    active_shovels: int = 6,
    active_trucks: int = 28,
    recent_rainfall_mm: float = 0.0
) -> Dict[str, Any]:
    """
    Simulates XGBoost 14-day production shortfall forecasting pipeline.
    Factors in weather projections, fleet availability, haul road gradient, and historical shift performance.
    """
    start_date = datetime.now(timezone.utc)
    daily_forecasts = []
    
    total_baseline = daily_target_tonnes * 14
    total_predicted = 0.0
    
    # Weather profile across 14 days (monsoon rain simulation on days 5-8)
    rainfall_profile = [0.0, 0.0, 2.5, 5.0, 32.0, 48.5, 22.0, 8.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    
    for i in range(14):
        f_date = start_date + timedelta(days=i + 1)
        rain = rainfall_profile[i]
        
        # Degradation factor based on rain and shovel load
        weather_penalty = min(0.45, (rain / 60.0) * 0.40)
        breakdown_risk = 0.05 if i not in [5, 6] else 0.12
        
        predicted_day_tonnes = daily_target_tonnes * (1.0 - weather_penalty - breakdown_risk)
        predicted_day_tonnes = round(max(5000.0, predicted_day_tonnes), 1)
        total_predicted += predicted_day_tonnes
        
        day_shortfall = round(max(0.0, daily_target_tonnes - predicted_day_tonnes), 1)
        risk_tag = "LOW" if day_shortfall < 1500 else ("MEDIUM" if day_shortfall < 4000 else "HIGH")
        
        daily_forecasts.append({
            "day": i + 1,
            "date": f_date.strftime("%Y-%m-%d"),
            "target_tonnes": daily_target_tonnes,
            "predicted_tonnes": predicted_day_tonnes,
            "shortfall_tonnes": day_shortfall,
            "rainfall_forecast_mm": rain,
            "truck_utilization_pct": round(92.0 - (rain * 0.6), 1),
            "risk_level": risk_tag
        })

    predicted_shortfall = round(total_baseline - total_predicted, 1)
    shortfall_pct = round((predicted_shortfall / total_baseline) * 100.0, 2)
    risk_level = "HIGH_RISK" if shortfall_pct > 7.0 else "MODERATE_RISK"

    contributing_factors = [
        {"factor": "Monsoon Rainfall Event (Days 5-7)", "impact_pct": 52.0, "description": "Haul road slipperiness slows cycle times from 18 min to 26 min."},
        {"factor": "Excavator Shovel #3 Scheduled Overhaul", "impact_pct": 28.0, "description": "35-ton hydraulic shovel maintenance outage reduces bench loading capacity."},
        {"factor": "North Ramp Gradient Steepness (11.2%)", "impact_pct": 20.0, "description": "Payload derating on overloaded dumpers climbing gradient."}
    ]

    action_recommendations = [
        {"priority": "URGENT", "action": "Pre-deploy submersible dewatering pumps in Sump Bench 9 before Day 5 rainfall."},
        {"priority": "HIGH", "action": "Re-dispatch 4 reserve 100-ton dump trucks from overburden to ore face on Days 1-4 to build ROM surge stockpile."},
        {"priority": "MEDIUM", "action": "Re-grade switchback hairpin at Chainage 950m with motorized grader to restore <=10% gradient."}
    ]

    return {
        "model_version": "XGBoost-14D-Production-v3.1",
        "horizon_days": 14,
        "baseline_target_tonnes": total_baseline,
        "predicted_tonnes": round(total_predicted, 1),
        "predicted_shortfall_tonnes": predicted_shortfall,
        "shortfall_pct": shortfall_pct,
        "risk_level": risk_level,
        "daily_forecasts": daily_forecasts,
        "contributing_factors": contributing_factors,
        "action_recommendations": action_recommendations
    }
