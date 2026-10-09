from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Auth & User
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "surveyor"

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Mine Site
class MineSiteCreate(BaseModel):
    code: str
    name: str
    location: str
    state: str = "Jharkhand"
    mineral_type: str = "Coking Coal"
    crs: str = "EPSG:32644 (WGS 84 / UTM Zone 44N)"
    area_sq_km: float = 4.0
    boundary_geojson: Optional[Dict[str, Any]] = None
    benches_count: int = 12
    estimated_reserves_mt: float = 48.5
    target_stripping_ratio: float = 2.8

class MineSiteOut(BaseModel):
    id: int
    code: str
    name: str
    location: str
    state: str
    country: str
    mineral_type: str
    crs: str
    area_sq_km: float
    boundary_geojson: Optional[Dict[str, Any]] = None
    benches_count: int
    estimated_reserves_mt: float
    target_stripping_ratio: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Sensors & UAV Specs
class SensorSuiteInfo(BaseModel):
    sensor_id: str
    name: str
    category: str
    specs: Dict[str, Any]
    purpose: str
    is_active: bool = True

class DroneSystemSpecs(BaseModel):
    model_name: str
    vtol_capable: bool
    endurance_minutes: float
    coverage_area_sq_km_single_flight: float
    mapping_scale: str
    max_lidar_range_m: float
    elevation_deviation_cm: float
    ground_control_points_required: bool
    dual_rtk_gps_antennas: bool
    magnetic_field_interference_resistance: bool
    mission_time_4sqkm_min: float
    traditional_rtk_comparison: Dict[str, Any]
    sensors_available: List[SensorSuiteInfo]

# Survey
class SurveyCreate(BaseModel):
    site_id: int
    name: str
    uav_model: str = "CW-25E VTOL / JOUAV-LR-LR"
    sensors_enabled: List[str] = [
        "LiDAR 1350m (6cm precision)",
        "Five-Lens Oblique Camera",
        "EO/IR Thermal Gimbal",
        "Image Inspectometer",
        "RGB Mapping Camera"
    ]
    dual_rtk_gps: bool = True
    flight_area_sq_km: float = 4.0
    flight_altitude_m: float = 120.0
    flight_speed_m_s: float = 18.0
    line_spacing_m: float = 45.0
    polygon_geojson: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class MissionPlanRequest(BaseModel):
    site_id: int
    polygon_geojson: Dict[str, Any]
    altitude_m: float = 120.0
    speed_m_s: float = 18.0
    overlap_front_pct: float = 80.0
    overlap_side_pct: float = 70.0
    lidar_pulse_rate_khz: float = 500.0

class MissionPlanResponse(BaseModel):
    survey_area_sq_km: float
    estimated_flight_time_minutes: float
    total_flight_distance_km: float
    waypoint_count: int
    flight_lines_count: int
    line_spacing_m: float
    waypoints: List[Dict[str, Any]]
    sensor_config: Dict[str, Any]
    efficiency_vs_traditional_rtk: Dict[str, Any]

class SurveyOut(BaseModel):
    id: int
    site_id: int
    name: str
    survey_date: datetime
    uav_model: str
    sensors_enabled: List[str]
    dual_rtk_gps: bool
    scale_factor: str
    flight_area_sq_km: float
    flight_duration_minutes: float
    flight_altitude_m: float
    flight_speed_m_s: float
    line_spacing_m: float
    endurance_capacity_minutes: float
    max_lidar_range_m: float
    polygon_geojson: Optional[Dict[str, Any]] = None
    waypoints_geojson: Optional[Dict[str, Any]] = None
    point_density_pts_m2: float
    elevation_deviation_cm: float
    status: str
    surveyor_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Survey File
class SurveyFileOut(BaseModel):
    id: int
    survey_id: int
    filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    crs: str
    bounds_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Processing Jobs
class ProcessingJobCreate(BaseModel):
    survey_id: int
    job_type: str = "electromechanical_filter_dem"

class ProcessingJobOut(BaseModel):
    id: int
    survey_id: int
    job_type: str
    status: str
    progress_pct: float
    machinery_filtered_count: int
    elevation_deviation_cm: float
    log: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Terrain Model & Profiles
class TerrainModelOut(BaseModel):
    id: int
    site_id: int
    survey_id: int
    name: str
    grid_resolution_m: float
    elevation_min: float
    elevation_max: float
    mean_elevation: float
    bounds_json: Optional[Dict[str, Any]] = None
    stage_label: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TerrainProfileRequest(BaseModel):
    terrain_model_id: int
    name: str = "Bench Transect A-A'"
    line_geojson: Dict[str, Any]
    samples_count: int = 50

class TerrainProfileOut(BaseModel):
    id: int
    terrain_model_id: int
    name: str
    line_geojson: Dict[str, Any]
    distance_total_m: float
    elevation_min: float
    elevation_max: float
    max_slope_deg: float
    samples_json: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoadProfileRequest(BaseModel):
    terrain_model_id: int
    name: str = "Main Haul Road North Ramp"
    alignment_geojson: Dict[str, Any]
    max_allowed_slope_pct: float = 10.0
    min_safety_berm_m: float = 1.8

class RoadProfileOut(BaseModel):
    id: int
    terrain_model_id: int
    name: str
    alignment_geojson: Dict[str, Any]
    length_m: float
    avg_slope_pct: float
    max_slope_pct: float
    max_allowed_slope_pct: float
    safety_berm_height_m: float
    violations_count: int
    violations_json: Optional[List[Dict[str, Any]]] = None
    safety_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Cut & Fill and Volume Acceptance
class CutFillRequest(BaseModel):
    terrain_model_id: int
    name: str = "Pit Sector 3 Bench 5"
    reference_elevation_m: float = 240.0
    polygon_geojson: Optional[Dict[str, Any]] = None

class CutFillOut(BaseModel):
    name: str
    reference_elevation_m: float
    affected_area_sq_m: float
    cut_volume_m3: float
    fill_volume_m3: float
    net_volume_m3: float
    calculation_method: str

class VolumeComparisonRequest(BaseModel):
    site_id: int
    current_survey_id: int
    previous_survey_id: int
    area_name: str = "North Pit Bench 4-8 Stripping Acceptance"
    ore_density_t_m3: float = 2.65
    polygon_geojson: Optional[Dict[str, Any]] = None

class VolumeComparisonOut(BaseModel):
    id: int
    site_id: int
    current_survey_id: int
    previous_survey_id: int
    area_name: str
    comparison_method: str
    cut_volume_m3: float
    fill_volume_m3: float
    net_volume_m3: float
    stripping_volume_m3: float
    ore_extracted_volume_m3: float
    ore_density_t_m3: float
    total_ore_tonnage_t: float
    waste_tonnage_t: float
    elevation_deviation_cm: float
    acceptance_status: str
    accepted_by: str
    accepted_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VolumeAcceptanceAction(BaseModel):
    status: str = "ACCEPTED"  # ACCEPTED, REJECTED
    accepted_by: str
    remarks: Optional[str] = None

# Production & Equipment
class ProductionRecordOut(BaseModel):
    id: int
    site_id: int
    record_date: datetime
    planned_ore_tonnes: float
    actual_ore_tonnes: float
    planned_waste_tonnes: float
    actual_waste_tonnes: float
    stripping_ratio: float
    active_trucks: int
    active_shovels: int
    active_pumps: int
    fuel_consumed_liters: float
    operational_cost_inr: float
    weather_condition: str
    rainfall_mm: float
    shortfall_tonnes: float

    model_config = ConfigDict(from_attributes=True)

class ProductionDashboardKPI(BaseModel):
    site_name: str
    date_range: str
    total_planned_ore_tonnes: float
    total_actual_ore_tonnes: float
    total_shortfall_tonnes: float
    compliance_rate_pct: float
    actual_stripping_ratio: float
    target_stripping_ratio: float
    active_fleet_count: int
    fuel_efficiency_t_per_l: float
    total_operational_cost_inr: float
    cost_per_ton_inr: float
    recent_records: List[ProductionRecordOut]

class EquipmentFleetOut(BaseModel):
    id: int
    site_id: int
    equipment_code: str
    equipment_type: str
    model: str
    status: str
    operating_hours: float
    fuel_rate_l_h: float
    hourly_cost_inr: float
    gps_lat: float
    gps_lng: float
    telemetry_json: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

# What-If Simulator & AI Forecasting
class WhatIfScenarioRequest(BaseModel):
    site_id: int
    rainfall_mm: float = 0.0
    loss_ratio_pct: float = 0.0
    shovels_breakdown_count: int = 0
    haul_trucks_breakdown_count: int = 0
    fuel_price_hike_pct: float = 0.0

class WhatIfScenarioResponse(BaseModel):
    scenario_parameters: Dict[str, Any]
    baseline_production_tonnes_day: float
    simulated_production_tonnes_day: float
    projected_shortfall_tonnes: float
    shortfall_pct: float
    projected_additional_cost_inr: float
    fleet_availability_pct: float
    haul_cycle_delay_minutes: float
    pit_flooding_risk: str
    recommended_mitigations: List[str]

class ForecastOut(BaseModel):
    id: int
    site_id: int
    model_version: str
    forecast_date: datetime
    horizon_days: int
    baseline_target_tonnes: float
    predicted_tonnes: float
    predicted_shortfall_tonnes: float
    shortfall_pct: float
    risk_level: str
    daily_forecasts_json: List[Dict[str, Any]]
    contributing_factors_json: List[Dict[str, Any]]
    action_recommendations_json: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RiskCalendarOut(BaseModel):
    id: int
    site_id: int
    risk_date: str
    risk_category: str
    risk_score: float
    severity: str
    title: str
    description: Optional[str] = None
    mitigation_action: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# PDF & Excel Reports
class ReportRequest(BaseModel):
    site_id: int
    survey_id: Optional[int] = None
    report_type: str = "stripping_volume_acceptance"
    file_format: str = "pdf"  # "pdf" or "excel" / "xlsx"
    notes: Optional[str] = None

class ReportOut(BaseModel):
    id: int
    site_id: int
    survey_id: Optional[int] = None
    report_title: str
    report_type: str
    file_path: str
    file_size_bytes: int
    download_url: str
    generated_by: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
