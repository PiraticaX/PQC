"""
QShield Enterprise
==================

ORM Model Registry

This module imports and exports every SQLAlchemy ORM model used by
QShield Enterprise.

Importing this module ensures all model metadata is registered with
SQLAlchemy before:

- Alembic autogeneration
- Database initialization
- Application startup
- Test execution

Typical usage:

    from app.models import *

or

    import app.models
"""

# ============================================================
# Core Models
# ============================================================

from .organization import Organization

# ============================================================
# Identity & Access Management
# ============================================================

from .user import User
from .role import Role
from .permission import Permission
from .user_role import UserRole
from .role_permission import RolePermission

# ============================================================
# Teams
# ============================================================

from .team import Team
from .team_member import TeamMember

# ============================================================
# Assets
# ============================================================

from .asset_group import AssetGroup
from .asset import Asset

# ============================================================
# Scan Engine
# ============================================================

from .scan import Scan

# ============================================================
# Findings
# ============================================================

from .finding import Finding
from .finding_evidence import FindingEvidence
from .finding_comment import FindingComment
from .finding_history import FindingHistory
from .finding_reference import FindingReference
from .finding_exception import FindingException

# ============================================================
# Scan Results
# ============================================================

from .tls_result import TLSResult
from .certificate_result import CertificateResult
from .dns_result import DNSResult
from .http_result import HTTPResult
from .cookie_result import CookieResult
from .email_result import EmailResult
from .technology_result import TechnologyResult
from .pqc_result import PQCResult
from .compliance_result import ComplianceResult

# ============================================================
# Intelligence
# ============================================================

from .ai_recommendation import AIRecommendation

# ============================================================
# Reports
# ============================================================

from .report import Report

# ============================================================
# Scheduling
# ============================================================

from .scheduled_scan import ScheduledScan

# ============================================================
# Auditing
# ============================================================

from .audit_log import AuditLog


__all__ = [
    # Core
    "Organization",

    # Identity
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",

    # Teams
    "Team",
    "TeamMember",

    # Assets
    "AssetGroup",
    "Asset",

    # Scan
    "Scan",

    # Findings
    "Finding",
    "FindingEvidence",
    "FindingComment",
    "FindingHistory",
    "FindingReference",
    "FindingException",

    # Scan Results
    "TLSResult",
    "CertificateResult",
    "DNSResult",
    "HTTPResult",
    "CookieResult",
    "EmailResult",
    "TechnologyResult",
    "PQCResult",
    "ComplianceResult",

    # AI
    "AIRecommendation",

    # Reports
    "Report",

    # Scheduling
    "ScheduledScan",

    # Audit
    "AuditLog",
]
