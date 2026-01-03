"""
N5 Centralized Path Constants
=============================

Single source of truth for all path constants used across N5 scripts.
Import from here instead of hardcoding paths.

Usage:
    from N5.lib.paths import N5_ROOT, CRM_DB, BRAIN_DB

    # Or import all
    from N5.lib import paths
    db = paths.CRM_DB
"""

from pathlib import Path

# =============================================================================
# ROOT DIRECTORIES
# =============================================================================

WORKSPACE_ROOT = Path("/home/workspace")
N5_ROOT = Path("/home/workspace/N5")

# =============================================================================
# N5 SUBDIRECTORIES
# =============================================================================

N5_DATA_DIR = N5_ROOT / "data"
N5_CONFIG_DIR = N5_ROOT / "config"
N5_SCRIPTS_DIR = N5_ROOT / "scripts"
N5_SCHEMAS_DIR = N5_ROOT / "schemas"
N5_COGNITION_DIR = N5_ROOT / "cognition"
N5_LOGS_DIR = N5_ROOT / "logs"
N5_PREFS_DIR = N5_ROOT / "prefs"
N5_BUILDS_DIR = N5_ROOT / "builds"
N5_STATE_DIR = N5_ROOT / ".state"
N5_WORKERS_DIR = N5_ROOT / "workers"
N5_DIGESTS_DIR = N5_ROOT / "digests"
N5_CAPABILITIES_DIR = N5_ROOT / "capabilities"

# =============================================================================
# CRM V3
# =============================================================================

CRM_V3_DIR = N5_ROOT / "crm_v3"
CRM_PROFILES_DIR = CRM_V3_DIR / "profiles"
CRM_DB_DIR = CRM_V3_DIR / "db"

# =============================================================================
# DATABASE PATHS
# =============================================================================

# Cognition / Memory
BRAIN_DB = N5_COGNITION_DIR / "brain.db"
BRAIN_HNSW_INDEX = N5_COGNITION_DIR / "brain.hnsw"
BRAIN_HNSW_IDS = N5_COGNITION_DIR / "brain.hnsw.ids"

# CRM
CRM_DB = N5_DATA_DIR / "crm_v3.db"

# Conversations & Registry
CONVERSATIONS_DB = N5_DATA_DIR / "conversations.db"
EXECUTABLES_DB = N5_DATA_DIR / "executables.db"

# Meetings & Pipeline
MEETING_PIPELINE_DB = N5_DATA_DIR / "meeting_pipeline.db"

# Events
LUMA_EVENTS_DB = N5_DATA_DIR / "luma_events.db"

# Wellness & Health
WELLNESS_DB = N5_DATA_DIR / "wellness.db"
WORKOUTS_DB = WORKSPACE_ROOT / "Personal" / "Health" / "workouts.db"
PRODUCTIVITY_DB = WORKSPACE_ROOT / "productivity_tracker.db"

# Feedback & Communication
ZO_FEEDBACK_DB = N5_DATA_DIR / "zo_feedback.db"
ZOBRIDGE_DB = N5_DATA_DIR / "zobridge.db"

# Documents & Media
DOCUMENTS_MEDIA_DB = N5_DATA_DIR / "documents_media.db"

# Intelligence
INTELLIGENCE_DB = WORKSPACE_ROOT / "Intelligence" / "intelligence.db"
BLOCKS_DB = WORKSPACE_ROOT / "Intelligence" / "blocks.db"

# Knowledge
KNOWLEDGE_CRM_DB = WORKSPACE_ROOT / "Knowledge" / "crm" / "crm.db"
LINKEDIN_DB = WORKSPACE_ROOT / "Knowledge" / "linkedin" / "linkedin.db"
GTM_INTELLIGENCE_DB = WORKSPACE_ROOT / "Knowledge" / "market_intelligence" / "gtm_intelligence.db"

# =============================================================================
# CONFIG FILES
# =============================================================================

USER_PREFERENCES_YAML = N5_CONFIG_DIR / "user_preferences.yaml"
USER_OVERRIDES_YAML = N5_CONFIG_DIR / "user_overrides.yaml"
COMMANDS_JSONL = N5_CONFIG_DIR / "commands.jsonl"
SECRETS_DIR = N5_CONFIG_DIR / "secrets"

# =============================================================================
# WORKSPACE DIRECTORIES
# =============================================================================

PERSONAL_DIR = WORKSPACE_ROOT / "Personal"
HEALTH_DIR = PERSONAL_DIR / "Health"
WORKOUT_TRACKER_DIR = HEALTH_DIR / "WorkoutTracker"
MEETINGS_DIR = PERSONAL_DIR / "Meetings"

KNOWLEDGE_DIR = WORKSPACE_ROOT / "Knowledge"
LISTS_DIR = WORKSPACE_ROOT / "Lists"
PROMPTS_DIR = WORKSPACE_ROOT / "Prompts"
DOCUMENTS_DIR = WORKSPACE_ROOT / "Documents"

# =============================================================================
# STAGING & TEMPORARY
# =============================================================================

STAGING_DIR = N5_DATA_DIR / "staging"
MEETINGS_STAGING_DIR = STAGING_DIR / "meetings"
AVIATO_STAGING_DIR = STAGING_DIR / "aviato"

# Conversation workspaces (ephemeral)
CONVERSATION_WORKSPACES_ROOT = Path("/home/.z/workspaces")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if not. Returns the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_conversation_workspace(conversation_id: str) -> Path:
    """Get workspace path for a conversation ID."""
    return CONVERSATION_WORKSPACES_ROOT / conversation_id


def get_thread_export_dir(timestamp: str = None) -> Path:
    """Get thread export directory, optionally with timestamp subfolder."""
    base = N5_LOGS_DIR / "threads"
    if timestamp:
        return base / timestamp
    return base


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Common alternate names used in existing scripts
DB_PATH = CRM_DB  # Used in crm_cli.py
PROFILES_DIR = CRM_PROFILES_DIR  # Used in crm_cli.py
PROD_DB_PATH = PRODUCTIVITY_DB  # Used in morning_digest.py
HEALTH_DB_PATH = WORKOUTS_DB  # Used in morning_digest.py
