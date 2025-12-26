"""
Manual Adapter for Unified Meeting Intake

Transforms raw transcript text (any source) → UnifiedTranscript

This is the "pseudo-webhook" adapter that accepts:
- Plain text transcripts
- Markdown transcripts  
- JSON transcript objects
- Pasted content from any meeting tool
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .base import BaseAdapter
from ..models import UnifiedTranscript, IntakeSource, Utterance

logger = logging.getLogger(__name__)


class ManualAdapter(BaseAdapter):
    """
    Adapter for manually provided transcripts.
    
    Handles flexible input formats:
    - Plain text with "Speaker: text" lines
    - Timestamped transcripts "[00:00:00] Speaker: text"
    - JSON with utterances array
    - Raw text dump (no speaker labels)
    
    V Priority Order for date detection:
    1. Check semantically (scan transcript for date mentions)
    2. Check against calendar (handled by IntakeEngine)
    3. Assume today (fallback)
    """
    
    source = IntakeSource.MANUAL
    
    def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
        """
        Transform manual input to UnifiedTranscript.
        
        Expected payload keys:
        - transcript: str or dict (required) - the transcript content
        - title: str (optional) - meeting title
        - date: str (optional) - explicit date override
        - participants: list (optional) - explicit participant list
        """
        
        # Handle different transcript input formats
        raw_transcript = payload.get("transcript", "")
        
        if isinstance(raw_transcript, dict):
            # JSON format with utterances
            return self._adapt_json(raw_transcript, payload)
        elif isinstance(raw_transcript, str):
            # Text format
            return self._adapt_text(raw_transcript, payload)
        else:
            raise ValueError(f"Unsupported transcript type: {type(raw_transcript)}")
    
    def _adapt_text(self, text: str, payload: Dict[str, Any]) -> UnifiedTranscript:
        """Adapt plain text transcript"""
        
        # Parse utterances from text
        utterances = self._parse_text_transcript(text)
        
        # Build full text with speaker labels if we parsed utterances
        if utterances:
            full_text = "\n".join([f"{u.speaker}: {u.text}" for u in utterances])
        else:
            full_text = text
        
        # Extract participants
        participants = payload.get("participants") or self.extract_participants({"transcript": text})
        
        # Detect date (semantic first, explicit override takes priority)
        explicit_date = payload.get("date")
        if explicit_date:
            detected_date = self._parse_explicit_date(explicit_date)
        else:
            detected_date = self._detect_date_from_text(text)
        
        return UnifiedTranscript(
            source=self.source,
            full_text=full_text,
            detected_date=detected_date,
            participants=participants,
            host=payload.get("host"),
            utterances=utterances,
            title=payload.get("title"),
            duration_seconds=payload.get("duration_seconds"),
            recording_url=payload.get("recording_url"),
            source_id=payload.get("source_id"),
            summary=payload.get("summary"),
            raw_payload=payload,
        )
    
    def _adapt_json(self, transcript_dict: Dict, payload: Dict[str, Any]) -> UnifiedTranscript:
        """Adapt JSON format transcript"""
        
        # Extract text
        full_text = transcript_dict.get("text", "")
        
        # Extract utterances if present
        raw_utterances = transcript_dict.get("utterances", [])
        utterances = []
        for u in raw_utterances:
            utterances.append(Utterance(
                speaker=u.get("speaker", "Unknown"),
                text=u.get("text", ""),
                start_ms=u.get("start") or u.get("start_ms"),
                end_ms=u.get("end") or u.get("end_ms"),
            ))
        
        # Build full_text from utterances if not provided
        if not full_text and utterances:
            full_text = "\n".join([f"{u.speaker}: {u.text}" for u in utterances])
        
        # Participants
        participants = payload.get("participants") or transcript_dict.get("participants", [])
        if not participants and utterances:
            participants = list(set(u.speaker for u in utterances if u.speaker != "Unknown"))
        
        # Date
        explicit_date = payload.get("date") or transcript_dict.get("date")
        if explicit_date:
            detected_date = self._parse_explicit_date(explicit_date)
        else:
            detected_date = self._detect_date_from_text(full_text)
        
        return UnifiedTranscript(
            source=self.source,
            full_text=full_text,
            detected_date=detected_date,
            participants=participants,
            host=payload.get("host") or transcript_dict.get("host"),
            utterances=utterances,
            title=payload.get("title") or transcript_dict.get("title"),
            duration_seconds=payload.get("duration_seconds") or transcript_dict.get("duration_seconds"),
            recording_url=payload.get("recording_url") or transcript_dict.get("recording_url"),
            source_id=payload.get("source_id") or transcript_dict.get("source_id"),
            summary=payload.get("summary") or transcript_dict.get("summary"),
            raw_payload=payload,
        )
    
    def extract_participants(self, payload: Dict[str, Any]) -> List[str]:
        """Extract participant names from transcript text"""
        text = payload.get("transcript", "")
        if isinstance(text, dict):
            text = text.get("text", "")
        
        speakers = set()
        
        # Pattern 1: "Speaker Name:" at line start
        pattern1 = r"^([A-Z][a-z]+(?: [A-Z][a-z]+)?)\s*:"
        matches = re.findall(pattern1, text, re.MULTILINE)
        speakers.update(matches)
        
        # Pattern 2: "[timestamp] Speaker Name:" 
        pattern2 = r"\[[\d:]+\]\s*([A-Z][a-z]+(?: [A-Z][a-z]+)?)\s*:"
        matches = re.findall(pattern2, text)
        speakers.update(matches)
        
        # Pattern 3: "**Speaker Name**:" (markdown bold)
        pattern3 = r"\*\*([^*]+)\*\*\s*:"
        matches = re.findall(pattern3, text)
        speakers.update(matches)
        
        # Filter out generic names
        filtered = [s for s in speakers if s.lower() not in ["speaker", "unknown", "participant"]]
        
        return filtered
    
    def detect_date_semantic(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        V Priority Order Step 1: Check semantically.
        
        Scans transcript for date mentions like:
        - "Today is December 23rd, 2025"
        - "Meeting on 12/23"
        - "Our call on the 23rd"
        """
        text = payload.get("transcript", "")
        if isinstance(text, dict):
            text = text.get("text", "")
        
        return self._detect_date_from_text(text)
    
    def _detect_date_from_text(self, text: str) -> Optional[datetime]:
        """Scan text for date references"""
        if not text:
            return None
        
        # Sample first 1000 chars (dates usually mentioned early)
        sample = text[:1000]
        
        # Month name patterns
        month_patterns = [
            # "December 23rd, 2025" or "December 23, 2025"
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?",
            # "23rd of December, 2025"
            r"(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s*(\d{4})?",
        ]
        
        for pattern in month_patterns:
            match = re.search(pattern, sample, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    return self._parse_month_day_year(groups)
                except:
                    continue
        
        # Numeric patterns
        numeric_patterns = [
            (r"(\d{4})-(\d{2})-(\d{2})", "ISO"),  # 2025-12-23
            (r"(\d{1,2})/(\d{1,2})/(\d{2,4})", "US"),  # 12/23/2025 or 12/23/25
        ]
        
        for pattern, fmt in numeric_patterns:
            match = re.search(pattern, sample)
            if match:
                try:
                    return self._parse_numeric_date(match.groups(), fmt)
                except:
                    continue
        
        return None
    
    def _parse_month_day_year(self, groups: tuple) -> Optional[datetime]:
        """Parse month name date groups"""
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        
        if len(groups) == 3:
            # "December 23, 2025" format
            month_str, day, year = groups
            month = months.get(month_str.lower())
            if not month:
                # Try "23rd of December" format
                day, month_str, year = groups
                month = months.get(month_str.lower())
            
            if month:
                day = int(day)
                year = int(year) if year else datetime.now().year
                return datetime(year, month, day)
        
        return None
    
    def _parse_numeric_date(self, groups: tuple, fmt: str) -> Optional[datetime]:
        """Parse numeric date groups"""
        if fmt == "ISO":
            year, month, day = map(int, groups)
        elif fmt == "US":
            month, day, year = map(int, groups)
            if year < 100:
                year += 2000
        else:
            return None
        
        return datetime(year, month, day)
    
    def _parse_explicit_date(self, date_str: str) -> Optional[datetime]:
        """Parse explicitly provided date string"""
        if not date_str:
            return None
        
        # Try ISO first
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%B %d %Y",
            "%b %d, %Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_text_transcript(self, text: str) -> List[Utterance]:
        """Parse text transcript into utterances"""
        if not text:
            return []
        
        utterances = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try "[HH:MM:SS] Speaker: text"
            ts_match = re.match(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*([^:]+):\s*(.+)", line)
            if ts_match:
                timestamp, speaker, text_content = ts_match.groups()
                start_ms = self._timestamp_to_ms(timestamp)
                utterances.append(Utterance(
                    speaker=speaker.strip(),
                    text=text_content.strip(),
                    start_ms=start_ms,
                ))
                continue
            
            # Try "Speaker: text" (with reasonable speaker name)
            speaker_match = re.match(r"([A-Za-z][A-Za-z\s]{0,30}):\s*(.+)", line)
            if speaker_match:
                speaker, text_content = speaker_match.groups()
                # Validate it looks like a name (not a URL prefix like "https")
                if not re.match(r"^https?$", speaker.lower()):
                    utterances.append(Utterance(
                        speaker=speaker.strip(),
                        text=text_content.strip(),
                    ))
                    continue
            
            # Try "**Speaker**: text" (markdown bold)
            md_match = re.match(r"\*\*([^*]+)\*\*:\s*(.+)", line)
            if md_match:
                speaker, text_content = md_match.groups()
                utterances.append(Utterance(
                    speaker=speaker.strip(),
                    text=text_content.strip(),
                ))
                continue
        
        return utterances
    
    def _timestamp_to_ms(self, ts: str) -> int:
        """Convert timestamp string to milliseconds"""
        parts = ts.split(":")
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return (h * 3600 + m * 60 + s) * 1000
        elif len(parts) == 2:
            m, s = map(int, parts)
            return (m * 60 + s) * 1000
        return 0

