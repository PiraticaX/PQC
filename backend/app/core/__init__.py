"""
QShield Enterprise
==================

Core Package

Shared backend infrastructure layer.

This package provides:

- Application configuration
- Database connectivity
- Security primitives
- Middleware components
- Global dependencies
- Exception handling
- Logging infrastructure
- Encryption utilities
- Caching
- Rate limiting
- Platform constants

All modules inside this package are foundational
components consumed across:

- API layer
- Services layer
- Models layer
- Background workers
- Integrations

"""



__version__ = "1.0.0"



__author__ = "QShield Enterprise"



__all__ = [

    "config",

    "database",

    "security",

    "dependencies",

    "middleware",

    "exceptions",

    "logging",

    "cache",

    "encryption",

    "rate_limit",

    "constants",

]