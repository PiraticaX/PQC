"""
QShield Enterprise
==================

Integrations API

External System Integration Management Endpoints.

Responsibilities:

- Integration registration
- Connector management
- Provider configuration
- Connection testing
- Credential lifecycle
- Integration monitoring

Integrates with:

- Integration Service
- API Key Service
- Webhook Service
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


from app.services.integration_service import IntegrationService
from app.services.api_key_service import APIKeyService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/integrations",

)



# ============================================================
# Request Schemas
# ============================================================


class IntegrationCreateRequest(
    BaseModel,
):
    """
    Integration creation payload.
    """

    name: str

    provider: str

    integration_type: str

    auth_type: str = "api_key"

    configuration: dict[str, Any] | None = None



class IntegrationUpdateRequest(
    BaseModel,
):
    """
    Integration update payload.
    """

    name: str | None = None

    configuration: dict[str, Any] | None = None

    status: str | None = None



class CredentialRequest(
    BaseModel,
):
    """
    Credential attachment payload.
    """

    credential_reference: str



# ============================================================
# Integration Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_integration(
    organization_id: UUID,
    request: IntegrationCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Register external integration.
    """

    service = IntegrationService(
        db
    )


    try:

        return await service.create_integration(

            organization_id=organization_id,

            name=request.name,

            provider=request.provider,

            integration_type=
                request.integration_type,

            auth_type=request.auth_type,

            configuration=
                request.configuration,

        )


    except Exception as exc:

        logger.exception(
            "Integration creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_integrations(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List organization integrations.
    """

    service = IntegrationService(
        db
    )


    return await service.get_organization_integrations(

        organization_id

    )



@router.get(
    "/{integration_id}",
)
async def get_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve integration.
    """

    service = IntegrationService(
        db
    )


    integration = await service.get_integration(

        integration_id

    )


    if not integration:

        raise HTTPException(

            status_code=404,

            detail="Integration not found.",

        )


    return integration



@router.put(
    "/{integration_id}",
)
async def update_integration(
    integration_id: UUID,
    request: IntegrationUpdateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update integration configuration.
    """

    service = IntegrationService(
        db
    )


    return await service.update_integration(

        integration_id=integration_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{integration_id}",
)
async def delete_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete integration.
    """

    service = IntegrationService(
        db
    )


    return await service.delete_integration(

        integration_id

    )



# ============================================================
# Connection Management
# ============================================================


@router.post(
    "/{integration_id}/test",
)
async def test_connection(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Test external connection.
    """

    service = IntegrationService(
        db
    )


    return await service.test_connection(

        integration_id=integration_id

    )



@router.post(
    "/{integration_id}/disconnect",
)
async def disconnect_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Disconnect integration.
    """

    service = IntegrationService(
        db
    )


    return await service.disconnect_integration(

        integration_id

    )



# ============================================================
# Credential Management
# ============================================================


@router.post(
    "/{integration_id}/credentials",
)
async def attach_credentials(
    integration_id: UUID,
    request: CredentialRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Attach integration credentials.
    """

    service = IntegrationService(
        db
    )


    return await service.attach_credentials(

        integration_id=integration_id,

        credential_reference=
            request.credential_reference,

    )



@router.post(
    "/{integration_id}/credentials/rotate",
)
async def rotate_credentials(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Rotate integration credentials.
    """

    service = IntegrationService(
        db
    )


    return await service.rotate_credentials(

        integration_id

    )



# ============================================================
# Health & Analytics
# ============================================================


@router.get(
    "/{integration_id}/health",
)
async def integration_health(
    integration_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Integration health status.
    """

    service = IntegrationService(
        db
    )


    return await service.check_health(

        integration_id

    )



@router.get(
    "/statistics/summary",
)
async def integration_statistics(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Integration analytics.
    """

    service = IntegrationService(
        db
    )


    return await service.generate_integration_report(

        organization_id

    )