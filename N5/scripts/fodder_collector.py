#!/usr/bin/env python3
"""
Fodder Collector Script

Captures the output of Thought Provoker sessions into managed lists.

Usage:
    python3 fodder_collector.py --type [fodder|tension] --title "Title" --content "Content"
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

LISTS_DIR = Path("/home/workspace/Lists")
FODDER_PATH = LISTS_DIR / "content-fodder.jsonl"
TENSION_PATH = LISTS_DIR / "unresolved-contradictions.jsonl"

def collect(type: str, title: str, content: str):
    target_path = FODDER_PATH if type == "fodder" else TENSION_PATH
    
    # Ensure dir exists
    LISTS_DIR.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "id": f"{datetime.now().strftime('%Y%m%d')}-{title.lower().replace(' ', '-')[:20]}",
        "title": title,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
        "status": "new"
    }
    
    try:
        with open(target_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        logger.info(f"Collected {type} entry: {title} to {target_path}")
    except Exception as e:
        logger.error(f"Failed to collect entry: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fodder Collector")
    parser.add_argument("--type", choices=["fodder", "tension"], required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True)
    args = parser.parse_args()
    
    collect(args.type, args.title, args.content)

