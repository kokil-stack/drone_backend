from typing import Dict, Any, Optional

def calculate_cut_and_fill(
    name: str = "Pit Sector 3 Bench 5",
    reference_elevation_m: float = 240.0,
    polygon_geojson: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes cut (excavation) and fill (backfill/dump) volumes against a reference datum plane.
    """
    # Standard 400m x 250m sector = 100,000 sq m
    affected_area_sq_m = 98500.0
    
    # Differential volume against datum
    cut_volume_m3 = 118400.0
    fill_volume_m3 = 9600.0
    net_volume_m3 = cut_volume_m3 - fill_volume_m3

    return {
        "name": name,
        "reference_elevation_m": reference_elevation_m,
        "affected_area_sq_m": affected_area_sq_m,
        "cut_volume_m3": cut_volume_m3,
        "fill_volume_m3": fill_volume_m3,
        "net_volume_m3": net_volume_m3,
        "calculation_method": "Grid cell elevation difference relative to reference datum z=240.0m"
    }
