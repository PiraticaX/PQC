"""
QShield Enterprise
==================

Storage Integration Layer.

This package provides secure storage
connectors for enterprise data.

Supported Providers:

- AWS S3
- Azure Blob Storage
- Cloud Object Storage
- Secure File Storage

Capabilities:

- Report storage
- Backup storage
- Security artifact storage
- Encrypted object management
- File lifecycle management

Architecture:

QShield

  |

  v

Storage Integration Layer

  |

  +----------------+----------------+

  |                |                |

  v                v                v

 AWS S3       Azure Blob       Object Storage

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "storage_manager",

    "s3",

    "azure_blob",

]