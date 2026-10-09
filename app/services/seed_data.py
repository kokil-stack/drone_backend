from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.schemas_db import (
    User, MineSite, Survey, ProcessingJob, TerrainModel,
    VolumeComparison, TerrainProfile, RoadProfile,
    ProductionRecord, EquipmentFleet, ProductionForecast,
    RiskCalendarEntry
)
from app.services.point_cloud import simulate_lidar_filtering_and_dem
from app.services.terrain_profile import calculate_terrain_profile
from app.services.road_profile import calculate_road_profile

def seed_database_if_empty(db: Session):
    # Check if users exist
    if db.query(User).first():
        return

    # 1. Seed Users
    surveyor_user = User(
        email="surveyor@digitalmine.in",
        hashed_password=get_password_hash("mine1234"),
        full_name="Rajesh Sharma (Lead UAV Surveyor)",
        role="surveyor",
        is_active=True
    )
    manager_user = User(
        email="manager@digitalmine.in",
        hashed_password=get_password_hash("mine1234"),
        full_name="Col. Arvind Verma (General Mine Manager)",
        role="mine_manager",
        is_active=True
    )
    admin_user = User(
        email="admin@digitalmine.in",
        hashed_password=get_password_hash("mine1234"),
        full_name="System Administrator",
        role="admin",
        is_active=True
    )
    db.add_all([surveyor_user, manager_user, admin_user])
    db.commit()

    # 2. Seed Mine Sites (Indian Open-Pit Mines)
    sites_data = [
        {
            "code": "JHARIA-PIT07",
            "name": "Jharia Coking Coalfield Pit #7",
            "location": "Dhanbad Basin, Jharkhand",
            "state": "Jharkhand",
            "mineral_type": "Prime Coking Coal",
            "crs": "EPSG:32644 (WGS 84 / UTM Zone 44N)",
            "area_sq_km": 4.0,
            "benches_count": 14,
            "estimated_reserves_mt": 54.2,
            "target_stripping_ratio": 2.85,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[86.410, 23.750], [86.435, 23.750], [86.435, 23.775], [86.410, 23.775], [86.410, 23.750]]]
            }
        },
        {
            "code": "BAILA-DEP14",
            "name": "Bailadila Iron Ore Deposit 14",
            "location": "Dantewada, Bastar Plateau",
            "state": "Chhattisgarh",
            "mineral_type": "High-Grade Hematite Iron Ore (65% Fe)",
            "crs": "EPSG:32644 (WGS 84 / UTM Zone 44N)",
            "area_sq_km": 6.5,
            "benches_count": 18,
            "estimated_reserves_mt": 120.0,
            "target_stripping_ratio": 1.95,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[81.220, 18.680], [81.250, 18.680], [81.250, 18.710], [81.220, 18.710], [81.220, 18.680]]]
            }
        },
        {
            "code": "SUKINDA-CHR02",
            "name": "Sukinda Valley Chromite Open Cast",
            "location": "Jajpur District, Odisha",
            "state": "Odisha",
            "mineral_type": "Metallurgical Chromite",
            "crs": "EPSG:32645 (WGS 84 / UTM Zone 45N)",
            "area_sq_km": 3.8,
            "benches_count": 12,
            "estimated_reserves_mt": 28.5,
            "target_stripping_ratio": 3.40,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[85.780, 21.010], [85.805, 21.010], [85.805, 21.035], [85.780, 21.035], [85.780, 21.010]]]
            }
        },
        {
            "code": "KORBA-MEGA01",
            "name": "Korba Mega Open-Pit Coal Mine",
            "location": "Hasdeo-Arand Basin, Korba",
            "state": "Chhattisgarh",
            "mineral_type": "Thermal Non-Coking Coal",
            "crs": "EPSG:32644 (WGS 84 / UTM Zone 44N)",
            "area_sq_km": 8.2,
            "benches_count": 20,
            "estimated_reserves_mt": 185.0,
            "target_stripping_ratio": 2.10,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[82.680, 22.340], [82.720, 22.340], [82.720, 22.380], [82.680, 22.380], [82.680, 22.340]]]
            }
        },
        {
            "code": "RAMPURA-AG01",
            "name": "Rampura Agucha Open Pit",
            "location": "Bhilwara District, Rajasthan",
            "state": "Rajasthan",
            "mineral_type": "Zinc-Lead Sulphide Ore",
            "crs": "EPSG:32643 (WGS 84 / UTM Zone 43N)",
            "area_sq_km": 5.0,
            "benches_count": 16,
            "estimated_reserves_mt": 62.0,
            "target_stripping_ratio": 4.10,
            "boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[[74.900, 25.820], [74.930, 25.820], [74.930, 25.850], [74.900, 25.850], [74.900, 25.820]]]
            }
        }
    ]

    mine_sites = []
    for s_item in sites_data:
        m = MineSite(**s_item)
        db.add(m)
        mine_sites.append(m)
    db.commit()

    primary_site = mine_sites[0]

    # 3. Seed Surveys for Primary Site (Stage 1 Previous & Stage 2 Current)
    now = datetime.now(timezone.utc)
    survey_stage1 = Survey(
        site_id=primary_site.id,
        name="Quarterly Baseline Survey Q1 - CW-25E VTOL",
        survey_date=now - timedelta(days=30),
        uav_model="CW-25E VTOL / JOUAV-LR-LR",
        sensors_enabled=[
            "LiDAR 1350m (6cm precision)",
            "Five-Lens Oblique Camera",
            "EO/IR Thermal Gimbal",
            "Image Inspectometer",
            "RGB Mapping Camera"
        ],
        dual_rtk_gps=True,
        scale_factor="1:1000",
        flight_area_sq_km=4.0,
        flight_duration_minutes=20.0,
        flight_altitude_m=120.0,
        flight_speed_m_s=18.0,
        line_spacing_m=45.0,
        endurance_capacity_minutes=120.0,
        max_lidar_range_m=1350.0,
        point_density_pts_m2=82.0,
        elevation_deviation_cm=5.9,
        status="accepted",
        surveyor_id=surveyor_user.id,
        notes="Q1 Baseline survey for 4 sq km completed in 20 min with zero GCPs."
    )

    survey_stage2 = Survey(
        site_id=primary_site.id,
        name="Monthly Stripping Acceptance Survey Q2 - CW-25E VTOL",
        survey_date=now - timedelta(days=1),
        uav_model="CW-25E VTOL / JOUAV-LR-LR",
        sensors_enabled=[
            "LiDAR 1350m (6cm precision)",
            "Five-Lens Oblique Camera",
            "EO/IR Thermal Gimbal",
            "Image Inspectometer",
            "RGB Mapping Camera"
        ],
        dual_rtk_gps=True,
        scale_factor="1:1000",
        flight_area_sq_km=4.0,
        flight_duration_minutes=20.0,
        flight_altitude_m=120.0,
        flight_speed_m_s=18.0,
        line_spacing_m=45.0,
        endurance_capacity_minutes=120.0,
        max_lidar_range_m=1350.0,
        point_density_pts_m2=88.0,
        elevation_deviation_cm=6.0,
        status="accepted",
        surveyor_id=surveyor_user.id,
        notes="High-precision acceptance flight. 34 electromechanical machines filtered out."
    )
    db.add_all([survey_stage1, survey_stage2])
    db.commit()

    # 4. Processing Job (Electromechanical Filter & DEM Generation)
    job = ProcessingJob(
        survey_id=survey_stage2.id,
        job_type="electromechanical_filter_dem",
        status="completed",
        progress_pct=100.0,
        machinery_filtered_count=34,
        elevation_deviation_cm=6.0,
        log="LiDAR point cloud (352M points) parsed. 34 electromechanical units (dumpers, shovels, pumps) filtered. Clean DEM built.",
        started_at=now - timedelta(days=1, hours=2),
        completed_at=now - timedelta(days=1, hours=1, minutes=40)
    )
    db.add(job)
    db.commit()

    # 5. Terrain Models
    _, _, dem_meta1, matrix1 = simulate_lidar_filtering_and_dem(base_elevation=230.0)
    _, _, dem_meta2, matrix2 = simulate_lidar_filtering_and_dem(base_elevation=218.0)

    terrain1 = TerrainModel(
        site_id=primary_site.id,
        survey_id=survey_stage1.id,
        name="Terrain DEM - Q1 Baseline Stage 1",
        grid_resolution_m=0.25,
        elevation_min=dem_meta1["elevation_min_m"],
        elevation_max=dem_meta1["elevation_max_m"],
        mean_elevation=dem_meta1["mean_elevation_m"],
        dem_matrix_json=matrix1,
        stage_label="stage_1_previous"
    )
    terrain2 = TerrainModel(
        site_id=primary_site.id,
        survey_id=survey_stage2.id,
        name="Terrain DEM - Q2 Current Stage 2",
        grid_resolution_m=0.25,
        elevation_min=dem_meta2["elevation_min_m"],
        elevation_max=dem_meta2["elevation_max_m"],
        mean_elevation=dem_meta2["mean_elevation_m"],
        dem_matrix_json=matrix2,
        stage_label="stage_2_current"
    )
    db.add_all([terrain1, terrain2])
    db.commit()

    # 6. Volume Comparison (Two-Stage Differential Demodulation)
    vol_comp = VolumeComparison(
        site_id=primary_site.id,
        current_survey_id=survey_stage2.id,
        previous_survey_id=survey_stage1.id,
        area_name="North Pit Bench 4-8 Stripping Acceptance",
        comparison_method="Two-Stage Differential Demodulation (LiDAR DEM vs Baseline)",
        cut_volume_m3=142500.0,
        fill_volume_m3=12400.0,
        net_volume_m3=130100.0,
        stripping_volume_m3=95400.0,
        ore_extracted_volume_m3=34700.0,
        ore_density_t_m3=2.65,
        total_ore_tonnage_t=91955.0,
        waste_tonnage_t=219420.0,
        elevation_deviation_cm=6.0,
        acceptance_status="ACCEPTED",
        accepted_by="Col. Arvind Verma (General Mine Manager)",
        accepted_at=now - timedelta(hours=6),
        remarks="Accepted without GCPs. Elevation accuracy certified within 6cm tolerance."
    )
    db.add(vol_comp)
    db.commit()

    # 7. Terrain Profile & Haul Road Profile
    t_prof_data = calculate_terrain_profile(
        matrix2,
        {"coordinates": [[86.415, 23.755], [86.430, 23.770]]},
        samples_count=50,
        elevation_min=dem_meta2["elevation_min_m"],
        elevation_max=dem_meta2["elevation_max_m"]
    )
    t_prof = TerrainProfile(
        terrain_model_id=terrain2.id,
        name="North-South Working Bench Transect B-B'",
        line_geojson={"coordinates": [[86.415, 23.755], [86.430, 23.770]]},
        distance_total_m=t_prof_data["distance_total_m"],
        elevation_min=t_prof_data["elevation_min"],
        elevation_max=t_prof_data["elevation_max"],
        max_slope_deg=t_prof_data["max_slope_deg"],
        samples_json=t_prof_data["samples"]
    )

    r_prof_data = calculate_road_profile({"coordinates": []})
    r_prof = RoadProfile(
        terrain_model_id=terrain2.id,
        name="Main Pit Ramp Haul Road #1",
        alignment_geojson={"type": "LineString", "coordinates": [[86.418, 23.758], [86.431, 23.771]]},
        length_m=r_prof_data["length_m"],
        avg_slope_pct=r_prof_data["avg_slope_pct"],
        max_slope_pct=r_prof_data["max_slope_pct"],
        max_allowed_slope_pct=10.0,
        safety_berm_height_m=1.8,
        violations_count=r_prof_data["violations_count"],
        violations_json=r_prof_data["violations"],
        safety_status=r_prof_data["safety_status"]
    )
    db.add_all([t_prof, r_prof])
    db.commit()

    # 8. Production History (Past 14 Days)
    for i in range(14, 0, -1):
        rec_date = now - timedelta(days=i)
        planned_ore = 15000.0
        # Introduce slight operational shortfall on some days
        actual_ore = 15000.0 if i not in [4, 5, 8] else (13400.0 if i == 4 else (12800.0 if i == 5 else 14100.0))
        planned_waste = 38000.0
        actual_waste = 36500.0 if i not in [4, 5] else 31200.0
        shortfall = max(0.0, planned_ore - actual_ore)
        
        prod_rec = ProductionRecord(
            site_id=primary_site.id,
            record_date=rec_date,
            planned_ore_tonnes=planned_ore,
            actual_ore_tonnes=actual_ore,
            planned_waste_tonnes=planned_waste,
            actual_waste_tonnes=actual_waste,
            stripping_ratio=round(actual_waste / actual_ore, 2),
            active_trucks=26 if i in [4, 5] else 28,
            active_shovels=5 if i == 5 else 6,
            active_pumps=4,
            fuel_consumed_liters=14200.0 if i not in [4, 5] else 12600.0,
            operational_cost_inr=2850000.0,
            weather_condition="Monsoon Showers" if i in [4, 5] else "Clear Sky",
            rainfall_mm=24.5 if i == 4 else (38.0 if i == 5 else 0.0),
            shortfall_tonnes=shortfall
        )
        db.add(prod_rec)
    db.commit()

    # 9. Equipment Fleet
    fleet_items = [
        {"code": "VTOL-01", "type": "vtol_drone", "model": "JOUAV CW-25E (Dual RTK GPS / LiDAR 1350m)", "status": "active", "hours": 420.0, "fuel_rate": 0.0, "cost": 4500.0, "lat": 23.762, "lng": 86.421},
        {"code": "SHV-01", "type": "excavator_shovel", "model": "Komatsu PC2000-8 (12 m³ Bucket)", "status": "active", "hours": 4120.0, "fuel_rate": 62.0, "cost": 18500.0, "lat": 23.758, "lng": 86.419},
        {"code": "SHV-02", "type": "excavator_shovel", "model": "Tata Hitachi EX1200-6", "status": "active", "hours": 3890.0, "fuel_rate": 54.0, "cost": 16200.0, "lat": 23.765, "lng": 86.425},
        {"code": "SHV-03", "type": "excavator_shovel", "model": "CAT 6015B Hydraulic Shovel", "status": "maintenance", "hours": 5100.0, "fuel_rate": 58.0, "cost": 17000.0, "lat": 23.754, "lng": 86.415},
        {"code": "DT-101", "type": "haul_truck", "model": "CAT 777E (100-Tonne Dumper)", "status": "active", "hours": 6200.0, "fuel_rate": 48.0, "cost": 9800.0, "lat": 23.760, "lng": 86.422},
        {"code": "DT-102", "type": "haul_truck", "model": "CAT 777E (100-Tonne Dumper)", "status": "active", "hours": 5940.0, "fuel_rate": 47.5, "cost": 9800.0, "lat": 23.763, "lng": 86.424},
        {"code": "DT-103", "type": "haul_truck", "model": "Komatsu HD785-7 (100-Tonne)", "status": "active", "hours": 4810.0, "fuel_rate": 49.0, "cost": 10200.0, "lat": 23.757, "lng": 86.418},
        {"code": "DT-104", "type": "haul_truck", "model": "Komatsu HD785-7 (100-Tonne)", "status": "breakdown", "hours": 5120.0, "fuel_rate": 49.0, "cost": 10200.0, "lat": 23.755, "lng": 86.416},
        {"code": "PUMP-01", "type": "dewatering_pump", "model": "Kirloskar High-Head Sump Dewatering 150HP", "status": "active", "hours": 7200.0, "fuel_rate": 18.0, "cost": 3200.0, "lat": 23.752, "lng": 86.412},
        {"code": "PUMP-02", "type": "dewatering_pump", "model": "Flygt Submersible Heavy Sump Pump 90kW", "status": "active", "hours": 6400.0, "fuel_rate": 16.5, "cost": 2900.0, "lat": 23.753, "lng": 86.413}
    ]
    for item in fleet_items:
        ef = EquipmentFleet(
            site_id=primary_site.id,
            equipment_code=item["code"],
            equipment_type=item["type"],
            model=item["model"],
            status=item["status"],
            operating_hours=item["hours"],
            fuel_rate_l_h=item["fuel_rate"],
            hourly_cost_inr=item["cost"],
            gps_lat=item["lat"],
            gps_lng=item["lng"],
            telemetry_json={"engine_temp_c": 82, "rpm": 1850, "oil_pressure_psi": 54}
        )
        db.add(ef)
    db.commit()

    # 10. AI Forecast & Risk Calendar
    from app.services.production_forecast import generate_14day_xgboost_forecast
    fc_data = generate_14day_xgboost_forecast()
    forecast = ProductionForecast(
        site_id=primary_site.id,
        model_version=fc_data["model_version"],
        forecast_date=now,
        horizon_days=14,
        baseline_target_tonnes=fc_data["baseline_target_tonnes"],
        predicted_tonnes=fc_data["predicted_tonnes"],
        predicted_shortfall_tonnes=fc_data["predicted_shortfall_tonnes"],
        shortfall_pct=fc_data["shortfall_pct"],
        risk_level=fc_data["risk_level"],
        daily_forecasts_json=fc_data["daily_forecasts"],
        contributing_factors_json=fc_data["contributing_factors"],
        action_recommendations_json=fc_data["action_recommendations"]
    )
    db.add(forecast)

    # Risk calendar entries
    risks = [
        {"date": (now + timedelta(days=2)).strftime("%Y-%m-%d"), "cat": "shovel_maintenance", "score": 62.0, "sev": "amber", "title": "CAT 6015B Hydraulic Shovel Scheduled Overhaul", "desc": "Reduced loading capacity at Bench 6.", "mit": "Shift reserve tippers to Shovel #1."},
        {"date": (now + timedelta(days=5)).strftime("%Y-%m-%d"), "cat": "weather_rain", "score": 85.0, "sev": "red", "title": "Heavy Monsoon Precipitation (48mm) Expected", "desc": "Haul road slip hazard and pit sump accumulation.", "mit": "Pre-deploy dewatering pumps and gravel ramps."},
        {"date": (now + timedelta(days=6)).strftime("%Y-%m-%d"), "cat": "slope_stability", "score": 74.0, "sev": "amber", "title": "Highwall Slope Tension Crack Monitoring", "desc": "LiDAR inspectometer detected 3mm displacement on Bench 8.", "mit": "Maintain 50m equipment standoff buffer until geotechnical clearance."},
        {"date": (now + timedelta(days=10)).strftime("%Y-%m-%d"), "cat": "production_target", "score": 35.0, "sev": "green", "title": "Normal Production Operations", "desc": "All 6 shovels operational. Target 15,000 MT/day reachable.", "mit": "Routine shift dispatching."}
    ]
    for r in risks:
        rc = RiskCalendarEntry(
            site_id=primary_site.id,
            risk_date=r["date"],
            risk_category=r["cat"],
            risk_score=r["score"],
            severity=r["sev"],
            title=r["title"],
            description=r["desc"],
            mitigation_action=r["mit"]
        )
        db.add(rc)
    db.commit()

    # 11. Seed Initial Decision Reports (Certified PDF & Excel Workbook)
    from app.models.schemas_db import ReportRecord
    from app.services.report_generation import generate_volume_acceptance_pdf, generate_mine_analytics_excel

    if not db.query(ReportRecord).first():
        pdf_file = "Stripping_Acceptance_JHARIA-PIT07_seed.pdf"
        excel_file = "Mine_Insights_JHARIA-PIT07_seed.xlsx"

        pdf_path = generate_volume_acceptance_pdf(
            report_title=f"{primary_site.name} Stripping Volume Acceptance Certificate",
            site_name=f"{primary_site.name} ({primary_site.state}, India)",
            survey_name="Autonomous Survey Q2 (LiDAR)",
            cut_volume_m3=142500.0,
            fill_volume_m3=12400.0,
            net_volume_m3=130100.0,
            stripping_volume_m3=95400.0,
            ore_tonnage_t=91955.0,
            waste_tonnage_t=219420.0,
            elevation_deviation_cm=6.0,
            accepted_by="Col. Arvind Verma (General Mine Manager)",
            output_filename=pdf_file
        )

        excel_path = generate_mine_analytics_excel(
            report_title=f"{primary_site.name} Digital Twin Analytics & Volumetric Workbook (.xlsx)",
            site_name=f"{primary_site.name} ({primary_site.state}, India)",
            site_code=primary_site.code,
            survey_name="Autonomous Survey Q2 (LiDAR)",
            cut_volume_m3=142500.0,
            fill_volume_m3=12400.0,
            net_volume_m3=130100.0,
            stripping_volume_m3=95400.0,
            ore_tonnage_t=91955.0,
            waste_tonnage_t=219420.0,
            elevation_deviation_cm=6.0,
            accepted_by="Col. Arvind Verma (General Mine Manager)",
            output_filename=excel_file
        )

        from pathlib import Path
        db.add(ReportRecord(
            site_id=primary_site.id,
            survey_id=survey_stage2.id,
            report_title=f"{primary_site.name} Stripping Acceptance Certificate",
            report_type="stripping_volume_acceptance_pdf",
            file_path=pdf_path,
            file_size_bytes=Path(pdf_path).stat().st_size if Path(pdf_path).exists() else 48000,
            generated_by="Digital Twin AI Reporting Engine",
            status="ready"
        ))
        db.add(ReportRecord(
            site_id=primary_site.id,
            survey_id=survey_stage2.id,
            report_title=f"{primary_site.code} - Digital Twin Analytics & Volumetric Workbook (.xlsx)",
            report_type="stripping_volume_acceptance_excel",
            file_path=excel_path,
            file_size_bytes=Path(excel_path).stat().st_size if Path(excel_path).exists() else 38000,
            generated_by="Digital Twin AI Reporting Engine",
            status="ready"
        ))
        db.commit()
