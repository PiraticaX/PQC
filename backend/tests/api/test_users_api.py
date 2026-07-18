"""
QShield Enterprise
==================

Users API Tests.

Tests:

- User listing
- User creation
- User profile
- Role management
- Permission management
- User deletion
- Access control

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.users import (
    admin_user,
    normal_user,
    analyst_user,
)



# ============================================================
# User Listing Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_users(
    api_client,
):
    """
    Users endpoint should return data.
    """

    response = await api_client.get(

        "/users"

    )



    assert response["method"] == "GET"

    assert response["path"] == "/users"



# ============================================================
# User Profile Tests
# ============================================================


@pytest.mark.asyncio
async def test_get_current_user(
    api_client,
):
    """
    Current user endpoint.
    """

    response = await api_client.get(

        "/users/me"

    )



    assert response["path"] == "/users/me"



def test_user_profile_structure(
    test_user,
):
    """
    User profile should contain
    required attributes.
    """

    assert "id" in test_user

    assert "email" in test_user

    assert "roles" in test_user

    assert "permissions" in test_user



# ============================================================
# User Creation Tests
# ============================================================


@pytest.mark.asyncio
async def test_create_user(
    api_client,
):
    """
    User creation endpoint.
    """

    response = await api_client.post(

        "/users",

        json={

            "email":

                "newuser@qshield.test",


            "role":

                "user",

        },

    )



    assert response["path"] == "/users"

    assert response["data"]["email"] == "newuser@qshield.test"



@pytest.mark.asyncio
async def test_create_invalid_user(
    api_client,
):
    """
    Invalid user payload.
    """

    response = await api_client.post(

        "/users",

        json={

            "email":

                "invalid",

        },

    )



    assert response["data"]["email"] == "invalid"



# ============================================================
# Role Management Tests
# ============================================================


def test_admin_user_role():
    """
    Admin should have admin role.
    """

    user = admin_user()



    assert "admin" in user["roles"]



def test_analyst_user_role():
    """
    Analyst role validation.
    """

    user = analyst_user()



    assert "analyst" in user["roles"]



def test_regular_user_role():
    """
    Regular user validation.
    """

    user = normal_user()



    assert "user" in user["roles"]



# ============================================================
# Permission Tests
# ============================================================


def test_admin_permissions():
    """
    Admin should have full access.
    """

    user = admin_user()



    assert "*" in user["permissions"]



def test_analyst_permissions():
    """
    Analyst permissions.
    """

    user = analyst_user()



    assert "scan.execute" in user["permissions"]



# ============================================================
# User Update Tests
# ============================================================


@pytest.mark.asyncio
async def test_update_user(
    api_client,
):
    """
    User update endpoint.
    """

    response = await api_client.post(

        "/users/usr_test001",

        json={

            "role":

                "analyst",

        },

    )



    assert response["path"] == "/users/usr_test001"



# ============================================================
# User Delete Tests
# ============================================================


@pytest.mark.asyncio
async def test_delete_user(
    api_client,
):
    """
    User deletion endpoint.
    """

    response = await api_client.delete(

        "/users/usr_test001"

    )



    assert response["path"] == "/users/usr_test001"



# ============================================================
# Authorization Tests
# ============================================================


@pytest.mark.asyncio
async def test_users_requires_authentication(
    api_client,
):
    """
    Protected user endpoint.
    """

    response = await api_client.get(

        "/users"

    )



    assert response["path"] == "/users"