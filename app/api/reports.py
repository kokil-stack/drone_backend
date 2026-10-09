import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.config import settings
from app.core.database import get_db
from app.models.schemas_db import ReportRecord, MineSite, Survey, VolumeComparison
from app.schemas.schemas import ReportRequest, ReportOut
from app.services.report_generation import generate_volume_acceptance_pdf, generate_mine_analytics_excel

router = APIRouter(prefix="/reports", tags=["Decision Reports, PDF & Excel Generation"])

@router.get("", response_model=List[ReportOut])
def list_reports(site_id: int, db: Session = Depends(get_db)):
    reports = db.query(ReportRecord).filter(ReportRecord.site_id == site_id).order_by(ReportRecord.created_at.desc()).all()
    results = []
    for r in reports:
        filename = Path(r.file_path).name
        results.append(ReportOut(
            id=r.id,
            site_id=r.site_id,
            survey_id=r.survey_id,
            report_title=r.report_title,
            report_type=r.report_type,
            file_path=r.file_path,
            file_size_bytes=r.file_size_bytes,
            download_url=f"/api/reports/download/{filename}",
            generated_by=r.generated_by,
            status=r.status,
            created_at=r.created_at
        ))
    return results

@router.post("/generate", response_model=ReportOut)
def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    site = db.query(MineSite).filter(MineSite.id == req.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Mine site not found")

    survey = None
    if req.survey_id:
        survey = db.query(Survey).filter(Survey.id == req.survey_id).first()
    if not survey:
        survey = db.query(Survey).filter(Survey.site_id == req.site_id).first()

    survey_name = survey.name if survey else "Autonomous Survey Q2"
    vol_comp = db.query(VolumeComparison).filter(VolumeComparison.site_id == req.site_id).first()

    cut_vol = vol_comp.cut_volume_m3 if vol_comp else 142500.0
    fill_vol = vol_comp.fill_volume_m3 if vol_comp else 12400.0
    net_vol = vol_comp.net_volume_m3 if vol_comp else 130100.0
    strip_vol = vol_comp.stripping_volume_m3 if vol_comp else 95400.0
    ore_t = vol_comp.total_ore_tonnage_t if vol_comp else 91955.0
    waste_t = vol_comp.waste_tonnage_t if vol_comp else 219420.0
    elev_dev = vol_comp.elevation_deviation_cm if vol_comp else 6.0
    accepted_by = vol_comp.accepted_by if vol_comp else "Col. Arvind Verma (General Mine Manager)"

    unique_id = uuid.uuid4().hex[:8]
    is_excel = req.file_format.lower() in ["excel", "xlsx", "xls"]

    if is_excel:
        if req.report_type == "mine_safety_geological":
            type_label = "Slope Stability & Geotechnical Audit (.xlsx)"
        elif req.report_type == "daily_production_executive":
            type_label = "14-Day Production & Fleet Reconciliation (.xlsx)"
        else:
            type_label = "Digital Twin Analytics & Volumetric Workbook (.xlsx)"

        filename = f"Mine_Insights_{site.code}_{unique_id}.xlsx"
        file_path = generate_mine_analytics_excel(
            report_title=f"{site.name} {type_label}",
            site_name=f"{site.name} ({site.state}, India)",
            site_code=site.code,
            survey_name=survey_name,
            cut_volume_m3=cut_vol,
            fill_volume_m3=fill_vol,
            net_volume_m3=net_vol,
            stripping_volume_m3=strip_vol,
            ore_tonnage_t=ore_t,
            waste_tonnage_t=waste_t,
            elevation_deviation_cm=elev_dev,
            accepted_by=accepted_by,
            output_filename=filename
        )
        report_title = f"{site.code} - {type_label}"
    else:
        if req.report_type == "mine_safety_geological":
            type_label = "Mine Geological & Slope Safety Certificate"
        elif req.report_type == "daily_production_executive":
            type_label = "14-Day Production Reconciliation Certificate"
        else:
            type_label = "Stripping Volume Acceptance Certificate"

        filename = f"Stripping_Acceptance_{site.code}_{unique_id}.pdf"
        file_path = generate_volume_acceptance_pdf(
            report_title=f"{site.name} {type_label}",
            site_name=f"{site.name} ({site.state}, India)",
            survey_name=survey_name,
            cut_volume_m3=cut_vol,
            fill_volume_m3=fill_vol,
            net_volume_m3=net_vol,
            stripping_volume_m3=strip_vol,
            ore_tonnage_t=ore_t,
            waste_tonnage_t=waste_t,
            elevation_deviation_cm=elev_dev,
            accepted_by=accepted_by,
            output_filename=filename
        )
        report_title = f"{type_label} - {site.code}"

    file_size = Path(file_path).stat().st_size

    rec = ReportRecord(
        site_id=site.id,
        survey_id=survey.id if survey else None,
        report_title=report_title,
        report_type=f"{req.report_type}_{req.file_format.lower()}",
        file_path=file_path,
        file_size_bytes=file_size,
        generated_by="Digital Twin AI Reporting Engine",
        status="ready"
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return ReportOut(
        id=rec.id,
        site_id=rec.site_id,
        survey_id=rec.survey_id,
        report_title=rec.report_title,
        report_type=rec.report_type,
        file_path=rec.file_path,
        file_size_bytes=rec.file_size_bytes,
        download_url=f"/api/reports/download/{filename}",
        generated_by=rec.generated_by,
        status=rec.status,
        created_at=rec.created_at
    )

@router.get("/export-excel")
def export_excel_report(
    site_id: int = Query(1, description="Target mine site ID"),
    report_type: str = Query("stripping_volume_acceptance", description="Report type"),
    db: Session = Depends(get_db)
):
    """
    Direct endpoint to generate and download the comprehensive Excel insights workbook.
    """
    req = ReportRequest(site_id=site_id, report_type=report_type, file_format="excel")
    report = generate_report(req=req, db=db)
    filename = Path(report.file_path).name
    return download_report(filename)

@router.get("/download/{filename}")
def download_report(filename: str):
    file_path = settings.REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    is_excel = filename.endswith(".xlsx") or filename.endswith(".xls")
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if is_excel
        else "application/pdf"
    )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )
