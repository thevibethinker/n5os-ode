#!/usr/bin/env python3
"""
Meeting Transcript Watcher - Google Drive Monitor

Monitors Google Drive for new transcripts and creates processing requests for Zo.
Runs periodically to check for new transcript files and queue them for processing.
"""

import json
import hashlib
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from meeting_config import WORKSPACE, MEETINGS_DIR, STAGING_DIR, LOG_DIR, REGISTRY_DB, TIMEZONE, ENABLE_SMS

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE = Path(WORKSPACE)
REQUESTS_DIR = WORKSPACE / "N5" / "queue" / "meeting_processing_requests"
STATE_FILE = WORKSPACE / "N5" / "data" / "transcript_watcher_state.json"
DOWNLOADS_DIR = WORKSPACE / "Downloads" / "Meetings"

# Ensure directories exist
REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


class TranscriptWatcher:
    """Watches for new transcripts and creates processing requests."""
    
    def __init__(self):
        self.processed_ids = self._load_state()
        
    def _load_state(self) -> Set[str]:
        """Load set of already processed transcript IDs."""
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text())
            return set(data.get("processed_ids", []))
        return set()
    
    def _save_state(self):
        """Save processed transcript IDs."""
        STATE_FILE.write_text(json.dumps({
            "processed_ids": list(self.processed_ids),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }, indent=2))
    
    def _generate_file_id(self, file_info: Dict) -> str:
        """Generate stable ID for a transcript file."""
        # Use file ID if available, otherwise hash of name + created time
        if 'id' in file_info:
            return file_info['id']
        
        identifier = f"{file_info['name']}_{file_info.get('createdTime', '')}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _extract_meeting_info(self, filename: str) -> Dict:
        """Extract meeting info from filename."""
        # Example: "Alex x Vrijen - Wisdom Partners Coaching-transcript-2025-10-09T18-06-05.257Z.docx"
        
        info = {
            "stakeholder_primary": "unknown",
            "meeting_type": "general",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Try to parse date from filename
        import re
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            info["date"] = date_match.group(1)
        
        # Try to identify stakeholder (first name before 'x' or ' and ')
        name_patterns = [
            r'^([A-Z][a-z]+)\s+x\s+',  # "Alex x Vrijen"
            r'^([A-Z][a-z]+)\s+and\s+', # "Alex and Vrijen"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, filename)
            if match:
                info["stakeholder_primary"] = match.group(1)
                break
        
        # Try to identify meeting type
        filename_lower = filename.lower()
        if 'coaching' in filename_lower:
            info["meeting_type"] = "coaching"
        elif 'advisory' in filename_lower:
            info["meeting_type"] = "advisory"
        elif 'sales' in filename_lower:
            info["meeting_type"] = "sales"
        elif 'standup' in filename_lower or 'stand-up' in filename_lower:
            info["meeting_type"] = "internal"
        
        return info
    
    async def check_google_drive(self) -> List[Dict]:
        """Check Google Drive for new transcripts."""
        # This will use subprocess to call Google Drive API
        # For now, return empty list - will be implemented with Google Drive integration
        logger.info("Checking Google Drive for new transcripts...")
        
        # TODO: Implement actual Google Drive API call
        # For now, we'll rely on manual downloads to DOWNLOADS_DIR
        
        return []
    
    def scan_local_incoming(self) -> List[Path]:
        """Scan local incoming directory for new transcripts."""
        new_files = []
        
        for file_path in DOWNLOADS_DIR.glob("*.docx"):
            file_id = hashlib.md5(file_path.name.encode()).hexdigest()
            if file_id not in self.processed_ids:
                new_files.append(file_path)
        
        for file_path in DOWNLOADS_DIR.glob("*.txt"):
            file_id = hashlib.md5(file_path.name.encode()).hexdigest()
            if file_id not in self.processed_ids:
                new_files.append(file_path)
        
        return new_files
    
    def create_processing_request(self, transcript_path: Path) -> Path:
        """Create a processing request file for Zo to handle."""
        file_id = hashlib.md5(transcript_path.name.encode()).hexdigest()
        meeting_info = self._extract_meeting_info(transcript_path.name)
        
        request = {
            "request_id": file_id,
            "transcript_path": str(transcript_path),
            "transcript_name": transcript_path.name,
            "meeting_info": meeting_info,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": None
        }
        
        request_file = REQUESTS_DIR / f"{file_id}.json"
        request_file.write_text(json.dumps(request, indent=2))
        
        logger.info(f"Created processing request: {request_file}")
        return request_file
    
    async def run(self):
        """Main execution: scan for new transcripts and create requests."""
        logger.info("Starting transcript watcher...")
        
        # Scan local incoming directory
        new_files = self.scan_local_incoming()
        
        if not new_files:
            logger.info("No new transcripts found")
            return
        
        logger.info(f"Found {len(new_files)} new transcript(s)")
        
        for file_path in new_files:
            logger.info(f"Creating request for: {file_path.name}")
            self.create_processing_request(file_path)
            
            # Mark as seen (but not processed yet)
            file_id = hashlib.md5(file_path.name.encode()).hexdigest()
            self.processed_ids.add(file_id)
        
        self._save_state()
        logger.info("Watcher complete")


async def main():
    """Main entry point."""
    watcher = TranscriptWatcher()
    await watcher.run()


if __name__ == "__main__":
    asyncio.run(main())
