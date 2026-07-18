"""
QShield Enterprise
==================

Integration Manager.

Responsibilities:

- Integration registration
- Provider lifecycle management
- Connection orchestration
- Health monitoring
- Runtime integration discovery
- External service coordination

Integrates with:

- Quantum Providers
- Cloud Providers
- Security Platforms
- Storage Systems
- Identity Providers

"""

from __future__ import annotations


import logging


from typing import Any



from app.integrations.base import BaseIntegration
from app.integrations.base import IntegrationConfig



logger = logging.getLogger(__name__)



# ============================================================
# Integration Registry
# ============================================================


class IntegrationManager:
    """
    Central integration controller.

    Maintains all external
    service connections.

    """



    def __init__(
        self,
    ):

        self.integrations: dict[
            str,
            BaseIntegration
        ] = {}



    # --------------------------------------------------------
    # Register Integration
    # --------------------------------------------------------


    def register(
        self,
        name: str,
        integration: BaseIntegration,
    ):
        """
        Register external provider.
        """

        self.integrations[name] = integration



        logger.info(

            "Integration registered: %s",

            name,

        )



    # --------------------------------------------------------
    # Remove Integration
    # --------------------------------------------------------


    def unregister(
        self,
        name: str,
    ):
        """
        Remove integration.
        """

        self.integrations.pop(

            name,

            None

        )



    # --------------------------------------------------------
    # Retrieve Integration
    # --------------------------------------------------------


    def get(
        self,
        name: str,
    ) -> BaseIntegration | None:
        """
        Retrieve provider.
        """

        return self.integrations.get(

            name

        )



    # --------------------------------------------------------
    # Initialize All
    # --------------------------------------------------------


    async def initialize_all(
        self,
    ) -> dict[str, bool]:
        """
        Initialize registered providers.
        """

        results = {}



        for name, integration in self.integrations.items():

            results[name] = await integration.initialize()



        return results



    # --------------------------------------------------------
    # Shutdown All
    # --------------------------------------------------------


    async def shutdown_all(
        self,
    ):
        """
        Disconnect all providers.
        """

        for name, integration in self.integrations.items():

            try:

                await integration.disconnect()



            except Exception as exc:

                logger.exception(

                    "Failed disconnecting %s: %s",

                    name,

                    exc,

                )



    # --------------------------------------------------------
    # Health Monitoring
    # --------------------------------------------------------


    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Check all integrations.
        """

        health = {}



        for name, integration in self.integrations.items():

            try:

                health[name] = await integration.health_check()



            except Exception as exc:

                health[name] = {

                    "status":

                        "error",


                    "error":

                        str(exc),

                }



        return health



    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------


    def status(
        self,
    ) -> dict[str, Any]:
        """
        Integration registry status.
        """

        return {

            name:

                integration.metadata()

            for name, integration

            in self.integrations.items()

        }



    # --------------------------------------------------------
    # Enabled Providers
    # --------------------------------------------------------


    def enabled_integrations(
        self,
    ) -> list[str]:
        """
        Return active integrations.
        """

        return [

            name

            for name, integration

            in self.integrations.items()

            if integration.config.enabled

        ]



# ============================================================
# Global Manager
# ============================================================


integration_manager = IntegrationManager()



# ============================================================
# Lifecycle Helpers
# ============================================================


async def initialize_integrations():
    """
    Application startup hook.
    """

    return await integration_manager.initialize_all()



async def shutdown_integrations():
    """
    Application shutdown hook.
    """

    await integration_manager.shutdown_all()



async def integrations_health():
    """
    External health endpoint.
    """

    return await integration_manager.health_check()