"""
QShield Enterprise
==================

Cryptographic Utilities.

Provides:

- Secure random generation
- HMAC signatures
- Secret generation
- Token generation
- Cryptographic helpers

Used across:

- Authentication
- API keys
- Webhooks
- Security events
- Integrations

"""

from __future__ import annotations


import hashlib


import hmac


import secrets


import base64



from typing import Any



# ============================================================
# Constants
# ============================================================


DEFAULT_TOKEN_LENGTH = 32


DEFAULT_SECRET_LENGTH = 64



# ============================================================
# Secure Random Generation
# ============================================================


def generate_random_bytes(
    length: int = 32,
) -> bytes:
    """
    Generate cryptographically secure bytes.

    """

    return secrets.token_bytes(

        length

    )



def generate_random_hex(
    length: int = 32,
) -> str:
    """
    Generate secure hexadecimal string.

    """

    return secrets.token_hex(

        length

    )



def generate_random_token(
    length: int = DEFAULT_TOKEN_LENGTH,
) -> str:
    """
    Generate secure URL-safe token.

    """

    return secrets.token_urlsafe(

        length

    )



def generate_secret(
    length: int = DEFAULT_SECRET_LENGTH,
) -> str:
    """
    Generate application secret.

    """

    return generate_random_token(

        length

    )



# ============================================================
# HMAC Operations
# ============================================================


def generate_hmac(
    data: str | bytes,
    secret: str | bytes,
    algorithm: str = "sha256",
) -> str:
    """
    Generate HMAC signature.

    """

    if isinstance(

        data,

        str,

    ):

        data = data.encode(

            "utf-8"

        )



    if isinstance(

        secret,

        str,

    ):

        secret = secret.encode(

            "utf-8"

        )



    digest = hmac.new(

        secret,

        data,

        getattr(

            hashlib,

            algorithm,

        ),

    )



    return digest.hexdigest()



def verify_hmac(
    data: str | bytes,
    signature: str,
    secret: str | bytes,
    algorithm: str = "sha256",
) -> bool:
    """
    Verify HMAC signature.

    """

    expected = generate_hmac(

        data,

        secret,

        algorithm,

    )


    return hmac.compare_digest(

        expected,

        signature,

    )



# ============================================================
# Fingerprinting
# ============================================================


def create_fingerprint(
    value: str,
) -> str:
    """
    Create SHA256 fingerprint.

    Used for:

    - Certificates
    - API keys
    - Assets

    """

    return hashlib.sha256(

        value.encode(

            "utf-8"

        )

    ).hexdigest()



def short_fingerprint(
    value: str,
    length: int = 16,
) -> str:
    """
    Generate shortened fingerprint.

    """

    return create_fingerprint(

        value

    )[:length]



# ============================================================
# Encoding Helpers
# ============================================================


def encode_base64(
    data: bytes,
) -> str:
    """
    Encode bytes to Base64.

    """

    return base64.b64encode(

        data

    ).decode(

        "utf-8"

    )



def decode_base64(
    value: str,
) -> bytes:
    """
    Decode Base64 string.

    """

    return base64.b64decode(

        value.encode(

            "utf-8"

        )

    )



# ============================================================
# Secure Comparison
# ============================================================


def secure_compare(
    first: str,
    second: str,
) -> bool:
    """
    Constant-time comparison.

    """

    return hmac.compare_digest(

        first,

        second,

    )



# ============================================================
# API Key Helpers
# ============================================================


def generate_api_secret() -> dict[str, str]:
    """
    Generate API secret pair.

    """

    secret = generate_secret()



    return {

        "secret":

            secret,


        "fingerprint":

            short_fingerprint(

                secret

            ),

    }



# ============================================================
# Security Payload Helpers
# ============================================================


def create_security_signature(
    payload: dict[str, Any],
    secret: str,
) -> str:
    """
    Create signature for payload.

    Used for:

    - Webhooks
    - Event validation

    """

    import json



    serialized = json.dumps(

        payload,

        sort_keys=True,

    )



    return generate_hmac(

        serialized,

        secret,

    )