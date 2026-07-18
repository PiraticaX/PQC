"""
QShield Enterprise
==================

Authentication Unit Tests.

Tests:

- User authentication
- Password verification
- Token validation
- Permission checks
- Role authorization
- Session handling

"""

from __future__ import annotations



import pytest



from backend.utils.hashing import (
    hash_password,
    verify_password,
)



from backend.utils.validators import (
    validate_password,
)



from backend.utils.ids import (
    generate_user_id,
)



# ============================================================
# Password Tests
# ============================================================


def test_password_hash_generation():
    """
    Password hashing should generate
    secure hash and salt.
    """

    password = "SecurePassword@123"



    result = hash_password(

        password

    )



    assert "hash" in result

    assert "salt" in result

    assert result["hash"] != password



def test_password_verification_success():
    """
    Valid password should verify.
    """

    password = "SecurePassword@123"



    result = hash_password(

        password

    )



    verified = verify_password(

        password,

        result["hash"],

        result["salt"],

    )



    assert verified is True



def test_password_verification_failure():
    """
    Invalid password should fail.
    """

    result = hash_password(

        "SecurePassword@123"

    )



    verified = verify_password(

        "WrongPassword@123",

        result["hash"],

        result["salt"],

    )



    assert verified is False



# ============================================================
# Password Policy Tests
# ============================================================


def test_password_policy_accepts_secure_password():
    """
    Strong passwords should pass.
    """

    assert validate_password(

        "SecurePassword@123"

    )



def test_password_policy_rejects_weak_password():
    """
    Weak passwords should fail.
    """

    assert not validate_password(

        "password"

    )



# ============================================================
# User Identity Tests
# ============================================================


def test_user_id_generation():
    """
    User IDs should generate correctly.
    """

    user_id = generate_user_id()



    assert user_id.startswith(

        "usr_"

    )



def test_user_fixture_has_required_fields(
    test_user,
):
    """
    User fixture validation.
    """

    assert test_user["id"]

    assert test_user["email"]

    assert test_user["roles"]

    assert test_user["permissions"]



# ============================================================
# Authorization Tests
# ============================================================


def test_admin_has_admin_role():
    """
    Admin users should contain admin role.
    """

    from backend.tests.fixtures.users import admin_user



    user = admin_user()



    assert "admin" in user["roles"]



def test_regular_user_has_no_admin_access():
    """
    Normal users should not have admin privileges.
    """

    from backend.tests.fixtures.users import normal_user



    user = normal_user()



    assert "admin" not in user["roles"]



# ============================================================
# Session Tests
# ============================================================


def test_auth_token_fixture(
    auth_token,
):
    """
    Authentication token fixture exists.
    """

    assert auth_token

    assert isinstance(

        auth_token,

        str,

    )