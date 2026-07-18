"""
QShield Enterprise
==================

Encryption Infrastructure.

Responsibilities:

- Symmetric encryption
- Data decryption
- Hashing utilities
- Secure token generation
- Field-level encryption
- Sensitive data masking
- Cryptographic helpers

Supports:

- AES-256 Fernet encryption
- SHA hashing
- PQC-ready abstraction layer

"""

from __future__ import annotations


import base64


import hashlib


import secrets


from typing import Any



from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken



from app.core.config import settings


from app.core.exceptions import EncryptionException



# ============================================================
# Key Management
# ============================================================


def generate_encryption_key() -> str:
    """
    Generate new encryption key.

    Returns:

        Base64 encoded AES key

    """

    return Fernet.generate_key().decode()



def load_encryption_key() -> bytes:
    """
    Load application encryption key.

    """

    if not settings.ENCRYPTION_KEY:

        raise EncryptionException(

            "Encryption key is not configured."

        )


    return settings.ENCRYPTION_KEY.encode()



# ============================================================
# Encryption Engine
# ============================================================


def encrypt(
    plaintext: str,
) -> str:
    """
    Encrypt plaintext.

    Uses:

    AES-256 Fernet

    """

    try:

        cipher = Fernet(

            load_encryption_key()

        )


        encrypted = cipher.encrypt(

            plaintext.encode()

        )


        return encrypted.decode()



    except Exception as exc:

        raise EncryptionException(

            str(exc)

        )



def decrypt(
    ciphertext: str,
) -> str:
    """
    Decrypt ciphertext.
    """

    try:

        cipher = Fernet(

            load_encryption_key()

        )


        decrypted = cipher.decrypt(

            ciphertext.encode()

        )


        return decrypted.decode()



    except InvalidToken:

        raise EncryptionException(

            "Invalid encrypted payload."

        )


    except Exception as exc:

        raise EncryptionException(

            str(exc)

        )



# ============================================================
# Data Encryption Helpers
# ============================================================


def encrypt_field(
    value: Any,
) -> str:
    """
    Encrypt database field.

    Used for:

    - Personal data
    - Secrets
    - Tokens
    """

    return encrypt(

        str(value)

    )



def decrypt_field(
    value: str,
) -> str:
    """
    Decrypt database field.
    """

    return decrypt(

        value

    )



# ============================================================
# Hashing Utilities
# ============================================================


def hash_sha256(
    value: str,
) -> str:
    """
    SHA-256 hash.
    """

    return hashlib.sha256(

        value.encode()

    ).hexdigest()



def hash_sha512(
    value: str,
) -> str:
    """
    SHA-512 hash.
    """

    return hashlib.sha512(

        value.encode()

    ).hexdigest()



def secure_hash(
    value: str,
    algorithm: str = "sha256",
) -> str:
    """
    Generic hashing interface.

    """

    if algorithm.lower() == "sha256":

        return hash_sha256(

            value

        )


    if algorithm.lower() == "sha512":

        return hash_sha512(

            value

        )


    raise ValueError(

        "Unsupported hash algorithm."

    )



# ============================================================
# Secure Random Generation
# ============================================================


def generate_secure_random(
    length: int = 32,
) -> str:
    """
    Generate cryptographically secure random bytes.

    """

    return secrets.token_urlsafe(

        length

    )



def generate_salt(
    length: int = 16,
) -> str:
    """
    Generate cryptographic salt.
    """

    return base64.urlsafe_b64encode(

        secrets.token_bytes(

            length

        )

    ).decode()



# ============================================================
# Data Masking
# ============================================================


def mask_sensitive_data(
    value: str,
    visible_chars: int = 4,
) -> str:
    """
    Mask sensitive information.

    Example:

        abcdef123456

        ****3456

    """

    if len(value) <= visible_chars:

        return "*" * len(value)



    masked_length = (

        len(value)

        -

        visible_chars

    )


    return (

        "*" * masked_length

        +

        value[-visible_chars:]

    )



# ============================================================
# Certificate / Key Utilities
# ============================================================


def encode_base64(
    data: bytes,
) -> str:
    """
    Encode bytes to base64.
    """

    return base64.b64encode(

        data

    ).decode()



def decode_base64(
    data: str,
) -> bytes:
    """
    Decode base64.
    """

    return base64.b64decode(

        data.encode()

    )



# ============================================================
# PQC Crypto Abstraction
# ============================================================


class CryptoProvider:
    """
    Unified cryptographic provider.

    Future compatible with:

    - Classical cryptography
    - Post Quantum Cryptography

    """

    def encrypt(
        self,
        data: str,
    ) -> str:

        return encrypt(

            data

        )



    def decrypt(
        self,
        data: str,
    ) -> str:

        return decrypt(

            data

        )



    def hash(
        self,
        data: str,
    ) -> str:

        return hash_sha256(

            data

        )



crypto_provider = CryptoProvider()