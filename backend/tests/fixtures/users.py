"""
QShield Enterprise
==================

User Test Fixtures.

Provides:

- Mock users
- Authentication users
- Role-based users
- Permission test data

Used across:

- Authentication tests
- API tests
- Authorization tests
- Service tests

"""

from __future__ import annotations



from typing import Any



# ============================================================
# User Templates
# ============================================================


def create_user(
    user_id: str = "usr_test001",
    email: str = "user@qshield.test",
    role: str = "user",
) -> dict[str, Any]:
    """
    Create generic test user.

    """

    return {

        "id":

            user_id,


        "email":

            email,


        "username":

            email.split("@")[0],


        "roles":

            [

                role

            ],


        "permissions":

            [

                "read"

            ],


        "is_active":

            True,

    }



# ============================================================
# Standard Users
# ============================================================


def normal_user() -> dict[str, Any]:
    """
    Regular application user.

    """

    return create_user()



def analyst_user() -> dict[str, Any]:
    """
    Security analyst user.

    """

    return {

        "id":

            "usr_analyst001",


        "email":

            "analyst@qshield.test",


        "username":

            "analyst",


        "roles":

            [

                "analyst"

            ],


        "permissions":

            [

                "read",

                "scan.execute",

                "report.view",

            ],


        "is_active":

            True,

    }



def admin_user() -> dict[str, Any]:
    """
    System administrator.

    """

    return {

        "id":

            "usr_admin001",


        "email":

            "admin@qshield.test",


        "username":

            "admin",


        "roles":

            [

                "admin"

            ],


        "permissions":

            [

                "*",

            ],


        "is_active":

            True,

    }



# ============================================================
# Security Users
# ============================================================


def security_operator() -> dict[str, Any]:
    """
    SOC/security operator.

    """

    return {

        "id":

            "usr_soc001",


        "email":

            "soc@qshield.test",


        "username":

            "security_operator",


        "roles":

            [

                "security_operator"

            ],


        "permissions":

            [

                "security.read",

                "security.manage",

                "incident.create",

            ],


        "is_active":

            True,

    }



# ============================================================
# Invalid Users
# ============================================================


def inactive_user() -> dict[str, Any]:
    """
    Disabled user account.

    """

    return {

        "id":

            "usr_disabled001",


        "email":

            "disabled@qshield.test",


        "username":

            "disabled",


        "roles":

            [

                "user"

            ],


        "permissions":

            [],


        "is_active":

            False,

    }



def invalid_user() -> dict[str, Any]:
    """
    Invalid user payload.

    """

    return {

        "id":

            None,


        "email":

            "invalid-email",


        "roles":

            [],


    }



# ============================================================
# Collections
# ============================================================


def user_collection() -> list[dict[str, Any]]:
    """
    Multiple test users.

    """

    return [

        normal_user(),

        analyst_user(),

        admin_user(),

        security_operator(),

    ]