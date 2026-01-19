#!/usr/bin/env python3
"""
Unified Database Paths - Single source of truth for n5_core.db access.

All scripts should import from here:
    from db_paths import get_db_connection, N5_CORE_DB

Created: 2026-01-19
Purpose: Consolidate CRM, deals, and related data into unified database
"""

from pathlib import Path
import sqlite3

WORKSPACE = Path("/home/workspace")
N5_DATA_DIR = WORKSPACE / "N5/data"
N5_CORE_DB = N5_DATA_DIR / "n5_core.db"


def get_db_connection(readonly: bool = False) -> sqlite3.Connection:
    """Get connection to unified database with FK enforcement."""
    uri = f"file:{N5_CORE_DB}"
    if readonly:
        uri += "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =============================================================================
# TABLE NAME CONSTANTS
# =============================================================================

PEOPLE_TABLE = "people"
ORGANIZATIONS_TABLE = "organizations"
DEALS_TABLE = "deals"
DEAL_ROLES_TABLE = "deal_roles"
INTERACTIONS_TABLE = "interactions"
CALENDAR_EVENTS_TABLE = "calendar_events"

# =============================================================================
# LEGACY DATABASE PATHS (for migration scripts only)
# =============================================================================

LEGACY_CRM_DB = WORKSPACE / "Personal/Knowledge/CRM/db/crm.db"
LEGACY_CRM_V3_DB = N5_DATA_DIR / "crm_v3.db"
LEGACY_DEALS_DB = N5_DATA_DIR / "deals.db"


if __name__ == "__main__":
    print("Unified Database Paths")
    print("=" * 50)
    print(f"N5_CORE_DB: {N5_CORE_DB}")
    print(f"Exists: {N5_CORE_DB.exists()}")
    print()
    print("Tables:")
    print(f"  - {PEOPLE_TABLE}")
    print(f"  - {ORGANIZATIONS_TABLE}")
    print(f"  - {DEALS_TABLE}")
    print(f"  - {DEAL_ROLES_TABLE}")
    print(f"  - {INTERACTIONS_TABLE}")
    print(f"  - {CALENDAR_EVENTS_TABLE}")
    print()
    
    if N5_CORE_DB.exists():
        try:
            conn = get_db_connection(readonly=True)
            print("Connection: OK")
            conn.close()
        except Exception as e:
            print(f"Connection: FAILED - {e}")
    else:
        print("Connection: SKIPPED (database not yet created)")
