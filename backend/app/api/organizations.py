"""
QShield Enterprise
==================

Organizations API

Organization Management Endpoints.

Responsibilities:

- Organization creation
- Organization retrieval
- Organization updates
- Organization deletion
- Organization member management
- Organization statistics
- Tenant administration

Integrates with:

- Organization Service
- User Service
- Permission Service
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


from app.services.organization_service import OrganizationService
from app.services.user_service import UserService
from app.services.permission_service import PermissionService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/organizations",

)



# ============================================================
# Request Schemas
# ============================================================


class OrganizationCreateRequest(
    BaseModel,
):
    """
    Organization creation payload.
    """

    name: str

    description: str | None = None

    domain: str | None = None



class OrganizationUpdateRequest(
    BaseModel,
):
    """
    Organization update payload.
    """

    name: str | None = None

    description: str | None = None

    domain: str | None = None

    is_active: bool | None = None



class AddMemberRequest(
    BaseModel,
):
    """
    Add organization member.
    """

    user_id: UUID

    role: str | None = None



# ============================================================
# Organization Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    request: OrganizationCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create organization tenant.
    """

    service = OrganizationService(
        db
    )


    try:

        return await service.create_organization(

            name=request.name,

            description=request.description,

            domain=request.domain,

        )


    except Exception as exc:

        logger.exception(
            "Organization creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_organizations(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List organizations.
    """

    service = OrganizationService(
        db
    )


    return await service.list_organizations()



@router.get(
    "/{organization_id}",
)
async def get_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve organization.
    """

    service = OrganizationService(
        db
    )


    organization = await service.get_organization(

        organization_id

    )


    if not organization:

        raise HTTPException(

            status_code=404,

            detail="Organization not found.",

        )


    return organization



@router.put(
    "/{organization_id}",
)
async def update_organization(
    organization_id: UUID,
    request: OrganizationUpdateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update organization.
    """

    service = OrganizationService(
        db
    )


    updates = request.model_dump(

        exclude_none=True

    )


    return await service.update_organization(

        organization_id=organization_id,

        updates=updates,

    )



@router.delete(
    "/{organization_id}",
)
async def delete_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete organization.
    """

    service = OrganizationService(
        db
    )


    return await service.delete_organization(

        organization_id

    )



# ============================================================
# Member Management
# ============================================================


@router.get(
    "/{organization_id}/users",
)
async def organization_users(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List organization members.
    """

    service = UserService(
        db
    )


    return await service.get_organization_users(

        organization_id

    )



@router.post(
    "/{organization_id}/users",
)
async def add_member(
    organization_id: UUID,
    request: AddMemberRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Add user to organization.
    """

    service = OrganizationService(
        db
    )


    return await service.add_member(

        organization_id=organization_id,

        user_id=request.user_id,

        role=request.role,

    )



@router.delete(
    "/{organization_id}/users/{user_id}",
)
async def remove_member(
    organization_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Remove organization member.
    """

    service = OrganizationService(
        db
    )


    return await service.remove_member(

        organization_id=organization_id,

        user_id=user_id,

    )



# ============================================================
# Authorization
# ============================================================


@router.get(
    "/{organization_id}/permissions",
)
async def organization_permissions(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve organization permissions.
    """

    service = PermissionService(
        db
    )


    return await service.get_organization_permissions(

        organization_id

    )



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/{organization_id}/statistics",
)
async def organization_statistics(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Organization statistics.
    """

    service = OrganizationService(
        db
    )


    return await service.organization_statistics(

        organization_id

    )



@router.post(
    "/{organization_id}/activate",
)
async def activate_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Activate organization.
    """

    service = OrganizationService(
        db
    )


    return await service.activate_organization(

        organization_id

    )



@router.post(
    "/{organization_id}/deactivate",
)
async def deactivate_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Disable organization.
    """

    service = OrganizationService(
        db
    )


    return await service.deactivate_organization(

        organization_id

    )