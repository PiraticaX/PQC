"""
QShield Enterprise
==================

Reports API

Enterprise Reporting & Document Generation Endpoints.

Responsibilities:

- Report creation
- Report generation
- Report retrieval
- Report export
- Report storage
- Executive reporting

Integrates with:

- Report Service
- Analytics Service
- Compliance Service
- Storage Service
- Audit Service

"""

from __future__ import annotations


import logging


from typing import Any


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status


from pydantic import BaseModel


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.report_service import ReportService
from app.services.storage_service import StorageService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/reports",

)



# ============================================================
# Request Schemas
# ============================================================


class ReportCreateRequest(
    BaseModel,
):
    """
    Report creation payload.
    """

    name: str

    report_type: str

    parameters: dict[str, Any] | None = None



class ReportGenerateRequest(
    BaseModel,
):
    """
    Report generation payload.
    """

    format: str = "pdf"

    include_charts: bool = True

    include_details: bool = True



class ReportScheduleRequest(
    BaseModel,
):
    """
    Report scheduling payload.
    """

    schedule: str

    recipients: list[str] | None = None



# ============================================================
# Report Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    request: ReportCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create report definition.
    """

    service = ReportService(
        db
    )


    try:

        return await service.create_report(

            name=request.name,

            report_type=
                request.report_type,

            parameters=
                request.parameters,

        )


    except Exception as exc:

        logger.exception(
            "Report creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_reports(
    report_type: str | None = None,
    db: Session = Depends(
        get_db
    ),
):
    """
    List reports.
    """

    service = ReportService(
        db
    )


    return await service.list_reports(

        report_type

    )



@router.get(
    "/{report_id}",
)
async def get_report(
    report_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve report.
    """

    service = ReportService(
        db
    )


    report = await service.get_report(

        report_id

    )


    if not report:

        raise HTTPException(

            status_code=404,

            detail="Report not found.",

        )


    return report



@router.delete(
    "/{report_id}",
)
async def delete_report(
    report_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete report.
    """

    service = ReportService(
        db
    )


    return await service.delete_report(

        report_id

    )



# ============================================================
# Generation
# ============================================================


@router.post(
    "/{report_id}/generate",
)
async def generate_report(
    report_id: UUID,
    request: ReportGenerateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Generate report document.

    Supports:

    - PDF
    - CSV
    - JSON
    - HTML

    """

    service = ReportService(
        db
    )


    return await service.generate_report(

        report_id=report_id,

        format=request.format,

        include_charts=
            request.include_charts,

        include_details=
            request.include_details,

    )



@router.get(
    "/{report_id}/download",
)
async def download_report(
    report_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Download generated report.
    """

    service = StorageService(
        db
    )


    return await service.get_report_file(

        report_id

    )



# ============================================================
# Report Scheduling
# ============================================================


@router.post(
    "/{report_id}/schedule",
)
async def schedule_report(
    report_id: UUID,
    request: ReportScheduleRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Schedule recurring report generation.
    """

    service = ReportService(
        db
    )


    return await service.schedule_report(

        report_id=report_id,

        schedule=request.schedule,

        recipients=request.recipients,

    )



@router.delete(
    "/{report_id}/schedule",
)
async def remove_report_schedule(
    report_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Remove report schedule.
    """

    service = ReportService(
        db
    )


    return await service.remove_schedule(

        report_id

    )



# ============================================================
# Templates
# ============================================================


@router.get(
    "/templates/list",
)
async def list_report_templates(
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve available report templates.
    """

    service = ReportService(
        db
    )


    return await service.list_templates()



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def report_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    Report analytics.
    """

    service = ReportService(
        db
    )


    return await service.report_statistics()



@router.get(
    "/health",
)
async def report_health():
    """
    Reporting engine health.
    """

    return {

        "reporting":

            {

                "status":

                    "healthy",


                "generation":

                    "enabled",


                "exports":

                    [

                        "PDF",

                        "CSV",

                        "JSON",

                        "HTML",

                    ],

            }

    }
