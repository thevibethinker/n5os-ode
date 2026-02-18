#!/usr/bin/env python3
"""
HITL review manager for Pulse v2.
Handles plan review flow: upload → notify → wait → process response.

Usage:
    python3 N5/pulse/review_manager.py initiate <slug>
    python3 N5/pulse/review_manager.py respond <slug> <response>
    python3 N5/pulse/review_manager.py status <slug>
"""

import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
from availability_checker import is_available, next_available_window

PULSE_DIR = Path(__file__).parent
BUILDS_DIR = Path("/home/workspace/N5/builds")


def run_cmd(cmd: list) -> dict:
    """Run a command and return parsed JSON output."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/workspace")
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stderr or result.stdout, "stdout": result.stdout}


def check_availability() -> dict:
    """Check if V is available for HITL review."""
    try:
        result = subprocess.run(
            ["python3", str(PULSE_DIR / "availability_checker.py"), "check"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"available": True, "reason": "checker_error_default_available"}
    except Exception as e:
        # Fail open - if checker errors, assume available
        return {"available": True, "reason": f"checker_exception: {e}"}


def initiate_review(slug: str, force: bool = False) -> dict:
    """
    Initiate plan review:
    0. Check availability (unless forced)
    1. Sync to Google Drive (best-effort)
    2. Get shareable link
    3. Generate SMS notification
    4. Update status to plan_review
    """
    # NEW: Check availability (unless forced)
    if not force:
        avail_result = check_availability()
        if not avail_result["available"]:
            next_window = next_available_window()
            return {
                "success": False,
                "deferred": True,
                "reason": avail_result.get("reasons", ["V unavailable"]),
                "next_window": next_window.get("suggested_check"),
                "message": f"Review deferred. Next available: {next_window.get('suggested_check', 'unknown')}"
            }
    
    build_dir = BUILDS_DIR / slug
    meta_path = build_dir / "meta.json"
    
    if not meta_path.exists():
        return {"success": False, "error": f"Build not found: {slug}"}
    
    meta = json.loads(meta_path.read_text())
    
    # 1. Try Drive sync (best-effort - may generate instructions only)
    sync_result = run_cmd([
        "python3", str(PULSE_DIR / "outpost_manager.py"), "sync", slug
    ])
    
    link = None
    if sync_result.get("success"):
        # outpost_manager may return instructions, not a direct link
        if "shareable_link" in sync_result:
            link = sync_result["shareable_link"]
        else:
            link = f"(Drive sync available - execute instructions in outpost_manager)"
    else:
        link = f"(Drive sync unavailable - review locally at N5/builds/{slug}/PLAN.md)"
    
    # 2. Load plan to generate SMS summary
    plan_path = build_dir / "PLAN.md"
    plan_content = plan_path.read_text() if plan_path.exists() else ""
    
    # Extract key info
    title = meta.get("title", slug)
    build_type = meta.get("build_type", "unknown")
    drops = meta.get("drops", {})
    drops_count = len(drops)
    
    # Count drops by stream if available
    streams = set()
    for drop_info in drops.values():
        if "stream" in drop_info:
            streams.add(drop_info["stream"])
    streams_count = len(streams) if streams else meta.get("total_streams", "?")
    
    sms_message = f"""📋 Plan ready: "{title}"
Type: {build_type}
Drops: {drops_count} across {streams_count} streams

{link}

Reply:
• "go" or "approve" to build
• "revise: <feedback>" to adjust
• "cancel" to abort"""
    
    # Learning mode: teaching moments handled natively by orchestrator LLM
    
    # 3. Update meta
    meta["status"] = "plan_review"
    meta["review"] = {
        "initiated_at": datetime.now(timezone.utc).isoformat(),
        "link": link,
        "response": None,
        "responded_at": None
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    
    # 4. Update task queue if task_id exists
    task_id = meta.get("task_id")
    if task_id:
        run_cmd([
            "python3", str(PULSE_DIR / "queue_manager.py"),
            "advance", task_id, "plan_review"
        ])
    
    return {
        "success": True,
        "status": "awaiting_review",
        "sms_message": sms_message,
        "link": link,
        "note": "Send SMS to V with the message above"
    }


def process_review_response(slug: str, response: str) -> dict:
    """
    Process V's response to plan review.
    
    Responses:
    - "go", "approve", "yes", "👍" → Advance to building
    - "revise: <feedback>" → Feed back to plan generator
    - "cancel" → Mark task as cancelled
    """
    build_dir = BUILDS_DIR / slug
    meta_path = build_dir / "meta.json"
    
    if not meta_path.exists():
        return {"success": False, "error": f"Build not found: {slug}"}
    
    meta = json.loads(meta_path.read_text())
    response_lower = response.strip().lower()
    
    # Ensure review object exists
    if "review" not in meta:
        meta["review"] = {
            "initiated_at": None,
            "link": None,
            "response": None,
            "responded_at": None
        }
    
    # Record response
    meta["review"]["response"] = response
    meta["review"]["responded_at"] = datetime.now(timezone.utc).isoformat()
    
    # Determine action based on response
    approval_signals = [
        "go", "approve", "approved", "yes", "👍", "lgtm", 
        "ship it", "looks good", "good to go", "proceed"
    ]
    
    if any(signal in response_lower for signal in approval_signals):
        # APPROVED → advance to building
        meta["status"] = "building"
        meta_path.write_text(json.dumps(meta, indent=2))
        
        # Update task queue
        task_id = meta.get("task_id")
        if task_id:
            run_cmd([
                "python3", str(PULSE_DIR / "queue_manager.py"),
                "advance", task_id, "building"
            ])
        
        return {
            "success": True,
            "action": "approved",
            "next_status": "building",
            "message": "Plan approved. Ready to start build."
        }
    
    elif response_lower.startswith("revise:"):
        # REVISION REQUESTED
        feedback = response[7:].strip()
        
        # Store revision history
        if "revision_history" not in meta["review"]:
            meta["review"]["revision_history"] = []
        meta["review"]["revision_history"].append({
            "feedback": feedback,
            "requested_at": datetime.now(timezone.utc).isoformat()
        })
        
        meta["review"]["revision_feedback"] = feedback
        meta["status"] = "planning"  # Back to planning
        meta_path.write_text(json.dumps(meta, indent=2))
        
        # Update task queue
        task_id = meta.get("task_id")
        if task_id:
            run_cmd([
                "python3", str(PULSE_DIR / "queue_manager.py"),
                "advance", task_id, "planning"
            ])
        
        return {
            "success": True,
            "action": "revision_requested",
            "feedback": feedback,
            "next_status": "planning",
            "message": f"Revision requested: {feedback}. Regenerate plan and re-review."
        }
    
    elif response_lower in ["cancel", "abort", "stop"]:
        meta["status"] = "cancelled"
        meta["cancelled_at"] = datetime.now(timezone.utc).isoformat()
        meta_path.write_text(json.dumps(meta, indent=2))
        
        task_id = meta.get("task_id")
        if task_id:
            run_cmd([
                "python3", str(PULSE_DIR / "queue_manager.py"),
                "advance", task_id, "cancelled"
            ])
        
        return {
            "success": True,
            "action": "cancelled",
            "next_status": "cancelled",
            "message": "Build cancelled."
        }
    
    else:
        # Unknown response
        return {
            "success": False,
            "action": "unknown",
            "message": f"Unclear response: '{response}'. Reply 'go' to approve, 'revise: <feedback>' to adjust, or 'cancel' to abort."
        }


def check_review_status(slug: str) -> dict:
    """Check current review status."""
    meta_path = BUILDS_DIR / slug / "meta.json"
    
    if not meta_path.exists():
        return {"success": False, "error": f"Build not found: {slug}"}
    
    meta = json.loads(meta_path.read_text())
    review = meta.get("review", {})
    
    return {
        "success": True,
        "slug": slug,
        "status": meta.get("status"),
        "initiated_at": review.get("initiated_at"),
        "responded_at": review.get("responded_at"),
        "response": review.get("response"),
        "revision_feedback": review.get("revision_feedback"),
        "revision_count": len(review.get("revision_history", [])),
        "awaiting_response": (
            review.get("responded_at") is None and 
            meta.get("status") == "plan_review"
        )
    }


def main():
    parser = argparse.ArgumentParser(
        description="HITL Review Manager for Pulse v2",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # initiate
    init_parser = subparsers.add_parser("initiate", help="Start plan review")
    init_parser.add_argument("slug", help="Build slug")
    init_parser.add_argument("--force", action="store_true", help="Skip availability check")
    
    # respond
    resp_parser = subparsers.add_parser("respond", help="Process review response")
    resp_parser.add_argument("slug", help="Build slug")
    resp_parser.add_argument("response", help="V's response")
    
    # status
    status_parser = subparsers.add_parser("status", help="Check review status")
    status_parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if args.command == "initiate":
        result = initiate_review(args.slug, getattr(args, 'force', False))
    elif args.command == "respond":
        result = process_review_response(args.slug, args.response)
    elif args.command == "status":
        result = check_review_status(args.slug)
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
