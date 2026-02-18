"""
Transcript Processor: Fetches from Fireflies and saves to Personal/Meetings/Inbox
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
import shutil
import os
import subprocess

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from .fireflies_client import FirefliesClient
from .webhook_processor import WebhookProcessor
from intake.intake_engine import IntakeEngine
from intake.models import IntakeSource

logger = logging.getLogger(__name__)

class DuplicateManager:
    """Handles temporal and participant deduplication for meeting transcripts."""
    
    INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
    QUARANTINE = INBOX / "_quarantine"

    @classmethod
    def find_potential_duplicate(cls, start_time: datetime, participants: List[str]) -> Optional[Path]:
        """Finds an existing folder with overlapping time and participants."""
        cls.QUARANTINE.mkdir(exist_ok=True)
        
        # Scan ±45 minutes (generous window for delays)
        window_start = start_time - timedelta(minutes=45)
        window_end = start_time + timedelta(minutes=45)
        
        for folder in cls.INBOX.iterdir():
            if not folder.is_dir() or folder.name.startswith("_"):
                continue
            
            # Extract date from folder name (YYYY-MM-DD)
            try:
                folder_date_str = folder.name[:10]
                if folder_date_str != start_time.strftime("%Y-%m-%d"):
                    continue
            except:
                continue

            metadata_path = folder / "metadata.json"
            if not metadata_path.exists():
                continue
                
            try:
                with open(metadata_path, 'r') as f:
                    meta = json.load(f)
                
                # Check Time Overlap
                # Many sources use epoch or ISO, we assume ISO from metadata_manager
                meta_time_str = meta.get("date") # Assuming standard metadata format
                if isinstance(meta_time_str, (int, float)):
                    meta_time = datetime.fromtimestamp(meta_time_str)
                else:
                    meta_time = datetime.fromisoformat(meta_time_str.replace("Z", "+00:00"))

                if window_start <= meta_time <= window_end:
                    # Check Participant Overlap (at least one matching email)
                    meta_participants = meta.get("participants", [])
                    if any(p in meta_participants for p in participants):
                        return folder
            except Exception as e:
                logger.warning(f"Error checking duplicate in {folder}: {e}")
                continue
                
        return None

    @classmethod
    def quarantine(cls, folder: Path, reason: str):
        """Moves a redundant folder to quarantine."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = cls.QUARANTINE / f"{folder.name}_quarantined_{timestamp}"
        shutil.move(str(folder), str(target))
        with open(target / "quarantine_reason.txt", "w") as f:
            f.write(reason)
        logger.info(f"Quarantined {folder.name}: {reason}")

class TranscriptProcessor:
    """Processes pending webhooks and saves transcripts to Inbox"""
    
    def __init__(
        self,
        fireflies_client: Optional[FirefliesClient] = None,
        webhook_processor: Optional[WebhookProcessor] = None,
        inbox_path: Path = Path("/home/workspace/Personal/Meetings/Inbox"),
        meetings_root: Path = Path("/home/workspace/Personal/Meetings")
    ):
        self.fireflies_client = fireflies_client or FirefliesClient()
        self.webhook_processor = webhook_processor or WebhookProcessor()
        self.intake_engine = IntakeEngine()
        self.last_error: Optional[str] = None
        self.inbox_path = inbox_path
        self.meetings_root = meetings_root
        
        if not self.inbox_path.exists():
            logger.warning(f"Inbox path does not exist: {self.inbox_path}")

    def _trigger_auto_process(self, meeting_folder_name: str) -> None:
        """Trigger shared meeting pipeline for a specific deposited meeting."""
        if not meeting_folder_name:
            return
        cli_path = "/home/workspace/Skills/meeting-ingestion/scripts/meeting_cli.py"
        log_path = f"/dev/shm/meeting-process-{meeting_folder_name}.log"
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                subprocess.Popen(
                    [sys.executable, cli_path, "tick", "--auto-process", "--target", meeting_folder_name],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            logger.info(f"Auto-processing triggered for {meeting_folder_name} (log: {log_path})")
        except Exception as e:
            logger.error(f"Failed to trigger auto-processing for {meeting_folder_name}: {e}")
    
    def _transcript_already_exists(self, transcript_id: str) -> Optional[Path]:
        """
        Check if a transcript_id already exists anywhere in the Meetings hierarchy.
        Scans metadata.json files in Inbox, Week-of-* folders, and Archive.
        
        Returns:
            Path to existing folder if found, None otherwise
        """
        if not transcript_id:
            return None
        
        # Directories to search
        search_dirs = [self.inbox_path]
        
        # Add week folders
        for item in self.meetings_root.iterdir():
            if item.is_dir() and (item.name.startswith("Week-of-") or item.name == "Archive"):
                search_dirs.append(item)
        
        # Search each directory
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            for meeting_folder in search_dir.iterdir():
                if not meeting_folder.is_dir():
                    continue
                
                metadata_file = meeting_folder / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        if metadata.get("transcript_id") == transcript_id:
                            return meeting_folder
                    except (json.JSONDecodeError, IOError):
                        continue
        
        return None
    
    def process_pending_webhooks(self, limit: int = 10) -> Dict[str, Any]:
        """
        Process pending webhooks: fetch transcripts and save to Inbox
        
        Returns:
            Dict with processing stats (processed, success, failed)
        """
        pending = self.webhook_processor.get_pending_webhooks()
        
        if not pending:
            logger.info("No pending webhooks to process")
            return {"processed": 0, "success": 0, "failed": 0}
        
        stats = {"processed": 0, "success": 0, "failed": 0}
        
        for webhook in pending[:limit]:
            webhook_id = webhook["webhook_id"]
            transcript_id = webhook["transcript_id"]
            
            logger.info(f"Processing webhook {webhook_id} for transcript {transcript_id}")
            
            try:
                # Fetch transcript from Fireflies
                transcript_data = self.fireflies_client.get_transcript(transcript_id)
                
                if not transcript_data:
                    self.webhook_processor.update_webhook_status(
                        webhook_id, 
                        "failed", 
                        "Failed to fetch transcript from Fireflies API"
                    )
                    stats["failed"] += 1
                    continue
                
                # Convert and save
                meeting_folder = self.save_transcript_to_inbox(transcript_data)
                
                if meeting_folder:
                    self.webhook_processor.update_webhook_status(
                        webhook_id,
                        "processed",
                        f"Saved to {meeting_folder}"
                    )
                    stats["success"] += 1
                else:
                    err = self.last_error or "Failed to save transcript to Inbox"
                    self.webhook_processor.update_webhook_status(
                        webhook_id,
                        "failed",
                        err
                    )
                    stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing webhook {webhook_id}: {e}")
                self.webhook_processor.update_webhook_status(
                    webhook_id,
                    "failed",
                    str(e)
                )
                stats["failed"] += 1
            
            stats["processed"] += 1
        
        logger.info(f"Processed {stats['processed']} webhooks: {stats['success']} success, {stats['failed']} failed")
        return stats
    
    def save_transcript_to_inbox(self, transcript_data: Dict[str, Any]) -> Optional[str]:
        """
        Convert Fireflies transcript to Zo format and save to Inbox using Unified Intake Engine
        
        Returns:
            Folder name if successful, None if failed
        """
        try:
            self.last_error = None
            # Step 1: Ingest using the Unified Intake Engine
            # This handles dedup, folder naming, metadata creation, and file writing
            result = self.intake_engine.ingest_from_source(
                source=IntakeSource.FIREFLIES,
                payload=transcript_data
            )
            
            if result.success:
                logger.info(f"Unified Ingest Successful: {result.folder_path}")
                self._trigger_auto_process(result.folder_name)
                return result.folder_name
            else:
                if result.duplicate_of:
                    logger.info(f"Transcript is a duplicate of {result.duplicate_of}. Skipping.")
                    return Path(result.duplicate_of).name
                
                self.last_error = result.error_message or "Unified ingest failed"
                logger.error(f"Unified Ingest Failed: {self.last_error}")
                return None
                
        except Exception as e:
            self.last_error = str(e)
            logger.exception(f"Exception during Unified Ingest for Fireflies: {e}")
            return None
    
    # Keeping helper methods for backwards compatibility if needed, 
    # but they are largely shadowed by the IntakeEngine now
    def _format_participant_names(self, participants: list, title: str) -> str:
        """Extract participant names for folder naming"""
        if not participants:
            # Try to extract from title
            # Common patterns: "Meeting with X", "X and Y", etc.
            return re.sub(r'[^a-zA-Z0-9\s-]', '', title)[:50].strip().replace(' ', '_')
        
        # Clean participant names
        names = []
        for p in participants[:4]:  # Limit to 4 names
            if isinstance(p, dict):
                name = p.get('name') or p.get('displayName') or p.get('email', '').split('@')[0]
            else:
                name = str(p)
            
            # Clean name
            name = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip()
            if name:
                names.append(name)
        
        if not names:
            return "meeting"
        
        return '_'.join(names[:4])
    
    def _convert_to_zo_format(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Fireflies transcript format to Zo transcript format
        
        Zo format:
        {
            "text": "full transcript text",
            "utterances": [{speaker, start, end, text}],
            "chunks": [{speaker, start, end, text}],
            "words": [{text, start, end, speaker}],
            "source_file": "original file path",
            "duration_seconds": float
        }
        """
        sentences = transcript_data.get("sentences", [])
        
        # Build full text
        full_text = "\n".join([s.get("text", "") for s in sentences if s.get("text")])
        
        # Convert sentences to utterances
        utterances = []
        for s in sentences:
            utterances.append({
                "speaker": s.get("speaker_name", "Unknown"),
                "start": int(s.get("start_time", 0) * 1000),  # Convert to ms
                "end": int(s.get("end_time", 0) * 1000),
                "text": s.get("text", "")
            })
        
        # Group into chunks (by speaker changes and pauses)
        chunks = self._group_into_chunks(utterances)
        
        # Extract words (if available in raw_text)
        words = self._extract_words(sentences)
        
        return {
            "text": full_text,
            "utterances": utterances,
            "chunks": chunks,
            "words": words,
            "source_file": transcript_data.get("audio_url") or transcript_data.get("video_url"),
            "duration_seconds": transcript_data.get("duration", 0),
            "source_mime_type": "audio/mpeg",  # Assumption
            "fireflies_id": transcript_data.get("id"),
        }
    
    def _group_into_chunks(self, utterances: list) -> list:
        """Group utterances into chunks by speaker changes"""
        if not utterances:
            return []
        
        chunks = []
        current_chunk = None
        
        for utt in utterances:
            if not current_chunk or current_chunk["speaker"] != utt["speaker"]:
                # New chunk
                if current_chunk:
                    chunks.append(current_chunk)
                
                current_chunk = {
                    "speaker": utt["speaker"],
                    "start": utt["start"],
                    "end": utt["end"],
                    "text": utt["text"]
                }
            else:
                # Append to current chunk
                current_chunk["end"] = utt["end"]
                current_chunk["text"] += " " + utt["text"]
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _extract_words(self, sentences: list) -> list:
        """Extract word-level timing if available"""
        # Fireflies may not provide word-level timing
        # Return empty list for now
        return []








