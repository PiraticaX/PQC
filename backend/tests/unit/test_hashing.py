"""
QShield Enterprise
==================

Hashing Unit Tests.

Tests:

- Data hashing
- Password hashing
- Salt generation
- Hash verification
- File integrity checks
- Fingerprinting

"""

from __future__ import annotations



import tempfile



from pathlib import Path



import pytest



from backend.utils.hashing import (
    hash_data,
    hash_json,
    hash_password,
    verify_password,
    generate_salt,
    hash_file,
    verify_file_hash,
    fingerprint,
    hash_token,
)



# ============================================================
# Generic Hash Tests
# ============================================================


def test_sha256_hash_generation():
    """
    SHA256 hash should generate.
    """

    result = hash_data(

        "QShield"

    )



    assert result

    assert len(result) == 64



def test_same_input_same_hash():
    """
    Same input should produce
    same digest.
    """

    first = hash_data(

        "security-data"

    )



    second = hash_data(

        "security-data"

    )



    assert first == second



def test_different_input_different_hash():
    """
    Different input should produce
    different digest.
    """

    first = hash_data(

        "data-one"

    )



    second = hash_data(

        "data-two"

    )



    assert first != second



# ============================================================
# JSON Hash Tests
# ============================================================


def test_json_hash_generation():
    """
    JSON objects should hash consistently.
    """

    payload = {

        "user":

            "admin",


        "role":

            "security",

    }



    result = hash_json(

        payload

    )



    assert result

    assert len(result) == 64



# ============================================================
# Password Hash Tests
# ============================================================


def test_password_hash_contains_required_fields():
    """
    Password hashing should return metadata.
    """

    result = hash_password(

        "SecurePassword@123"

    )



    assert "hash" in result

    assert "salt" in result

    assert "algorithm" in result



def test_password_hash_verification():
    """
    Correct password should verify.
    """

    password = "SecurePassword@123"



    result = hash_password(

        password

    )



    assert verify_password(

        password,

        result["hash"],

        result["salt"],

    )



def test_wrong_password_fails():
    """
    Incorrect password should fail.
    """

    result = hash_password(

        "SecurePassword@123"

    )



    assert not verify_password(

        "WrongPassword@123",

        result["hash"],

        result["salt"],

    )



# ============================================================
# Salt Tests
# ============================================================


def test_salt_generation():
    """
    Salt values should be unique.
    """

    first = generate_salt()



    second = generate_salt()



    assert first != second



# ============================================================
# File Integrity Tests
# ============================================================


def test_file_hash_generation():
    """
    File checksum should generate.
    """

    with tempfile.NamedTemporaryFile(

        mode="w",

        delete=False,

    ) as file:

        file.write(

            "QShield integrity test"

        )


        filepath = file.name



    checksum = hash_file(

        filepath

    )



    assert checksum

    assert len(checksum) == 64



def test_file_hash_verification():
    """
    File checksum should verify.
    """

    with tempfile.NamedTemporaryFile(

        mode="w",

        delete=False,

    ) as file:

        file.write(

            "Immutable security file"

        )


        filepath = file.name



    checksum = hash_file(

        filepath

    )



    assert verify_file_hash(

        filepath,

        checksum,

    )



# ============================================================
# Fingerprint Tests
# ============================================================


def test_fingerprint_generation():
    """
    Fingerprint should create short identifier.
    """

    result = fingerprint(

        "api-secret"

    )



    assert len(result) == 16



def test_token_hashing():
    """
    Authentication tokens should hash.
    """

    token_hash = hash_token(

        "test.jwt.token"

    )



    assert token_hash

    assert token_hash != "test.jwt.token"