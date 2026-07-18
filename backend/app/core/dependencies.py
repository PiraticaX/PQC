"""
QShield Enterprise
==================

FastAPI Dependency Infrastructure.

Responsibilities:

- Authentication dependencies
- Current user resolution
- Role verification
- Permission enforcement
- Database injection helpers
- Security context handling

Integrates with:

- Security module
- User Service
- Permission Service
- Role Service
- Database Layer

"""

from __future__ import annotations


import logging


from typing import Annotated


from uuid import UUID


from fastapi import Depends
from fastapi import HTTPException
from fastapi import Security
from fastapi.security import OAuth2PasswordBearer


from sqlalchemy.ext.asyncio import AsyncSession



from app.core.database import get_db


from app.core.security import validate_access_token


from app.core.exceptions import AuthenticationException
from app.core.exceptions import PermissionDeniedException



logger = logging.getLogger(__name__)



# ============================================================
# Authentication Scheme
# ============================================================


oauth2_scheme = OAuth2PasswordBearer(

    tokenUrl="/api/v1/auth/login"

)



# ============================================================
# Database Dependency
# ============================================================


DatabaseSession = Annotated[

    AsyncSession,

    Depends(get_db)

]



# ============================================================
# Current User Context
# ============================================================


class CurrentUser:
    """
    Authenticated user context.

    Contains:

    - User identity
    - Organization
    - Roles
    - Permissions

    """

    def __init__(
        self,
        user_id: UUID,
        email: str | None = None,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
    ):

        self.user_id = user_id

        self.email = email

        self.roles = roles or []

        self.permissions = permissions or []



    def has_role(
        self,
        role: str,
    ) -> bool:
        """
        Check role membership.
        """

        return role in self.roles



    def has_permission(
        self,
        permission: str,
    ) -> bool:
        """
        Check permission.
        """

        return permission in self.permissions



# ============================================================
# Authentication Dependency
# ============================================================


async def get_current_user(
    token: str = Security(
        oauth2_scheme
    ),
) -> CurrentUser:
    """
    Resolve authenticated user.

    Flow:

    JWT Token

        |

        v

    Decode Token

        |

        v

    User Context

    """

    try:

        payload = validate_access_token(

            token

        )


        user_id = payload.get(

            "sub"

        )


        if not user_id:

            raise AuthenticationException()



        return CurrentUser(

            user_id=UUID(

                user_id

            ),

            email=payload.get(

                "email"

            ),

            roles=payload.get(

                "roles",

                []

            ),

            permissions=payload.get(

                "permissions",

                []

            ),

        )


    except Exception as exc:

        logger.warning(

            "Authentication failed: %s",

            str(exc),

        )


        raise HTTPException(

            status_code=401,

            detail="Authentication required.",

        )



# ============================================================
# Optional Authentication
# ============================================================


async def get_optional_user(
    token: str | None = Security(
        oauth2_scheme,
        scopes=[],
    ),
) -> CurrentUser | None:
    """
    Optional authentication.

    Used for:

    - Public APIs
    - Personalized responses

    """

    if not token:

        return None


    try:

        return await get_current_user(

            token

        )


    except Exception:

        return None



# ============================================================
# Role Dependency Factory
# ============================================================


def require_role(
    required_role: str,
):
    """
    Create role checker dependency.

    Example:

        Depends(require_role("admin"))

    """

    async def role_checker(
        user: CurrentUser = Depends(
            get_current_user
        ),
    ):

        if not user.has_role(

            required_role

        ):

            raise HTTPException(

                status_code=403,

                detail="Insufficient role.",

            )


        return user



    return role_checker



# ============================================================
# Permission Dependency Factory
# ============================================================


def require_permission(
    permission: str,
):
    """
    Create permission checker dependency.

    Example:

        Depends(
            require_permission(
                "users.read"
            )
        )

    """

    async def permission_checker(
        user: CurrentUser = Depends(
            get_current_user
        ),
    ):

        if not user.has_permission(

            permission

        ):

            raise PermissionDeniedException(

                resource=permission

            )


        return user



    return permission_checker



# ============================================================
# Administrative Access
# ============================================================


async def require_admin(
    user: CurrentUser = Depends(
        get_current_user
    ),
):
    """
    Require administrator access.
    """

    admin_roles = [

        "admin",

        "super_admin",

    ]


    if not any(

        role in user.roles

        for role in admin_roles

    ):

        raise HTTPException(

            status_code=403,

            detail="Administrator access required.",

        )


    return user



# ============================================================
# Organization Context
# ============================================================


async def get_organization_id(
    user: CurrentUser = Depends(
        get_current_user
    ),
) -> UUID | None:
    """
    Retrieve organization context.

    """

    return getattr(

        user,

        "organization_id",

        None

    )