"""
QShield Enterprise
==================

Pagination Utilities.

Provides:

- Pagination models
- Offset/limit handling
- Page calculations
- Pagination metadata
- API listing helpers

Used across:

- API endpoints
- Database queries
- Reports
- Asset listings
"""

from __future__ import annotations


from math import ceil



from typing import Any
from typing import Generic
from typing import TypeVar



# ============================================================
# Generic Type
# ============================================================


T = TypeVar(

    "T"

)



# ============================================================
# Pagination Constants
# ============================================================


DEFAULT_PAGE_SIZE = 50


MAX_PAGE_SIZE = 500



# ============================================================
# Pagination Parameters
# ============================================================


class PaginationParams:
    """
    Pagination request parameters.

    """



    def __init__(
        self,
        page: int = 1,
        size: int = DEFAULT_PAGE_SIZE,
    ):

        self.page = max(

            1,

            page,

        )


        self.size = min(

            max(

                1,

                size,

            ),

            MAX_PAGE_SIZE,

        )



    @property
    def offset(
        self,
    ) -> int:
        """
        Calculate database offset.

        """

        return (

            self.page - 1

        ) * self.size



    @property
    def limit(
        self,
    ) -> int:
        """
        Return page size.

        """

        return self.size



# ============================================================
# Pagination Metadata
# ============================================================


class PaginationMetadata:
    """
    Pagination response metadata.

    """



    def __init__(
        self,
        total: int,
        page: int,
        size: int,
    ):

        self.total = total

        self.page = page

        self.size = size



    @property
    def pages(
        self,
    ) -> int:
        """
        Total pages.

        """

        if self.total == 0:

            return 0



        return ceil(

            self.total

            /

            self.size

        )



    @property
    def has_next(
        self,
    ) -> bool:
        """
        Check next page.

        """

        return self.page < self.pages



    @property
    def has_previous(
        self,
    ) -> bool:
        """
        Check previous page.

        """

        return self.page > 1



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert metadata.

        """

        return {

            "total":

                self.total,


            "page":

                self.page,


            "size":

                self.size,


            "pages":

                self.pages,


            "has_next":

                self.has_next,


            "has_previous":

                self.has_previous,

        }



# ============================================================
# Paginated Response
# ============================================================


class PaginatedResponse(
    Generic[T]
):
    """
    Standard paginated response.

    """



    def __init__(
        self,
        items: list[T],
        metadata: PaginationMetadata,
    ):

        self.items = items

        self.metadata = metadata



    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert response.

        """

        return {

            "items":

                self.items,


            "pagination":

                self.metadata.to_dict(),

        }



# ============================================================
# Pagination Helpers
# ============================================================


def paginate(
    items: list[T],
    page: int = 1,
    size: int = DEFAULT_PAGE_SIZE,
) -> PaginatedResponse[T]:
    """
    Paginate in-memory list.

    """

    params = PaginationParams(

        page,

        size,

    )


    total = len(

        items

    )



    start = params.offset



    end = start + params.limit



    metadata = PaginationMetadata(

        total,

        params.page,

        params.size,

    )



    return PaginatedResponse(

        items[start:end],

        metadata,

    )



def calculate_pages(
    total_items: int,
    page_size: int,
) -> int:
    """
    Calculate number of pages.

    """

    if total_items == 0:

        return 0



    return ceil(

        total_items

        /

        page_size

    )