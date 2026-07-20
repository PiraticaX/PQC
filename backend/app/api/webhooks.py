"""
QShield Enterprise
==================

Webhooks API

Webhook Event Delivery Management Endpoints.

Responsibilities:

- Webhook registration
- Webhook lifecycle management
- Event subscription
- Secure delivery testing
- Retry management
- Delivery history tracking

Integrates with:

- Webhook Service
- Event Service
- Integration Service
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


from app.services.webhook_service import WebhookService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/webhooks",

)



# ============================================================
# Request Schemas
# ============================================================


class WebhookCreateRequest(
    BaseModel,
):
    """
    Webhook creation payload.
    """

    name: str

    endpoint_url: str

    events: list[str]



class WebhookUpdateRequest(
    BaseModel,
):
    """
    Webhook update payload.
    """

    endpoint_url: str | None = None

    events: list[str] | None = None

    status: str | None = None



class WebhookTestRequest(
    BaseModel,
):
    """
    Webhook test payload.
    """

    event: str

    payload: dict[str, Any]



# ============================================================
# Webhook Lifecycle
# ============================================================


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_webhook(
    organization_id: UUID,
    request: WebhookCreateRequest,
    db: Session = Depends(
        get_db
    ),
) -> dict[str, Any]:
    """
    Register webhook endpoint.
    """

    service = WebhookService(
        db
    )


    try:

        return await service.create_webhook(

            organization_id=organization_id,

            name=request.name,

            endpoint_url=
                request.endpoint_url,

            events=request.events,

        )


    except Exception as exc:

        logger.exception(
            "Webhook creation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



@router.get(
    "",
)
async def list_webhooks(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    List organization webhooks.
    """

    service = WebhookService(
        db
    )


    return await service.get_organization_webhooks(

        organization_id

    )



@router.get(
    "/{webhook_id}",
)
async def get_webhook(
    webhook_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve webhook.
    """

    service = WebhookService(
        db
    )


    webhook = await service.get_webhook(

        webhook_id

    )


    if not webhook:

        raise HTTPException(

            status_code=404,

            detail="Webhook not found.",

        )


    return webhook



@router.put(
    "/{webhook_id}",
)
async def update_webhook(
    webhook_id: UUID,
    request: WebhookUpdateRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Update webhook.
    """

    service = WebhookService(
        db
    )


    return await service.update_webhook(

        webhook_id=webhook_id,

        updates=request.model_dump(

            exclude_none=True

        ),

    )



@router.delete(
    "/{webhook_id}",
)
async def delete_webhook(
    webhook_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Delete webhook.
    """

    service = WebhookService(
        db
    )


    return await service.delete_webhook(

        webhook_id

    )



# ============================================================
# Delivery Operations
# ============================================================


@router.post(
    "/{webhook_id}/test",
)
async def test_webhook(
    webhook_id: UUID,
    request: WebhookTestRequest,
    db: Session = Depends(
        get_db
    ),
):
    """
    Test webhook delivery.

    Used for:

    - Connector verification
    - Endpoint validation

    """

    service = WebhookService(
        db
    )


    return await service.send_webhook(

        webhook_id=webhook_id,

        event=request.event,

        payload=request.payload,

    )



@router.post(
    "/{webhook_id}/retry/{event_id}",
)
async def retry_webhook_delivery(
    webhook_id: UUID,
    event_id: str,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retry failed webhook delivery.
    """

    service = WebhookService(
        db
    )


    return await service.retry_delivery(

        webhook_id=webhook_id,

        event_id=event_id,

    )



# ============================================================
# Delivery History
# ============================================================


@router.get(
    "/{webhook_id}/history",
)
async def webhook_history(
    webhook_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Retrieve webhook delivery history.
    """

    service = WebhookService(
        db
    )


    return await service.get_delivery_history(

        webhook_id

    )



# ============================================================
# Security
# ============================================================


@router.post(
    "/validate-signature",
)
async def validate_signature(
    payload: dict[str, Any],
    signature: str,
    secret: str,
    db: Session = Depends(
        get_db
    ),
):
    """
    Validate webhook HMAC signature.
    """

    service = WebhookService(
        db
    )


    valid = await service.validate_signature(

        payload=payload,

        signature=signature,

        secret=secret,

    )


    return {

        "valid":

            valid,

    }



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics/summary",
)
async def webhook_statistics(
    organization_id: UUID,
    db: Session = Depends(
        get_db
    ),
):
    """
    Webhook analytics.
    """

    service = WebhookService(
        db
    )


    return await service.generate_webhook_report(

        organization_id

    )
