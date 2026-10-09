from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="surveyor")  # surveyor, mine_manager, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

class MineSite(Base):
    __tablename__ = "mine_sites"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    state = Column(String(100), default="Jharkhand")
    country = Column(String(100), default="India")
    mineral_type = Column(String(100), default="Coking Coal")
    crs = Column(String(100), default="EPSG:32644 (WGS 84 / UTM Zone 44N)")
    area_sq_km = Column(Float, default=4.0)
    boundary_geojson = Column(JSON, nullable=True)
    benches_count = Column(Integer, default=12)
    estimated_reserves_mt = Column(Float, default=48.5)
    target_stripping_ratio = Column(Float, default=2.8)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=utcnow)

    surveys = relationship("Survey", back_populates="site", cascade="all, delete-orphan")
    production_records = relationship("ProductionRecord", back_populates="site", cascade="all, delete-orphan")
    equipment = relationship("EquipmentFleet", back_populates="site", cascade="all, delete-orphan")

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    name = Column(String(255), nullable=False)
    survey_date = Column(DateTime, default=utcnow)
    uav_model = Column(String(100), default="CW-25E VTOL / JOUAV-LR-LR")
    sensors_enabled = Column(JSON, default=lambda: [
        "LiDAR 1350m (6cm precision)",
        "Five-Lens Oblique Camera",
        "EO/IR Thermal Gimbal",
        "Image Inspectometer",
        "RGB Mapping Camera"
    ])
    dual_rtk_gps = Column(Boolean, default=True)  # Directional finding & magnetic resistance
    scale_factor = Column(String(50), default="1:1000")
    flight_area_sq_km = Column(Float, default=4.0)
    flight_duration_minutes = Column(Float, default=20.0)
    flight_altitude_m = Column(Float, default=120.0)
    flight_speed_m_s = Column(Float, default=18.0)
    line_spacing_m = Column(Float, default=45.0)
    endurance_capacity_minutes = Column(Float, default=120.0)
    max_lidar_range_m = Column(Float, default=1350.0)
    polygon_geojson = Column(JSON, nullable=True)
    waypoints_geojson = Column(JSON, nullable=True)
    point_density_pts_m2 = Column(Float, default=85.0)
    elevation_deviation_cm = Column(Float, default=6.0)  # 6cm deviation with no GCPs required
    status = Column(String(50), default="completed")  # planned, flying, completed, processing, accepted
    surveyor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    site = relationship("MineSite", back_populates="surveys")
    files = relationship("SurveyFile", back_populates="survey", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="survey", cascade="all, delete-orphan")
    terrains = relationship("TerrainModel", back_populates="survey", cascade="all, delete-orphan")

class SurveyFile(Base):
    __tablename__ = "survey_files"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # las, laz, geotiff, dem, orthophoto, oblique
    file_size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=False)
    crs = Column(String(100), default="EPSG:32644")
    bounds_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    survey = relationship("Survey", back_populates="files")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    job_type = Column(String(100), default="electromechanical_filter_dem")
    # lidar_filtering, dem_generation, differential_demodulation, volume_acceptance
    status = Column(String(50), default="completed")  # pending, running, completed, failed
    progress_pct = Column(Float, default=100.0)
    machinery_filtered_count = Column(Integer, default=34)  # Trucks, shovels, personnel filtered
    elevation_deviation_cm = Column(Float, default=5.8)
    log = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, default=utcnow)

    survey = relationship("Survey", back_populates="jobs")

class TerrainModel(Base):
    __tablename__ = "terrain_models"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    name = Column(String(255), nullable=False)
    grid_resolution_m = Column(Float, default=0.25)
    elevation_min = Column(Float, default=180.5)
    elevation_max = Column(Float, default=325.8)
    mean_elevation = Column(Float, default=246.3)
    bounds_json = Column(JSON, nullable=True)
    dem_matrix_json = Column(JSON, nullable=True)  # Grid data for rapid client interpolation
    stage_label = Column(String(50), default="stage_2_current")  # stage_1_previous, stage_2_current
    created_at = Column(DateTime, default=utcnow)

    survey = relationship("Survey", back_populates="terrains")

class VolumeComparison(Base):
    __tablename__ = "volume_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    current_survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    previous_survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    area_name = Column(String(255), default="North Pit Bench 4-8 Stripping Zone")
    comparison_method = Column(String(100), default="Two-Stage Differential Demodulation (LiDAR DEM vs Baseline)")
    cut_volume_m3 = Column(Float, default=142500.0)  # Excavation / stripping volume
    fill_volume_m3 = Column(Float, default=12400.0)   # Overburden dump / backfill volume
    net_volume_m3 = Column(Float, default=130100.0)
    stripping_volume_m3 = Column(Float, default=95400.0)
    ore_extracted_volume_m3 = Column(Float, default=34700.0)
    ore_density_t_m3 = Column(Float, default=2.65)   # Specific gravity
    total_ore_tonnage_t = Column(Float, default=91955.0)
    waste_tonnage_t = Column(Float, default=219420.0)
    elevation_deviation_cm = Column(Float, default=6.0)
    acceptance_status = Column(String(50), default="ACCEPTED")  # PENDING, ACCEPTED, REJECTED
    accepted_by = Column(String(255), default="Chief Mine Surveyor")
    accepted_at = Column(DateTime, default=utcnow)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

class TerrainProfile(Base):
    __tablename__ = "terrain_profiles"

    id = Column(Integer, primary_key=True, index=True)
    terrain_model_id = Column(Integer, ForeignKey("terrain_models.id"), nullable=False)
    name = Column(String(255), nullable=False)
    line_geojson = Column(JSON, nullable=False)
    distance_total_m = Column(Float, default=1250.0)
    elevation_min = Column(Float, default=195.0)
    elevation_max = Column(Float, default=310.0)
    max_slope_deg = Column(Float, default=32.4)
    samples_json = Column(JSON, nullable=False)  # [{distance_m, elevation_m, slope_deg}]
    created_at = Column(DateTime, default=utcnow)

class RoadProfile(Base):
    __tablename__ = "road_profiles"

    id = Column(Integer, primary_key=True, index=True)
    terrain_model_id = Column(Integer, ForeignKey("terrain_models.id"), nullable=False)
    name = Column(String(255), nullable=False)
    alignment_geojson = Column(JSON, nullable=False)
    length_m = Column(Float, default=2100.0)
    avg_slope_pct = Column(Float, default=7.8)
    max_slope_pct = Column(Float, default=11.2)
    max_allowed_slope_pct = Column(Float, default=10.0)  # DGMS Indian mining safety standard: <= 10% (1 in 10)
    safety_berm_height_m = Column(Float, default=1.8)     # Min DGMS requirement: Tyre radius of largest vehicle
    violations_count = Column(Integer, default=2)
    violations_json = Column(JSON, nullable=True)
    safety_status = Column(String(50), default="WARNING_SLOPE_EXCEEDED")  # SAFE, WARNING, CRITICAL
    created_at = Column(DateTime, default=utcnow)

class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    record_date = Column(DateTime, default=utcnow)
    planned_ore_tonnes = Column(Float, default=15000.0)
    actual_ore_tonnes = Column(Float, default=13850.0)
    planned_waste_tonnes = Column(Float, default=37500.0)
    actual_waste_tonnes = Column(Float, default=34900.0)
    stripping_ratio = Column(Float, default=2.52)
    active_trucks = Column(Integer, default=28)
    active_shovels = Column(Integer, default=6)
    active_pumps = Column(Integer, default=4)
    fuel_consumed_liters = Column(Float, default=14200.0)
    operational_cost_inr = Column(Float, default=2850000.0)
    weather_condition = Column(String(100), default="Clear / Dry")
    rainfall_mm = Column(Float, default=0.0)
    shortfall_tonnes = Column(Float, default=1150.0)

    site = relationship("MineSite", back_populates="production_records")

class EquipmentFleet(Base):
    __tablename__ = "equipment_fleet"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    equipment_type = Column(String(50), nullable=False)  # haul_truck, excavator_shovel, dewatering_pump, vtol_drone
    model = Column(String(100), nullable=False)
    status = Column(String(50), default="active")  # active, standby, maintenance, breakdown
    operating_hours = Column(Float, default=3420.0)
    fuel_rate_l_h = Column(Float, default=48.5)
    hourly_cost_inr = Column(Float, default=9500.0)
    gps_lat = Column(Float, default=23.754)
    gps_lng = Column(Float, default=86.412)
    telemetry_json = Column(JSON, nullable=True)

    site = relationship("MineSite", back_populates="equipment")

class ProductionForecast(Base):
    __tablename__ = "production_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    model_version = Column(String(100), default="XGBoost-14D-Production-v3.1")
    forecast_date = Column(DateTime, default=utcnow)
    horizon_days = Column(Integer, default=14)
    baseline_target_tonnes = Column(Float, default=210000.0)
    predicted_tonnes = Column(Float, default=192400.0)
    predicted_shortfall_tonnes = Column(Float, default=17600.0)
    shortfall_pct = Column(Float, default=8.38)
    risk_level = Column(String(50), default="HIGH_RISK")  # LOW, MEDIUM, HIGH, CRITICAL
    daily_forecasts_json = Column(JSON, nullable=False)
    contributing_factors_json = Column(JSON, nullable=False)
    action_recommendations_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow)

class RiskCalendarEntry(Base):
    __tablename__ = "risk_calendar"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    risk_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    risk_category = Column(String(100), nullable=False)  # weather_rain, shovel_breakdown, slope_instability
    risk_score = Column(Float, default=65.0)  # 0-100
    severity = Column(String(20), default="amber")  # green, amber, red
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    mitigation_action = Column(Text, nullable=True)

class ReportRecord(Base):
    __tablename__ = "report_records"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("mine_sites.id"), nullable=False)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=True)
    report_title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    generated_by = Column(String(255), default="System AI Engine")
    status = Column(String(50), default="ready")
    created_at = Column(DateTime, default=utcnow)
