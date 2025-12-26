#!/usr/bin/env python3
"""
N5 Semantic Re-Index Service
Full re-index of critical areas with text-embedding-3-large.

Features:
- Runs as a persistent service
- Detailed progress logging to /dev/shm/ for Loki monitoring
- State persistence for resumability
- Lock file to prevent concurrent runs
- Sleeps on completion (service manager keeps it alive)
"""
import hashlib
import json
import logging
import os
import sys
import time
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Force correct import path FIRST
sys.path.insert(0, '/home/workspace/N5/cognition')
os.chdir('/home/workspace')

from n5_memory_client import N5MemoryClient

# === CONFIGURATION ===
LOG_PATH = "/dev/shm/semantic-reindex.log"
STATE_PATH = "/home/workspace/N5/data/reindex_state.json"
COMPLETION_MARKER = "/home/workspace/N5/data/reindex_complete.json"
LOCK_FILE = "/home/workspace/N5/data/reindex.lock"

# Rate limiting
DELAY_BETWEEN_FILES = 0.3
DELAY_ON_ERROR = 5.0
DELAY_ON_RATE_LIMIT = 60.0
PROGRESS_LOG_INTERVAL = 10
STATE_SAVE_INTERVAL = 5

# Critical paths to index
CRITICAL_AREAS = [
    # Core system
    "/home/workspace/N5/capabilities",
    "/home/workspace/N5/prefs",
    "/home/workspace/N5/docs",
    "/home/workspace/N5/schemas",
    "/home/workspace/N5/workflows",
    # Knowledge bases
    "/home/workspace/Knowledge",
    "/home/workspace/Personal/Knowledge",
    # Prompts
    "/home/workspace/Prompts",
    # NEW: Lists (all)
    "/home/workspace/Lists",
    # NEW: Articles (all)
    "/home/workspace/Articles",
    # NEW: Selective Documents
    "/home/workspace/Documents/Careerspan",
    "/home/workspace/Documents/Deliverables",
    "/home/workspace/Documents/Knowledge",
    "/home/workspace/Documents/System",
    # NEW: Meeting blocks only (handled specially below)
    "/home/workspace/Personal/Meetings",
]

EXCLUDE_PATTERNS = [
    ".git", "__pycache__", ".stversions", ".stfolder",
    "node_modules", ".n5protected", "backup", "archive",
    # Meeting exclusions
    "transcript", "manifest.json", "FOLLOW_UP",
]

# === LOGGING SETUP ===
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

# Use stderr for service logs (captured by Zo service manager)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr
)
LOG = logging.getLogger("semantic-reindex")


def acquire_lock():
    """Acquire exclusive lock, return lock file handle or None if can't acquire."""
    try:
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except (IOError, OSError):
        return None


def release_lock(lock_fd):
    """Release the lock."""
    if lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            os.remove(LOCK_FILE)
        except:
            pass


def should_exclude(path: str) -> bool:
    """Check if path should be excluded."""
    path_lower = path.lower()
    for pattern in EXCLUDE_PATTERNS:
        if pattern.lower() in path_lower:
            return True
    return False


def is_meeting_path(path: str) -> bool:
    """Check if this is a meeting folder path."""
    return "/Personal/Meetings/" in path


def collect_files() -> List[str]:
    """Collect all files to index with special handling for meetings."""
    files = []
    for area in CRITICAL_AREAS:
        if not os.path.exists(area):
            continue
        for root, dirs, filenames in os.walk(area):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            
            for fname in filenames:
                fpath = os.path.join(root, fname)
                
                # Skip non-indexable files
                if not fname.endswith(('.md', '.jsonl', '.yaml', '.yml')):
                    continue
                
                # Skip excluded patterns
                if should_exclude(fpath):
                    continue
                
                # Special handling for meetings: ONLY B*.md block files
                if is_meeting_path(fpath):
                    if not fname.startswith('B') or not fname.endswith('.md'):
                        continue
                
                files.append(fpath)
    
    return sorted(set(files))


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"processed": [], "failed": [], "started_at": None, "model": None}


def save_state(state: dict):
    state["last_update"] = datetime.now().isoformat()
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def index_single_file(client: N5MemoryClient, fpath: str) -> tuple:
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if not content.strip():
            return True, "empty"
        content_date = client.extract_content_date(fpath)
        client.index_file(fpath, content, content_date)
        return True, "indexed"
    except Exception as e:
        error_str = str(e).lower()
        if "rate" in error_str or "429" in error_str:
            return False, "rate_limited"
        if "locked" in error_str:
            return False, "db_locked"
        return False, str(e)[:100]


def write_completion_report(state: dict, total_files: int):
    report = {
        "completed_at": datetime.now().isoformat(),
        "started_at": state.get("started_at"),
        "model": state.get("model"),
        "total_files": total_files,
        "successfully_indexed": len(state["processed"]),
        "failed": len(state["failed"]),
        "failed_files": state["failed"][:50],
    }
    with open(COMPLETION_MARKER, 'w') as f:
        json.dump(report, f, indent=2)
    LOG.info(f"Completion report written to {COMPLETION_MARKER}")


def main():
    # Check if already complete
    if os.path.exists(COMPLETION_MARKER):
        LOG.info("Indexing already complete. Sleeping indefinitely.")
        while True:
            time.sleep(3600)  # Sleep 1 hour, repeat forever
    
    # Acquire lock
    lock_fd = acquire_lock()
    if not lock_fd:
        LOG.warning("Another instance is running. Waiting 60s then retrying...")
        time.sleep(60)
        return  # Exit, service manager will restart
    
    try:
        LOG.info("=" * 70)
        LOG.info("N5 SEMANTIC REINDEX SERVICE - CLEAN START")
        LOG.info("=" * 70)
        
        # Initialize client
        client = N5MemoryClient()
        LOG.info(f"Provider: {client.provider}")
        LOG.info(f"Model: {client.openai_model}")
        LOG.info(f"DB Path: {client.db_path}")
        
        if client.provider != "openai":
            LOG.error("OpenAI provider not available!")
            return
        
        state = load_state()
        if not state["started_at"]:
            state["started_at"] = datetime.now().isoformat()
            state["model"] = client.openai_model
        
        all_files = collect_files()
        LOG.info(f"Total files: {len(all_files)}")
        
        already_done = set(state["processed"])
        to_process = [f for f in all_files if f not in already_done]
        LOG.info(f"Already processed: {len(already_done)}")
        LOG.info(f"Remaining: {len(to_process)}")
        
        if not to_process:
            LOG.info("All files processed!")
            write_completion_report(state, len(all_files))
            release_lock(lock_fd)
            while True:
                time.sleep(3600)
        
        success_count = len(state["processed"])
        
        for i, fpath in enumerate(to_process):
            short = fpath.replace("/home/workspace/", "")
            
            ok, msg = index_single_file(client, fpath)
            
            if ok:
                state["processed"].append(fpath)
                success_count += 1
                LOG.info(f"[{success_count}/{len(all_files)}] ✓ {short}")
            else:
                state["failed"].append(fpath)
                LOG.warning(f"[{success_count}/{len(all_files)}] ✗ {short}: {msg}")
                
                if msg == "rate_limited":
                    LOG.warning(f"Rate limited - sleeping {DELAY_ON_RATE_LIMIT}s")
                    save_state(state)
                    time.sleep(DELAY_ON_RATE_LIMIT)
                elif msg == "db_locked":
                    time.sleep(5)
                else:
                    time.sleep(DELAY_ON_ERROR)
                continue
            
            if (i + 1) % STATE_SAVE_INTERVAL == 0:
                save_state(state)
            
            if (i + 1) % PROGRESS_LOG_INTERVAL == 0:
                pct = (success_count * 100) // len(all_files)
                LOG.info(f"PROGRESS: {success_count}/{len(all_files)} ({pct}%)")
            
            time.sleep(DELAY_BETWEEN_FILES)
        
        save_state(state)
        write_completion_report(state, len(all_files))
        
        LOG.info("=" * 70)
        LOG.info("INDEXING COMPLETE")
        LOG.info(f"Total: {len(all_files)}, Success: {success_count}, Failed: {len(state['failed'])}")
        LOG.info("=" * 70)
        
    finally:
        release_lock(lock_fd)
    
    # Sleep forever after completion
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()



