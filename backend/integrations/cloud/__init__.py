"""
QShield Enterprise
==================

Cloud Integration Layer.

This package provides connectors
for enterprise cloud platforms.

Supported Providers:

- AWS
- Microsoft Azure
- Google Cloud Platform

Capabilities:

- Key Management Services
- Cloud storage
- Identity services
- Infrastructure monitoring
- Secure cloud operations

Architecture:

QShield

  |

  v

Cloud Integration Layer

  |

  +---------------+---------------+

  |               |               |

  v               v               v

 AWS             Azure            GCP

 KMS             Key Vault        Cloud KMS

 S3              Blob Storage     Cloud Storage

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "cloud_manager",

    "aws",

    "azure",

    "gcp",

]