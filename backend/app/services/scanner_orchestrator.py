"""
QShield Enterprise
==================

Scanner Orchestrator

Central execution engine responsible for:

- Scheduling scans
- Selecting scanner engines
- Managing workers
- Executing security scans
- Processing results
- Triggering risk analysis
- Triggering recommendations

Supported Engines:

- DNS Scanner
- HTTP Scanner
- TLS Scanner
- Port Scanner
- PQC Scanner

Used by:

- REST API
- Celery Workers
- Kubernetes Jobs
- Scheduler
- CLI

Author:
QShield Enterprise
"""

from __future__ import annotations


import asyncio
import logging

from datetime import datetime
from typing import Any
from uuid import UUID


from sqlalchemy import func
from sqlalchemy import select


from sqlalchemy.ext.asyncio import AsyncSession


from app.models.asset import Asset


from app.models.scan import (
    Scan,
    ScanStatus,
    ScanEngine,
    ScanTrigger,
)


from app.models.finding import Finding


from app.services.risk_service import (
    RiskService,
)


from app.services.recommendation_service import (
    RecommendationService,
)



logger = logging.getLogger(__name__)



class ScannerOrchestrator:
    """
    Enterprise Scanner Execution Engine.

    Responsibilities:

    • Schedule scans

    • Manage scanner workers

    • Execute security engines

    • Collect results

    • Create findings

    • Update risk

    • Generate recommendations
    """



    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db


        self.risk_service = (
            RiskService(
                db,
            )
        )


        self.recommendation_service = (
            RecommendationService(
                db,
            )
        )



        self.scanner_registry = {

            ScanEngine.DNS:
                self.run_dns_scan,


            ScanEngine.HTTP:
                self.run_http_scan,


            ScanEngine.TLS:
                self.run_tls_scan,


            ScanEngine.PORT:
                self.run_port_scan,


            ScanEngine.PQC:
                self.run_pqc_scan,

        }



    # ============================================================
    # Constants
    # ============================================================


    MAX_CONCURRENT_SCANS = 10


    DEFAULT_TIMEOUT_SECONDS = 900



    # ============================================================
    # Basic Helpers
    # ============================================================


    @staticmethod
    def normalize_engine(
        engine: ScanEngine,
    ) -> ScanEngine:

        if isinstance(
            engine,
            ScanEngine,
        ):

            return engine


        return ScanEngine(
            str(engine).lower()
        )
        # ============================================================
    # Database Helpers
    # ============================================================

    async def get_asset(
        self,
        asset_id: UUID,
    ) -> Asset | None:
        """
        Retrieve asset for scanning.
        """

        stmt = (
            select(Asset)
            .where(

                Asset.id == asset_id,

                Asset.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def get_scan(
        self,
        scan_id: UUID,
    ) -> Scan | None:
        """
        Retrieve scan execution object.
        """

        stmt = (
            select(Scan)
            .where(

                Scan.id == scan_id,

                Scan.deleted_at.is_(None),

            )
        )


        result = await self.db.execute(
            stmt,
        )


        return result.scalar_one_or_none()



    async def scan_exists(
        self,
        scan_id: UUID,
    ) -> bool:
        """
        Verify scan exists.
        """

        count = await self.db.scalar(
            select(
                func.count(
                    Scan.id,
                )
            )
            .where(
                Scan.id == scan_id,
            )
        )


        return bool(count)



    async def asset_exists(
        self,
        asset_id: UUID,
    ) -> bool:
        """
        Verify asset exists.
        """

        count = await self.db.scalar(
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



    async def commit(
        self,
    ) -> None:
        """
        Safe database commit.
        """

        try:

            await self.db.commit()


        except Exception:

            await self.db.rollback()


            logger.exception(
                "Scanner orchestrator commit failed."
            )

            raise



    async def rollback(
        self,
    ) -> None:
        """
        Rollback database transaction.
        """

        await self.db.rollback()



    # ============================================================
    # Validation
    # ============================================================

    def validate_engine(
        self,
        engine: ScanEngine,
    ) -> None:
        """
        Validate scanner engine availability.
        """

        if engine not in self.scanner_registry:

            raise ValueError(
                f"Unsupported scanner engine: {engine}"
            )



    def validate_scan_state(
        self,
        scan: Scan,
    ) -> None:
        """
        Validate scan execution state.
        """

        allowed = [

            ScanStatus.PENDING,

            ScanStatus.QUEUED,

        ]


        if scan.status not in allowed:

            raise ValueError(
                "Scan cannot be executed in current state."
            )



    async def validate_execution(
        self,
        scan_id: UUID,
        engine: ScanEngine,
    ) -> tuple[Scan, Asset]:
        """
        Validate complete execution context.

        Returns:

        (
            Scan,
            Asset
        )
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        self.validate_scan_state(
            scan,
        )


        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Scan asset not found."
            )


        self.validate_engine(
            engine,
        )


        return scan, asset
        # ============================================================
    # Scan Queue Management
    # ============================================================

    async def queue_scan(
        self,
        scan_id: UUID,
    ) -> Scan:
        """
        Move scan into execution queue.

        Lifecycle:

        PENDING
            |
            v
        QUEUED
            |
            v
        RUNNING
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        if scan.status not in (

            ScanStatus.PENDING,

            ScanStatus.QUEUED,

        ):

            raise ValueError(
                "Scan cannot be queued."
            )


        scan.status = (
            ScanStatus.QUEUED
        )


        scan.queued_at = (
            datetime.utcnow()
        )


        await self.commit()


        await self.db.refresh(
            scan,
        )


        logger.info(
            "Scan queued. id=%s",
            scan.id,
        )


        return scan



    async def create_scan_job(
        self,
        asset_id: UUID,
        *,
        engine: ScanEngine,
        trigger: ScanTrigger = ScanTrigger.MANUAL,
        configuration: dict[str, Any] | None = None,
    ) -> Scan:
        """
        Create scanner execution job.

        Workflow:

        Asset
          |
          v
        Create Scan
          |
          v
        Queue Worker
        """

        asset = await self.get_asset(
            asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        self.validate_engine(
            engine,
        )


        scan = Scan(

            asset_id=asset.id,

            engine=engine,

            trigger=trigger,

            status=ScanStatus.PENDING,

            configuration=(
                configuration
                or {}
            ),

            created_at=datetime.utcnow(),

        )


        self.db.add(
            scan,
        )


        await self.commit()


        await self.db.refresh(
            scan,
        )


        logger.info(
            "Created scan job. asset=%s scan=%s engine=%s",
            asset.id,
            scan.id,
            engine,
        )


        return scan



    async def create_and_queue_scan(
        self,
        asset_id: UUID,
        *,
        engine: ScanEngine,
        trigger: ScanTrigger = ScanTrigger.MANUAL,
        configuration: dict[str, Any] | None = None,
    ) -> Scan:
        """
        Create scan and immediately queue it.
        """

        scan = await self.create_scan_job(
            asset_id,
            engine=engine,
            trigger=trigger,
            configuration=configuration,
        )


        return await self.queue_scan(
            scan.id,
        )



    # ============================================================
    # Worker Management
    # ============================================================

    async def assign_worker(
        self,
        scan_id: UUID,
        worker_id: str,
    ) -> Scan:
        """
        Assign worker to scan.

        Used by:

        - Celery workers
        - Kubernetes jobs
        - Scanner agents
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        scan.worker_id = worker_id


        scan.worker_assigned_at = (
            datetime.utcnow()
        )


        await self.commit()


        await self.db.refresh(
            scan,
        )


        logger.info(
            "Worker assigned. scan=%s worker=%s",
            scan.id,
            worker_id,
        )


        return scan



    async def release_worker(
        self,
        scan_id: UUID,
    ) -> Scan:
        """
        Remove worker assignment.
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        scan.worker_id = None


        await self.commit()


        await self.db.refresh(
            scan,
        )


        return scan
        # ============================================================
    # Scanner Engine Routing
    # ============================================================

    async def select_engine(
        self,
        scan: Scan,
    ) -> ScanEngine:
        """
        Select execution engine for scan.

        Uses configured engine.

        Future extension:

        - AI based engine selection
        - Dynamic scanner selection
        - Cost optimization
        """

        if scan.engine not in self.scanner_registry:

            raise ValueError(
                f"No scanner available for {scan.engine}"
            )


        return scan.engine



    async def execute_engine(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Execute selected scanner engine.

        Flow:

        Scan
          |
          v
        Select Engine
          |
          v
        Execute Scanner
          |
          v
        Return Results
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        engine = await self.select_engine(
            scan,
        )


        scanner = (
            self.scanner_registry[
                engine
            ]
        )


        logger.info(
            "Executing scanner. scan=%s engine=%s",
            scan.id,
            engine,
        )


        results = await scanner(
            scan,
        )


        return {

            "scan_id":
                str(
                    scan.id
                ),

            "engine":
                engine.value,

            "results":
                results,

            "completed_at":
                datetime.utcnow().isoformat(),

        }



    async def start_scan_execution(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Start complete scan workflow.

        Lifecycle:

        QUEUED
          |
          v
        RUNNING
          |
          v
        ENGINE EXECUTION
          |
          v
        PROCESS RESULTS
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        if scan.status != ScanStatus.QUEUED:

            raise ValueError(
                "Scan must be queued before execution."
            )


        scan.status = (
            ScanStatus.RUNNING
        )


        scan.started_at = (
            datetime.utcnow()
        )


        await self.commit()


        try:

            result = await self.execute_engine(
                scan.id,
            )


            scan.status = (
                ScanStatus.COMPLETED
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()


            return result



        except Exception as exc:

            scan.status = (
                ScanStatus.FAILED
            )


            scan.error_message = (
                str(exc)
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()


            logger.exception(
                "Scan execution failed. scan=%s",
                scan.id,
            )


            raise



    async def cancel_scan(
        self,
        scan_id: UUID,
    ) -> Scan:
        """
        Cancel running scan.
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        scan.status = (
            ScanStatus.CANCELLED
        )


        scan.completed_at = (
            datetime.utcnow()
        )


        await self.commit()


        await self.db.refresh(
            scan,
        )


        logger.info(
            "Scan cancelled. id=%s",
            scan.id,
        )


        return scan
        # ============================================================
    # DNS Scanner Integration
    # ============================================================

    async def run_dns_scan(
        self,
        scan: Scan,
    ) -> dict[str, Any]:
        """
        Execute DNS security scan.

        Checks:

        - DNS resolution
        - Records
        - Subdomain exposure
        - DNS misconfiguration
        """

        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Running DNS scan. asset=%s",
            asset.asset_value,
        )


        results = {

            "scanner":
                "dns",

            "asset":
                asset.asset_value,

            "records":
                [],

            "issues":
                [],

            "status":
                "completed",

        }



        # --------------------------------------------------------
        # Placeholder integration layer
        #
        # Production implementation connects:
        #
        # - dnspython
        # - DNSSEC validator
        # - Subdomain discovery engine
        #
        # --------------------------------------------------------


        if not asset.fqdn:

            results["issues"].append(

                {

                    "title":
                        "Missing FQDN information",

                    "severity":
                        "low",

                    "category":
                        "dns",

                    "description":
                        (
                            "Asset DNS information "
                            "could not be fully validated."
                        ),

                }

            )



        return results



    async def run_dns_record_analysis(
        self,
        hostname: str,
    ) -> dict[str, Any]:
        """
        Analyze DNS records.

        Supported:

        - A
        - AAAA
        - MX
        - TXT
        - CNAME
        - NS
        """

        return {

            "hostname":
                hostname,

            "records":

                {

                    "A":
                        [],

                    "AAAA":
                        [],

                    "MX":
                        [],

                    "TXT":
                        [],

                    "CNAME":
                        [],

                    "NS":
                        [],

                },

            "security_checks":

                {

                    "dnssec":
                        "unknown",

                    "spf":
                        "unknown",

                    "dmarc":
                        "unknown",

                },

        }



    async def run_subdomain_discovery(
        self,
        domain: str,
    ) -> list[str]:
        """
        Discover subdomains.

        Future integrations:

        - Certificate transparency
        - Passive DNS
        - Wordlist discovery
        """

        discovered = []


        logger.info(
            "Subdomain discovery started. domain=%s",
            domain,
        )


        return discovered
        # ============================================================
    # HTTP Scanner Integration
    # ============================================================

    async def run_http_scan(
        self,
        scan: Scan,
    ) -> dict[str, Any]:
        """
        Execute HTTP security assessment.

        Checks:

        - HTTP availability
        - Security headers
        - Redirects
        - Technologies
        - Common exposures
        """

        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Running HTTP scan. asset=%s",
            asset.asset_value,
        )


        results = {

            "scanner":
                "http",

            "target":
                asset.asset_url(),

            "status":
                "completed",

            "response":
                {},

            "technologies":
                [],

            "issues":
                [],

        }



        # --------------------------------------------------------
        # HTTP Engine Integration Point
        #
        # Production:
        #
        # - httpx
        # - aiohttp
        # - Playwright
        # - Wappalyzer
        #
        # --------------------------------------------------------


        if not asset.scheme:

            results["issues"].append(

                {

                    "title":
                        "Missing HTTP scheme",

                    "severity":
                        "info",

                    "category":
                        "http",

                    "description":
                        (
                            "Unable to determine "
                            "HTTP protocol configuration."
                        ),

                }

            )



        header_results = (
            await self.analyze_security_headers(
                asset.asset_url(),
            )
        )


        results["security_headers"] = (
            header_results
        )


        return results



    async def analyze_security_headers(
        self,
        url: str,
    ) -> dict[str, Any]:
        """
        Analyze HTTP security headers.

        Checks:

        - CSP
        - HSTS
        - X-Frame-Options
        - X-Content-Type-Options
        """

        return {

            "url":
                url,

            "headers":

                {

                    "content_security_policy":
                        "unknown",

                    "strict_transport_security":
                        "unknown",

                    "x_frame_options":
                        "unknown",

                    "x_content_type_options":
                        "unknown",

                },


            "issues":

                [],

        }



    async def technology_detection(
        self,
        url: str,
    ) -> list[str]:
        """
        Detect web technologies.

        Examples:

        - Frameworks
        - Servers
        - CMS
        - Libraries
        """

        technologies = []


        logger.info(
            "Technology detection. url=%s",
            url,
        )


        return technologies



    async def crawl_endpoint(
        self,
        url: str,
        *,
        depth: int = 2,
    ) -> list[str]:
        """
        Basic endpoint discovery.

        Used for:

        - APIs
        - Web applications
        - Attack surface mapping
        """

        endpoints = []


        logger.info(
            "Crawling endpoint. url=%s depth=%s",
            url,
            depth,
        )


        return endpoints
        # ============================================================
    # TLS / Certificate Scanner Integration
    # ============================================================

    async def run_tls_scan(
        self,
        scan: Scan,
    ) -> dict[str, Any]:
        """
        Execute TLS security assessment.

        Checks:

        - Certificate validity
        - Expiration
        - TLS versions
        - Cipher configuration
        - Certificate chain
        """

        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Running TLS scan. asset=%s",
            asset.asset_value,
        )


        results = {

            "scanner":
                "tls",

            "target":
                asset.hostname_or_ip,

            "status":
                "completed",

            "certificate":
                {},

            "protocols":
                [],

            "ciphers":
                [],

            "issues":
                [],

        }



        certificate = (
            await self.inspect_certificate(
                asset.hostname_or_ip,
            )
        )


        results["certificate"] = (
            certificate
        )



        if certificate.get(
            "expired",
            False,
        ):

            results["issues"].append(

                {

                    "title":
                        "Expired TLS Certificate",

                    "severity":
                        "high",

                    "category":
                        "certificate",

                    "description":
                        (
                            "TLS certificate has expired "
                            "and should be replaced."
                        ),

                }

            )



        tls_versions = (
            await self.check_tls_versions(
                asset.hostname_or_ip,
            )
        )


        results["protocols"] = (
            tls_versions
        )


        return results



    async def inspect_certificate(
        self,
        hostname: str,
    ) -> dict[str, Any]:
        """
        Inspect TLS certificate.

        Production integration:

        - OpenSSL
        - cryptography
        - certifi
        """

        return {

            "hostname":
                hostname,

            "issuer":
                None,

            "subject":
                None,

            "valid_from":
                None,

            "valid_until":
                None,

            "expired":
                False,

            "chain_valid":
                True,

        }



    async def check_tls_versions(
        self,
        hostname: str,
    ) -> list[dict[str, Any]]:
        """
        Evaluate TLS protocol versions.
        """

        return [

            {

                "version":
                    "TLS1.3",

                "supported":
                    True,

            },

            {

                "version":
                    "TLS1.2",

                "supported":
                    True,

            },

            {

                "version":
                    "TLS1.0",

                "supported":
                    False,

            },

        ]



    async def analyze_cipher_security(
        self,
        hostname: str,
    ) -> dict[str, Any]:
        """
        Analyze cipher strength.

        Detects:

        - Weak ciphers
        - Deprecated algorithms
        - Quantum vulnerable primitives
        """

        return {

            "hostname":
                hostname,

            "weak_ciphers":
                [],

            "quantum_vulnerable":
                [],

            "recommended_action":
                (
                    "Adopt crypto-agility "
                    "and prepare PQC migration."
                ),

        }
        # ============================================================
    # Port / Network Scanner Integration
    # ============================================================

    async def run_port_scan(
        self,
        scan: Scan,
    ) -> dict[str, Any]:
        """
        Execute network port discovery.

        Checks:

        - Open ports
        - Services
        - Network exposure
        - Unexpected services
        """

        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Running port scan. asset=%s",
            asset.hostname_or_ip,
        )


        results = {

            "scanner":
                "port",

            "target":
                asset.hostname_or_ip,

            "status":
                "completed",

            "ports":
                [],

            "services":
                [],

            "issues":
                [],

        }



        # --------------------------------------------------------
        # Port Scanner Integration Point
        #
        # Production:
        #
        # - Nmap
        # - Masscan
        # - RustScan
        #
        # --------------------------------------------------------


        discovered_ports = (
            await self.discover_ports(
                asset.hostname_or_ip,
            )
        )


        results["ports"] = (
            discovered_ports
        )


        for port in discovered_ports:

            if port in (

                21,

                23,

                3389,

            ):

                results["issues"].append(

                    {

                        "title":
                            (
                                f"Risky exposed port "
                                f"{port}"
                            ),

                        "severity":
                            "medium",

                        "category":
                            "network",

                        "description":
                            (
                                "Review externally "
                                "accessible service."
                            ),

                    }

                )



        return results



    async def discover_ports(
        self,
        host: str,
    ) -> list[int]:
        """
        Discover open network ports.

        Future:

        - Async socket scanner
        - Nmap integration
        - Cloud scanner
        """

        logger.info(
            "Discovering ports. host=%s",
            host,
        )


        return []



    async def service_detection(
        self,
        host: str,
        ports: list[int],
    ) -> list[dict[str, Any]]:
        """
        Detect services running on ports.

        Example:

        443 -> HTTPS
        22  -> SSH
        3306 -> MySQL
        """

        services = []


        for port in ports:

            services.append(

                {

                    "port":
                        port,

                    "service":
                        "unknown",

                    "version":
                        None,

                }

            )


        return services



    async def network_exposure_analysis(
        self,
        asset_id: UUID,
    ) -> dict[str, Any]:
        """
        Analyze network exposure risk.
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

            "internet_facing":
                asset.internet_facing,

            "external":
                asset.external,

            "risk":

                (

                    "high"

                    if asset.internet_facing

                    else

                    "low"

                ),

        }
        # ============================================================
    # Post Quantum Cryptography Scanner Integration
    # ============================================================

    async def run_pqc_scan(
        self,
        scan: Scan,
    ) -> dict[str, Any]:
        """
        Execute PQC readiness assessment.

        Checks:

        - Cryptographic algorithms
        - TLS key exchange
        - Certificate algorithms
        - Quantum vulnerability
        - Migration readiness
        """

        asset = await self.get_asset(
            scan.asset_id,
        )


        if asset is None:

            raise ValueError(
                "Asset not found."
            )


        logger.info(
            "Running PQC scan. asset=%s",
            asset.asset_value,
        )


        results = {

            "scanner":
                "pqc",

            "asset":
                asset.asset_value,

            "status":
                "completed",

            "crypto_inventory":
                {},

            "quantum_risk":
                {},

            "recommendations":
                [],

            "issues":
                [],

        }



        crypto_inventory = (
            await self.collect_crypto_inventory(
                asset,
            )
        )


        results["crypto_inventory"] = (
            crypto_inventory
        )



        quantum_risk = (
            await self.evaluate_quantum_risk(
                crypto_inventory,
            )
        )


        results["quantum_risk"] = (
            quantum_risk
        )



        if quantum_risk["risk_level"] in (

            "high",

            "critical",

        ):

            results["issues"].append(

                {

                    "title":
                        (
                            "Quantum Vulnerable "
                            "Cryptography Detected"
                        ),

                    "severity":
                        "high",

                    "category":
                        "pqc",

                    "description":
                        (
                            "Current cryptographic "
                            "configuration may be "
                            "vulnerable to future "
                            "quantum attacks."
                        ),

                }

            )



        results["recommendations"] = (

            await self.generate_pqc_actions(
                quantum_risk,
            )

        )


        return results



    async def collect_crypto_inventory(
        self,
        asset: Asset,
    ) -> dict[str, Any]:
        """
        Collect cryptographic information.

        Tracks:

        - Algorithms
        - Certificates
        - Protocols
        - Key sizes
        """

        return {

            "asset":
                asset.asset_value,

            "algorithms":

                [

                    "RSA",

                    "ECDSA",

                    "AES",

                ],

            "key_exchange":

                [

                    "ECDHE",

                ],

            "certificate_algorithm":
                "RSA",

            "crypto_agility":
                False,

        }



    async def evaluate_quantum_risk(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate quantum threat exposure.

        Current focus:

        - RSA
        - ECC
        - Static keys
        """

        risk_score = 0


        algorithms = (
            inventory.get(
                "algorithms",
                [],
            )
        )


        if "RSA" in algorithms:

            risk_score += 40


        if "ECDSA" in algorithms:

            risk_score += 40


        if not inventory.get(
            "crypto_agility",
            False,
        ):

            risk_score += 20



        risk_score = min(
            100,
            risk_score,
        )



        level = "low"


        if risk_score >= 80:

            level = "critical"


        elif risk_score >= 60:

            level = "high"


        elif risk_score >= 30:

            level = "medium"



        return {

            "risk_score":
                risk_score,

            "risk_level":
                level,

        }



    async def generate_pqc_actions(
        self,
        quantum_risk: dict[str, Any],
    ) -> list[str]:
        """
        Generate PQC migration actions.
        """

        actions = []


        if quantum_risk["risk_score"] >= 60:

            actions.extend(

                [

                    "Create cryptographic inventory.",

                    "Enable crypto-agility architecture.",

                    "Evaluate hybrid PQC deployment.",

                    "Prepare migration roadmap.",

                ]

            )


        else:

            actions.append(

                "Continue monitoring cryptographic posture."

            )


        return actions
        # ============================================================
    # Scan Execution Workflow
    # ============================================================

    async def execute_scan_workflow(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Complete scanner workflow.

        Pipeline:

        1. Validate scan
        2. Start execution
        3. Run scanner engine
        4. Process results
        5. Create findings
        6. Update risk
        7. Generate recommendations
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        try:

            # ----------------------------------------------------
            # Start Scan
            # ----------------------------------------------------

            scan.status = (
                ScanStatus.RUNNING
            )


            scan.started_at = (
                datetime.utcnow()
            )


            await self.commit()



            # ----------------------------------------------------
            # Execute Engine
            # ----------------------------------------------------

            execution_result = (
                await self.execute_engine(
                    scan.id,
                )
            )



            # ----------------------------------------------------
            # Process Results
            # ----------------------------------------------------

            findings = (
                await self.process_scan_results(
                    scan,
                    execution_result,
                )
            )



            # ----------------------------------------------------
            # Risk Update
            # ----------------------------------------------------

            await self.risk_service.calculate_scan_risk(
                scan.id,
            )



            # ----------------------------------------------------
            # Recommendations
            # ----------------------------------------------------

            await self.recommendation_service.generate_scan_recommendations(
                scan.id,
            )



            scan.status = (
                ScanStatus.COMPLETED
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()



            return {

                "scan_id":
                    str(
                        scan.id
                    ),

                "status":
                    "completed",

                "findings":
                    len(
                        findings
                    ),

                "completed_at":
                    scan.completed_at.isoformat(),

            }



        except Exception as exc:

            scan.status = (
                ScanStatus.FAILED
            )


            scan.error_message = (
                str(exc)
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()


            logger.exception(
                "Scan workflow failed. id=%s",
                scan.id,
            )


            raise



    async def process_scan_results(
        self,
        scan: Scan,
        result: dict[str, Any],
    ) -> list[Finding]:
        """
        Convert scanner output into findings.

        Supports:

        - DNS issues
        - HTTP issues
        - TLS issues
        - Network issues
        - PQC issues
        """

        created = []


        issues = (
            result
            .get(
                "results",
                {}
            )
            .get(
                "issues",
                []
            )
        )



        for issue in issues:

            finding = Finding(

                scan_id=scan.id,

                title=issue.get(
                    "title",
                    "Scanner Finding",
                ),

                description=issue.get(
                    "description",
                ),

                severity=self.map_severity(
                    issue.get(
                        "severity",
                        "info",
                    )
                ),

                category=issue.get(
                    "category",
                ),

                discovered_at=datetime.utcnow(),

            )


            self.db.add(
                finding,
            )


            created.append(
                finding,
            )



        if created:

            await self.commit()


            for finding in created:

                await self.db.refresh(
                    finding,
                )


        return created



    @staticmethod
    def map_severity(
        severity: str,
    ):
        """
        Convert scanner severity
        into database enum.
        """

        value = (
            severity.lower()
        )


        mapping = {

            "critical":
                "critical",

            "high":
                "high",

            "medium":
                "medium",

            "low":
                "low",

        }


        from app.models.finding import FindingSeverity


        return FindingSeverity(
            mapping.get(
                value,
                "info",
            )
        )
        # ============================================================
    # Scan Execution Workflow
    # ============================================================

    async def execute_scan_workflow(
        self,
        scan_id: UUID,
    ) -> dict[str, Any]:
        """
        Complete scanner workflow.

        Pipeline:

        1. Validate scan
        2. Start execution
        3. Run scanner engine
        4. Process results
        5. Create findings
        6. Update risk
        7. Generate recommendations
        """

        scan = await self.get_scan(
            scan_id,
        )


        if scan is None:

            raise ValueError(
                "Scan not found."
            )


        try:

            # ----------------------------------------------------
            # Start Scan
            # ----------------------------------------------------

            scan.status = (
                ScanStatus.RUNNING
            )


            scan.started_at = (
                datetime.utcnow()
            )


            await self.commit()



            # ----------------------------------------------------
            # Execute Engine
            # ----------------------------------------------------

            execution_result = (
                await self.execute_engine(
                    scan.id,
                )
            )



            # ----------------------------------------------------
            # Process Results
            # ----------------------------------------------------

            findings = (
                await self.process_scan_results(
                    scan,
                    execution_result,
                )
            )



            # ----------------------------------------------------
            # Risk Update
            # ----------------------------------------------------

            await self.risk_service.calculate_scan_risk(
                scan.id,
            )



            # ----------------------------------------------------
            # Recommendations
            # ----------------------------------------------------

            await self.recommendation_service.generate_scan_recommendations(
                scan.id,
            )



            scan.status = (
                ScanStatus.COMPLETED
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()



            return {

                "scan_id":
                    str(
                        scan.id
                    ),

                "status":
                    "completed",

                "findings":
                    len(
                        findings
                    ),

                "completed_at":
                    scan.completed_at.isoformat(),

            }



        except Exception as exc:

            scan.status = (
                ScanStatus.FAILED
            )


            scan.error_message = (
                str(exc)
            )


            scan.completed_at = (
                datetime.utcnow()
            )


            await self.commit()


            logger.exception(
                "Scan workflow failed. id=%s",
                scan.id,
            )


            raise



    async def process_scan_results(
        self,
        scan: Scan,
        result: dict[str, Any],
    ) -> list[Finding]:
        """
        Convert scanner output into findings.

        Supports:

        - DNS issues
        - HTTP issues
        - TLS issues
        - Network issues
        - PQC issues
        """

        created = []


        issues = (
            result
            .get(
                "results",
                {}
            )
            .get(
                "issues",
                []
            )
        )



        for issue in issues:

            finding = Finding(

                scan_id=scan.id,

                title=issue.get(
                    "title",
                    "Scanner Finding",
                ),

                description=issue.get(
                    "description",
                ),

                severity=self.map_severity(
                    issue.get(
                        "severity",
                        "info",
                    )
                ),

                category=issue.get(
                    "category",
                ),

                discovered_at=datetime.utcnow(),

            )


            self.db.add(
                finding,
            )


            created.append(
                finding,
            )



        if created:

            await self.commit()


            for finding in created:

                await self.db.refresh(
                    finding,
                )


        return created



    @staticmethod
    def map_severity(
        severity: str,
    ):
        """
        Convert scanner severity
        into database enum.
        """

        value = (
            severity.lower()
        )


        mapping = {

            "critical":
                "critical",

            "high":
                "high",

            "medium":
                "medium",

            "low":
                "low",

        }


        from app.models.finding import FindingSeverity


        return FindingSeverity(
            mapping.get(
                value,
                "info",
            )
        )
    