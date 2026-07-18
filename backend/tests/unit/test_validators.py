"""
QShield Enterprise
==================

Validator Unit Tests.

Tests:

- Email validation
- Username validation
- Password validation
- UUID validation
- API key validation
- File validation
- Input sanitization
- Required field validation
- IP validation

"""

from __future__ import annotations



from pathlib import Path



import pytest



from backend.utils.validators import (
    is_empty,
    validate_length,
    validate_email,
    validate_username,
    validate_password,
    validate_uuid,
    validate_api_key,
    validate_file_extension,
    validate_file_size,
    sanitize_string,
    validate_required_fields,
    validate_ip_address,
)



# ============================================================
# Empty Validation Tests
# ============================================================


def test_empty_none_value():
    """
    None should be considered empty.
    """

    assert is_empty(None)



def test_empty_string_value():
    """
    Blank string should be empty.
    """

    assert is_empty("   ")



def test_non_empty_value():
    """
    Valid value should not be empty.
    """

    assert not is_empty(

        "qshield"

    )



# ============================================================
# String Validation Tests
# ============================================================


def test_string_length_validation():
    """
    Length rules should work.
    """

    assert validate_length(

        "security",

        minimum=3,

        maximum=20,

    )



def test_string_length_failure():
    """
    Invalid length should fail.
    """

    assert not validate_length(

        "a",

        minimum=3,

    )



# ============================================================
# Email Validation
# ============================================================


def test_valid_email():
    """
    Valid emails should pass.
    """

    assert validate_email(

        "admin@qshield.test"

    )



def test_invalid_email():
    """
    Invalid emails should fail.
    """

    assert not validate_email(

        "invalid-email"

    )



# ============================================================
# Username Validation
# ============================================================


def test_valid_username():
    """
    Username format validation.
    """

    assert validate_username(

        "security_admin"

    )



def test_invalid_username():
    """
    Invalid username format.
    """

    assert not validate_username(

        "a"

    )



# ============================================================
# Password Validation
# ============================================================


def test_secure_password():
    """
    Strong password should pass.
    """

    assert validate_password(

        "SecurePassword@123"

    )



def test_weak_password():
    """
    Weak password should fail.
    """

    assert not validate_password(

        "password"

    )



# ============================================================
# UUID Validation
# ============================================================


def test_valid_uuid():
    """
    UUID should validate.
    """

    assert validate_uuid(

        "550e8400-e29b-41d4-a716-446655440000"

    )



def test_invalid_uuid():
    """
    Invalid UUID should fail.
    """

    assert not validate_uuid(

        "not-a-uuid"

    )



# ============================================================
# API Key Validation
# ============================================================


def test_valid_api_key():
    """
    Valid QShield API keys should pass.
    """

    key = (

        "qsk_"

        +

        "A" * 32

    )



    assert validate_api_key(

        key

    )



def test_invalid_api_key():
    """
    Invalid API key should fail.
    """

    assert not validate_api_key(

        "random-key"

    )



# ============================================================
# File Validation
# ============================================================


def test_valid_file_extension():
    """
    Allowed extensions should pass.
    """

    assert validate_file_extension(

        "report.pdf",

        [

            ".pdf",

            ".txt",

        ],

    )



def test_invalid_file_extension():
    """
    Unsupported extension should fail.
    """

    assert not validate_file_extension(

        "malware.exe",

        [

            ".pdf",

            ".txt",

        ],

    )



def test_valid_file_size():
    """
    File size should validate.
    """

    assert validate_file_size(

        1024,

        2048,

    )



def test_large_file_size_failure():
    """
    Oversized files should fail.
    """

    assert not validate_file_size(

        5000,

        1000,

    )



# ============================================================
# Sanitization Tests
# ============================================================


def test_string_sanitization():
    """
    Dangerous characters should remove.
    """

    result = sanitize_string(

        "<script>test</script>"

    )



    assert "<" not in result

    assert ">" not in result



# ============================================================
# Required Fields Tests
# ============================================================


def test_required_fields_success():
    """
    Required fields should validate.
    """

    valid, missing = validate_required_fields(

        {

            "name":

                "QShield",

            "email":

                "admin@qshield.test",

        },

        [

            "name",

            "email",

        ],

    )



    assert valid

    assert missing == []



def test_required_fields_failure():
    """
    Missing fields should return.
    """

    valid, missing = validate_required_fields(

        {

            "name":

                "QShield",

        },

        [

            "name",

            "email",

        ],

    )



    assert not valid

    assert "email" in missing



# ============================================================
# IP Validation Tests
# ============================================================


def test_valid_ip_address():
    """
    Valid IP should pass.
    """

    assert validate_ip_address(

        "192.168.1.1"

    )



def test_invalid_ip_address():
    """
    Invalid IP should fail.
    """

    assert not validate_ip_address(

        "300.300.300.300"

    )