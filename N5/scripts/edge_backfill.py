#!/usr/bin/env python3
from N5.lib.paths import N5_ROOT, N5_DATA_DIR
"""
Edge Backfill: Batch process historical meetings for edge extraction.

Usage:
    # Scan for meetings that need edge extraction
    python3 edge_backfill.py scan --period Q4-2025
    
    # Generate extraction batch (JSONL file for review)
    python3 edge_backfill.py prepare --batch-size 10
    
    # List pending batches
    python3 edge_backfill.py list
    
    # Show batch details
    python3 edge_backfill.py show <batch_file>

This script prepares meetings for edge extraction. The actual extraction
happens via B33 prompt (LLM-based), then edges are committed via edge_reviewer.py.

Workflow:
1. scan → Find meetings with B01 but no B33
2. prepare → Create batch file with meeting contexts
3. (Zo runs B33 on batch) → Generates JSONL edges
4. edge_reviewer.py commit → Commits to edges.db
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3

# Paths
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
REVIEW_DIR = N5_ROOT / "review" / "edges"
BACKFILL_DIR = REVIEW_DIR / "backfill"
EDGES_DB = N5_DATA_DIR / "edges.db"


def get_processed_meetings() -> set:
    """Get meeting IDs that already have edges."""
    if not EDGES_DB.exists():
        return set()
    
    conn = sqlite3.connect(EDGES_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT context_meeting_id FROM edges WHERE context_meeting_id IS NOT NULL")
    result = {row[0] for row in cursor.fetchall()}
    conn.close()
    return result


def find_meetings_for_period(period: str) -> List[Path]:
    """Find meetings for a given period (e.g., 'Q4-2025', '2025-12', 'all')."""
    meetings = []
    
    # Find all Week-of directories and sort them DESCENDING for LIFO
    week_dirs = sorted(list(MEETINGS_ROOT.glob("Week-of-*")), reverse=True)
    
    for week_dir in week_dirs:
        # Extract date from week directory name
        week_name = week_dir.name  # e.g., "Week-of-2025-12-15"
        
        # Filter by period
        if period == "all":
            pass  # Include all
        elif period.startswith("Q"):
            # Quarter format: Q4-2025
            quarter, year = period.split("-")
            quarter_num = int(quarter[1])
            year = int(year)
            
            # Extract year-month from week name
            try:
                parts = week_name.replace("Week-of-", "").split("-")
                week_year = int(parts[0])
                week_month = int(parts[1])
                
                # Check if in quarter
                quarter_start = (quarter_num - 1) * 3 + 1
                quarter_end = quarter_num * 3
                
                if week_year != year or not (quarter_start <= week_month <= quarter_end):
                    continue
            except (ValueError, IndexError):
                continue
        elif "-" in period and len(period) == 7:
            # Month format: 2025-12
            if not week_name.startswith(f"Week-of-{period}"):
                continue
        
        # Find meeting directories within week
        week_meetings = []
        for meeting_dir in week_dir.iterdir():
            if meeting_dir.is_dir():
                # Check if it has B01 (required for extraction)
                b01_file = meeting_dir / "B01_DETAILED_RECAP.md"
                if b01_file.exists():
                    week_meetings.append(meeting_dir)
        
        # Sort meetings within the week descending (newest first)
        meetings.extend(sorted(week_meetings, reverse=True))
    
    return meetings


def meeting_to_id(meeting_path: Path) -> str:
    """Generate consistent meeting ID from path."""
    # e.g., "mtg_2025-12-15_david-x-careerspan"
    name = meeting_path.name.lower()
    # Clean up name
    name = name.replace(" ", "-").replace("_", "-")
    # Truncate if too long
    if len(name) > 60:
        name = name[:60]
    return f"mtg_{name}"


def scan_meetings(period: str) -> Dict:
    """Scan for meetings that need edge extraction."""
    all_meetings = find_meetings_for_period(period)
    processed = get_processed_meetings()
    
    needs_extraction = []
    already_processed = []
    
    for meeting_path in all_meetings:
        meeting_id = meeting_to_id(meeting_path)
        
        if meeting_id in processed:
            already_processed.append({
                "path": str(meeting_path),
                "meeting_id": meeting_id
            })
        else:
            # Check what blocks exist
            blocks = []
            for f in meeting_path.iterdir():
                if f.name.startswith("B") and f.name.endswith(".md"):
                    blocks.append(f.name.replace(".md", ""))
            
            needs_extraction.append({
                "path": str(meeting_path),
                "meeting_id": meeting_id,
                "blocks": blocks
            })
    
    return {
        "period": period,
        "total_meetings": len(all_meetings),
        "needs_extraction": len(needs_extraction),
        "already_processed": len(already_processed),
        "meetings": needs_extraction
    }


def prepare_batch(batch_size: int = 10, period: str = "all") -> Dict:
    """Prepare a batch of meetings for extraction."""
    scan_result = scan_meetings(period)
    
    if scan_result["needs_extraction"] == 0:
        return {
            "status": "empty",
            "message": "No meetings need extraction"
        }
    
    # Take batch_size meetings
    batch_meetings = scan_result["meetings"][:batch_size]
    
    # Create batch file
    BACKFILL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    batch_file = BACKFILL_DIR / f"batch_{timestamp}.json"
    
    batch_data = {
        "created": datetime.now().isoformat(),
        "period": period,
        "batch_size": len(batch_meetings),
        "status": "pending",
        "meetings": []
    }
    
    for meeting in batch_meetings:
        meeting_path = Path(meeting["path"])
        
        # Read B01 for context
        b01_path = meeting_path / "B01_DETAILED_RECAP.md"
        b01_content = ""
        if b01_path.exists():
            b01_content = b01_path.read_text()[:4000]  # Truncate for batch
        
        # Read manifest for metadata
        manifest_path = meeting_path / "manifest.json"
        manifest = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
            except:
                pass
        
        # Read B03 for decisions
        b03_path = meeting_path / "B03_DECISIONS.md"
        b03_content = ""
        if b03_path.exists():
            b03_content = b03_path.read_text()[:2000]
        
        batch_data["meetings"].append({
            "meeting_id": meeting["meeting_id"],
            "path": meeting["path"],
            "blocks": meeting["blocks"],
            "b01_preview": b01_content,
            "b03_preview": b03_content,
            "attendees": manifest.get("attendees", []),
            "meeting_type": manifest.get("meeting_type", "unknown")
        })
    
    # Write batch file
    batch_file.write_text(json.dumps(batch_data, indent=2))
    
    return {
        "status": "created",
        "batch_file": str(batch_file),
        "meetings_in_batch": len(batch_meetings),
        "remaining": scan_result["needs_extraction"] - len(batch_meetings)
    }


def list_batches() -> Dict:
    """List all batch files."""
    BACKFILL_DIR.mkdir(parents=True, exist_ok=True)
    
    batches = []
    for f in BACKFILL_DIR.glob("batch_*.json"):
        try:
            data = json.loads(f.read_text())
            batches.append({
                "file": f.name,
                "created": data.get("created", "unknown"),
                "status": data.get("status", "unknown"),
                "meetings": len(data.get("meetings", []))
            })
        except:
            batches.append({
                "file": f.name,
                "error": "Could not parse"
            })
    
    return {
        "batches": sorted(batches, key=lambda x: x.get("created", ""), reverse=True)
    }


def show_batch(batch_file: str) -> Dict:
    """Show details of a batch file."""
    # Handle both full path and just filename
    if "/" not in batch_file:
        batch_path = BACKFILL_DIR / batch_file
    else:
        batch_path = Path(batch_file)
    
    if not batch_path.exists():
        return {"error": f"Batch file not found: {batch_path}"}
    
    data = json.loads(batch_path.read_text())
    
    # Summarize meetings
    summary = []
    for m in data.get("meetings", []):
        summary.append({
            "meeting_id": m["meeting_id"],
            "type": m.get("meeting_type", "unknown"),
            "attendees": len(m.get("attendees", [])),
            "blocks": len(m.get("blocks", []))
        })
    
    return {
        "file": str(batch_path),
        "created": data.get("created"),
        "status": data.get("status"),
        "period": data.get("period"),
        "meeting_count": len(summary),
        "meetings": summary
    }


def generate_extraction_prompt(batch_file: str) -> str:
    """Generate a prompt for Zo to extract edges from a batch."""
    if "/" not in batch_file:
        batch_path = BACKFILL_DIR / batch_file
    else:
        batch_path = Path(batch_file)
    
    if not batch_path.exists():
        return f"Error: Batch file not found: {batch_path}"
    
    data = json.loads(batch_path.read_text())
    
    prompt_parts = [
        "# Edge Extraction Batch",
        f"Batch: {batch_path.name}",
        f"Meetings: {len(data['meetings'])}",
        "",
        "For each meeting below, extract edges using B33 format.",
        "Output JSONL (one JSON object per line) for all edges found.",
        "",
        "---",
        ""
    ]
    
    for i, meeting in enumerate(data["meetings"], 1):
        prompt_parts.append(f"## Meeting {i}: {meeting['meeting_id']}")
        prompt_parts.append(f"Type: {meeting.get('meeting_type', 'unknown')}")
        prompt_parts.append(f"Attendees: {', '.join(meeting.get('attendees', ['unknown']))}")
        prompt_parts.append("")
        prompt_parts.append("### B01 (Recap):")
        prompt_parts.append("```")
        prompt_parts.append(meeting.get("b01_preview", "No B01 available")[:2000])
        prompt_parts.append("```")
        if meeting.get("b03_preview"):
            prompt_parts.append("")
            prompt_parts.append("### B03 (Decisions):")
            prompt_parts.append("```")
            prompt_parts.append(meeting["b03_preview"][:1500])
            prompt_parts.append("```")
        prompt_parts.append("")
        prompt_parts.append("---")
        prompt_parts.append("")
    
    prompt_parts.append("Now extract all edges as JSONL. Remember:")
    prompt_parts.append("- Each line is a complete JSON object")
    prompt_parts.append("- Include meeting_id in each edge")
    prompt_parts.append("- Use valid relation types: originated_by, supported_by, challenged_by, etc.")
    
    return "\n".join(prompt_parts)


def main():
    parser = argparse.ArgumentParser(description="Edge backfill for historical meetings")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for meetings needing extraction")
    scan_parser.add_argument("--period", default="Q4-2025", 
                            help="Period to scan: 'Q4-2025', '2025-12', or 'all'")
    
    # prepare command
    prepare_parser = subparsers.add_parser("prepare", help="Prepare extraction batch")
    prepare_parser.add_argument("--batch-size", type=int, default=10,
                               help="Number of meetings per batch")
    prepare_parser.add_argument("--period", default="Q4-2025",
                               help="Period to prepare from")
    
    # list command
    subparsers.add_parser("list", help="List pending batches")
    
    # show command
    show_parser = subparsers.add_parser("show", help="Show batch details")
    show_parser.add_argument("batch_file", help="Batch file to show")
    
    # prompt command - generate extraction prompt
    prompt_parser = subparsers.add_parser("prompt", help="Generate extraction prompt for batch")
    prompt_parser.add_argument("batch_file", help="Batch file to generate prompt for")
    
    args = parser.parse_args()
    
    try:
        if args.command == "scan":
            result = scan_meetings(args.period)
            print(json.dumps(result, indent=2))
            
        elif args.command == "prepare":
            result = prepare_batch(args.batch_size, args.period)
            print(json.dumps(result, indent=2))
            
        elif args.command == "list":
            result = list_batches()
            print(json.dumps(result, indent=2))
            
        elif args.command == "show":
            result = show_batch(args.batch_file)
            print(json.dumps(result, indent=2))
            
        elif args.command == "prompt":
            prompt = generate_extraction_prompt(args.batch_file)
            print(prompt)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()




