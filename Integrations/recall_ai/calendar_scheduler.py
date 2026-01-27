#!/usr/bin/env python3
"""
Calendar Scheduler for Recall AI
Syncs Google Calendar events to scheduled Recall bots

v2.1 - Rate-limit aware: fetches all bots ONCE per sync, caches for deduplication
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Set

# Import config
try:
    from .config import RECALL_API_KEY, RECALL_REGION, get_api_url, DEFAULT_BOT_CONFIG
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import RECALL_API_KEY, RECALL_REGION, get_api_url, DEFAULT_BOT_CONFIG

# Import recall client
try:
    from .recall_client import RecallClient
except ImportError:
    from recall_client import RecallClient

# State file path
STATE_FILE = Path("/home/workspace/N5/data/recall_calendar_sync.json")
DATA_DIR = Path("/home/workspace/N5/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Meeting link patterns
VIDEO_LINK_PATTERNS = [
    # Zoom: zoom.us/j/123456789 or zoom.us/w/123456789
    r'zoom\.us/(?:j|w)/[\w\-/?=&]+',
    # Zoom: zoom.us/my/roomname or zoom.us/s/123456
    r'zoom\.us/(?:my|s)/[\w\-/?=&]+',
    # Google Meet: meet.google.com/abc-defg-hij
    r'meet\.google\.com/[a-z\-]+',
    # Microsoft Teams: teams.microsoft.com/l/meetup-join/...
    r'teams\.microsoft\.com/l/meetup-join/[^/]+',
    # Teams: teams.microsoft.com/...meetingLink
    r'teams\.microsoft\.com/[^\s"\'<>]+[?&]meetingLink',
    # Webex: webex.com/meet/roomname
    r'webex\.com/meet/[\w\-]+',
]

# Skip markers in event titles
SKIP_MARKERS = ["[NR]", "[SKIP]", "[NO RECORD]", "[NORECORD]"]

# Force record markers - will attempt to record even if no video link auto-detected
FORCE_RECORD_MARKERS = ["[REC]", "[RECORD]"]

# V-OS tag to bot config mapping
# Tags in calendar title/description modify bot behavior
TAG_BOT_CONFIG = {
    # Layout modifications
    "[AUDIO]": {
        "recording_config": {
            "video_mixed_layout": "audio_only"
        }
    },
    "[GALLERY]": {
        "recording_config": {
            "video_mixed_layout": "gallery_view_v2"
        }
    },
    # Join timing
    "[NO-JOIN-EARLY]": {
        "_join_offset_minutes": 0  # Internal flag, not sent to API
    },
    # Metadata markers (don't change bot config, but stored in metadata)
    "[INTERNAL]": {},
}

# Bot configuration
MIN_JOIN_MINUTES_AHEAD = 10  # Recall requires at least 10 minutes for scheduled bots
DEFAULT_JOIN_MINUTES_AHEAD = 15  # Default: join 15 minutes early
MAX_EVENTS_TO_SYNC = 50
SYNC_WINDOW_HOURS = 48

# Rate limiting config
RATE_LIMIT_REQUESTS_PER_MIN = 60
RATE_LIMIT_SAFETY_MARGIN = 0.7  # Use only 70% of limit to be safe
MAX_REQUESTS_PER_SYNC = int(RATE_LIMIT_REQUESTS_PER_MIN * RATE_LIMIT_SAFETY_MARGIN)
REQUEST_DELAY_SECONDS = 0.5  # Minimum delay between requests when throttling

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter to avoid hitting API limits"""
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_SYNC, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
    
    def wait_if_needed(self) -> None:
        """Block if we're approaching rate limit"""
        now = time.time()
        # Remove old requests outside window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        
        if len(self.requests) >= self.max_requests:
            # Calculate how long to wait
            oldest = min(self.requests)
            wait_time = self.window_seconds - (now - oldest) + 0.1
            if wait_time > 0:
                logger.warning(f"Rate limit approaching, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                self.requests = []
    
    def record_request(self) -> None:
        """Record that a request was made"""
        self.requests.append(time.time())
    
    @property
    def requests_remaining(self) -> int:
        """How many requests we can still make this window"""
        now = time.time()
        recent = [t for t in self.requests if now - t < self.window_seconds]
        return max(0, self.max_requests - len(recent))


class CalendarScheduler:
    """Syncs calendar events to Recall bots"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        state_file: Optional[Path] = None,
    ):
        self.recall_client = RecallClient(api_key=api_key, region=region)
        self.state_file = state_file or STATE_FILE
        self.state = self._load_state()
        self.rate_limiter = RateLimiter()
        
        # Cache for active bots - populated once per sync
        self._active_bots_cache: Optional[Dict[str, Dict]] = None
        self._all_bots_cache: Optional[List[Dict]] = None

    def _load_state(self) -> Dict[str, Any]:
        """Load sync state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load state file: {e}")
        return {
            "synced_events": {},
            "last_sync": None,
            "version": "2.1",
        }

    def _save_state(self) -> None:
        """Save sync state to file"""
        self.state["last_sync"] = datetime.now(timezone.utc).isoformat()
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)
        logger.info(f"State saved to {self.state_file}")
    
    def _clear_cache(self) -> None:
        """Clear bot caches (call at start of each sync)"""
        self._active_bots_cache = None
        self._all_bots_cache = None

    def _fetch_all_bots_once(self) -> List[Dict]:
        """
        Fetch ALL bots from API in a single paginated call.
        Results are cached for the duration of the sync.
        
        This replaces the old approach of calling list_bots multiple times
        with different status filters (which caused rate limit issues).
        
        Returns:
            List of all bot objects
        """
        if self._all_bots_cache is not None:
            return self._all_bots_cache
        
        all_bots = []
        cursor = None
        page_count = 0
        max_pages = 10  # Safety limit
        
        while page_count < max_pages:
            self.rate_limiter.wait_if_needed()
            
            try:
                result = self.recall_client.list_bots(limit=100, cursor=cursor)
                self.rate_limiter.record_request()
                
                bots = result.get('results', [])
                all_bots.extend(bots)
                
                # Check for next page
                cursor = result.get('next')
                if not cursor:
                    break
                    
                page_count += 1
                
            except Exception as e:
                logger.error(f"Error fetching bots (page {page_count}): {e}")
                break
        
        logger.info(f"Fetched {len(all_bots)} bots in {page_count + 1} API call(s)")
        self._all_bots_cache = all_bots
        return all_bots

    def _build_active_bots_index(self) -> Dict[str, Dict]:
        """
        Build an index of active bots by meeting ID.
        Uses cached bot list from _fetch_all_bots_once().
        
        Returns:
            Dict of meeting_id -> {bot_id, bot_name, status, meeting_url}
        """
        if self._active_bots_cache is not None:
            return self._active_bots_cache
        
        all_bots = self._fetch_all_bots_once()
        active_bots = {}
        
        # Terminal statuses - bots in these states are "done" and shouldn't block new bots
        terminal_statuses = {'done', 'fatal', 'analysis_done'}
        
        for bot in all_bots:
            # Determine current status
            status_changes = bot.get('status_changes', [])
            if status_changes:
                current_status = status_changes[-1].get('code', 'unknown')
            else:
                current_status = 'scheduled'  # No status changes = scheduled but not started
            
            # Skip terminal bots
            if current_status in terminal_statuses:
                continue
            
            # Extract meeting ID from URL
            meeting_url = bot.get('meeting_url', '')
            if isinstance(meeting_url, dict):
                meeting_url = meeting_url.get('meeting_id', '') or str(meeting_url)
            
            meeting_id = self._extract_meeting_id(str(meeting_url))
            
            if meeting_id:
                active_bots[meeting_id] = {
                    'bot_id': bot.get('id'),
                    'bot_name': bot.get('bot_name'),
                    'status': current_status,
                    'meeting_url': meeting_url,
                }
        
        logger.info(f"Built index of {len(active_bots)} active bots")
        self._active_bots_cache = active_bots
        return active_bots
    
    def _extract_meeting_id(self, url: str) -> Optional[str]:
        """Extract meeting ID from various video conferencing URLs"""
        patterns = [
            r'meet\.google\.com/([a-z\-]+)',
            r'zoom\.us/[jw]/(\d+)',
            r'zoom\.us/my/([\w\-]+)',
            r'teams\.microsoft\.com/.*meetup-join/([^/\?]+)',
            r'webex\.com/meet/([\w\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback: use the full URL as ID
        if url:
            return url
        return None

    def has_video_link(self, event: Dict[str, Any]) -> bool:
        """Check if event has a video conferencing link"""
        text_fields = [
            event.get("summary", ""),
            event.get("description", ""),
            event.get("location", ""),
        ]

        # Check conference data
        if "conferenceData" in event:
            entry_points = event["conferenceData"].get("entryPoints", [])
            for ep in entry_points:
                if ep.get("entryPointType") == "video":
                    uri = ep.get("uri", "")
                    if uri and any(re.search(p, uri, re.IGNORECASE) for p in VIDEO_LINK_PATTERNS):
                        return True

        # Check text fields
        combined_text = " ".join(text_fields)
        for pattern in VIDEO_LINK_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True

        return False

    def extract_video_link(self, event: Dict[str, Any]) -> Optional[str]:
        """Extract video link from event"""
        # First check conference data (most reliable)
        if "conferenceData" in event:
            entry_points = event["conferenceData"].get("entryPoints", [])
            for ep in entry_points:
                if ep.get("entryPointType") == "video":
                    uri = ep.get("uri", "")
                    if uri:
                        logger.debug(f"Found video link in conferenceData: {uri}")
                        return uri

        # Then check text fields - look for full URLs with protocol
        text_fields = [
            (event.get("location", ""), "location"),
            (event.get("description", ""), "description"),
            (event.get("summary", ""), "summary"),
        ]

        url_pattern = r'(https?://(?:[\w\-]+\.)*zoom\.us|meet\.google\.com|teams\.microsoft\.com|webex\.com)/[^\s"\'<>]+'

        for text, source in text_fields:
            match = re.search(url_pattern, text)
            if match:
                link = match.group(0)
                logger.debug(f"Found video link in {source}: {link}")
                return link

        return None

    def should_record(self, event: Dict[str, Any]) -> bool:
        """Determine if event should be recorded"""
        # Skip cancelled events
        if event.get("status") == "cancelled":
            return False

        # Check skip markers in title
        title = event.get("summary", "")
        for marker in SKIP_MARKERS:
            if marker in title:
                logger.info(f"Skipping event with marker '{marker}': {title}")
                return False

        # Check force record markers
        for marker in FORCE_RECORD_MARKERS:
            if marker in title:
                logger.info(f"Force recording event with marker '{marker}': {title}")
                return True

        # Must have video link
        if not self.has_video_link(event):
            return False

        return True

    def get_event_key(self, event: Dict[str, Any]) -> str:
        """Generate unique key for event"""
        return event.get("iCalUID") or event.get("id", "")

    def calculate_join_time(self, event_start: str) -> datetime:
        """Calculate when bot should join the meeting"""
        start_time = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
        join_time = start_time - timedelta(minutes=DEFAULT_JOIN_MINUTES_AHEAD)

        # Ensure we meet Recall's minimum requirement
        now = datetime.now(timezone.utc)
        earliest_allowed = now + timedelta(minutes=MIN_JOIN_MINUTES_AHEAD)

        if join_time < earliest_allowed:
            join_time = earliest_allowed
            logger.warning(
                f"Adjusted join time to meet minimum requirement: {join_time.isoformat()}"
            )

        return join_time

    def is_already_scheduled(self, event: Dict[str, Any], active_bots: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """
        Check if event already has a scheduled bot.
        
        Uses local state + cached active bots index (NO API calls).
        
        Args:
            event: Calendar event dict
            active_bots: Pre-fetched index of active bots by meeting ID
        
        Returns:
            Synced event record if found, None otherwise
        """
        key = self.get_event_key(event)
        synced = self.state["synced_events"].get(key)

        if not synced:
            return None

        bot_id = synced.get("recall_bot_id")
        if not bot_id:
            return synced
        
        # Check if this bot is still in the active bots list
        # by looking up the meeting URL
        meeting_url = synced.get("meeting_url", "")
        meeting_id = self._extract_meeting_id(meeting_url)
        
        if meeting_id and meeting_id in active_bots:
            active_bot = active_bots[meeting_id]
            if active_bot.get('bot_id') == bot_id:
                # Bot is still active
                return synced
        
        # Also check if the bot_id appears anywhere in active bots
        for _, bot_info in active_bots.items():
            if bot_info.get('bot_id') == bot_id:
                return synced
        
        # Bot not found in active bots - it may have completed or been deleted
        # Trust local state but mark for potential cleanup
        logger.debug(f"Bot {bot_id} not found in active bots, trusting local state")
        return synced

    def check_duplicate_meeting(self, meeting_url: str, active_bots: Dict[str, Dict]) -> Optional[Dict]:
        """
        Check if there's already an active bot for this meeting URL.
        
        Uses cached active bots index (NO API calls).
        
        Args:
            meeting_url: The meeting URL to check
            active_bots: Pre-fetched index of active bots
        
        Returns:
            Active bot info if duplicate found, None otherwise
        """
        meeting_id = self._extract_meeting_id(meeting_url)
        if meeting_id and meeting_id in active_bots:
            return active_bots[meeting_id]
        return None

    def schedule_bot(self, event: Dict[str, Any], active_bots: Dict[str, Dict]) -> Optional[str]:
        """
        Schedule a Recall bot for an event.
        
        Args:
            event: Calendar event dict
            active_bots: Pre-fetched index of active bots (for deduplication)

        Returns:
            Bot ID if successful, None otherwise
        """
        meeting_url = self.extract_video_link(event)
        if not meeting_url:
            logger.error(f"Could not extract meeting URL from event: {event.get('summary')}")
            return None

        # Check for duplicate using cached data (NO API call)
        existing = self.check_duplicate_meeting(meeting_url, active_bots)
        if existing:
            logger.warning(
                f"Bot already exists for meeting: "
                f"{existing['bot_id']} ({existing['status']}). Skipping duplicate."
            )
            return None

        event_start = event.get("start", {})
        if isinstance(event_start, dict):
            start_time = event_start.get("dateTime") or event_start.get("date")
        else:
            start_time = str(event_start)

        if not start_time:
            logger.error(f"Event has no start time: {event.get('summary')}")
            return None

        join_time = self.calculate_join_time(start_time)
        join_at = join_time.isoformat()

        title = event.get("summary", "Meeting")

        try:
            self.rate_limiter.wait_if_needed()
            
            logger.info(f"Scheduling bot for '{title}' at {join_at}")
            bot = self.recall_client.create_bot(
                meeting_url=meeting_url,
                bot_name=DEFAULT_BOT_CONFIG.get("bot_name", "Zo Notetaker"),
                join_at=join_at,
            )
            self.rate_limiter.record_request()

            bot_id = bot.get("id")
            if not bot_id:
                logger.error(f"Bot creation failed, no ID returned: {bot}")
                return None

            # Update local state
            key = self.get_event_key(event)
            self.state["synced_events"][key] = {
                "recall_bot_id": bot_id,
                "scheduled_at": datetime.now(timezone.utc).isoformat(),
                "meeting_url": meeting_url,
                "event_start": start_time,
                "event_title": title,
                "join_at": join_at,
            }
            
            # Also add to active bots cache to prevent duplicate scheduling within same sync
            meeting_id = self._extract_meeting_id(meeting_url)
            if meeting_id and self._active_bots_cache is not None:
                self._active_bots_cache[meeting_id] = {
                    'bot_id': bot_id,
                    'bot_name': DEFAULT_BOT_CONFIG.get("bot_name", "Zo Notetaker"),
                    'status': 'scheduled',
                    'meeting_url': meeting_url,
                }

            logger.info(f"Bot {bot_id} scheduled for '{title}'")
            return bot_id

        except Exception as e:
            logger.error(f"Failed to schedule bot for '{title}': {e}")
            return None

    def cleanup_orphaned_bots(self, current_events: List[Dict[str, Any]], active_bots: Dict[str, Dict]) -> int:
        """
        Cancel bots for events that no longer exist or should not be recorded.
        
        Args:
            current_events: List of current calendar events
            active_bots: Pre-fetched index of active bots
        
        Returns:
            Number of bots cleaned up
        """
        current_event_keys = {self.get_event_key(e) for e in current_events}
        cancelled_events = {self.get_event_key(e) for e in current_events if e.get("status") == "cancelled"}

        synced_keys = set(self.state["synced_events"].keys())
        orphaned_keys = synced_keys - current_event_keys
        
        cleaned = 0

        for key in orphaned_keys:
            record = self.state["synced_events"][key]
            bot_id = record.get("recall_bot_id")

            logger.info(f"Event '{record.get('event_title')}' no longer exists, cancelling bot {bot_id}")

            if bot_id:
                try:
                    self.rate_limiter.wait_if_needed()
                    self.recall_client.delete_bot(bot_id)
                    self.rate_limiter.record_request()
                    logger.info(f"Cancelled orphaned bot {bot_id}")
                    cleaned += 1
                except Exception as e:
                    logger.error(f"Failed to cancel bot {bot_id}: {e}")

            del self.state["synced_events"][key]

        # Also handle cancelled events
        for key in cancelled_events:
            if key in self.state["synced_events"]:
                record = self.state["synced_events"][key]
                bot_id = record.get("recall_bot_id")

                logger.info(f"Event '{record.get('event_title')}' was cancelled, cancelling bot {bot_id}")

                if bot_id:
                    try:
                        self.rate_limiter.wait_if_needed()
                        self.recall_client.delete_bot(bot_id)
                        self.rate_limiter.record_request()
                        logger.info(f"Cancelled bot for cancelled event: {bot_id}")
                        cleaned += 1
                    except Exception as e:
                        logger.error(f"Failed to cancel bot {bot_id}: {e}")

                del self.state["synced_events"][key]
        
        return cleaned

    def sync(self, events: List[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
        """
        Sync calendar events to Recall bots.
        
        Rate-limit aware: fetches all bots ONCE at start, then uses
        cached data for all deduplication checks.

        Args:
            events: List of calendar events from Google Calendar
            dry_run: If True, don't make any changes

        Returns:
            Summary of sync results
        """
        results = {
            "total_events": len(events),
            "recordable": 0,
            "already_scheduled": 0,
            "new_scheduled": 0,
            "orphaned_cleaned": 0,
            "skipped": 0,
            "errors": [],
            "api_calls": 0,
        }

        logger.info(f"Starting sync with {len(events)} events (dry_run={dry_run})")
        
        # Clear caches at start of sync
        self._clear_cache()
        
        # Fetch all bots ONCE at the start (rate-limit friendly)
        if not dry_run:
            active_bots = self._build_active_bots_index()
            results["api_calls"] = len(self._all_bots_cache or []) // 100 + 1
        else:
            active_bots = {}

        # Filter to recordable events
        recordable_events = [e for e in events if self.should_record(e)]
        results["recordable"] = len(recordable_events)
        logger.info(f"Found {len(recordable_events)} recordable events")

        # Schedule new bots
        for event in recordable_events:
            title = event.get("summary", "Untitled")

            # Check using local state + cached API data (NO API call)
            existing = self.is_already_scheduled(event, active_bots)
            if existing:
                logger.debug(f"Already scheduled: {title}")
                results["already_scheduled"] += 1
                continue

            if dry_run:
                logger.info(f"[DRY RUN] Would schedule: {title}")
                results["new_scheduled"] += 1
            else:
                bot_id = self.schedule_bot(event, active_bots)
                if bot_id:
                    results["new_scheduled"] += 1
                    results["api_calls"] += 1
                else:
                    results["errors"].append(f"Failed to schedule: {title}")

        # Clean up orphaned bots
        if not dry_run:
            cleaned = self.cleanup_orphaned_bots(events, active_bots)
            results["orphaned_cleaned"] = cleaned
            results["api_calls"] += cleaned

        # Save state
        if not dry_run:
            self._save_state()

        logger.info(f"Sync complete: {results}")
        logger.info(f"Total API calls this sync: {results['api_calls']} (limit: {MAX_REQUESTS_PER_SYNC}/min)")
        return results

    def list_scheduled_bots(self) -> List[Dict[str, Any]]:
        """
        List all synced events and their bot status.
        
        Note: This method makes API calls for each bot to get current status.
        Use sparingly to avoid rate limits.
        """
        synced = []
        for key, record in self.state["synced_events"].items():
            bot_id = record.get("recall_bot_id")
            bot_status = "unknown"

            if bot_id:
                try:
                    self.rate_limiter.wait_if_needed()
                    bot = self.recall_client.get_bot(bot_id)
                    self.rate_limiter.record_request()
                    
                    status_changes = bot.get("status_changes", [])
                    if status_changes:
                        bot_status = status_changes[-1].get("code", "unknown")
                    else:
                        bot_status = "scheduled"
                except:
                    bot_status = "not_found"

            synced.append({
                **record,
                "event_key": key,
                "bot_status": bot_status,
            })

        return synced
    
    def list_scheduled_bots_fast(self) -> List[Dict[str, Any]]:
        """
        List all synced events using cached/local data only.
        
        Does NOT make API calls - uses local state only.
        Bot status will be from last known state, not live.
        """
        synced = []
        for key, record in self.state["synced_events"].items():
            synced.append({
                **record,
                "event_key": key,
                "bot_status": "unknown (local state)",
            })
        return synced


def sync_from_zo(events_json: str, dry_run: bool = False) -> Dict[str, Any]:
    """Entry point for Zo integration"""
    events = json.loads(events_json)
    scheduler = CalendarScheduler()
    return scheduler.sync(events, dry_run=dry_run)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Calendar Scheduler for Recall AI (v2.1 - rate-limit aware)")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes")
    parser.add_argument("--list", action="store_true", help="List scheduled bots (makes API calls)")
    parser.add_argument("--list-fast", action="store_true", help="List scheduled bots (local state only, no API calls)")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--events-file", help="Load events from JSON file")
    parser.add_argument("--reset", action="store_true", help="Reset sync state")

    args = parser.parse_args()

    scheduler = CalendarScheduler()

    if args.reset:
        if input("Reset sync state? This will cancel all tracked bots. [y/N] ").lower() == "y":
            for key, record in scheduler.state["synced_events"].items():
                bot_id = record.get("recall_bot_id")
                if bot_id:
                    try:
                        scheduler.rate_limiter.wait_if_needed()
                        scheduler.recall_client.delete_bot(bot_id)
                        scheduler.rate_limiter.record_request()
                        print(f"Cancelled bot {bot_id}")
                    except Exception as e:
                        print(f"Failed to cancel bot {bot_id}: {e}")

            scheduler.state = {
                "synced_events": {},
                "last_sync": None,
                "version": "2.1",
            }
            scheduler._save_state()
            print("Sync state reset")
        return

    if args.list:
        print("\n⚠️  Note: This makes API calls for each bot. Use --list-fast for no API calls.\n")
        synced = scheduler.list_scheduled_bots()
        print("Scheduled Bots:")
        for s in synced:
            print(f"  - {s['event_title']}")
            print(f"    Bot: {s['recall_bot_id']} ({s['bot_status']})")
            print(f"    Start: {s['event_start']}")
            print(f"    URL: {s['meeting_url']}")
            print()
        return
    
    if args.list_fast:
        synced = scheduler.list_scheduled_bots_fast()
        print("\nScheduled Bots (local state, no API calls):")
        for s in synced:
            print(f"  - {s['event_title']}")
            print(f"    Bot: {s['recall_bot_id']}")
            print(f"    Start: {s['event_start']}")
            print(f"    URL: {s['meeting_url']}")
            print()
        return

    if args.status:
        print("\nSync Status:")
        print(f"  Last sync: {scheduler.state.get('last_sync') or 'Never'}")
        print(f"  Tracked events: {len(scheduler.state['synced_events'])}")
        print(f"  State file: {scheduler.state_file}")
        print(f"  Version: {scheduler.state.get('version', 'unknown')}")
        print(f"  Rate limit: {MAX_REQUESTS_PER_SYNC} requests/min (safety margin applied)")
        print()
        return

    if args.events_file:
        with open(args.events_file, "r") as f:
            events = json.load(f)
        results = scheduler.sync(events, dry_run=args.dry_run)
        print("\nSync Results:")
        print(json.dumps(results, indent=2))
    else:
        print("No events provided. Use --events-file or integrate with Zo calendar.")
        print("\nExample Zo integration:")
        print("  python3 calendar_scheduler.py --events-file events.json")


if __name__ == "__main__":
    main()
