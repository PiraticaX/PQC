"""
QShield Enterprise
==================

Roles API

Role Based Access Control (RBAC) Management Endpoints.

Responsibilities:

- Role creation
- Role retrieval
- Role updates
- Role deletion
- User-role assignment
- Role permission mapping
- RBAC governance

Integrates with:

- Role Service
- Permission Service
- User Service
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


from app.services.role_service import RoleService
from app.services.permission_service import PermissionService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/roles",

)



# ============================================================
# Request Schemas
# ============================================================


class RoleCreateRequest(
    BaseModel,
):
    """
    Role creation payload.
    """

    name: str

    description: str | None = None



class RoleUpdateRequest(
    BaseModel,
):
    """
    Role update payload.
    """

    name: str | None = None

    description: str | None = None

    is_active: bool | None = None



# ============================================================
# Role Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    request: RoleCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create RBAC role.
    """

    service = RoleService(
        db
    )


    try:

        return await service.create_role(

            name=request.name,

            description=request.description,

        )


    except Exception as exc:

        logger.exception(
            "Role creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_roles(
    db: Session = Depends(
        get_db
    ),
):
    """
    List roles.
    """

    service = RoleService(
        db
    )


    return await service.list_roles()



@router.get(
    "/{role_id}",
)
async def get_role(
    role_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve role.
    """

    service = RoleService(
        db
    )


    role = await service.get_role(
        role_id
    )


    if not role:

        raise HTTPException(

            status_code=404,

            detail="Role not found.",

        )


    return role



@router.put(
    "/{role_id}",
)
async def update_role(
    role_id: UUID,
    request: RoleUpdateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Update role.
    """

    service = RoleService(
        db
    )


    return await service.update_role(

        role_id=role_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{role_id}",
)
async def delete_role(
    role_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete role.
    """

    service = RoleService(
        db
    )


    return await service.delete_role(

        role_id

    )



# ============================================================
# User Role Assignment
# ============================================================


@router.post(
    "/{role_id}/users/{user_id}",
)
async def assign_role_to_user(
    role_id: UUID,
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Assign role to user.
    """

    service = RoleService(
        db
    )


    return await service.assign_role(

        user_id=user_id,

        role_id=role_id,

    )



@router.delete(
    "/{role_id}/users/{user_id}",
)
async def remove_role_from_user(
    role_id: UUID,
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Remove role from user.
    """

    service = RoleService(
        db
    )


    return await service.remove_role(

        user_id=user_id,

        role_id=role_id,

    )



@router.get(
    "/{role_id}/users",
)
async def role_users(
    role_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    List users assigned to role.
    """

    service = RoleService(
        db
    )


    return await service.get_role_users(

        role_id

    )



# ============================================================
# Permission Mapping
# ============================================================


@router.get(
    "/{role_id}/permissions",
)
async def role_permissions(
    role_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve role permissions.
    """

    service = PermissionService(
        db
    )


    return await service.get_role_permissions(

        role_id

    )



@router.post(
    "/{role_id}/permissions/{permission_id}",
)
async def assign_permission(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Attach permission to role.
    """

    service = PermissionService(
        db
    )


    return await service.assign_permission(

        role_id=role_id,

        permission_id=permission_id,

    )



@router.delete(
    "/{role_id}/permissions/{permission_id}",
)
async def remove_permission(
    role_id: UUID,
    permission_id: UUID,
    db: Session = Depends(
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
# Analytics
# ============================================================


@router.get(
    "/statistics/summary",
)
async def role_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    Role analytics.
    """

    service = RoleService(
        db
    )


    return await service.role_statistics()
