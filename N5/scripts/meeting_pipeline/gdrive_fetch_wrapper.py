#!/usr/bin/env python3
"""
Google Drive Fetch Wrapper
This script is meant to be executed BY ZO with tool access,
not as a standalone subprocess
"""
import json
import sys
from pathlib import Path

# Output structure for Zo to act on
def main():
    folder_id = "1JOoPs3WpsIbJWfU7jiD-s6kcQnvFg5VV"
    
    request = {
        "action": "fetch_transcripts",
        "folder_id": folder_id,
        "inbox_dir": "/home/workspace/Personal/Meetings/Inbox",
        "staging_dir": "/home/workspace/N5/data/meeting_pipeline/staging"
    }
    
    print(json.dumps(request, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
