"""
QShield Enterprise
==================

JSON Utilities.

Provides:

- Safe JSON serialization
- JSON parsing
- Validation helpers
- Pretty formatting
- Object conversion

Used across:

- APIs
- Database layer
- Events
- Integrations
- Reports
"""

from __future__ import annotations


import json


from datetime import datetime
from datetime import date


from decimal import Decimal


from uuid import UUID


from typing import Any



# ============================================================
# Custom JSON Encoder
# ============================================================


class QShieldJSONEncoder(
    json.JSONEncoder
):
    """
    Custom JSON encoder.

    Handles:

    - datetime
    - UUID
    - Decimal
    - Sets
    """



    def default(
        self,
        obj: Any,
    ):
        """
        Convert unsupported objects.
        """

        if isinstance(

            obj,

            (

                datetime,

                date,

            ),

        ):

            return obj.isoformat()



        if isinstance(

            obj,

            UUID,

        ):

            return str(

                obj

            )



        if isinstance(

            obj,

            Decimal,

        ):

            return float(

                obj

            )



        if isinstance(

            obj,

            set,

        ):

            return list(

                obj

            )



        return super().default(

            obj

        )



# ============================================================
# Serialization
# ============================================================


def serialize(
    data: Any,
) -> str:
    """
    Convert object into JSON string.

    """

    return json.dumps(

        data,

        cls=QShieldJSONEncoder,

        ensure_ascii=False,

    )



def serialize_pretty(
    data: Any,
) -> str:
    """
    Convert object into formatted JSON.

    """

    return json.dumps(

        data,

        cls=QShieldJSONEncoder,

        indent=4,

        ensure_ascii=False,

    )



# ============================================================
# Deserialization
# ============================================================


def deserialize(
    value: str,
) -> Any:
    """
    Parse JSON string.

    """

    return json.loads(

        value

    )



def safe_deserialize(
    value: str,
    default: Any = None,
) -> Any:
    """
    Safe JSON parsing.

    Returns default
    if parsing fails.

    """

    try:

        return deserialize(

            value

        )



    except (

        json.JSONDecodeError,

        TypeError,

    ):

        return default



# ============================================================
# Validation
# ============================================================


def is_valid_json(
    value: str,
) -> bool:
    """
    Check JSON validity.

    """

    try:

        json.loads(

            value

        )


        return True



    except (

        json.JSONDecodeError,

        TypeError,

    ):

        return False



# ============================================================
# Object Helpers
# ============================================================


def to_json_dict(
    obj: Any,
) -> dict[str, Any]:
    """
    Convert object into JSON-compatible dictionary.

    """

    if isinstance(

        obj,

        dict,

    ):

        return obj



    if hasattr(

        obj,

        "model_dump",

    ):

        return obj.model_dump()



    if hasattr(

        obj,

        "__dict__",

    ):

        return {

            key:

                value

            for key, value in obj.__dict__.items()

            if not key.startswith(

                "_"

            )

        }



    return {

        "value":

            obj

    }



# ============================================================
# JSON Merge Helpers
# ============================================================


def merge_json(
    base: dict[str, Any],
    update: dict[str, Any],
) -> dict[str, Any]:
    """
    Merge two JSON objects.

    """

    result = base.copy()



    for key, value in update.items():

        if (

            key in result

            and

            isinstance(

                result[key],

                dict,

            )

            and

            isinstance(

                value,

                dict,

            )

        ):

            result[key] = merge_json(

                result[key],

                value,

            )



        else:

            result[key] = value



    return result



# ============================================================
# JSON Size
# ============================================================


def json_size(
    data: Any,
) -> int:
    """
    Calculate JSON byte size.

    """

    return len(

        serialize(

            data

        ).encode(

            "utf-8"

        )

    )
# ============================================================
# Backward Compatibility Aliases
# ============================================================

def serialize_json(
    data: Any,
) -> str:
    """
    Backward compatible JSON serializer.

    Alias for serialize().
    """

    return serialize(data)



def deserialize_json(
    value: str,
) -> Any:
    """
    Backward compatible JSON deserializer.

    Alias for deserialize().
    """

    return deserialize(value)