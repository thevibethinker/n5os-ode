#!/usr/bin/env python3
"""
Thought Provoker Scanner V2

Scans B32_THOUGHT_PROVOKING_IDEAS.md blocks from meetings
to extract high-signal provocations for daily sessions.

Usage:
    python3 thought_provoker_scan_v2.py [--days 14] [--output PATH]
"""

import argparse
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
DEFAULT_OUTPUT = Path("/home/workspace/N5/data/provocation_candidates_v2.json")


def parse_b32_file(filepath: Path) -> list[dict]:
    """
    Parse a B32_THOUGHT_PROVOKING_IDEAS.md file.
    
    Handles multiple formats:
    1. Structured: ## N. Title with optional **Idea:** and **Provocation:** fields
    2. Bullet: - **Title:** Description...
    3. Simple bullets: - Some idea text
    
    Returns list of {title, idea, provocation, category} dicts.
    """
    ideas = []
    
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not read {filepath}: {e}")
        return ideas
    
    # Try Format 1: ## N. Title sections (with or without ### prefix)
    sections = re.split(r'\n###? \d+\.\s*', content)
    
    if len(sections) > 1:
        # Structured format detected
        for section in sections[1:]:
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            title = lines[0].strip()
            idea = ""
            provocation = ""
            category = ""
            
            # Check for explicit **Idea:** and **Provocation:** fields
            has_explicit_fields = False
            for line in lines[1:]:
                line_lower = line.lower()
                if "**idea:**" in line_lower:
                    idea = re.sub(r'.*\*\*idea:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
                    has_explicit_fields = True
                elif "**provocation:**" in line_lower:
                    provocation = re.sub(r'.*\*\*provocation:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
                    has_explicit_fields = True
                elif "**category:**" in line_lower:
                    category = re.sub(r'.*\*\*category:\*\*\s*', '', line, flags=re.IGNORECASE).strip()
            
            # If no explicit fields, use the full section content as the idea
            if not has_explicit_fields and len(lines) > 1:
                # Join all non-empty lines after the title
                idea = ' '.join(line.strip() for line in lines[1:] if line.strip())
            
            if title and idea:
                ideas.append({
                    "title": title,
                    "idea": idea,
                    "provenance": provocation,
                    "category": category or "Uncategorized"
                })
    
    # Try Format 2: Bullet points with **Title:** pattern
    if not ideas:
        # Look for lines like: - **Title:** Description
        bullet_pattern = re.compile(r'^-\s*\*\*([^*:]+)(?::\*\*|\*\*:)\s*(.+)$', re.MULTILINE)
        matches = bullet_pattern.findall(content)
        
        for title, description in matches:
            title = title.strip()
            description = description.strip()
            if title and description:
                ideas.append({
                    "title": title,
                    "idea": description,
                    "provocation": "",
                    "category": "Uncategorized"
                })
    
    # Try Format 3: Simple bullet points (- Some idea text) or (* Some idea text)
    if not ideas:
        lines = content.split('\n')
        in_content = False
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                in_content = True
                continue
            if not in_content:
                continue
            # Match both - and * bullets
            if (line.startswith('- ') or line.startswith('* ')) and len(line) > 20:
                idea_text = line[2:].strip()
                # Extract title if bold at start
                title_match = re.match(r'\*\*([^*]+)\*\*[:\s]*(.*)$', idea_text)
                if title_match:
                    title = title_match.group(1).strip()
                    description = title_match.group(2).strip()
                else:
                    # Use first ~50 chars as title
                    title = idea_text[:50] + "..." if len(idea_text) > 50 else idea_text
                    description = idea_text
                
                ideas.append({
                    "title": title,
                    "idea": description,
                    "provocation": "",
                    "category": "Uncategorized"
                })
    
    return ideas


def extract_meeting_date(folder_name: str) -> Optional[str]:
    """Extract date from meeting folder name like '2025-12-09_Meeting-Name'."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', folder_name)
    if match:
        return match.group(1)
    return None


def scan_meetings(days: int = 14, scan_all: bool = False) -> dict:
    """
    Scan B32 files from recent meetings.
    
    Args:
        days: Number of days to look back for "fresh" ideas
        scan_all: If True, scan ALL meetings regardless of date (for pattern detection)
    
    Returns:
        Dict with scan metadata and candidates array
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    candidates = []
    meetings_scanned = 0
    
    # Find all B32 files
    b32_files = list(MEETINGS_ROOT.glob("**/B32_*.md"))
    logger.info(f"Found {len(b32_files)} B32 files total")
    
    for b32_path in b32_files:
        # Get meeting folder (parent)
        meeting_folder = b32_path.parent
        meeting_name = meeting_folder.name
        
        # Extract date from folder name
        meeting_date_str = extract_meeting_date(meeting_name)
        if not meeting_date_str:
            # Try to get from parent Week-of folder
            week_folder = meeting_folder.parent.name
            if week_folder.startswith("Week-of-"):
                # Use folder mtime as fallback
                pass
            logger.debug(f"Could not extract date from {meeting_name}, using mtime")
            meeting_date_str = datetime.fromtimestamp(
                b32_path.stat().st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%d")
        
        # Parse date
        try:
            meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            logger.warning(f"Invalid date format for {meeting_name}")
            continue
        
        # Filter by date unless scanning all
        if not scan_all and meeting_date < cutoff_date:
            continue
        
        # Parse B32 content
        ideas = parse_b32_file(b32_path)
        if not ideas:
            continue
        
        meetings_scanned += 1
        
        # Build relative path from Meetings root
        try:
            relative_path = meeting_folder.relative_to(MEETINGS_ROOT)
        except ValueError:
            relative_path = meeting_folder.name
        
        candidates.append({
            "meeting_folder": str(relative_path),
            "meeting_date": meeting_date_str,
            "meeting_name": meeting_name,
            "ideas": ideas
        })
    
    # Sort by date descending (most recent first)
    candidates.sort(key=lambda x: x["meeting_date"], reverse=True)
    
    result = {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "window_days": days if not scan_all else "all",
        "meetings_scanned": meetings_scanned,
        "total_ideas": sum(len(c["ideas"]) for c in candidates),
        "candidates": candidates
    }
    
    return result


def save_candidates(data: dict, output_path: Path):
    """Save candidates to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {data['total_ideas']} ideas from {data['meetings_scanned']} meetings to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Scan B32 meeting blocks for thought provocations")
    parser.add_argument("--days", type=int, default=14, help="Number of days to look back (default: 14)")
    parser.add_argument("--all", action="store_true", help="Scan ALL meetings regardless of date")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT), help="Output JSON path")
    args = parser.parse_args()
    
    result = scan_meetings(days=args.days, scan_all=args.all)
    save_candidates(result, Path(args.output))
    
    # Print summary for agent consumption
    print(f"Scanned {result['meetings_scanned']} meetings, found {result['total_ideas']} ideas")
    
    if result['candidates']:
        print(f"Most recent: {result['candidates'][0]['meeting_name']} ({result['candidates'][0]['meeting_date']})")


if __name__ == "__main__":
    main()



