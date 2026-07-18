"""
QShield Enterprise
==================

Serialization Utilities.

Provides:

- Object serialization
- Model conversion
- API payload formatting
- Sensitive field filtering
- Safe data transformation

Used across:

- API responses
- Database models
- Reports
- Events
- Integrations

"""

from __future__ import annotations


from datetime import datetime
from datetime import date


from decimal import Decimal


from uuid import UUID



from typing import Any



# ============================================================
# Sensitive Fields
# ============================================================


DEFAULT_SENSITIVE_FIELDS = {

    "password",

    "password_hash",

    "secret",

    "api_key",

    "token",

    "private_key",

    "encryption_key",

}



# ============================================================
# Basic Serialization
# ============================================================


def serialize_value(
    value: Any,
) -> Any:
    """
    Convert value into JSON-safe format.

    """

    if isinstance(

        value,

        (

            datetime,

            date,

        ),

    ):

        return value.isoformat()



    if isinstance(

        value,

        UUID,

    ):

        return str(

            value

        )



    if isinstance(

        value,

        Decimal,

    ):

        return float(

            value

        )



    if isinstance(

        value,

        bytes,

    ):

        return value.decode(

            "utf-8",

            errors="ignore",

        )



    if isinstance(

        value,

        list,

    ):

        return [

            serialize_value(

                item

            )

            for item in value

        ]



    if isinstance(

        value,

        dict,

    ):

        return {

            key:

                serialize_value(

                    item

                )

            for key, item in value.items()

        }



    return value



# ============================================================
# Object Serialization
# ============================================================


def serialize_object(
    obj: Any,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """
    Convert object into dictionary.

    """

    exclude = exclude or set()



    if isinstance(

        obj,

        dict,

    ):

        data = obj



    elif hasattr(

        obj,

        "model_dump",

    ):

        data = obj.model_dump()



    elif hasattr(

        obj,

        "__dict__",

    ):

        data = obj.__dict__



    else:

        return {

            "value":

                serialize_value(

                    obj

                )

        }



    return {

        key:

            serialize_value(

                value

            )

        for key, value in data.items()

        if key not in exclude

        and not key.startswith(

            "_"

        )

    }



# ============================================================
# Sensitive Data Handling
# ============================================================


def remove_sensitive_fields(
    data: dict[str, Any],
    fields: set[str] | None = None,
) -> dict[str, Any]:
    """
    Remove sensitive information.

    """

    fields = fields or DEFAULT_SENSITIVE_FIELDS



    return {

        key:

            value

        for key, value in data.items()

        if key.lower()

        not in {

            field.lower()

            for field in fields

        }

    }



def mask_sensitive_fields(
    data: dict[str, Any],
    fields: set[str] | None = None,
) -> dict[str, Any]:
    """
    Mask sensitive values.

    """

    fields = fields or DEFAULT_SENSITIVE_FIELDS



    result = {}



    for key, value in data.items():

        if key.lower() in {

            field.lower()

            for field in fields

        }:

            result[key] = "********"



        else:

            result[key] = value



    return result



# ============================================================
# API Serialization
# ============================================================


def serialize_response(
    data: Any,
) -> dict[str, Any]:
    """
    Standard API serialization.

    """

    return {

        "data":

            serialize_value(

                data

            )

    }



def serialize_list(
    items: list[Any],
) -> list[Any]:
    """
    Serialize list objects.

    """

    return [

        serialize_value(

            item

        )

        for item in items

    ]



# ============================================================
# Database Helpers
# ============================================================


def model_to_dict(
    model: Any,
) -> dict[str, Any]:
    """
    Convert database model to dict.

    """

    if hasattr(

        model,

        "__table__",

    ):

        return {

            column.name:

                getattr(

                    model,

                    column.name,

                )

            for column in model.__table__.columns

        }



    return serialize_object(

        model

    )



# ============================================================
# Event Serialization
# ============================================================


def serialize_event(
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Create standardized event payload.

    """

    from backend.utils.ids import generate_event_id

    from backend.utils.datetime_utils import utc_isoformat



    return {

        "event_id":

            generate_event_id(),


        "event_type":

            event_type,


        "timestamp":

            utc_isoformat(),


        "payload":

            serialize_value(

                payload

            ),

    }