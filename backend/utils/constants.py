"""
QShield Enterprise
==================

Global Utility Constants.

Contains:

- System constants
- Security constants
- Validation limits
- File handling limits
- Common configuration values

This module must remain dependency-free.

"""

from __future__ import annotations



# ============================================================
# Application
# ============================================================


APPLICATION_NAME = "QShield Enterprise"


APPLICATION_VERSION = "1.0.0"


ENVIRONMENT_DEVELOPMENT = "development"


ENVIRONMENT_PRODUCTION = "production"


DEFAULT_TIMEZONE = "UTC"



# ============================================================
# Security Constants
# ============================================================


MIN_PASSWORD_LENGTH = 12


MAX_PASSWORD_LENGTH = 128


HASH_ALGORITHM = "SHA256"


TOKEN_EXPIRY_MINUTES = 30


REFRESH_TOKEN_EXPIRY_DAYS = 30



# Authentication

AUTH_HEADER_PREFIX = "Bearer"


API_KEY_PREFIX = "qsk_"



# Encryption

DEFAULT_ENCRYPTION_ALGORITHM = "AES-256-GCM"


KEY_SIZE_BYTES = 32


IV_SIZE_BYTES = 12



# ============================================================
# Cryptography / PQC Constants
# ============================================================


PQC_ALGORITHMS = [

    "CRYSTALS-Kyber",

    "CRYSTALS-Dilithium",

    "SPHINCS+",

    "Falcon",

]


DEFAULT_PQC_KEM = "CRYSTALS-Kyber"


DEFAULT_PQC_SIGNATURE = "CRYSTALS-Dilithium"



# ============================================================
# File Constants
# ============================================================


MAX_FILE_SIZE_MB = 100


MAX_FILE_SIZE_BYTES = (

    MAX_FILE_SIZE_MB

    *

    1024

    *

    1024

)



ALLOWED_FILE_EXTENSIONS = [

    ".pdf",

    ".json",

    ".csv",

    ".txt",

    ".zip",

]



TEMP_DIRECTORY = "/tmp/qshield"



# ============================================================
# Database Constants
# ============================================================


DEFAULT_PAGE_SIZE = 50


MAX_PAGE_SIZE = 500



DATABASE_CONNECTION_TIMEOUT = 30



# ============================================================
# API Constants
# ============================================================


API_VERSION = "v1"


API_PREFIX = "/api"



DEFAULT_RESPONSE_STATUS = "success"



# Pagination

DEFAULT_OFFSET = 0



# ============================================================
# Worker Constants
# ============================================================


DEFAULT_WORKER_TIMEOUT_SECONDS = 300


MAX_WORKER_RETRIES = 3



WORKER_STATUS_RUNNING = "running"


WORKER_STATUS_STOPPED = "stopped"


WORKER_STATUS_FAILED = "failed"



# ============================================================
# Event Constants
# ============================================================


EVENT_SECURITY_ALERT = "security.alert"


EVENT_KEY_ROTATED = "key.rotated"


EVENT_BACKUP_COMPLETED = "backup.completed"


EVENT_SCAN_COMPLETED = "scan.completed"


EVENT_REPORT_GENERATED = "report.generated"


EVENT_COMPLIANCE_COMPLETED = "compliance.completed"



# ============================================================
# Integration Constants
# ============================================================


SUPPORTED_CLOUD_PROVIDERS = [

    "aws",

    "azure",

    "gcp",

]


SUPPORTED_QUANTUM_PROVIDERS = [

    "ibm_quantum",

    "dwave",

    "local_simulator",

]


SUPPORTED_SIEM_PROVIDERS = [

    "splunk",

    "sentinel",

]



# ============================================================
# Risk Severity
# ============================================================


RISK_LEVELS = [

    "low",

    "medium",

    "high",

    "critical",

]



RISK_SCORE_MIN = 0


RISK_SCORE_MAX = 100



# ============================================================
# Compliance
# ============================================================


COMPLIANCE_FRAMEWORKS = [

    "ISO27001",

    "SOC2",

    "NIST",

    "GDPR",

    "PCI_DSS",

]



# ============================================================
# Logging
# ============================================================


LOG_FORMAT = (

    "%(asctime)s "

    "%(levelname)s "

    "%(name)s "

    "%(message)s"

)



LOG_LEVEL_INFO = "INFO"


LOG_LEVEL_WARNING = "WARNING"


LOG_LEVEL_ERROR = "ERROR"