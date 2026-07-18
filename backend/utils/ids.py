"""
QShield Enterprise
==================

Identifier Utilities.

Provides:

- UUID generation
- Secure IDs
- Request tracking IDs
- Correlation IDs
- Entity identifiers

Used across:

- API requests
- Database records
- Workers
- Events
- Audit logs
- Distributed tracing

"""

from __future__ import annotations


import uuid


import secrets


import string



# ============================================================
# UUID Utilities
# ============================================================


def generate_uuid() -> str:
    """
    Generate standard UUID4.

    Returns:

        "8f4d7f8e-8d8e-4d89-a8f8..."

    """

    return str(

        uuid.uuid4()

    )



def generate_short_uuid(
    length: int = 12,
) -> str:
    """
    Generate shortened UUID.

    Useful for:

    - Display IDs
    - Reference numbers

    """

    value = (

        uuid.uuid4()

        .hex

    )


    return value[:length]



# ============================================================
# Secure Identifier Generation
# ============================================================


def generate_secure_id(
    length: int = 32,
) -> str:
    """
    Generate cryptographically secure ID.

    """

    alphabet = (

        string.ascii_letters

        +

        string.digits

    )


    return "".join(

        secrets.choice(

            alphabet

        )

        for _ in range(length)

    )



def generate_api_key_id() -> str:
    """
    Generate API key identifier.

    Format:

        qsk_xxxxxxxxxxxx

    """

    return (

        "qsk_"

        +

        generate_secure_id(

            32

        )

    )



# ============================================================
# Distributed Tracing IDs
# ============================================================


def generate_request_id() -> str:
    """
    Generate API request ID.
    """

    return (

        "req_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_correlation_id() -> str:
    """
    Generate distributed correlation ID.

    Used for:

    - Logs
    - Events
    - Worker jobs

    """

    return (

        "corr_"

        +

        generate_short_uuid(

            20

        )

    )



def generate_trace_id() -> str:
    """
    Generate tracing identifier.
    """

    return (

        "trace_"

        +

        generate_short_uuid(

            24

        )

    )



# ============================================================
# Entity IDs
# ============================================================


def generate_user_id() -> str:
    """
    Generate user ID.
    """

    return (

        "usr_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_organization_id() -> str:
    """
    Generate organization ID.
    """

    return (

        "org_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_asset_id() -> str:
    """
    Generate asset identifier.
    """

    return (

        "ast_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_scan_id() -> str:
    """
    Generate security scan ID.
    """

    return (

        "scan_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_report_id() -> str:
    """
    Generate report ID.
    """

    return (

        "rpt_"

        +

        generate_short_uuid(

            16

        )

    )



def generate_event_id() -> str:
    """
    Generate event identifier.
    """

    return (

        "evt_"

        +

        generate_short_uuid(

            20

        )

    )



# ============================================================
# Validation
# ============================================================


def is_valid_uuid(
    value: str,
) -> bool:
    """
    Validate UUID string.
    """

    try:

        uuid.UUID(

            value

        )


        return True



    except (

        ValueError,

        TypeError,

    ):

        return False



def extract_uuid(
    value: str,
) -> str | None:
    """
    Extract UUID from text.
    """

    try:

        return str(

            uuid.UUID(

                value

            )

        )



    except Exception:

        return None