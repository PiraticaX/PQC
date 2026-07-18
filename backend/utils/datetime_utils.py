"""
QShield Enterprise
==================

Date and Time Utilities.

Provides:

- UTC timestamp handling
- Timezone conversion
- Date formatting
- Expiry calculations
- Duration helpers

Used across:

- Authentication
- Audit logs
- Events
- Workers
- Reports
"""

from __future__ import annotations


from datetime import datetime
from datetime import timedelta
from datetime import timezone


from typing import Any



# ============================================================
# Current Time
# ============================================================


def utc_now() -> datetime:
    """
    Return current UTC datetime.

    """

    return datetime.now(

        timezone.utc

    )



def utc_timestamp() -> int:
    """
    Return current Unix timestamp.

    """

    return int(

        utc_now()

        .timestamp()

    )



def utc_isoformat() -> str:
    """
    Return ISO formatted UTC timestamp.

    Example:

    2026-07-18T10:30:00+00:00

    """

    return utc_now().isoformat()



# ============================================================
# Formatting
# ============================================================


DEFAULT_DATE_FORMAT = "%Y-%m-%d"


DEFAULT_DATETIME_FORMAT = (

    "%Y-%m-%d %H:%M:%S"

)



def format_date(
    value: datetime,
    format_string: str = DEFAULT_DATE_FORMAT,
) -> str:
    """
    Format datetime into date string.

    """

    return value.strftime(

        format_string

    )



def format_datetime(
    value: datetime,
    format_string: str = DEFAULT_DATETIME_FORMAT,
) -> str:
    """
    Format datetime.

    """

    return value.strftime(

        format_string

    )



# ============================================================
# Parsing
# ============================================================


def parse_datetime(
    value: str,
) -> datetime | None:
    """
    Parse ISO datetime string.

    """

    try:

        return datetime.fromisoformat(

            value

        )



    except (

        ValueError,

        TypeError,

    ):

        return None



# ============================================================
# Expiry Helpers
# ============================================================


def add_minutes(
    minutes: int,
    start: datetime | None = None,
) -> datetime:
    """
    Add minutes to datetime.

    """

    base = start or utc_now()


    return base + timedelta(

        minutes=minutes

    )



def add_hours(
    hours: int,
    start: datetime | None = None,
) -> datetime:
    """
    Add hours to datetime.

    """

    base = start or utc_now()


    return base + timedelta(

        hours=hours

    )



def add_days(
    days: int,
    start: datetime | None = None,
) -> datetime:
    """
    Add days to datetime.

    """

    base = start or utc_now()


    return base + timedelta(

        days=days

    )



# ============================================================
# Comparisons
# ============================================================


def is_expired(
    expiry: datetime,
) -> bool:
    """
    Check whether timestamp expired.

    """

    return utc_now() >= expiry



def seconds_until(
    expiry: datetime,
) -> int:
    """
    Calculate remaining seconds.

    """

    difference = (

        expiry

        -

        utc_now()

    )


    return max(

        0,

        int(

            difference.total_seconds()

        )

    )



# ============================================================
# Duration Helpers
# ============================================================


def duration_seconds(
    start: datetime,
    end: datetime,
) -> int:
    """
    Calculate duration seconds.

    """

    return int(

        (

            end - start

        )

        .total_seconds()

    )



def duration_minutes(
    start: datetime,
    end: datetime,
) -> float:
    """
    Calculate duration minutes.

    """

    return (

        end - start

    ).total_seconds() / 60



# ============================================================
# Timezone Helpers
# ============================================================


def ensure_utc(
    value: datetime,
) -> datetime:
    """
    Convert datetime to UTC.

    """

    if value.tzinfo is None:

        return value.replace(

            tzinfo=timezone.utc

        )



    return value.astimezone(

        timezone.utc

    )



# ============================================================
# Audit Helpers
# ============================================================


def create_timestamp_metadata() -> dict[str, Any]:
    """
    Generate standard timestamp metadata.

    Used for:

    - Events
    - Audit logs
    - Database records

    """

    now = utc_now()


    return {

        "created_at":

            now.isoformat(),


        "updated_at":

            now.isoformat(),


        "timestamp":

            int(

                now.timestamp()

            ),

    }