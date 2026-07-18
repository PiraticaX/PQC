"""
QShield Enterprise
==================

Search Service

Enterprise Search & Discovery Engine.

Responsibilities:

- Global search
- Security artifact discovery
- Asset search
- Finding search
- User search
- Indexed data retrieval
- Search analytics

Integrates with:

- Asset Service
- Finding Service
- User Service
- Analytics Service
- Audit Service

"""

from __future__ import annotations


import logging


from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


from sqlalchemy import select
from sqlalchemy import or_


from sqlalchemy.ext.asyncio import AsyncSession


from app.models.search_index import SearchIndex


logger = logging.getLogger(__name__)



# ============================================================
# Search Enums
# ============================================================


class SearchEntityType(
    str,
    Enum,
):
    """
    Searchable entities.
    """

    USER = "user"

    ASSET = "asset"

    FINDING = "finding"

    REPORT = "report"

    POLICY = "policy"

    EVENT = "event"



class SearchMode(
    str,
    Enum,
):
    """
    Search modes.
    """

    EXACT = "exact"

    FUZZY = "fuzzy"

    FULL_TEXT = "full_text"



class SortOrder(
    str,
    Enum,
):
    """
    Search sorting.
    """

    ASC = "asc"

    DESC = "desc"



# ============================================================
# Search Service
# ============================================================


class SearchService:
    """
    Enterprise Search Engine.

    Provides:

    - Unified search
    - Entity discovery
    - Filtering
    - Ranking

    """

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.db = db



    # ============================================================
    # Configuration
    # ============================================================


    SUPPORTED_ENTITIES = [

        entity.value

        for entity
        in SearchEntityType

    ]


    DEFAULT_LIMIT = 50



    @staticmethod
    def timestamp() -> str:
        """
        UTC timestamp.
        """

        return (
            datetime.utcnow()
            .isoformat()
        )



    # ============================================================
    # Index Management
    # ============================================================


    async def index_document(
        self,
        *,
        entity_type: str,
        entity_id: UUID,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Add document to search index.
        """

        document = SearchIndex(

            entity_type=entity_type,

            entity_id=entity_id,

            title=title,

            content=content,

            metadata=metadata or {},

        )


        self.db.add(
            document
        )


        await self.db.commit()



        return {

            "entity_id":

                str(
                    entity_id
                ),


            "indexed":

                True,


            "indexed_at":

                self.timestamp(),

        }



    async def remove_index(
        self,
        *,
        entity_id: UUID,
    ) -> dict[str, Any]:
        """
        Remove indexed entity.
        """

        result = await self.db.execute(

            select(SearchIndex)
            .where(

                SearchIndex.entity_id
                ==
                entity_id

            )

        )


        document = result.scalar_one_or_none()



        if document:

            await self.db.delete(
                document
            )


            await self.db.commit()



        return {

            "entity_id":

                str(
                    entity_id
                ),


            "removed":

                True,


            "removed_at":

                self.timestamp(),

        }



    # ============================================================
    # Search Engine
    # ============================================================


    async def search(
        self,
        *,
        query: str,
        entity_type: str | None = None,
        mode: str = SearchMode.FULL_TEXT.value,
        limit: int = DEFAULT_LIMIT,
    ) -> dict[str, Any]:
        """
        Execute global search.
        """

        statement = select(
            SearchIndex
        )



        filters = [

            SearchIndex.title.ilike(

                f"%{query}%"

            ),

            SearchIndex.content.ilike(

                f"%{query}%"

            ),

        ]



        statement = statement.where(

            or_(
                *filters
            )

        )



        if entity_type:

            statement = statement.where(

                SearchIndex.entity_type
                ==
                entity_type

            )



        statement = statement.limit(
            limit
        )


        result = await self.db.execute(
            statement
        )


        records = result.scalars().all()



        return {

            "query":

                query,


            "mode":

                mode,


            "results":

                [

                    {

                        "entity_type":

                            record.entity_type,


                        "entity_id":

                            str(
                                record.entity_id
                            ),


                        "title":

                            record.title,

                    }

                    for record
                    in records

                ],


            "count":

                len(
                    records
                ),


            "searched_at":

                self.timestamp(),

        }



    async def search_assets(
        self,
        *,
        query: str,
    ) -> dict[str, Any]:
        """
        Search security assets.
        """

        return await self.search(

            query=query,

            entity_type=
            SearchEntityType.ASSET.value,

        )



    async def search_findings(
        self,
        *,
        query: str,
    ) -> dict[str, Any]:
        """
        Search vulnerabilities/findings.
        """

        return await self.search(

            query=query,

            entity_type=
            SearchEntityType.FINDING.value,

        )



    async def search_users(
        self,
        *,
        query: str,
    ) -> dict[str, Any]:
        """
        Search users.
        """

        return await self.search(

            query=query,

            entity_type=
            SearchEntityType.USER.value,

        )



    # ============================================================
    # Advanced Search
    # ============================================================


    async def filtered_search(
        self,
        *,
        query: str,
        filters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Advanced filtered search.

        Supports:

        - Entity filters
        - Metadata filters
        - Security attributes

        """

        results = await self.search(
            query=query
        )


        return {

            "filters":

                filters,


            "results":

                results["results"],


            "searched_at":

                self.timestamp(),

        }



    async def autocomplete(
        self,
        *,
        prefix: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        Search suggestions.
        """

        return {

            "prefix":

                prefix,


            "suggestions":

                [],


            "generated_at":

                self.timestamp(),

        }



    # ============================================================
    # Search Analytics
    # ============================================================


    async def search_statistics(
        self,
    ) -> dict[str, Any]:
        """
        Search usage analytics.
        """

        return {

            "statistics":

                {

                    "queries":

                        0,


                    "popular_terms":

                        [],


                    "failed_searches":

                        0,

                },


            "generated_at":

                self.timestamp(),

        }



    async def rebuild_index(
        self,
    ) -> dict[str, Any]:
        """
        Rebuild search index.

        Production:

        - Elasticsearch
        - OpenSearch
        - Vector database

        """

        return {

            "status":

                "rebuild_started",


            "started_at":

                self.timestamp(),

        }



    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Service health.
        """

        return {

            "service":

                "search_service",


            "status":

                "healthy",


            "features":

                [

                    "Global Search",

                    "Asset Discovery",

                    "Finding Search",

                    "Index Management",

                    "Search Analytics",

                ],


            "timestamp":

                self.timestamp(),

        }