"""
QShield Enterprise
==================

API Response Utilities.

Provides:

- Standard API response format
- Success responses
- Error responses
- Response metadata
- Pagination integration
- Consistent API contracts

Used across:

- API endpoints
- Services
- Exception handlers
- Middleware
"""

from __future__ import annotations


from datetime import datetime
from datetime import timezone



from typing import Any



# ============================================================
# Response Status
# ============================================================


STATUS_SUCCESS = "success"


STATUS_ERROR = "error"


STATUS_WARNING = "warning"



# ============================================================
# Base Response
# ============================================================


class APIResponse:
    """
    Standard QShield API response.

    Format:

    {
        status,
        message,
        data,
        metadata
    }

    """



    def __init__(
        self,
        status: str,
        message: str,
        data: Any = None,
        metadata: dict[str, Any] | None = None,
    ):

        self.status = status

        self.message = message

        self.data = data

        self.metadata = metadata or {}



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert response to dictionary.

        """

        return {

            "status":

                self.status,


            "message":

                self.message,


            "data":

                self.data,


            "metadata":

                self.metadata,


            "timestamp":

                datetime.now(

                    timezone.utc

                ).isoformat(),

        }



# ============================================================
# Success Responses
# ============================================================


def success_response(
    data: Any = None,
    message: str = "Operation successful",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create successful API response.

    """

    return APIResponse(

        status=STATUS_SUCCESS,

        message=message,

        data=data,

        metadata=metadata,

    ).to_dict()



def created_response(
    data: Any = None,
    message: str = "Resource created successfully",
) -> dict[str, Any]:
    """
    Create resource response.

    """

    return success_response(

        data,

        message,

    )



def accepted_response(
    data: Any = None,
    message: str = "Request accepted",
) -> dict[str, Any]:
    """
    Async processing response.

    """

    return success_response(

        data,

        message,

    )



# ============================================================
# Error Responses
# ============================================================


def error_response(
    message: str,
    code: str | None = None,
    details: Any = None,
    status_code: int = 400,
) -> dict[str, Any]:
    """
    Create API error response.

    """

    return {

        "status":

            STATUS_ERROR,


        "message":

            message,


        "error":

            {

                "code":

                    code,


                "details":

                    details,

            },


        "status_code":

            status_code,


        "timestamp":

            datetime.now(

                timezone.utc

            ).isoformat(),

    }



def unauthorized_response(
    message: str = "Authentication required",
):
    """
    Unauthorized response.

    """

    return error_response(

        message,

        code="UNAUTHORIZED",

        status_code=401,

    )



def forbidden_response(
    message: str = "Permission denied",
):
    """
    Forbidden response.

    """

    return error_response(

        message,

        code="FORBIDDEN",

        status_code=403,

    )



def not_found_response(
    message: str = "Resource not found",
):
    """
    Not found response.

    """

    return error_response(

        message,

        code="NOT_FOUND",

        status_code=404,

    )



def validation_error_response(
    errors: Any,
):
    """
    Validation failure response.

    """

    return error_response(

        "Validation failed",

        code="VALIDATION_ERROR",

        details=errors,

        status_code=422,

    )



def internal_error_response(
    message: str = "Internal server error",
):
    """
    Internal server error response.

    """

    return error_response(

        message,

        code="INTERNAL_ERROR",

        status_code=500,

    )



# ============================================================
# Exception Conversion
# ============================================================


def exception_response(
    exc: Exception,
) -> dict[str, Any]:
    """
    Convert exception into API response.

    """

    if hasattr(

        exc,

        "to_dict",

    ):

        return {

            "status":

                STATUS_ERROR,


            "error":

                exc.to_dict(),

        }



    return internal_error_response(

        str(exc)

    )



# ============================================================
# Pagination Response
# ============================================================


def paginated_response(
    items: list[Any],
    pagination: dict[str, Any],
    message: str = "Data retrieved successfully",
):
    """
    Create paginated API response.

    """

    return success_response(

        data={

            "items":

                items,

        },


        message=message,


        metadata={

            "pagination":

                pagination,

        },

    )