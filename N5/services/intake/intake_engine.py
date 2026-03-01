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
from datetime import datetime, date, timezone
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
    DEDUP_WINDOW_SECONDS = 600
    HOST_NAME_ALIASES = {
        "vrijen",
        "vrijenattawar",
        "attawar",
        "va",
        "v",
    }
    TITLE_STOPWORDS = {
        "meeting",
        "call",
        "sync",
        "update",
        "standup",
        "demo",
        "review",
        "check",
        "with",
        "and",
        "weekly",
        "monthly",
        "team",
        "internal",
        "external",
        "status",
        "planning",
        "alignment",
        "loop",
        "catch",
        "up",
        "briefing",
    }
    
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
                fingerprint TEXT,
                PRIMARY KEY (source, source_id)
            )
            """
        )
        # Add index on content_hash and meeting_date for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON ingested_transcripts (content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_date ON ingested_transcripts (meeting_date)")
        self._ensure_dedup_columns(cursor)
        conn.commit()
        conn.close()
    
    def _ensure_dedup_columns(self, cursor):
        cursor.execute("PRAGMA table_info(ingested_transcripts)")
        columns = {row[1] for row in cursor.fetchall()}
        if "fingerprint" not in columns:
            cursor.execute("ALTER TABLE ingested_transcripts ADD COLUMN fingerprint TEXT")
        if "participant_hash" not in columns:
            cursor.execute("ALTER TABLE ingested_transcripts ADD COLUMN participant_hash TEXT")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fingerprint ON ingested_transcripts (fingerprint)")
    
    def _normalize_participants_list(self, participants):
        normalized = []
        for participant in participants or []:
            name = self._normalize_participant_name(participant)
            if name and name not in self.HOST_NAME_ALIASES:
                normalized.append(name)
        if not normalized:
            normalized = ["unknown"]
        return sorted(set(normalized))
    
    @staticmethod
    def _normalize_participant_name(name: str) -> str:
        if not name:
            return ""
        cleaned = re.sub(r"[^a-z0-9]", "", name.lower())
        return cleaned
    
    def _round_to_window(self, dt: datetime) -> datetime:
        if dt is None:
            dt = datetime.utcnow()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        timestamp = int(dt.timestamp())
        bucket = timestamp - (timestamp % self.DEDUP_WINDOW_SECONDS)
        return datetime.fromtimestamp(bucket, tz=timezone.utc)
    
    def _normalize_title_tokens(self, title: Optional[str]) -> list[str]:
        if not title:
            return []
        words = re.findall(r"\w+", title.lower())
        tokens = [w for w in words if w not in self.TITLE_STOPWORDS]
        return sorted(set(tokens))
    
    def _compute_participant_hash(self, normalized_participants: list[str]) -> str:
        joined = "|".join(normalized_participants)
        return hashlib.sha256(joined.encode()).hexdigest()[:16]
    
    def _compute_fingerprint(
        self,
        transcript: UnifiedTranscript,
        meeting_date: date,
        normalized_participants: list[str],
    ) -> str:
        rounded_time = self._round_to_window(transcript.detected_date)
        participant_key = "|".join(normalized_participants)
        fingerprint_input = "|".join(
            filter(None, [
                rounded_time.isoformat(),
                meeting_date.isoformat(),
                participant_key,
            ])
        )
        if not fingerprint_input:
            fingerprint_input = meeting_date.isoformat()
        return hashlib.sha256(fingerprint_input.encode()).hexdigest()[:32]
    
    def _compute_content_hash(self, transcript: UnifiedTranscript) -> str:
        """Compute SHA-256 hash of transcript content for deduplication"""
        content = transcript.full_text.lower().strip()
        content = " ".join(content.split())
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
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

        # Step 2: Deduplication inputs
        content_hash = self._compute_content_hash(transcript)
        meeting_date = self._resolve_date(transcript)
        normalized_participants = self._normalize_participants_list(transcript.participants)
        participant_hash = self._compute_participant_hash(normalized_participants)
        fingerprint = self._compute_fingerprint(transcript, meeting_date, normalized_participants)

        if not force:
            existing = self._check_duplicate(transcript, content_hash, meeting_date, fingerprint)
            if existing:
                logger.info("Duplicate fingerprint %s matched existing folder %s", fingerprint, existing)
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
            self._write_metadata(transcript, meeting_date, metadata_file, fingerprint, participant_hash)

            # Write manifest.json so downstream tick/process can run immediately
            manifest_file = folder_path / "manifest.json"
            self._write_manifest(
                transcript,
                meeting_date,
                folder_path.name,
                manifest_file,
                fingerprint,
                participant_hash,
            )

            logger.info(f"Created meeting folder: {folder_path}")

        except Exception as e:
            logger.exception(f"Failed to create meeting folder: {folder_path}")
            return IntakeResult(
                success=False,
                error_message=f"Failed to create folder: {e}",
            )

        # Step 6: Record in dedup database
        self._record_ingestion(
            transcript,
            content_hash,
            str(folder_path),
            meeting_date,
            fingerprint,
            participant_hash,
        )

        return IntakeResult(
            success=True,
            folder_path=str(folder_path),
            folder_name=folder_path.name,
            validation_results=validation_errors if validation_errors else [],
        )

    def _check_duplicate(
        self,
        transcript: UnifiedTranscript,
        content_hash: str,
        meeting_date: date,
        fingerprint: str,
    ) -> Optional[str]:
        """
        Check if transcript is a duplicate.

        Layers:
        0. Canonical fingerprint (cross-source, time-bucket + date + participants)
        1. Source ID match (exact, same-source re-delivery)
        2. Content hash match (cross-source identical text)
        3. Title overlap on same date (legacy heuristic)
        4. Ingestion-time proximity + participant overlap (catches Fathom/Fireflies
           with different titles and slightly different participant names)
        """
        conn = sqlite3.connect(self.dedup_db_path)
        cursor = conn.cursor()

        # 0. Check fingerprint first to catch near-simultaneous duplicates
        if fingerprint:
            cursor.execute(
                "SELECT folder_path FROM ingested_transcripts WHERE fingerprint = ?",
                (fingerprint,)
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                return row[0]

        # 1. Check by source_id next (most reliable)
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

        # 3. Title overlap on same date (existing heuristic)
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

                existing_lower = existing_title.lower()

                current_words = set(re.findall(r"\w+", current_title))
                existing_words = set(re.findall(r"\w+", existing_lower))

                common_ignore = {'sync', 'meeting', 'call', 'with', 'and', 'zoom', 'fathom', 'fireflies',
                                 'project', 'review', 'kickoff', 'demo', 'standup', 'update', 'check', 'in'}
                current_words -= common_ignore
                existing_words -= common_ignore

                overlap = current_words.intersection(existing_words)

                min_unique = min(len(current_words), len(existing_words))
                overlap_ratio = len(overlap) / min_unique if min_unique > 0 else 0

                if (len(overlap) >= 2) or (overlap_ratio > 0.5 and len(overlap) >= 1 and min_unique >= 2):
                    conn.close()
                    return folder_path

        # 4. Cross-source ingestion-time proximity
        #    If a transcript from a DIFFERENT source was ingested on the same date
        #    within DEDUP_WINDOW_SECONDS, it's the same meeting. This is the primary
        #    catch for Fathom vs Fireflies where titles differ completely
        #    ("Impromptu Google Meet" vs "kgb-eonn-wbg") and participant lists
        #    don't align (Fathom may only list the host).
        #    Rationale: you never have two separate meetings, each captured by only
        #    one transcription service, ending within 10 minutes of each other.
        cursor.execute(
            "SELECT folder_path, ingested_at, source FROM ingested_transcripts WHERE meeting_date = ?",
            (date_str,)
        )
        proximity_rows = cursor.fetchall()

        for folder_path, ingested_at_str, existing_source in proximity_rows:
            if not ingested_at_str:
                continue
            if existing_source == transcript.source.value:
                continue
            try:
                ingested_at = datetime.fromisoformat(ingested_at_str)
                if ingested_at.tzinfo is None:
                    ingested_at = ingested_at.replace(tzinfo=timezone.utc)
                now_dt = datetime.now(timezone.utc)
                delta = abs((now_dt - ingested_at).total_seconds())
            except (ValueError, TypeError):
                continue

            if delta <= self.DEDUP_WINDOW_SECONDS:
                logger.info(
                    "Cross-source dedup: %s ingested %ds after %s entry for %s — treating as duplicate",
                    transcript.source.value, int(delta), existing_source, date_str,
                )
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
        fingerprint: str,
        participant_hash: str,
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
            "state": "raw",
            "fingerprint": fingerprint,
            "participant_hash": participant_hash,
        }

        with open(path, "w") as f:
            json.dump(metadata, f, indent=2)

    def _write_manifest(
        self,
        transcript: UnifiedTranscript,
        meeting_date: date,
        folder_name: str,
        path: Path,
        fingerprint: str,
        participant_hash: str,
    ):
        """Write v3 manifest seed so meeting_cli tick can process this folder."""
        now_iso = datetime.utcnow().isoformat() + "Z"
        duration_minutes = int(transcript.duration_seconds / 60) if transcript.duration_seconds else None
        meeting_title = transcript.title or folder_name

        identified = []
        for participant in transcript.participants or []:
            if not participant:
                continue
            identified.append(
                {
                    "name": participant,
                    "email": None,
                    "crm_id": None,
                    "role": "attendee",
                    "confidence": 0.5,
                }
            )

        manifest = {
            "$schema": "manifest-v3",
            "schema_version": "v3",
            "meeting_id": folder_name,
            "status": "ingested",
            "status_history": [
                {"status": "ingested", "at": now_iso},
            ],
            "source": {
                "type": transcript.source.value,
                "source_id": transcript.source_id,
                "ingested_at": now_iso,
            },
            "meeting": {
                "date": meeting_date.isoformat(),
                "time_utc": transcript.detected_date.strftime("%H:%M:%S") if transcript.detected_date else None,
                "duration_minutes": duration_minutes,
                "title": meeting_title,
                "type": "external",
                "summary": transcript.summary,
            },
            "participants": {
                "identified": identified,
                "unidentified": [],
                "confidence": 0.5 if identified else 0.0,
            },
            "calendar_match": {
                "event_id": None,
                "confidence": 0.0,
                "method": "none",
            },
            "quality_gate": {
                "passed": False,
                "checks": {},
                "score": 0.0,
            },
            "blocks": {
                "policy": "external_standard",
                "requested": [],
                "generated": [],
                "failed": [],
                "skipped": [],
            },
            "hitl": {
                "queue_id": None,
                "reason": None,
                "resolved_at": None,
            },
            "timestamps": {
                "created_at": now_iso,
                "ingested_at": now_iso,
                "identified_at": None,
                "gated_at": None,
                "processed_at": None,
                "archived_at": None,
            },
            "transcript_file": "transcript.md",
            "dedup": {
                "fingerprint": fingerprint,
                "participant_hash": participant_hash,
                "window_seconds": self.DEDUP_WINDOW_SECONDS,
            },
        }

        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)

    def _record_ingestion(
        self,
        transcript: UnifiedTranscript,
        content_hash: str,
        folder_path: str,
        meeting_date: date,
        fingerprint: str,
        participant_hash: str,
    ):
        """Record successful ingestion in dedup database"""
        conn = sqlite3.connect(self.dedup_db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO ingested_transcripts 
                (source, source_id, content_hash, folder_path, ingested_at, title, meeting_date, fingerprint, participant_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transcript.source.value,
                    transcript.source_id,
                    content_hash,
                    folder_path,
                    datetime.now().isoformat(),
                    transcript.title,
                    meeting_date.isoformat(),
                    fingerprint,
                    participant_hash,
                )
            )
            conn.commit()
        finally:
            conn.close()








