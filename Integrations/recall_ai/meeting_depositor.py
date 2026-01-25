#!/usr/bin/env python3
"""
Meeting Depositor
Deposits Recall.ai recordings into the meeting pipeline per meeting-queue-protocol
"""

import json
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Import config - handle both module and direct execution
try:
    from .config import (
        MEETINGS_DIR,
        INTERNAL_MEETING_KEYWORDS,
        CAREERSPAN_DOMAINS,
        TEAM_REFERENCES,
    )
    from .recall_client import RecallClient
except ImportError:
    # Direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from config import MEETINGS_DIR, INTERNAL_MEETING_KEYWORDS, CAREERSPAN_DOMAINS, TEAM_REFERENCES
    from recall_client import RecallClient

# Recall video retention period in days
VIDEO_RETENTION_DAYS = 180

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """Convert text to slug format"""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_meeting_title(bot: Dict[str, Any]) -> str:
    """
    Extract meeting title from Recall bot response with multiple fallbacks
    
    Priority:
    1. meeting_metadata.title
    2. meeting_url.meeting_id
    3. meeting_url object (stringified)
    4. bot_name
    5. "Unknown Meeting"
    """
    # Try meeting_metadata.title first (best source - comes from calendar)
    meeting_metadata = bot.get("meeting_metadata", {})
    if isinstance(meeting_metadata, dict):
        title = meeting_metadata.get("title")
        if title and isinstance(title, str) and title.strip():
            return title.strip()
    
    # Try meeting_url.meeting_id
    meeting_url = bot.get("meeting_url")
    if isinstance(meeting_url, dict):
        meeting_id = meeting_url.get("meeting_id")
        if meeting_id and isinstance(meeting_id, str) and meeting_id.strip():
            return meeting_id.strip()
    
    # Try raw meeting_url as string
    if meeting_url and not isinstance(meeting_url, dict):
        return str(meeting_url)
    
    # Try bot_name as fallback
    bot_name = bot.get("bot_name")
    if bot_name and isinstance(bot_name, str):
        # Strip common bot suffixes
        for suffix in [" Notetaker", " Bot", " Recorder", " AI"]:
            if bot_name.endswith(suffix):
                return bot_name[:-len(suffix)].strip()
        return bot_name.strip()
    
    return "Unknown Meeting"


def calculate_recording_duration(bot: Dict[str, Any]) -> Optional[int]:
    """
    Calculate recording duration in seconds from status_changes
    
    Duration = last status_change timestamp - first status_change timestamp
    """
    status_changes = bot.get("status_changes", [])
    if not status_changes or len(status_changes) < 2:
        return None
    
    try:
        # Get first change timestamp
        first_change = status_changes[0].get("created_at")
        last_change = status_changes[-1].get("created_at")
        
        if not first_change or not last_change:
            return None
        
        first_dt = datetime.fromisoformat(first_change.replace("Z", "+00:00"))
        last_dt = datetime.fromisoformat(last_change.replace("Z", "+00:00"))
        
        duration = int((last_dt - first_dt).total_seconds())
        return duration if duration > 0 else None
    except (ValueError, TypeError, KeyError):
        return None


def calculate_video_expiry(bot: Dict[str, Any]) -> Optional[str]:
    """
    Calculate video expiry timestamp (creation + 180 days)
    
    Returns ISO timestamp or None if cannot determine
    """
    status_changes = bot.get("status_changes", [])
    if not status_changes:
        return None
    
    try:
        created_at = status_changes[0].get("created_at")
        if not created_at:
            return None
        
        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        expiry_dt = created_dt + timedelta(days=VIDEO_RETENTION_DAYS)
        return expiry_dt.isoformat()
    except (ValueError, TypeError):
        return None


def classify_meeting(title: str, participants: list[Dict]) -> Tuple[str, Optional[str]]:
    """
    Classify meeting as internal or external
    
    Returns:
        Tuple of (classification, external_participant_slug)
    """
    title_lower = title.lower()
    
    # Check internal keywords
    for keyword in INTERNAL_MEETING_KEYWORDS:
        if keyword in title_lower:
            return ("internal", None)
    
    # Check participant emails
    if participants:
        external_found = False
        for p in participants:
            email = p.get("email", "")
            is_internal = any(domain in email for domain in CAREERSPAN_DOMAINS)
            if email and not is_internal:
                external_found = True
                break
        
        if not external_found and participants:
            return ("internal", None)
    
    # External meeting - extract participant slug
    participant_name = title
    for ref in TEAM_REFERENCES:
        participant_name = participant_name.replace(ref, "")
    
    # Clean up common suffixes
    participant_name = re.sub(r'-?transcript.*$', '', participant_name, flags=re.IGNORECASE)
    participant_slug = slugify(participant_name)
    
    return ("external", participant_slug if participant_slug else None)


def generate_meeting_id(
    meeting_date: str,
    classification: str,
    external_participant: Optional[str] = None,
    time_suffix: Optional[str] = None,
) -> str:
    """Generate standardized meeting ID per naming convention"""
    if classification == "internal":
        base_id = f"{meeting_date}_internal-team"
    else:
        participant = external_participant or "unknown"
        base_id = f"{meeting_date}_external-{participant}"
    
    if time_suffix:
        base_id = f"{base_id}-{time_suffix}"
    
    return base_id


def check_duplicate(meeting_id: str, recall_bot_id: str) -> bool:
    """Check if this meeting already exists"""
    meeting_path = Path(MEETINGS_DIR) / meeting_id
    if meeting_path.exists():
        manifest_path = meeting_path / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                existing_bot_id = manifest.get("recall_bot_id")
                if existing_bot_id == recall_bot_id:
                    logger.info(f"Meeting {meeting_id} already processed (same bot)")
                    return True
    return False


def save_recall_metadata(bot: Dict[str, Any], meeting_path: Path) -> None:
    """
    Save raw Recall bot metadata for audit trail
    
    This preserves the full API response for debugging and reference
    """
    metadata_path = meeting_path / "recall_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(bot, f, indent=2, default=str)
    logger.info(f"Saved Recall metadata to {metadata_path}")


def deposit_meeting(
    bot_id: str,
    client: Optional[RecallClient] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Deposit a Recall.ai recording into the meeting pipeline
    
    Args:
        bot_id: Recall.ai bot ID
        client: Optional RecallClient instance
        force: Force re-deposit even if exists
    
    Returns:
        Dict with meeting_id, folder_path, and artifacts
    """
    client = client or RecallClient()
    
    # Get bot details
    bot = client.get_bot(bot_id)
    logger.info(f"Processing bot {bot_id}")
    
    # Extract meeting info with enhanced title extraction
    title = extract_meeting_title(bot)
    logger.info(f"Meeting title: {title}")
    
    # Parse meeting date from status changes
    status_changes = bot.get("status_changes", [])
    if status_changes:
        first_change = status_changes[0]
        created_at = first_change.get("created_at", "")
        if created_at:
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            meeting_date = dt.strftime("%Y-%m-%d")
            time_suffix = dt.strftime("%H%M%S")
        else:
            meeting_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            time_suffix = None
    else:
        meeting_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        time_suffix = None
    
    # Get participants
    participants = bot.get("meeting_participants", [])
    participant_count = len(participants) if participants else 0
    
    # Classify meeting
    classification, external_participant = classify_meeting(title, participants)
    logger.info(f"Classification: {classification}, participant: {external_participant}")
    
    # Generate meeting ID
    meeting_id = generate_meeting_id(
        meeting_date,
        classification,
        external_participant,
        time_suffix,
    )
    
    # Check for duplicates
    if not force and check_duplicate(meeting_id, bot_id):
        return {
            "status": "skipped",
            "reason": "duplicate",
            "meeting_id": meeting_id,
        }
    
    # Create meeting folder
    meeting_path = Path(MEETINGS_DIR) / meeting_id
    meeting_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created meeting folder: {meeting_path}")
    
    # Download artifacts
    artifacts = client.download_recording(
        bot_id,
        str(meeting_path),
        include_video=True,
        include_audio=True,
        include_transcript=True,
    )
    
    # Save full Recall metadata
    save_recall_metadata(bot, meeting_path)
    
    # Calculate enhanced metadata
    recording_duration = calculate_recording_duration(bot)
    video_expires_at = calculate_video_expiry(bot)
    
    # Build enhanced manifest
    manifest = {
        "manifest_version": "2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meeting_folder": meeting_id,
        "meeting_date": meeting_date,
        "meeting_type": classification,
        "meeting_title": title,
        "recall_bot_id": bot_id,
        "recall_region": client.region,
        "recall_meeting_url": bot.get("meeting_url"),
        "recall_meeting_id": bot.get("meeting_url", {}).get("meeting_id") if isinstance(bot.get("meeting_url"), dict) else None,
        "participants": participants,
        "participant_count": participant_count,
        "recording_duration_seconds": recording_duration,
        "video_retention_days": VIDEO_RETENTION_DAYS if artifacts.get("video") else None,
        "video_expires_at": video_expires_at,
        "status": "pending_processing",
        "artifacts": {
            "audio": "audio.mp3" if artifacts.get("audio") else None,
            "video": "video.mp4" if artifacts.get("video") else None,
            "transcript_json": "transcript.json" if artifacts.get("transcript_json") else None,
            "transcript_txt": "transcript.txt" if artifacts.get("transcript_txt") else None,
            "participants_json": "participants.json" if artifacts.get("participants") else None,
            "recall_metadata": "recall_metadata.json",
        },
        "blocks_generated": {
            "transcript_processed": False,
            "brief": False,
            "stakeholder_intelligence": False,
            "decisions": False,
            "tone_and_context": False,
        },
        "zo_take_heed_count": 0,
        "last_updated_by": "recall-ai-depositor",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    
    manifest_path = meeting_path / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Meeting deposited: {meeting_id}")
    if video_expires_at:
        logger.warning(f"Video expires: {video_expires_at} ({VIDEO_RETENTION_DAYS} days retention)")
    
    return {
        "status": "deposited",
        "meeting_id": meeting_id,
        "folder_path": str(meeting_path),
        "artifacts": artifacts,
        "classification": classification,
        "title": title,
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Deposit Recall.ai recording into meeting pipeline")
    parser.add_argument("bot_id", help="Recall.ai bot ID")
    parser.add_argument("--force", action="store_true", help="Force re-deposit")
    
    args = parser.parse_args()
    
    result = deposit_meeting(args.bot_id, force=args.force)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
