#!/usr/bin/env python3
"""Interview fragment storage and synthesis for Pulse v2.

Manages multi-channel interview fragments with JSONL append-only storage
and synthesis capabilities for seeded task creation.

Storage structure per interview:
  N5/pulse/interviews/<task-id>/
  ├── meta.json           # Interview metadata
  ├── fragments.jsonl     # Append-only fragment log
  ├── synthesis.json      # Aggregated synthesis (when seeded)
  └── seed_judgment.json  # LLM judgment result
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timezone
import uuid
import sys

INTERVIEWS_DIR = Path(__file__).parent / "interviews"


def now_utc() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_dir(task_id: str) -> Path:
    """Ensure interview directory exists."""
    interview_dir = INTERVIEWS_DIR / task_id
    interview_dir.mkdir(parents=True, exist_ok=True)
    return interview_dir


def create_interview(task_id: str) -> dict:
    """Initialize a new interview.
    
    Args:
        task_id: Unique identifier for the interview/task
        
    Returns:
        Interview metadata dict or None if already exists
    """
    interview_dir = ensure_dir(task_id)
    meta_path = interview_dir / "meta.json"
    
    if meta_path.exists():
        print(json.dumps({"success": False, "error": "Interview already exists"}))
        return None
    
    meta = {
        "task_id": task_id,
        "created_at": now_utc(),
        "status": "open",
        "fragment_count": 0,
        "last_fragment_at": None,
        "seeded_at": None
    }
    
    meta_path.write_text(json.dumps(meta, indent=2))
    
    # Initialize empty fragments file
    (interview_dir / "fragments.jsonl").touch()
    
    print(json.dumps({"success": True, "interview": meta}))
    return meta


def add_fragment(task_id: str, channel: str, content: str) -> dict:
    """Add a fragment to an interview.
    
    Fragments are appended to the JSONL file and meta is updated.
    Auto-creates interview if it doesn't exist.
    
    Args:
        task_id: Interview/task identifier
        channel: Source channel (sms, email, chat)
        content: Fragment text content
        
    Returns:
        Fragment dict or None if interview is already seeded
    """
    interview_dir = INTERVIEWS_DIR / task_id
    meta_path = interview_dir / "meta.json"
    fragments_path = interview_dir / "fragments.jsonl"
    
    if not meta_path.exists():
        # Auto-create interview if it doesn't exist
        ensure_dir(task_id)
        meta = {
            "task_id": task_id,
            "created_at": now_utc(),
            "status": "open",
            "fragment_count": 0,
            "last_fragment_at": None,
            "seeded_at": None
        }
        meta_path.write_text(json.dumps(meta, indent=2))
        fragments_path.touch()
    
    meta = json.loads(meta_path.read_text())
    
    if meta["status"] == "seeded":
        print(json.dumps({"success": False, "error": "Interview already seeded, cannot add fragments"}))
        return None
    
    fragment = {
        "id": f"frag-{uuid.uuid4().hex[:8]}",
        "timestamp": now_utc(),
        "channel": channel,
        "content": content,
        "processed": False
    }
    
    # Append to JSONL (atomic append)
    with open(fragments_path, "a") as f:
        f.write(json.dumps(fragment) + "\n")
    
    # Update meta
    meta["fragment_count"] += 1
    meta["last_fragment_at"] = fragment["timestamp"]
    meta_path.write_text(json.dumps(meta, indent=2))
    
    print(json.dumps({"success": True, "fragment": fragment}))
    return fragment


def list_fragments(task_id: str) -> list:
    """List all fragments for an interview.
    
    Args:
        task_id: Interview/task identifier
        
    Returns:
        List of fragment dicts
    """
    fragments_path = INTERVIEWS_DIR / task_id / "fragments.jsonl"
    
    if not fragments_path.exists():
        print(json.dumps({"success": False, "error": "Interview not found"}))
        return []
    
    fragments = []
    with open(fragments_path) as f:
        for line in f:
            if line.strip():
                fragments.append(json.loads(line))
    
    print(json.dumps({"success": True, "fragments": fragments, "count": len(fragments)}))
    return fragments


def synthesize(task_id: str) -> dict:
    """Aggregate fragments into synthesis for seeded judgment.
    
    Creates a synthesis.json combining all fragments for LLM review.
    Marks fragments as processed.
    
    Args:
        task_id: Interview/task identifier
        
    Returns:
        Synthesis dict or None if interview not found
    """
    interview_dir = INTERVIEWS_DIR / task_id
    meta_path = interview_dir / "meta.json"
    fragments_path = interview_dir / "fragments.jsonl"
    synthesis_path = interview_dir / "synthesis.json"
    
    if not meta_path.exists():
        print(json.dumps({"success": False, "error": "Interview not found"}))
        return None
    
    meta = json.loads(meta_path.read_text())
    
    if meta["fragment_count"] == 0:
        print(json.dumps({"success": False, "error": "No fragments to synthesize"}))
        return None
    
    # Collect all fragments
    fragments = []
    with open(fragments_path) as f:
        for line in f:
            if line.strip():
                fragments.append(json.loads(line))
    
    # Build synthesis object
    synthesis = {
        "task_id": task_id,
        "synthesized_at": now_utc(),
        "fragment_count": len(fragments),
        "channels_used": list(set(f["channel"] for f in fragments)),
        "raw_content": [f["content"] for f in fragments],
        "combined_text": "\n\n---\n\n".join(f["content"] for f in fragments),
        "fragments": fragments  # Include full fragment details for context
    }
    
    synthesis_path.write_text(json.dumps(synthesis, indent=2))
    
    # Mark fragments as processed
    processed_fragments = []
    for f in fragments:
        f["processed"] = True
        processed_fragments.append(f)
    
    with open(fragments_path, "w") as f:
        for frag in processed_fragments:
            f.write(json.dumps(frag) + "\n")
    
    print(json.dumps({"success": True, "synthesis": synthesis}))
    return synthesis


def mark_seeded(task_id: str, judgment: dict) -> dict:
    """Mark interview as seeded with judgment result.
    
    Called after LLM determines fragments are sufficient.
    Prevents further fragment additions.
    
    Args:
        task_id: Interview/task identifier
        judgment: Dict with seeded, confidence, missing keys
        
    Returns:
        Updated meta dict or None if not found
    """
    interview_dir = INTERVIEWS_DIR / task_id
    meta_path = interview_dir / "meta.json"
    judgment_path = interview_dir / "seed_judgment.json"
    
    if not meta_path.exists():
        print(json.dumps({"success": False, "error": "Interview not found"}))
        return None
    
    meta = json.loads(meta_path.read_text())
    meta["status"] = "seeded"
    meta["seeded_at"] = now_utc()
    meta_path.write_text(json.dumps(meta, indent=2))
    
    # Record judgment
    judgment["recorded_at"] = now_utc()
    judgment_path.write_text(json.dumps(judgment, indent=2))
    
    print(json.dumps({"success": True, "meta": meta, "judgment": judgment}))
    return meta


def get_synthesis(task_id: str) -> dict:
    """Retrieve synthesis for plan generation.
    
    Args:
        task_id: Interview/task identifier
        
    Returns:
        Synthesis dict or None if not found
    """
    synthesis_path = INTERVIEWS_DIR / task_id / "synthesis.json"
    
    if not synthesis_path.exists():
        print(json.dumps({"success": False, "error": "No synthesis found. Run synthesize first."}))
        return None
    
    synthesis = json.loads(synthesis_path.read_text())
    print(json.dumps({"success": True, "synthesis": synthesis}))
    return synthesis


def get_status(task_id: str) -> dict:
    """Get interview status and metadata.
    
    Args:
        task_id: Interview/task identifier
        
    Returns:
        Interview meta dict or None if not found
    """
    meta_path = INTERVIEWS_DIR / task_id / "meta.json"
    
    if not meta_path.exists():
        print(json.dumps({"success": False, "error": "Interview not found"}))
        return None
    
    meta = json.loads(meta_path.read_text())
    print(json.dumps({"success": True, "interview": meta}))
    return meta


def list_interviews() -> list:
    """List all interviews.
    
    Returns:
        List of interview metadata dicts
    """
    if not INTERVIEWS_DIR.exists():
        print(json.dumps({"success": True, "interviews": [], "count": 0}))
        return []
    
    interviews = []
    for interview_dir in INTERVIEWS_DIR.iterdir():
        if interview_dir.is_dir():
            meta_path = interview_dir / "meta.json"
            if meta_path.exists():
                interviews.append(json.loads(meta_path.read_text()))
    
    print(json.dumps({"success": True, "interviews": interviews, "count": len(interviews)}))
    return interviews


def delete_interview(task_id: str, force: bool = False) -> bool:
    """Delete an interview and all its data.
    
    Args:
        task_id: Interview/task identifier
        force: Skip confirmation for seeded interviews
        
    Returns:
        True if deleted, False otherwise
    """
    interview_dir = INTERVIEWS_DIR / task_id
    
    if not interview_dir.exists():
        print(json.dumps({"success": False, "error": "Interview not found"}))
        return False
    
    meta_path = interview_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta["status"] == "seeded" and not force:
            print(json.dumps({"success": False, "error": "Interview is seeded. Use --force to delete."}))
            return False
    
    # Remove all files in directory
    import shutil
    shutil.rmtree(interview_dir)
    
    print(json.dumps({"success": True, "deleted": task_id}))
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Pulse v2 Interview Manager - Fragment storage and synthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create interview
  python3 interview_manager.py create task-abc123
  
  # Add fragments from different channels
  python3 interview_manager.py add task-abc123 --channel sms --content "Make it professional"
  python3 interview_manager.py add task-abc123 --channel email --content "Event is Thursday 6pm"
  
  # List fragments
  python3 interview_manager.py list task-abc123
  
  # Synthesize for seeded judgment
  python3 interview_manager.py synthesize task-abc123
  
  # Mark as seeded
  python3 interview_manager.py mark-seeded task-abc123 --confidence 0.85
  
  # Get status
  python3 interview_manager.py status task-abc123
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # create
    create_parser = subparsers.add_parser("create", help="Create new interview")
    create_parser.add_argument("task_id", help="Task ID for the interview")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add fragment to interview")
    add_parser.add_argument("task_id", help="Task ID")
    add_parser.add_argument("--channel", required=True, choices=["sms", "email", "chat"],
                          help="Source channel for the fragment")
    add_parser.add_argument("--content", required=True, help="Fragment content text")
    
    # list
    list_parser = subparsers.add_parser("list", help="List fragments for an interview")
    list_parser.add_argument("task_id", help="Task ID")
    
    # synthesize
    synth_parser = subparsers.add_parser("synthesize", help="Synthesize fragments for judgment")
    synth_parser.add_argument("task_id", help="Task ID")
    
    # mark-seeded
    seed_parser = subparsers.add_parser("mark-seeded", help="Mark interview as seeded")
    seed_parser.add_argument("task_id", help="Task ID")
    seed_parser.add_argument("--confidence", type=float, required=True,
                           help="Confidence score (0.0-1.0)")
    seed_parser.add_argument("--missing", default="", 
                           help="Comma-separated list of missing items")
    
    # get-synthesis
    get_synth_parser = subparsers.add_parser("get-synthesis", help="Get synthesis for plan generation")
    get_synth_parser.add_argument("task_id", help="Task ID")
    
    # status
    status_parser = subparsers.add_parser("status", help="Get interview status")
    status_parser.add_argument("task_id", help="Task ID")
    
    # list-all
    list_all_parser = subparsers.add_parser("list-all", help="List all interviews")
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete an interview")
    delete_parser.add_argument("task_id", help="Task ID")
    delete_parser.add_argument("--force", action="store_true",
                             help="Force delete even if seeded")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_interview(args.task_id)
    elif args.command == "add":
        add_fragment(args.task_id, args.channel, args.content)
    elif args.command == "list":
        list_fragments(args.task_id)
    elif args.command == "synthesize":
        synthesize(args.task_id)
    elif args.command == "mark-seeded":
        missing = [m.strip() for m in args.missing.split(",") if m.strip()]
        mark_seeded(args.task_id, {
            "seeded": True, 
            "confidence": args.confidence, 
            "missing": missing
        })
    elif args.command == "get-synthesis":
        get_synthesis(args.task_id)
    elif args.command == "status":
        get_status(args.task_id)
    elif args.command == "list-all":
        list_interviews()
    elif args.command == "delete":
        delete_interview(args.task_id, args.force)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
