"""
QShield Enterprise
==================

Validation Utilities.

Provides:

- Input validation
- Security validation
- Identity validation
- File validation
- API validation

Used across:

- API endpoints
- Schemas
- Services
- Authentication
- Integrations
"""

from __future__ import annotations


import re


from pathlib import Path


from uuid import UUID



from typing import Any



# ============================================================
# Regular Expressions
# ============================================================


EMAIL_PATTERN = re.compile(

    r"^[a-zA-Z0-9._%+-]+@"

    r"[a-zA-Z0-9.-]+\."

    r"[a-zA-Z]{2,}$"

)



USERNAME_PATTERN = re.compile(

    r"^[a-zA-Z0-9._-]{3,64}$"

)



API_KEY_PATTERN = re.compile(

    r"^qsk_[a-zA-Z0-9]{32,}$"

)



# ============================================================
# String Validation
# ============================================================


def is_empty(
    value: Any,
) -> bool:
    """
    Check empty value.

    """

    return (

        value is None

        or

        (

            isinstance(

                value,

                str,

            )

            and

            not value.strip()

        )

    )



def validate_length(
    value: str,
    minimum: int = 1,
    maximum: int = 255,
) -> bool:
    """
    Validate string length.

    """

    if not isinstance(

        value,

        str,

    ):

        return False



    return (

        minimum

        <=

        len(value)

        <=

        maximum

    )



# ============================================================
# Email Validation
# ============================================================


def validate_email(
    email: str,
) -> bool:
    """
    Validate email address.

    """

    if not email:

        return False



    return bool(

        EMAIL_PATTERN.match(

            email

        )

    )



# ============================================================
# Username Validation
# ============================================================


def validate_username(
    username: str,
) -> bool:
    """
    Validate username.

    """

    return bool(

        USERNAME_PATTERN.match(

            username

        )

    )



# ============================================================
# Password Validation
# ============================================================


def validate_password(
    password: str,
    minimum_length: int = 12,
) -> bool:
    """
    Validate password strength.

    Requirements:

    - Minimum length
    - Uppercase
    - Lowercase
    - Number
    - Special character

    """

    if not password:

        return False



    if len(password) < minimum_length:

        return False



    checks = [

        re.search(

            r"[A-Z]",

            password,

        ),

        re.search(

            r"[a-z]",

            password,

        ),

        re.search(

            r"\d",

            password,

        ),

        re.search(

            r"[!@#$%^&*(),.?\":{}|<>]",

            password,

        ),

    ]



    return all(

        checks

    )



# ============================================================
# UUID Validation
# ============================================================


def validate_uuid(
    value: str,
) -> bool:
    """
    Validate UUID format.

    """

    try:

        UUID(

            value

        )


        return True



    except (

        ValueError,

        TypeError,

    ):

        return False



# ============================================================
# API Key Validation
# ============================================================


def validate_api_key(
    key: str,
) -> bool:
    """
    Validate QShield API key format.

    """

    return bool(

        API_KEY_PATTERN.match(

            key

        )

    )



# ============================================================
# File Validation
# ============================================================


def validate_file_extension(
    filename: str,
    allowed_extensions: list[str],
) -> bool:
    """
    Validate file extension.

    """

    extension = Path(

        filename

    ).suffix.lower()



    return extension in [

        ext.lower()

        for ext in allowed_extensions

    ]



def validate_file_size(
    size_bytes: int,
    maximum_bytes: int,
) -> bool:
    """
    Validate file size.

    """

    return (

        0

        <

        size_bytes

        <=

        maximum_bytes

    )



# ============================================================
# Security Input Validation
# ============================================================


def sanitize_string(
    value: str,
) -> str:
    """
    Basic input sanitization.

    Removes:

    - HTML-like characters
    - Excess whitespace

    """

    if not value:

        return ""



    value = value.strip()



    dangerous = [

        "<",

        ">",

        "{",

        "}",

    ]



    for char in dangerous:

        value = value.replace(

            char,

            "",

        )



    return value



# ============================================================
# Dictionary Validation
# ============================================================


def validate_required_fields(
    data: dict[str, Any],
    fields: list[str],
) -> tuple[bool, list[str]]:
    """
    Validate required dictionary fields.

    """

    missing = [

        field

        for field in fields

        if field not in data

        or

        data[field] is None

    ]



    return (

        len(missing) == 0,

        missing,

    )



# ============================================================
# IP Validation
# ============================================================


def validate_ip_address(
    ip: str,
) -> bool:
    """
    Validate IPv4/IPv6 address.

    """

    import ipaddress


    try:

        ipaddress.ip_address(

            ip

        )


        return True



    except ValueError:

        return False