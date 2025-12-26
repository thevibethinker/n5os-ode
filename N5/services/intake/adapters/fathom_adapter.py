"""
Fathom Adapter for Unified Meeting Intake

Transforms Fathom webhook payload → UnifiedTranscript
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
    """
    
    source = IntakeSource.FATHOM
    
    def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
        """Transform Fathom payload to UnifiedTranscript"""
        
        # Fathom payload structure (from webhook)
        recording_id = payload.get("recording_id")
        title = payload.get("title") or payload.get("meeting_title", "")
        
        # Get transcript text - Fathom sends it directly in payload
        transcript_text = payload.get("transcript") or ""
        
        # Parse structured transcript if available
        utterances = self._parse_transcript_text(transcript_text)
        
        # If utterances parsed, rebuild full_text with speaker labels
        if utterances:
            full_text = "\n".join([f"{u.speaker}: {u.text}" for u in utterances])
        else:
            full_text = transcript_text
        
        # Extract participants
        participants = self.extract_participants(payload)
        
        # Detect date
        detected_date = self._parse_date(payload)
        
        # Get summary if available
        summary = payload.get("default_summary") or payload.get("summary")
        
        # Get duration
        duration = payload.get("duration_seconds") or payload.get("duration")
        if isinstance(duration, str):
            duration = self._parse_duration(duration)
        
        return UnifiedTranscript(
            source=self.source,
            full_text=full_text,
            detected_date=detected_date,
            participants=participants,
            host=payload.get("organizer_email") or payload.get("host"),
            utterances=utterances,
            title=title,
            duration_seconds=duration,
            recording_url=payload.get("url") or payload.get("video_url"),
            source_id=str(recording_id) if recording_id else None,
            summary=summary,
            raw_payload=payload,
        )
    
    def extract_participants(self, payload: Dict[str, Any]) -> List[str]:
        """Extract participant names from Fathom data"""
        participants = []
        
        # Try attendees/participants fields
        for field in ["attendees", "participants", "invitees"]:
            raw = payload.get(field, [])
            if raw:
                for p in raw:
                    if isinstance(p, dict):
                        name = p.get("name") or p.get("email") or p.get("displayName")
                        if name:
                            participants.append(name)
                    elif isinstance(p, str):
                        participants.append(p)
        
        # Fallback: extract from transcript
        if not participants:
            transcript = payload.get("transcript", "")
            speakers = self._extract_speakers_from_text(transcript)
            participants = list(speakers)
        
        return participants
    
    def detect_date_semantic(self, payload: Dict[str, Any]) -> Optional[str]:
        """Attempt to detect meeting date from transcript content"""
        # First check payload metadata
        for field in ["date", "start_time", "meeting_date", "recorded_at"]:
            if payload.get(field):
                return str(payload.get(field))
        
        # Search in transcript
        transcript = payload.get("transcript", "")
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
        # Try various date fields
        for field in ["date", "start_time", "meeting_date", "recorded_at", "created_at"]:
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
    
    def _parse_transcript_text(self, transcript: str) -> List[Utterance]:
        """Parse Fathom's transcript format into utterances"""
        if not transcript:
            return []
        
        utterances = []
        
        # Fathom format is typically "Speaker Name: text" or timestamped
        # Pattern: "Speaker Name: text" or "[00:00:00] Speaker Name: text"
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

