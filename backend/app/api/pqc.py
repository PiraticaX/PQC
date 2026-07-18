"""
QShield Enterprise
==================

PQC API

Post Quantum Cryptography Management Endpoints.

Responsibilities:

- PQC readiness assessment
- Post quantum key generation
- PQC encryption/decryption
- Digital signatures
- Signature verification
- Algorithm discovery
- Migration readiness

Integrates with:

- PQC Service
- Key Management Service
- Encryption Service
- Audit Service
- Compliance Service

"""

from __future__ import annotations


import logging


from typing import Any


from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException


from pydantic import BaseModel


from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import get_db


from app.services.pqc_service import PQCService



logger = logging.getLogger(__name__)



# ============================================================
# Router
# ============================================================


router = APIRouter(

    prefix="/pqc",

)



# ============================================================
# Request Schemas
# ============================================================


class PQCKeyGenerationRequest(
    BaseModel,
):
    """
    PQC key generation payload.
    """

    algorithm: str = "CRYSTALS-KYBER"

    security_level: int = 3



class PQCEncryptRequest(
    BaseModel,
):
    """
    PQC encryption payload.
    """

    plaintext: str

    key_id: str



class PQCDecryptRequest(
    BaseModel,
):
    """
    PQC decryption payload.
    """

    ciphertext: str

    key_id: str



class PQCSignRequest(
    BaseModel,
):
    """
    PQC signature payload.
    """

    message: str

    private_key_id: str



class PQCVerifyRequest(
    BaseModel,
):
    """
    PQC verification payload.
    """

    message: str

    signature: str

    public_key_id: str



class PQCReadinessRequest(
    BaseModel,
):
    """
    Migration readiness payload.
    """

    organization: str

    systems: list[str]



# ============================================================
# PQC Status
# ============================================================


@router.get(
    "/status",
)
async def pqc_status():
    """
    Retrieve PQC system status.
    """

    return {

        "pqc":

            {

                "status":

                    "operational",


                "quantum_safe":

                    True,


                "algorithms":

                    [

                        "CRYSTALS-KYBER",

                        "CRYSTALS-DILITHIUM",

                    ],

            }

    }



@router.get(
    "/algorithms",
)
async def supported_algorithms():
    """
    List supported PQC algorithms.
    """

    service = PQCService()


    return await service.list_algorithms()



# ============================================================
# Key Operations
# ============================================================


@router.post(
    "/keys/generate",
)
async def generate_pqc_keys(
    request: PQCKeyGenerationRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Generate post quantum key pair.
    """

    service = PQCService(
        db
    )


    try:

        return await service.generate_keys(

            algorithm=request.algorithm,

            security_level=
                request.security_level,

        )


    except Exception as exc:

        logger.exception(
            "PQC key generation failed."
        )


        raise HTTPException(

            status_code=400,

            detail=str(exc),

        )



# ============================================================
# Encryption
# ============================================================


@router.post(
    "/encrypt",
)
async def pqc_encrypt(
    request: PQCEncryptRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Encrypt using PQC mechanism.
    """

    service = PQCService(
        db
    )


    return await service.encrypt(

        plaintext=request.plaintext,

        key_id=request.key_id,

    )



@router.post(
    "/decrypt",
)
async def pqc_decrypt(
    request: PQCDecryptRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Decrypt PQC ciphertext.
    """

    service = PQCService(
        db
    )


    return await service.decrypt(

        ciphertext=request.ciphertext,

        key_id=request.key_id,

    )



# ============================================================
# Digital Signatures
# ============================================================


@router.post(
    "/sign",
)
async def pqc_sign(
    request: PQCSignRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Generate PQC digital signature.
    """

    service = PQCService(
        db
    )


    return await service.sign(

        message=request.message,

        private_key_id=
            request.private_key_id,

    )



@router.post(
    "/verify",
)
async def pqc_verify(
    request: PQCVerifyRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Verify PQC signature.
    """

    service = PQCService(
        db
    )


    return await service.verify(

        message=request.message,

        signature=request.signature,

        public_key_id=
            request.public_key_id,

    )



# ============================================================
# Migration Readiness
# ============================================================


@router.post(
    "/readiness",
)
async def pqc_readiness(
    request: PQCReadinessRequest,
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Assess quantum migration readiness.

    Evaluates:

    - Cryptographic inventory
    - Vulnerable algorithms
    - Migration priority
    - PQC adoption roadmap

    """

    service = PQCService(
        db
    )


    return await service.assess_readiness(

        organization=
            request.organization,

        systems=
            request.systems,

    )



@router.get(
    "/migration-report",
)
async def migration_report(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Generate PQC migration report.
    """

    service = PQCService(
        db
    )


    return await service.generate_migration_report()



# ============================================================
# Analytics
# ============================================================


@router.get(
    "/statistics",
)
async def pqc_statistics(
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    PQC analytics.
    """

    service = PQCService(
        db
    )


    return await service.statistics()



@router.get(
    "/health",
)
async def pqc_health():
    """
    PQC service health.
    """

    return {

        "pqc_service":

            {

                "status":

                    "healthy",


                "quantum_readiness":

                    "enabled",


                "migration_engine":

                    "available",

            }

    }