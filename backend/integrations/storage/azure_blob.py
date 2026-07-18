"""
QShield Enterprise
==================

Azure Blob Storage Integration.

Responsibilities:

- Blob upload
- Blob download
- Blob deletion
- Secure artifact storage
- Backup storage support
- Azure storage monitoring

Integrates with:

- Azure Blob Storage
- Storage Manager
- Backup Worker
- Report Worker

"""

from __future__ import annotations


import logging


from typing import Any



from app.integrations.storage.storage_manager import StorageProvider



logger = logging.getLogger(__name__)



# ============================================================
# Optional Azure Imports
# ============================================================


try:

    from azure.storage.blob import (

        BlobServiceClient,

    )


    from azure.identity import (

        DefaultAzureCredential,

    )


    AZURE_STORAGE_AVAILABLE = True



except ImportError:

    AZURE_STORAGE_AVAILABLE = False



# ============================================================
# Azure Blob Provider
# ============================================================


class AzureBlobStorageProvider(
    StorageProvider
):
    """
    Azure Blob Storage connector.

    Supports:

    - Upload
    - Download
    - Delete
    - Metadata

    """



    def __init__(
        self,
        account_url: str | None = None,
        container: str = "qshield-data",
        connection_string: str | None = None,
    ):

        self.account_url = account_url

        self.container = container

        self.connection_string = connection_string


        self.client = None

        self.container_client = None


        self.connected = False



    # --------------------------------------------------------
    # Connect
    # --------------------------------------------------------


    async def connect(
        self,
    ) -> bool:
        """
        Initialize Azure Blob client.
        """

        if not AZURE_STORAGE_AVAILABLE:

            logger.warning(

                "Azure Blob SDK unavailable. Running mock mode."

            )


            self.connected = True


            return True



        try:

            if self.connection_string:

                self.client = (

                    BlobServiceClient

                    .from_connection_string(

                        self.connection_string

                    )

                )


            else:

                self.client = BlobServiceClient(

                    account_url=self.account_url,

                    credential=

                        DefaultAzureCredential(),

                )



            self.container_client = (

                self.client

                .get_container_client(

                    self.container

                )

            )


            self.connected = True



            logger.info(

                "Connected to Azure Blob container %s",

                self.container,

            )



            return True



        except Exception as exc:

            logger.exception(

                "Azure Blob connection failed: %s",

                exc,

            )


            return False



    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------


    async def upload(
        self,
        path: str,
        data: bytes,
    ) -> dict[str, Any]:
        """
        Upload blob.

        """

        if not self.connected:

            await self.connect()



        if not AZURE_STORAGE_AVAILABLE:

            return {

                "provider":

                    "azure_blob",


                "path":

                    path,


                "status":

                    "simulated",

            }



        blob = (

            self.container_client

            .get_blob_client(

                path

            )

        )



        blob.upload_blob(

            data,

            overwrite=True,

        )



        return {

            "status":

                "uploaded",


            "container":

                self.container,


            "path":

                path,

        }



    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------


    async def download(
        self,
        path: str,
    ) -> bytes:
        """
        Download blob.
        """

        if not self.connected:

            await self.connect()



        if not AZURE_STORAGE_AVAILABLE:

            return b""



        blob = (

            self.container_client

            .get_blob_client(

                path

            )

        )



        downloader = blob.download_blob()



        return downloader.readall()



    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------


    async def delete(
        self,
        path: str,
    ) -> bool:
        """
        Delete blob.
        """

        if not self.connected:

            await self.connect()



        if not AZURE_STORAGE_AVAILABLE:

            return True



        blob = (

            self.container_client

            .get_blob_client(

                path

            )

        )



        blob.delete_blob()



        return True



    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------


    async def metadata(
        self,
        path: str,
    ) -> dict[str, Any]:
        """
        Retrieve blob metadata.
        """

        if not AZURE_STORAGE_AVAILABLE:

            return {

                "path":

                    path,


                "mode":

                    "simulation",

            }



        blob = (

            self.container_client

            .get_blob_client(

                path

            )

        )



        properties = blob.get_blob_properties()



        return {

            "size":

                properties.size,


            "created":

                properties.creation_time,


            "modified":

                properties.last_modified,

        }



    # --------------------------------------------------------
    # Health
    # --------------------------------------------------------


    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Azure Blob health status.
        """

        return {

            "provider":

                "Azure Blob Storage",


            "connected":

                self.connected,


            "container":

                self.container,


            "sdk_available":

                AZURE_STORAGE_AVAILABLE,

        }



# ============================================================
# Factory
# ============================================================


def create_azure_blob_provider(
    account_url: str | None = None,
    container: str = "qshield-data",
):
    """
    Create Azure Blob provider.
    """

    return AzureBlobStorageProvider(

        account_url=account_url,

        container=container,

    )