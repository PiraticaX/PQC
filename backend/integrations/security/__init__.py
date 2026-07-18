"""
QShield Enterprise
==================

Security Integration Layer.

This package provides connectors
for enterprise security platforms.

Supported Systems:

- SIEM Platforms
- Security Monitoring Systems
- Threat Intelligence Platforms
- Incident Response Systems

Capabilities:

- Security event forwarding
- Log ingestion
- Alert synchronization
- Threat intelligence exchange
- SOC automation

Architecture:

QShield

  |

  v

Security Integration Layer

  |

  +----------------+----------------+

  |                |                |

  v                v                v

 SIEM          Threat Intel       SOC Tools

 Splunk        Feeds             Response

 Sentinel

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "security_manager",

    "siem",

    "splunk",

    "sentinel",

]