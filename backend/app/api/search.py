"""
QShield Enterprise
==================

Search API

Enterprise Intelligent Search Endpoints.

Responsibilities:

- Global search
- Asset discovery
- Finding discovery
- User search
- Security object search
- Autocomplete suggestions
- Search analytics

Integrates with:

- Search Service
- Analytics Service
- Asset Service
- Finding Service
- Audit Service

"""

from __future__ import annotations


import logging


from typing import Any


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends


from pydantic import BaseModel


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.search_service import SearchService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/search",

)



# ============================================================
# Request Schemas
# ============================================================


class SearchRequest(
    BaseModel,
):
    """
    Search payload.
    """

    query: str

    category: str | None = None

    filters: dict[str, Any] | None = None

    limit: int = 20



class AdvancedSearchRequest(
    BaseModel,
):
    """
    Advanced search payload.
    """

    query: str

    fields: list[str]

    filters: dict[str, Any] | None = None



# ============================================================
# Global Search
# ============================================================


@router.post(
    "",
)
async def global_search(
    request: SearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Perform global enterprise search.

    Searches:

    - Users
    - Assets
    - Events
    - Findings
    - Reports

    """

    service = SearchService(
        db
    )


    return await service.search(

        query=request.query,

        category=request.category,

        filters=request.filters,

        limit=request.limit,

    )



@router.get(
    "",
)
async def search_get(
    query: str,
    category: str | None = None,
    limit: int = 20,
    db: Session = Depends(
        get_db
    ),
):
    """
    Quick search endpoint.
    """

    service = SearchService(
        db
    )


    return await service.search(

        query=query,

        category=category,

        limit=limit,

    )



# ============================================================
# Category Search
# ============================================================


@router.post(
    "/assets",
)
async def search_assets(
    request: SearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Search security assets.
    """

    service = SearchService(
        db
    )


    return await service.search_assets(

        query=request.query,

        filters=request.filters,

    )



@router.post(
    "/findings",
)
async def search_findings(
    request: SearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Search security findings.
    """

    service = SearchService(
        db
    )


    return await service.search_findings(

        query=request.query,

        filters=request.filters,

    )



@router.post(
    "/users",
)
async def search_users(
    request: SearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Search users.
    """

    service = SearchService(
        db
    )


    return await service.search_users(

        query=request.query,

    )



@router.post(
    "/events",
)
async def search_events(
    request: SearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Search events.
    """

    service = SearchService(
        db
    )


    return await service.search_events(

        query=request.query,

        filters=request.filters,

    )



# ============================================================
# Advanced Search
# ============================================================


@router.post(
    "/advanced",
)
async def advanced_search(
    request: AdvancedSearchRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Advanced multi-field search.
    """

    service = SearchService(
        db
    )


    return await service.advanced_search(

        query=request.query,

        fields=request.fields,

        filters=request.filters,

    )



# ============================================================
# Discovery
# ============================================================


@router.get(
    "/autocomplete",
)
async def autocomplete(
    query: str,
    db: Session = Depends(
        get_db
    ),
):
    """
    Search autocomplete suggestions.
    """

    service = SearchService(
        db
    )


    return await service.autocomplete(

        query

    )



@router.get(
    "/recent",
)
async def recent_searches(
    user_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve recent searches.
    """

    service = SearchService(
        db
    )


    return await service.recent_searches(

        user_id

    )



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def search_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    Search engine analytics.
    """

    service = SearchService(
        db
    )


    return await service.search_statistics()



@router.get(
    "/health",
)
async def search_health():
    """
    Search engine health.
    """

    return {

        "search":

            {

                "status":

                    "healthy",


                "engine":

                    "operational",


                "index":

                    "available",

            }

    }
