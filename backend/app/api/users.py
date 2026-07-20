"""
QShield Enterprise
==================

Users API

User Identity Management Endpoints.

Responsibilities:

- User creation
- User retrieval
- User updates
- User deletion
- User role visibility
- User permission visibility
- User account management

Integrates with:

- User Service
- Role Service
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
from pydantic import EmailStr


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.permission_service import PermissionService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/users",

)



# ============================================================
# Request Schemas
# ============================================================


class UserCreateRequest(
    BaseModel,
):
    """
    User creation payload.
    """

    email: EmailStr

    username: str

    password: str

    first_name: str | None = None

    last_name: str | None = None



class UserUpdateRequest(
    BaseModel,
):
    """
    User update payload.
    """

    first_name: str | None = None

    last_name: str | None = None

    email: EmailStr | None = None

    is_active: bool | None = None



# ============================================================
# User Routes
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: UserCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create new user.
    """

    service = UserService(
        db
    )


    try:

        return await service.create_user(

            email=request.email,

            username=request.username,

            password=request.password,

            first_name=request.first_name,

            last_name=request.last_name,

        )


    except Exception as exc:

        logger.exception(
            "User creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_users(
    db: Session = Depends(
        get_db
    ),
):
    """
    List users.
    """

    service = UserService(
        db
    )


    return await service.list_users()



@router.get(
    "/{user_id}",
)
async def get_user(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve user details.
    """

    service = UserService(
        db
    )


    user = await service.get_user(
        user_id
    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found.",

        )


    return user



@router.put(
    "/{user_id}",
)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Update user account.
    """

    service = UserService(
        db
    )


    updates = request.model_dump(
        exclude_none=True
    )


    return await service.update_user(

        user_id=user_id,

        updates=updates,

    )



@router.delete(
    "/{user_id}",
)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete user.
    """

    service = UserService(
        db
    )


    return await service.delete_user(
        user_id
    )



# ============================================================
# User Authorization Views
# ============================================================


@router.get(
    "/{user_id}/roles",
)
async def user_roles(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve user roles.
    """

    service = RoleService(
        db
    )


    return await service.get_user_roles(

        user_id

    )



@router.get(
    "/{user_id}/permissions",
)
async def user_permissions(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve user permissions.
    """

    service = PermissionService(
        db
    )


    return await service.get_user_permissions(

        user_id

    )



# ============================================================
# User Security
# ============================================================


@router.post(
    "/{user_id}/activate",
)
async def activate_user(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Activate user account.
    """

    service = UserService(
        db
    )


    return await service.activate_user(

        user_id

    )



@router.post(
    "/{user_id}/deactivate",
)
async def deactivate_user(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Disable user account.
    """

    service = UserService(
        db
    )


    return await service.deactivate_user(

        user_id

    )



@router.get(
    "/statistics/summary",
)
async def user_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    User analytics summary.
    """

    service = UserService(
        db
    )


    return await service.user_statistics()
