#!/usr/bin/env python3
"""
Media Ingest Script for Content Library
Ingests a single media file (audio/video/image) into the Content Library.

Part of Content Library Media Extension build (Worker 2)

Usage:
    python3 media_ingest.py <file_path> [--move] [--dry-run] [--title "Custom Title"]
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/content_library.db")
CONTENT_LIBRARY_ROOT = Path("/home/workspace/Knowledge/content-library")

# Media type mappings
AUDIO_EXTENSIONS = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".wma"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".wmv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg"}

MIME_TYPE_MAP = {
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".aac": "audio/aac",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def get_content_type(file_path: Path) -> str:
    """Determine content type from file extension."""
    ext = file_path.suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return "audio"
    elif ext in VIDEO_EXTENSIONS:
        return "video"
    elif ext in IMAGE_EXTENSIONS:
        return "image"
    else:
        return "unknown"


def get_mime_type(file_path: Path) -> str:
    """Get MIME type from file extension."""
    ext = file_path.suffix.lower()
    return MIME_TYPE_MAP.get(ext, "application/octet-stream")


def extract_media_metadata(file_path: Path) -> dict:
    """Extract metadata using ffprobe."""
    metadata = {
        "duration_seconds": None,
        "dimensions": None,
        "format": None,
        "bitrate": None,
    }
    
    try:
        # Get format info (duration, format name)
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration,format_name,bit_rate",
                "-of", "json",
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            fmt = data.get("format", {})
            if "duration" in fmt:
                metadata["duration_seconds"] = int(float(fmt["duration"]))
            metadata["format"] = fmt.get("format_name")
            metadata["bitrate"] = fmt.get("bit_rate")
        
        # Get video stream info (dimensions)
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "json",
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            if streams:
                width = streams[0].get("width")
                height = streams[0].get("height")
                if width and height:
                    metadata["dimensions"] = f"{width}x{height}"
    
    except subprocess.TimeoutExpired:
        logger.warning(f"ffprobe timed out for {file_path}")
    except Exception as e:
        logger.warning(f"Failed to extract metadata: {e}")
    
    return metadata


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def find_transcript(file_path: Path) -> Path | None:
    """Check for existing transcript file."""
    transcript_path = Path(str(file_path) + ".transcript.jsonl")
    if transcript_path.exists():
        return transcript_path
    return None


def read_transcript_text(transcript_path: Path) -> str | None:
    """Read transcript text from .transcript.jsonl file."""
    try:
        with open(transcript_path, "r") as f:
            data = json.loads(f.readline())
            return data.get("text", "")
    except Exception as e:
        logger.warning(f"Failed to read transcript: {e}")
        return None


def slugify(text: str) -> str:
    """Convert text to a clean slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def generate_canonical_filename(file_path: Path, title: str | None = None) -> str:
    """Generate a canonical filename for storage."""
    ext = file_path.suffix.lower()
    if title:
        base = slugify(title)[:50]
    else:
        base = slugify(file_path.stem)[:50]
    
    # Add short UUID to prevent collisions
    short_id = uuid.uuid4().hex[:8]
    return f"{base}-{short_id}{ext}"


def check_already_ingested(source_path: str, file_hash: str) -> bool:
    """Check if file is already in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM items WHERE source_file_path = ? OR media_metadata LIKE ?",
        (source_path, f'%"checksum": "{file_hash}"%')
    )
    result = cursor.fetchone()
    conn.close()
    
    return result is not None


def ingest_media(
    file_path: Path,
    title: str | None = None,
    move: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Ingest a media file into the Content Library.
    
    Returns dict with status and details.
    """
    file_path = file_path.resolve()
    
    if not file_path.exists():
        return {"status": "error", "message": f"File not found: {file_path}"}
    
    content_type = get_content_type(file_path)
    if content_type == "unknown":
        return {"status": "error", "message": f"Unsupported file type: {file_path.suffix}"}
    
    # Compute hash for deduplication
    file_hash = compute_file_hash(file_path)
    
    # Check if already ingested
    if check_already_ingested(str(file_path), file_hash):
        return {"status": "skipped", "message": "File already in Content Library"}
    
    # Extract metadata
    metadata = extract_media_metadata(file_path)
    mime_type = get_mime_type(file_path)
    
    # Check for transcript
    transcript_source = find_transcript(file_path)
    transcript_text = None
    transcript_dest = None
    tags = []
    
    if transcript_source:
        transcript_text = read_transcript_text(transcript_source)
        tags.append("transcribed")
    else:
        tags.append("needs-transcription")
    
    # Generate title if not provided
    if not title:
        title = file_path.stem.replace("-", " ").replace("_", " ").title()
    
    # Determine canonical destination
    dest_dir = CONTENT_LIBRARY_ROOT / content_type
    canonical_filename = generate_canonical_filename(file_path, title)
    dest_path = dest_dir / canonical_filename
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would ingest: {file_path}")
        logger.info(f"[DRY-RUN] Destination: {dest_path}")
        logger.info(f"[DRY-RUN] Content type: {content_type}")
        logger.info(f"[DRY-RUN] Metadata: {metadata}")
        return {
            "status": "dry-run",
            "source": str(file_path),
            "destination": str(dest_path),
            "content_type": content_type,
            "metadata": metadata
        }
    
    # Copy or move file
    dest_dir.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(file_path), str(dest_path))
        logger.info(f"Moved {file_path} -> {dest_path}")
    else:
        shutil.copy2(str(file_path), str(dest_path))
        logger.info(f"Copied {file_path} -> {dest_path}")
    
    # Handle transcript
    if transcript_source:
        transcript_dest = CONTENT_LIBRARY_ROOT / "transcripts" / (canonical_filename + ".transcript.jsonl")
        if move:
            shutil.move(str(transcript_source), str(transcript_dest))
        else:
            shutil.copy2(str(transcript_source), str(transcript_dest))
        logger.info(f"Transcript: {transcript_dest}")
    
    # Prepare media_metadata JSON
    media_meta = {
        "checksum": file_hash,
        "original_filename": file_path.name,
        "format": metadata.get("format"),
        "bitrate": metadata.get("bitrate"),
        "ingested_at": datetime.now().isoformat(),
    }
    
    # Insert into database
    item_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO items (
            id, title, content_type, content, source_file_path, tags,
            created_at, updated_at, ingested_at, has_content,
            file_path, mime_type, duration_seconds, dimensions,
            transcript_path, media_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_id,
        title,
        content_type,
        transcript_text[:5000] if transcript_text else None,  # Store snippet
        str(file_path),
        json.dumps(tags),
        now,
        now,
        now,
        1 if transcript_text else 0,
        str(dest_path),
        mime_type,
        metadata.get("duration_seconds"),
        metadata.get("dimensions"),
        str(transcript_dest) if transcript_dest else None,
        json.dumps(media_meta)
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✓ Ingested: {title} (id: {item_id})")
    
    return {
        "status": "success",
        "id": item_id,
        "title": title,
        "content_type": content_type,
        "file_path": str(dest_path),
        "duration_seconds": metadata.get("duration_seconds"),
        "has_transcript": transcript_text is not None
    }


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a media file into the Content Library"
    )
    parser.add_argument("file_path", type=Path, help="Path to media file")
    parser.add_argument("--title", type=str, help="Custom title for the item")
    parser.add_argument("--move", action="store_true", help="Move file instead of copying")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    result = ingest_media(
        file_path=args.file_path,
        title=args.title,
        move=args.move,
        dry_run=args.dry_run
    )
    
    print(json.dumps(result, indent=2))
    
    if result["status"] == "error":
        exit(1)
    elif result["status"] == "skipped":
        exit(0)
    else:
        exit(0)


if __name__ == "__main__":
    main()

