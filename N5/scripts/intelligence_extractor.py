#!/usr/bin/env python3
"""
Intelligence Extractor - Extract insights from documents and media.
Creates human-readable intelligence files in markdown format.
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/documents_media.db")
INTELLIGENCE_DIR = Path("/home/workspace/Knowledge/intelligence")


def ensure_intelligence_dir():
    """Ensure intelligence output directory exists."""
    INTELLIGENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (INTELLIGENCE_DIR / "documents").mkdir(exist_ok=True)
    (INTELLIGENCE_DIR / "media").mkdir(exist_ok=True)
    (INTELLIGENCE_DIR / "extracts").mkdir(exist_ok=True)


def read_document_content(filepath: Path) -> Optional[str]:
    """Read document content. Returns text content or None."""
    try:
        if filepath.suffix.lower() == '.md':
            return filepath.read_text(encoding='utf-8')
        elif filepath.suffix.lower() == '.txt':
            return filepath.read_text(encoding='utf-8')
        elif filepath.suffix.lower() == '.json':
            # Return formatted JSON
            data = json.loads(filepath.read_text())
            return json.dumps(data, indent=2)
        else:
            # For other types, return metadata only
            return None
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        return None


def read_transcript(transcript_path: Path) -> Optional[Dict]:
    """Read transcript JSONL file."""
    try:
        with open(transcript_path, 'r') as f:
            data = json.loads(f.readline())
            return data
    except Exception as e:
        logging.error(f"Error reading transcript {transcript_path}: {e}")
        return None


def extract_document_intelligence(doc_id: str, filepath: Path, file_type: str, dry_run: bool = False) -> Optional[str]:
    """
    Extract intelligence from document.
    Returns intelligence file path or None.
    """
    try:
        # Read content
        content = read_document_content(filepath)
        
        # Generate intelligence file
        intelligence_file = INTELLIGENCE_DIR / "documents" / f"{doc_id}_intelligence.md"
        
        # Create intelligence summary
        intelligence = f"""---
source_id: {doc_id}
source_type: document
source_file: {filepath}
extract_date: {datetime.now().isoformat()}
extract_type: document_intelligence
---

# Document Intelligence: {filepath.name}

## Metadata
- **File Type:** {file_type}
- **Source:** `file '{filepath}'`
- **Extracted:** {datetime.now().strftime('%Y-%m-%d')}

## Content Summary
"""
        
        if content:
            # Count key metrics
            lines = content.split('\n')
            words = len(content.split())
            
            intelligence += f"""
- **Lines:** {len(lines)}
- **Words:** {words}
- **Characters:** {len(content)}

## Key Sections
"""
            
            # Extract headers for markdown
            if file_type == 'markdown':
                headers = [line for line in lines if line.startswith('#')]
                if headers:
                    intelligence += "\n".join(f"- {h.strip()}" for h in headers[:10])
                else:
                    intelligence += "No headers found\n"
            else:
                # Show first 5 non-empty lines
                preview_lines = [line for line in lines[:20] if line.strip()][:5]
                intelligence += "\n```\n"
                intelligence += "\n".join(preview_lines)
                intelligence += "\n```\n"
        else:
            intelligence += "\n*Binary or unsupported format - metadata only*\n"
        
        intelligence += f"""

## Processing Notes
- Extraction method: Content analysis
- Intelligence quality: Automated
- Review status: Pending

## Next Steps
- [ ] Manual review required
- [ ] Extract key insights
- [ ] Add tags
- [ ] Link to related content
"""
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would create intelligence file: {intelligence_file}")
            return str(intelligence_file)
        
        # Write intelligence file
        intelligence_file.write_text(intelligence, encoding='utf-8')
        logging.info(f"✓ Created intelligence file: {intelligence_file.name}")
        
        return str(intelligence_file)
        
    except Exception as e:
        logging.error(f"Error extracting intelligence from {filepath}: {e}", exc_info=True)
        return None


def extract_media_intelligence(media_id: str, filepath: Path, media_type: str, transcript_path: Optional[str], dry_run: bool = False) -> Optional[str]:
    """
    Extract intelligence from media file.
    Returns intelligence file path or None.
    """
    try:
        intelligence_file = INTELLIGENCE_DIR / "media" / f"{media_id}_intelligence.md"
        
        # Base intelligence
        intelligence = f"""---
source_id: {media_id}
source_type: media
source_file: {filepath}
extract_date: {datetime.now().isoformat()}
extract_type: media_intelligence
---

# Media Intelligence: {filepath.name}

## Metadata
- **Media Type:** {media_type}
- **Source:** `file '{filepath}'`
- **Extracted:** {datetime.now().strftime('%Y-%m-%d')}

"""
        
        # Process transcript if available
        if transcript_path and Path(transcript_path).exists():
            transcript_data = read_transcript(Path(transcript_path))
            
            if transcript_data:
                text = transcript_data.get('text', '')
                words = len(text.split())
                
                intelligence += f"""## Transcript Summary
- **Transcript:** Available
- **Words:** {words}
- **Characters:** {len(text)}

## Transcript Preview
```
{text[:500]}...
```

"""
                
                # Check for utterances (speaker data)
                if 'utterances' in transcript_data:
                    utterances = transcript_data['utterances']
                    speakers = set(u.get('speaker', 'Unknown') for u in utterances)
                    intelligence += f"""## Speakers
- **Count:** {len(speakers)}
- **Identified:** {', '.join(sorted(speakers))}

"""
            else:
                intelligence += "## Transcript\n- Status: File exists but could not be parsed\n\n"
        else:
            intelligence += "## Transcript\n- Status: Not available\n- Action: Consider transcribing this media\n\n"
        
        intelligence += f"""## Processing Notes
- Extraction method: Transcript analysis
- Intelligence quality: Automated
- Review status: Pending

## Next Steps
- [ ] Manual review required
- [ ] Extract key insights
- [ ] Identify action items
- [ ] Add tags
- [ ] Link to related content
"""
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would create intelligence file: {intelligence_file}")
            return str(intelligence_file)
        
        # Write intelligence file
        intelligence_file.write_text(intelligence, encoding='utf-8')
        logging.info(f"✓ Created intelligence file: {intelligence_file.name}")
        
        return str(intelligence_file)
        
    except Exception as e:
        logging.error(f"Error extracting intelligence from {filepath}: {e}", exc_info=True)
        return None


def record_intelligence_extract(conn: sqlite3.Connection, source_id: str, source_type: str, extract_path: str, extract_type: str):
    """Record intelligence extract in database."""
    cursor = conn.cursor()
    
    extract_id = f"{source_id}_{extract_type}_{datetime.now().strftime('%Y%m%d')}"
    
    cursor.execute("""
        INSERT OR REPLACE INTO intelligence_extracts (
            id, source_id, source_type, extracted_date,
            extract_type, knowledge_path, content
        ) VALUES (?, ?, ?, ?, ?, ?, '')
    """, (
        extract_id,
        source_id,
        source_type,
        datetime.now().isoformat(),
        extract_type,
        extract_path
    ))
    conn.commit()


def update_processing_status(conn: sqlite3.Connection, item_id: str, item_type: str, status: str):
    """Update processing status for document or media."""
    cursor = conn.cursor()
    table = 'documents' if item_type == 'document' else 'media'
    cursor.execute(f"UPDATE {table} SET processing_status = ? WHERE id = ?", (status, item_id))
    conn.commit()


def process_pending_documents(conn: sqlite3.Connection, dry_run: bool = False) -> int:
    """Process all pending documents."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filepath, file_type 
        FROM documents 
        WHERE processing_status = 'pending'
    """)
    
    pending = cursor.fetchall()
    logging.info(f"Found {len(pending)} pending documents")
    
    processed = 0
    for doc_id, filepath, file_type in pending:
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            logging.warning(f"File not found: {filepath}")
            update_processing_status(conn, doc_id, 'document', 'error')
            continue
        
        # Extract intelligence
        intel_path = extract_document_intelligence(doc_id, filepath_obj, file_type, dry_run)
        
        if intel_path:
            if not dry_run:
                record_intelligence_extract(conn, doc_id, 'document', intel_path, 'document_intelligence')
                update_processing_status(conn, doc_id, 'document', 'processed')
            processed += 1
    
    return processed


def process_pending_media(conn: sqlite3.Connection, dry_run: bool = False) -> int:
    """Process all pending media files."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filepath, media_type, transcript_path
        FROM media 
        WHERE processing_status = 'pending'
    """)
    
    pending = cursor.fetchall()
    logging.info(f"Found {len(pending)} pending media files")
    
    processed = 0
    for media_id, filepath, media_type, transcript_path in pending:
        filepath_obj = Path(filepath)
        if not filepath_obj.exists():
            logging.warning(f"File not found: {filepath}")
            update_processing_status(conn, media_id, 'media', 'error')
            continue
        
        # Extract intelligence
        intel_path = extract_media_intelligence(media_id, filepath_obj, media_type, transcript_path, dry_run)
        
        if intel_path:
            if not dry_run:
                record_intelligence_extract(conn, media_id, 'media', intel_path, 'media_intelligence')
                update_processing_status(conn, media_id, 'media', 'processed')
            processed += 1
    
    return processed


def main(dry_run: bool = False) -> int:
    """Main extraction function."""
    try:
        # Ensure output directory
        ensure_intelligence_dir()
        
        # Connect to database
        if not DB_PATH.exists():
            logging.error(f"Database not found: {DB_PATH}")
            return 1
        
        conn = sqlite3.connect(DB_PATH)
        
        # Process pending items
        docs_processed = process_pending_documents(conn, dry_run)
        media_processed = process_pending_media(conn, dry_run)
        
        conn.close()
        
        logging.info("")
        logging.info("=== Intelligence Extraction Complete ===")
        logging.info(f"Documents processed: {docs_processed}")
        logging.info(f"Media processed: {media_processed}")
        logging.info(f"Total: {docs_processed + media_processed}")
        logging.info(f"Intelligence files: {INTELLIGENCE_DIR}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract intelligence from documents and media"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(dry_run=args.dry_run))
