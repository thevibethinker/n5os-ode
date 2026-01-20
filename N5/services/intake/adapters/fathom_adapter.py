"""
Fathom Adapter for Unified Meeting Intake

Transforms Fathom webhook payload → UnifiedTranscript

---
created: 2025-12-23
last_edited: 2026-01-19
version: 2.0
provenance: con_uRvg5R7OPDTissJB
---
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseAdapter
from ..models import UnifiedTranscript, IntakeSource, Utterance

logger = logging.getLogger(__name__)


class FathomAdapter(BaseAdapter):
    """
    Adapter for Fathom.ai transcripts.
    
    Handles webhook payloads from Fathom's new_meeting_content_ready event.
    
    Fathom payload structure (as of 2026-01):
    {
        "recording_id": int,
        "title": str,
        "meeting_title": str,
        "recording_start_time": "2026-01-19T20:01:32Z",
        "recording_end_time": "2026-01-19T20:27:37Z",
        "share_url": "https://fathom.video/share/...",
        "calendar_invitees": [
            {"name": "Ben Guo", "email": "ben@substrate.run", "matched_speaker_display_name": "Ben Guo", ...}
        ],
        "transcript": [
            {"speaker": {"display_name": "Ben Guo", "matched_calendar_invitee_email": "..."}, "text": "...", "timestamp": "00:00:01"}
        ],
        "default_summary": str | null,
        "action_items": list | null,
        ...
    }
    """
    
    source = IntakeSource.FATHOM
    
    def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
        """Transform Fathom payload to UnifiedTranscript"""
        
        recording_id = payload.get("recording_id")
        title = payload.get("title") or payload.get("meeting_title", "")
        
        # Get transcript - Fathom sends it as a LIST of utterance objects
        transcript_raw = payload.get("transcript") or []
        
        # Parse based on type
        if isinstance(transcript_raw, list):
            utterances = self._parse_transcript_list(transcript_raw)
        elif isinstance(transcript_raw, str):
            # Fallback for legacy string format
            utterances = self._parse_transcript_text(transcript_raw)
        else:
            logger.warning(f"Unknown transcript format: {type(transcript_raw)}")
            utterances = []
        
        # Build full_text from utterances
        if utterances:
            full_text = "\n".join([f"{u.speaker}: {u.text}" for u in utterances])
        else:
            full_text = transcript_raw if isinstance(transcript_raw, str) else ""
        
        # Extract participants
        participants = self.extract_participants(payload)
        
        # Detect date
        detected_date = self._parse_date(payload)
        
        # Get summary if available
        summary = payload.get("default_summary") or payload.get("summary")
        
        # Calculate duration from start/end times
        duration = self._calculate_duration(payload)
        
        return UnifiedTranscript(
            source=self.source,
            full_text=full_text,
            detected_date=detected_date,
            participants=participants,
            host=payload.get("organizer_email") or payload.get("recorded_by", {}).get("email"),
            utterances=utterances,
            title=title,
            duration_seconds=duration,
            recording_url=payload.get("url") or payload.get("share_url"),
            source_id=str(recording_id) if recording_id else None,
            summary=summary,
            raw_payload=payload,
        )
    
    def _parse_transcript_list(self, transcript_list: List[Dict[str, Any]]) -> List[Utterance]:
        """Parse Fathom's list-of-objects transcript format into utterances.
        
        Each item in the list has structure:
        {
            "speaker": {"display_name": "Name", "matched_calendar_invitee_email": "..."},
            "text": "What they said",
            "timestamp": "00:01:23"
        }
        """
        utterances = []
        
        for item in transcript_list:
            if not isinstance(item, dict):
                continue
            
            # Extract speaker name
            speaker_obj = item.get("speaker", {})
            if isinstance(speaker_obj, dict):
                speaker = speaker_obj.get("display_name") or speaker_obj.get("name") or "Unknown"
            elif isinstance(speaker_obj, str):
                speaker = speaker_obj
            else:
                speaker = "Unknown"
            
            text = item.get("text", "")
            timestamp = item.get("timestamp", "")
            
            # Convert timestamp to milliseconds
            start_ms = self._timestamp_to_ms(timestamp) if timestamp else None
            
            if text:  # Only add if there's actual text
                utterances.append(Utterance(
                    speaker=speaker.strip(),
                    text=text.strip(),
                    start_ms=start_ms,
                ))
        
        return utterances
    
    def extract_participants(self, payload: Dict[str, Any]) -> List[str]:
        """Extract participant names from Fathom data"""
        participants = []
        
        # Primary: calendar_invitees (Fathom's main participant field)
        invitees = payload.get("calendar_invitees", [])
        for p in invitees:
            if isinstance(p, dict):
                # Prefer matched_speaker_display_name (actual speaker), then name, then email
                name = (
                    p.get("matched_speaker_display_name") or 
                    p.get("name") or 
                    p.get("email", "").split("@")[0]
                )
                if name and name not in participants:
                    participants.append(name)
            elif isinstance(p, str) and p not in participants:
                participants.append(p)
        
        # Fallback: try other fields
        for field in ["attendees", "participants", "invitees"]:
            if participants:
                break
            raw = payload.get(field, [])
            if raw:
                for p in raw:
                    if isinstance(p, dict):
                        name = p.get("name") or p.get("email") or p.get("displayName")
                        if name and name not in participants:
                            participants.append(name)
                    elif isinstance(p, str) and p not in participants:
                        participants.append(p)
        
        # Last resort: extract speakers from transcript
        if not participants:
            transcript_raw = payload.get("transcript", [])
            if isinstance(transcript_raw, list):
                speakers = set()
                for item in transcript_raw:
                    if isinstance(item, dict):
                        speaker_obj = item.get("speaker", {})
                        if isinstance(speaker_obj, dict):
                            name = speaker_obj.get("display_name")
                            if name and name not in ["Unknown", "Speaker"]:
                                speakers.add(name)
                participants = list(speakers)
            elif isinstance(transcript_raw, str):
                speakers = self._extract_speakers_from_text(transcript_raw)
                participants = list(speakers)
        
        return participants
    
    def detect_date_semantic(self, payload: Dict[str, Any]) -> Optional[str]:
        """Attempt to detect meeting date from transcript content"""
        # First check payload metadata
        for field in ["date", "recording_start_time", "start_time", "meeting_date", "recorded_at"]:
            if payload.get(field):
                return str(payload.get(field))
        
        # Search in transcript (for string format)
        transcript = payload.get("transcript", "")
        if isinstance(transcript, list):
            return None  # Can't search list for date patterns
        if not transcript:
            return None
        
        sample = transcript[:500]
        
        patterns = [
            r"(?:today is|meeting on|call on)\s+(\w+ \d{1,2}(?:st|nd|rd|th)?(?:,? \d{4})?)",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sample, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_source_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Get Fathom recording ID for deduplication"""
        recording_id = payload.get("recording_id")
        return str(recording_id) if recording_id else None
    
    def _parse_date(self, payload: Dict[str, Any]) -> Optional[datetime]:
        """Parse date from Fathom payload"""
        # Try various date fields (recording_start_time is primary for Fathom)
        for field in ["recording_start_time", "date", "start_time", "meeting_date", "recorded_at", "created_at"]:
            date_val = payload.get(field)
            if not date_val:
                continue
            
            # Handle epoch
            if isinstance(date_val, (int, float)):
                return datetime.fromtimestamp(date_val)
            
            # Handle ISO string
            if isinstance(date_val, str):
                try:
                    return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
                except ValueError:
                    pass
                
                # Try common formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"]:
                    try:
                        return datetime.strptime(date_val.split("+")[0].split(".")[0], fmt)
                    except ValueError:
                        continue
        
        return None
    
    def _calculate_duration(self, payload: Dict[str, Any]) -> Optional[int]:
        """Calculate duration in seconds from start/end times"""
        # First check explicit duration field
        duration = payload.get("duration_seconds") or payload.get("duration")
        if duration:
            if isinstance(duration, (int, float)):
                return int(duration)
            if isinstance(duration, str):
                parsed = self._parse_duration(duration)
                if parsed:
                    return parsed
        
        # Calculate from start/end times
        start_str = payload.get("recording_start_time")
        end_str = payload.get("recording_end_time")
        
        if start_str and end_str:
            try:
                start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                return int((end - start).total_seconds())
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _parse_transcript_text(self, transcript: str) -> List[Utterance]:
        """Parse Fathom's legacy text transcript format into utterances (fallback)"""
        if not transcript:
            return []
        
        utterances = []
        
        lines = transcript.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try "[timestamp] Speaker: text" format
            ts_match = re.match(r"\[(\d{2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.+)", line)
            if ts_match:
                timestamp, speaker, text = ts_match.groups()
                start_ms = self._timestamp_to_ms(timestamp)
                utterances.append(Utterance(
                    speaker=speaker.strip(),
                    text=text.strip(),
                    start_ms=start_ms,
                ))
                continue
            
            # Try "Speaker: text" format
            speaker_match = re.match(r"([^:]+):\s*(.+)", line)
            if speaker_match:
                speaker, text = speaker_match.groups()
                # Skip if "speaker" looks like a URL or timestamp
                if not re.match(r"^https?://", speaker) and len(speaker) < 50:
                    utterances.append(Utterance(
                        speaker=speaker.strip(),
                        text=text.strip(),
                    ))
        
        return utterances
    
    def _extract_speakers_from_text(self, transcript: str) -> set:
        """Extract unique speaker names from transcript text"""
        speakers = set()
        
        # Pattern: "Name:" at start of line or after timestamp
        pattern = r"(?:^|\[[\d:]+\]\s*)([A-Z][a-z]+(?: [A-Z][a-z]+)?):"
        matches = re.findall(pattern, transcript, re.MULTILINE)
        
        for name in matches:
            if name and name not in ["Unknown", "Speaker"]:
                speakers.add(name)
        
        return speakers
    
    def _timestamp_to_ms(self, ts: str) -> int:
        """Convert HH:MM:SS to milliseconds"""
        if not ts:
            return 0
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return (h * 3600 + m * 60 + s) * 1000
        elif len(parts) == 2:
            m, s = map(int, parts)
            return (m * 60 + s) * 1000
        return 0
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds"""
        if not duration_str:
            return None
        
        if isinstance(duration_str, (int, float)):
            return int(duration_str)
        
        # Handle "1h 30m" format
        total = 0
        h = re.search(r"(\d+)\s*h", duration_str)
        m = re.search(r"(\d+)\s*m", duration_str)
        s = re.search(r"(\d+)\s*s", duration_str)
        
        if h: total += int(h.group(1)) * 3600
        if m: total += int(m.group(1)) * 60
        if s: total += int(s.group(1))
        
        return total if total > 0 else None
