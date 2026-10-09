from fastapi import APIRouter
from app.schemas.schemas import DroneSystemSpecs, SensorSuiteInfo

router = APIRouter(prefix="/sensors", tags=["UAV & Sensor Suite"])

@router.get("/system-specs", response_model=DroneSystemSpecs)
def get_system_specs():
    sensors = [
        SensorSuiteInfo(
            sensor_id="SEN-LIDAR-1350",
            name="Long-Range High-Density LiDAR System",
            category="LiDAR",
            specs={
                "max_range_m": 1350.0,
                "elevation_deviation_cm": 6.0,
                "pulse_rate_khz": 500.0,
                "returns_per_pulse": 4,
                "day_night_capability": True,
                "gcp_required": False
            },
            purpose="High-density point cloud data collection and precise terrain 3D mapping with 6cm elevation deviation."
        ),
        SensorSuiteInfo(
            sensor_id="SEN-OBLIQUE-5L",
            name="Five-Lens Oblique Photogrammetry Camera",
            category="Photogrammetry",
            specs={
                "lenses": 5,
                "total_resolution_mp": 120,
                "focal_length_mm": "25mm nadir / 35mm oblique",
                "shutter_speed_s": "1/2000s"
            },
            purpose="Detailed aerial photography and high-fidelity 3D digital twin mesh modeling of open-pit benches."
        ),
        SensorSuiteInfo(
            sensor_id="SEN-INSPECT-01",
            name="Image Inspectometer",
            category="Optical Inspection",
            specs={
                "zoom_optical": "30x",
                "ai_edge_defect_detection": True,
                "crack_detection_mm": 2.0
            },
            purpose="Dynamic monitoring, highwall slope stability, tension crack identification, and mine disaster investigation."
        ),
        SensorSuiteInfo(
            sensor_id="SEN-EOIR-GIMBAL",
            name="EO/IR Dual Stabilized Gimbal",
            category="Thermal & Night Vision",
            specs={
                "optical_eo_resolution": "4K Ultra-HD",
                "thermal_ir_resolution": "640x512 Radiometric",
                "temperature_sensitivity_mk": 40,
                "thermal_range_c": "-20 to 550"
            },
            purpose="Thermal coal fire detection, equipment overheating inspection, and round-the-clock day/night operation."
        ),
        SensorSuiteInfo(
            sensor_id="SEN-RGB-MAP",
            name="RGB High-Resolution Topographic Mapping Camera",
            category="Orthophoto Mapping",
            specs={
                "resolution_mp": 61,
                "sensor_format": "Full Frame (35.7 x 23.8 mm)",
                "gsd_at_120m_cm_px": 1.5
            },
            purpose="1:1000 scale high-resolution topographic surveying, orthomosaic generation, and environmental restoration tracking."
        )
    ]

    return DroneSystemSpecs(
        model_name="JOUAV CW-25E / DJI Enterprise VTOL Hybrid",
        vtol_capable=True,
        endurance_minutes=120.0,
        coverage_area_sq_km_single_flight=40.0,
        mapping_scale="1:1000",
        max_lidar_range_m=1350.0,
        elevation_deviation_cm=6.0,
        ground_control_points_required=False,
        dual_rtk_gps_antennas=True,
        magnetic_field_interference_resistance=True,
        mission_time_4sqkm_min=20.0,
        traditional_rtk_comparison={
            "traditional_method": "Manual GPS-RTK Ground Survey",
            "traditional_technicians_required": 6,
            "traditional_field_days": 8,
            "traditional_data_processing_days": 4,
            "traditional_point_spacing_m": "5-20 meters with 2-3m dangerous bench standoff",
            "traditional_pitfall": "Regular plane interpolation failing to capture true terrain undulations",
            "drone_solution_field_time_min": 20,
            "drone_solution_point_density": "85+ pts/m² LiDAR point cloud",
            "time_saved_multiplier": "120x faster data acquisition"
        },
        sensors_available=sensors
    )
