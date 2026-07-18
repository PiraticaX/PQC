"""
QShield Enterprise
==================

Scans API

Enterprise Security Scanning Management Endpoints.

Responsibilities:

- Scan creation
- Scan execution
- Scan monitoring
- Scan result retrieval
- Scan cancellation
- Vulnerability discovery

Integrates with:

- Scan Service
- Asset Service
- Finding Service
- Scheduler Service
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


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db


from app.services.scan_service import ScanService
from app.services.finding_service import FindingService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/scans",

)



# ============================================================
# Request Schemas
# ============================================================


class ScanCreateRequest(
    BaseModel,
):
    """
    Scan creation payload.
    """

    asset_id: UUID

    scan_type: str = "security"

    profile: str = "standard"



class ScanScheduleRequest(
    BaseModel,
):
    """
    Scheduled scan payload.
    """

    schedule: str

    enabled: bool = True



# ============================================================
# Scan Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_scan(
    request: ScanCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create security scan.
    """

    service = ScanService(
        db
    )


    try:

        return await service.create_scan(

            asset_id=request.asset_id,

            scan_type=request.scan_type,

            profile=request.profile,

        )


    except Exception as exc:

        logger.exception(
            "Scan creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_scans(
    status: str | None = None,
    scan_type: str | None = None,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List security scans.
    """

    service = ScanService(
        db
    )


    return await service.list_scans(

        status=status,

        scan_type=scan_type,

    )



@router.get(
    "/{scan_id}",
)
async def get_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve scan details.
    """

    service = ScanService(
        db
    )


    scan = await service.get_scan(

        scan_id

    )


    if not scan:

        raise HTTPException(

            status_code=404,

            detail="Scan not found.",

        )


    return scan



# ============================================================
# Scan Execution
# ============================================================


@router.post(
    "/{scan_id}/start",
)
async def start_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Start security scan.
    """

    service = ScanService(
        db
    )


    return await service.start_scan(

        scan_id

    )



@router.post(
    "/{scan_id}/stop",
)
async def stop_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Stop running scan.
    """

    service = ScanService(
        db
    )


    return await service.stop_scan(

        scan_id

    )



@router.post(
    "/{scan_id}/cancel",
)
async def cancel_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Cancel scan.
    """

    service = ScanService(
        db
    )


    return await service.cancel_scan(

        scan_id

    )



@router.post(
    "/{scan_id}/retry",
)
async def retry_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retry failed scan.
    """

    service = ScanService(
        db
    )


    return await service.retry_scan(

        scan_id

    )



# ============================================================
# Results
# ============================================================


@router.get(
    "/{scan_id}/results",
)
async def scan_results(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve scan results.
    """

    service = ScanService(
        db
    )


    return await service.get_scan_results(

        scan_id

    )



@router.get(
    "/{scan_id}/findings",
)
async def scan_findings(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve findings generated by scan.
    """

    service = FindingService(
        db
    )


    return await service.get_scan_findings(

        scan_id

    )



# ============================================================
# Scheduling
# ============================================================


@router.post(
    "/{scan_id}/schedule",
)
async def schedule_scan(
    scan_id: UUID,
    request: ScanScheduleRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Schedule recurring security scan.
    """

    service = ScanService(
        db
    )


    return await service.schedule_scan(

        scan_id=scan_id,

        schedule=request.schedule,

        enabled=request.enabled,

    )



@router.delete(
    "/{scan_id}",
)
async def delete_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete scan record.
    """

    service = ScanService(
        db
    )


    return await service.delete_scan(

        scan_id

    )



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def scan_statistics(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Scan analytics.
    """

    service = ScanService(
        db
    )


    return await service.scan_statistics()



@router.get(
    "/health",
)
async def scan_health():
    """
    Scan engine health.
    """

    return {

        "scanner":

            {

                "status":

                    "healthy",


                "engine":

                    "operational",


                "scheduler":

                    "enabled",

            }

    }