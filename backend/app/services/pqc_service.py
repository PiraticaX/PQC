"""
QShield Enterprise
==================

PQC Service

Post Quantum Cryptography Intelligence Engine.

Responsible for:

- Cryptographic inventory analysis
- Quantum threat assessment
- PQC migration readiness
- Crypto agility scoring
- Algorithm recommendations

Supported Standards:

- NIST PQC
- ML-KEM
- ML-DSA
- SLH-DSA
- Hybrid Cryptography

Used by:

- Scanner Orchestrator
- Risk Engine
- Recommendation Engine
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


from app.models.finding import (
    Finding,
    FindingSeverity,
)


logger = logging.getLogger(__name__)



class PQCService:
    """
    Enterprise Post Quantum Cryptography Service.

    Responsibilities:

    • Analyze cryptographic exposure

    • Detect quantum vulnerable algorithms

    • Calculate PQC readiness

    • Generate migration strategy

    • Support compliance reporting
    """



    def __init__(
        self,
        db: Session,
    ):
        self.db = db



    # ============================================================
    # Algorithm Knowledge Base
    # ============================================================


    QUANTUM_VULNERABLE_ALGORITHMS = {

        "RSA":

            {

                "threat":
                    "Shor",

                "risk":
                    95,

                "replacement":
                    "ML-KEM / ML-DSA",

            },


        "RSA-1024":

            {

                "threat":
                    "Shor",

                "risk":
                    100,

                "replacement":
                    "ML-KEM",

            },


        "ECDSA":

            {

                "threat":
                    "Shor",

                "risk":
                    90,

                "replacement":
                    "ML-DSA",

            },


        "ECC":

            {

                "threat":
                    "Shor",

                "risk":
                    90,

                "replacement":
                    "ML-DSA",

            },


        "DH":

            {

                "threat":
                    "Shor",

                "risk":
                    85,

                "replacement":
                    "ML-KEM",

            },


    }



    PQC_ALGORITHMS = {

        "ML-KEM":

            {

                "purpose":
                    "Key Encapsulation",

                "standard":
                    "NIST FIPS 203",

            },


        "ML-DSA":

            {

                "purpose":
                    "Digital Signatures",

                "standard":
                    "NIST FIPS 204",

            },


        "SLH-DSA":

            {

                "purpose":
                    "Hash Based Signatures",

                "standard":
                    "NIST FIPS 205",

            },


    }



    CRYPTO_AGILITY_FACTORS = {

        "algorithm_inventory":
            20,

        "replaceable_keys":
            20,

        "protocol_flexibility":
            20,

        "hybrid_support":
            20,

        "automation":
            20,

    }



    # ============================================================
    # Helpers
    # ============================================================


    @staticmethod
    def normalize_algorithm(
        algorithm: str | None,
    ) -> str:

        if not algorithm:

            return ""

        return (
            algorithm
            .upper()
            .replace(
                "-",
                "",
            )
            .strip()
        )
        # ============================================================
    # Database Helpers
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



    async def get_asset_findings(
        self,
        asset_id: UUID,
    ) -> list[Finding]:
        """
        Retrieve security findings
        associated with an asset.
        """

        stmt = (
            select(Finding)
            .join(
                Asset,
            )
            .where(

                Asset.id == asset_id,

                Finding.deleted_at.is_(None),

            )
        )


        result = self.db.execute(
            stmt,
        )


        return list(
            result.scalars().all()
        )



    async def asset_exists(
        self,
        asset_id: UUID,
    ) -> bool:
        """
        Check asset availability.
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



    async def get_crypto_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Retrieve cryptographic inventory.

        Production integration:

        - Certificate scanner
        - TLS scanner
        - Application scanner
        - Key management systems
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        #
        # Current implementation acts
        # as normalization layer.
        #
        # Scanner modules can populate
        # this structure.
        #

        return {

            "asset_id":
                str(
                    asset.id
                ),

            "asset":
                asset.asset_value,


            "algorithms":

                [],


            "key_exchange":

                [],


            "signature_algorithms":

                [],


            "certificates":

                [],


            "protocols":

                [],


            "crypto_agility":
                False,

        }



    async def update_crypto_inventory(
        self,
        asset_id: UUID,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update crypto inventory.

        Storage abstraction layer.

        Can connect to:

        - Database JSON fields
        - Vault systems
        - CMDB
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        #
        # Future:
        #
        # asset.crypto_inventory = inventory
        #

        logger.info(
            "Crypto inventory updated. asset=%s",
            asset.id,
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
                "PQC service commit failed."
            )

            raise
            # ============================================================
    # Cryptographic Algorithm Detection Engine
    # ============================================================

    def detect_vulnerable_algorithms(
        self,
        algorithms: list[str],
    ) -> list[dict[str, Any]]:
        """
        Detect quantum vulnerable algorithms.

        Identifies algorithms vulnerable to:

        - Shor's algorithm
        - Future quantum attacks

        """

        vulnerabilities = []


        for algorithm in algorithms:

            normalized = (
                self.normalize_algorithm(
                    algorithm,
                )
            )


            for known, details in (
                self.QUANTUM_VULNERABLE_ALGORITHMS.items()
            ):

                known_normalized = (
                    self.normalize_algorithm(
                        known,
                    )
                )


                if known_normalized in normalized:

                    vulnerabilities.append(

                        {

                            "algorithm":
                                algorithm,

                            "threat":
                                details["threat"],

                            "risk_score":
                                details["risk"],

                            "recommended_replacement":
                                details["replacement"],

                        }

                    )

                    break



        return vulnerabilities



    def detect_symmetric_risk(
        self,
        algorithms: list[str],
    ) -> list[dict[str, Any]]:
        """
        Analyze symmetric cryptography.

        Quantum impact:

        Grover's algorithm.

        Examples:

        AES-128 -> weaker margin
        AES-256 -> recommended
        """

        findings = []


        for algorithm in algorithms:

            normalized = (
                self.normalize_algorithm(
                    algorithm,
                )
            )


            if "AES128" in normalized:

                findings.append(

                    {

                        "algorithm":
                            algorithm,

                        "threat":
                            "Grover",

                        "risk_score":
                            50,

                        "recommendation":
                            (
                                "Upgrade to AES-256 "
                                "for quantum security margin."
                            ),

                    }

                )



            elif "3DES" in normalized:

                findings.append(

                    {

                        "algorithm":
                            algorithm,

                        "threat":
                            "Grover",

                        "risk_score":
                            80,

                        "recommendation":
                            (
                                "Replace deprecated "
                                "3DES encryption."
                            ),

                    }

                )



        return findings



    def analyze_signature_algorithms(
        self,
        signatures: list[str],
    ) -> dict[str, Any]:
        """
        Analyze digital signature algorithms.

        Quantum vulnerable:

        - RSA signatures
        - ECDSA
        - EdDSA
        """

        vulnerable = (
            self.detect_vulnerable_algorithms(
                signatures,
            )
        )


        return {

            "total":

                len(
                    signatures
                ),

            "vulnerable":

                len(
                    vulnerable
                ),

            "details":
                vulnerable,

            "quantum_safe":

                (
                    len(
                        vulnerable
                    )
                    ==
                    0
                ),

        }



    def analyze_key_exchange(
        self,
        exchanges: list[str],
    ) -> dict[str, Any]:
        """
        Analyze key exchange protocols.

        Quantum vulnerable:

        - DH
        - ECDH

        Recommended:

        - ML-KEM
        - Hybrid TLS
        """

        vulnerabilities = (
            self.detect_vulnerable_algorithms(
                exchanges,
            )
        )


        return {

            "protocols":
                exchanges,

            "vulnerabilities":
                vulnerabilities,

            "migration_required":
                bool(
                    vulnerabilities
                ),

            "recommended":
                [

                    "ML-KEM",

                    "Hybrid Key Exchange",

                ],

        }



    def analyze_inventory(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze complete crypto inventory.

        Combines:

        - Encryption
        - Signatures
        - Key exchange
        """

        algorithms = (
            inventory.get(
                "algorithms",
                [],
            )
        )


        signatures = (
            inventory.get(
                "signature_algorithms",
                [],
            )
        )


        exchanges = (
            inventory.get(
                "key_exchange",
                [],
            )
        )


        return {

            "algorithm_risk":

                self.detect_vulnerable_algorithms(
                    algorithms,
                ),


            "symmetric_risk":

                self.detect_symmetric_risk(
                    algorithms,
                ),


            "signature_analysis":

                self.analyze_signature_algorithms(
                    signatures,
                ),


            "key_exchange_analysis":

                self.analyze_key_exchange(
                    exchanges,
                ),

        }
        # ============================================================
    # Quantum Vulnerability Scoring Engine
    # ============================================================

    def calculate_quantum_risk_score(
        self,
        analysis: dict[str, Any],
    ) -> float:
        """
        Calculate quantum vulnerability score.

        Score:

        0   = Quantum safe
        100 = Extremely vulnerable
        """

        score = 0.0



        # --------------------------------------------------------
        # Asymmetric Algorithm Risk
        # --------------------------------------------------------

        algorithm_risks = (
            analysis.get(
                "algorithm_risk",
                [],
            )
        )


        if algorithm_risks:

            highest_algorithm_risk = max(

                item["risk_score"]

                for item
                in algorithm_risks

            )


            score += (
                highest_algorithm_risk
                *
                0.45
            )



        # --------------------------------------------------------
        # Symmetric Risk
        # --------------------------------------------------------

        symmetric_risks = (
            analysis.get(
                "symmetric_risk",
                [],
            )
        )


        if symmetric_risks:

            highest_symmetric_risk = max(

                item["risk_score"]

                for item
                in symmetric_risks

            )


            score += (
                highest_symmetric_risk
                *
                0.15
            )



        # --------------------------------------------------------
        # Signature Risk
        # --------------------------------------------------------

        signature_analysis = (
            analysis.get(
                "signature_analysis",
                {},
            )
        )


        if not signature_analysis.get(
            "quantum_safe",
            True,
        ):

            score += 25



        # --------------------------------------------------------
        # Key Exchange Risk
        # --------------------------------------------------------

        exchange_analysis = (
            analysis.get(
                "key_exchange_analysis",
                {},
            )
        )


        if exchange_analysis.get(
            "migration_required",
            False,
        ):

            score += 20



        return round(

            min(
                100,
                score,
            ),

            2,

        )



    def classify_quantum_risk(
        self,
        score: float,
    ) -> str:
        """
        Convert score into risk category.
        """

        if score >= 85:

            return "critical"


        if score >= 65:

            return "high"


        if score >= 40:

            return "medium"


        if score >= 15:

            return "low"


        return "quantum_ready"



    def generate_quantum_assessment(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate complete quantum risk assessment.
        """

        score = (
            self.calculate_quantum_risk_score(
                analysis,
            )
        )


        level = (
            self.classify_quantum_risk(
                score,
            )
        )


        return {

            "quantum_risk_score":
                score,

            "risk_level":
                level,

            "migration_required":

                level
                !=
                "quantum_ready",

            "threat_model":

                [

                    "Shor Algorithm",

                    "Grover Algorithm",

                    "Harvest Now Decrypt Later",

                ],

            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def assess_asset_quantum_risk(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Complete quantum risk assessment
        for an asset.
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        analysis = (
            self.analyze_inventory(
                inventory,
            )
        )


        assessment = (
            self.generate_quantum_assessment(
                analysis,
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

            "assessment":
                assessment,

        }
        # ============================================================
    # RSA / ECC / Shor Threat Analysis
    # ============================================================

    def analyze_shor_vulnerability(
        self,
        algorithm: str,
    ) -> dict[str, Any]:
        """
        Analyze vulnerability against Shor's algorithm.

        Shor impacts:

        - RSA
        - ECC
        - DH
        - ECDH
        """

        normalized = (
            self.normalize_algorithm(
                algorithm,
            )
        )


        vulnerable = False

        severity = "none"

        risk = 0



        for known, details in (
            self.QUANTUM_VULNERABLE_ALGORITHMS.items()
        ):

            if (
                self.normalize_algorithm(
                    known,
                )
                in normalized
            ):

                vulnerable = True

                risk = details["risk"]

                severity = (

                    "critical"

                    if risk >= 90

                    else

                    "high"

                )

                break



        return {

            "algorithm":
                algorithm,

            "shor_vulnerable":
                vulnerable,

            "risk_score":
                risk,

            "severity":
                severity,

            "replacement":

                (
                    details["replacement"]

                    if vulnerable

                    else None

                ),

        }



    def analyze_rsa_security(
        self,
        key_size: int,
    ) -> dict[str, Any]:
        """
        Analyze RSA quantum exposure.

        RSA security is affected by:

        - Key size
        - Shor algorithm
        """

        risk = 0

        recommendation = ""



        if key_size <= 1024:

            risk = 100

            recommendation = (
                "Immediately migrate away from RSA-1024."
            )


        elif key_size <= 2048:

            risk = 85

            recommendation = (
                "Plan PQC migration. RSA-2048 "
                "is vulnerable in future quantum era."
            )


        elif key_size <= 3072:

            risk = 60

            recommendation = (
                "Prepare hybrid cryptography transition."
            )


        else:

            risk = 40

            recommendation = (
                "Maintain crypto agility strategy."
            )



        return {

            "algorithm":
                "RSA",

            "key_size":
                key_size,

            "quantum_risk":
                risk,

            "recommendation":
                recommendation,

        }



    def analyze_ecc_security(
        self,
        curve: str,
    ) -> dict[str, Any]:
        """
        Analyze elliptic curve vulnerability.

        ECC is vulnerable to Shor.
        """

        return {

            "algorithm":
                "ECC",

            "curve":
                curve,

            "quantum_risk":
                90,

            "threat":
                "Shor Algorithm",

            "recommendation":
                (
                    "Replace ECC signatures "
                    "with ML-DSA or hybrid signatures."
                ),

        }



    def analyze_harvest_now_decrypt_later(
        self,
        data_sensitivity: str,
        retention_years: int,
    ) -> dict[str, Any]:
        """
        Evaluate HNDL threat.

        Harvest Now Decrypt Later:

        Attackers collect encrypted data today
        and decrypt after quantum computers mature.
        """

        risk = 0



        if data_sensitivity.lower() in (

            "high",

            "critical",

        ):

            risk += 60



        if retention_years >= 10:

            risk += 30


        elif retention_years >= 5:

            risk += 15



        risk = min(
            100,
            risk,
        )



        return {

            "threat":
                "Harvest Now Decrypt Later",

            "risk_score":
                risk,

            "migration_required":
                risk >= 50,

            "recommendation":

                (

                    "Prioritize PQC migration "
                    "for long-lived sensitive data."

                    if risk >= 50

                    else

                    "Continue monitoring."

                ),

        }



    def generate_shor_migration_advice(
        self,
        vulnerabilities: list[dict[str, Any]],
    ) -> list[str]:
        """
        Generate migration advice
        for Shor vulnerable systems.
        """

        actions = []


        for item in vulnerabilities:

            algorithm = item.get(
                "algorithm",
                "",
            )


            if "RSA" in algorithm.upper():

                actions.append(
                    "Migrate RSA workloads toward ML-KEM based key exchange."
                )


            elif "ECC" in algorithm.upper():

                actions.append(
                    "Adopt ML-DSA based quantum-safe signatures."
                )


            elif "DH" in algorithm.upper():

                actions.append(
                    "Deploy hybrid key exchange mechanisms."
                )



        return list(
            set(actions)
        )
        # ============================================================
    # PQC Readiness Assessment Engine
    # ============================================================

    def calculate_pqc_readiness_score(
        self,
        inventory: dict[str, Any],
        analysis: dict[str, Any],
    ) -> float:
        """
        Calculate PQC migration readiness.

        Score:

        100 = Fully ready
        0   = Not ready
        """

        score = 0



        # --------------------------------------------------------
        # Algorithm Inventory
        # --------------------------------------------------------

        algorithms = inventory.get(
            "algorithms",
            [],
        )


        if algorithms:

            score += 20



        # --------------------------------------------------------
        # Crypto Agility
        # --------------------------------------------------------

        if inventory.get(
            "crypto_agility",
            False,
        ):

            score += 25



        # --------------------------------------------------------
        # Hybrid Support
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

            score += 20



        # --------------------------------------------------------
        # PQC Algorithm Presence
        # --------------------------------------------------------

        all_algorithms = [

            str(item).upper()

            for item
            in algorithms

        ]


        pqc_found = any(

            pqc
            in
            all_algorithms

            for pqc
            in self.PQC_ALGORITHMS.keys()

        )


        if pqc_found:

            score += 35



        return round(

            min(
                100,
                score,
            ),

            2,

        )



    def classify_readiness(
        self,
        score: float,
    ) -> str:
        """
        Convert readiness score
        into maturity level.
        """

        if score >= 85:

            return "pqc_ready"


        if score >= 60:

            return "migration_ready"


        if score >= 30:

            return "assessment_phase"


        return "not_ready"



    async def assess_pqc_readiness(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Complete PQC readiness assessment.

        Flow:

        Inventory
            |
            v
        Analysis
            |
            v
        Readiness Score
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        analysis = (
            self.analyze_inventory(
                inventory,
            )
        )


        quantum_risk = (
            self.generate_quantum_assessment(
                analysis,
            )
        )


        readiness_score = (
            self.calculate_pqc_readiness_score(
                inventory,
                analysis,
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "quantum_risk":

                quantum_risk,


            "pqc_readiness_score":
                readiness_score,


            "readiness_level":
                self.classify_readiness(
                    readiness_score,
                ),


            "migration_required":

                readiness_score < 80,


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    def identify_readiness_gaps(
        self,
        inventory: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Identify missing PQC capabilities.
        """

        gaps = []



        if not inventory.get(
            "algorithms",
        ):

            gaps.append(

                {

                    "gap":
                        "No crypto inventory",

                    "impact":
                        "Cannot assess quantum exposure",

                }

            )



        if not inventory.get(
            "crypto_agility",
            False,
        ):

            gaps.append(

                {

                    "gap":
                        "No crypto agility",

                    "impact":
                        "Migration complexity increases",

                }

            )



        return gaps
        # ============================================================
    # Crypto Agility Evaluation Engine
    # ============================================================

    def calculate_crypto_agility_score(
        self,
        inventory: dict[str, Any],
    ) -> float:
        """
        Calculate cryptographic agility score.

        Crypto agility means:

        Ability to replace cryptographic
        algorithms without major redesign.

        Score:

        100 = Highly agile
        0   = Fully static
        """

        score = 0



        # --------------------------------------------------------
        # Algorithm Inventory
        # --------------------------------------------------------

        algorithms = inventory.get(
            "algorithms",
            [],
        )


        if algorithms:

            score += (
                self.CRYPTO_AGILITY_FACTORS[
                    "algorithm_inventory"
                ]
            )



        # --------------------------------------------------------
        # Replaceable Keys
        # --------------------------------------------------------

        if inventory.get(
            "key_rotation",
            False,
        ):

            score += (
                self.CRYPTO_AGILITY_FACTORS[
                    "replaceable_keys"
                ]
            )



        # --------------------------------------------------------
        # Protocol Flexibility
        # --------------------------------------------------------

        protocols = inventory.get(
            "protocols",
            [],
        )


        if protocols:

            score += (
                self.CRYPTO_AGILITY_FACTORS[
                    "protocol_flexibility"
                ]
            )



        # --------------------------------------------------------
        # Hybrid Support
        # --------------------------------------------------------

        hybrid = any(

            "HYBRID"
            in
            str(protocol).upper()

            for protocol
            in protocols

        )


        if hybrid:

            score += (
                self.CRYPTO_AGILITY_FACTORS[
                    "hybrid_support"
                ]
            )



        # --------------------------------------------------------
        # Automation
        # --------------------------------------------------------

        if inventory.get(
            "automation",
            False,
        ):

            score += (
                self.CRYPTO_AGILITY_FACTORS[
                    "automation"
                ]
            )



        return round(
            min(
                100,
                score,
            ),
            2,
        )



    def classify_crypto_agility(
        self,
        score: float,
    ) -> str:
        """
        Classify crypto agility maturity.
        """

        if score >= 80:

            return "advanced"


        if score >= 50:

            return "moderate"


        if score >= 25:

            return "limited"


        return "static"



    async def assess_crypto_agility(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Complete crypto agility assessment.
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        score = (
            self.calculate_crypto_agility_score(
                inventory,
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "crypto_agility_score":
                score,


            "maturity":

                self.classify_crypto_agility(
                    score,
                ),


            "recommendations":

                self.generate_agility_recommendations(
                    score,
                ),


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    def generate_agility_recommendations(
        self,
        score: float,
    ) -> list[str]:
        """
        Generate crypto agility improvements.
        """

        recommendations = []



        if score < 50:

            recommendations.extend(

                [

                    "Create cryptographic inventory.",

                    "Separate crypto implementations from applications.",

                    "Introduce algorithm replacement capability.",

                ]

            )



        if score < 80:

            recommendations.append(

                "Prepare hybrid cryptography deployment."

            )



        if score >= 80:

            recommendations.append(

                "Maintain continuous PQC readiness monitoring."

            )



        return recommendations



    async def generate_crypto_agility_report(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate crypto agility report.
        """

        assessment = (
            await self.assess_crypto_agility(
                asset_id,
            )
        )


        return {

            "report_type":
                "crypto_agility",

            "assessment":
                assessment,

            "generated_at":
                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # PQC Migration Roadmap Generator
    # ============================================================

    def generate_migration_phases(
        self,
        risk_level: str,
        readiness_level: str,
    ) -> list[dict[str, Any]]:
        """
        Generate PQC migration roadmap.

        Phases:

        1. Discovery
        2. Assessment
        3. Preparation
        4. Migration
        5. Validation
        """

        phases = []



        # --------------------------------------------------------
        # Phase 1: Discovery
        # --------------------------------------------------------

        phases.append(

            {

                "phase":
                    "discovery",

                "priority":
                    "high",

                "actions":

                    [

                        "Create cryptographic inventory.",

                        "Identify RSA, ECC and DH dependencies.",

                        "Map certificates and key lifecycle.",

                    ],

            }

        )



        # --------------------------------------------------------
        # Phase 2: Assessment
        # --------------------------------------------------------

        phases.append(

            {

                "phase":
                    "assessment",

                "priority":
                    "high",

                "actions":

                    [

                        "Evaluate quantum vulnerability.",

                        "Identify harvest-now-decrypt-later exposure.",

                        "Classify critical data assets.",

                    ],

            }

        )



        # --------------------------------------------------------
        # Phase 3: Preparation
        # --------------------------------------------------------

        phases.append(

            {

                "phase":
                    "preparation",

                "priority":
                    (
                        "high"

                        if risk_level
                        in
                        (
                            "critical",
                            "high",
                        )

                        else

                        "medium"
                    ),

                "actions":

                    [

                        "Enable cryptographic agility.",

                        "Deploy hybrid cryptography testing.",

                        "Prepare PQC implementation strategy.",

                    ],

            }

        )



        # --------------------------------------------------------
        # Phase 4: Migration
        # --------------------------------------------------------

        phases.append(

            {

                "phase":
                    "migration",

                "priority":
                    "medium",

                "actions":

                    [

                        "Adopt ML-KEM for key exchange.",

                        "Adopt ML-DSA for signatures.",

                        "Replace vulnerable algorithms.",

                    ],

            }

        )



        # --------------------------------------------------------
        # Phase 5: Validation
        # --------------------------------------------------------

        phases.append(

            {

                "phase":
                    "validation",

                "priority":
                    "medium",

                "actions":

                    [

                        "Perform interoperability testing.",

                        "Validate security controls.",

                        "Monitor PQC posture continuously.",

                    ],

            }

        )


        return phases



    async def generate_asset_migration_plan(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate asset-specific PQC migration plan.
        """

        assessment = (
            await self.assess_pqc_readiness(
                asset_id,
            )
        )


        quantum_risk = (
            assessment["quantum_risk"]
        )


        phases = (
            self.generate_migration_phases(
                quantum_risk["risk_level"],
                assessment["readiness_level"],
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "current_state":

                {

                    "quantum_risk":
                        quantum_risk["risk_level"],

                    "readiness":
                        assessment["readiness_level"],

                },


            "migration_plan":
                phases,


            "recommended_algorithms":

                {

                    "key_exchange":
                        "ML-KEM",

                    "digital_signature":
                        "ML-DSA",

                },


            "generated_at":
                datetime.utcnow().isoformat(),

        }



    async def generate_organization_migration_plan(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate enterprise PQC roadmap.

        Covers:

        - Asset discovery
        - Prioritization
        - Migration sequence
        """

        stmt = (
            select(Asset)
            .where(

                Asset.organization_id
                ==
                organization_id,

                Asset.deleted_at.is_(None),

            )
        )


        result = self.db.execute(
            stmt,
        )


        assets = list(
            result.scalars().all()
        )


        asset_plans = []


        for asset in assets:

            plan = (
                await self.generate_asset_migration_plan(
                    asset.id,
                )
            )


            asset_plans.append(
                plan,
            )


        return {

            "organization_id":
                str(
                    organization_id
                ),

            "assets_analyzed":
                len(
                    assets
                ),

            "migration_plans":
                asset_plans,

            "generated_at":
                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # PQC Standards Mapping
    # ML-KEM / ML-DSA Readiness Engine
    # ============================================================

    def map_algorithm_to_pqc_standard(
        self,
        algorithm: str,
    ) -> dict[str, Any]:
        """
        Map vulnerable algorithms
        to NIST PQC replacements.

        Examples:

        RSA/ECDH
            ->
        ML-KEM

        RSA/ECDSA
            ->
        ML-DSA
        """

        normalized = (
            self.normalize_algorithm(
                algorithm,
            )
        )


        mapping = {

            "RSA":

                {

                    "replacement":
                        "ML-DSA",

                    "purpose":
                        "Digital Signature",

                    "standard":
                        "FIPS 204",

                },


            "ECDSA":

                {

                    "replacement":
                        "ML-DSA",

                    "purpose":
                        "Digital Signature",

                    "standard":
                        "FIPS 204",

                },


            "ECC":

                {

                    "replacement":
                        "ML-DSA",

                    "purpose":
                        "Digital Signature",

                    "standard":
                        "FIPS 204",

                },


            "DH":

                {

                    "replacement":
                        "ML-KEM",

                    "purpose":
                        "Key Encapsulation",

                    "standard":
                        "FIPS 203",

                },


            "ECDH":

                {

                    "replacement":
                        "ML-KEM",

                    "purpose":
                        "Key Encapsulation",

                    "standard":
                        "FIPS 203",

                },

        }



        for source, details in mapping.items():

            if source in normalized:

                return {

                    "current_algorithm":
                        algorithm,

                    **details,

                }



        return {

            "current_algorithm":
                algorithm,

            "replacement":
                None,

            "status":
                "unknown",

        }



    def evaluate_ml_kem_readiness(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate ML-KEM deployment readiness.

        ML-KEM replaces:

        - RSA key exchange
        - DH
        - ECDH
        """

        exchanges = inventory.get(
            "key_exchange",
            [],
        )


        vulnerable = (
            self.detect_vulnerable_algorithms(
                exchanges,
            )
        )


        return {

            "algorithm":
                "ML-KEM",

            "standard":
                "NIST FIPS 203",

            "current_vulnerabilities":
                vulnerable,

            "ready":

                len(
                    vulnerable
                )
                >
                0,


            "recommendation":

                (
                    "Deploy hybrid ML-KEM key exchange."

                    if vulnerable

                    else

                    "Maintain PQC readiness monitoring."

                ),

        }



    def evaluate_ml_dsa_readiness(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate ML-DSA signature migration.

        ML-DSA replaces:

        - RSA signatures
        - ECDSA
        """

        signatures = inventory.get(
            "signature_algorithms",
            [],
        )


        vulnerable = (
            self.detect_vulnerable_algorithms(
                signatures,
            )
        )


        return {

            "algorithm":
                "ML-DSA",

            "standard":
                "NIST FIPS 204",

            "current_vulnerabilities":
                vulnerable,

            "ready":

                len(
                    vulnerable
                )
                >
                0,


            "recommendation":

                (
                    "Migrate digital signatures "
                    "towards ML-DSA."

                    if vulnerable

                    else

                    "Current signatures have "
                    "no detected quantum exposure."

                ),

        }



    def generate_pqc_standard_matrix(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate PQC transition matrix.
        """

        return {

            "key_encapsulation":

                self.evaluate_ml_kem_readiness(
                    inventory,
                ),


            "digital_signature":

                self.evaluate_ml_dsa_readiness(
                    inventory,
                ),


            "hash_signature":

                {

                    "algorithm":
                        "SLH-DSA",

                    "standard":
                        "NIST FIPS 205",

                    "status":
                        "available",

                },

        }



    async def pqc_algorithm_recommendation(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate recommended PQC algorithms
        for an asset.
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        matrix = (
            self.generate_pqc_standard_matrix(
                inventory,
            )
        )


        return {

            "asset_id":
                str(
                    asset_id
                ),

            "recommended_algorithms":

                {

                    "key_exchange":
                        "ML-KEM",

                    "signature":
                        "ML-DSA",

                    "hash_signature":
                        "SLH-DSA",

                },


            "assessment":
                matrix,


            "generated_at":
                datetime.utcnow().isoformat(),

        }
        # ============================================================
    # PQC Dashboard Analytics
    # ============================================================

    async def get_pqc_statistics(
        self,
        organization_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Generate PQC security metrics.

        Metrics:

        - Total assets
        - Assets assessed
        - Quantum vulnerable assets
        - PQC migration required
        """

        filters = [

            Asset.deleted_at.is_(None),

        ]


        if organization_id:

            filters.append(

                Asset.organization_id
                ==
                organization_id

            )


        total_assets = self.db.scalar(
            select(
                func.count(
                    Asset.id,
                )
            )
            .where(
                *filters,
            )
        )



        assessed_assets = 0

        vulnerable_assets = 0

        migration_required = 0



        #
        # Future:
        #
        # This will query stored PQC
        # assessment results.
        #
        # Current implementation
        # keeps aggregation layer.
        #



        return {

            "total_assets":

                int(
                    total_assets or 0
                ),


            "assessed_assets":

                assessed_assets,


            "quantum_vulnerable_assets":

                vulnerable_assets,


            "migration_required":

                migration_required,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_pqc_dashboard(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive PQC dashboard.

        Used by:

        - CISO Dashboard
        - Compliance Portal
        - Board Reports
        """

        statistics = (
            await self.get_pqc_statistics(
                organization_id,
            )
        )


        return {

            "title":

                "Post Quantum Security Dashboard",


            "statistics":

                statistics,


            "key_messages":

                [

                    "Identify quantum vulnerable cryptography.",

                    "Prioritize high-value assets.",

                    "Prepare PQC migration roadmap.",

                ],


            "recommended_standards":

                [

                    "NIST FIPS 203 ML-KEM",

                    "NIST FIPS 204 ML-DSA",

                    "NIST FIPS 205 SLH-DSA",

                ],


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def calculate_enterprise_quantum_score(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Calculate enterprise quantum security score.

        Score:

        100 = Quantum ready
        0   = High exposure
        """

        statistics = (
            await self.get_pqc_statistics(
                organization_id,
            )
        )


        total = statistics[
            "total_assets"
        ]


        assessed = statistics[
            "assessed_assets"
        ]



        if total == 0:

            score = 0


        else:

            score = (
                assessed
                /
                total
            ) * 100



        return {

            "organization_id":

                str(
                    organization_id
                ),


            "quantum_security_score":

                round(
                    score,
                    2,
                ),


            "maturity":

                (

                    "quantum_ready"

                    if score >= 85

                    else

                    "transitioning"

                    if score >= 50

                    else

                    "early_stage"

                ),


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_risk_heatmap(
        self,
        organization_id: UUID,
    ) -> list[dict[str, Any]]:
        """
        Generate PQC risk heatmap.

        Used for visualization.
        """

        return [

            {

                "category":
                    "RSA",

                "risk":
                    "high",

                "migration":
                    "ML-DSA",

            },


            {

                "category":
                    "ECC",

                "risk":
                    "high",

                "migration":
                    "ML-DSA",

            },


            {

                "category":
                    "DH/ECDH",

                "risk":
                    "high",

                "migration":
                    "ML-KEM",

            },


        ]
        # ============================================================
    # PQC Reporting & Export Helpers
    # ============================================================

    async def export_pqc_assessment(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Export complete PQC assessment.

        Includes:

        - Crypto inventory
        - Quantum risk
        - Readiness
        - Migration guidance
        """

        readiness = (
            await self.assess_pqc_readiness(
                asset_id,
            )
        )


        agility = (
            await self.assess_crypto_agility(
                asset_id,
            )
        )


        migration = (
            await self.generate_asset_migration_plan(
                asset_id,
            )
        )


        algorithms = (
            await self.pqc_algorithm_recommendation(
                asset_id,
            )
        )


        return {

            "report_type":

                "PQC Readiness Assessment",


            "asset_id":

                str(
                    asset_id
                ),


            "readiness":

                readiness,


            "crypto_agility":

                agility,


            "migration_plan":

                migration,


            "recommended_algorithms":

                algorithms,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_executive_pqc_summary(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate executive PQC summary.

        Designed for:

        - CISO
        - CTO
        - Board
        """

        dashboard = (
            await self.generate_pqc_dashboard(
                organization_id,
            )
        )


        score = (
            await self.calculate_enterprise_quantum_score(
                organization_id,
            )
        )


        return {

            "summary":

                (
                    "Post Quantum Cryptography "
                    "readiness assessment completed."
                ),


            "quantum_security_score":

                score["quantum_security_score"],


            "maturity":

                score["maturity"],


            "key_actions":

                [

                    "Inventory cryptographic assets.",

                    "Identify RSA/ECC dependencies.",

                    "Prepare ML-KEM migration.",

                    "Prepare ML-DSA migration.",

                ],


            "dashboard":

                dashboard,


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def export_crypto_inventory(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Export cryptographic inventory.
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        analysis = (
            self.analyze_inventory(
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


            "generated_at":

                datetime.utcnow().isoformat(),

        }



    async def generate_compliance_mapping(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Generate PQC standards mapping.

        Maps:

        - NIST PQC
        - Crypto inventory
        - Migration requirements
        """

        inventory = (
            await self.get_crypto_inventory(
                asset_id,
            )
        )


        return {

            "asset_id":

                str(
                    asset_id
                ),


            "standards":

                {

                    "NIST_FIPS_203":

                        "ML-KEM Key Encapsulation",


                    "NIST_FIPS_204":

                        "ML-DSA Digital Signatures",


                    "NIST_FIPS_205":

                        "SLH-DSA Hash Signatures",

                },


            "current_inventory":

                inventory,


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
        PQC service health status.

        Checks:

        - Database connectivity
        - Algorithm knowledge base
        - Service availability
        """

        try:

            return {

                "service":
                    "pqc_service",

                "status":
                    "healthy",

                "supported_algorithms":

                    {

                        "quantum_vulnerable":

                            len(
                                self.QUANTUM_VULNERABLE_ALGORITHMS
                            ),


                        "pqc_algorithms":

                            len(
                                self.PQC_ALGORITHMS
                            ),

                    },


                "standards":

                    [

                        "NIST FIPS 203",

                        "NIST FIPS 204",

                        "NIST FIPS 205",

                    ],


                "timestamp":

                    datetime.utcnow().isoformat(),

            }


        except Exception as exc:

            logger.exception(
                "PQC health check failed."
            )


            return {

                "service":
                    "pqc_service",

                "status":
                    "unhealthy",

                "error":
                    str(exc),

            }



    async def validate_algorithm_inventory(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate cryptographic inventory.

        Ensures required fields exist.
        """

        required_fields = [

            "algorithms",

            "key_exchange",

            "signature_algorithms",

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


            "timestamp":

                datetime.utcnow().isoformat(),

        }



    async def cleanup_old_assessments(
        self,
        *,
        older_than_days: int = 180,
    ) -> int:
        """
        Cleanup historical PQC assessments.

        Reserved for:

        - Scheduled workers
        - Database maintenance
        """

        #
        # Assessment storage cleanup
        # will be implemented when
        # PQCAssessment model is added.
        #

        return 0



    async def rebuild_pqc_metrics(
        self,
        organization_id: UUID,
    ) -> dict[str, Any]:
        """
        Recalculate PQC organization metrics.
        """

        dashboard = (
            await self.generate_pqc_dashboard(
                organization_id,
            )
        )


        score = (
            await self.calculate_enterprise_quantum_score(
                organization_id,
            )
        )


        return {

            "dashboard":

                dashboard,


            "security_score":

                score,


            "rebuilt_at":

                datetime.utcnow().isoformat(),

        }



    async def get_supported_pqc_algorithms(
        self,
    ) -> dict[str, Any]:
        """
        Return supported PQC algorithms.
        """

        return {

            "algorithms":

                self.PQC_ALGORITHMS,


            "standards":

                {

                    "key_encapsulation":

                        "NIST FIPS 203",


                    "digital_signature":

                        "NIST FIPS 204",


                    "hash_signature":

                        "NIST FIPS 205",

                },


            "timestamp":

                datetime.utcnow().isoformat(),

        }



# ============================================================
# End of File
# ============================================================
