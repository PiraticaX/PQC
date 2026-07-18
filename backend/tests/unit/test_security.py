"""
QShield Enterprise
==================

Security Unit Tests.

Tests:

- Security exceptions
- Permission validation
- API key validation
- Security event validation
- Risk scoring
- Audit security controls

"""

from __future__ import annotations



import pytest



from backend.utils.exceptions import (
    SecurityError,
    EncryptionError,
    PermissionDeniedError,
)



from backend.utils.validators import (
    validate_api_key,
    validate_uuid,
    validate_ip_address,
)



from backend.utils.crypto import (
    generate_api_secret,
    verify_hmac,
    generate_hmac,
)



from backend.tests.fixtures.security_events import (
    critical_security_alert,
    audit_event,
)



# ============================================================
# Exception Tests
# ============================================================


def test_security_exception_creation():
    """
    Security exception should initialize correctly.
    """

    error = SecurityError(

        "Security violation",

        code="SEC001",

    )



    response = error.to_dict()



    assert response["message"] == "Security violation"

    assert response["code"] == "SEC001"



def test_encryption_error_is_security_error():
    """
    Encryption errors inherit security errors.
    """

    error = EncryptionError(

        "Encryption failed"

    )



    assert isinstance(

        error,

        SecurityError,

    )



def test_permission_error_is_security_related():
    """
    Permission errors should be raised
    for access violations.
    """

    error = PermissionDeniedError(

        "Access denied"

    )



    assert "Access denied" in str(

        error

    )



# ============================================================
# API Key Tests
# ============================================================


def test_api_secret_generation():
    """
    API secret generation should work.
    """

    secret = generate_api_secret()



    assert "secret" in secret

    assert "fingerprint" in secret

    assert len(

        secret["secret"]

    ) > 10



def test_invalid_api_key_format():
    """
    Invalid API keys should fail.
    """

    assert not validate_api_key(

        "invalid_key"

    )



# ============================================================
# HMAC Security Tests
# ============================================================


def test_hmac_signature_generation():
    """
    HMAC signatures should verify.
    """

    payload = "security-event"



    secret = "test-secret"



    signature = generate_hmac(

        payload,

        secret,

    )



    assert verify_hmac(

        payload,

        signature,

        secret,

    )



def test_hmac_invalid_signature():
    """
    Modified signature should fail.
    """

    assert not verify_hmac(

        "payload",

        "wrong-signature",

        "secret",

    )



# ============================================================
# Security Event Tests
# ============================================================


def test_critical_security_event():
    """
    Critical alerts should contain required fields.
    """

    event = critical_security_alert()



    assert event["severity"] == "critical"

    assert event["status"] == "open"

    assert event["risk_score"] > 90



def test_audit_event_structure():
    """
    Audit events should contain tracking information.
    """

    event = audit_event()



    assert event["type"] == "audit.activity"

    assert event["user"]

    assert event["action"]



# ============================================================
# Validation Security Tests
# ============================================================


def test_uuid_validation():
    """
    UUID validation should work.
    """

    assert validate_uuid(

        "550e8400-e29b-41d4-a716-446655440000"

    )



def test_invalid_uuid_validation():
    """
    Invalid UUID should fail.
    """

    assert not validate_uuid(

        "invalid"

    )



def test_ip_validation():
    """
    IP validation should work.
    """

    assert validate_ip_address(

        "192.168.1.1"

    )



def test_invalid_ip_validation():
    """
    Invalid IP should fail.
    """

    assert not validate_ip_address(

        "999.999.999.999"

    )