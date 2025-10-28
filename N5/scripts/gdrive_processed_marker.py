#!/usr/bin/env python3
"""
Google Drive Processed Marker
Marks successfully-processed meeting transcripts on Google Drive with [ZO-PROCESSED] prefix.

NOTE: This script only identifies candidates. The actual renaming is done by the scheduled agent
which has access to use_app_google_drive tool.
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")

def load_google_drive_tool():
    """Import and return use_app_google_drive function."""
    # This will be called by the agent with access to the tool
    pass

def get_processed_meetings_needing_marking():
    """Find meetings that have been processed but whose Drive files aren't marked.
    
    NOTE: Returns candidate list. Agent must verify actual Drive filename via API
    before attempting to rename (file may already be marked).
    """
    needs_marking = []
    
    for meeting_dir in MEETINGS_DIR.iterdir():
        if not meeting_dir.is_dir() or meeting_dir.name.startswith('.'):
            continue
            
        metadata_file = meeting_dir / "_metadata.json"
        if not metadata_file.exists():
            continue
            
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            # Check if this meeting came from Google Drive and has a gdrive_id
            gdrive_id = metadata.get("gdrive_id")
            original_filename = metadata.get("original_filename", "")
            
            if not gdrive_id:
                continue
                
            # Check if already marked
            if original_filename.startswith("[ZO-PROCESSED]"):
                continue
                
            # Check if processing is complete (has blocks_count > 0)
            blocks_count = metadata.get("blocks_count", 0)
            if blocks_count == 0:
                continue
                
            needs_marking.append({
                "meeting_id": metadata.get("meeting_id"),
                "gdrive_id": gdrive_id,
                "original_filename": original_filename,
                "meeting_dir": str(meeting_dir)
            })
                
        except Exception as e:
            logger.warning(f"Could not read metadata for {meeting_dir.name}: {e}")
            continue
    
    return needs_marking

def main():
    """Find processed meetings and return list for agent to mark."""
    try:
        meetings = get_processed_meetings_needing_marking()
        
        if not meetings:
            logger.info("✓ No meetings need marking on Google Drive (based on local metadata)")
            return 0
        
        logger.info(f"Found {len(meetings)} meetings that MAY need [ZO-PROCESSED] marking:")
        logger.info("NOTE: Agent must verify actual Drive filename before renaming")
        for m in meetings:
            logger.info(f"  - {m['meeting_id']} (gdrive_id: {m['gdrive_id']})")
        
        # Output JSON for agent to consume
        output = {
            "meetings_to_mark": meetings,
            "count": len(meetings),
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "note": "Agent must check actual Drive filename before renaming (may already be marked)"
        }
        
        output_file = Path("/tmp/gdrive_marking_needed.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"✓ Output written to {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
