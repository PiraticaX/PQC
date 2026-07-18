"""
QShield Enterprise
==================

Security Event Test Fixtures.

Provides:

- Security alerts
- Incident events
- Audit events
- SIEM events
- PQC migration events
- Threat scenarios

Used across:

- Security tests
- SIEM integration tests
- Notification tests
- Audit tests
- Risk analysis tests

"""

from __future__ import annotations



from datetime import datetime
from datetime import timezone



from typing import Any



# ============================================================
# Event Factory
# ============================================================


def create_security_event(
    event_id: str = "evt_test001",
    event_type: str = "security.alert",
    severity: str = "medium",
) -> dict[str, Any]:
    """
    Create generic security event.

    """

    return {

        "id":

            event_id,


        "type":

            event_type,


        "severity":

            severity,


        "source":

            "qshield-test",


        "timestamp":

            datetime.now(

                timezone.utc

            ).isoformat(),


        "details":

            {},


    }



# ============================================================
# Security Alerts
# ============================================================


def critical_security_alert() -> dict[str, Any]:
    """
    Critical security alert.

    """

    return {

        "id":

            "evt_critical001",


        "type":

            "security.alert",


        "severity":

            "critical",


        "title":

            "Unauthorized access detected",


        "source":

            "SIEM",


        "status":

            "open",


        "affected_asset":

            "ast_server001",


        "risk_score":

            95,

    }



def malware_detection_event() -> dict[str, Any]:
    """
    Malware detection event.

    """

    return {

        "id":

            "evt_malware001",


        "type":

            "threat.detected",


        "severity":

            "high",


        "threat":

            {

                "name":

                    "TestMalware",


                "category":

                    "malware",


            },


        "host":

            "server-test-01",


        "action":

            "blocked",

    }



# ============================================================
# Authentication Events
# ============================================================


def failed_login_event() -> dict[str, Any]:
    """
    Failed authentication attempt.

    """

    return {

        "id":

            "evt_auth001",


        "type":

            "authentication.failed",


        "severity":

            "medium",


        "user":

            "unknown-user",


        "ip_address":

            "192.168.1.100",


        "attempts":

            5,

    }



def suspicious_login_event() -> dict[str, Any]:
    """
    Suspicious login event.

    """

    return {

        "id":

            "evt_auth002",


        "type":

            "authentication.suspicious",


        "severity":

            "high",


        "user":

            "admin",


        "location":

            "unknown",


        "risk_score":

            80,

    }



# ============================================================
# PQC Events
# ============================================================


def pqc_migration_event() -> dict[str, Any]:
    """
    Post quantum migration event.

    """

    return {

        "id":

            "evt_pqc001",


        "type":

            "pqc.migration",


        "severity":

            "info",


        "asset":

            "enterprise-crypto-system",


        "old_algorithm":

            "RSA-2048",


        "new_algorithm":

            "CRYSTALS-Kyber",


        "status":

            "completed",

    }



# ============================================================
# Audit Events
# ============================================================


def audit_event() -> dict[str, Any]:
    """
    Security audit event.

    """

    return {

        "id":

            "evt_audit001",


        "type":

            "audit.activity",


        "severity":

            "info",


        "user":

            "admin",


        "action":

            "configuration_changed",


        "resource":

            "security_policy",

    }



# ============================================================
# SIEM Events
# ============================================================


def siem_event() -> dict[str, Any]:
    """
    External SIEM event.

    """

    return {

        "id":

            "evt_siem001",


        "type":

            "siem.ingest",


        "severity":

            "high",


        "provider":

            "splunk",


        "raw_event":

            {

                "message":

                    "Suspicious activity detected",

            },

    }



# ============================================================
# Collections
# ============================================================


def security_event_collection() -> list[dict[str, Any]]:
    """
    Collection of security events.

    """

    return [

        critical_security_alert(),

        malware_detection_event(),

        failed_login_event(),

        suspicious_login_event(),

        pqc_migration_event(),

        audit_event(),

        siem_event(),

    ]