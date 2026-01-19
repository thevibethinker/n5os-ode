#!/usr/bin/env python3
"""
CRM Paths - Centralized path constants for all CRM-related scripts.

This module establishes the SINGLE SOURCE OF TRUTH for CRM file locations.
All CRM scripts should import paths from here rather than defining their own.

UPDATED 2026-01-19: CRM data now lives in unified n5_core.db
- Markdown profiles remain in Personal/Knowledge/CRM/
- Database records consolidated into N5/data/n5_core.db
"""

from pathlib import Path

WORKSPACE = Path("/home/workspace")

# =============================================================================
# UNIFIED DATABASE (NEW - 2026-01-19)
# =============================================================================

N5_DATA_DIR = WORKSPACE / "N5/data"
N5_CORE_DB = N5_DATA_DIR / "n5_core.db"

# Primary database - use this for all CRM queries
CRM_DB = N5_CORE_DB  # DEPRECATED name, use N5_CORE_DB
DEALS_DB = N5_CORE_DB  # Alias for deals access

# =============================================================================
# MARKDOWN PROFILE LOCATIONS (unchanged)
# =============================================================================

CRM_ROOT = WORKSPACE / "Personal/Knowledge/CRM"
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
LEGACY_CRM_DB = CRM_ROOT / "db/crm.db"
LEGACY_DEALS_DB = N5_DATA_DIR / "deals.db"

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
    print("CRM Paths Configuration (Updated 2026-01-19)")
    print("=" * 50)
    print(f"N5_CORE_DB:      {N5_CORE_DB}")
    print(f"CRM_DB:          {CRM_DB} (alias for N5_CORE_DB)")
    print(f"DEALS_DB:        {DEALS_DB} (alias for N5_CORE_DB)")
    print()
    print("Markdown Profiles:")
    print(f"CRM_INDIVIDUALS: {CRM_INDIVIDUALS}")
    print(f"CRM_ORGANIZATIONS: {CRM_ORGANIZATIONS}")
    print(f"CRM_INDEX:       {CRM_INDEX}")
    print()
    print("Legacy paths (deprecated):")
    print(f"LEGACY_CRM_DB:      {LEGACY_CRM_DB}")
    print(f"LEGACY_CRM_V3_DB:   {LEGACY_CRM_V3_DB}")
    print(f"LEGACY_DEALS_DB:    {LEGACY_DEALS_DB}")
