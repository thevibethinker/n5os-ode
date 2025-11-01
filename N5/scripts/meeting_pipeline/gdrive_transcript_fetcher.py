#!/usr/bin/env python3
"""
Google Drive Transcript Fetcher
Fetches unprocessed transcripts from Google Drive, converts to markdown, 
and marks processed in Drive.
"""
import argparse, json, logging, sys, subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
INBOX_DIR = WORKSPACE_ROOT / "Personal/Meetings/Inbox"
STAGING_DIR = WORKSPACE_ROOT / "N5/data/meeting_pipeline/staging"
GDRIVE_FOLDER_ID = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"

# Supported formats (priority order)
SUPPORTED_MIMETYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",  # Fireflies
    "application/vnd.google-apps.document": ".gdoc",  # Granola
    "text/plain": ".txt",  # Plaud Notes
}

def ensure_dirs():
    """Ensure required directories exist"""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

def list_unprocessed_transcripts():
    """List transcripts without [ZO-PROCESSED] prefix from Google Drive"""
    try:
        result = subprocess.run([
            "python3", "-c",
            """
import sys, json
sys.path.append('/home/workspace/N5/scripts')
from pipedream_helper import call_google_drive_tool

result = call_google_drive_tool(
    'google_drive-list-files',
    {'folderId': '""" + GDRIVE_FOLDER_ID + """', 'trashed': False}
)
print(json.dumps(result))
"""
        ], capture_output=True, text=True, check=True)
        
        files_data = json.loads(result.stdout)
        files = files_data.get('ret', [])
        
        # Filter unprocessed files with supported formats
        unprocessed = []
        for f in files:
            name = f.get('name', '')
            mimetype = f.get('mimeType', '')
            
            if name.startswith('[ZO-PROCESSED]'):
                continue
            if mimetype not in SUPPORTED_MIMETYPES:
                continue
            
            # Check if it looks like a transcript
            if 'transcript' in name.lower() or mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                unprocessed.append(f)
        
        return unprocessed
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return []

def download_file(file_id, filename, mimetype):
    """Download file from Google Drive"""
    staging_path = STAGING_DIR / filename
    
    try:
        if mimetype == "application/vnd.google-apps.document":
            # Export Google Doc as .docx
            subprocess.run([
                "python3", "-c",
                """
import sys
sys.path.append('/home/workspace/N5/scripts')
from pipedream_helper import call_google_drive_tool

result = call_google_drive_tool(
    'google_drive-download-file',
    {
        'fileId': '""" + file_id + """',
        'filePath': '""" + str(staging_path.with_suffix('.docx')) + """',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
)
"""
            ], check=True)
            return staging_path.with_suffix('.docx')
        else:
            # Download as-is
            subprocess.run([
                "python3", "-c",
                """
import sys
sys.path.append('/home/workspace/N5/scripts')
from pipedream_helper import call_google_drive_tool

result = call_google_drive_tool(
    'google_drive-download-file',
    {'fileId': '""" + file_id + """', 'filePath': '""" + str(staging_path) + """'}
)
"""
            ], check=True)
            return staging_path
    except Exception as e:
        logger.error(f"Failed to download {filename}: {e}")
        return None

def convert_to_markdown(file_path):
    """Convert document to markdown"""
    md_path = file_path.with_suffix('.transcript.md')
    
    try:
        if file_path.suffix == '.docx':
            # Use pandoc for .docx → .md
            subprocess.run([
                'pandoc',
                str(file_path),
                '-t', 'markdown',
                '-o', str(md_path)
            ], check=True)
        elif file_path.suffix == '.txt':
            # Copy .txt as-is to .md
            md_path.write_text(file_path.read_text())
        else:
            logger.warning(f"Unsupported format: {file_path.suffix}")
            return None
        
        return md_path
    except Exception as e:
        logger.error(f"Failed to convert {file_path}: {e}")
        return None

def move_to_inbox(md_path, original_name):
    """Move converted file to inbox"""
    # Generate temporary name (will be renamed by block selector)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    temp_name = f"temp_{timestamp}_{md_path.name}"
    inbox_path = INBOX_DIR / temp_name
    
    try:
        md_path.rename(inbox_path)
        logger.info(f"  → Moved to inbox: {temp_name}")
        return inbox_path
    except Exception as e:
        logger.error(f"Failed to move to inbox: {e}")
        return None

def mark_processed_in_drive(file_id, filename):
    """Rename file in Google Drive with [ZO-PROCESSED] prefix"""
    new_name = f"[ZO-PROCESSED] {filename}"
    
    try:
        subprocess.run([
            "python3", "-c",
            """
import sys
sys.path.append('/home/workspace/N5/scripts')
from pipedream_helper import call_google_drive_tool

result = call_google_drive_tool(
    'google_drive-update-file',
    {
        'fileId': '""" + file_id + """',
        'name': '""" + new_name.replace('"', '\"') + """'
    }
)
"""
        ], check=True)
        logger.info(f"  ✓ Marked in Drive: {new_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to mark processed: {e}")
        return False

def main(dry_run=False):
    """Main execution"""
    logger.info("Google Drive Transcript Fetcher")
    
    try:
        ensure_dirs()
        
        # List unprocessed transcripts
        unprocessed = list_unprocessed_transcripts()
        logger.info(f"Found {len(unprocessed)} unprocessed transcripts")
        
        if not unprocessed:
            logger.info("No new transcripts to process")
            return 0
        
        processed_count = 0
        for file_info in unprocessed:
            file_id = file_info['id']
            filename = file_info['name']
            mimetype = file_info['mimeType']
            
            logger.info(f"Processing: {filename}")
            
            if dry_run:
                logger.info("  [DRY-RUN] Would download, convert, and mark processed")
                continue
            
            # Download
            downloaded = download_file(file_id, filename, mimetype)
            if not downloaded:
                continue
            
            # Convert to markdown
            md_file = convert_to_markdown(downloaded)
            if not md_file:
                continue
            
            # Move to inbox
            inbox_file = move_to_inbox(md_file, filename)
            if not inbox_file:
                continue
            
            # Mark processed in Drive
            if mark_processed_in_drive(file_id, filename):
                processed_count += 1
            
            # Cleanup staging
            if downloaded.exists():
                downloaded.unlink()
        
        logger.info(f"✓ Processed {processed_count}/{len(unprocessed)} transcripts")
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run))
