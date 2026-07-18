"""
QShield Enterprise
==================

Encryption Unit Tests.

Tests:

- Key generation
- AES encryption/decryption
- JSON encryption
- Data confidentiality
- Secret masking
- Invalid encryption scenarios

"""

from __future__ import annotations



import pytest



from backend.utils.encryption import (
    generate_encryption_key,
    encrypt,
    decrypt,
    decrypt_string,
    encrypt_json,
    decrypt_json,
    mask_secret,
)



# ============================================================
# Key Generation Tests
# ============================================================


def test_encryption_key_generation():
    """
    Encryption key should be generated.
    """

    key = generate_encryption_key()



    assert key

    assert isinstance(

        key,

        str,

    )



# ============================================================
# AES Encryption Tests
# ============================================================


def test_encrypt_and_decrypt_string():
    """
    Encrypted data should decrypt correctly.
    """

    key = generate_encryption_key()



    message = "QShield confidential data"



    encrypted = encrypt(

        message,

        key,

    )



    assert "ciphertext" in encrypted

    assert "nonce" in encrypted



    decrypted = decrypt_string(

        encrypted["ciphertext"],

        encrypted["nonce"],

        key,

    )



    assert decrypted == message



def test_encrypted_value_is_not_plaintext():
    """
    Ciphertext should not expose original data.
    """

    key = generate_encryption_key()



    message = "Sensitive Information"



    encrypted = encrypt(

        message,

        key,

    )



    assert message not in encrypted["ciphertext"]



# ============================================================
# Binary Encryption Tests
# ============================================================


def test_encrypt_bytes():
    """
    Binary payload encryption.
    """

    key = generate_encryption_key()



    payload = b"binary-security-data"



    encrypted = encrypt(

        payload,

        key,

    )



    decrypted = decrypt(

        encrypted["ciphertext"],

        encrypted["nonce"],

        key,

    )



    assert decrypted == payload



# ============================================================
# JSON Encryption Tests
# ============================================================


def test_json_encryption():
    """
    JSON objects should encrypt/decrypt.
    """

    key = generate_encryption_key()



    payload = {

        "user":

            "admin",


        "role":

            "security",

    }



    encrypted = encrypt_json(

        payload,

        key,

    )



    decrypted = decrypt_json(

        encrypted,

        key,

    )



    assert decrypted == payload



# ============================================================
# Secret Protection Tests
# ============================================================


def test_secret_masking():
    """
    Sensitive values should be masked.
    """

    secret = "abcdefghijklmnopqrstuvwxyz"



    masked = mask_secret(

        secret

    )



    assert masked.startswith(

        "abcd"

    )



    assert "*" in masked



# ============================================================
# Failure Scenarios
# ============================================================


def test_wrong_key_fails_decryption():
    """
    Incorrect key should fail.
    """

    key = generate_encryption_key()

    wrong_key = generate_encryption_key()



    encrypted = encrypt(

        "protected",

        key,

    )



    with pytest.raises(

        Exception

    ):

        decrypt_string(

            encrypted["ciphertext"],

            encrypted["nonce"],

            wrong_key,

        )



def test_empty_secret_masking():
    """
    Empty values should be handled.
    """

    assert mask_secret(

        ""

    ) == ""