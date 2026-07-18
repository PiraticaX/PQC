"""
QShield Enterprise
==================

Permissions API

Authorization Permission Management Endpoints.

Responsibilities:

- Permission creation
- Permission retrieval
- Permission updates
- Permission deletion
- User permission lookup
- Role permission lookup
- Permission governance

Integrates with:

- Permission Service
- Role Service
- Policy Service
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


from app.services.permission_service import PermissionService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/permissions",

)



# ============================================================
# Request Schemas
# ============================================================


class PermissionCreateRequest(
    BaseModel,
):
    """
    Permission creation payload.
    """

    name: str

    resource: str

    action: str

    description: str | None = None



class PermissionUpdateRequest(
    BaseModel,
):
    """
    Permission update payload.
    """

    name: str | None = None

    description: str | None = None

    is_active: bool | None = None



# ============================================================
# Permission Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    request: PermissionCreateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create authorization permission.
    """

    service = PermissionService(
        db
    )


    try:

        return await service.create_permission(

            name=request.name,

            resource=request.resource,

            action=request.action,

            description=request.description,

        )


    except Exception as exc:

        logger.exception(
            "Permission creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_permissions(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    List permissions.
    """

    service = PermissionService(
        db
    )


    return await service.list_permissions()



@router.get(
    "/{permission_id}",
)
async def get_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve permission.
    """

    service = PermissionService(
        db
    )


    permission = await service.get_permission(

        permission_id

    )


    if not permission:

        raise HTTPException(

            status_code=404,

            detail="Permission not found.",

        )


    return permission



@router.put(
    "/{permission_id}",
)
async def update_permission(
    permission_id: UUID,
    request: PermissionUpdateRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Update permission.
    """

    service = PermissionService(
        db
    )


    return await service.update_permission(

        permission_id=permission_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{permission_id}",
)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Delete permission.
    """

    service = PermissionService(
        db
    )


    return await service.delete_permission(

        permission_id

    )



# ============================================================
# Permission Mapping
# ============================================================


@router.get(
    "/user/{user_id}",
)
async def get_user_permissions(
    user_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve permissions assigned to user.
    """

    service = PermissionService(
        db
    )


    return await service.get_user_permissions(

        user_id

    )



@router.get(
    "/role/{role_id}",
)
async def get_role_permissions(
    role_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Retrieve permissions assigned to role.
    """

    service = PermissionService(
        db
    )


    return await service.get_role_permissions(

        role_id

    )



@router.post(
    "/role/{role_id}/assign/{permission_id}",
)
async def assign_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Assign permission to role.
    """

    service = PermissionService(
        db
    )


    return await service.assign_permission(

        role_id=role_id,

        permission_id=permission_id,

    )



@router.delete(
    "/role/{role_id}/remove/{permission_id}",
)
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Remove permission from role.
    """

    service = PermissionService(
        db
    )


    return await service.remove_permission(

        role_id=role_id,

        permission_id=permission_id,

    )



# ============================================================
# Authorization Checks
# ============================================================


@router.post(
    "/check",
)
async def check_permission(
    user_id: UUID,
    resource: str,
    action: str,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Check whether user has permission.

    Used by:

    - API middleware
    - RBAC engine
    - Policy enforcement

    """

    service = PermissionService(
        db
    )


    return await service.check_permission(

        user_id=user_id,

        resource=resource,

        action=action,

    )



@router.get(
    "/statistics/summary",
)
async def permission_statistics(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Permission analytics.
    """

    service = PermissionService(
        db
    )


    return await service.permission_statistics()