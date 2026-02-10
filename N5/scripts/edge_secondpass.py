#!/usr/bin/env python3
"""
Edge Second Pass: Additive extraction for broader ideas on already-processed meetings.

Scans meetings that have existing edges but were extracted with narrow (Careerspan-focused)
prompt. Re-extracts with broader prompt focusing on non-career themes.

Usage:
    # Scan for meetings needing second pass
    python3 edge_secondpass.py scan
    
    # Prepare a batch for extraction
    python3 edge_secondpass.py prepare --batch-size 3
    
    # Generate prompt for a batch
    python3 edge_secondpass.py prompt <batch_file>
    
    # Mark a batch as complete
    python3 edge_secondpass.py complete <batch_id>
    
    # Show status
    python3 edge_secondpass.py status
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Paths
N5_ROOT = Path("/home/workspace/N5")
N5_DATA = N5_ROOT / "data"
EDGES_DB = Path("/home/workspace/N5/cognition/brain.db")
TRACKING_FILE = N5_DATA / "secondpass_tracking.json"
BATCH_DIR = N5_ROOT / "review" / "edges" / "secondpass"
PROGRESS_LOG = N5_ROOT / "data" / "secondpass_progress.log"
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")

# Cutoff date: meetings processed BEFORE this date need second pass
# Meetings processed ON or AFTER this date already have expanded POV
CUTOFF_DATE = datetime(2026, 1, 9, tzinfo=timezone.utc)

# Ensure directories exist
BATCH_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(EDGES_DB)
    conn.row_factory = sqlite3.Row
    return conn


def load_tracking() -> Dict:
    """Load or initialize tracking file."""
    if TRACKING_FILE.exists():
        return json.loads(TRACKING_FILE.read_text())
    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "completed_meetings": [],
        "in_progress_batches": [],
        "stats": {
            "total_identified": 0,
            "completed": 0,
            "edges_added": 0
        }
    }


def save_tracking(data: Dict):
    """Save tracking file."""
    data["updated"] = datetime.now(timezone.utc).isoformat()
    TRACKING_FILE.write_text(json.dumps(data, indent=2))


def find_processed_meetings() -> List[Dict]:
    """Find all meetings that have intelligence blocks (B01) and should get second pass.
    
    Only includes meetings where B01 was created BEFORE CUTOFF_DATE.
    Meetings processed on/after cutoff already have expanded extraction.
    """
    tracking = load_tracking()
    completed = set(tracking.get("completed_meetings", []))
    
    meetings = []
    
    # Scan meeting folders - any meeting with B01 is considered "processed"
    for week_dir in sorted(MEETINGS_ROOT.iterdir(), reverse=True):
        if not week_dir.is_dir() or not week_dir.name.startswith("Week-of-"):
            continue
        
        for meeting_dir in week_dir.iterdir():
            if not meeting_dir.is_dir():
                continue
            
            # Check if this meeting has a B01 (was processed with intelligence)
            b01_files = list(meeting_dir.glob("B01*.md"))
            if not b01_files:
                continue
            
            # Check B01 modification time - only include if processed BEFORE cutoff
            b01_mtime = datetime.fromtimestamp(b01_files[0].stat().st_mtime, tz=timezone.utc)
            if b01_mtime >= CUTOFF_DATE:
                # This meeting was processed with expanded POV, skip
                continue
            
            meeting_id = f"mtg_{meeting_dir.name}"
            
            # Skip if already completed second pass
            if meeting_id in completed:
                continue
            
            meetings.append({
                "meeting_id": meeting_id,
                "path": str(meeting_dir),
                "has_b01": True,
                "b01_processed": b01_mtime.isoformat(),
                "week": week_dir.name
            })
    
    return meetings


def scan_meetings() -> Dict:
    """Scan for meetings needing second pass."""
    meetings = find_processed_meetings()
    tracking = load_tracking()
    
    # Update tracking
    tracking["stats"]["total_identified"] = len(meetings)
    save_tracking(tracking)
    
    return {
        "cutoff_date": CUTOFF_DATE.isoformat(),
        "total_meetings_before_cutoff": len(meetings),
        "already_completed": tracking["stats"]["completed"],
        "remaining": len(meetings),
        "sample": meetings[:5] if meetings else []
    }


def prepare_batch(batch_size: int = 3) -> Dict:
    """Prepare a batch of meetings for second-pass extraction."""
    meetings = find_processed_meetings()
    
    if not meetings:
        return {"status": "complete", "message": "All meetings have had second pass"}
    
    # Take batch_size meetings (LIFO - most recent first, already sorted)
    batch_meetings = meetings[:batch_size]
    
    # Create batch file
    batch_id = datetime.now().strftime("%Y-%m-%d_%H%M")
    batch_file = BATCH_DIR / f"secondpass_{batch_id}.json"
    
    batch_data = {
        "created": datetime.now(timezone.utc).isoformat(),
        "batch_id": batch_id,
        "batch_size": len(batch_meetings),
        "status": "pending",
        "meetings": []
    }
    
    for meeting in batch_meetings:
        meeting_path = Path(meeting["path"])
        
        # Get B01 content for context
        b01_files = list(meeting_path.glob("B01*.md"))
        b01_content = ""
        if b01_files:
            b01_content = b01_files[0].read_text()[:3000]
        
        batch_data["meetings"].append({
            "meeting_id": meeting["meeting_id"],
            "path": meeting["path"],
            "b01_preview": b01_content
        })
    
    batch_file.write_text(json.dumps(batch_data, indent=2))
    
    # Update tracking
    tracking = load_tracking()
    tracking["in_progress_batches"].append(batch_id)
    save_tracking(tracking)
    
    return {
        "status": "created",
        "batch_file": str(batch_file),
        "batch_id": batch_id,
        "meetings_in_batch": len(batch_meetings),
        "remaining": len(meetings) - len(batch_meetings)
    }


def generate_prompt(batch_file: str) -> str:
    """Generate extraction prompt for second pass."""
    batch_path = Path(batch_file)
    if not batch_path.exists():
        raise FileNotFoundError(f"Batch file not found: {batch_file}")
    
    batch_data = json.loads(batch_path.read_text())
    
    # Load contextual primer
    try:
        sys.path.insert(0, str(N5_ROOT / "scripts" / "resonance"))
        from contextual_primer import generate_primer
        primer = generate_primer()
    except ImportError:
        primer = "<!-- Contextual primer not available -->"
    
    # Build prompt
    lines = [
        "# Second Pass Edge Extraction — Broader Ideas",
        f"Batch: {batch_path.name}",
        "",
        "## CRITICAL INSTRUCTION",
        "",
        "This is a SECOND PASS extraction. These meetings have ALREADY been processed for",
        "career/hiring/Careerspan-related ideas. Your job is to extract ONLY the ideas that",
        "were MISSED in the first pass.",
        "",
        "### DO NOT EXTRACT (already covered):",
        "- Career coaching methodology",
        "- Resume/job search advice", 
        "- Hiring/recruiting tactics",
        "- ATS/applicant tracking systems",
        "- Candidate evaluation methods",
        "- Interview techniques",
        "- Careerspan product features",
        "- Talent marketplace dynamics",
        "",
        "### DO EXTRACT (missed in first pass):",
        "- **N5/Productivity Systems** — Personal automation, Zo workflows, agent coordination",
        "- **AI Philosophy** — LLM capabilities, AGI predictions, human-AI collaboration",
        "- **Mental Models** — Personal frameworks for decision-making, pattern recognition",
        "- **Business Strategy** — Non-hiring: fundraising, partnerships, market positioning",
        "- **Trust & Relationships** — Network dynamics, relationship building, social capital",
        "- **Content/Media** — Observations about content strategy, thought leadership",
        "- **Technology Trends** — Beyond AI: platforms, tools, infrastructure",
        "- **Personal Development** — Energy management, focus, productivity philosophy",
        "",
        "---",
        "",
        primer,
        "",
        "---",
        "",
        "## Meetings to Process",
        ""
    ]
    
    for i, meeting in enumerate(batch_data["meetings"], 1):
        lines.append(f"### Meeting {i}: {meeting['meeting_id']}")
        lines.append(f"Path: `{meeting['path']}`")
        lines.append("")
        lines.append("#### B01 Content:")
        lines.append("```")
        lines.append(meeting.get("b01_preview", "No B01 available")[:2500])
        lines.append("```")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## Output Format",
        "",
        "For each meeting, output a JSONL file with edges. Use `secondpass-{batch_id}` as context_meeting_id.",
        "",
        "```jsonl",
        '{"source_type": "idea", "source_id": "your-idea-slug", "relation": "originated_by", "target_type": "person", "target_id": "vrijen-attawar", "evidence": "Quote or context", "context_meeting_id": "secondpass-' + batch_data["batch_id"] + '"}',
        "```",
        "",
        "Remember: ONLY extract non-career ideas. If a meeting has no relevant non-career ideas, output nothing for it.",
        ""
    ])
    
    return "\n".join(lines)


def log_run(batch_id: str, edges_added: int, meetings_completed: int, total_completed: int, remaining: int):
    """Append a progress entry to the log file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"{timestamp} | Batch {batch_id} | +{edges_added} edges | {meetings_completed} mtgs | Total: {total_completed}/{total_completed + remaining} | Remaining: {remaining}\n"
    
    # Create header if file doesn't exist
    if not PROGRESS_LOG.exists():
        header = "=" * 80 + "\n"
        header += "SECOND PASS EDGE EXTRACTION PROGRESS LOG\n"
        header += f"Started: {timestamp}\n"
        header += f"Cutoff Date: {CUTOFF_DATE.isoformat()}\n"
        header += "=" * 80 + "\n\n"
        PROGRESS_LOG.write_text(header)
    
    # Append entry
    with open(PROGRESS_LOG, "a") as f:
        f.write(entry)
        
        # Add completion marker if done
        if remaining == 0:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"COMPLETED: {timestamp}\n")
            f.write(f"Total edges added: {edges_added} (this batch) + previous\n")
            f.write("=" * 80 + "\n")


def get_progress_log() -> str:
    """Return the contents of the progress log."""
    if not PROGRESS_LOG.exists():
        return "No progress log yet. Run some batches first."
    return PROGRESS_LOG.read_text()


def mark_complete(batch_id: str, edges_added: int = 0) -> Dict:
    """Mark a batch as complete."""
    tracking = load_tracking()
    
    # Find batch file
    batch_file = BATCH_DIR / f"secondpass_{batch_id}.json"
    if not batch_file.exists():
        return {"error": f"Batch {batch_id} not found"}
    
    batch_data = json.loads(batch_file.read_text())
    
    # Update tracking
    for meeting in batch_data["meetings"]:
        if meeting["meeting_id"] not in tracking["completed_meetings"]:
            tracking["completed_meetings"].append(meeting["meeting_id"])
    
    if batch_id in tracking["in_progress_batches"]:
        tracking["in_progress_batches"].remove(batch_id)
    
    tracking["stats"]["completed"] += len(batch_data["meetings"])
    tracking["stats"]["edges_added"] += edges_added
    
    # Update batch file
    batch_data["status"] = "complete"
    batch_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    batch_data["edges_added"] = edges_added
    batch_file.write_text(json.dumps(batch_data, indent=2))
    
    save_tracking(tracking)
    
    # Log the run
    remaining = len(find_processed_meetings())
    log_run(
        batch_id=batch_id,
        edges_added=edges_added,
        meetings_completed=len(batch_data["meetings"]),
        total_completed=tracking["stats"]["completed"],
        remaining=remaining
    )
    
    return {
        "status": "marked_complete",
        "batch_id": batch_id,
        "meetings_completed": len(batch_data["meetings"]),
        "total_completed": tracking["stats"]["completed"]
    }


def get_status() -> Dict:
    """Get current second-pass status."""
    tracking = load_tracking()
    meetings = find_processed_meetings()
    
    return {
        "total_with_intelligence": len(meetings) + tracking["stats"]["completed"],
        "completed_second_pass": tracking["stats"]["completed"],
        "remaining": len(meetings),
        "edges_added": tracking["stats"]["edges_added"],
        "in_progress_batches": tracking["in_progress_batches"]
    }


def main():
    parser = argparse.ArgumentParser(description="Second pass edge extraction")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Scan
    subparsers.add_parser("scan", help="Scan for meetings needing second pass")
    
    # Prepare
    prepare_parser = subparsers.add_parser("prepare", help="Prepare a batch")
    prepare_parser.add_argument("--batch-size", type=int, default=3, help="Meetings per batch")
    
    # Prompt
    prompt_parser = subparsers.add_parser("prompt", help="Generate extraction prompt")
    prompt_parser.add_argument("batch_file", help="Path to batch JSON file")
    
    # Complete
    complete_parser = subparsers.add_parser("complete", help="Mark batch complete")
    complete_parser.add_argument("batch_id", help="Batch ID to mark complete")
    complete_parser.add_argument("--edges", type=int, default=0, help="Number of edges added")
    
    # Status
    subparsers.add_parser("status", help="Show current status")
    
    # Log
    subparsers.add_parser("log", help="Show progress log")
    
    args = parser.parse_args()
    
    try:
        if args.command == "scan":
            result = scan_meetings()
            print(json.dumps(result, indent=2))
            
        elif args.command == "prepare":
            result = prepare_batch(args.batch_size)
            print(json.dumps(result, indent=2))
            
        elif args.command == "prompt":
            prompt = generate_prompt(args.batch_file)
            print(prompt)
            
        elif args.command == "complete":
            result = mark_complete(args.batch_id, args.edges)
            print(json.dumps(result, indent=2))
            
        elif args.command == "status":
            result = get_status()
            print(json.dumps(result, indent=2))
            
        elif args.command == "log":
            print(get_progress_log())
            
        else:
            parser.print_help()
            
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()






