"""
QShield Enterprise
==================

Permission Management Infrastructure.

Responsibilities:

- RBAC permission definitions
- Role permission mapping
- Permission evaluation
- Resource access validation
- Security policy enforcement
- Administrative overrides

Integrates with:

- Authentication System
- User Service
- Role Service
- Policy Service

"""

from __future__ import annotations


from typing import Iterable


from dataclasses import dataclass



from app.core.constants import ROLE_ADMIN
from app.core.constants import ROLE_SUPER_ADMIN



# ============================================================
# Permission Definitions
# ============================================================


class Permissions:
    """
    Enterprise permission registry.
    """

    # --------------------------------------------------------
    # User Management
    # --------------------------------------------------------

    USER_READ = "users.read"

    USER_CREATE = "users.create"

    USER_UPDATE = "users.update"

    USER_DELETE = "users.delete"



    # --------------------------------------------------------
    # Organization
    # --------------------------------------------------------

    ORGANIZATION_READ = "organizations.read"

    ORGANIZATION_UPDATE = "organizations.update"

    ORGANIZATION_DELETE = "organizations.delete"



    # --------------------------------------------------------
    # Security Assets
    # --------------------------------------------------------

    ASSET_READ = "assets.read"

    ASSET_CREATE = "assets.create"

    ASSET_UPDATE = "assets.update"

    ASSET_DELETE = "assets.delete"

    ASSET_SCAN = "assets.scan"



    # --------------------------------------------------------
    # Vulnerabilities
    # --------------------------------------------------------

    FINDING_READ = "findings.read"

    FINDING_UPDATE = "findings.update"

    FINDING_RESOLVE = "findings.resolve"



    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    RISK_READ = "risks.read"

    RISK_CREATE = "risks.create"

    RISK_UPDATE = "risks.update"

    RISK_MITIGATE = "risks.mitigate"



    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    REPORT_READ = "reports.read"

    REPORT_CREATE = "reports.create"

    REPORT_EXPORT = "reports.export"



    # --------------------------------------------------------
    # Cryptography
    # --------------------------------------------------------

    KEY_READ = "keys.read"

    KEY_CREATE = "keys.create"

    KEY_ROTATE = "keys.rotate"

    KEY_REVOKE = "keys.revoke"



    # --------------------------------------------------------
    # PQC
    # --------------------------------------------------------

    PQC_READ = "pqc.read"

    PQC_OPERATE = "pqc.operate"



    # --------------------------------------------------------
    # Administration
    # --------------------------------------------------------

    SYSTEM_CONFIG = "system.config"

    AUDIT_READ = "audit.read"

    SECURITY_ADMIN = "security.admin"



# ============================================================
# Permission Groups
# ============================================================


ALL_PERMISSIONS = [

    value

    for name, value in Permissions.__dict__.items()

    if not name.startswith("_")

    and isinstance(value, str)

]



# ============================================================
# Role Mapping
# ============================================================


ROLE_PERMISSIONS: dict[str, set[str]] = {


    ROLE_SUPER_ADMIN:

        set(ALL_PERMISSIONS),



    ROLE_ADMIN:

        {

            Permissions.USER_READ,

            Permissions.USER_CREATE,

            Permissions.USER_UPDATE,

            Permissions.ORGANIZATION_READ,

            Permissions.ASSET_READ,

            Permissions.ASSET_CREATE,

            Permissions.ASSET_UPDATE,

            Permissions.ASSET_SCAN,

            Permissions.FINDING_READ,

            Permissions.FINDING_UPDATE,

            Permissions.RISK_READ,

            Permissions.RISK_UPDATE,

            Permissions.REPORT_READ,

            Permissions.REPORT_EXPORT,

            Permissions.KEY_READ,

            Permissions.KEY_ROTATE,

            Permissions.SECURITY_ADMIN,

        },



    "security_analyst":

        {

            Permissions.ASSET_READ,

            Permissions.ASSET_SCAN,

            Permissions.FINDING_READ,

            Permissions.FINDING_UPDATE,

            Permissions.RISK_READ,

            Permissions.REPORT_READ,

            Permissions.PQC_READ,

        },



    "auditor":

        {

            Permissions.USER_READ,

            Permissions.ORGANIZATION_READ,

            Permissions.ASSET_READ,

            Permissions.FINDING_READ,

            Permissions.RISK_READ,

            Permissions.REPORT_READ,

            Permissions.AUDIT_READ,

        },



    "user":

        {

            Permissions.USER_READ,

            Permissions.REPORT_READ,

        },

}



# ============================================================
# Permission Context
# ============================================================


@dataclass
class PermissionContext:
    """
    Security evaluation context.
    """

    user_id: str

    roles: list[str]

    permissions: list[str]

    organization_id: str | None = None



# ============================================================
# Permission Evaluation
# ============================================================


def get_role_permissions(
    roles: Iterable[str],
) -> set[str]:
    """
    Resolve permissions from roles.
    """

    permissions: set[str] = set()



    for role in roles:

        permissions.update(

            ROLE_PERMISSIONS.get(

                role,

                set()

            )

        )



    return permissions



def has_permission(
    context: PermissionContext,
    permission: str,
) -> bool:
    """
    Check permission access.
    """

    # Super admin bypass

    if ROLE_SUPER_ADMIN in context.roles:

        return True



    if permission in context.permissions:

        return True



    role_permissions = get_role_permissions(

        context.roles

    )


    return permission in role_permissions



def has_any_permission(
    context: PermissionContext,
    permissions: Iterable[str],
) -> bool:
    """
    Check if user has any permission.
    """

    return any(

        has_permission(

            context,

            permission

        )

        for permission in permissions

    )



def has_all_permissions(
    context: PermissionContext,
    permissions: Iterable[str],
) -> bool:
    """
    Check if user has every permission.
    """

    return all(

        has_permission(

            context,

            permission

        )

        for permission in permissions

    )



# ============================================================
# Resource Authorization
# ============================================================


@dataclass
class ResourcePolicy:
    """
    Resource access policy.
    """

    resource: str

    read_permission: str

    write_permission: str

    delete_permission: str



RESOURCE_POLICIES = {


    "users":

        ResourcePolicy(

            resource="users",

            read_permission=

                Permissions.USER_READ,

            write_permission=

                Permissions.USER_UPDATE,

            delete_permission=

                Permissions.USER_DELETE,

        ),



    "assets":

        ResourcePolicy(

            resource="assets",

            read_permission=

                Permissions.ASSET_READ,

            write_permission=

                Permissions.ASSET_UPDATE,

            delete_permission=

                Permissions.ASSET_DELETE,

        ),



    "findings":

        ResourcePolicy(

            resource="findings",

            read_permission=

                Permissions.FINDING_READ,

            write_permission=

                Permissions.FINDING_UPDATE,

            delete_permission=

                Permissions.FINDING_RESOLVE,

        ),

}



def can_access_resource(
    context: PermissionContext,
    resource: str,
    action: str,
) -> bool:
    """
    Validate resource access.

    """

    policy = RESOURCE_POLICIES.get(

        resource

    )


    if not policy:

        return False



    permission_map = {


        "read":

            policy.read_permission,


        "write":

            policy.write_permission,


        "delete":

            policy.delete_permission,

    }



    required = permission_map.get(

        action

    )


    if not required:

        return False



    return has_permission(

        context,

        required

    )