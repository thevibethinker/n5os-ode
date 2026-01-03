#!/usr/bin/env python3
"""
CRM Paths - Centralized path constants for all CRM-related scripts.

This module establishes the SINGLE SOURCE OF TRUTH for CRM file locations.
All CRM scripts should import paths from here rather than defining their own.

Canonical locations (as of 2026-01):
- Database: Personal/Knowledge/CRM/db/crm.db
- Profiles: Personal/Knowledge/CRM/individuals/*.md
- Index: Personal/Knowledge/CRM/individuals/index.jsonl
"""

from pathlib import Path

WORKSPACE = Path("/home/workspace")

# =============================================================================
# CANONICAL CRM LOCATIONS
# =============================================================================

CRM_ROOT = WORKSPACE / "Personal/Knowledge/CRM"
CRM_DB = CRM_ROOT / "db/crm.db"
CRM_INDIVIDUALS = CRM_ROOT / "individuals"
CRM_ORGANIZATIONS = CRM_ROOT / "organizations"
CRM_VIEWS = CRM_ROOT / "views"
CRM_INDEX = CRM_INDIVIDUALS / "index.jsonl"

# =============================================================================
# MEETINGS
# =============================================================================

MEETINGS_ROOT = WORKSPACE / "Personal/Meetings"
MEETINGS_INBOX = MEETINGS_ROOT / "Inbox"

# =============================================================================
# LEGACY PATHS (for migration reference only - DO NOT USE in new code)
# =============================================================================

LEGACY_CRM_DIR = WORKSPACE / "Knowledge/crm/individuals"
LEGACY_CRM_INDEX = LEGACY_CRM_DIR / "index.jsonl"
LEGACY_PROFILES_DB = WORKSPACE / "N5/data/profiles.db"
LEGACY_CRM_V3_DB = WORKSPACE / "N5/data/crm_v3.db"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_profile_path(slug: str) -> Path:
    """Get the canonical path for a profile by slug."""
    return CRM_INDIVIDUALS / f"{slug}.md"


def slug_from_path(path: Path) -> str:
    """Extract slug from a profile path."""
    return path.stem


def ensure_crm_dirs():
    """Ensure all CRM directories exist."""
    CRM_ROOT.mkdir(parents=True, exist_ok=True)
    CRM_INDIVIDUALS.mkdir(parents=True, exist_ok=True)
    CRM_ORGANIZATIONS.mkdir(parents=True, exist_ok=True)
    CRM_VIEWS.mkdir(parents=True, exist_ok=True)
    (CRM_ROOT / "db").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    print("CRM Paths Configuration")
    print("=" * 50)
    print(f"CRM_ROOT:        {CRM_ROOT}")
    print(f"CRM_DB:          {CRM_DB}")
    print(f"CRM_INDIVIDUALS: {CRM_INDIVIDUALS}")
    print(f"CRM_INDEX:       {CRM_INDEX}")
    print(f"MEETINGS_ROOT:   {MEETINGS_ROOT}")
    print()
    print("Legacy paths (for reference):")
    print(f"LEGACY_CRM_DIR:     {LEGACY_CRM_DIR}")
    print(f"LEGACY_PROFILES_DB: {LEGACY_PROFILES_DB}")
