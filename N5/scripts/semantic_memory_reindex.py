#!/usr/bin/env python3
"""
Wrapper to run the N5 Semantic Re-index Service as a one-shot command.
"""
import os
import subprocess
import sys
from pathlib import Path

try:
    from N5.lib.paths import N5_DATA_DIR, N5_SCRIPTS_DIR
except ImportError:
    N5_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
    N5_SCRIPTS_DIR = Path(__file__).resolve().parent

LOCK_FILE = str(N5_DATA_DIR / "reindex.lock")
COMPLETION_MARKER = str(N5_DATA_DIR / "reindex_complete.json")
SERVICE_SCRIPT = str(N5_SCRIPTS_DIR / "semantic_reindex_service.py")

def main():
    # If already complete, remove marker to force re-run (as requested)
    # Otherwise the service would sleep forever.
    if os.path.exists(COMPLETION_MARKER):
        print(f"Removing completion marker to allow re-run...")
        os.remove(COMPLETION_MARKER)

    # Check for existing lock
    if os.path.exists(LOCK_FILE):
        print("Re-index already in progress.")
        sys.exit(1)

    # Run the service
    print(f"Starting semantic memory re-indexing...")
    print(f"Running {SERVICE_SCRIPT}...")
    
    # Run the script and pipe output
    result = subprocess.run(
        [sys.executable, SERVICE_SCRIPT],
        cwd="/home/workspace"
    )
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
