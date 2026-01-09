"""
Fathom Transcript Processor: Processes Fathom payload and saves to Personal/Meetings/Inbox
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
import shutil
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from .fathom_client import FathomClient
from .webhook_processor import WebhookProcessor
from intake.intake_engine import IntakeEngine
from intake.models import IntakeSource

logger = logging.getLogger(__name__)

class TranscriptProcessor:
    """Processes pending Fathom webhooks and saves transcripts to Inbox"""
    
    def __init__(
        self,
        fathom_client: Optional[FathomClient] = None,
        webhook_processor: Optional[WebhookProcessor] = None,
        inbox_path: Path = Path("/home/workspace/Personal/Meetings/Inbox"),
        meetings_root: Path = Path("/home/workspace/Personal/Meetings")
    ):
        self.fathom_client = fathom_client or FathomClient()
        self.webhook_processor = webhook_processor or WebhookProcessor()
        self.intake_engine = IntakeEngine()
        self.inbox_path = inbox_path
        self.meetings_root = meetings_root
        
        if not self.inbox_path.exists():
            self.inbox_path.mkdir(parents=True, exist_ok=True)
    
    def _transcript_already_exists(self, recording_id: int) -> Optional[Path]:
        """Check if a recording_id already exists in the Meetings hierarchy"""
        if not recording_id:
            return None
        
        search_dirs = [self.inbox_path]
        for item in self.meetings_root.iterdir():
            if item.is_dir() and (item.name.startswith("Week-of-") or item.name == "Archive"):
                search_dirs.append(item)
        
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
                        if metadata.get("recording_id") == recording_id:
                            return meeting_folder
                    except (json.JSONDecodeError, IOError):
                        continue
        return None
    
    def process_pending_webhooks(self, limit: int = 10) -> Dict[str, Any]:
        pending = self.webhook_processor.get_pending_webhooks()
        
        if not pending:
            return {"processed": 0, "success": 0, "failed": 0}
        
        stats = {"processed": 0, "success": 0, "failed": 0}
        
        for webhook in pending[:limit]:
            webhook_id = webhook["webhook_id"]
            payload_str = webhook["payload"]
            
            try:
                payload_data = json.loads(payload_str)
                
                # Fathom often sends the transcript IN the webhook payload.
                # If transcript is missing, we might need to fetch it via API,
                # but let's assume it's there based on the documentation.
                
                meeting_folder = self.save_transcript_to_inbox(payload_data)
                
                if meeting_folder:
                    self.webhook_processor.update_webhook_status(
                        webhook_id,
                        "processed",
                        f"Saved to {meeting_folder}"
                    )
                    stats["success"] += 1
                else:
                    self.webhook_processor.update_webhook_status(
                        webhook_id,
                        "failed",
                        "Failed to save transcript to Inbox"
                    )
                    stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing Fathom webhook {webhook_id}: {e}")
                self.webhook_processor.update_webhook_status(
                    webhook_id,
                    "failed",
                    str(e)
                )
                stats["failed"] += 1
            
            stats["processed"] += 1
        
        return stats
    
    def save_transcript_to_inbox(self, payload: Dict[str, Any]) -> Optional[str]:
        try:
            # Step 1: Ingest using the Unified Intake Engine
            # This handles dedup, folder naming, metadata creation, and file writing
            result = self.intake_engine.ingest_from_source(
                source=IntakeSource.FATHOM,
                payload=payload
            )
            
            if result.success:
                logger.info(f"Unified Ingest Successful (Fathom): {result.folder_path}")
                return result.folder_name
            else:
                if result.duplicate_of:
                    logger.info(f"Fathom transcript is a duplicate of {result.duplicate_of}. Skipping.")
                    # Return the name of the existing folder to mark webhook as processed
                    return Path(result.duplicate_of).name
                
                logger.error(f"Unified Ingest Failed (Fathom): {result.error_message}")
                return None
                
        except Exception as e:
            logger.exception(f"Exception during Unified Ingest for Fathom: {e}")
            return None

    def _format_participant_names(self, invitees: list, title: str) -> str:
        names = []
        for p in invitees[:4]:
            name = p.get('name') or p.get('email', '').split('@')[0]
            name = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip()
            if name:
                names.append(name)
        
        if not names:
            return re.sub(r'[^a-zA-Z0-9\s-]', '', title)[:50].strip().replace(' ', '_')
        
        return '_'.join(names)

    def _convert_to_zo_format(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        transcript_list = payload.get("transcript", [])
        
        full_text = "\n".join([t.get("text", "") for t in transcript_list])
        
        utterances = []
        for t in transcript_list:
            speaker_info = t.get("speaker", {})
            speaker_name = speaker_info.get("display_name", "Unknown")
            
            # Fathom timestamp is HH:MM:SS, convert to ms
            ts_str = t.get("timestamp", "00:00:00")
            parts = ts_str.split(':')
            ms = 0
            if len(parts) == 3:
                ms = (int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])) * 1000
            
            utterances.append({
                "speaker": speaker_name,
                "start": ms,
                "end": ms, # Fathom doesn't provide end time per utterance in this view
                "text": t.get("text", "")
            })
            
        return {
            "text": full_text,
            "utterances": utterances,
            "chunks": utterances, # Simple mapping for now
            "source_file": payload.get("url"),
            "recording_id": payload.get("recording_id")
        }




