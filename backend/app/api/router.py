"""
QShield Enterprise
==================

API Router

Central FastAPI Route Registration.

Responsibilities:

- Register all API modules
- Provide versioned API structure
- Manage route namespaces
- Maintain API organization

"""

from fastapi import APIRouter


# ============================================================
# Import API Modules
# ============================================================

from app.api import health

from app.api import auth
from app.api import users
from app.api import organizations
from app.api import sessions


from app.api import permissions
from app.api import roles
from app.api import policies


from app.api import api_keys
from app.api import integrations
from app.api import webhooks


from app.api import events
from app.api import queue
from app.api import scheduler


from app.api import storage
from app.api import backups


from app.api import encryption
from app.api import keys


from app.api import analytics
from app.api import search


from app.api import assets
from app.api import scans
from app.api import findings
from app.api import risks
from app.api import reports
from app.api import compliance
from app.api import pqc



# ============================================================
# Root Router
# ============================================================


api_router = APIRouter()



# ============================================================
# API Version
# ============================================================


API_PREFIX = "/api/v1"



# ============================================================
# Health
# ============================================================


api_router.include_router(

    health.router,

    prefix=API_PREFIX,

    tags=[
        "Health"
    ],

)



# ============================================================
# Identity
# ============================================================


api_router.include_router(

    auth.router,

    prefix=API_PREFIX,

    tags=[
        "Authentication"
    ],

)


api_router.include_router(

    users.router,

    prefix=API_PREFIX,

    tags=[
        "Users"
    ],

)


api_router.include_router(

    organizations.router,

    prefix=API_PREFIX,

    tags=[
        "Organizations"
    ],

)


api_router.include_router(

    sessions.router,

    prefix=API_PREFIX,

    tags=[
        "Sessions"
    ],

)



# ============================================================
# Authorization
# ============================================================


api_router.include_router(

    permissions.router,

    prefix=API_PREFIX,

    tags=[
        "Permissions"
    ],

)


api_router.include_router(

    roles.router,

    prefix=API_PREFIX,

    tags=[
        "Roles"
    ],

)


api_router.include_router(

    policies.router,

    prefix=API_PREFIX,

    tags=[
        "Policies"
    ],

)



# ============================================================
# Integrations
# ============================================================


api_router.include_router(

    api_keys.router,

    prefix=API_PREFIX,

    tags=[
        "API Keys"
    ],

)


api_router.include_router(

    integrations.router,

    prefix=API_PREFIX,

    tags=[
        "Integrations"
    ],

)


api_router.include_router(

    webhooks.router,

    prefix=API_PREFIX,

    tags=[
        "Webhooks"
    ],

)



# ============================================================
# Platform Operations
# ============================================================


api_router.include_router(

    events.router,

    prefix=API_PREFIX,

    tags=[
        "Events"
    ],

)


api_router.include_router(

    queue.router,

    prefix=API_PREFIX,

    tags=[
        "Queue"
    ],

)


api_router.include_router(

    scheduler.router,

    prefix=API_PREFIX,

    tags=[
        "Scheduler"
    ],

)



# ============================================================
# Data Management
# ============================================================


api_router.include_router(

    storage.router,

    prefix=API_PREFIX,

    tags=[
        "Storage"
    ],

)


api_router.include_router(

    backups.router,

    prefix=API_PREFIX,

    tags=[
        "Backups"
    ],

)



# ============================================================
# Cryptography
# ============================================================


api_router.include_router(

    encryption.router,

    prefix=API_PREFIX,

    tags=[
        "Encryption"
    ],

)


api_router.include_router(

    keys.router,

    prefix=API_PREFIX,

    tags=[
        "Key Management"
    ],

)



# ============================================================
# Intelligence
# ============================================================


api_router.include_router(

    analytics.router,

    prefix=API_PREFIX,

    tags=[
        "Analytics"
    ],

)


api_router.include_router(

    search.router,

    prefix=API_PREFIX,

    tags=[
        "Search"
    ],

)



# ============================================================
# Security Operations
# ============================================================


api_router.include_router(

    assets.router,

    prefix=API_PREFIX,

    tags=[
        "Assets"
    ],

)


api_router.include_router(

    scans.router,

    prefix=API_PREFIX,

    tags=[
        "Scans"
    ],

)


api_router.include_router(

    findings.router,

    prefix=API_PREFIX,

    tags=[
        "Findings"
    ],

)


api_router.include_router(

    risks.router,

    prefix=API_PREFIX,

    tags=[
        "Risk Management"
    ],

)


api_router.include_router(

    reports.router,

    prefix=API_PREFIX,

    tags=[
        "Reports"
    ],

)


api_router.include_router(

    compliance.router,

    prefix=API_PREFIX,

    tags=[
        "Compliance"
    ],

)


api_router.include_router(

    pqc.router,

    prefix=API_PREFIX,

    tags=[
        "Post Quantum Cryptography"
    ],

)



# ============================================================
# API Metadata
# ============================================================


def get_api_routes() -> list[dict]:
    """
    Return registered API routes.

    Useful for:

    - Documentation
    - Monitoring
    - Debugging

    """

    routes = []


    for route in api_router.routes:

        routes.append(

            {

                "path":

                    route.path,


                "methods":

                    list(
                        route.methods
                    ),

            }

        )


    return routes