"""Extract meeting metadata from transcript."""
import logging
import re
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Import the proper extraction functions from llm_utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_utils import extract_participants_from_transcript, extract_company_names

logger = logging.getLogger(__name__)


async def extract_meeting_info(transcript: str) -> Dict[str, Any]:
    """
    Extract meeting metadata from transcript using LLM.
    
    Returns:
        - date: YYYY-MM-DD
        - time: HH:MM
        - participants: List of names
        - participants_count: Integer
        - duration_minutes: Integer
        - stakeholder_primary: Inferred primary stakeholder
        - companies: List of company names
    """
    # Parse transcript for basic structure
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    
    # Extract participants using proper extraction logic from llm_utils
    participants = extract_participants_from_transcript(transcript)
    
    # Extract companies using proper extraction logic from llm_utils
    companies = extract_company_names(transcript)
    
    # Try to extract date/time from transcript header or content
    date, time = _extract_datetime(lines)
    
    # Estimate duration from timestamps if present
    duration_minutes = _estimate_duration(lines)
    
    # Determine primary stakeholder (non-Vrijen participant most mentioned)
    stakeholder_primary = _determine_primary_stakeholder(participants, lines)
    
    return {
        "date": date,
        "time": time,
        "participants": participants,
        "companies": companies,
        "participants_count": len(participants),
        "duration_minutes": duration_minutes,
        "stakeholder_primary": stakeholder_primary,
    }


def _extract_datetime(lines: List[str]) -> tuple[str, str]:
    """Extract meeting date and time from transcript."""
    date = datetime.now().strftime("%Y-%m-%d")
    time = "00:00"
    
    # Look for date patterns in first 20 lines
    date_patterns = [
        r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD or YYYY/MM/DD
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # MM-DD-YYYY or MM/DD/YYYY
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
    ]
    
    time_patterns = [
        r'(\d{1,2}:\d{2}(?:\s?[AP]M)?)',  # HH:MM or HH:MM AM/PM
    ]
    
    for line in lines[:20]:
        # Try to find date
        for pattern in date_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Normalize to YYYY-MM-DD
                    parsed = datetime.strptime(date_str, "%Y-%m-%d")
                    date = parsed.strftime("%Y-%m-%d")
                    break
                except:
                    pass
        
        # Try to find time
        for pattern in time_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                time_str = match.group(1)
                try:
                    # Normalize to HH:MM (24-hour)
                    if "PM" in time_str.upper() or "AM" in time_str.upper():
                        parsed = datetime.strptime(time_str.upper().replace(" ", ""), "%I:%M%p")
                    else:
                        parsed = datetime.strptime(time_str, "%H:%M")
                    time = parsed.strftime("%H:%M")
                    break
                except:
                    pass
    
    return date, time


def _estimate_duration(lines: List[str]) -> int:
    """Estimate meeting duration from timestamps in transcript."""
    timestamps = []
    
    # Look for timestamp patterns: [MM:SS] or (MM:SS) or MM:SS
    timestamp_pattern = re.compile(r'[\[\(]?(\d{1,2}:\d{2})[\]\)]?')
    
    for line in lines:
        match = timestamp_pattern.search(line)
        if match:
            time_str = match.group(1)
            try:
                parts = time_str.split(":")
                minutes = int(parts[0])
                seconds = int(parts[1])
                total_seconds = minutes * 60 + seconds
                timestamps.append(total_seconds)
            except:
                pass
    
    if timestamps:
        duration_seconds = max(timestamps) - min(timestamps)
        return max(1, duration_seconds // 60)  # At least 1 minute
    
    # Default estimate based on line count
    return max(30, len(lines) // 20)  # Rough estimate: 20 lines per minute


def _determine_primary_stakeholder(participants: List[str], lines: List[str]) -> str:
    """Determine primary external stakeholder."""
    if not participants:
        return "unknown"
    
    # Remove Vrijen from participants
    external_participants = [p for p in participants if "vrijen" not in p.lower()]
    
    if not external_participants:
        return "unknown"
    
    # If only one external participant, that's primary
    if len(external_participants) == 1:
        return external_participants[0].lower().replace(" ", "-")
    
    # Count mentions of each participant
    mention_counts = {p: 0 for p in external_participants}
    
    for line in lines:
        for participant in external_participants:
            if participant in line:
                mention_counts[participant] += 1
    
    # Return most mentioned
    primary = max(mention_counts, key=mention_counts.get)
    return primary.lower().replace(" ", "-")
