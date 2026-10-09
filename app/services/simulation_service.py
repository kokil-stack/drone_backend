from typing import Dict, Any, List

def run_what_if_simulation(
    baseline_production_tonnes_day: float = 15000.0,
    rainfall_mm: float = 0.0,
    loss_ratio_pct: float = 0.0,
    shovels_breakdown_count: int = 0,
    haul_trucks_breakdown_count: int = 0,
    fuel_price_hike_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Simulates operational impact of user-defined what-if parameters:
    rain, equipment breakdowns, ore loss ratio, and fuel cost spikes.
    """
    # Base daily parameters
    active_shovels = 6
    active_trucks = 28
    
    # Capacity penalties
    shovel_loss_factor = min(1.0, (shovels_breakdown_count / active_shovels) * 0.9)
    truck_loss_factor = min(1.0, (haul_trucks_breakdown_count / active_trucks) * 0.75)
    
    # Rainfall effect: slippery roads, sump filling
    rain_loss_factor = min(0.60, (rainfall_mm / 100.0) * 0.8) if rainfall_mm > 0 else 0.0
    
    # Grade & dilution loss ratio
    loss_ratio_factor = (loss_ratio_pct / 100.0)
    
    total_reduction = min(0.85, shovel_loss_factor + truck_loss_factor + rain_loss_factor + loss_ratio_factor)
    simulated_production = round(baseline_production_tonnes_day * (1.0 - total_reduction), 1)
    projected_shortfall = round(baseline_production_tonnes_day - simulated_production, 1)
    shortfall_pct = round((projected_shortfall / baseline_production_tonnes_day) * 100.0, 2)
    
    # Additional financial cost (idle equipment + diesel surge + shortfall penalty)
    fuel_extra = (fuel_price_hike_pct / 100.0) * 14200.0 * 95.0  # liters * INR/liter
    breakdown_idling_cost = (shovels_breakdown_count * 250000.0) + (haul_trucks_breakdown_count * 80000.0)
    projected_additional_cost_inr = round(fuel_extra + breakdown_idling_cost + (projected_shortfall * 180.0), 2)
    
    # Fleet availability
    fleet_avail = round((( (active_shovels - shovels_breakdown_count) / active_shovels ) * 0.35 + 
                          ( (active_trucks - haul_trucks_breakdown_count) / active_trucks ) * 0.65) * 100.0, 1)
                          
    haul_cycle_delay = round(18.0 + (rainfall_mm * 0.25) + (haul_trucks_breakdown_count * 0.8), 1)
    
    flooding_risk = "NORMAL"
    if rainfall_mm > 40.0:
        flooding_risk = "HIGH_PIT_FLOODING_RISK"
    elif rainfall_mm > 15.0:
        flooding_risk = "MODERATE_WATER_INGRESS"
        
    mitigations = []
    if shovels_breakdown_count > 0:
        mitigations.append(f"Deploy mobile field maintenance crew to repair {shovels_breakdown_count} shovel(s); reroute dump trucks to active face.")
    if rainfall_mm > 10.0:
        mitigations.append("Activate secondary sump drainage pumps (min 500 m3/hr capacity) and apply gravel crushed stone on ramp switchbacks.")
    if haul_trucks_breakdown_count > 2:
        mitigations.append("Commission contracted backup tippers to maintain crusher throughput.")
    if shortfall_pct > 10.0:
        mitigations.append("Extend afternoon shift by 1.5 hours and utilize surge stockpile at secondary crusher.")

    return {
        "scenario_parameters": {
            "rainfall_mm": rainfall_mm,
            "loss_ratio_pct": loss_ratio_pct,
            "shovels_breakdown_count": shovels_breakdown_count,
            "haul_trucks_breakdown_count": haul_trucks_breakdown_count,
            "fuel_price_hike_pct": fuel_price_hike_pct
        },
        "baseline_production_tonnes_day": baseline_production_tonnes_day,
        "simulated_production_tonnes_day": simulated_production,
        "projected_shortfall_tonnes": projected_shortfall,
        "shortfall_pct": shortfall_pct,
        "projected_additional_cost_inr": projected_additional_cost_inr,
        "fleet_availability_pct": fleet_avail,
        "haul_cycle_delay_minutes": haul_cycle_delay,
        "pit_flooding_risk": flooding_risk,
        "recommended_mitigations": mitigations
    }
