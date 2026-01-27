"""
Recall.ai Integration Configuration
"""

import os
from typing import Optional

# API Configuration
RECALL_API_KEY = os.environ.get("RECALL_API_KEY")
RECALL_REGION = os.environ.get("RECALL_REGION", "us-west-2")
RECALL_WEBHOOK_SECRET = (
    os.environ.get("RECALL_WEBHOOK_SIGNING_SECRET") or 
    os.environ.get("RECALL_WEBHOOK_SIGING_SECRET")  # Handle typo variant
)

# Base URLs by region
REGION_URLS = {
    "us-east-1": "https://us-east-1.recall.ai",
    "us-west-2": "https://us-west-2.recall.ai",
    "eu-central-1": "https://eu-central-1.recall.ai",
    "ap-northeast-1": "https://ap-northeast-1.recall.ai",
}

def get_base_url(region: Optional[str] = None) -> str:
    """Get API base URL for region"""
    region = region or RECALL_REGION
    return REGION_URLS.get(region, REGION_URLS["us-west-2"])

def get_api_url(region: Optional[str] = None) -> str:
    """Get full API URL"""
    return f"{get_base_url(region)}/api/v1"

# Calendar accounts to sync (add all your Google Calendar accounts here)
CALENDAR_ACCOUNTS = [
    "attawar.v@gmail.com",
    "vrijen@mycareerspan.com",
    # "vrijen@substrate.run",  # Uncomment after connecting in Settings > Integrations
]

# Local paths
MEETINGS_DIR = "/home/workspace/Personal/Meetings"
WEBHOOK_DB_PATH = "/home/workspace/N5/data/recall_webhooks.db"
WEBHOOK_LOG_PATH = "/home/workspace/N5/logs/recall_webhook.log"
RECALL_DB_PATH = "/home/workspace/N5/data/recall_calendar.db"

# Webhook port
WEBHOOK_PORT = 8846

# Default bot configuration
DEFAULT_BOT_CONFIG = {
    "bot_name": "Donald Dunn, Chief of Staff (AI Notetaker)",
    "recording_config": {
        "video_mixed_layout": "speaker_view",
        "screenshare_behavior": "overlap",
        "start_recording_on": "participant_join",
        "video_retention_days": 180,
    },
    "transcription_config": {
        "provider": "recall",  # Options: recall, assembly_ai, deepgram, rev, meeting_captions
        "language": "en",
    },
    "automatic_leave": {
        "waiting_room_timeout": 900,  # 15 minutes
        "noone_joined_timeout": 900,   # 15 minutes
        "everyone_left_timeout": 120,  # 2 minutes
    },
    "zoom": {
        "breakout_room": {
            "mode": "join_specific_room",
        },
    },
    # Real-time streaming capability (built in but not active)
    "real_time_transcription": {
        "enabled": False,  # Set to True to activate
        "destination_url": None,  # Webhook URL for streaming
    },
    "real_time_media": {
        "enabled": False,
        "audio_destination_url": None,
        "video_destination_url": None,
    },
}

# Meeting type presets - activated by V-OS tags in calendar
# Each preset overrides/extends DEFAULT_BOT_CONFIG
MEETING_PRESETS = {
    # === Recording Control ===
    "[NR]": None,  # No recording - scheduler skips entirely
    "[SKIP]": None,
    "[REC]": {},  # Force record with defaults
    
    # === Layout Presets ===
    "[AUDIO]": {
        "recording_config": {
            "video_mixed_layout": "audio_only",
        },
        "_description": "Audio only - no video capture, smaller file",
    },
    "[GALLERY]": {
        "recording_config": {
            "video_mixed_layout": "gallery_view_v2",
        },
        "_description": "Gallery view - see all participants",
    },
    "[SPEAKER]": {
        "recording_config": {
            "video_mixed_layout": "speaker_view",
        },
        "_description": "Speaker view - focus on active speaker (default)",
    },
    
    # === Meeting Type Presets ===
    "[DEMO]": {
        "recording_config": {
            "screenshare_behavior": "overlap",  # Ensure screenshare is prominent
            "video_mixed_layout": "speaker_view",
        },
        "_description": "Demo mode - optimized for screenshare presentations",
    },
    "[SEMINAR]": {
        "recording_config": {
            "video_mixed_layout": "speaker_view",
            "screenshare_behavior": "overlap",
        },
        # Future: could capture V's audio separately for podcast repurposing
        "_description": "Seminar/webinar - focus on presenter",
    },
    "[INTERVIEW]": {
        "recording_config": {
            "video_mixed_layout": "gallery_view_v2",
        },
        "_description": "Interview - show both parties equally",
    },
    "[PANEL]": {
        "recording_config": {
            "video_mixed_layout": "gallery_view_v2",
        },
        "_description": "Panel discussion - gallery view for multiple speakers",
    },
    "[1:1]": {
        "recording_config": {
            "video_mixed_layout": "speaker_view",
        },
        "_description": "1:1 meeting - speaker view default",
    },
    "[INTERNAL]": {
        # No config changes, but flags for processing pipeline
        "_meeting_type": "internal",
        "_description": "Internal meeting - different recap handling",
    },
    
    # === Timing Modifiers ===
    "[NO-JOIN-EARLY]": {
        "_join_offset_minutes": 0,  # Bot joins at exact start time
        "_description": "Don't join early - useful for back-to-back meetings",
    },
    "[JOIN-EARLY]": {
        "_join_offset_minutes": 5,  # Join 5 min early (more than default 1 min)
        "_description": "Join early - for important meetings",
    },
}

# Video retention cleanup config
VIDEO_RETENTION_DAYS = 180
LOCAL_VIDEO_CLEANUP_ENABLED = True

# Meeting classification keywords (from meeting-queue-protocol)
INTERNAL_MEETING_KEYWORDS = [
    "daily team stand-up",
    "team standup",
    "co-founder",
    "extended cof",
    "bi-weekly extended",
    "internal"
]

CAREERSPAN_DOMAINS = ["@mycareerspan.com", "@theapply.ai"]

# Team members to strip from external meeting names
TEAM_REFERENCES = [
    "x Vrijen",
    "and Vrijen Attawar",
    "+ Logan Currie",
    "Vrijen",
]
