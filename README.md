# Intelligent Drone-Based Mining & Digital Mine Backend

Backend API built for Indian open-pit digital mine operations, UAV low-altitude remote sensing, LiDAR point cloud processing, volume acceptance, and production decision support.

## Core Capabilities
- **UAV Remote Sensing**: CW-25E VTOL / DJI Enterprise multi-sensor integration (LiDAR 1350m range, 5-lens oblique camera, EO/IR thermal gimbal, image inspectometer, RGB mapping camera).
- **Survey Efficiency**: 4 km² area survey completed in 20 minutes (vs 6 technicians for 8 working days with traditional RTK). 40 km² coverage per flight with 1:1000 scale.
- **High-Precision LiDAR (Zero GCP)**: 6 cm elevation deviation verified with dual differential GPS antennas (directional finding resisting magnetic interference).
- **Noise Filtering**: Automated removal of electromechanical machinery (dumpers, shovels, pumps) and personnel point-cloud noise.
- **Two-Stage Differential Demodulation**: Current vs previous survey DEM comparison for automated stripping & mining volume acceptance.
- **DGMS Road Safety**: Haul road profile slope checks (<= 10% limit) and safety berm height inspection (>= 1.8m).
- **AI Forecasting & Decision Support**: XGBoost 14-day production shortfall prediction, What-If simulator (rain, breakdown, loss ratio), and risk calendar.
- **Automated PDF Reports**: Official ReportLab generated Volume Acceptance Certificates with DGMS & IBM compliance seals.

## Tech Stack
- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite / PostgreSQL with PostGIS
- **ORM / Validation**: SQLAlchemy 2.0 & Pydantic v2
- **PDF Generation**: ReportLab
- **Auth**: JWT with direct bcrypt

## Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run backend server
python run_server.py
# Server starts on http://localhost:8000
# OpenAPI Docs: http://localhost:8000/docs
```

## API Modules
| Route | Description |
|---|---|
| `/api/auth` | Login (`surveyor@digitalmine.in` / `mine1234`), registration, role auth |
| `/api/sites` | Indian open-pit mines (Jharia, Bailadila, Sukinda, Korba, Rampura Agucha) |
| `/api/sensors` | Multi-sensor suite & CW-25E VTOL platform specifications |
| `/api/surveys` | Flight planning (lawnmower paths, waypoints, 20 min flight), telemetry |
| `/api/files` | LAS/LAZ point cloud and GeoTIFF upload |
| `/api/processing-jobs` | Machinery noise filtering & clean DEM generation (6cm deviation) |
| `/api/terrain` | Digital elevation models & grid matrices |
| `/api/analysis/terrain-profile` | Transect distance vs elevation sampling |
| `/api/analysis/road-profile` | DGMS haul road slope % and berm height safety checks |
| `/api/analysis/cut-fill` | Cut and fill volumes relative to reference datum |
| `/api/analysis/volume-comparison` | Two-stage differential demodulation volume acceptance |
| `/api/production` | Daily planned vs actual ore, stripping ratio, diesel usage |
| `/api/equipment` | Haul trucks, excavators, pumps fleet dispatching |
| `/api/forecast` | XGBoost 14-day shortfall forecast & risk calendar |
| `/api/simulations` | What-If simulator (rain, shovel breakdown, loss ratio) |
| `/api/reports` | Automated PDF Volume Acceptance Certificate generation & download |
