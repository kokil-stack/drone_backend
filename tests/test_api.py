import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "6cm" in data["lidar_precision"]

def test_auth_login():
    response = client.post("/api/auth/login", json={
        "email": "surveyor@digitalmine.in",
        "password": "mine1234"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "surveyor"

def test_get_mine_sites():
    response = client.get("/api/sites")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    codes = [s["code"] for s in data]
    assert "JHARIA-PIT07" in codes
    assert "BAILA-DEP14" in codes

def test_sensor_suite_and_uav_specs():
    response = client.get("/api/sensors/system-specs")
    assert response.status_code == 200
    data = response.json()
    assert data["vtol_capable"] is True
    assert data["endurance_minutes"] >= 120.0
    assert data["elevation_deviation_cm"] == 6.0
    assert data["mission_time_4sqkm_min"] == 20.0
    assert len(data["sensors_available"]) == 5

def test_mission_planning():
    response = client.post("/api/surveys/plan-mission", json={
        "site_id": 1,
        "polygon_geojson": {"type": "Polygon", "coordinates": []},
        "altitude_m": 120.0,
        "speed_m_s": 18.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["survey_area_sq_km"] == 4.0
    assert data["estimated_flight_time_minutes"] > 0
    assert len(data["waypoints"]) > 0

def test_survey_telemetry():
    surveys = client.get("/api/surveys").json()
    assert len(surveys) > 0
    s_id = surveys[0]["id"]
    response = client.get(f"/api/surveys/{s_id}/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["dual_differential_gps_lock"] is True
    assert data["satellites_tracked"] >= 30

def test_processing_job_filtering():
    surveys = client.get("/api/surveys").json()
    s_id = surveys[0]["id"]
    response = client.post("/api/processing-jobs", json={
        "survey_id": s_id,
        "job_type": "electromechanical_filter_dem"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["machinery_filtered_count"] > 0
    assert 5.0 <= data["elevation_deviation_cm"] <= 6.5

def test_terrain_profile_analysis():
    terrains = client.get("/api/terrain").json()
    assert len(terrains) > 0
    t_id = terrains[0]["id"]
    response = client.post("/api/analysis/terrain-profile", json={
        "terrain_model_id": t_id,
        "name": "Pit Transect Test",
        "line_geojson": {"coordinates": [[86.415, 23.755], [86.430, 23.770]]},
        "samples_count": 30
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["samples_json"]) == 30
    assert data["distance_total_m"] > 0

def test_road_profile_dgms_compliance():
    terrains = client.get("/api/terrain").json()
    t_id = terrains[0]["id"]
    response = client.post("/api/analysis/road-profile", json={
        "terrain_model_id": t_id,
        "name": "Haul Ramp Check",
        "alignment_geojson": {"coordinates": []},
        "max_allowed_slope_pct": 10.0,
        "min_safety_berm_m": 1.8
    })
    assert response.status_code == 200
    data = response.json()
    assert data["safety_berm_height_m"] == 1.8
    assert "safety_status" in data

def test_cut_fill_analysis():
    terrains = client.get("/api/terrain").json()
    t_id = terrains[0]["id"]
    response = client.post("/api/analysis/cut-fill", json={
        "terrain_model_id": t_id,
        "name": "Bench Cut Fill",
        "reference_elevation_m": 240.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["cut_volume_m3"] > 0

def test_volume_comparison_and_acceptance():
    surveys = client.get("/api/surveys").json()
    assert len(surveys) >= 2
    s1, s2 = surveys[0]["id"], surveys[1]["id"]
    response = client.post("/api/analysis/volume-comparison", json={
        "site_id": 1,
        "current_survey_id": s1,
        "previous_survey_id": s2,
        "area_name": "Test Stripping Bench 6-8",
        "ore_density_t_m3": 2.65
    })
    assert response.status_code == 200
    data = response.json()
    assert data["stripping_volume_m3"] > 0
    assert data["total_ore_tonnage_t"] > 0
    assert data["elevation_deviation_cm"] == 6.0

    # Test acceptance sign-off
    comp_id = data["id"]
    acc_res = client.patch(f"/api/analysis/volume-comparison/{comp_id}/acceptance", json={
        "status": "ACCEPTED",
        "accepted_by": "Mine General Manager Col. Verma",
        "remarks": "Volume certified with LiDAR 6cm precision."
    })
    assert acc_res.status_code == 200
    assert acc_res.json()["acceptance_status"] == "ACCEPTED"

def test_production_kpis():
    response = client.get("/api/production/dashboard-kpi?site_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total_actual_ore_tonnes"] > 0
    assert data["compliance_rate_pct"] > 0

def test_what_if_simulation():
    response = client.post("/api/simulations/run", json={
        "site_id": 1,
        "rainfall_mm": 35.0,
        "shovels_breakdown_count": 1,
        "haul_trucks_breakdown_count": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert data["projected_shortfall_tonnes"] > 0
    assert len(data["recommended_mitigations"]) > 0

def test_14day_forecast():
    response = client.get("/api/forecast/14-day?site_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_days"] == 14
    assert len(data["daily_forecasts_json"]) == 14

def test_report_generation_and_download():
    response = client.post("/api/reports/generate", json={
        "site_id": 1,
        "report_type": "stripping_volume_acceptance"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["download_url"].startswith("/api/reports/download/")

    # Test downloading the PDF
    dl_res = client.get(data["download_url"])
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert len(dl_res.content) > 1000  # valid PDF generated

    # Test generating Excel format
    res_xl = client.post("/api/reports/generate", json={
        "site_id": 1,
        "report_type": "stripping_volume_acceptance",
        "file_format": "excel"
    })
    assert res_xl.status_code == 200
    xl_data = res_xl.json()
    assert xl_data["download_url"].endswith(".xlsx")

    # Test downloading the Excel file
    dl_xl = client.get(xl_data["download_url"])
    assert dl_xl.status_code == 200
    assert "openxmlformats" in dl_xl.headers["content-type"]
    assert len(dl_xl.content) > 2000  # valid multi-sheet Excel generated

    # Test direct export-excel endpoint
    exp_res = client.get("/api/reports/export-excel?site_id=1")
    assert exp_res.status_code == 200
    assert "openxmlformats" in exp_res.headers["content-type"]

def test_google_earth_engine_endpoints():
    # Status
    res_status = client.get("/api/earth-engine/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert "sdk_installed" in status_data
    assert "provider" in status_data
    assert len(status_data["supported_datasets"]) >= 5

    # Layers
    res_layers = client.get("/api/earth-engine/layers?lat=23.762&lng=86.422")
    assert res_layers.status_code == 200
    layers_data = res_layers.json()
    assert "google_satellite" in layers_data["basemaps"]
    assert "sentinel2_ndvi" in layers_data["gee_overlays"]
    assert "thermal_coal_fire" in layers_data["gee_overlays"]

    # Inspect Pixel
    res_inspect = client.get("/api/earth-engine/inspect?lat=23.762&lng=86.422&site_id=1")
    assert res_inspect.status_code == 200
    inspect_data = res_inspect.json()
    assert "ndvi_score" in inspect_data
    assert "srtm_elevation_m" in inspect_data
    assert "surface_temperature_celsius" in inspect_data
    assert "bands" in inspect_data
    assert "B8_NIR" in inspect_data["bands"]

    # Thermal hazards
    res_thermal = client.get("/api/earth-engine/thermal-hazards?lat=23.762&lng=86.422")
    assert res_thermal.status_code == 200
    thermal_data = res_thermal.json()
    assert thermal_data["total_hotspots_detected"] > 0
    assert len(thermal_data["hotspots"]) > 0

    # Environmental reclamation
    res_reclamation = client.get("/api/earth-engine/reclamation?site_id=1")
    assert res_reclamation.status_code == 200
    reclamation_data = res_reclamation.json()
    assert reclamation_data["lease_area_hectares"] == 400.0
    assert reclamation_data["reclamation_progress_pct"] > 0

    # NDVI Time Series
    res_ts = client.get("/api/earth-engine/ndvi-timeseries?site_id=1")
    assert res_ts.status_code == 200
    ts_data = res_ts.json()
    assert ts_data["observation_count"] > 0
    assert len(ts_data["historical_timeline"]) > 0
    assert "net_gain_hectares" in ts_data

    # Authenticate
    res_auth = client.post("/api/earth-engine/authenticate", json={"project_id": "test-gee-project"})
    assert res_auth.status_code == 200
    auth_data = res_auth.json()
    assert auth_data["project_id"] == "test-gee-project"

