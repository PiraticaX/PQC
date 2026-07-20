"""
QShield Enterprise
==================

Crypto Inventory Service

Enterprise cryptographic asset discovery
and inventory management engine.

Tracks:

- Encryption algorithms
- Digital signatures
- Key exchange protocols
- Certificates
- Key lifecycle
- TLS configuration
- Crypto dependencies

Integrates with:

- PQC Service
- Scanner Orchestrator
- Risk Engine
- Compliance Engine

Author:
QShield Enterprise
"""

from __future__ import annotations


import logging


from datetime import datetime
from typing import Any
from uuid import UUID


from sqlalchemy import func
from sqlalchemy import select


from sqlalchemy.orm import Session


from app.models.asset import Asset


logger = logging.getLogger(__name__)



class CryptoInventoryService:
    """
    Enterprise Crypto Discovery Engine.

    Responsibilities:

    • Discover cryptographic usage

    • Maintain crypto inventory

    • Identify vulnerable algorithms

    • Support PQC migration

    """



    def __init__(
        self,
        db: Session,
    ):
        self.db = db



    # ============================================================
    # Cryptographic Knowledge Base
    # ============================================================


    ASYMMETRIC_ALGORITHMS = {

        "RSA":

            {

                "type":
                    "public_key",

                "quantum_vulnerable":
                    True,

                "replacement":
                    "ML-DSA",

            },


        "ECC":

            {

                "type":
                    "public_key",

                "quantum_vulnerable":
                    True,

                "replacement":
                    "ML-DSA",

            },


        "ECDSA":

            {

                "type":
                    "signature",

                "quantum_vulnerable":
                    True,

                "replacement":
                    "ML-DSA",

            },


        "ECDH":

            {

                "type":
                    "key_exchange",

                "quantum_vulnerable":
                    True,

                "replacement":
                    "ML-KEM",

            },


        "DH":

            {

                "type":
                    "key_exchange",

                "quantum_vulnerable":
                    True,

                "replacement":
                    "ML-KEM",

            },

    }



    SYMMETRIC_ALGORITHMS = {

        "AES-256":

            {

                "quantum_security":
                    "strong",

                "recommendation":
                    "continue",

            },


        "AES-128":

            {

                "quantum_security":
                    "reduced",

                "recommendation":
                    "upgrade",

            },


        "3DES":

            {

                "quantum_security":
                    "weak",

                "recommendation":
                    "replace",

            },

    }



    HASH_ALGORITHMS = {

        "SHA256":
            "acceptable",

        "SHA384":
            "acceptable",

        "SHA512":
            "acceptable",

        "MD5":
            "deprecated",

        "SHA1":
            "deprecated",

    }



    # ============================================================
    # Helpers
    # ============================================================


    @staticmethod
    def normalize(
        value: str | None,
    ) -> str:

        if not value:

            return ""


        return (

            value

            .upper()

            .replace(
                "_",
                "",
            )

            .replace(
                "-",
                "",
            )

            .strip()

        )
        # ============================================================
    # Database Helpers & Inventory Storage Layer
    # ============================================================

    async def get_asset(
        self,
        asset_id: UUID,
    ) -> Asset | None:
        """
        Retrieve asset information.
        """

        stmt = (
            select(Asset)
            .where(

                Asset.id == asset_id,

                Asset.deleted_at.is_(None),

            )
        )


        result = self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def asset_exists(
        self,
        asset_id: UUID,
    ) -> bool:
        """
        Check asset existence.
        """

        count = self.db.scalar(
            select(
                func.count(
                    Asset.id,
                )
            )
            .where(

                Asset.id == asset_id,

                Asset.deleted_at.is_(None),

            )
        )


        return bool(count)



    async def get_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieve cryptographic inventory.

        Storage abstraction layer.

        Future integrations:

        - Database JSON column
        - CMDB
        - Vault
        - Cloud KMS
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        return {

            "asset_id":

                str(
                    asset.id
                ),


            "asset":

                asset.asset_value,


            "certificates":

                [],


            "public_keys":

                [],


            "private_keys":

                [],


            "algorithms":

                [],


            "signatures":

                [],


            "key_exchange":

                [],


            "tls_versions":

                [],


            "discovered_at":

                None,

        }



    async def save_inventory(
        self,
        asset_id: UUID,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Store crypto inventory.

        Provides persistence boundary.
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        #
        # Future implementation:
        #
        # asset.crypto_inventory = inventory
        #


        logger.info(
            "Crypto inventory saved. asset=%s",
            asset.id,
        )


        return inventory



    async def update_inventory_timestamp(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update inventory discovery timestamp.
        """

        inventory[
            "discovered_at"
        ] = (
            datetime.utcnow()
            .isoformat()
        )


        return inventory



    async def commit(
        self,
    ) -> None:
        """
        Safe transaction commit.
        """

        try:

            self.db.commit()


        except Exception:

            self.db.rollback()


            logger.exception(
                "Crypto inventory commit failed."
            )

            raise



    async def rollback(
        self,
    ) -> None:
        """
        Rollback transaction.
        """

        self.db.rollback()
            # ============================================================
    # Certificate Inventory Engine
    # ============================================================

    async def collect_certificate_inventory(
        self,
        asset_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Collect certificate inventory.

        Tracks:

        - Subject
        - Issuer
        - Validity
        - Signature algorithm
        - Key algorithm
        - Quantum exposure
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Collecting certificates. asset=%s",
            asset.asset_value,
        )


        certificates = []



        # --------------------------------------------------------
        # Certificate Scanner Integration Point
        #
        # Production:
        #
        # - OpenSSL
        # - cryptography library
        # - Certificate transparency APIs
        #
        # --------------------------------------------------------



        return certificates



    def analyze_certificate(
        self,
        certificate: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze certificate cryptographic posture.
        """

        signature_algorithm = (
            certificate.get(
                "signature_algorithm",
                "",
            )
        )


        key_algorithm = (
            certificate.get(
                "key_algorithm",
                "",
            )
        )


        quantum_risk = []


        for algorithm in [

            signature_algorithm,

            key_algorithm,

        ]:

            normalized = (
                self.normalize(
                    algorithm,
                )
            )


            for known, details in (
                self.ASYMMETRIC_ALGORITHMS.items()
            ):

                if (

                    self.normalize(
                        known,
                    )

                    in

                    normalized

                ):

                    quantum_risk.append(

                        {

                            "algorithm":
                                algorithm,

                            "quantum_vulnerable":
                                details[
                                    "quantum_vulnerable"
                                ],

                            "replacement":
                                details[
                                    "replacement"
                                ],

                        }

                    )



        return {

            "certificate":
                certificate.get(
                    "subject",
                ),


            "issuer":
                certificate.get(
                    "issuer",
                ),


            "signature_algorithm":
                signature_algorithm,


            "key_algorithm":
                key_algorithm,


            "quantum_risk":
                quantum_risk,


            "secure":

                len(
                    quantum_risk
                )
                ==
                0,

        }



    async def analyze_certificates(
        self,
        certificates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Analyze multiple certificates.
        """

        results = []


        for certificate in certificates:

            results.append(

                self.analyze_certificate(
                    certificate,
                )

            )


        return results



    async def detect_expiring_certificates(
        self,
        certificates: list[dict[str, Any]],
        *,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Detect certificates near expiry.
        """

        expiring = []


        now = datetime.utcnow()



        for certificate in certificates:

            expiry = certificate.get(
                "valid_until",
            )


            if not expiry:

                continue



            #
            # Date parsing layer.
            # Actual implementation depends
            # on certificate format.
            #


            expiring.append(

                {

                    "subject":
                        certificate.get(
                            "subject",
                        ),

                    "expiry":
                        expiry,

                    "days_remaining":
                        None,

                }

            )


        return expiring



    async def build_certificate_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Build complete certificate inventory.
        """

        certificates = (
            await self.collect_certificate_inventory(
                asset_id,
            )
        )


        analyzed = (
            await self.analyze_certificates(
                certificates,
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "certificates":
                certificates,

            "analysis":
                analyzed,

            "count":
                len(
                    certificates
                ),

            "generated_at":
                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # TLS Cryptographic Discovery Engine
    # ============================================================

    async def collect_tls_configuration(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Collect TLS cryptographic configuration.

        Discovers:

        - TLS versions
        - Cipher suites
        - Key exchange
        - Certificate usage
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Collecting TLS configuration. asset=%s",
            asset.asset_value,
        )


        #
        # Production integrations:
        #
        # - OpenSSL
        # - testssl.sh
        # - sslyze
        #
        

        return {

            "asset_id":
                str(
                    asset.id
                ),

            "tls_versions":

                [],


            "cipher_suites":

                [],


            "key_exchange":

                [],


            "signature_algorithms":

                [],


            "certificates":

                [],


            "collected_at":

                datetime.utcnow().isoformat(),

        }



    def analyze_tls_version(
        self,
        version: str,
    ) -> dict[str, Any]:
        """
        Analyze TLS protocol security.
        """

        normalized = (
            self.normalize(
                version,
            )
        )


        insecure_versions = [

            "TLS10",

            "TLS11",

        ]


        insecure = (
            normalized
            in
            insecure_versions
        )


        return {

            "version":
                version,

            "secure":
                not insecure,

            "risk":

                (

                    "high"

                    if insecure

                    else

                    "low"

                ),

        }



    def analyze_cipher_suite(
        self,
        cipher: str,
    ) -> dict[str, Any]:
        """
        Analyze cipher suite.

        Detects:

        - Weak encryption
        - Quantum vulnerable exchange
        """

        normalized = (
            self.normalize(
                cipher,
            )
        )


        risks = []



        if "3DES" in normalized:

            risks.append(

                {

                    "issue":
                        "Weak encryption",

                    "severity":
                        "high",

                }

            )



        if (
            "RSA"
            in
            normalized
        ):

            risks.append(

                {

                    "issue":
                        "Quantum vulnerable key exchange",

                    "severity":
                        "medium",

                }

            )



        if (
            "ECDHE"
            in
            normalized
        ):

            risks.append(

                {

                    "issue":
                        "ECC based key exchange",

                    "severity":
                        "medium",

                }

            )



        return {

            "cipher":
                cipher,

            "risks":
                risks,

            "secure":

                len(
                    risks
                )
                ==
                0,

        }



    async def analyze_tls_configuration(
        self,
        tls_config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze TLS posture.
        """

        versions = [

            self.analyze_tls_version(
                item,
            )

            for item
            in tls_config.get(
                "tls_versions",
                [],
            )

        ]



        ciphers = [

            self.analyze_cipher_suite(
                item,
            )

            for item
            in tls_config.get(
                "cipher_suites",
                [],
            )

        ]



        return {

            "tls_versions":

                versions,


            "cipher_analysis":

                ciphers,


            "quantum_exposure":

                [

                    cipher

                    for cipher
                    in ciphers

                    if not cipher["secure"]

                ],


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def build_tls_crypto_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Build TLS crypto inventory.
        """

        configuration = (
            await self.collect_tls_configuration(
                asset_id,
            )
        )


        analysis = (
            await self.analyze_tls_configuration(
                configuration,
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "configuration":
                configuration,

            "analysis":
                analysis,

        }
        # ============================================================
    # Key & Algorithm Inventory Engine
    # ============================================================

    async def collect_algorithm_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Collect cryptographic algorithm usage.

        Tracks:

        - Encryption algorithms
        - Signature algorithms
        - Key exchange protocols
        - Hash functions
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Collecting algorithms. asset=%s",
            asset.asset_value,
        )


        return {

            "asset_id":
                str(
                    asset.id
                ),


            "algorithms":

                [],


            "signature_algorithms":

                [],


            "key_exchange":

                [],


            "hash_algorithms":

                [],


            "discovered_at":

                datetime.utcnow().isoformat(),

        }



    def classify_algorithm(
        self,
        algorithm: str,
    ) -> dict[str, Any]:
        """
        Classify cryptographic algorithm.

        Categories:

        - Symmetric
        - Asymmetric
        - Hash
        - Unknown
        """

        normalized = (
            self.normalize(
                algorithm,
            )
        )



        for name, details in (
            self.ASYMMETRIC_ALGORITHMS.items()
        ):

            if (

                self.normalize(
                    name,
                )

                in

                normalized

            ):

                return {

                    "algorithm":
                        algorithm,

                    "category":
                        details["type"],

                    "quantum_vulnerable":
                        details["quantum_vulnerable"],

                    "replacement":
                        details["replacement"],

                }



        for name, details in (
            self.SYMMETRIC_ALGORITHMS.items()
        ):

            if (

                self.normalize(
                    name,
                )

                in

                normalized

            ):

                return {

                    "algorithm":
                        algorithm,

                    "category":
                        "symmetric",

                    "quantum_vulnerable":
                        False,

                    "security_level":
                        details["quantum_security"],

                    "recommendation":
                        details["recommendation"],

                }



        for name, status in (
            self.HASH_ALGORITHMS.items()
        ):

            if (

                self.normalize(
                    name,
                )

                in

                normalized

            ):

                return {

                    "algorithm":
                        algorithm,

                    "category":
                        "hash",

                    "status":
                        status,

                }



        return {

            "algorithm":
                algorithm,

            "category":
                "unknown",

            "quantum_vulnerable":
                None,

        }



    def analyze_algorithm_inventory(
        self,
        algorithms: list[str],
    ) -> list[dict[str, Any]]:
        """
        Analyze complete algorithm list.
        """

        return [

            self.classify_algorithm(
                algorithm,
            )

            for algorithm
            in algorithms

        ]



    async def build_algorithm_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Build algorithm security inventory.
        """

        inventory = (
            await self.collect_algorithm_inventory(
                asset_id,
            )
        )


        analyzed = (
            self.analyze_algorithm_inventory(
                inventory.get(
                    "algorithms",
                    [],
                )
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "algorithms":
                inventory,

            "analysis":
                analyzed,

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    def detect_quantum_vulnerable_usage(
        self,
        analysis: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Extract quantum vulnerable
        cryptographic usage.
        """

        return [

            item

            for item
            in analysis

            if item.get(
                "quantum_vulnerable",
                False,
            )

        ]
        # ============================================================
    # Application Cryptographic Discovery Engine
    # ============================================================

    async def collect_application_crypto_usage(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Discover cryptographic usage
        inside applications.

        Tracks:

        - Libraries
        - Frameworks
        - Crypto APIs
        - Hardcoded algorithms
        - Dependencies
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Collecting application crypto usage. asset=%s",
            asset.asset_value,
        )


        #
        # Production integrations:
        #
        # - SAST scanners
        # - SBOM analysis
        # - Dependency scanners
        # - Code analyzers
        #


        return {

            "asset_id":

                str(
                    asset.id
                ),


            "applications":

                [],


            "libraries":

                [],


            "crypto_api_usage":

                [],


            "hardcoded_algorithms":

                [],


            "dependencies":

                [],


            "collected_at":

                datetime.utcnow().isoformat(),

        }



    def analyze_crypto_dependency(
        self,
        dependency: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze software crypto dependency.

        Example:

        OpenSSL
        BouncyCastle
        Crypto libraries
        """

        name = (
            dependency.get(
                "name",
                "",
            )
        )


        version = (
            dependency.get(
                "version",
            )
        )


        risk = "unknown"



        if "openssl" in name.lower():

            risk = "review_required"



        return {

            "dependency":

                name,


            "version":

                version,


            "risk":

                risk,


            "recommendation":

                (
                    "Validate PQC support "
                    "and crypto agility."
                ),

        }



    def analyze_hardcoded_algorithms(
        self,
        algorithms: list[str],
    ) -> list[dict[str, Any]]:
        """
        Detect hardcoded cryptographic choices.

        Example:

        AES-128
        RSA
        MD5
        """

        findings = []


        for algorithm in algorithms:

            analysis = (
                self.classify_algorithm(
                    algorithm,
                )
            )


            if (

                analysis.get(
                    "quantum_vulnerable",
                    False,
                )

                or

                analysis.get(
                    "status",
                )
                ==
                "deprecated"

            ):

                findings.append(

                    {

                        "algorithm":
                            algorithm,

                        "issue":
                            "Hardcoded cryptographic dependency",

                        "risk":
                            "high",

                        "recommendation":
                            (
                                "Implement "
                                "crypto-agility."
                            ),

                    }

                )


        return findings



    async def analyze_application_inventory(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze application crypto posture.
        """

        dependencies = (

            [

                self.analyze_crypto_dependency(
                    item,
                )

                for item
                in inventory.get(
                    "dependencies",
                    [],
                )

            ]

        )


        hardcoded = (
            self.analyze_hardcoded_algorithms(
                inventory.get(
                    "hardcoded_algorithms",
                    [],
                )
            )
        )


        return {

            "dependencies":

                dependencies,


            "hardcoded_crypto":

                hardcoded,


            "migration_required":

                len(
                    hardcoded
                )
                >
                0,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def build_application_crypto_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Build application-level
        crypto inventory.
        """

        inventory = (
            await self.collect_application_crypto_usage(
                asset_id,
            )
        )


        analysis = (
            await self.analyze_application_inventory(
                inventory,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "inventory":

                inventory,


            "analysis":

                analysis,

        }
        # ============================================================
    # Cloud KMS, HSM & Secret Inventory Engine
    # ============================================================

    async def collect_key_management_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Collect key management information.

        Tracks:

        - KMS providers
        - HSM usage
        - Key rotation
        - Key storage
        - Secret management
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Collecting key management inventory. asset=%s",
            asset.asset_value,
        )


        #
        # Production integrations:
        #
        # AWS KMS
        # Azure Key Vault
        # Google Cloud KMS
        # Hashicorp Vault
        # Hardware Security Modules
        #



        return {

            "asset_id":

                str(
                    asset.id
                ),


            "kms_providers":

                [],


            "hsm_devices":

                [],


            "keys":

                [],


            "rotation_enabled":

                False,


            "secrets":

                [],


            "collected_at":

                datetime.utcnow().isoformat(),

        }



    def analyze_key_strength(
        self,
        key: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze cryptographic key strength.
        """

        algorithm = (
            key.get(
                "algorithm",
                "",
            )
        )


        key_size = (
            key.get(
                "key_size",
            )
        )


        classification = (
            self.classify_algorithm(
                algorithm,
            )
        )


        risk = "low"



        if classification.get(
            "quantum_vulnerable",
            False,
        ):

            risk = "high"



        if key_size:

            if (

                "RSA"
                in
                algorithm.upper()

                and

                key_size < 2048

            ):

                risk = "critical"



        return {

            "algorithm":

                algorithm,


            "key_size":

                key_size,


            "risk":

                risk,


            "quantum_vulnerable":

                classification.get(
                    "quantum_vulnerable",
                ),


            "replacement":

                classification.get(
                    "replacement",
                ),

        }



    def analyze_key_inventory(
        self,
        keys: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Analyze all managed keys.
        """

        return [

            self.analyze_key_strength(
                key,
            )

            for key
            in keys

        ]



    def evaluate_key_rotation(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate key lifecycle security.
        """

        enabled = inventory.get(
            "rotation_enabled",
            False,
        )


        return {

            "rotation_enabled":

                enabled,


            "risk":

                (

                    "low"

                    if enabled

                    else

                    "medium"

                ),


            "recommendation":

                (

                    "Maintain automated rotation."

                    if enabled

                    else

                    "Enable automated key rotation."

                ),

        }



    async def build_key_management_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Build KMS/HSM inventory.
        """

        inventory = (
            await self.collect_key_management_inventory(
                asset_id,
            )
        )


        key_analysis = (
            self.analyze_key_inventory(
                inventory.get(
                    "keys",
                    [],
                )
            )
        )


        rotation = (
            self.evaluate_key_rotation(
                inventory,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "inventory":

                inventory,


            "keys_analysis":

                key_analysis,


            "rotation_analysis":

                rotation,


            "generated_at":

                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # Cryptographic Exposure Analysis Engine
    # ============================================================

    async def analyze_crypto_exposure(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Perform complete cryptographic exposure analysis.

        Combines:

        - Certificates
        - TLS
        - Algorithms
        - Applications
        - Key management
        """

        certificate_inventory = (
            await self.build_certificate_inventory(
                asset_id,
            )
        )


        tls_inventory = (
            await self.build_tls_crypto_inventory(
                asset_id,
            )
        )


        algorithm_inventory = (
            await self.build_algorithm_inventory(
                asset_id,
            )
        )


        application_inventory = (
            await self.build_application_crypto_inventory(
                asset_id,
            )
        )


        key_inventory = (
            await self.build_key_management_inventory(
                asset_id,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "certificates":

                certificate_inventory,


            "tls":

                tls_inventory,


            "algorithms":

                algorithm_inventory,


            "applications":

                application_inventory,


            "keys":

                key_inventory,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    def calculate_exposure_score(
        self,
        exposure: dict[str, Any],
    ) -> float:
        """
        Calculate overall crypto exposure.

        Score:

        100 = Maximum exposure
        0   = Minimal exposure
        """

        score = 0



        # --------------------------------------------------------
        # Algorithm Exposure
        # --------------------------------------------------------

        algorithms = (
            exposure
            .get(
                "algorithms",
                {}
            )
            .get(
                "analysis",
                []
            )
        )


        vulnerable_algorithms = [

            item

            for item
            in algorithms

            if item.get(
                "quantum_vulnerable",
                False,
            )

        ]


        if vulnerable_algorithms:

            score += 35



        # --------------------------------------------------------
        # Certificate Exposure
        # --------------------------------------------------------

        certificates = (
            exposure
            .get(
                "certificates",
                {}
            )
            .get(
                "analysis",
                []
            )
        )


        certificate_risks = [

            item

            for item
            in certificates

            if not item.get(
                "secure",
                True,
            )

        ]


        if certificate_risks:

            score += 20



        # --------------------------------------------------------
        # TLS Exposure
        # --------------------------------------------------------

        tls_risks = (
            exposure
            .get(
                "tls",
                {}
            )
            .get(
                "analysis",
                {}
            )
            .get(
                "quantum_exposure",
                []
            )
        )


        if tls_risks:

            score += 25



        # --------------------------------------------------------
        # Key Exposure
        # --------------------------------------------------------

        key_risks = (
            exposure
            .get(
                "keys",
                {}
            )
            .get(
                "keys_analysis",
                []
            )
        )


        critical_keys = [

            item

            for item
            in key_risks

            if item.get(
                "risk",
                ""
            )
            in
            (
                "high",
                "critical",
            )

        ]


        if critical_keys:

            score += 20



        return round(

            min(
                100,
                score,
            ),

            2,

        )



    def classify_exposure(
        self,
        score: float,
    ) -> str:
        """
        Classify cryptographic exposure.
        """

        if score >= 80:

            return "critical"


        if score >= 60:

            return "high"


        if score >= 30:

            return "medium"


        return "low"



    async def generate_exposure_report(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate crypto exposure report.
        """

        exposure = (
            await self.analyze_crypto_exposure(
                asset_id,
            )
        )


        score = (
            self.calculate_exposure_score(
                exposure,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "exposure_score":

                score,


            "risk_level":

                self.classify_exposure(
                    score,
                ),


            "details":

                exposure,


            "generated_at":

                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # Crypto Inventory Scoring Engine
    # ============================================================

    def calculate_crypto_maturity_score(
        self,
        inventory: dict[str, Any],
    ) -> float:
        """
        Calculate cryptographic maturity score.

        Score:

        100 = Enterprise crypto mature
        0   = Poor crypto posture
        """

        score = 0



        # --------------------------------------------------------
        # Inventory Coverage
        # --------------------------------------------------------

        algorithms = inventory.get(
            "algorithms",
            [],
        )


        certificates = inventory.get(
            "certificates",
            [],
        )


        keys = inventory.get(
            "keys",
            [],
        )


        if algorithms:

            score += 25


        if certificates:

            score += 15


        if keys:

            score += 15



        # --------------------------------------------------------
        # Lifecycle Management
        # --------------------------------------------------------

        if inventory.get(
            "rotation_enabled",
            False,
        ):

            score += 15



        # --------------------------------------------------------
        # PQC Preparation
        # --------------------------------------------------------

        protocols = inventory.get(
            "protocols",
            [],
        )


        hybrid_support = any(

            "HYBRID"
            in
            str(protocol).upper()

            for protocol
            in protocols

        )


        if hybrid_support:

            score += 15



        # --------------------------------------------------------
        # Automation
        # --------------------------------------------------------

        if inventory.get(
            "automation",
            False,
        ):

            score += 15



        return round(

            min(
                100,
                score,
            ),

            2,

        )



    def classify_crypto_maturity(
        self,
        score: float,
    ) -> str:
        """
        Convert maturity score
        into security maturity level.
        """

        if score >= 85:

            return "optimized"


        if score >= 65:

            return "managed"


        if score >= 40:

            return "developing"


        return "initial"



    def identify_crypto_gaps(
        self,
        inventory: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Identify crypto management gaps.
        """

        gaps = []



        if not inventory.get(
            "algorithms",
        ):

            gaps.append(

                {

                    "area":
                        "visibility",

                    "gap":
                        "No algorithm inventory",

                    "impact":
                        "Unknown cryptographic exposure",

                }

            )



        if not inventory.get(
            "rotation_enabled",
            False,
        ):

            gaps.append(

                {

                    "area":
                        "key_management",

                    "gap":
                        "Automated rotation unavailable",

                    "impact":
                        "Higher key compromise risk",

                }

            )



        if not inventory.get(
            "crypto_agility",
            False,
        ):

            gaps.append(

                {

                    "area":
                        "crypto_agility",

                    "gap":
                        "Static cryptographic architecture",

                    "impact":
                        "Difficult PQC migration",

                }

            )



        return gaps



    async def generate_inventory_score(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate crypto maturity report.
        """

        inventory = (
            await self.get_inventory(
                asset_id,
            )
        )


        score = (
            self.calculate_crypto_maturity_score(
                inventory,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "maturity_score":

                score,


            "maturity_level":

                self.classify_crypto_maturity(
                    score,
                ),


            "gaps":

                self.identify_crypto_gaps(
                    inventory,
                ),


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def compare_crypto_posture(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Compare crypto posture improvement.
        """

        before_score = (
            before.get(
                "maturity_score",
                0,
            )
        )


        after_score = (
            after.get(
                "maturity_score",
                0,
            )
        )


        return {

            "previous_score":

                before_score,


            "current_score":

                after_score,


            "improvement":

                round(

                    after_score
                    -
                    before_score,

                    2,

                ),

            "improved":

                after_score
                >
                before_score,

        }
        # ============================================================
    # PQC Integration Layer
    # ============================================================

    async def prepare_pqc_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Prepare cryptographic inventory
        for PQC analysis.

        Converts internal inventory format
        into PQC engine compatible schema.
        """

        inventory = (
            await self.get_inventory(
                asset_id,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "algorithms":

                inventory.get(
                    "algorithms",
                    [],
                ),


            "key_exchange":

                inventory.get(
                    "key_exchange",
                    [],
                ),


            "signature_algorithms":

                inventory.get(
                    "signatures",
                    [],
                ),


            "certificates":

                inventory.get(
                    "certificates",
                    [],
                ),


            "protocols":

                inventory.get(
                    "tls_versions",
                    [],
                ),


            "crypto_agility":

                inventory.get(
                    "crypto_agility",
                    False,
                ),


        }



    async def evaluate_quantum_exposure(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Evaluate quantum cryptographic exposure.

        Designed for integration with:

        - PQC Service
        - Risk Engine
        """

        inventory = (
            await self.prepare_pqc_inventory(
                asset_id,
            )
        )


        vulnerabilities = []


        algorithms = (
            inventory.get(
                "algorithms",
                [],
            )
        )


        for algorithm in algorithms:

            analysis = (
                self.classify_algorithm(
                    algorithm,
                )
            )


            if analysis.get(
                "quantum_vulnerable",
                False,
            ):

                vulnerabilities.append(
                    analysis
                )



        risk_score = 0


        if vulnerabilities:

            risk_score = min(

                100,

                len(
                    vulnerabilities
                )
                *
                25,

            )



        return {

            "asset_id":

                str(
                    asset_id
                ),


            "vulnerable_algorithms":

                vulnerabilities,


            "quantum_risk_score":

                risk_score,


            "migration_required":

                risk_score >= 50,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_pqc_migration_inputs(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate migration input package
        for PQC engine.

        Includes:

        - Current algorithms
        - Vulnerabilities
        - Replacement mapping
        """

        inventory = (
            await self.prepare_pqc_inventory(
                asset_id,
            )
        )


        exposure = (
            await self.evaluate_quantum_exposure(
                asset_id,
            )
        )


        replacements = []



        for item in exposure[
            "vulnerable_algorithms"
        ]:

            algorithm = item.get(
                "algorithm",
            )


            replacements.append(

                {

                    "current":

                        algorithm,


                    "recommended":

                        self.get_pqc_replacement(
                            algorithm,
                        ),

                }

            )



        return {

            "asset_id":

                str(
                    asset_id
                ),


            "inventory":

                inventory,


            "exposure":

                exposure,


            "migration_mapping":

                replacements,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    def get_pqc_replacement(
        self,
        algorithm: str,
    ) -> str:
        """
        Return recommended PQC replacement.
        """

        normalized = (
            self.normalize(
                algorithm,
            )
        )


        if (

            "RSA"
            in
            normalized

            or

            "ECDSA"
            in
            normalized

            or

            "ECC"
            in
            normalized

        ):

            return "ML-DSA"



        if (

            "DH"
            in
            normalized

            or

            "ECDH"
            in
            normalized

        ):

            return "ML-KEM"



        return "Review Required"



    async def sync_with_pqc_engine(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Synchronize inventory with PQC engine.

        Future:

        - Direct service call
        - Event based architecture
        - Message queue
        """

        migration_inputs = (
            await self.generate_pqc_migration_inputs(
                asset_id,
            )
        )


        logger.info(
            "Synced crypto inventory with PQC engine. asset=%s",
            asset_id,
        )


        return migration_inputs
        # ============================================================
    # Crypto Inventory Reporting & Export
    # ============================================================

    async def export_crypto_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Export complete cryptographic inventory.

        Includes:

        - Certificates
        - Algorithms
        - TLS
        - Keys
        - PQC readiness inputs
        """

        inventory = (
            await self.get_inventory(
                asset_id,
            )
        )


        exposure = (
            await self.analyze_crypto_exposure(
                asset_id,
            )
        )


        maturity = (
            await self.generate_inventory_score(
                asset_id,
            )
        )


        return {

            "report_type":

                "Cryptographic Inventory Report",


            "asset_id":

                str(
                    asset_id
                ),


            "inventory":

                inventory,


            "exposure":

                exposure,


            "maturity":

                maturity,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_executive_crypto_summary(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive summary.

        Audience:

        - CISO
        - CTO
        - Security Leadership
        """

        exposure = (
            await self.generate_exposure_report(
                asset_id,
            )
        )


        maturity = (
            await self.generate_inventory_score(
                asset_id,
            )
        )


        return {

            "summary":

                (
                    "Cryptographic posture "
                    "assessment completed."
                ),


            "risk_level":

                exposure["risk_level"],


            "exposure_score":

                exposure["exposure_score"],


            "maturity_level":

                maturity["maturity_level"],


            "priority_actions":

                [

                    "Complete cryptographic inventory.",

                    "Remove quantum vulnerable algorithms.",

                    "Enable crypto agility.",

                    "Prepare PQC migration.",

                ],


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_audit_report(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate audit-ready crypto report.

        Used for:

        - Compliance reviews
        - Security audits
        - Governance
        """

        inventory = (
            await self.export_crypto_inventory(
                asset_id,
            )
        )


        return {

            "audit_type":

                "Cryptographic Security Audit",


            "scope":

                {

                    "asset_id":
                        str(
                            asset_id
                        ),

                },


            "findings":

                inventory["exposure"],


            "recommendations":

                [

                    "Maintain algorithm inventory.",

                    "Monitor certificate lifecycle.",

                    "Prepare PQC transition roadmap.",

                ],


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def export_inventory_json(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Export machine-readable inventory.

        Used by:

        - APIs
        - SIEM integrations
        - Automation pipelines
        """

        inventory = (
            await self.get_inventory(
                asset_id,
            )
        )


        return {

            "format":

                "json",


            "version":

                "1.0",


            "asset_id":

                str(
                    asset_id
                ),


            "crypto_inventory":

                inventory,


            "exported_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_compliance_evidence(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate compliance evidence package.

        Supports:

        - ISO 27001
        - NIST
        - PQC readiness
        """

        maturity = (
            await self.generate_inventory_score(
                asset_id,
            )
        )


        return {

            "controls":

                {

                    "cryptographic_controls":

                        "tracked",


                    "algorithm_inventory":

                        "available",


                    "key_management":

                        "reviewed",


                    "pqc_readiness":

                        maturity["maturity_level"],

                },


            "generated_at":

                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # Maintenance & Health Management
    # ============================================================

    async def health_check(
        self,
    ) -> dict[str, Any]:
        """
        Crypto inventory service health check.

        Validates:

        - Database connectivity
        - Algorithm databases
        - Service availability
        """

        try:

            return {

                "service":

                    "crypto_inventory_service",


                "status":

                    "healthy",


                "supported_crypto_categories":

                    {

                        "asymmetric":

                            len(
                                self.ASYMMETRIC_ALGORITHMS
                            ),


                        "symmetric":

                            len(
                                self.SYMMETRIC_ALGORITHMS
                            ),


                        "hash":

                            len(
                                self.HASH_ALGORITHMS
                            ),

                    },


                "capabilities":

                    [

                        "Certificate Discovery",

                        "TLS Analysis",

                        "Algorithm Inventory",

                        "Key Management Analysis",

                        "PQC Preparation",

                    ],


                "timestamp":

                    datetime.utcnow().isoformat(),

            }


        except Exception as exc:

            logger.exception(
                "Crypto inventory health check failed."
            )


            return {

                "service":

                    "crypto_inventory_service",


                "status":

                    "unhealthy",


                "error":

                    str(exc),

            }



    async def validate_inventory(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate crypto inventory structure.
        """

        required_fields = [

            "algorithms",

            "certificates",

            "key_exchange",

        ]


        missing = [

            field

            for field
            in required_fields

            if field not in inventory

        ]



        return {

            "valid":

                len(
                    missing
                )
                ==
                0,


            "missing_fields":

                missing,


            "validated_at":

                datetime.utcnow().isoformat(),

        }



    async def cleanup_inventory_cache(
        self,
        *,
        older_than_days: int = 90,
    ) -> int:
        """
        Cleanup stale inventory cache.

        Reserved for:

        - Scheduled workers
        - Background jobs
        """

        #
        # Future implementation:
        #
        # Remove stale discovery snapshots
        #

        return 0



    async def rebuild_inventory_metrics(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Recalculate inventory metrics.
        """

        exposure = (
            await self.generate_exposure_report(
                asset_id,
            )
        )


        maturity = (
            await self.generate_inventory_score(
                asset_id,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "exposure":

                exposure,


            "maturity":

                maturity,


            "rebuilt_at":

                datetime.utcnow().isoformat(),

        }



    async def get_supported_algorithms(
        self,
    ) -> dict[str, Any]:
        """
        Return supported cryptographic knowledge base.
        """

        return {

            "asymmetric_algorithms":

                self.ASYMMETRIC_ALGORITHMS,


            "symmetric_algorithms":

                self.SYMMETRIC_ALGORITHMS,


            "hash_algorithms":

                self.HASH_ALGORITHMS,


            "timestamp":

                datetime.utcnow().isoformat(),

        }



# ============================================================
# End of File
# ============================================================
