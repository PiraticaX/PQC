"""
QShield Enterprise
==================

Security Infrastructure.

Responsibilities:

- Password hashing
- Password verification
- JWT token generation
- JWT token validation
- API key hashing
- Security utility functions
- Authentication primitives

Technology:

- JWT
- Passlib
- Cryptographic hashing

"""

from __future__ import annotations


import hashlib


import secrets


from datetime import datetime
from datetime import timedelta
from datetime import timezone


from typing import Any



from jose import JWTError
from jose import jwt



from passlib.context import CryptContext



from app.core.config import settings


from app.core.exceptions import AuthenticationException
from app.core.exceptions import InvalidTokenException



# ============================================================
# Password Hashing
# ============================================================


password_context = CryptContext(

    schemes=[

        "bcrypt"

    ],

    deprecated="auto",

)



def hash_password(
    password: str
) -> str:
    """
    Hash user password.

    Uses:

    - bcrypt

    """

    return password_context.hash(

        password

    )



def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify password against hash.
    """

    return password_context.verify(

        plain_password,

        hashed_password,

    )



# ============================================================
# JWT Token Handling
# ============================================================


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Generate JWT access token.
    """

    now = datetime.now(

        timezone.utc

    )


    expire = (

        now + expires_delta

        if expires_delta

        else now +

        timedelta(

            minutes=

            settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

        )

    )


    payload = {

        "sub":

            subject,


        "iat":

            now,


        "exp":

            expire,


        "type":

            "access",

    }



    if extra_claims:

        payload.update(

            extra_claims

        )



    return jwt.encode(

        payload,

        settings.JWT_SECRET_KEY,

        algorithm=settings.JWT_ALGORITHM,

    )



def create_refresh_token(
    subject: str,
) -> str:
    """
    Generate refresh token.
    """

    return create_access_token(

        subject=subject,

        expires_delta=timedelta(

            days=

            settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

        ),

        extra_claims={

            "type":

                "refresh"

        }

    )



def decode_token(
    token: str,
) -> dict[str, Any]:
    """
    Decode and validate JWT token.
    """

    try:

        return jwt.decode(

            token,

            settings.JWT_SECRET_KEY,

            algorithms=[

                settings.JWT_ALGORITHM

            ],

        )


    except JWTError:

        raise InvalidTokenException()



def validate_access_token(
    token: str,
) -> dict[str, Any]:
    """
    Validate access token.
    """

    payload = decode_token(

        token

    )


    if payload.get(

        "type"

    ) != "access":

        raise AuthenticationException(

            "Invalid access token."

        )


    return payload



# ============================================================
# API Key Utilities
# ============================================================


def generate_api_key() -> str:
    """
    Generate secure API key.

    Format:

    qsk_<random>

    """

    random_value = secrets.token_urlsafe(

        48

    )


    return f"qsk_{random_value}"



def hash_api_key(
    api_key: str,
) -> str:
    """
    Hash API key.

    """

    return hashlib.sha256(

        api_key.encode()

    ).hexdigest()



def verify_api_key(
    api_key: str,
    hashed_key: str,
) -> bool:
    """
    Verify API key.
    """

    return hash_api_key(

        api_key

    ) == hashed_key



# ============================================================
# Secure Random Utilities
# ============================================================


def generate_secure_token(
    length: int = 32,
) -> str:
    """
    Generate cryptographically secure token.
    """

    return secrets.token_hex(

        length

    )



def generate_secret_key(
    length: int = 64,
) -> str:
    """
    Generate random secret.
    """

    return secrets.token_urlsafe(

        length

    )



# ============================================================
# Security Headers
# ============================================================


def security_headers() -> dict[str, str]:
    """
    Recommended HTTP security headers.
    """

    return {

        "X-Content-Type-Options":

            "nosniff",


        "X-Frame-Options":

            "DENY",


        "X-XSS-Protection":

            "1; mode=block",


        "Strict-Transport-Security":

            "max-age=31536000",

    }



# ============================================================
# Password Policy
# ============================================================


def validate_password_strength(
    password: str,
) -> bool:
    """
    Validate password policy.

    Requirements:

    - Minimum length
    - Uppercase
    - Lowercase
    - Digit
    - Special character

    """

    if len(password) < settings.PASSWORD_MIN_LENGTH:

        return False



    has_upper = any(

        c.isupper()

        for c in password

    )


    has_lower = any(

        c.islower()

        for c in password

    )


    has_digit = any(

        c.isdigit()

        for c in password

    )


    has_special = any(

        not c.isalnum()

        for c in password

    )



    return (

        has_upper

        and

        has_lower

        and

        has_digit

        and

        has_special

    )