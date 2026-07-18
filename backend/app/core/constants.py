"""
QShield Enterprise
==================

Core System Constants.

Centralized immutable values used across:

- API layer
- Services layer
- Database models
- Security engine
- PQC modules
- Compliance modules
- Background workers

"""

from __future__ import annotations



# ============================================================
# Application
# ============================================================


APP_NAME = "QShield Enterprise"


APP_VERSION = "1.0.0"


DEFAULT_API_VERSION = "v1"



# ============================================================
# Environment
# ============================================================


ENV_DEVELOPMENT = "development"


ENV_TESTING = "testing"


ENV_STAGING = "staging"


ENV_PRODUCTION = "production"



# ============================================================
# User Roles
# ============================================================


ROLE_SUPER_ADMIN = "super_admin"


ROLE_ADMIN = "admin"


ROLE_SECURITY_ANALYST = "security_analyst"


ROLE_AUDITOR = "auditor"


ROLE_USER = "user"


ROLE_SERVICE_ACCOUNT = "service_account"



SYSTEM_ROLES = [

    ROLE_SUPER_ADMIN,

    ROLE_ADMIN,

    ROLE_SECURITY_ANALYST,

    ROLE_AUDITOR,

    ROLE_USER,

    ROLE_SERVICE_ACCOUNT,

]



# ============================================================
# Permission Actions
# ============================================================


PERMISSION_READ = "read"


PERMISSION_WRITE = "write"


PERMISSION_CREATE = "create"


PERMISSION_UPDATE = "update"


PERMISSION_DELETE = "delete"


PERMISSION_EXECUTE = "execute"


PERMISSION_ADMIN = "admin"



# ============================================================
# User Status
# ============================================================


USER_ACTIVE = "active"


USER_INACTIVE = "inactive"


USER_SUSPENDED = "suspended"


USER_PENDING = "pending"


USER_DELETED = "deleted"



# ============================================================
# Organization Status
# ============================================================


ORG_ACTIVE = "active"


ORG_SUSPENDED = "suspended"


ORG_PENDING = "pending"



# ============================================================
# Security Severity Levels
# ============================================================


SEVERITY_INFO = "info"


SEVERITY_LOW = "low"


SEVERITY_MEDIUM = "medium"


SEVERITY_HIGH = "high"


SEVERITY_CRITICAL = "critical"



SEVERITY_LEVELS = [

    SEVERITY_INFO,

    SEVERITY_LOW,

    SEVERITY_MEDIUM,

    SEVERITY_HIGH,

    SEVERITY_CRITICAL,

]



# ============================================================
# Risk Levels
# ============================================================


RISK_LOW = "low"


RISK_MEDIUM = "medium"


RISK_HIGH = "high"


RISK_CRITICAL = "critical"



RISK_LEVELS = [

    RISK_LOW,

    RISK_MEDIUM,

    RISK_HIGH,

    RISK_CRITICAL,

]



# ============================================================
# Finding Status
# ============================================================


FINDING_OPEN = "open"


FINDING_INVESTIGATING = "investigating"


FINDING_MITIGATED = "mitigated"


FINDING_RESOLVED = "resolved"


FINDING_ACCEPTED = "accepted"



# ============================================================
# Scan Status
# ============================================================


SCAN_PENDING = "pending"


SCAN_RUNNING = "running"


SCAN_COMPLETED = "completed"


SCAN_FAILED = "failed"


SCAN_CANCELLED = "cancelled"



# ============================================================
# Job / Queue Status
# ============================================================


JOB_PENDING = "pending"


JOB_RUNNING = "running"


JOB_COMPLETED = "completed"


JOB_FAILED = "failed"


JOB_CANCELLED = "cancelled"


JOB_RETRYING = "retrying"



# ============================================================
# Backup Status
# ============================================================


BACKUP_CREATED = "created"


BACKUP_RUNNING = "running"


BACKUP_COMPLETED = "completed"


BACKUP_FAILED = "failed"


BACKUP_RESTORED = "restored"



# ============================================================
# Cryptography Constants
# ============================================================


AES_256 = "AES-256"


AES_192 = "AES-192"


AES_128 = "AES-128"



HASH_SHA256 = "SHA-256"


HASH_SHA512 = "SHA-512"


HASH_BLAKE3 = "BLAKE3"



# ============================================================
# Post Quantum Cryptography
# ============================================================


PQC_KYBER = "CRYSTALS-KYBER"


PQC_DILITHIUM = "CRYSTALS-DILITHIUM"


PQC_FALCON = "FALCON"


PQC_SPHINCS = "SPHINCS+"



PQC_KEM_ALGORITHMS = [

    PQC_KYBER,

]



PQC_SIGNATURE_ALGORITHMS = [

    PQC_DILITHIUM,

    PQC_FALCON,

    PQC_SPHINCS,

]



# ============================================================
# Encryption Classification
# ============================================================


DATA_PUBLIC = "public"


DATA_INTERNAL = "internal"


DATA_CONFIDENTIAL = "confidential"


DATA_RESTRICTED = "restricted"


DATA_TOP_SECRET = "top_secret"



# ============================================================
# Event Types
# ============================================================


EVENT_USER_CREATED = "user.created"


EVENT_USER_LOGIN = "user.login"


EVENT_USER_LOGOUT = "user.logout"


EVENT_PERMISSION_CHANGED = "permission.changed"


EVENT_KEY_ROTATED = "key.rotated"


EVENT_KEY_REVOKED = "key.revoked"


EVENT_SECURITY_ALERT = "security.alert"


EVENT_SCAN_COMPLETED = "scan.completed"


EVENT_BACKUP_COMPLETED = "backup.completed"



# ============================================================
# Integration Types
# ============================================================


INTEGRATION_API = "api"


INTEGRATION_WEBHOOK = "webhook"


INTEGRATION_DATABASE = "database"


INTEGRATION_STORAGE = "storage"


INTEGRATION_IDENTITY = "identity"



# ============================================================
# Report Types
# ============================================================


REPORT_SECURITY = "security"


REPORT_COMPLIANCE = "compliance"


REPORT_RISK = "risk"


REPORT_AUDIT = "audit"


REPORT_EXECUTIVE = "executive"



# ============================================================
# Compliance Frameworks
# ============================================================


FRAMEWORK_ISO27001 = "ISO27001"


FRAMEWORK_SOC2 = "SOC2"


FRAMEWORK_NIST = "NIST"


FRAMEWORK_GDPR = "GDPR"


FRAMEWORK_PCI_DSS = "PCI_DSS"



SUPPORTED_FRAMEWORKS = [

    FRAMEWORK_ISO27001,

    FRAMEWORK_SOC2,

    FRAMEWORK_NIST,

    FRAMEWORK_GDPR,

    FRAMEWORK_PCI_DSS,

]



# ============================================================
# Pagination Defaults
# ============================================================


DEFAULT_PAGE_SIZE = 20


MAX_PAGE_SIZE = 100



# ============================================================
# Security Limits
# ============================================================


MAX_LOGIN_ATTEMPTS = 5


PASSWORD_EXPIRY_DAYS = 90


API_KEY_EXPIRY_DAYS = 365



# ============================================================
# Time Constants
# ============================================================


SECONDS_PER_MINUTE = 60


SECONDS_PER_HOUR = 3600


SECONDS_PER_DAY = 86400



# ============================================================
# File Storage
# ============================================================


MAX_FILE_SIZE_MB = 100


ALLOWED_REPORT_FORMATS = [

    "pdf",

    "csv",

    "json",

    "html",

]



# ============================================================
# Default Messages
# ============================================================


SYSTEM_HEALTHY = "healthy"


SYSTEM_DEGRADED = "degraded"


SYSTEM_UNAVAILABLE = "unavailable"