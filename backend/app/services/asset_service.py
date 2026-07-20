"""
QShield Enterprise
==================

Asset Service

Business logic for managing enterprise assets.

This service is intentionally framework-independent and can be reused by:

- FastAPI REST APIs
- Background Workers
- Scheduled Jobs
- CLI Tools
- Unit Tests
- Scanner Orchestrator

Author:
QShield Enterprise
"""

from __future__ import annotations

import ipaddress
import logging
import socket
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.asset import (
    Asset,
    AssetStatus,
    AssetType,
    Criticality,
)
from app.models.organization import Organization

from app.schemas.asset import (
    AssetCreate,
    AssetDashboard,
    AssetDetail,
    AssetListRequest,
    AssetListResponse,
    AssetResponse,
    AssetSearchRequest,
    AssetSearchResponse,
    AssetStatistics,
    AssetSummary,
    AssetUpdate,
)

logger = logging.getLogger(__name__)


class AssetService:
    """
    Enterprise Asset Service.

    Responsibilities
    ----------------
    - Asset CRUD
    - Validation
    - Search
    - Pagination
    - Statistics
    - Dashboard aggregation
    - Bulk operations
    - Scanner integration
    - Risk score management
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        """
        Initialize the service.

        Parameters
        ----------
        db:
            Active SQLAlchemy Session.
        """
        self.db = db
            # ============================================================
    # Validation Helpers
    # ============================================================

    @staticmethod
    def normalize_asset_value(
        value: str,
    ) -> str:
        """
        Normalize a user supplied asset value.

        - Trim whitespace
        - Remove trailing slash
        - Lower-case domains/hostnames
        """

        value = value.strip()

        while value.endswith("/"):
            value = value[:-1]

        return value

    @staticmethod
    def is_ipv4(
        value: str,
    ) -> bool:
        """
        Returns True if the supplied value is a valid IPv4 address.
        """

        try:
            ipaddress.IPv4Address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def is_ipv6(
        value: str,
    ) -> bool:
        """
        Returns True if the supplied value is a valid IPv6 address.
        """

        try:
            ipaddress.IPv6Address(value)
            return True
        except Exception:
            return False

    @staticmethod
    def is_cidr(
        value: str,
    ) -> bool:
        """
        Returns True if the supplied value is a valid CIDR block.
        """

        try:
            ipaddress.ip_network(
                value,
                strict=False,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def resolve_hostname(
        hostname: str,
    ) -> str | None:
        """
        Resolve a hostname to an IPv4 address.

        Returns
        -------
        str | None
            IPv4 address if resolution succeeds,
            otherwise None.
        """

        try:
            return socket.gethostbyname(
                hostname,
            )

        except Exception:
            logger.debug(
                "Unable to resolve hostname '%s'",
                hostname,
            )
            return None

    @staticmethod
    def normalize_tags(
        tags: list[str] | None,
    ) -> list[str]:
        """
        Normalize tag collection.

        - Lower-case
        - Trim whitespace
        - Remove duplicates
        - Sort alphabetically
        """

        if not tags:
            return []

        return sorted(
            {
                tag.strip().lower()
                for tag in tags
                if tag and tag.strip()
            }
        )

    @staticmethod
    def serialize_tags(
        tags: list[str] | None,
    ) -> str:
        """
        Convert a tag list into database storage format.
        """

        return ",".join(
            AssetService.normalize_tags(tags)
        )

    @staticmethod
    def deserialize_tags(
        tags: str | None,
    ) -> list[str]:
        """
        Convert database tag string into a list.
        """

        if not tags:
            return []

        return sorted(
            {
                tag.strip()
                for tag in tags.split(",")
                if tag.strip()
            }
        )
        # ============================================================
    # Database Helpers
    # ============================================================

    async def organization_exists(
        self,
        organization_id: UUID,
    ) -> bool:
        """
        Check whether an organization exists and has not been
        soft-deleted.
        """

        stmt = (
            select(func.count())
            .select_from(Organization)
            .where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )

        total = self.db.scalar(stmt)

        return bool(total)

    async def asset_exists(
        self,
        organization_id: UUID,
        asset_value: str,
        *,
        exclude_asset_id: UUID | None = None,
    ) -> bool:
        """
        Determine whether an asset already exists within an
        organization.

        Parameters
        ----------
        organization_id:
            Organization identifier.

        asset_value:
            Canonical asset value.

        exclude_asset_id:
            Optional asset ID to exclude during updates.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                func.lower(Asset.asset_value)
                == asset_value.lower(),
                Asset.deleted_at.is_(None),
            )
        )

        if exclude_asset_id is not None:
            stmt = stmt.where(
                Asset.id != exclude_asset_id,
            )

        result = self.db.execute(stmt)

        return result.scalar_one_or_none() is not None

    async def get_asset_model(
        self,
        asset_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> Asset | None:
        """
        Retrieve the ORM Asset instance.
        """

        stmt = select(Asset).where(
            Asset.id == asset_id,
        )

        if not include_deleted:
            stmt = stmt.where(
                Asset.deleted_at.is_(None),
            )

        result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_asset_by_value(
        self,
        organization_id: UUID,
        asset_value: str,
    ) -> Asset | None:
        """
        Retrieve an asset by its canonical value.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                func.lower(Asset.asset_value)
                == asset_value.lower(),
                Asset.deleted_at.is_(None),
            )
        )

        result = self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_assets_by_ids(
        self,
        asset_ids: list[UUID],
    ) -> list[Asset]:
        """
        Retrieve multiple assets by ID.
        """

        if not asset_ids:
            return []

        stmt = (
            select(Asset)
            .where(
                Asset.id.in_(asset_ids),
                Asset.deleted_at.is_(None),
            )
        )

        result = self.db.execute(stmt)

        return list(result.scalars().all())

    async def commit(
        self,
    ) -> None:
        """
        Commit the current transaction with rollback protection.
        """

        try:
            self.db.commit()

        except Exception:
            self.db.rollback()
            logger.exception(
                "Database transaction failed."
            )
            raise
            # ============================================================
    # Serialization Helpers
    # ============================================================

    @staticmethod
    def _summary(
        asset: Asset,
    ) -> AssetSummary:
        """
        Convert an Asset ORM object into an AssetSummary schema.
        """

        return AssetSummary(
            id=asset.id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            name=asset.asset_name,
            value=asset.asset_value,
            asset_type=asset.asset_type,
            status=asset.status,
            criticality=asset.criticality,
            organization_id=asset.organization_id,
            asset_group_id=asset.asset_group_id,
            owner_id=asset.owner_id,
            tags=asset.tag_list(),
            risk_score=asset.risk_score,
            active_findings=0,
            last_scan_at=(
                max(
                    (
                        scan.completed_at
                        for scan in asset.scans
                        if scan.completed_at is not None
                    ),
                    default=None,
                )
            ),
        )

    @staticmethod
    def _response(
        asset: Asset,
    ) -> AssetResponse:
        """
        Convert an Asset ORM object into the standard API response.
        """

        return AssetResponse(
            id=asset.id,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            name=asset.asset_name,
            value=asset.asset_value,
            description=asset.description,
            organization_id=asset.organization_id,
            asset_group_id=asset.asset_group_id,
            owner_id=asset.owner_id,
            asset_type=asset.asset_type,
            status=asset.status,
            criticality=asset.criticality,
            external=asset.external,
            scan_enabled=asset.enabled,
            tags=asset.tag_list(),
            risk_score=asset.risk_score,
            active_findings=0,
            total_findings=0,
            scan_count=asset.scan_count,
            last_scan_at=(
                max(
                    (
                        scan.completed_at
                        for scan in asset.scans
                        if scan.completed_at is not None
                    ),
                    default=None,
                )
            ),
            discovered_at=asset.created_at,
        )

    @staticmethod
    def _detail(
        asset: Asset,
    ) -> AssetDetail:
        """
        Convert an Asset ORM object into a detailed response.
        """

        response = AssetDetail(
            **AssetService._response(asset).model_dump(),

            hostname=asset.hostname,
            fqdn=asset.fqdn,
            ip_address=asset.ip_address,
            port=asset.port,
            protocol=asset.protocol,
            scheme=asset.scheme,

            display_name=asset.display_name,

            production=asset.production,
            internet_facing=asset.internet_facing,

            business_impact=asset.business_impact,
            attack_surface_score=asset.attack_surface_score,

            discovered_by=asset.discovered_by,
            source=asset.source,

            notes=asset.notes,
        )

        return response

    @staticmethod
    def _serialize_collection(
        assets: list[Asset],
    ) -> list[AssetSummary]:
        """
        Convert a list of ORM objects into summary schemas.
        """

        return [
            AssetService._summary(asset)
            for asset in assets
        ]
        # ============================================================
    # Create Asset
    # ============================================================

    async def create_asset(
        self,
        payload: AssetCreate,
    ) -> AssetResponse:
        """
        Create a new asset.

        Raises
        ------
        ValueError
            If the organization does not exist or the asset
            already exists.
        """

        if not await self.organization_exists(
            payload.organization_id,
        ):
            raise ValueError(
                "Organization does not exist."
            )

        asset_value = self.normalize_asset_value(
            payload.value,
        )

        if await self.asset_exists(
            payload.organization_id,
            asset_value,
        ):
            raise ValueError(
                "Asset already exists."
            )

        hostname = None
        fqdn = None
        ip_address = None
        scheme = None
        protocol = None
        port = None

        if payload.asset_type in (
            AssetType.DOMAIN,
            AssetType.SUBDOMAIN,
            AssetType.HOSTNAME,
        ):

            hostname = asset_value
            fqdn = asset_value

            ip_address = self.resolve_hostname(
                hostname,
            )

        elif payload.asset_type == AssetType.URL:

            parsed = urlparse(asset_value)

            hostname = parsed.hostname
            fqdn = parsed.hostname
            scheme = parsed.scheme
            protocol = parsed.scheme
            port = parsed.port

            if hostname:
                ip_address = self.resolve_hostname(
                    hostname,
                )

        elif payload.asset_type in (
            AssetType.IPV4,
            AssetType.IPV6,
        ):

            ip_address = asset_value

        elif payload.asset_type == AssetType.CIDR:

            ipaddress.ip_network(
                asset_value,
                strict=False,
            )

        asset = Asset(

            organization_id=payload.organization_id,

            asset_group_id=payload.asset_group_id,

            owner_id=payload.owner_id,

            asset_name=payload.name,

            asset_value=asset_value,

            asset_type=payload.asset_type,

            description=payload.description,

            hostname=hostname,

            fqdn=fqdn,

            ip_address=ip_address,

            scheme=scheme,

            protocol=protocol,

            port=port,

            status=payload.status,

            criticality=payload.criticality,

            enabled=payload.scan_enabled,

            external=payload.external,

            production=getattr(
                payload,
                "production",
                False,
            ),

            internet_facing=getattr(
                payload,
                "internet_facing",
                False,
            ),

            discovered_by=getattr(
                payload,
                "discovered_by",
                None,
            ),

            source=getattr(
                payload,
                "source",
                None,
            ),

            notes=getattr(
                payload,
                "notes",
                None,
            ),

            tags=self.serialize_tags(
                payload.tags,
            ),
        )

        self.db.add(asset)
        try:
            await self.commit()

            # Refresh the ORM instance so autogenerated values
            # (UUID, timestamps, defaults, relationships) are loaded.
            self.db.refresh(asset)

            logger.info(
                "Asset created successfully. id=%s organization=%s",
                asset.id,
                asset.organization_id,
            )

            return self._response(asset)

        except Exception:
            logger.exception(
                "Failed to create asset '%s'.",
                asset_value,
            )
            raise

    # ============================================================
    # Get Asset
    # ============================================================

    async def get_asset(
        self,
        asset_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> AssetResponse:
        """
        Retrieve a single asset.

        Raises
        ------
        ValueError
            If the asset cannot be found.
        """

        asset = await self.get_asset_model(
            asset_id,
            include_deleted=include_deleted,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        return self._response(asset)

    async def get_asset_detail(
        self,
        asset_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> AssetDetail:
        """
        Retrieve a detailed representation of an asset.

        Raises
        ------
        ValueError
            If the asset cannot be found.
        """

        asset = await self.get_asset_model(
            asset_id,
            include_deleted=include_deleted,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        return self._detail(asset)
        # ============================================================
    # Update Asset
    # ============================================================

    async def update_asset(
        self,
        asset_id: UUID,
        payload: AssetUpdate,
    ) -> AssetResponse:
        """
        Update an existing asset.

        Raises
        ------
        ValueError
            If the asset does not exist or the updated asset value
            would conflict with another asset in the organization.
        """

        asset = await self.get_asset_model(asset_id)

        if asset is None:
            raise ValueError("Asset not found.")

        updates = payload.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        # --------------------------------------------------------
        # Asset Value
        # --------------------------------------------------------

        if "value" in updates:

            asset_value = self.normalize_asset_value(
                updates["value"],
            )

            if await self.asset_exists(
                asset.organization_id,
                asset_value,
                exclude_asset_id=asset.id,
            ):
                raise ValueError(
                    "Another asset with this value already exists."
                )

            asset.asset_value = asset_value

            hostname = None
            fqdn = None
            ip_address = None
            scheme = None
            protocol = None
            port = None

            if asset.asset_type in (
                AssetType.DOMAIN,
                AssetType.SUBDOMAIN,
                AssetType.HOSTNAME,
            ):

                hostname = asset_value
                fqdn = asset_value
                ip_address = self.resolve_hostname(hostname)

            elif asset.asset_type == AssetType.URL:

                parsed = urlparse(asset_value)

                hostname = parsed.hostname
                fqdn = parsed.hostname
                scheme = parsed.scheme
                protocol = parsed.scheme
                port = parsed.port

                if hostname:
                    ip_address = self.resolve_hostname(hostname)

            elif asset.asset_type in (
                AssetType.IPV4,
                AssetType.IPV6,
            ):
                ip_address = asset_value

            asset.hostname = hostname
            asset.fqdn = fqdn
            asset.ip_address = ip_address
            asset.scheme = scheme
            asset.protocol = protocol
            asset.port = port

        # --------------------------------------------------------
        # Simple field mappings
        # --------------------------------------------------------

        field_mapping = {
            "name": "asset_name",
            "description": "description",
            "asset_group_id": "asset_group_id",
            "owner_id": "owner_id",
            "asset_type": "asset_type",
            "status": "status",
            "criticality": "criticality",
            "scan_enabled": "enabled",
            "external": "external",
            "production": "production",
            "internet_facing": "internet_facing",
            "display_name": "display_name",
            "business_impact": "business_impact",
            "attack_surface_score": "attack_surface_score",
            "discovered_by": "discovered_by",
            "source": "source",
            "notes": "notes",
        }

        for schema_field, model_field in field_mapping.items():
            if schema_field in updates:
                setattr(
                    asset,
                    model_field,
                    updates[schema_field],
                )

        if "tags" in updates:
            asset.tags = self.serialize_tags(
                updates["tags"],
            )

        try:
            await self.commit()
            self.db.refresh(asset)

            logger.info(
                "Asset updated successfully. id=%s",
                asset.id,
            )

            return self._response(asset)

        except Exception:
            logger.exception(
                "Failed to update asset. id=%s",
                asset.id,
            )
            raise
            # ============================================================
    # Delete / Restore Asset
    # ============================================================

    async def delete_asset(
        self,
        asset_id: UUID,
        *,
        hard_delete: bool = False,
    ) -> bool:
        """
        Delete an asset.

        By default a soft-delete is performed. Set
        ``hard_delete=True`` to permanently remove the asset.

        Raises
        ------
        ValueError
            If the asset does not exist.
        """

        asset = await self.get_asset_model(
            asset_id,
            include_deleted=True,
        )

        if asset is None:
            raise ValueError("Asset not found.")

        try:
            if hard_delete:
                self.db.delete(asset)

                logger.info(
                    "Hard deleted asset. id=%s",
                    asset.id,
                )
            else:
                asset.soft_delete()

                logger.info(
                    "Soft deleted asset. id=%s",
                    asset.id,
                )

            await self.commit()
            return True

        except Exception:
            logger.exception(
                "Failed to delete asset. id=%s",
                asset_id,
            )
            raise

    async def restore_asset(
        self,
        asset_id: UUID,
    ) -> AssetResponse:
        """
        Restore a previously soft-deleted asset.

        Raises
        ------
        ValueError
            If the asset does not exist.
        """

        asset = await self.get_asset_model(
            asset_id,
            include_deleted=True,
        )

        if asset is None:
            raise ValueError("Asset not found.")

        asset.restore()

        try:
            await self.commit()
            self.db.refresh(asset)

            logger.info(
                "Restored asset. id=%s",
                asset.id,
            )

            return self._response(asset)

        except Exception:
            logger.exception(
                "Failed to restore asset. id=%s",
                asset.id,
            )
            raise

    async def asset_count(
        self,
        organization_id: UUID,
        *,
        include_deleted: bool = False,
    ) -> int:
        """
        Return the total number of assets in an organization.
        """

        stmt = (
            select(func.count())
            .select_from(Asset)
            .where(
                Asset.organization_id == organization_id,
            )
        )

        if not include_deleted:
            stmt = stmt.where(
                Asset.deleted_at.is_(None),
            )

        total = self.db.scalar(stmt)

        return int(total or 0)
        # ============================================================
    # Query Builder Helpers
    # ============================================================

    def _build_filters(
        self,
        request: AssetListRequest,
    ) -> list[Any]:
        """
        Build SQLAlchemy filter expressions from an AssetListRequest.
        """

        filters: list[Any] = []

        # Organization (required)
        filters.append(
            Asset.organization_id == request.organization_id,
        )

        # Exclude soft-deleted assets unless explicitly requested
        if not getattr(request, "include_deleted", False):
            filters.append(
                Asset.deleted_at.is_(None),
            )

        # Asset types
        if request.asset_types:
            filters.append(
                Asset.asset_type.in_(request.asset_types),
            )

        # Statuses
        if request.statuses:
            filters.append(
                Asset.status.in_(request.statuses),
            )

        # Criticalities
        if request.criticalities:
            filters.append(
                Asset.criticality.in_(request.criticalities),
            )

        # Asset Group
        if request.asset_group_id:
            filters.append(
                Asset.asset_group_id == request.asset_group_id,
            )

        # Owner
        if request.owner_id:
            filters.append(
                Asset.owner_id == request.owner_id,
            )

        # External / Internal
        if request.external is not None:
            filters.append(
                Asset.external == request.external,
            )

        # Production
        if request.production is not None:
            filters.append(
                Asset.production == request.production,
            )

        # Internet Facing
        if request.internet_facing is not None:
            filters.append(
                Asset.internet_facing == request.internet_facing,
            )

        # Scanner Enabled
        if request.scan_enabled is not None:
            filters.append(
                Asset.enabled == request.scan_enabled,
            )

        # Risk Score Range
        if request.min_risk_score is not None:
            filters.append(
                Asset.risk_score >= request.min_risk_score,
            )

        if request.max_risk_score is not None:
            filters.append(
                Asset.risk_score <= request.max_risk_score,
            )

        # Business Impact Range
        if request.min_business_impact is not None:
            filters.append(
                Asset.business_impact >= request.min_business_impact,
            )

        if request.max_business_impact is not None:
            filters.append(
                Asset.business_impact <= request.max_business_impact,
            )

        # Search Text
        if request.search:
            search = f"%{request.search.strip()}%"

            filters.append(
                or_(
                    Asset.asset_name.ilike(search),
                    Asset.asset_value.ilike(search),
                    Asset.display_name.ilike(search),
                    Asset.hostname.ilike(search),
                    Asset.fqdn.ilike(search),
                    Asset.ip_address.ilike(search),
                    Asset.description.ilike(search),
                )
            )

        # Tags (stored as comma-separated string)
        if request.tags:
            tag_filters = [
                Asset.tags.ilike(f"%{tag}%")
                for tag in request.tags
            ]

            filters.append(
                and_(*tag_filters),
            )

        return filters

    def _build_base_query(
        self,
        request: AssetListRequest,
    ):
        """
        Construct the base SELECT query for asset listings.
        """

        return (
            select(Asset)
            .where(
                *self._build_filters(request),
            )
        )
        # ============================================================
    # List Assets
    # ============================================================

    async def list_assets(
        self,
        request: AssetListRequest,
    ) -> AssetListResponse:
        """
        Retrieve a paginated list of assets.

        Supports:
        - Filtering
        - Searching
        - Sorting
        - Pagination
        """

        stmt = self._build_base_query(request)

        # --------------------------------------------------------
        # Sorting
        # --------------------------------------------------------

        sort_field = getattr(
            request,
            "sort_by",
            "created_at",
        )

        sort_column = getattr(
            Asset,
            sort_field,
            Asset.created_at,
        )

        sort_order = getattr(
            request,
            "sort_order",
            "desc",
        )

        if str(sort_order).lower() == "asc":
            stmt = stmt.order_by(
                sort_column.asc(),
            )
        else:
            stmt = stmt.order_by(
                sort_column.desc(),
            )

        # --------------------------------------------------------
        # Count (before pagination)
        # --------------------------------------------------------

        count_stmt = (
            select(func.count())
            .select_from(Asset)
            .where(
                *self._build_filters(request),
            )
        )

        total = self.db.scalar(count_stmt)
        total = int(total or 0)

        # --------------------------------------------------------
        # Pagination
        # --------------------------------------------------------

        page = max(1, request.page)
        page_size = max(1, request.page_size)

        offset = (page - 1) * page_size

        stmt = (
            stmt.offset(offset)
                .limit(page_size)
        )

        # --------------------------------------------------------
        # Execute
        # --------------------------------------------------------

        result = self.db.execute(stmt)

        assets = list(result.scalars().all())

        # --------------------------------------------------------
        # Response
        # --------------------------------------------------------

        return AssetListResponse(
            items=self._serialize_collection(
                assets,
            ),
            total=total,
            page=page,
            page_size=page_size,
            pages=(
                (total + page_size - 1)
                // page_size
            ),
        )
        # ============================================================
    # Advanced Search
    # ============================================================

    async def search_assets(
        self,
        request: AssetSearchRequest,
    ) -> AssetSearchResponse:
        """
        Perform an advanced asset search.

        Supports searching by:
        - Asset name
        - Asset value
        - Hostname
        - FQDN
        - IP Address
        - Display name
        - Description
        - Tags
        """

        query = request.query.strip()

        search = f"%{query}%"

        filters = [
            Asset.organization_id == request.organization_id,
            Asset.deleted_at.is_(None),
        ]

        stmt = (
            select(Asset)
            .where(
                *filters,
                or_(
                    Asset.asset_name.ilike(search),
                    Asset.asset_value.ilike(search),
                    Asset.display_name.ilike(search),
                    Asset.hostname.ilike(search),
                    Asset.fqdn.ilike(search),
                    Asset.ip_address.ilike(search),
                    Asset.description.ilike(search),
                    Asset.tags.ilike(search),
                ),
            )
            .order_by(
                Asset.risk_score.desc(),
                Asset.asset_name.asc(),
            )
        )

        if request.limit:
            stmt = stmt.limit(request.limit)

        result = self.db.execute(stmt)

        assets = list(result.scalars().all())

        summaries = self._serialize_collection(
            assets,
        )

        return AssetSearchResponse(
            query=query,
            total=len(summaries),
            results=summaries,
        )

    async def asset_lookup(
        self,
        organization_id: UUID,
        query: str,
        *,
        limit: int = 20,
    ) -> list[AssetSummary]:
        """
        Lightweight lookup endpoint for autocomplete controls.
        """

        search = f"%{query.strip()}%"

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                or_(
                    Asset.asset_name.ilike(search),
                    Asset.asset_value.ilike(search),
                    Asset.display_name.ilike(search),
                ),
            )
            .order_by(
                Asset.asset_name.asc(),
            )
            .limit(limit)
        )

        result = self.db.execute(stmt)

        return self._serialize_collection(
            list(result.scalars().all())
        )
        # ============================================================
    # Search Helpers
    # ============================================================

    async def find_by_hostname(
        self,
        organization_id: UUID,
        hostname: str,
    ) -> Asset | None:
        """
        Find an asset by hostname or FQDN.
        """

        hostname = hostname.strip().lower()

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                or_(
                    func.lower(Asset.hostname) == hostname,
                    func.lower(Asset.fqdn) == hostname,
                ),
            )
            .limit(1)
        )

        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_ip(
        self,
        organization_id: UUID,
        ip_address: str,
    ) -> Asset | None:
        """
        Find an asset by IP address.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.ip_address == ip_address,
            )
            .limit(1)
        )

        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_tag(
        self,
        organization_id: UUID,
        tag: str,
    ) -> list[AssetSummary]:
        """
        Return all assets containing the supplied tag.
        """

        tag = tag.strip().lower()

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.tags.ilike(f"%{tag}%"),
            )
            .order_by(
                Asset.asset_name.asc(),
            )
        )

        result = self.db.execute(stmt)

        assets = list(result.scalars().all())

        return self._serialize_collection(assets)

    async def asset_name_exists(
        self,
        organization_id: UUID,
        asset_name: str,
        *,
        exclude_asset_id: UUID | None = None,
    ) -> bool:
        """
        Check whether an asset name already exists within an organization.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                func.lower(Asset.asset_name) == asset_name.strip().lower(),
                Asset.deleted_at.is_(None),
            )
        )

        if exclude_asset_id is not None:
            stmt = stmt.where(Asset.id != exclude_asset_id)

        result = self.db.execute(stmt)

        return result.scalar_one_or_none() is not None
        # ============================================================
    # Statistics
    # ============================================================

    async def get_statistics(
        self,
        organization_id: UUID,
    ) -> AssetStatistics:
        """
        Return aggregate asset statistics for an organization.
        """

        base_filter = [
            Asset.organization_id == organization_id,
            Asset.deleted_at.is_(None),
        ]

        # --------------------------------------------------------
        # Total Assets
        # --------------------------------------------------------

        total_assets = int(
            (
                self.db.scalar(
                    select(func.count())
                    .select_from(Asset)
                    .where(*base_filter)
                )
            )
            or 0
        )

        # --------------------------------------------------------
        # Active Assets
        # --------------------------------------------------------

        active_assets = int(
            (
                self.db.scalar(
                    select(func.count())
                    .select_from(Asset)
                    .where(
                        *base_filter,
                        Asset.status == AssetStatus.ACTIVE,
                    )
                )
            )
            or 0
        )

        # --------------------------------------------------------
        # External Assets
        # --------------------------------------------------------

        external_assets = int(
            (
                self.db.scalar(
                    select(func.count())
                    .select_from(Asset)
                    .where(
                        *base_filter,
                        Asset.external.is_(True),
                    )
                )
            )
            or 0
        )

        # --------------------------------------------------------
        # Production Assets
        # --------------------------------------------------------

        production_assets = int(
            (
                self.db.scalar(
                    select(func.count())
                    .select_from(Asset)
                    .where(
                        *base_filter,
                        Asset.production.is_(True),
                    )
                )
            )
            or 0
        )

        # --------------------------------------------------------
        # Internet Facing Assets
        # --------------------------------------------------------

        internet_facing_assets = int(
            (
                self.db.scalar(
                    select(func.count())
                    .select_from(Asset)
                    .where(
                        *base_filter,
                        Asset.internet_facing.is_(True),
                    )
                )
            )
            or 0
        )

        # --------------------------------------------------------
        # Average Risk Score
        # --------------------------------------------------------

        average_risk_score = float(
            (
                self.db.scalar(
                    select(func.avg(Asset.risk_score))
                    .where(*base_filter)
                )
            )
            or 0.0
        )

        return AssetStatistics(
            total_assets=total_assets,
            active_assets=active_assets,
            external_assets=external_assets,
            production_assets=production_assets,
            internet_facing_assets=internet_facing_assets,
            average_risk_score=round(
                average_risk_score,
                2,
            ),
        )
        # ============================================================
    # Dashboard
    # ============================================================

    async def get_dashboard(
        self,
        organization_id: UUID,
    ) -> AssetDashboard:
        """
        Build the asset dashboard for an organization.
        """

        statistics = await self.get_statistics(
            organization_id,
        )

        base_filter = [
            Asset.organization_id == organization_id,
            Asset.deleted_at.is_(None),
        ]

        # --------------------------------------------------------
        # Criticality Distribution
        # --------------------------------------------------------

        criticality_rows = (
            self.db.execute(
                select(
                    Asset.criticality,
                    func.count(Asset.id),
                )
                .where(*base_filter)
                .group_by(Asset.criticality)
            )
        ).all()

        criticality_distribution = {
            str(level.value): count
            for level, count in criticality_rows
            if level is not None
        }

        # --------------------------------------------------------
        # Asset Type Distribution
        # --------------------------------------------------------

        asset_type_rows = (
            self.db.execute(
                select(
                    Asset.asset_type,
                    func.count(Asset.id),
                )
                .where(*base_filter)
                .group_by(Asset.asset_type)
            )
        ).all()

        asset_type_distribution = {
            str(asset_type.value): count
            for asset_type, count in asset_type_rows
            if asset_type is not None
        }

        # --------------------------------------------------------
        # Status Distribution
        # --------------------------------------------------------

        status_rows = (
            self.db.execute(
                select(
                    Asset.status,
                    func.count(Asset.id),
                )
                .where(*base_filter)
                .group_by(Asset.status)
            )
        ).all()

        status_distribution = {
            str(status.value): count
            for status, count in status_rows
            if status is not None
        }

        # --------------------------------------------------------
        # Top Risk Assets
        # --------------------------------------------------------

        result = self.db.execute(
            select(Asset)
            .where(*base_filter)
            .order_by(
                Asset.risk_score.desc(),
                Asset.asset_name.asc(),
            )
            .limit(10)
        )

        top_risk_assets = self._serialize_collection(
            list(result.scalars().all())
        )

        return AssetDashboard(
            statistics=statistics,
            criticality_distribution=criticality_distribution,
            asset_type_distribution=asset_type_distribution,
            status_distribution=status_distribution,
            top_risk_assets=top_risk_assets,
        )
        # ============================================================
    # Bulk Operations
    # ============================================================

    async def bulk_create_assets(
        self,
        assets: list[AssetCreate],
    ) -> list[AssetResponse]:
        """
        Create multiple assets sequentially.

        Returns only successfully created assets.
        """

        created_assets: list[AssetResponse] = []

        for payload in assets:
            try:
                created = await self.create_asset(payload)
                created_assets.append(created)
            except Exception:
                logger.exception(
                    "Failed to create asset '%s'",
                    payload.value,
                )

        return created_assets

    async def bulk_update_assets(
        self,
        asset_ids: list[UUID],
        payload: AssetUpdate,
    ) -> list[AssetResponse]:
        """
        Apply the same update to multiple assets.

        Assets that fail to update are skipped.
        """

        updated_assets: list[AssetResponse] = []

        for asset_id in asset_ids:
            try:
                updated = await self.update_asset(
                    asset_id,
                    payload,
                )
                updated_assets.append(updated)
            except Exception:
                logger.exception(
                    "Failed to update asset. id=%s",
                    asset_id,
                )

        return updated_assets

    async def bulk_delete_assets(
        self,
        asset_ids: list[UUID],
        *,
        hard_delete: bool = False,
    ) -> int:
        """
        Delete multiple assets.

        Returns the number of successfully deleted assets.
        """

        deleted = 0

        for asset_id in asset_ids:
            try:
                if await self.delete_asset(
                    asset_id,
                    hard_delete=hard_delete,
                ):
                    deleted += 1
            except Exception:
                logger.exception(
                    "Failed deleting asset. id=%s",
                    asset_id,
                )

        return deleted
        # ============================================================
    # Bulk Tag & Ownership Operations
    # ============================================================

    async def bulk_add_tags(
        self,
        asset_ids: list[UUID],
        tags: list[str],
    ) -> int:
        """
        Add one or more tags to multiple assets.

        Returns
        -------
        int
            Number of successfully updated assets.
        """

        normalized_tags = self.normalize_tags(tags)
        updated = 0

        for asset in await self.get_assets_by_ids(asset_ids):
            existing = set(self.deserialize_tags(asset.tags))
            existing.update(normalized_tags)

            asset.tags = self.serialize_tags(list(existing))
            updated += 1

        if updated:
            await self.commit()

        logger.info(
            "Added tags to %s asset(s).",
            updated,
        )

        return updated

    async def bulk_remove_tags(
        self,
        asset_ids: list[UUID],
        tags: list[str],
    ) -> int:
        """
        Remove one or more tags from multiple assets.
        """

        remove_tags = set(self.normalize_tags(tags))
        updated = 0

        for asset in await self.get_assets_by_ids(asset_ids):
            current = set(self.deserialize_tags(asset.tags))

            current.difference_update(remove_tags)

            asset.tags = self.serialize_tags(list(current))
            updated += 1

        if updated:
            await self.commit()

        logger.info(
            "Removed tags from %s asset(s).",
            updated,
        )

        return updated

    async def assign_owner(
        self,
        asset_ids: list[UUID],
        owner_id: UUID | None,
    ) -> int:
        """
        Assign or clear the owner for multiple assets.
        """

        updated = 0

        for asset in await self.get_assets_by_ids(asset_ids):
            asset.owner_id = owner_id
            updated += 1

        if updated:
            await self.commit()

        logger.info(
            "Assigned owner to %s asset(s).",
            updated,
        )

        return updated

    async def assign_asset_group(
        self,
        asset_ids: list[UUID],
        asset_group_id: UUID | None,
    ) -> int:
        """
        Assign or clear the asset group for multiple assets.
        """

        updated = 0

        for asset in await self.get_assets_by_ids(asset_ids):
            asset.asset_group_id = asset_group_id
            updated += 1

        if updated:
            await self.commit()

        logger.info(
            "Assigned asset group to %s asset(s).",
            updated,
        )

        return updated
        # ============================================================
    # Risk Management
    # ============================================================

    async def update_risk_score(
        self,
        asset_id: UUID,
        score: float,
    ) -> AssetResponse:
        """
        Update the calculated risk score of an asset.

        Score is automatically clamped by the model helper.
        """

        asset = await self.get_asset_model(asset_id)

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.update_risk_score(
            score,
        )

        try:
            await self.commit()
            self.db.refresh(asset)

            logger.info(
                "Updated risk score. asset=%s score=%s",
                asset.id,
                asset.risk_score,
            )

            return self._response(asset)

        except Exception:
            logger.exception(
                "Failed updating risk score. asset=%s",
                asset.id,
            )
            raise

    async def increase_risk(
        self,
        asset_id: UUID,
        amount: float,
    ) -> AssetResponse:
        """
        Increase an asset risk score.
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.increase_risk(
            amount,
        )

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)

    async def decrease_risk(
        self,
        asset_id: UUID,
        amount: float,
    ) -> AssetResponse:
        """
        Decrease an asset risk score.
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.decrease_risk(
            amount,
        )

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)

    async def update_attack_surface_score(
        self,
        asset_id: UUID,
        score: float,
    ) -> AssetResponse:
        """
        Update attack surface score.

        Score range:
        0 - 100
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.attack_surface_score = max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)
        # ============================================================
    # Scanner Integration Helpers
    # ============================================================

    async def mark_discovered(
        self,
        asset_id: UUID,
        *,
        source: str,
        discovered_by: str,
    ) -> AssetResponse:
        """
        Mark an asset as discovered by a scanner,
        crawler, or discovery engine.
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.status = AssetStatus.DISCOVERED
        asset.source = source
        asset.discovered_by = discovered_by

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)

    async def activate_asset(
        self,
        asset_id: UUID,
    ) -> AssetResponse:
        """
        Activate an asset.
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.enabled = True
        asset.status = AssetStatus.ACTIVE

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)

    async def deactivate_asset(
        self,
        asset_id: UUID,
    ) -> AssetResponse:
        """
        Disable scanning for an asset.
        """

        asset = await self.get_asset_model(
            asset_id,
        )

        if asset is None:
            raise ValueError(
                "Asset not found."
            )

        asset.enabled = False
        asset.status = AssetStatus.INACTIVE

        await self.commit()
        self.db.refresh(asset)

        return self._response(asset)

    async def get_scan_targets(
        self,
        organization_id: UUID,
        *,
        limit: int = 1000,
    ) -> list[Asset]:
        """
        Return assets eligible for scanning.

        Scanner workers use this method to obtain targets.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.enabled.is_(True),
                Asset.status == AssetStatus.ACTIVE,
            )
            .order_by(
                Asset.risk_score.desc(),
            )
            .limit(limit)
        )

        result = self.db.execute(stmt)

        return list(
            result.scalars().all()
        )

    async def get_external_assets(
        self,
        organization_id: UUID,
    ) -> list[AssetSummary]:
        """
        Return internet-facing assets.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.external.is_(True),
            )
            .order_by(
                Asset.risk_score.desc(),
            )
        )

        result = self.db.execute(stmt)

        assets = list(
            result.scalars().all()
        )

        return self._serialize_collection(
            assets,
        )
        # ============================================================
    # Asset Analytics Helpers
    # ============================================================

    async def get_high_risk_assets(
        self,
        organization_id: UUID,
        *,
        threshold: float = 70.0,
        limit: int = 20,
    ) -> list[AssetSummary]:
        """
        Return assets above a risk threshold.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.risk_score >= threshold,
            )
            .order_by(
                Asset.risk_score.desc(),
            )
            .limit(limit)
        )

        result = self.db.execute(stmt)

        assets = list(
            result.scalars().all()
        )

        return self._serialize_collection(
            assets,
        )

    async def get_recently_added_assets(
        self,
        organization_id: UUID,
        *,
        limit: int = 10,
    ) -> list[AssetSummary]:
        """
        Return recently discovered assets.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
            )
            .order_by(
                Asset.created_at.desc(),
            )
            .limit(limit)
        )

        result = self.db.execute(stmt)

        assets = list(
            result.scalars().all()
        )

        return self._serialize_collection(
            assets,
        )

    async def get_production_assets(
        self,
        organization_id: UUID,
    ) -> list[AssetSummary]:
        """
        Return production assets.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.production.is_(True),
            )
            .order_by(
                Asset.asset_name.asc(),
            )
        )

        result = self.db.execute(stmt)

        return self._serialize_collection(
            list(result.scalars().all())
        )

    async def get_assets_by_criticality(
        self,
        organization_id: UUID,
        criticality: Criticality,
    ) -> list[AssetSummary]:
        """
        Retrieve assets matching a criticality level.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
                Asset.criticality == criticality,
            )
            .order_by(
                Asset.risk_score.desc(),
            )
        )

        result = self.db.execute(stmt)

        return self._serialize_collection(
            list(result.scalars().all())
        )
        # ============================================================
    # Final Utilities
    # ============================================================

    async def export_assets(
        self,
        organization_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Export all active assets for an organization.

        Used by:
        - Reporting engine
        - Compliance exports
        - Backup workflows
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
            )
            .order_by(
                Asset.asset_name.asc(),
            )
        )

        result = self.db.execute(stmt)

        assets = list(
            result.scalars().all()
        )

        return [
            asset.to_dict()
            for asset in assets
        ]

    async def count_by_type(
        self,
        organization_id: UUID,
    ) -> dict[str, int]:
        """
        Return asset counts grouped by asset type.
        """

        stmt = (
            select(
                Asset.asset_type,
                func.count(Asset.id),
            )
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
            )
            .group_by(
                Asset.asset_type,
            )
        )

        result = self.db.execute(stmt)

        return {
            asset_type.value: int(count)
            for asset_type, count in result.all()
        }

    async def count_by_status(
        self,
        organization_id: UUID,
    ) -> dict[str, int]:
        """
        Return asset counts grouped by status.
        """

        stmt = (
            select(
                Asset.status,
                func.count(Asset.id),
            )
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_(None),
            )
            .group_by(
                Asset.status,
            )
        )

        result = self.db.execute(stmt)

        return {
            status.value: int(count)
            for status, count in result.all()
        }

    async def purge_deleted_assets(
        self,
        organization_id: UUID,
    ) -> int:
        """
        Permanently delete soft-deleted assets.

        Intended for maintenance jobs.

        Returns
        -------
        int
            Number of removed assets.
        """

        stmt = (
            select(Asset)
            .where(
                Asset.organization_id == organization_id,
                Asset.deleted_at.is_not(None),
            )
        )

        result = self.db.execute(stmt)

        assets = list(
            result.scalars().all()
        )

        for asset in assets:
            self.db.delete(asset)

        if assets:
            await self.commit()

        logger.info(
            "Purged %s deleted assets for organization %s",
            len(assets),
            organization_id,
        )

        return len(assets)


# ============================================================
# End of File
# ============================================================
