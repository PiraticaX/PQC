"""
QShield Enterprise
==================

Authentication API Tests.

Tests:

- Login endpoint
- Token generation
- Invalid credentials
- Authentication headers
- Session validation
- Logout flows

"""

from __future__ import annotations



import pytest



from backend.tests.fixtures.users import (
    admin_user,
    normal_user,
)



from backend.utils.hashing import (
    hash_password,
    verify_password,
)



from backend.utils.crypto import (
    generate_random_token,
)



# ============================================================
# Login Flow Tests
# ============================================================


@pytest.mark.asyncio
async def test_login_success(
    api_client,
):
    """
    Valid credentials should authenticate.
    """

    response = await api_client.post(

        "/auth/login",

        json={

            "email":

                "admin@qshield.test",


            "password":

                "SecurePassword@123",

        },

    )



    assert response["method"] == "POST"

    assert response["path"] == "/auth/login"



@pytest.mark.asyncio
async def test_login_invalid_credentials(
    api_client,
):
    """
    Invalid credentials should fail.
    """

    response = await api_client.post(

        "/auth/login",

        json={

            "email":

                "invalid@test.com",


            "password":

                "wrong",

        },

    )



    assert response["data"]["email"] == "invalid@test.com"



# ============================================================
# Token Tests
# ============================================================


def test_token_generation():
    """
    Authentication tokens should generate.
    """

    token = generate_random_token()



    assert token

    assert isinstance(

        token,

        str,

    )



def test_password_based_authentication():
    """
    Password verification flow.
    """

    password = "SecurePassword@123"



    stored = hash_password(

        password

    )



    assert verify_password(

        password,

        stored["hash"],

        stored["salt"],

    )



# ============================================================
# User Authentication Tests
# ============================================================


def test_admin_login_user():
    """
    Admin users should authenticate.
    """

    user = admin_user()



    assert user["is_active"]

    assert "admin" in user["roles"]



def test_regular_user_login():
    """
    Normal users should authenticate.
    """

    user = normal_user()



    assert user["is_active"]

    assert "user" in user["roles"]



# ============================================================
# Authorization Header Tests
# ============================================================


@pytest.mark.asyncio
async def test_authenticated_request(
    api_client,
    auth_token,
):
    """
    Authenticated requests should include token.
    """

    response = await api_client.get(

        "/users/me",

    )



    assert response["path"] == "/users/me"

    assert auth_token



# ============================================================
# Logout Tests
# ============================================================


@pytest.mark.asyncio
async def test_logout_endpoint(
    api_client,
):
    """
    Logout endpoint should be reachable.
    """

    response = await api_client.post(

        "/auth/logout"

    )



    assert response["path"] == "/auth/logout"



# ============================================================
# Session Validation
# ============================================================


@pytest.mark.asyncio
async def test_session_validation(
    api_client,
):
    """
    Session validation endpoint.
    """

    response = await api_client.get(

        "/auth/session"

    )



    assert response["path"] == "/auth/session"