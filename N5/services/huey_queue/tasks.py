#!/usr/bin/env python3
"""
Huey tasks for meeting transcript ingestion pipeline

Based on manual process executed 2025-11-04 (Architect's platonic ideal)
"""
import hashlib
import logging
import re
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .config import huey

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(message)s')
logger = logging.getLogger(__name__)

# Directory constants
STAGING = Path("/home/workspace/N5/data/staging/meetings")
INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
IMPORT_LOG = Path("/home/workspace/N5/logs/meeting_import.jsonl")


def normalize_title(filename: str) -> str:
    """Normalize filename to base title for duplicate detection"""
    # Remove extension
    name = filename.replace(".docx", "").replace(".transcript.md", "")
    # Remove [ZO-PROCESSED] prefix
    name = re.sub(r'^\[ZO-PROCESSED\]\s*', '', name)
    # Extract title (everything before -transcript-)
    match = re.search(r'(.+?)-transcript-', name)
    if match:
        title = match.group(1)
    else:
        title = name
    
    # Normalize: lowercase, remove punctuation
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def extract_timestamp(filename: str) -> datetime | None:
    """Extract timestamp from filename"""
    # Pattern: 2025-10-24T17-32-41.785Z or 2025-10-24T17-32-41-785Z
    pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})[-.](\d{3})Z'
    match = re.search(pattern, filename)
    
    if match:
        date_str = match.group(1).replace('T', ' ').replace('-', ':', 2)
        ms = match.group(2)
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return dt
        except:
            pass
    
    return None


def compute_md5(file_path: Path) -> str:
    """Compute MD5 hash of file"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


@huey.task(retries=3, retry_delay=60)
def deduplicate_raw_files(staging_dir: str = None):
    """
    Deduplicate raw .docx files before conversion
    
    Strategy (from 2025-11-04 manual work):
    1. Group by normalized title
    2. Within groups, check:
       - MD5 hash (identical content)
       - Timestamps < 5 minutes apart
    3. Keep oldest in each duplicate group
    
    Returns: (kept_count, removed_count)
    """
    staging_path = Path(staging_dir) if staging_dir else STAGING
    staging_path.mkdir(parents=True, exist_ok=True)
    
    duplicates_dir = staging_path / "duplicates"
    duplicates_dir.mkdir(exist_ok=True)
    
    # Find all .docx files
    files = list(staging_path.glob("*.docx"))
    logger.info(f"Found {len(files)} .docx files to deduplicate")
    
    if not files:
        return (0, 0)
    
    # Group by title
    title_groups = defaultdict(list)
    for file_path in files:
        title = normalize_title(file_path.name)
        timestamp = extract_timestamp(file_path.name)
        md5 = compute_md5(file_path)
        
        title_groups[title].append({
            'path': file_path,
            'timestamp': timestamp,
            'md5': md5
        })
    
    # Find duplicates within each group
    removed = []
    for title, file_group in title_groups.items():
        if len(file_group) == 1:
            continue  # No duplicates
        
        # Sort by timestamp (oldest first, None last)
        file_group.sort(key=lambda x: x['timestamp'] if x['timestamp'] else datetime.max)
        
        # Check for duplicates (MD5 or time-based)
        seen_md5 = set()
        kept = []
        
        for file_info in file_group:
            # Check MD5 duplicate
            if file_info['md5'] in seen_md5:
                logger.info(f"Duplicate (MD5): {file_info['path'].name}")
                removed.append(file_info['path'])
                continue
            
            # Check time-based duplicate (within 5 min of any kept file)
            is_duplicate = False
            if file_info['timestamp']:
                for kept_file in kept:
                    if kept_file['timestamp']:
                        time_diff = abs((file_info['timestamp'] - kept_file['timestamp']).total_seconds())
                        if time_diff < 300:  # 5 minutes
                            logger.info(f"Duplicate (time): {file_info['path'].name} ({int(time_diff)}s from {kept_file['path'].name})")
                            is_duplicate = True
                            break
            
            if is_duplicate:
                removed.append(file_info['path'])
            else:
                seen_md5.add(file_info['md5'])
                kept.append(file_info)
    
    # Move duplicates
    for file_path in removed:
        dest = duplicates_dir / file_path.name
        file_path.rename(dest)
    
    kept_count = len(files) - len(removed)
    logger.info(f"✅ Deduplication complete: {kept_count} kept, {len(removed)} removed")
    
    return (kept_count, len(removed))


@huey.task(retries=2, retry_delay=30)
def convert_to_markdown(docx_path: str):
    """
    Convert .docx to .transcript.md using pandoc
    
    Returns: path to converted .md file
    Raises: Exception if conversion fails validation
    """
    docx_file = Path(docx_path)
    
    if not docx_file.exists():
        raise FileNotFoundError(f"File not found: {docx_path}")
    
    # Output path (same dir, .transcript.md extension)
    md_file = docx_file.parent / docx_file.name.replace(".docx", ".transcript.md")
    
    # Run pandoc conversion
    try:
        result = subprocess.run(
            ["pandoc", str(docx_file), "-o", str(md_file)],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.info(f"✅ Converted: {docx_file.name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc error: {e.stderr}")
        raise Exception(f"Pandoc conversion failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception(f"Pandoc timeout after 60s")
    
    # Validate output
    if not md_file.exists():
        raise Exception(f"Output file not created: {md_file}")
    
    size = md_file.stat().st_size
    if size < 100:
        raise Exception(f"Output too small: {size} bytes")
    if size > 10 * 1024 * 1024:
        raise Exception(f"Output too large: {size} bytes")
    
    # Check UTF-8 encoding
    try:
        md_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise Exception("Output is not valid UTF-8")
    
    # Delete original .docx
    docx_file.unlink()
    
    return str(md_file)


@huey.task(retries=1)
def stage_validated_file(md_path: str):
    """
    Move validated .transcript.md to Inbox (triggers existing pipeline)
    
    Returns: final path in Inbox
    """
    md_file = Path(md_path)
    
    if not md_file.exists():
        raise FileNotFoundError(f"File not found: {md_path}")
    
    INBOX.mkdir(parents=True, exist_ok=True)
    
    # Move to Inbox
    dest = INBOX / md_file.name
    md_file.rename(dest)
    
    # Log import
    IMPORT_LOG.parent.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": "gdrive_huey",
        "filename": md_file.name,
        "status": "imported"
    }
    
    with open(IMPORT_LOG, 'a') as f:
        import json
        f.write(json.dumps(log_entry) + '\n')
    
    logger.info(f"✅ Staged: {md_file.name} → Inbox")
    
    return str(dest)


@huey.task()
def process_batch(docx_files: list[str]):
    """
    Orchestration task: deduplicate → convert → stage
    
    This is the main entry point called by Zo scheduled task
    """
    staging_dir = Path(docx_files[0]).parent if docx_files else STAGING
    
    # Step 1: Deduplicate
    kept, removed = deduplicate_raw_files.schedule((str(staging_dir),), delay=0).get(blocking=True, timeout=300)
    logger.info(f"Deduplication: {kept} kept, {removed} removed")
    
    # Step 2: Convert (parallel)
    unique_files = list(staging_dir.glob("*.docx"))
    conversion_tasks = []
    for docx_file in unique_files:
        task = convert_to_markdown.schedule((str(docx_file),))
        conversion_tasks.append(task)
    
    # Wait for conversions
    converted_files = []
    for task in conversion_tasks:
        try:
            md_path = task.get(blocking=True, timeout=120)
            converted_files.append(md_path)
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
    
    logger.info(f"Converted: {len(converted_files)}/{len(unique_files)}")
    
    # Step 3: Stage (sequential, fast)
    staged = 0
    for md_path in converted_files:
        try:
            stage_validated_file.schedule((md_path,), delay=0).get(blocking=True, timeout=30)
            staged += 1
        except Exception as e:
            logger.error(f"Staging failed: {e}")
    
    logger.info(f"✅ Batch complete: {staged} files staged to Inbox")
    
    return {
        "deduplicated": removed,
        "converted": len(converted_files),
        "staged": staged
    }
