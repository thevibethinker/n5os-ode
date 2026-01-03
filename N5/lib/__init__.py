"""
N5 Library Package
==================

Shared utilities and constants for N5 scripts.

Modules:
    - paths: Centralized path constants
    - db: Database connection pooling
    - cache: File and preference caching
    - secrets: Secret management utilities
"""

from N5.lib import paths
from N5.lib import db
from N5.lib import cache
from N5.lib import secrets

__all__ = ["paths", "db", "cache", "secrets"]
