"""
QShield Enterprise
==================

Assets API

Enterprise Asset Discovery & Management Endpoints.

Responsibilities:

- Asset registration
- Asset inventory
- Asset updates
- Asset deletion
- Asset scanning
- Asset findings lookup
- Asset intelligence

Integrates with:

- Asset Service
- Scan Service
- Finding Service
- Risk Service
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


from app.services.asset_service import AssetService
from app.services.scan_service import ScanService
from app.services.finding_service import FindingService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/assets",

)



# ============================================================
# Request Schemas
# ============================================================


class AssetCreateRequest(
    BaseModel,
):
    """
    Asset creation payload.
    """

    name: str

    asset_type: str

    hostname: str | None = None

    ip_address: str | None = None

    metadata: dict[str, Any] | None = None



class AssetUpdateRequest(
    BaseModel,
):
    """
    Asset update payload.
    """

    name: str | None = None

    metadata: dict[str, Any] | None = None

    status: str | None = None



class AssetScanRequest(
    BaseModel,
):
    """
    Asset scan request.
    """

    scan_type: str = "security"



# ============================================================
# Asset Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_asset(
    request: AssetCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Register new asset.
    """

    service = AssetService(
        db
    )


    try:

        return await service.create_asset(

            name=request.name,

            asset_type=
                request.asset_type,

            hostname=
                request.hostname,

            ip_address=
                request.ip_address,

            metadata=
                request.metadata,

        )


    except Exception as exc:

        logger.exception(
            "Asset creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_assets(
    asset_type: str | None = None,
    asset_status: str | None = None,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve asset inventory.
    """

    service = AssetService(
        db
    )


    return await service.list_assets(

        asset_type=asset_type,

        status=asset_status,

    )



@router.get(
    "/{asset_id}",
)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve asset details.
    """

    service = AssetService(
        db
    )


    asset = await service.get_asset(

        asset_id

    )


    if not asset:

        raise HTTPException(

            status_code=404,

            detail="Asset not found.",

        )


    return asset



@router.put(
    "/{asset_id}",
)
async def update_asset(
    asset_id: UUID,
    request: AssetUpdateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update asset.
    """

    service = AssetService(
        db
    )


    return await service.update_asset(

        asset_id=asset_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{asset_id}",
)
async def delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Remove asset.
    """

    service = AssetService(
        db
    )


    return await service.delete_asset(

        asset_id

    )



# ============================================================
# Asset Security Operations
# ============================================================


@router.post(
    "/{asset_id}/scan",
)
async def scan_asset(
    asset_id: UUID,
    request: AssetScanRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Initiate asset security scan.
    """

    service = ScanService(
        db
    )


    return await service.start_scan(

        asset_id=asset_id,

        scan_type=
            request.scan_type,

    )



@router.get(
    "/{asset_id}/findings",
)
async def asset_findings(
    asset_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve asset vulnerabilities.
    """

    service = FindingService(
        db
    )


    return await service.get_asset_findings(

        asset_id

    )



@router.get(
    "/{asset_id}/history",
)
async def asset_history(
    asset_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve asset activity history.
    """

    service = AssetService(
        db
    )


    return await service.get_asset_history(

        asset_id

    )



# ============================================================
# Asset Discovery
# ============================================================


@router.post(
    "/discover",
)
async def discover_assets(
    network: str,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Discover assets from network.

    """

    service = AssetService(
        db
    )


    return await service.discover_assets(

        network

    )



@router.post(
    "/sync",
)
async def sync_assets(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Synchronize asset inventory.
    """

    service = AssetService(
        db
    )


    return await service.sync_inventory()



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def asset_statistics(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Asset inventory analytics.
    """

    service = AssetService(
        db
    )


    return await service.asset_statistics()



@router.get(
    "/health",
)
async def asset_health():
    """
    Asset service health.
    """

    return {

        "assets":

            {

                "status":

                    "healthy",


                "inventory":

                    "available",


                "discovery":

                    "enabled",

            }

    }