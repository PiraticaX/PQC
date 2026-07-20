"""
QShield Enterprise
==================

Policies API

Policy-Based Access Control (PBAC) Management Endpoints.

Responsibilities:

- Policy creation
- Policy retrieval
- Policy updates
- Policy deletion
- Policy evaluation
- Rule management
- Access governance

Integrates with:

- Policy Service
- Permission Service
- Role Service
- Audit Service

"""

from __future__ import annotations


import logging


from typing import Any


from uuid import UUID


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status


from pydantic import BaseModel


from sqlalchemy.orm import Session


from app.core.database import get_db


from app.services.policy_service import PolicyService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/policies",

)



# ============================================================
# Request Schemas
# ============================================================


class PolicyCreateRequest(
    BaseModel,
):
    """
    Policy creation payload.
    """

    name: str

    description: str | None = None

    resource: str

    action: str

    effect: str = "allow"

    rules: dict[str, Any] | None = None



class PolicyUpdateRequest(
    BaseModel,
):
    """
    Policy update payload.
    """

    name: str | None = None

    description: str | None = None

    effect: str | None = None

    rules: dict[str, Any] | None = None

    is_active: bool | None = None



class PolicyEvaluationRequest(
    BaseModel,
):
    """
    Policy evaluation payload.
    """

    user_id: UUID

    resource: str

    action: str

    context: dict[str, Any] | None = None



# ============================================================
# Policy Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_policy(
    request: PolicyCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Create access policy.
    """

    service = PolicyService(
        db
    )


    try:

        return await service.create_policy(

            name=request.name,

            description=request.description,

            resource=request.resource,

            action=request.action,

            effect=request.effect,

            rules=request.rules,

        )


    except Exception as exc:

        logger.exception(
            "Policy creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_policies(
    db: Session = Depends(
        get_db
    ),
):
    """
    List policies.
    """

    service = PolicyService(
        db
    )


    return await service.list_policies()



@router.get(
    "/{policy_id}",
)
async def get_policy(
    policy_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve policy.
    """

    service = PolicyService(
        db
    )


    policy = await service.get_policy(

        policy_id

    )


    if not policy:

        raise HTTPException(

            status_code=404,

            detail="Policy not found.",

        )


    return policy



@router.put(
    "/{policy_id}",
)
async def update_policy(
    policy_id: UUID,
    request: PolicyUpdateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Update policy.
    """

    service = PolicyService(
        db
    )


    return await service.update_policy(

        policy_id=policy_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{policy_id}",
)
async def delete_policy(
    policy_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete policy.
    """

    service = PolicyService(
        db
    )


    return await service.delete_policy(

        policy_id

    )



# ============================================================
# Policy Evaluation Engine
# ============================================================


@router.post(
    "/evaluate",
)
async def evaluate_policy(
    request: PolicyEvaluationRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Evaluate access decision.

    Flow:

    User Request
          |
          v
    Policy Engine
          |
          v
    Allow / Deny Decision

    """

    service = PolicyService(
        db
    )


    return await service.evaluate_policy(

        user_id=request.user_id,

        resource=request.resource,

        action=request.action,

        context=request.context,

    )



@router.post(
    "/check-access",
)
async def check_access(
    request: PolicyEvaluationRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Access authorization check.
    """

    service = PolicyService(
        db
    )


    return await service.check_access(

        user_id=request.user_id,

        resource=request.resource,

        action=request.action,

    )



# ============================================================
# Policy Rules
# ============================================================


@router.get(
    "/{policy_id}/rules",
)
async def get_policy_rules(
    policy_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve policy rules.
    """

    service = PolicyService(
        db
    )


    return await service.get_policy_rules(

        policy_id

    )



@router.post(
    "/{policy_id}/activate",
)
async def activate_policy(
    policy_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Activate policy.
    """

    service = PolicyService(
        db
    )


    return await service.activate_policy(

        policy_id

    )



@router.post(
    "/{policy_id}/disable",
)
async def disable_policy(
    policy_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Disable policy.
    """

    service = PolicyService(
        db
    )


    return await service.disable_policy(

        policy_id

    )



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics/summary",
)
async def policy_statistics(
    db: Session = Depends(
        get_db
    ),
):
    """
    Policy analytics.
    """

    service = PolicyService(
        db
    )


    return await service.policy_statistics()
