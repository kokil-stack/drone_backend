# Intelligent Drone-Based Mining and Digital Mine Platform

## Final Project Technical Specification

**Document type:** System overview, technical architecture, workflows,
and implementation specification\
**Project domain:** Open-pit mining, drone surveying, geospatial
analytics, production intelligence, and mine operations\
**Status:** Proposed system design based on the supplied workflow
diagrams and project details

------------------------------------------------------------------------

## 1. Project Overview

The Intelligent Drone-Based Mining and Digital Mine Platform combines
UAV aerial surveying, LiDAR point-cloud processing, geospatial analysis,
mine data management, and optional AI-assisted production forecasting in
one operational system.

The platform is intended to help surveyors and mine managers collect and
interpret mine-site data, inspect terrain changes, calculate excavation
and fill volumes, compare surveys over time, examine road profiles,
monitor production, and review decision-support recommendations.

The system follows five main stages:

1.  **Collect data** from drone surveys and mine-operational sources.
2.  **Process and clean** survey, sensor, and satellite data.
3.  **Store** processed outputs and operational records in a spatial
    database.
4.  **Perform geospatial and AI analysis** for terrain, volume, reserve,
    and production insights.
5.  **Present results** through role-based dashboards, maps, charts,
    alerts, and reports.

The platform should be developed in modules so that the core surveying
and analysis workflow can operate independently of optional AI and
satellite-analysis capabilities.

------------------------------------------------------------------------

## 2. Project Objectives

-   Plan and manage UAV survey missions over defined mine-site polygons.
-   Collect and process LiDAR point clouds and related survey imagery.
-   Generate terrain models and digital elevation models (DEM/DTM, where
    supported by the processing workflow).
-   Store spatial features, survey metadata, terrain outputs, and
    mine-operation records.
-   Analyse terrain profiles, road profiles, cut-and-fill quantities,
    and volume differences between surveys.
-   Bring production reports, drill logs, equipment data, weather data,
    and satellite-derived layers into a shared analysis workflow.
-   Provide reserve-estimation and production-shortfall prediction
    modules when suitable input data and validated models are available.
-   Give surveyors and mine managers appropriate access to maps,
    telemetry, operational indicators, analysis results, and decision
    reports.
-   Support secure sign-in and role-based access.
-   Allow analysis results to be exported as decision reports, including
    automated PDF reports.

------------------------------------------------------------------------

## 3. User Roles

### 3.1 Surveyor

The surveyor uses the platform to:

-   Define a survey area using a polygon.
-   Configure supported flight and LiDAR parameters.
-   Review mission distance, survey area, estimated flight time, and
    waypoint information when provided by the flight system.
-   Monitor flight telemetry and survey status when a supported
    integration is available.
-   Upload or transfer raw point-cloud data and associated imagery.
-   Review terrain outputs, profiles, volume calculations, and
    comparisons between survey dates.

### 3.2 Mine Manager

The mine manager uses the platform to:

-   Review mine and production dashboards.
-   View survey results, terrain and road analysis, and volume
    comparisons.
-   Review production forecasts, risk indicators, and action
    recommendations when those modules are enabled.
-   Run what-if scenarios for supported assumptions such as rainfall,
    loss ratio, or equipment breakdowns.
-   Review reports and take operational decisions.
-   Request or approve follow-up actions according to configured
    permissions.

Actual UAV flight commands and operational equipment actions must only
be enabled through supported integrations and authorized workflows. A
dashboard alone does not control a drone or mine equipment.

------------------------------------------------------------------------

## 4. Technology Stack

### 4.1 Frontend

The supplied frontend stack is retained:

-   **JavaScript / JSX (ES6+)** --- application logic and React
    components.
-   **React 18** --- UI component architecture and interactive state.
-   **Vite 5** --- development server and production build tooling.
-   **HTML5** --- application document and root structure.
-   **CSS3 and Tailwind CSS** --- responsive layouts, styling, and UI
    utilities.
-   **Lucide React** --- interface icons.
-   **Leaflet.js** --- interactive 2D maps and spatial overlays, where
    applicable.
-   **Charting library** --- for elevation profiles, production charts,
    volume comparisons, and KPI visualizations; select and standardize
    one library during implementation.

Existing project references include `src/App.jsx`, `src/main.jsx`,
`src/index.css`, `index.html`, `vite.config.js`, and
`tailwind.config.js`. Geometry and identifier validation scripts may be
retained where they are part of the current repository.

### 4.2 Backend

-   **Python** --- geospatial processing, data validation, calculations,
    and analytics.
-   **FastAPI** --- REST API layer connecting the frontend to processing
    services and stored data.
-   **Pydantic** --- request/response validation and typed API schemas.
-   **Background processing** --- for long-running point-cloud, raster,
    report, or model tasks. A production job queue/worker should be
    selected if processing volume requires it.

### 4.3 Data Storage and Authentication

-   **PostgreSQL** --- relational storage for users' permitted project
    metadata, survey records, mine sites, operational data, and analysis
    results.
-   **PostGIS** --- spatial data types and spatial queries.
-   **Supabase Auth** --- authentication and identity management.
-   **Supabase Storage** --- optional object storage for uploaded source
    files and generated artifacts, subject to project configuration and
    access policies.

The architecture should avoid maintaining duplicate authoritative copies
of the same records in separate databases. PostgreSQL/PostGIS is the
primary application and spatial data store; Supabase services are
integrated where they provide authentication or storage capabilities.

The supplied architecture diagram mentions a main database containing 10
tables across 9 mine sites. Treat those numbers as diagram-specific
example/current design information, not a fixed platform limit; confirm
the actual schema and site count during implementation.

### 4.4 Geospatial Processing

Potential Python libraries and tools include:

-   **PDAL** --- point-cloud processing pipelines.
-   **laspy** --- reading and writing LAS/LAZ data where supported.
-   **Rasterio** --- raster and DEM operations.
-   **GeoPandas** --- vector geospatial data processing.
-   Additional GDAL-compatible tooling may be selected if required by
    the chosen file formats and deployment environment.

Use only the tools required by the actual data formats and processing
pipeline.

### 4.5 AI and Satellite Analysis

-   **XGBoost** --- optional model for production-shortfall forecasting,
    including the proposed 14-day forecast.
-   **Kriging** --- proposed geostatistical method for reserve
    estimation, subject to the availability and suitability of
    geological sampling data and domain validation.
-   **Google Earth Engine** --- optional satellite-data processing and
    derived-layer generation.
-   **Landsat** --- source of satellite observations used in the
    supplied architecture for ground/land-surface temperature-related
    analysis.
-   **Sentinel-2** --- source of multispectral imagery for surface,
    vegetation, moisture, and related index workflows.
-   **Weather data (NASA/IMD, as configured)** --- rainfall or weather
    inputs where access, licensing, coverage, and data quality are
    confirmed.

AI and satellite modules are optional analytical components. They should
not be represented as validated or operational until data pipelines,
model evaluation, and acceptance tests are completed.

------------------------------------------------------------------------

## 5. High-Level Architecture

``` text
Surveyor / Mine Manager
          |
          v
React 18 + Vite Dashboard
(JavaScript/JSX, Tailwind CSS, Lucide React)
          |
          v
FastAPI REST API
          |
          +--------------------+----------------------+
          |                    |                      |
          v                    v                      v
Authentication           PostgreSQL + PostGIS    File/Object Storage
Supabase Auth            Spatial + operational   Raw survey files,
                         records and results      imagery and exports
          |
          v
Processing and Analytics Services
          |
          +--> LiDAR point-cloud processing
          +--> Terrain model / DEM generation
          +--> Terrain and road profile analysis
          +--> Cut-and-fill / volume comparison
          +--> Satellite map processing (optional)
          +--> Reserve estimation (optional)
          +--> Production forecasting (optional)
          +--> What-if simulation and action advice (optional)
          |
          v
Dashboard Results, Maps, Charts, Alerts and PDF Reports
```

### 5.1 Architectural Principles

-   Keep the frontend separate from the backend through documented APIs.
-   Keep large source files in object/file storage rather than storing
    the entire file payload in ordinary relational rows.
-   Store searchable metadata, geometry, status, and derived results in
    PostgreSQL/PostGIS.
-   Run heavy geospatial operations as trackable jobs rather than
    blocking ordinary dashboard requests.
-   Record processing status, timestamps, source survey identifiers,
    processing parameters, and errors.
-   Enforce authentication and authorization on the backend, not only by
    hiding frontend controls.
-   Preserve links between source survey files and their derived outputs
    for auditability and repeatability.

------------------------------------------------------------------------

## 6. End-to-End Workflow

### Step 1 --- Collect Data

The supplied diagrams identify the following inputs:

  -----------------------------------------------------------------------
  Data source                         Data or purpose
  ----------------------------------- -----------------------------------
  UAV aerial survey flight            CW-25E / JOUAV-LR-LR as labelled in
                                      the diagrams; survey area, mission
                                      details, point-cloud collection

  Daily production reports            Planned versus actual output

  Drill logs                          Ore grade and depth

  Equipment sensors                   Trucks, shovels/excavators, and
                                      pumps

  Landsat satellite                   Ground/land-surface
                                      temperature-related information

  Sentinel-2 satellite                Multispectral surface imagery and
                                      derived indices

  Weather data                        NASA / IMD rainfall or other
                                      configured weather inputs
  -----------------------------------------------------------------------

The exact aircraft, sensor, and payload compatibility must be confirmed
against the actual equipment. The diagrams use the labels `CW-25E` and
`JOUAV-LR-LR`; confirm the precise model and payload naming before
treating these as final procurement specifications.

#### UAV survey planning

The survey workflow should allow an authorized surveyor to:

1.  Select a mine site and draw or upload a polygon survey area.
2.  Configure available flight and LiDAR settings, such as altitude,
    speed, point-cloud settings, and line spacing where supported.
3.  Review mission geometry, waypoints, survey area, distance, and
    estimated duration when supplied by the flight-planning integration.
4.  Validate the planned area and parameters before exporting or sending
    the mission to compatible flight software.
5.  Record mission status and associate the resulting files with the
    survey job.

Flight execution, telemetry, and mission upload depend on an actual
supported UAV/flight-controller integration. Without such an
integration, the application can support planning records and file
import, but must not claim live drone control.

### Step 2 --- Process and Clean

The supplied architecture includes three main processing paths:

#### 2.1 LiDAR point-cloud processing

-   Ingest raw point-cloud files.
-   Validate file type, coordinate reference system, and required
    metadata.
-   Run configured point-cloud processing.
-   Generate terrain products and elevation surfaces where the source
    data supports them.
-   Retain processing parameters and source-to-output relationships.
-   Report processing failures and quality warnings.

#### 2.2 Feature extraction

For supported satellite imagery and other suitable inputs, calculate
selected features such as:

-   Vegetation indices.
-   Moisture-related indices.
-   Mineral-related indices.

The exact indices must be selected according to the sensor bands, data
quality, and mining use case. A feature should not be displayed as a
reliable measurement unless its calculation and interpretation have been
defined.

#### 2.3 Satellite map processing

-   Retrieve or import the selected satellite imagery.
-   Prepare usable map layers.
-   Align layers to the required coordinate system and study area.
-   Track acquisition dates, source, resolution, and processing steps.

#### 2.4 Quality checks

-   Check for missing or invalid data.
-   Validate geometry and coordinate systems.
-   Normalize fields where required.
-   Check timestamps and identifiers.
-   Flag incomplete, anomalous, or incompatible input.
-   Keep a processing log for traceability.

### Step 3 --- Store

The database and storage layer should manage:

-   Mine sites and survey areas.
-   Survey missions and mission metadata.
-   Source file metadata and storage references.
-   Point-cloud, imagery, terrain, and raster product metadata.
-   Coordinate reference systems and geometries.
-   Terrain profile results.
-   Road profile results.
-   Cut-and-fill calculations.
-   Survey-to-survey volume comparisons.
-   Production reports and drill logs.
-   Equipment and weather observations.
-   AI forecasts and scenario results, when enabled.
-   Users, roles, and access-controlled relationships.
-   Report metadata and processing job status.

Supabase Auth handles identity in the proposed architecture.
Application-level permissions must still be enforced by the backend and
database/storage policies. The exact database schema is to be finalized
during implementation; the diagram's "10 tables, 9 mine sites" label is
not a complete schema specification.

### Step 4 --- Geospatial Analysis

#### 4.1 Terrain Profile Analysis

Purpose: inspect elevation along a selected line or transect.

Expected workflow: 1. Select a terrain model and draw or select a
profile line. 2. Sample elevations along the line. 3. Return
distance/elevation pairs. 4. Display an elevation-versus-distance chart
and profile summary. 5. Record the source terrain model and sampling
settings.

#### 4.2 Cut-and-Fill Analysis

Purpose: estimate excavation and fill volumes between a selected terrain
surface and a reference surface or elevation.

Expected workflow: 1. Select the area of interest. 2. Select the current
surface and reference surface/elevation. 3. Apply the configured
calculation method. 4. Return excavation volume, fill volume, affected
area, and reference parameters. 5. Display the results on the map and in
a summary panel.

The calculation method, units, surface alignment, and assumptions must
be documented. Results are estimates based on input surface quality and
the chosen reference method.

#### 4.3 Volume Comparison --- Current versus Previous Survey

Purpose: compare two surveys to identify terrain changes and estimate
volume differences.

Expected workflow: 1. Select a mine site, area, current survey, and
previous survey. 2. Validate that both datasets use compatible
coordinate systems, vertical references, coverage, and processing
conventions. 3. Align or resample surfaces as required by the approved
method. 4. Calculate elevation differences and configured volume
summaries. 5. Display change layers and a current-versus-previous
summary.

Outputs may include cut/fill distribution, change area, and calculated
volume differences. Do not imply that the results are survey-certified
unless the project defines and completes the relevant validation
process.

#### 4.4 Road Profile Analysis

Purpose: inspect elevation and slope along a selected mine road.

Expected workflow: 1. Select or draw a road alignment. 2. Sample the
selected terrain model along the alignment. 3. Calculate
distance/elevation profile and configured slope metrics. 4. Display road
length, profile chart, and slope summary. 5. Identify sections for
review according to configured thresholds.

#### 4.5 Reserve Estimation --- Kriging

The supplied architecture proposes a Kriging algorithm to estimate a
three-dimensional underground ore distribution.

Inputs may include drill-hole locations, depths, and ore-grade
measurements, along with a validated geological model and appropriate
spatial parameters.

Requirements: - Validate drill-hole data and coordinate systems. -
Define the estimation domain and geological assumptions. - Configure and
document the variogram and Kriging parameters. - Evaluate estimation
uncertainty and validation performance. - Label outputs as estimates,
not direct observations.

This module requires suitable geological data and specialist review. It
should be treated as optional until the dataset and validation procedure
are available.

### Step 4B --- AI Analysis and Production Decision Support

The supplied architecture proposes four linked capabilities.

#### 4.6 Production Shortfall Prediction --- XGBoost

-   Input: historical planned and actual production, relevant
    mine-operation variables, and available weather/equipment
    indicators.
-   Output: a forecast of possible production shortfall, proposed for a
    14-day horizon.
-   Display: forecast values, model-generated risk indicators, and
    relevant input context.

A 14-day forecast is a design target from the supplied diagram, not a
guaranteed level of accuracy. Training data, baseline comparison,
validation, monitoring, and retraining rules are required before
operational use.

#### 4.7 What-If Simulator

The supplied diagram lists scenarios involving:

-   Loss ratio.
-   Rain.
-   Equipment breakdowns.

The simulator should let authorized users change supported assumptions
and compare projected outcomes against a baseline. Clearly distinguish
user-entered assumptions and simulated estimates from observed data.

#### 4.8 Action Advisor

The action advisor proposes corrective steps intended to help recover
production output.

Recommendations should: - Be traceable to forecast results or scenario
assumptions. - Explain the main contributing factors where possible. -
Include impact or confidence information only when it is supported by
the method. - Require human review before consequential operational
actions.

#### 4.9 Risk Calendar

The architecture includes a color-coded daily risk calendar. It can
present configured risk alerts derived from production forecasts,
weather information, or other approved signals. Risk categories,
thresholds, and update frequency must be defined by the project.

------------------------------------------------------------------------

## 7. Frontend Modules and Screens

The React application should be organized into the following functional
areas.

### 7.1 Aerial Survey Dashboard

-   Survey area and mission overview.
-   Mission status and available flight telemetry.
-   Survey file upload/import.
-   Flight planning details and waypoint list, where integrated.
-   Survey history and processing status.

### 7.2 Interactive Mine Map

-   Mine-site boundaries and survey polygons.
-   Survey footprints and terrain layers.
-   Road alignments and profile lines.
-   Volume-change overlays.
-   Satellite layers when available.
-   Layer visibility controls, legend, scale, and coordinate context.

Leaflet supports the 2D mapping requirement. A dedicated 3D renderer and
suitable terrain/point-cloud visualization pipeline would be needed for
interactive 3D mine scenes; that capability is not supplied by Leaflet
alone.

### 7.3 Terrain and Survey Analysis Dashboard

-   Terrain profile chart.
-   Road profile and slope metrics.
-   Cut-and-fill summary.
-   Current-versus-previous survey comparison.
-   Processing metadata and quality notices.

### 7.4 Production Dashboard

-   Planned versus actual production.
-   Production history.
-   Equipment summaries for configured trucks, shovels/excavators, and
    pumps.
-   Forecast and shortfall indicators when the AI model is enabled.
-   Data freshness and source information.

The diagrams identify the dashboard metrics and data sources, but do not
define all KPI formulas or sensor protocols. Those must be agreed during
implementation.

### 7.5 AI and Risk Dashboard

-   Production-shortfall forecast.
-   Risk calendar.
-   What-if scenario controls.
-   Action recommendations.
-   Forecast history and model version/validation information.

### 7.6 Reports

-   Generate decision reports in PDF format.
-   Include selected mine site, survey dates, source datasets, analysis
    parameters, units, summary values, charts/maps where applicable, and
    generation timestamp.
-   Include data-quality caveats and the status of optional model
    outputs.
-   Restrict access to reports according to user permissions.

### 7.7 Authentication and Role Dashboards

-   Secure sign-in through Supabase Auth.
-   Role-based views for surveyors and mine managers.
-   Backend authorization checks for protected API routes and
    operations.
-   Session and access error handling.
-   Audit logging for significant data changes and operations.

The supplied architecture refers to a "UK4G UI/UX" standard. Confirm the
intended standard name and applicable requirements before treating that
label as a compliance commitment.

------------------------------------------------------------------------

## 8. Proposed API Areas

The following are suggested API groups for implementation, not existing
or already tested endpoints.

  API area                            Example responsibilities
  ----------------------------------- ----------------------------------------------
  `/api/sites`                        Mine-site metadata and permitted site access
  `/api/surveys`                      Create, list, and retrieve survey records
  `/api/surveys/{id}/files`           Register uploaded source files
  `/api/processing-jobs`              Submit processing jobs and inspect status
  `/api/terrain`                      Terrain products and terrain metadata
  `/api/analysis/terrain-profile`     Terrain profile calculations
  `/api/analysis/cut-fill`            Cut-and-fill calculations
  `/api/analysis/volume-comparison`   Survey-to-survey comparison
  `/api/analysis/road-profile`        Road profile and slope analysis
  `/api/production`                   Production records and dashboard summaries
  `/api/equipment`                    Configured equipment data and status
  `/api/forecast`                     Forecast requests and results when enabled
  `/api/simulations`                  What-if scenarios and results
  `/api/reports`                      PDF report generation and retrieval

All endpoints should validate input, enforce authorization, return
consistent error responses, and record processing status where relevant.
Exact endpoint contracts should be documented in the FastAPI OpenAPI
specification.

------------------------------------------------------------------------

## 9. Suggested Backend Project Structure

``` text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── sites.py
│   │   ├── surveys.py
│   │   ├── files.py
│   │   ├── terrain.py
│   │   ├── analysis.py
│   │   ├── production.py
│   │   ├── equipment.py
│   │   ├── forecast.py
│   │   ├── simulations.py
│   │   └── reports.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── schemas/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   │   ├── point_cloud.py
│   │   ├── terrain.py
│   │   ├── terrain_profile.py
│   │   ├── cut_fill.py
│   │   ├── volume_comparison.py
│   │   ├── road_profile.py
│   │   ├── satellite.py
│   │   ├── reserve_estimation.py
│   │   ├── production_forecast.py
│   │   └── report_generation.py
│   └── workers/
├── tests/
├── requirements.txt
└── README.md
```

The worker and service modules can be introduced progressively. Do not
create empty modules and describe them as completed functionality.

------------------------------------------------------------------------

## 10. Data and Processing Considerations

### 10.1 Spatial Reference and Units

-   Store and document the coordinate reference system for each source
    and output.
-   Define the vertical datum and elevation units for terrain
    comparisons.
-   Validate units before calculating areas, distances, slopes, and
    volumes.
-   Ensure that surfaces being compared are compatible or processed
    through a documented alignment method.

### 10.2 Large Files and Processing Jobs

-   Validate file size, format, and metadata at upload time.
-   Store original files and generated artifacts in file/object storage.
-   Process large files asynchronously when needed.
-   Return a job identifier and status to the frontend.
-   Capture logs and errors for failed jobs.
-   Avoid loading entire high-density point clouds into browser memory
    without a deliberate visualization strategy.

### 10.3 Data Provenance

Each derived result should retain: - Source survey/file identifiers. -
Processing date and software/configuration version where practical. -
Coordinate system and units. - Calculation parameters. - Completion
status and warnings. - User or process responsible for initiating the
job.

### 10.4 AI Data Readiness

Before enabling forecasting or reserve estimation, verify that: -
Historical data is sufficiently complete and consistent. - Features and
target variables are explicitly defined. - Train/test validation avoids
data leakage. - Results are compared with a baseline. - Model
limitations and uncertainty are communicated to users.

------------------------------------------------------------------------

## 11. Security and Access Control

-   Use Supabase Auth for identity according to the chosen integration.
-   Verify user tokens on protected backend requests.
-   Apply role- and site-based authorization in the backend.
-   Protect uploaded files and report downloads with access policies or
    short-lived signed access where appropriate.
-   Validate all user input and uploaded data.
-   Store secrets in environment configuration or a secret manager, not
    in frontend source code.
-   Use HTTPS in deployed environments.
-   Log important events without recording passwords, tokens, or other
    secrets.
-   Back up the database and define a recovery procedure.
-   Test that one mine site's users cannot access another site's
    protected data without explicit authorization.

Authentication alone does not guarantee correct authorization. API,
database, and storage access policies must be configured and tested
together.

------------------------------------------------------------------------

## 12. Implementation Phases

### Phase 1 --- Application Foundation

-   Set up FastAPI and connect it to PostgreSQL/PostGIS.
-   Configure Supabase Auth and storage as needed.
-   Define mine-site, survey, file, and processing-job records.
-   Connect the existing React/Vite frontend to the backend.
-   Implement secure authentication and role-aware navigation.

### Phase 2 --- Survey Data Management

-   Add survey area and survey metadata workflows.
-   Implement file upload/import and validation.
-   Record processing status and source-file metadata.
-   Add a survey history and data-quality view.

### Phase 3 --- Geospatial Processing

-   Implement LiDAR/point-cloud ingestion.
-   Generate terrain products where supported.
-   Implement terrain profile analysis.
-   Implement cut-and-fill analysis.
-   Implement current-versus-previous volume comparison.
-   Implement road profile and slope analysis.
-   Validate calculations against known test datasets.

### Phase 4 --- Dashboards and Reporting

-   Build the interactive mine map and analysis dashboards.
-   Add production and equipment data views.
-   Add PDF report generation.
-   Implement role-specific dashboard content and access checks.

### Phase 5 --- Optional Satellite and AI Modules

-   Integrate satellite processing if the required data access is
    available.
-   Implement and validate Kriging-based reserve estimation with
    appropriate geological inputs.
-   Train and evaluate the XGBoost production forecast.
-   Add what-if scenarios, action recommendations, and risk-calendar
    rules.
-   Document model limitations and monitoring procedures.

### Phase 6 --- Integration and Acceptance

-   Test end-to-end workflows.
-   Validate spatial calculations, units, and coordinate handling.
-   Test access controls and cross-site isolation.
-   Test large-file and failed-job behavior.
-   Verify report accuracy and source traceability.
-   Conduct user acceptance testing with surveyor and mine-manager
    workflows.

------------------------------------------------------------------------

## 13. Acceptance Criteria

The platform should not be considered complete until the relevant
implemented modules pass tests such as:

-   A permitted user can create a survey record and associate source
    files with it.
-   Invalid or incompatible files are rejected with understandable
    errors.
-   Processing jobs expose a clear status and report failures.
-   Terrain profile outputs include distance and elevation values with
    documented units.
-   Cut-and-fill calculations identify the reference method, area,
    units, and resulting volumes.
-   Survey comparison checks coordinate and vertical-reference
    compatibility before calculating differences.
-   Road profile outputs include the configured length, elevation
    profile, and slope metrics.
-   Map layers correspond to the selected mine site and survey.
-   Production charts distinguish observed values from forecasts.
-   Optional AI outputs are not shown as validated if no validated model
    is configured.
-   PDF reports identify their source datasets and calculation context.
-   Protected API routes and files reject unauthorized access.
-   Users cannot access records outside their permitted mine-site scope.
-   Processing and report errors are logged without exposing secrets.

Numerical tolerances for geospatial outputs must be set using
project-specific reference datasets and survey requirements; the
supplied diagrams do not define universal tolerances.

------------------------------------------------------------------------

## 14. Assumptions and Items Requiring Confirmation

The supplied diagrams and project notes establish the intended workflow,
but do not fully specify every integration or operational parameter.
Confirm the following before final implementation:

1.  Exact UAV and LiDAR hardware models, payloads, file formats, and
    available control/telemetry APIs.
2.  Whether live mission planning and drone control are required, or
    whether survey planning and file import are sufficient for the first
    release.
3.  Required point-cloud formats, expected file sizes, and target
    processing time.
4.  Required coordinate reference systems, vertical datum, units, and
    survey accuracy criteria.
5.  Exact PostgreSQL schema; the diagram's "10 tables" is not enough to
    define it.
6.  Production and equipment source systems, update frequency, and
    integration protocols.
7.  Satellite data access and the precise meaning of "ground heat" in
    the intended Landsat workflow.
8.  Geological data availability and validation requirements for
    Kriging.
9.  Historical data availability and success criteria for the 14-day
    XGBoost forecast.
10. Exact role/permission matrix and intended meaning of "UK4G UI/UX."
11. Hosting environment, backup policy, storage limits, and expected
    concurrent users.

Where a capability depends on an unconfirmed external system or
unavailable data, implement a clear integration boundary and show an
unavailable/not-configured state rather than fabricated live data.

------------------------------------------------------------------------

## 15. Conclusion

The proposed platform combines a React 18 + Vite frontend with a Python
FastAPI backend, PostgreSQL/PostGIS spatial storage, Supabase
authentication/storage services, and a modular geospatial processing
pipeline. Its core surveying functions cover survey records, LiDAR
processing, terrain products, terrain and road profiles, cut-and-fill
calculations, and volume comparison. Production dashboards, satellite
analysis, Kriging-based reserve estimation, XGBoost forecasting, what-if
simulation, risk calendars, and action recommendations extend the
platform when their data and validation requirements are met.

The implementation should prioritize reliable survey data management and
reproducible geospatial calculations, then add operational integrations
and AI capabilities incrementally. The supplied diagrams define the
intended system workflow; hardware integrations, calculation tolerances,
database schema, model performance, and compliance requirements still
require project-specific confirmation and testing.
