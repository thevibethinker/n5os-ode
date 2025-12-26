"""
Fireflies Adapter for Unified Meeting Intake

Transforms Fireflies webhook/API payload → UnifiedTranscript
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseAdapter
from ..models import UnifiedTranscript, IntakeSource, Utterance

logger = logging.getLogger(__name__)


class FirefliesAdapter(BaseAdapter):
    """
    Adapter for Fireflies.ai transcripts.
    
    Handles both webhook payloads and direct API responses.
    """
    
    source = IntakeSource.FIREFLIES
    
    def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
        """Transform Fireflies payload to UnifiedTranscript"""
        
        # Extract core data
        transcript_id = payload.get("id") or payload.get("transcript_id")
        title = payload.get("title", "")
        
        # Get sentences/utterances
        sentences = payload.get("sentences", [])
        
        # Build full text
        full_text = self._build_full_text(sentences)
        
        # Extract participants
        participants = self.extract_participants(payload)
        
        # Detect date
        detected_date = self._parse_date(payload)
        
        # Build utterances
        utterances = self._build_utterances(sentences)
        
        # Get summary if available
        summary = payload.get("summary") or payload.get("ai_summary")
        
        # Get duration
        duration = payload.get("duration")
        if duration and isinstance(duration, str):
            # Parse "1h 30m" format if needed
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
            recording_url=payload.get("video_url") or payload.get("audio_url"),
            source_id=transcript_id,
            summary=summary,
            raw_payload=payload,
        )
    
    def extract_participants(self, payload: Dict[str, Any]) -> List[str]:
        """Extract participant names/emails from Fireflies data"""
        participants = []
        
        # Try attendees field
        attendees = payload.get("attendees", [])
        if attendees:
            for a in attendees:
                if isinstance(a, dict):
                    name = a.get("displayName") or a.get("name") or a.get("email")
                    if name:
                        participants.append(name)
                elif isinstance(a, str):
                    participants.append(a)
        
        # Try participants field
        if not participants:
            raw_participants = payload.get("participants", [])
            if raw_participants:
                for p in raw_participants:
                    if isinstance(p, dict):
                        name = p.get("name") or p.get("email")
                        if name:
                            participants.append(name)
                    elif isinstance(p, str):
                        participants.append(p)
        
        # Fallback: extract from sentences
        if not participants:
            sentences = payload.get("sentences", [])
            speakers = set()
            for s in sentences:
                speaker = s.get("speaker_name") or s.get("speaker")
                if speaker and speaker not in ["Unknown", "Speaker"]:
                    speakers.add(speaker)
            participants = list(speakers)
        
        return participants
    
    def detect_date_semantic(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to detect meeting date from transcript content.
        
        Looks for patterns like:
        - "Today is December 23rd"
        - "Meeting on 12/23/2025"
        - "for our December 23 call"
        """
        # First check if date is in payload metadata
        date_str = payload.get("date") or payload.get("dateString") or payload.get("meeting_date")
        if date_str:
            return date_str
        
        # Search in transcript text
        sentences = payload.get("sentences", [])
        if not sentences:
            return None
        
        # Get first ~500 chars of transcript
        sample_text = " ".join([s.get("text", "") for s in sentences[:20]])[:500]
        
        # Date patterns to look for
        patterns = [
            r"(?:today is|meeting on|call on|for our)\s+(\w+ \d{1,2}(?:st|nd|rd|th)?(?:,? \d{4})?)",
            r"(\d{1,2}/\d{1,2}/\d{2,4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sample_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_source_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Get Fireflies transcript ID for deduplication"""
        return payload.get("id") or payload.get("transcript_id")
    
    def _parse_date(self, payload: Dict[str, Any]) -> Optional[datetime]:
        """Parse date from various Fireflies formats"""
        # Try direct date field
        date_val = payload.get("date") or payload.get("dateString") or payload.get("meeting_date")
        
        if not date_val:
            return None
        
        # Handle epoch timestamp
        if isinstance(date_val, (int, float)):
            return datetime.fromtimestamp(date_val)
        
        # Handle ISO string
        if isinstance(date_val, str):
            try:
                # Try ISO format
                return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
            except ValueError:
                pass
            
            # Try common formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
                try:
                    return datetime.strptime(date_val, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _build_full_text(self, sentences: List[Dict]) -> str:
        """Build full transcript text from sentences"""
        if not sentences:
            return ""
        
        lines = []
        for s in sentences:
            speaker = s.get("speaker_name") or s.get("speaker") or "Unknown"
            text = s.get("text", "")
            if text:
                lines.append(f"{speaker}: {text}")
        
        return "\n".join(lines)
    
    def _build_utterances(self, sentences: List[Dict]) -> List[Utterance]:
        """Convert Fireflies sentences to Utterance objects"""
        utterances = []
        
        for s in sentences:
            speaker = s.get("speaker_name") or s.get("speaker") or "Unknown"
            text = s.get("text", "")
            
            if not text:
                continue
            
            utterances.append(Utterance(
                speaker=speaker,
                text=text,
                start_ms=s.get("start_time"),
                end_ms=s.get("end_time"),
            ))
        
        return utterances
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds"""
        if not duration_str:
            return None
        
        # Handle "1h 30m" format
        total_seconds = 0
        
        hours_match = re.search(r"(\d+)\s*h", duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
        
        mins_match = re.search(r"(\d+)\s*m", duration_str)
        if mins_match:
            total_seconds += int(mins_match.group(1)) * 60
        
        secs_match = re.search(r"(\d+)\s*s", duration_str)
        if secs_match:
            total_seconds += int(secs_match.group(1))
        
        # Handle plain seconds
        if total_seconds == 0 and duration_str.isdigit():
            return int(duration_str)
        
        return total_seconds if total_seconds > 0 else None

