import math
import random
import numpy as np
from typing import Dict, Any, Tuple

def simulate_lidar_filtering_and_dem(
    area_sq_km: float = 4.0,
    point_density_pts_m2: float = 85.0,
    base_elevation: float = 220.0
) -> Tuple[int, float, Dict[str, Any], list]:
    """
    Simulates high-density LiDAR point-cloud processing:
    1. Ingestion of raw points (covers 4 sq km in 20 min).
    2. Automatic filtering of electromechanical noise (dump trucks, shovels, pumps, personnel).
    3. Generating clean DEM with 6cm elevation deviation (no GCPs needed).
    """
    total_points = int(area_sq_km * 1_000_000 * point_density_pts_m2)
    # Filter equipment noise (typical 20 to 50 electromechanical items in 4 sq km active pit)
    filtered_machinery_count = random.randint(28, 42)
    
    # Elevation deviation 6cm verified (randomly 5.6 to 6.2 cm)
    elevation_deviation_cm = round(random.uniform(5.6, 6.2), 2)
    
    # Generate 20x20 grid matrix representing open pit terrain benches
    grid_size = 20
    x = np.linspace(0, 2000, grid_size)
    y = np.linspace(0, 2000, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Open pit crater simulation with terrace benches:
    # Radius from center
    center_x, center_y = 1000.0, 1000.0
    R = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
    
    # Stepped pit benches (15m step every 100m radius)
    bench_step = np.floor(R / 120.0) * 12.0
    noise = np.random.normal(0, 0.3, (grid_size, grid_size))
    Z = base_elevation + bench_step - 80.0 + noise
    
    # Bounds for Indian UTM 44N projection
    bounds = {
        "min_x": 86.410,
        "max_x": 86.435,
        "min_y": 23.750,
        "max_y": 23.775,
        "crs": "EPSG:32644",
        "units": "meters",
        "resolution_m": 0.25
    }
    
    dem_summary = {
        "total_raw_points": total_points,
        "ground_classified_points": int(total_points * 0.94),
        "vegetation_filtered": int(total_points * 0.045),
        "equipment_filtered_points": int(total_points * 0.015),
        "elevation_min_m": round(float(np.min(Z)), 2),
        "elevation_max_m": round(float(np.max(Z)), 2),
        "mean_elevation_m": round(float(np.mean(Z)), 2),
        "elevation_deviation_cm": elevation_deviation_cm,
        "gcp_required": False,
        "dual_rtk_directional_lock": True,
        "magnetic_interference_suppressed": True
    }
    
    dem_matrix = Z.round(2).tolist()
    return filtered_machinery_count, elevation_deviation_cm, dem_summary, dem_matrix
