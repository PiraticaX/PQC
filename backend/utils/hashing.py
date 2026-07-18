"""
QShield Enterprise
==================

Hashing Utilities.

Provides:

- Secure hashing
- Password hashing
- Hash verification
- Integrity checks
- Digital fingerprints

Used across:

- Authentication
- API keys
- Audit logs
- File integrity
- Security workflows

"""

from __future__ import annotations


import hashlib


import hmac


import secrets



from typing import Any



# ============================================================
# Hash Algorithms
# ============================================================


DEFAULT_HASH_ALGORITHM = "sha256"



SUPPORTED_HASH_ALGORITHMS = {

    "sha256":

        hashlib.sha256,


    "sha384":

        hashlib.sha384,


    "sha512":

        hashlib.sha512,

}



# ============================================================
# Generic Hashing
# ============================================================


def hash_data(
    data: str | bytes,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Generate cryptographic hash.

    """

    if algorithm not in SUPPORTED_HASH_ALGORITHMS:

        raise ValueError(

            f"Unsupported hash algorithm: {algorithm}"

        )



    if isinstance(

        data,

        str,

    ):

        data = data.encode(

            "utf-8"

        )



    hasher = SUPPORTED_HASH_ALGORITHMS[algorithm]()


    hasher.update(

        data

    )



    return hasher.hexdigest()



def hash_json(
    data: dict[str, Any],
) -> str:
    """
    Hash JSON-compatible data.

    """

    import json


    serialized = json.dumps(

        data,

        sort_keys=True,

    )


    return hash_data(

        serialized

    )



# ============================================================
# Password Hashing
# ============================================================


def generate_salt(
    length: int = 32,
) -> str:
    """
    Generate secure random salt.

    """

    return secrets.token_hex(

        length

    )



def hash_password(
    password: str,
    salt: str | None = None,
) -> dict[str, str]:
    """
    Hash password securely.

    Uses PBKDF2-HMAC.

    """

    salt = salt or generate_salt()



    derived = hashlib.pbkdf2_hmac(

        "sha256",

        password.encode(

            "utf-8"

        ),

        salt.encode(

            "utf-8"

        ),

        310000,

    )



    return {

        "hash":

            derived.hex(),


        "salt":

            salt,


        "algorithm":

            "PBKDF2-SHA256",

    }



def verify_password(
    password: str,
    stored_hash: str,
    salt: str,
) -> bool:
    """
    Verify password hash.

    """

    result = hash_password(

        password,

        salt,

    )



    return hmac.compare_digest(

        result["hash"],

        stored_hash,

    )



# ============================================================
# Integrity Hashing
# ============================================================


def hash_file(
    filepath: str,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> str:
    """
    Generate file checksum.

    """

    if algorithm not in SUPPORTED_HASH_ALGORITHMS:

        raise ValueError(

            "Unsupported algorithm"

        )



    hasher = SUPPORTED_HASH_ALGORITHMS[algorithm]()



    with open(

        filepath,

        "rb",

    ) as file:


        while chunk := file.read(

            8192

        ):

            hasher.update(

                chunk

            )



    return hasher.hexdigest()



def verify_file_hash(
    filepath: str,
    expected_hash: str,
    algorithm: str = DEFAULT_HASH_ALGORITHM,
) -> bool:
    """
    Verify file integrity.

    """

    actual = hash_file(

        filepath,

        algorithm,

    )


    return hmac.compare_digest(

        actual,

        expected_hash,

    )



# ============================================================
# Identifier Hashing
# ============================================================


def fingerprint(
    value: str,
) -> str:
    """
    Create short fingerprint.

    Useful for:

    - API keys
    - Assets
    - Certificates

    """

    return hash_data(

        value

    )[:16]



def hash_token(
    token: str,
) -> str:
    """
    Hash authentication token.

    """

    return hash_data(

        token

    )