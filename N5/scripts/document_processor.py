#!/usr/bin/env python3
"""
Document & Media Processor - Core processing pipeline for intelligence extraction.
Handles ingestion, deduplication, metadata extraction, and processing orchestration.
"""

import argparse
import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/documents_media.db")

# Watched directories for auto-scanning
WATCHED_DIRS = [
    Path("/home/workspace/Articles"),
    Path("/home/workspace/Documents"),
    Path("/home/workspace/Personal/Meetings"),
    Path("/home/workspace/Records"),
    Path("/home/workspace/Reports"),
]

# Document type mappings
DOCUMENT_TYPES = {
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.doc': 'doc',
    '.xlsx': 'xlsx',
    '.xls': 'xls',
    '.md': 'markdown',
    '.txt': 'text',
    '.csv': 'csv',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
}

MEDIA_TYPES = {
    '.mp3': ('audio', 'mp3'),
    '.m4a': ('audio', 'm4a'),
    '.wav': ('audio', 'wav'),
    '.mp4': ('video', 'mp4'),
    '.mov': ('video', 'mov'),
    '.avi': ('video', 'avi'),
}


def compute_checksum(filepath: Path) -> str:
    """Compute SHA256 checksum for file deduplication."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def generate_id(filepath: Path, created_date: str) -> str:
    """Generate unique ID for document/media based on path and creation date."""
    content = f"{filepath}{created_date}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def is_document(filepath: Path) -> bool:
    """Check if file is a trackable document."""
    return filepath.suffix.lower() in DOCUMENT_TYPES


def is_media(filepath: Path) -> bool:
    """Check if file is trackable media."""
    return filepath.suffix.lower() in MEDIA_TYPES


def extract_document_metadata(filepath: Path) -> Dict:
    """Extract metadata from document file."""
    try:
        stat = filepath.stat()
        file_type = DOCUMENT_TYPES.get(filepath.suffix.lower(), 'unknown')
        
        created_date = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        return {
            'filepath': str(filepath.absolute()),
            'filename': filepath.name,
            'file_type': file_type,
            'size_bytes': stat.st_size,
            'created_date': created_date,
            'modified_date': modified_date,
            'ingestion_date': datetime.now().isoformat(),
        }
    except Exception as e:
        logging.error(f"Error extracting metadata from {filepath}: {e}")
        return None


def extract_media_metadata(filepath: Path) -> Dict:
    """Extract metadata from media file."""
    try:
        stat = filepath.stat()
        media_type, format_type = MEDIA_TYPES.get(filepath.suffix.lower(), ('unknown', 'unknown'))
        
        created_date = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Check for existing transcript
        transcript_path = None
        transcript_status = 'none'
        potential_transcript = Path(str(filepath) + '.transcript.jsonl')
        if potential_transcript.exists():
            transcript_path = str(potential_transcript.absolute())
            transcript_status = 'complete'
        
        return {
            'filepath': str(filepath.absolute()),
            'filename': filepath.name,
            'media_type': media_type,
            'format': format_type,
            'size_bytes': stat.st_size,
            'created_date': created_date,
            'modified_date': modified_date,
            'ingestion_date': datetime.now().isoformat(),
            'transcript_path': transcript_path,
            'transcript_status': transcript_status,
        }
    except Exception as e:
        logging.error(f"Error extracting metadata from {filepath}: {e}")
        return None


def check_duplicate(conn: sqlite3.Connection, checksum: str, table: str) -> Optional[str]:
    """Check if file with same checksum already exists. Returns existing filepath if found."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT filepath FROM {table} WHERE checksum = ?", (checksum,))
    result = cursor.fetchone()
    return result[0] if result else None


def ingest_document(conn: sqlite3.Connection, filepath: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Ingest a document into the registry.
    Returns (success, message)
    """
    try:
        # Extract metadata
        metadata = extract_document_metadata(filepath)
        if not metadata:
            return False, f"Failed to extract metadata from {filepath}"
        
        # Compute checksum
        checksum = compute_checksum(filepath)
        
        # Check for duplicate
        existing = check_duplicate(conn, checksum, 'documents')
        if existing:
            if existing == metadata['filepath']:
                return True, f"Document already ingested: {filepath.name}"
            else:
                return True, f"Duplicate of existing document: {existing}"
        
        # Generate ID
        doc_id = generate_id(filepath, metadata['created_date'])
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would ingest document: {filepath.name} (ID: {doc_id})")
            return True, f"[DRY-RUN] Would ingest: {filepath.name}"
        
        # Insert into database
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (
                id, filepath, filename, file_type, size_bytes,
                created_date, modified_date, ingestion_date,
                checksum, processing_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            doc_id,
            metadata['filepath'],
            metadata['filename'],
            metadata['file_type'],
            metadata['size_bytes'],
            metadata['created_date'],
            metadata['modified_date'],
            metadata['ingestion_date'],
            checksum
        ))
        conn.commit()
        
        logging.info(f"✓ Ingested document: {filepath.name} (ID: {doc_id})")
        return True, f"Ingested: {filepath.name}"
        
    except Exception as e:
        logging.error(f"Error ingesting document {filepath}: {e}", exc_info=True)
        return False, f"Error: {str(e)}"


def ingest_media(conn: sqlite3.Connection, filepath: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """
    Ingest a media file into the registry.
    Returns (success, message)
    """
    try:
        # Extract metadata
        metadata = extract_media_metadata(filepath)
        if not metadata:
            return False, f"Failed to extract metadata from {filepath}"
        
        # Compute checksum
        checksum = compute_checksum(filepath)
        
        # Check for duplicate
        existing = check_duplicate(conn, checksum, 'media')
        if existing:
            if existing == metadata['filepath']:
                return True, f"Media already ingested: {filepath.name}"
            else:
                return True, f"Duplicate of existing media: {existing}"
        
        # Generate ID
        media_id = generate_id(filepath, metadata['created_date'])
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would ingest media: {filepath.name} (ID: {media_id})")
            return True, f"[DRY-RUN] Would ingest: {filepath.name}"
        
        # Insert into database
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO media (
                id, filepath, filename, media_type, format, size_bytes,
                created_date, modified_date, ingestion_date,
                transcript_path, transcript_status, checksum, processing_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            media_id,
            metadata['filepath'],
            metadata['filename'],
            metadata['media_type'],
            metadata['format'],
            metadata['size_bytes'],
            metadata['created_date'],
            metadata['modified_date'],
            metadata['ingestion_date'],
            metadata['transcript_path'],
            metadata['transcript_status'],
            checksum
        ))
        conn.commit()
        
        logging.info(f"✓ Ingested media: {filepath.name} (ID: {media_id})")
        return True, f"Ingested: {filepath.name}"
        
    except Exception as e:
        logging.error(f"Error ingesting media {filepath}: {e}", exc_info=True)
        return False, f"Error: {str(e)}"


def scan_directory(directory: Path, recursive: bool = True) -> Tuple[List[Path], List[Path]]:
    """
    Scan directory for documents and media files.
    Returns (documents, media)
    """
    documents = []
    media_files = []
    
    try:
        pattern = "**/*" if recursive else "*"
        for filepath in directory.glob(pattern):
            if not filepath.is_file():
                continue
            
            # Skip hidden files and system files
            if filepath.name.startswith('.'):
                continue
            
            # Skip transcript files (handled with media)
            if '.transcript.jsonl' in filepath.name:
                continue
            
            if is_document(filepath):
                documents.append(filepath)
            elif is_media(filepath):
                media_files.append(filepath)
        
        return documents, media_files
        
    except Exception as e:
        logging.error(f"Error scanning directory {directory}: {e}")
        return [], []


def main(
    scan: bool = False,
    file_path: Optional[str] = None,
    directory: Optional[str] = None,
    dry_run: bool = False
) -> int:
    """Main processing function."""
    try:
        # Connect to database
        if not DB_PATH.exists():
            logging.error(f"Database not found: {DB_PATH}")
            logging.error("Run documents_media_db_init.py first")
            return 1
        
        conn = sqlite3.connect(DB_PATH)
        
        total_docs = 0
        total_media = 0
        success_docs = 0
        success_media = 0
        
        # Process single file
        if file_path:
            filepath = Path(file_path).absolute()
            if not filepath.exists():
                logging.error(f"File not found: {filepath}")
                return 1
            
            if is_document(filepath):
                success, msg = ingest_document(conn, filepath, dry_run)
                total_docs += 1
                if success:
                    success_docs += 1
                logging.info(msg)
            elif is_media(filepath):
                success, msg = ingest_media(conn, filepath, dry_run)
                total_media += 1
                if success:
                    success_media += 1
                logging.info(msg)
            else:
                logging.error(f"Unsupported file type: {filepath.suffix}")
                return 1
        
        # Scan directory
        elif directory:
            dir_path = Path(directory).absolute()
            if not dir_path.exists():
                logging.error(f"Directory not found: {dir_path}")
                return 1
            
            logging.info(f"Scanning directory: {dir_path}")
            documents, media_files = scan_directory(dir_path)
            
            logging.info(f"Found {len(documents)} documents, {len(media_files)} media files")
            
            for doc in documents:
                success, msg = ingest_document(conn, doc, dry_run)
                total_docs += 1
                if success:
                    success_docs += 1
            
            for media in media_files:
                success, msg = ingest_media(conn, media, dry_run)
                total_media += 1
                if success:
                    success_media += 1
        
        # Auto-scan watched directories
        elif scan:
            logging.info("Auto-scanning watched directories...")
            all_documents = []
            all_media = []
            
            for watch_dir in WATCHED_DIRS:
                if not watch_dir.exists():
                    logging.warning(f"Watched directory does not exist: {watch_dir}")
                    continue
                
                logging.info(f"Scanning: {watch_dir}")
                documents, media_files = scan_directory(watch_dir)
                all_documents.extend(documents)
                all_media.extend(media_files)
            
            logging.info(f"Found {len(all_documents)} documents, {len(all_media)} media files across all directories")
            
            for doc in all_documents:
                success, msg = ingest_document(conn, doc, dry_run)
                total_docs += 1
                if success:
                    success_docs += 1
            
            for media in all_media:
                success, msg = ingest_media(conn, media, dry_run)
                total_media += 1
                if success:
                    success_media += 1
        
        else:
            logging.error("Must specify --scan, --file, or --directory")
            return 1
        
        # Report results
        conn.close()
        
        logging.info(f"")
        logging.info(f"=== Processing Complete ===")
        logging.info(f"Documents: {success_docs}/{total_docs} ingested")
        logging.info(f"Media: {success_media}/{total_media} ingested")
        logging.info(f"Total: {success_docs + success_media}/{total_docs + total_media}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error in main: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process documents and media for intelligence extraction"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Auto-scan watched directories"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Process single file"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Scan specific directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    exit(main(
        scan=args.scan,
        file_path=args.file,
        directory=args.directory,
        dry_run=args.dry_run
    ))
