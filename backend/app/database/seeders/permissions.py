"""
QShield Enterprise
==================

Permission Seeder

Seeds all built-in QShield permissions.

Features
--------
- Async SQLAlchemy
- Idempotent
- Enterprise RBAC
- Safe to execute multiple times
- Categorized permissions
- Automatic updates for existing permissions

Author
------
QShield Enterprise
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission

logger = logging.getLogger(__name__)

# ============================================================
# Permission Catalog
# ============================================================

PERMISSIONS: list[dict[str, str]] = [

    # ========================================================
    # Organization
    # ========================================================

    {
        "name": "organization:create",
        "display_name": "Create Organization",
        "category": "Organization",
        "description": "Create organizations.",
    },
    {
        "name": "organization:read",
        "display_name": "View Organization",
        "category": "Organization",
        "description": "View organization information.",
    },
    {
        "name": "organization:update",
        "display_name": "Update Organization",
        "category": "Organization",
        "description": "Update organization settings.",
    },
    {
        "name": "organization:delete",
        "display_name": "Delete Organization",
        "category": "Organization",
        "description": "Delete organizations.",
    },
    {
        "name": "organization:list",
        "display_name": "List Organizations",
        "category": "Organization",
        "description": "View all organizations.",
    },
    {
        "name": "organization:manage",
        "display_name": "Manage Organization",
        "category": "Organization",
        "description": "Full organization management.",
    },

    # ========================================================
    # Users
    # ========================================================

    {
        "name": "user:create",
        "display_name": "Create User",
        "category": "Users",
        "description": "Create users.",
    },
    {
        "name": "user:read",
        "display_name": "View User",
        "category": "Users",
        "description": "View users.",
    },
    {
        "name": "user:update",
        "display_name": "Update User",
        "category": "Users",
        "description": "Modify users.",
    },
    {
        "name": "user:delete",
        "display_name": "Delete User",
        "category": "Users",
        "description": "Delete users.",
    },
    {
        "name": "user:list",
        "display_name": "List Users",
        "category": "Users",
        "description": "View user directory.",
    },
    {
        "name": "user:manage",
        "display_name": "Manage Users",
        "category": "Users",
        "description": "Full user administration.",
    },
    {
        "name": "user:assign-role",
        "display_name": "Assign Roles",
        "category": "Users",
        "description": "Assign roles to users.",
    },
    {
        "name": "user:reset-password",
        "display_name": "Reset Password",
        "category": "Users",
        "description": "Reset user passwords.",
    },
    {
        "name": "user:disable",
        "display_name": "Disable User",
        "category": "Users",
        "description": "Disable user accounts.",
    },

    # ========================================================
    # Roles
    # ========================================================

    {
        "name": "role:create",
        "display_name": "Create Role",
        "category": "Roles",
        "description": "Create security roles.",
    },
    {
        "name": "role:read",
        "display_name": "View Role",
        "category": "Roles",
        "description": "View roles.",
    },
    {
        "name": "role:update",
        "display_name": "Update Role",
        "category": "Roles",
        "description": "Modify roles.",
    },
    {
        "name": "role:delete",
        "display_name": "Delete Role",
        "category": "Roles",
        "description": "Delete roles.",
    },
    {
        "name": "role:list",
        "display_name": "List Roles",
        "category": "Roles",
        "description": "View all roles.",
    },
    {
        "name": "role:assign-permission",
        "display_name": "Assign Permission",
        "category": "Roles",
        "description": "Assign permissions to roles.",
    },
    {
        "name": "role:manage",
        "display_name": "Manage Roles",
        "category": "Roles",
        "description": "Full role administration.",
    },

    # ========================================================
    # Teams
    # ========================================================

    {
        "name": "team:create",
        "display_name": "Create Team",
        "category": "Teams",
        "description": "Create security teams.",
    },
    {
        "name": "team:read",
        "display_name": "View Team",
        "category": "Teams",
        "description": "View teams.",
    },
    {
        "name": "team:update",
        "display_name": "Update Team",
        "category": "Teams",
        "description": "Modify teams.",
    },
    {
        "name": "team:delete",
        "display_name": "Delete Team",
        "category": "Teams",
        "description": "Delete teams.",
    },
    {
        "name": "team:list",
        "display_name": "List Teams",
        "category": "Teams",
        "description": "View all teams.",
    },
    {
        "name": "team:manage",
        "display_name": "Manage Teams",
        "category": "Teams",
        "description": "Full team management.",
    },

    # ========================================================
    # Dashboard
    # ========================================================

    {
        "name": "dashboard:view",
        "display_name": "View Dashboard",
        "category": "Dashboard",
        "description": "Access executive dashboard.",
    },
    {
        "name": "dashboard:analytics",
        "display_name": "View Analytics",
        "category": "Dashboard",
        "description": "Access security analytics.",
    },
    {
        "name": "dashboard:export",
        "display_name": "Export Dashboard",
        "category": "Dashboard",
        "description": "Export dashboard widgets.",
    },
    # ========================================================
    # Assets
    # ========================================================

    {
        "name": "asset:create",
        "display_name": "Create Asset",
        "category": "Assets",
        "description": "Create new assets.",
    },
    {
        "name": "asset:read",
        "display_name": "View Asset",
        "category": "Assets",
        "description": "View assets.",
    },
    {
        "name": "asset:update",
        "display_name": "Update Asset",
        "category": "Assets",
        "description": "Modify assets.",
    },
    {
        "name": "asset:delete",
        "display_name": "Delete Asset",
        "category": "Assets",
        "description": "Delete assets.",
    },
    {
        "name": "asset:list",
        "display_name": "List Assets",
        "category": "Assets",
        "description": "View asset inventory.",
    },
    {
        "name": "asset:import",
        "display_name": "Import Assets",
        "category": "Assets",
        "description": "Bulk import assets.",
    },
    {
        "name": "asset:export",
        "display_name": "Export Assets",
        "category": "Assets",
        "description": "Export asset inventory.",
    },
    {
        "name": "asset:discover",
        "display_name": "Discover Assets",
        "category": "Assets",
        "description": "Run asset discovery.",
    },
    {
        "name": "asset:manage",
        "display_name": "Manage Assets",
        "category": "Assets",
        "description": "Full asset administration.",
    },

    # ========================================================
    # Asset Groups
    # ========================================================

    {
        "name": "asset-group:create",
        "display_name": "Create Asset Group",
        "category": "Asset Groups",
        "description": "Create asset groups.",
    },
    {
        "name": "asset-group:read",
        "display_name": "View Asset Group",
        "category": "Asset Groups",
        "description": "View asset groups.",
    },
    {
        "name": "asset-group:update",
        "display_name": "Update Asset Group",
        "category": "Asset Groups",
        "description": "Modify asset groups.",
    },
    {
        "name": "asset-group:delete",
        "display_name": "Delete Asset Group",
        "category": "Asset Groups",
        "description": "Delete asset groups.",
    },
    {
        "name": "asset-group:list",
        "display_name": "List Asset Groups",
        "category": "Asset Groups",
        "description": "View all asset groups.",
    },
    {
        "name": "asset-group:manage",
        "display_name": "Manage Asset Groups",
        "category": "Asset Groups",
        "description": "Full asset group administration.",
    },

    # ========================================================
    # Scans
    # ========================================================

    {
        "name": "scan:create",
        "display_name": "Create Scan",
        "category": "Scans",
        "description": "Create scans.",
    },
    {
        "name": "scan:read",
        "display_name": "View Scan",
        "category": "Scans",
        "description": "View scans.",
    },
    {
        "name": "scan:update",
        "display_name": "Update Scan",
        "category": "Scans",
        "description": "Modify scans.",
    },
    {
        "name": "scan:delete",
        "display_name": "Delete Scan",
        "category": "Scans",
        "description": "Delete scans.",
    },
    {
        "name": "scan:list",
        "display_name": "List Scans",
        "category": "Scans",
        "description": "View scan history.",
    },
    {
        "name": "scan:run",
        "display_name": "Run Scan",
        "category": "Scans",
        "description": "Execute scans.",
    },
    {
        "name": "scan:cancel",
        "display_name": "Cancel Scan",
        "category": "Scans",
        "description": "Cancel running scans.",
    },
    {
        "name": "scan:schedule",
        "display_name": "Schedule Scan",
        "category": "Scans",
        "description": "Schedule scans.",
    },
    {
        "name": "scan:approve",
        "display_name": "Approve Scan",
        "category": "Scans",
        "description": "Approve scans.",
    },
    {
        "name": "scan:manage",
        "display_name": "Manage Scans",
        "category": "Scans",
        "description": "Full scan administration.",
    },

    # ========================================================
    # Scheduled Scans
    # ========================================================

    {
        "name": "scheduled-scan:create",
        "display_name": "Create Scheduled Scan",
        "category": "Scheduled Scans",
        "description": "Create scheduled scans.",
    },
    {
        "name": "scheduled-scan:read",
        "display_name": "View Scheduled Scan",
        "category": "Scheduled Scans",
        "description": "View scheduled scans.",
    },
    {
        "name": "scheduled-scan:update",
        "display_name": "Update Scheduled Scan",
        "category": "Scheduled Scans",
        "description": "Modify scheduled scans.",
    },
    {
        "name": "scheduled-scan:delete",
        "display_name": "Delete Scheduled Scan",
        "category": "Scheduled Scans",
        "description": "Delete scheduled scans.",
    },
    {
        "name": "scheduled-scan:list",
        "display_name": "List Scheduled Scans",
        "category": "Scheduled Scans",
        "description": "View all scheduled scans.",
    },
    {
        "name": "scheduled-scan:manage",
        "display_name": "Manage Scheduled Scans",
        "category": "Scheduled Scans",
        "description": "Manage scheduled scan policies.",
    },

    # ========================================================
    # Findings
    # ========================================================

    {
        "name": "finding:create",
        "display_name": "Create Finding",
        "category": "Findings",
        "description": "Create findings.",
    },
    {
        "name": "finding:read",
        "display_name": "View Finding",
        "category": "Findings",
        "description": "View findings.",
    },
    {
        "name": "finding:update",
        "display_name": "Update Finding",
        "category": "Findings",
        "description": "Modify findings.",
    },
    {
        "name": "finding:delete",
        "display_name": "Delete Finding",
        "category": "Findings",
        "description": "Delete findings.",
    },
    {
        "name": "finding:list",
        "display_name": "List Findings",
        "category": "Findings",
        "description": "View all findings.",
    },
    {
        "name": "finding:assign",
        "display_name": "Assign Finding",
        "category": "Findings",
        "description": "Assign findings to analysts.",
    },
    {
        "name": "finding:resolve",
        "display_name": "Resolve Finding",
        "category": "Findings",
        "description": "Mark findings as resolved.",
    },
    {
        "name": "finding:manage",
        "display_name": "Manage Findings",
        "category": "Findings",
        "description": "Full finding administration.",
    },

    # ========================================================
    # Reports
    # ========================================================

    {
        "name": "report:create",
        "display_name": "Create Report",
        "category": "Reports",
        "description": "Create reports.",
    },
    {
        "name": "report:read",
        "display_name": "View Report",
        "category": "Reports",
        "description": "View reports.",
    },
    {
        "name": "report:update",
        "display_name": "Update Report",
        "category": "Reports",
        "description": "Modify reports.",
    },
    {
        "name": "report:delete",
        "display_name": "Delete Report",
        "category": "Reports",
        "description": "Delete reports.",
    },
    {
        "name": "report:list",
        "display_name": "List Reports",
        "category": "Reports",
        "description": "View all reports.",
    },
    {
        "name": "report:export",
        "display_name": "Export Report",
        "category": "Reports",
        "description": "Export reports.",
    },
    {
        "name": "report:share",
        "display_name": "Share Report",
        "category": "Reports",
        "description": "Share reports.",
    },
    {
        "name": "report:manage",
        "display_name": "Manage Reports",
        "category": "Reports",
        "description": "Full report administration.",
    },


    # ========================================================
    # Compliance
    # ========================================================

    {
        "name": "compliance:create",
        "display_name": "Create Compliance",
        "category": "Compliance",
        "description": "Create compliance policies.",
    },
    {
        "name": "compliance:read",
        "display_name": "View Compliance",
        "category": "Compliance",
        "description": "View compliance information.",
    },
    {
        "name": "compliance:update",
        "display_name": "Update Compliance",
        "category": "Compliance",
        "description": "Modify compliance policies.",
    },
    {
        "name": "compliance:delete",
        "display_name": "Delete Compliance",
        "category": "Compliance",
        "description": "Delete compliance policies.",
    },
    {
        "name": "compliance:manage",
        "display_name": "Manage Compliance",
        "category": "Compliance",
        "description": "Full compliance administration.",
    },

    # ========================================================
    # Policies
    # ========================================================

    {
        "name": "policy:create",
        "display_name": "Create Policy",
        "category": "Policies",
        "description": "Create policies.",
    },
    {
        "name": "policy:read",
        "display_name": "View Policy",
        "category": "Policies",
        "description": "View policies.",
    },
    {
        "name": "policy:update",
        "display_name": "Update Policy",
        "category": "Policies",
        "description": "Modify policies.",
    },
    {
        "name": "policy:delete",
        "display_name": "Delete Policy",
        "category": "Policies",
        "description": "Delete policies.",
    },
    {
        "name": "policy:manage",
        "display_name": "Manage Policies",
        "category": "Policies",
        "description": "Full policy administration.",
    },

    # ========================================================
    # API Keys
    # ========================================================

    {
        "name": "api-key:create",
        "display_name": "Create API Key",
        "category": "API Keys",
        "description": "Create API keys.",
    },
    {
        "name": "api-key:read",
        "display_name": "View API Key",
        "category": "API Keys",
        "description": "View API keys.",
    },
    {
        "name": "api-key:delete",
        "display_name": "Delete API Key",
        "category": "API Keys",
        "description": "Delete API keys.",
    },
    {
        "name": "api-key:manage",
        "display_name": "Manage API Keys",
        "category": "API Keys",
        "description": "Full API key management.",
    },

    # ========================================================
    # Integrations
    # ========================================================

    {
        "name": "integration:create",
        "display_name": "Create Integration",
        "category": "Integrations",
        "description": "Create integrations.",
    },
    {
        "name": "integration:read",
        "display_name": "View Integration",
        "category": "Integrations",
        "description": "View integrations.",
    },
    {
        "name": "integration:update",
        "display_name": "Update Integration",
        "category": "Integrations",
        "description": "Modify integrations.",
    },
    {
        "name": "integration:delete",
        "display_name": "Delete Integration",
        "category": "Integrations",
        "description": "Delete integrations.",
    },
    {
        "name": "integration:manage",
        "display_name": "Manage Integrations",
        "category": "Integrations",
        "description": "Full integration management.",
    },

    # ========================================================
    # Notifications
    # ========================================================

    {
        "name": "notification:send",
        "display_name": "Send Notifications",
        "category": "Notifications",
        "description": "Send notifications.",
    },
    {
        "name": "notification:manage",
        "display_name": "Manage Notifications",
        "category": "Notifications",
        "description": "Manage notification channels.",
    },

    # ========================================================
    # Audit Logs
    # ========================================================

    {
        "name": "audit:read",
        "display_name": "View Audit Logs",
        "category": "Audit",
        "description": "View audit logs.",
    },
    {
        "name": "audit:export",
        "display_name": "Export Audit Logs",
        "category": "Audit",
        "description": "Export audit logs.",
    },

    # ========================================================
    # Settings
    # ========================================================

    {
        "name": "settings:read",
        "display_name": "View Settings",
        "category": "Settings",
        "description": "View platform settings.",
    },
    {
        "name": "settings:update",
        "display_name": "Update Settings",
        "category": "Settings",
        "description": "Modify platform settings.",
    },

    # ========================================================
    # PQC
    # ========================================================

    {
        "name": "pqc:view",
        "display_name": "View PQC",
        "category": "Post Quantum Cryptography",
        "description": "View PQC dashboard.",
    },
    {
        "name": "pqc:scan",
        "display_name": "Run PQC Scan",
        "category": "Post Quantum Cryptography",
        "description": "Run PQC assessments.",
    },
    {
        "name": "pqc:recommend",
        "display_name": "View PQC Recommendations",
        "category": "Post Quantum Cryptography",
        "description": "Access migration recommendations.",
    },
    {
        "name": "pqc:manage",
        "display_name": "Manage PQC",
        "category": "Post Quantum Cryptography",
        "description": "Manage PQC configuration.",
    },

    # ========================================================
    # AI
    # ========================================================

    {
        "name": "ai:chat",
        "display_name": "AI Chat",
        "category": "Artificial Intelligence",
        "description": "Use AI assistant.",
    },
    {
        "name": "ai:recommend",
        "display_name": "AI Recommendations",
        "category": "Artificial Intelligence",
        "description": "Receive AI recommendations.",
    },
    {
        "name": "ai:triage",
        "display_name": "AI Triage",
        "category": "Artificial Intelligence",
        "description": "AI-assisted finding triage.",
    },
    {
        "name": "ai:manage",
        "display_name": "Manage AI",
        "category": "Artificial Intelligence",
        "description": "Manage AI services.",
    },

    # ========================================================
    # System
    # ========================================================

    {
        "name": "*",
        "display_name": "Super Administrator",
        "category": "System",
        "description": "Full unrestricted access.",
    },

]

async def seed_permissions(
    db: AsyncSession,
) -> list[Permission]:
    """
    Seed all built-in permissions.

    Existing permissions are updated.
    Missing permissions are created.

    Safe to execute multiple times.
    """

    logger.info("Seeding permissions...")

    permissions: list[Permission] = []

    for item in PERMISSIONS:

        result = await db.execute(
            select(Permission).where(
                Permission.name == item["name"]
            )
        )

        permission = result.scalar_one_or_none()

        if permission is None:

            permission = Permission(
                name=item["name"],
                display_name=item["display_name"],
                description=item["description"],
                category=item["category"],
                system_permission=True,
                enabled=True,
            )

            db.add(permission)

        else:

            permission.display_name = item["display_name"]
            permission.description = item["description"]
            permission.category = item["category"]
            permission.system_permission = True
            permission.enabled = True

        permissions.append(permission)

    await db.commit()

    logger.info(
        "Seeded %d permissions.",
        len(PERMISSIONS),
    )

    return permissions