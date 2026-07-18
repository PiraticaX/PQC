"""
QShield Enterprise
==================

Encryption Utilities.

Provides:

- Symmetric encryption
- AES-GCM encryption
- Secure payload protection
- Key handling
- Encryption/decryption helpers

Used across:

- Secrets
- Database fields
- API payloads
- Backup artifacts
- Sensitive information

"""

from __future__ import annotations


import base64


import os



from typing import Any



# ============================================================
# Optional Cryptography Import
# ============================================================


try:

    from cryptography.hazmat.primitives.ciphers.aead import (

        AESGCM,

    )


    CRYPTOGRAPHY_AVAILABLE = True



except ImportError:

    CRYPTOGRAPHY_AVAILABLE = False



# ============================================================
# Constants
# ============================================================


AES_KEY_SIZE = 32


NONCE_SIZE = 12



# ============================================================
# Key Generation
# ============================================================


def generate_encryption_key() -> str:
    """
    Generate AES-256 key.

    Returns:

        Base64 encoded key

    """

    key = os.urandom(

        AES_KEY_SIZE

    )


    return base64.b64encode(

        key

    ).decode(

        "utf-8"

    )



def decode_key(
    key: str,
) -> bytes:
    """
    Decode base64 encryption key.

    """

    return base64.b64decode(

        key.encode(

            "utf-8"

        )

    )



# ============================================================
# Encryption
# ============================================================


def encrypt(
    plaintext: str | bytes,
    key: str,
    associated_data: bytes | None = None,
) -> dict[str, str]:
    """
    Encrypt data using AES-256-GCM.

    Returns:

    {
        ciphertext,
        nonce
    }

    """

    if isinstance(

        plaintext,

        str,

    ):

        plaintext = plaintext.encode(

            "utf-8"

        )



    if not CRYPTOGRAPHY_AVAILABLE:

        raise RuntimeError(

            "Cryptography package unavailable"

        )



    aes = AESGCM(

        decode_key(

            key

        )

    )



    nonce = os.urandom(

        NONCE_SIZE

    )



    encrypted = aes.encrypt(

        nonce,

        plaintext,

        associated_data,

    )



    return {

        "ciphertext":

            base64.b64encode(

                encrypted

            ).decode(

                "utf-8"

            ),


        "nonce":

            base64.b64encode(

                nonce

            ).decode(

                "utf-8"

            ),

    }



# ============================================================
# Decryption
# ============================================================


def decrypt(
    ciphertext: str,
    nonce: str,
    key: str,
    associated_data: bytes | None = None,
) -> bytes:
    """
    Decrypt AES-GCM encrypted data.

    """

    if not CRYPTOGRAPHY_AVAILABLE:

        raise RuntimeError(

            "Cryptography package unavailable"

        )



    aes = AESGCM(

        decode_key(

            key

        )

    )



    encrypted = base64.b64decode(

        ciphertext.encode(

            "utf-8"

        )

    )



    nonce_bytes = base64.b64decode(

        nonce.encode(

            "utf-8"

        )

    )



    return aes.decrypt(

        nonce_bytes,

        encrypted,

        associated_data,

    )



def decrypt_string(
    ciphertext: str,
    nonce: str,
    key: str,
    associated_data: bytes | None = None,
) -> str:
    """
    Decrypt and return string.

    """

    return decrypt(

        ciphertext,

        nonce,

        key,

        associated_data,

    ).decode(

        "utf-8"

    )



# ============================================================
# JSON Encryption
# ============================================================


def encrypt_json(
    data: dict[str, Any],
    key: str,
) -> dict[str, str]:
    """
    Encrypt JSON object.

    """

    import json



    payload = json.dumps(

        data,

        sort_keys=True,

    )



    return encrypt(

        payload,

        key,

    )



def decrypt_json(
    encrypted_data: dict[str, str],
    key: str,
) -> dict[str, Any]:
    """
    Decrypt JSON object.

    """

    import json



    plaintext = decrypt_string(

        encrypted_data["ciphertext"],

        encrypted_data["nonce"],

        key,

    )



    return json.loads(

        plaintext

    )



# ============================================================
# Masking Helpers
# ============================================================


def mask_secret(
    value: str,
    visible_chars: int = 4,
) -> str:
    """
    Mask sensitive values.

    Example:

    abcd********1234

    """

    if len(value) <= visible_chars:

        return "*" * len(value)



    return (

        value[:visible_chars]

        +

        "*" *

        (

            len(value)

            -

            visible_chars

        )

    )