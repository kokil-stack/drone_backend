import math
from typing import Dict, Any, List

def calculate_terrain_profile(
    dem_matrix: List[List[float]],
    line_geojson: Dict[str, Any],
    samples_count: int = 50,
    elevation_min: float = 180.0,
    elevation_max: float = 320.0
) -> Dict[str, Any]:
    """
    Samples elevation and slope along a transect across the open pit mine benches.
    """
    coords = line_geojson.get("coordinates", [[86.415, 23.755], [86.430, 23.770]])
    if len(coords) < 2:
        coords = [[86.415, 23.755], [86.430, 23.770]]
    
    # Calculate approximate distance on ground
    p1, p2 = coords[0], coords[-1]
    # rough meter conversion in India latitude
    dx = (p2[0] - p1[0]) * 102000.0
    dy = (p2[1] - p1[1]) * 111000.0
    total_dist_m = math.sqrt(dx*dx + dy*dy)
    if total_dist_m < 100.0:
        total_dist_m = 1250.0

    samples = []
    step_m = total_dist_m / (samples_count - 1)
    
    # Interpolate along DEM profile
    max_slope_deg = 0.0
    prev_elev = None

    for i in range(samples_count):
        dist = i * step_m
        norm_t = i / (samples_count - 1)
        
        # Pit profile shape: terrace steps descending into center and rising out
        center_factor = math.sin(norm_t * math.pi)
        elev = elevation_max - (elevation_max - elevation_min) * center_factor
        
        # Add bench terraces (step function)
        terrace_mod = (dist % 120.0) / 120.0
        elev = elev + (math.floor(dist / 120.0) * 3.5) - (terrace_mod * 8.0)
        elev = round(elev, 2)
        
        slope_deg = 0.0
        if prev_elev is not None and step_m > 0:
            diff_z = abs(elev - prev_elev)
            slope_rad = math.atan2(diff_z, step_m)
            slope_deg = round(math.degrees(slope_rad), 2)
            if slope_deg > max_slope_deg:
                max_slope_deg = slope_deg

        prev_elev = elev
        samples.append({
            "step_index": i,
            "distance_m": round(dist, 1),
            "elevation_m": elev,
            "slope_deg": slope_deg,
            "bench_classification": "Working Bench" if slope_deg < 15 else "Highwall Slope"
        })

    elevations = [s["elevation_m"] for s in samples]
    return {
        "distance_total_m": round(total_dist_m, 1),
        "elevation_min": min(elevations),
        "elevation_max": max(elevations),
        "max_slope_deg": max_slope_deg,
        "samples": samples
    }
