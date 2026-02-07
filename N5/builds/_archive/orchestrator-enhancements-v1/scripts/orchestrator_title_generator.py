#!/usr/bin/env python3
"""
Orchestrator Title Generator
Pre-generates thread titles for all workers during SPAWN stage

Usage:
    python3 orchestrator_title_generator.py --project "Meeting Pipeline v2" --workers 3 --output titles.json
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_titles(project_name: str, num_workers: int, worker_descriptions: list) -> dict:
    """Generate thread titles for orchestrator + workers"""
    
    date_prefix = datetime.now().strftime("%b %d")
    
    titles = {
        "orchestrator": f"{date_prefix} | 🏗️ Build: {project_name}",
        "workers": []
    }
    
    for i in range(num_workers):
        worker_num = i + 1
        desc = worker_descriptions[i] if i < len(worker_descriptions) else f"Worker {worker_num}"
        title = f"{date_prefix} | 🔨 {project_name} W{worker_num}: {desc}"
        
        # Enforce length limits (35 char max per N5 standards)
        if len(title) > 35:
            # Truncate description
            max_desc_len = 35 - len(f"{date_prefix} | 🔨 {project_name} W{worker_num}: ")
            desc_short = desc[:max_desc_len-3] + "..."
            title = f"{date_prefix} | 🔨 {project_name} W{worker_num}: {desc_short}"
        
        titles["workers"].append({
            "worker_num": worker_num,
            "title": title,
            "description": desc
        })
    
    return titles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--workers", type=int, required=True, help="Number of workers")
    parser.add_argument("--desc", action="append", help="Worker descriptions")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    
    titles = generate_titles(
        project_name=args.project,
        num_workers=args.workers,
        worker_descriptions=args.desc or []
    )
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(titles, indent=2))
    
    logger.info(f"✓ Generated titles: {args.output}")
    logger.info(f"Orchestrator: {titles['orchestrator']}")
    for w in titles['workers']:
        logger.info(f"  Worker {w['worker_num']}: {w['title']}")
    
    return 0


if __name__ == "__main__":
    exit(main())
