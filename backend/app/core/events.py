"""
QShield Enterprise
==================

Internal Event Infrastructure.

Responsibilities:

- Application event publishing
- Event subscription management
- Security event handling
- Audit event propagation
- Async event processing
- Service-to-service communication

Integrates with:

- Audit Service
- Queue Service
- Scheduler
- Security Monitoring
- Background Workers

"""

from __future__ import annotations


import asyncio


import logging


from datetime import datetime
from datetime import timezone


from dataclasses import dataclass
from dataclasses import field


from typing import Any
from typing import Awaitable
from typing import Callable



from app.core.constants import EVENT_SECURITY_ALERT



logger = logging.getLogger(__name__)



# ============================================================
# Event Model
# ============================================================


@dataclass
class Event:
    """
    Internal application event.

    Contains:

    - Event type
    - Source
    - Payload
    - Timestamp
    - Metadata

    """

    event_type: str

    source: str

    payload: dict[str, Any] = field(

        default_factory=dict

    )

    timestamp: datetime = field(

        default_factory=lambda:

            datetime.now(

                timezone.utc

            )

    )

    metadata: dict[str, Any] = field(

        default_factory=dict

    )



# ============================================================
# Event Handlers
# ============================================================


EventHandler = Callable[

    [Event],

    Awaitable[None]

]



# ============================================================
# Event Bus
# ============================================================


class EventBus:
    """
    Async internal event bus.

    Provides:

    - Publish events
    - Subscribe handlers
    - Async execution

    """

    def __init__(
        self,
    ):

        self.handlers: dict[str, list[EventHandler]] = {}



    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ):
        """
        Register event handler.
        """

        if event_type not in self.handlers:

            self.handlers[event_type] = []



        self.handlers[event_type].append(

            handler

        )



        logger.info(

            "Event handler registered: %s",

            event_type,

        )



    async def publish(
        self,
        event: Event,
    ):
        """
        Publish event.

        All registered handlers execute
        asynchronously.

        """

        handlers = self.handlers.get(

            event.event_type,

            []

        )



        if not handlers:

            logger.debug(

                "No handlers for event: %s",

                event.event_type,

            )

            return



        tasks = [

            handler(event)

            for handler in handlers

        ]



        await asyncio.gather(

            *tasks,

            return_exceptions=True,

        )



    def clear(
        self,
    ):
        """
        Remove all handlers.
        """

        self.handlers.clear()



# ============================================================
# Global Event Bus
# ============================================================


event_bus = EventBus()



# ============================================================
# Event Publisher Helpers
# ============================================================


async def publish_event(
    event_type: str,
    source: str,
    payload: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
):
    """
    Publish application event.

    Example:

        await publish_event(
            "user.created",
            "user_service",
            {
                "user_id": id
            }
        )

    """

    event = Event(

        event_type=event_type,

        source=source,

        payload=payload or {},

        metadata=metadata or {},

    )


    await event_bus.publish(

        event

    )



# ============================================================
# Security Events
# ============================================================


async def publish_security_event(
    event: str,
    details: dict[str, Any],
):
    """
    Publish security event.

    Used for:

    - Login failures
    - Permission violations
    - Key operations
    - Threat detection

    """

    await publish_event(

        event_type=EVENT_SECURITY_ALERT,

        source="security_engine",

        payload={

            "event":

                event,


            "details":

                details,

        }

    )



# ============================================================
# Audit Event Wrapper
# ============================================================


async def publish_audit_event(
    action: str,
    actor: str,
    resource: str,
    metadata: dict[str, Any] | None = None,
):
    """
    Publish audit event.

    """

    await publish_event(

        event_type="audit.record",

        source="audit_system",

        payload={

            "action":

                action,


            "actor":

                actor,


            "resource":

                resource,

        },

        metadata=metadata,

    )



# ============================================================
# Default Handlers
# ============================================================


async def logging_event_handler(
    event: Event,
):
    """
    Default event logger.
    """

    logger.info(

        "Event received: %s",

        {

            "type":

                event.event_type,


            "source":

                event.source,


            "payload":

                event.payload,

        }

    )



# Register default handler

event_bus.subscribe(

    "*",

    logging_event_handler,

)



# ============================================================
# Event Health
# ============================================================


def event_bus_health() -> dict[str, Any]:
    """
    Event system health.
    """

    return {

        "status":

            "healthy",


        "registered_events":

            len(

                event_bus.handlers

            ),

    }