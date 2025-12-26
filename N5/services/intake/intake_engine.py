"""
Unified Meeting Intake Engine

The canonical orchestrator for all meeting transcript ingestion.
All sources (Fathom, Fireflies, Manual, Granola) flow through here.

Responsibilities:
1. Accept adapter output (UnifiedTranscript)
2. Validate the transcript
3. Detect/resolve date (semantic → calendar → today)
4. Check deduplication
5. Create meeting folder with canonical structure
6. Generate metadata.json
7. Return IntakeResult
"""

import json
import logging
import sqlite3
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import re

from .models import (
    UnifiedTranscript,
    IntakeResult,
    IntakeSource,
    ValidationResult,
    ValidationSeverity,
    TranscriptValidator,
)
from .adapters.base import BaseAdapter
from .adapters.fireflies_adapter import FirefliesAdapter
from .adapters.fathom_adapter import FathomAdapter
from .adapters.manual_adapter import ManualAdapter

logger = logging.getLogger(__name__)


class IntakeEngine:
    """
    Central orchestrator for meeting transcript ingestion.
    
    Usage:
        engine = IntakeEngine()
        
        # From webhook payload
        result = engine.ingest_from_source(IntakeSource.FATHOM, payload)
        
        # From manual transcript
        result = engine.ingest_manual(transcript_text, title="My Meeting")
    """
    
    INBOX_PATH = Path("/home/workspace/Personal/Meetings/Inbox")
    MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
    DEDUP_DB_PATH = Path("/home/workspace/N5/data/intake_dedup.db")
    
    def __init__(
        self,
        inbox_path: Optional[Path] = None,
        meetings_root: Optional[Path] = None,
        dedup_db_path: Optional[Path] = None,
        calendar_service: Optional[Any] = None,
    ):
        self.inbox_path = inbox_path or self.INBOX_PATH
        self.meetings_root = meetings_root or self.MEETINGS_ROOT
        self.dedup_db_path = dedup_db_path or self.DEDUP_DB_PATH
        self.calendar_service = calendar_service
        
        # Ensure paths exist
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.dedup_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize adapters
        self.adapters: Dict[IntakeSource, BaseAdapter] = {
            IntakeSource.FIREFLIES: FirefliesAdapter(),
            IntakeSource.FATHOM: FathomAdapter(),
            IntakeSource.MANUAL: ManualAdapter(),
        }
        
        # Initialize dedup database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for deduplication tracking"""
        conn = sqlite3.connect(self.dedup_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ingested_transcripts (
                source TEXT,
                source_id TEXT,
                content_hash TEXT,
                folder_path TEXT,
                ingested_at TEXT,
                title TEXT,
                meeting_date TEXT,
                participant_hash TEXT,
                PRIMARY KEY (source, source_id)
            )
            """
        )
        # Add index on content_hash and meeting_date for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON ingested_transcripts (content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_date ON ingested_transcripts (meeting_date)")
        conn.commit()
        conn.close()
    
    def ingest_from_source(
        self,
        source: IntakeSource,
        payload: Dict[str, Any],
        force: bool = False,
    ) -> IntakeResult:
        """
        Ingest a transcript from a specific source.
        
        Args:
            source: The source type (FATHOM, FIREFLIES, etc.)
            payload: The source-specific payload
            force: Skip deduplication check
            
        Returns:
            IntakeResult with success status and folder path
        """
        adapter = self.adapters.get(source)
        if not adapter:
            return IntakeResult(
                success=False,
                error_message=f"No adapter registered for source: {source.value}",
            )
        
        try:
            # Step 1: Adapt to unified format
            transcript = adapter.adapt(payload)
            
            # Step 2: Ingest
            return self.ingest_transcript(transcript, force=force)
            
        except Exception as e:
            logger.exception(f"Failed to ingest from {source.value}")
            return IntakeResult(
                success=False,
                error_message=str(e),
            )
    
    def ingest_manual(
        self,
        transcript_text: str,
        title: Optional[str] = None,
        date_str: Optional[str] = None,
        participants: Optional[List[str]] = None,
        force: bool = False,
    ) -> IntakeResult:
        """Convenience method for manual ingestion"""
        payload = {
            "transcript": transcript_text,
            "title": title,
            "date": date_str,
            "participants": participants,
        }
        return self.ingest_from_source(IntakeSource.MANUAL, payload, force=force)

    def ingest_json(
        self,
        transcript_data: Dict[str, Any],
        title: Optional[str] = None,
        date_str: Optional[str] = None,
        force: bool = False,
    ) -> IntakeResult:
        """
        Ingest a pre-parsed structured transcript.
        Bypasses the "dumb" regex adapter and uses the provided data directly.
        """
        # Create a "pass-through" adapter for this request
        from .adapters.base import BaseAdapter
        from .models import UnifiedTranscript, Utterance

        class PassThroughAdapter(BaseAdapter):
            source = IntakeSource.MANUAL
            def adapt(self, payload: Dict[str, Any]) -> UnifiedTranscript:
                # Use utterances if provided, otherwise parse text
                raw_utterances = payload.get("utterances", [])
                utterances = [
                    Utterance(
                        speaker=u.get("speaker", "Unknown"),
                        text=u.get("text", ""),
                        start_ms=u.get("start_ms") or 0,
                    )
                    for u in raw_utterances
                ]
                
                return UnifiedTranscript(
                    source=self.source,
                    full_text=payload.get("text", ""),
                    detected_date=datetime.fromisoformat(payload["date"]) if payload.get("date") else None,
                    participants=payload.get("participants", []),
                    title=payload.get("title"),
                    utterances=utterances,
                    raw_payload=payload,
                )

        adapter = PassThroughAdapter()
        transcript = adapter.adapt(transcript_data)
        
        # Merge manual overrides
        if title: transcript.title = title
        if date_str: transcript.detected_date = datetime.fromisoformat(date_str)

        return self.ingest_transcript(transcript, force=force)

    def ingest_transcript(
        self,
        transcript: UnifiedTranscript,
        force: bool = False,
    ) -> IntakeResult:
        """
        Core ingestion logic for a UnifiedTranscript.
        
        Steps:
        1. Validate transcript
        2. Check deduplication
        3. Resolve date (semantic → calendar → today)
        4. Generate folder name
        5. Create folder and files
        6. Record in dedup database
        """
        validation_errors = []
        
        # Step 1: Validate
        validation_results = TranscriptValidator.validate(transcript)
        errors = [v for v in validation_results if v.severity == ValidationSeverity.ERROR]
        warnings = [v for v in validation_results if v.severity == ValidationSeverity.WARNING]
        
        if errors:
            return IntakeResult(
                success=False,
                error_message=f"Validation failed: {errors[0].message}",
                validation_results=errors,
            )
        
        if warnings:
            validation_errors = warnings
        
        # Step 2: Deduplication
        content_hash = self._compute_content_hash(transcript)
        meeting_date = self._resolve_date(transcript) # Moved up for dedup logic
        
        if not force:
            existing = self._check_duplicate(transcript, content_hash, meeting_date)
            if existing:
                return IntakeResult(
                    success=False,
                    error_message=f"Duplicate detected: {existing}",
                    duplicate_of=existing,
                )
        
        # Step 4: Generate folder name
        folder_name = self._generate_folder_name(transcript, meeting_date)
        folder_path = self.inbox_path / folder_name
        
        # Handle name collision
        if folder_path.exists():
            counter = 1
            while folder_path.exists():
                folder_path = self.inbox_path / f"{folder_name}_{counter}"
                counter += 1
        
        # Step 5: Create folder and files
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Write transcript.md
            transcript_file = folder_path / "transcript.md"
            self._write_transcript_md(transcript, transcript_file)
            
            # Write transcript.jsonl (structured format)
            jsonl_file = folder_path / "transcript.jsonl"
            self._write_transcript_jsonl(transcript, jsonl_file)
            
            # Write metadata.json
            metadata_file = folder_path / "metadata.json"
            self._write_metadata(transcript, meeting_date, metadata_file)
            
            logger.info(f"Created meeting folder: {folder_path}")
            
        except Exception as e:
            logger.exception(f"Failed to create meeting folder: {folder_path}")
            return IntakeResult(
                success=False,
                error_message=f"Failed to create folder: {e}",
            )
        
        # Step 6: Record in dedup database
        self._record_ingestion(transcript, content_hash, str(folder_path), meeting_date)
        
        return IntakeResult(
            success=True,
            folder_path=str(folder_path),
            folder_name=folder_path.name,
            validation_results=validation_errors if validation_errors else [],
        )
    
    def _compute_content_hash(self, transcript: UnifiedTranscript) -> str:
        """Compute SHA-256 hash of transcript content for deduplication"""
        # Normalize: lowercase, strip whitespace, remove timestamps
        content = transcript.full_text.lower().strip()
        content = " ".join(content.split())  # Normalize whitespace
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _check_duplicate(
        self,
        transcript: UnifiedTranscript,
        content_hash: str,
        meeting_date: date,
    ) -> Optional[str]:
        """
        Check if transcript is a duplicate.
        
        Layers:
        1. Source ID match (exact)
        2. Content hash match (cross-source semantic)
        3. Time-window match (+/- 24 hours on same date with overlapping title/participants)
        """
        conn = sqlite3.connect(self.dedup_db_path)
        cursor = conn.cursor()
        
        # 1. Check by source_id first (most reliable)
        if transcript.source_id:
            cursor.execute(
                "SELECT folder_path FROM ingested_transcripts WHERE source = ? AND source_id = ?",
                (transcript.source.value, transcript.source_id)
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                return row[0]
        
        # 2. Check by content hash
        cursor.execute(
            "SELECT folder_path FROM ingested_transcripts WHERE content_hash = ?",
            (content_hash,)
        )
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]

        # 3. Time-window / Semantic match
        # Check if any meeting exists on the SAME DATE with a SIMILAR TITLE
        # This catches "V/Mihir Sync" vs "Mihir/Vrijen Meeting" from different bots
        date_str = meeting_date.isoformat()
        cursor.execute(
            "SELECT folder_path, title FROM ingested_transcripts WHERE meeting_date = ?",
            (date_str,)
        )
        rows = cursor.fetchall()
        
        if transcript.title:
            current_title = transcript.title.lower()
            for folder_path, existing_title in rows:
                if not existing_title: continue
                
                # Check for significant title overlap
                # (e.g. "Careerspan" in both, or "Mihir" in both)
                existing_lower = existing_title.lower()
                
                # Simple Jaccard-ish similarity or keyword overlap
                current_words = set(re.findall(r'\w+', current_title))
                existing_words = set(re.findall(r'\w+', existing_lower))
                
                # Ignore common words
                common_ignore = {'sync', 'meeting', 'call', 'with', 'and', 'zoom', 'fathom', 'fireflies', 
                                 'project', 'review', 'kickoff', 'demo', 'standup', 'update', 'check', 'in'}
                current_words -= common_ignore
                existing_words -= common_ignore
                
                overlap = current_words.intersection(existing_words)
                
                # Require EITHER:
                # - At least 2 shared unique words, OR
                # - Overlap > 50% of the smaller set of unique words
                min_unique = min(len(current_words), len(existing_words))
                overlap_ratio = len(overlap) / min_unique if min_unique > 0 else 0
                
                if (len(overlap) >= 2) or (overlap_ratio > 0.5 and len(overlap) >= 1 and min_unique >= 2):
                    # Strong title similarity on same day → likely a dupe
                    conn.close()
                    return folder_path

        conn.close()
        return None
    
    def _resolve_date(self, transcript: UnifiedTranscript) -> date:
        """
        Resolve meeting date using V's priority order:
        1. Semantic detection from transcript
        2. Calendar lookup
        3. Today
        """
        # Priority 1: Already detected date
        if transcript.detected_date:
            return transcript.detected_date.date()
        
        # Priority 2: Calendar lookup (if service available)
        if self.calendar_service and transcript.title:
            try:
                calendar_date = self._lookup_calendar(transcript)
                if calendar_date:
                    return calendar_date
            except Exception as e:
                logger.warning(f"Calendar lookup failed: {e}")
        
        # Priority 3: Today
        return date.today()
    
    def _lookup_calendar(self, transcript: UnifiedTranscript) -> Optional[date]:
        """
        Look up meeting in calendar by title/participants.
        
        This is a placeholder - actual implementation depends on
        calendar service integration.
        """
        # TODO: Implement calendar lookup via use_app_google_calendar
        # For now, return None to fall through to "today"
        return None
    
    def _generate_folder_name(
        self,
        transcript: UnifiedTranscript,
        meeting_date: date,
    ) -> str:
        """
        Generate canonical folder name.
        
        Format: YYYY-MM-DD_<title-or-participants>
        """
        date_str = meeting_date.strftime("%Y-%m-%d")
        
        # Prefer title
        if transcript.title:
            name_part = self._sanitize_name(transcript.title)
        # Fall back to first participant (not V)
        elif transcript.participants:
            # Filter out V's name variants
            v_names = {"vrijen", "v", "vrijen attawar", "attawar"}
            others = [p for p in transcript.participants if p.lower() not in v_names]
            if others:
                name_part = self._sanitize_name(others[0])
            else:
                name_part = "Meeting"
        else:
            name_part = "Meeting"
        
        return f"{date_str}_{name_part}"
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in folder name"""
        import re
        # Remove special characters, replace spaces with hyphens
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"\s+", "-", name.strip())
        # Limit length
        if len(name) > 50:
            name = name[:50]
        return name or "Meeting"
    
    def _write_transcript_md(self, transcript: UnifiedTranscript, path: Path):
        """Write human-readable transcript markdown"""
        with open(path, "w") as f:
            f.write(f"# {transcript.title or 'Meeting Transcript'}\n\n")
            
            # Metadata header
            f.write("---\n")
            f.write(f"source: {transcript.source.value}\n")
            if transcript.detected_date:
                f.write(f"date: {transcript.detected_date.date().isoformat()}\n")
            if transcript.participants:
                f.write(f"participants: {', '.join(transcript.participants)}\n")
            if transcript.duration_seconds:
                mins = transcript.duration_seconds // 60
                f.write(f"duration: {mins} minutes\n")
            f.write("---\n\n")
            
            # Summary if available
            if transcript.summary:
                f.write("## Summary\n\n")
                f.write(f"{transcript.summary}\n\n")
            
            # Transcript body
            f.write("## Transcript\n\n")
            f.write(transcript.full_text)
    
    def _write_transcript_jsonl(self, transcript: UnifiedTranscript, path: Path):
        """Write structured transcript in JSONL format"""
        data = {
            "text": transcript.full_text,
            "source": transcript.source.value,
            "source_id": transcript.source_id,
            "title": transcript.title,
            "participants": transcript.participants,
            "host": transcript.host,
            "duration_seconds": transcript.duration_seconds,
            "recording_url": transcript.recording_url,
            "summary": transcript.summary,
        }
        
        if transcript.detected_date:
            data["date"] = transcript.detected_date.isoformat()
        
        if transcript.utterances:
            data["utterances"] = [
                {
                    "speaker": u.speaker,
                    "text": u.text,
                    "start": u.start_ms,
                    "end": u.end_ms,
                }
                for u in transcript.utterances
            ]
        
        with open(path, "w") as f:
            f.write(json.dumps(data))
    
    def _write_metadata(
        self,
        transcript: UnifiedTranscript,
        meeting_date: date,
        path: Path,
    ):
        """Write metadata.json for meeting folder"""
        metadata = {
            "source": transcript.source.value,
            "source_id": transcript.source_id,
            "title": transcript.title,
            "date": meeting_date.isoformat(),
            "participants": transcript.participants,
            "host": transcript.host,
            "duration_seconds": transcript.duration_seconds,
            "recording_url": transcript.recording_url,
            "ingested_at": datetime.now().isoformat(),
            "state": "raw",  # For N5 meeting pipeline: raw → [M] → [P] → [C]
        }
        
        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def _record_ingestion(
        self,
        transcript: UnifiedTranscript,
        content_hash: str,
        folder_path: str,
        meeting_date: date,
    ):
        """Record successful ingestion in dedup database"""
        conn = sqlite3.connect(self.dedup_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO ingested_transcripts 
                (source, source_id, content_hash, folder_path, ingested_at, title, meeting_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transcript.source.value,
                    transcript.source_id,
                    content_hash,
                    folder_path,
                    datetime.now().isoformat(),
                    transcript.title,
                    meeting_date.isoformat(),
                )
            )
            conn.commit()
        finally:
            conn.close()









