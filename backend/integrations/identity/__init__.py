"""
QShield Enterprise
==================

Identity Integration Layer.

This package provides enterprise
identity and access management
connectors.

Supported Providers:

- OAuth2 / OpenID Connect
- LDAP
- SAML SSO

Capabilities:

- Enterprise authentication
- Identity federation
- User synchronization
- Single Sign-On
- Access management integration

Architecture:

QShield

  |

  v

Identity Integration Layer

  |

  +----------------+----------------+

  |                |                |

  v                v                v

 OAuth2          LDAP            SAML

 OIDC            Directory       SSO

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "oauth",

    "ldap",

    "saml",

]