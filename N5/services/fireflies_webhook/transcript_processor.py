"""
Transcript Processor: Fetches from Fireflies and saves to Personal/Meetings/Inbox
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re

from .fireflies_client import FirefliesClient
from .webhook_processor import WebhookProcessor

logger = logging.getLogger(__name__)

class TranscriptProcessor:
    """Processes pending webhooks and saves transcripts to Inbox"""
    
    def __init__(
        self,
        fireflies_client: Optional[FirefliesClient] = None,
        webhook_processor: Optional[WebhookProcessor] = None,
        inbox_path: Path = Path("/home/workspace/Personal/Meetings/Inbox")
    ):
        self.fireflies_client = fireflies_client or FirefliesClient()
        self.webhook_processor = webhook_processor or WebhookProcessor()
        self.inbox_path = inbox_path
        
        if not self.inbox_path.exists():
            logger.warning(f"Inbox path does not exist: {self.inbox_path}")
    
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
                    self.webhook_processor.update_webhook_status(
                        webhook_id,
                        "failed",
                        "Failed to save transcript to Inbox"
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
        Convert Fireflies transcript to Zo format and save to Inbox
        
        Returns:
            Folder name if successful, None if failed
        """
        try:
            # Extract metadata
            transcript_id = transcript_data.get("id")
            title = transcript_data.get("title", "Untitled Meeting")
            date_str = transcript_data.get("date")  # ISO format
            participants = transcript_data.get("participants", [])
            duration = transcript_data.get("duration", 0)  # seconds
            
            # Parse date - Fireflies returns Unix timestamp in milliseconds
            if date_str:
                if isinstance(date_str, int):
                    # Unix timestamp in milliseconds
                    meeting_date = datetime.fromtimestamp(date_str / 1000)
                elif isinstance(date_str, str):
                    # ISO format string
                    meeting_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    meeting_date = datetime.now()
            else:
                meeting_date = datetime.now()
            
            # Create folder name: YYYY-MM-DD_participant-names
            date_prefix = meeting_date.strftime("%Y-%m-%d")
            participant_names = self._format_participant_names(participants, title)
            folder_name = f"{date_prefix}_{participant_names}"
            
            # Sanitize folder name
            folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
            folder_name = folder_name[:200]  # Limit length
            
            meeting_folder = self.inbox_path / folder_name
            meeting_folder.mkdir(parents=True, exist_ok=True)
            
            # Convert transcript to Zo format
            zo_transcript = self._convert_to_zo_format(transcript_data)
            
            # Save transcript.jsonl
            transcript_file = meeting_folder / "transcript.jsonl"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(zo_transcript, f, ensure_ascii=False)
            
            # Save metadata
            metadata_file = meeting_folder / "metadata.json"
            metadata = {
                "source": "fireflies",
                "transcript_id": transcript_id,
                "title": title,
                "date": date_str,
                "duration_seconds": duration,
                "participants": participants,
                "processed_at": datetime.now().isoformat(),
                "transcript_url": transcript_data.get("transcript_url"),
                "audio_url": transcript_data.get("audio_url"),
                "video_url": transcript_data.get("video_url"),
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved transcript to {meeting_folder}")
            return folder_name
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            return None
    
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




