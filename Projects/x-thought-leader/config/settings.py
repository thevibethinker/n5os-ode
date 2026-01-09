"""
X Thought Leader Configuration

Centralized settings for the thought leadership engine.
"""

# ---
# created: 2026-01-09
# last_edited: 2026-01-09
# version: 1.0
# provenance: con_nRtJ8573Bwl836An
# ---

# =============================================================================
# X List Configuration
# =============================================================================

# V's "Curated opinions" list - SSOT for monitored accounts
DEFAULT_LIST_ID = "1703516711629054447"

# =============================================================================
# Polling Configuration
# =============================================================================

POLLING_INTERVAL_MINUTES = 15

# =============================================================================
# Relevance Gate Configuration
# =============================================================================

# Stage 1: Heuristic filter keywords (case-insensitive)
RELEVANCE_KEYWORDS = [
    "hiring", "talent", "recruiting", "recruiter", "sourcing",
    "AI", "artificial intelligence", "machine learning", "LLM",
    "career", "job", "role", "position", "opportunity",
    "founder", "startup", "building", "shipped",
    "leadership", "culture", "team", "people",
    "interview", "candidate", "resume", "application"
]

# Minimum tweet length for Stage 1 pass
MIN_TWEET_LENGTH = 50

# Stage 2: LLM correlation threshold for alerting
RELEVANCE_THRESHOLD = 0.7

# =============================================================================
# Alerting Configuration
# =============================================================================

# Maximum SMS alerts per day (ET timezone)
MAX_SMS_PER_DAY = 8

# Quiet hours (no SMS) - tuple of (start_hour, end_hour) in ET
# 22 = 10pm, 8 = 8am → no SMS from 10pm to 8am
QUIET_HOURS_START = 22
QUIET_HOURS_END = 8

# Hours when approval review is active (ET)
APPROVAL_HOURS_START = 8
APPROVAL_HOURS_END = 22

# =============================================================================
# API Rate Limiting
# =============================================================================

# Basic tier limits (approximate)
MAX_TWEETS_PER_MONTH = 10000
MAX_REQUESTS_PER_15_MIN = 15

