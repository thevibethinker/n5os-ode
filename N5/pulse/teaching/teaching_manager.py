#!/usr/bin/env python3
"""
Orchestrate VibeTeacher activations at HITL checkpoints.
Teaching moments are non-blocking and stored for later review.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

PULSE_DIR = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(PULSE_DIR))

from teaching.moment_generator import (
    generate_moment,
    mark_absorbed,
    load_glossary,
    save_glossary
)

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"

ACTIVATION_POINTS = [
    "interview_complete",  # After seeded judgment
    "plan_review",         # When V reviews plan
    "feedback",            # When V provides feedback
    "build_complete"       # Final review
]


def _get_moments_file(slug: str) -> Path:
    """Get path to teaching moments file for a build."""
    return BUILDS_DIR / slug / "teaching_moments.jsonl"


def _load_moments(slug: str) -> List[Dict[str, Any]]:
    """Load teaching moments for a build."""
    moments_file = _get_moments_file(slug)
    if not moments_file.exists():
        return []

    moments = []
    with open(moments_file, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    moments.append(json.loads(line))
                except:
                    pass
    return moments


def _save_moment(slug: str, moment: Dict[str, Any]):
    """Append a moment to moments file."""
    moments_file = _get_moments_file(slug)
    moments_file.parent.mkdir(parents=True, exist_ok=True)

    moment_id = f"tm-{uuid.uuid4().hex[:8]}"
    moment_record = {
        "id": moment_id,
        "checkpoint": moment.get("checkpoint", "unknown"),
        "moment": moment.get("teaching"),
        "acknowledged": False,
        "absorbed": False,
        "created_at": datetime.now().isoformat(),
        "matched_term": moment.get("matched_term")
    }

    with open(moments_file, 'a') as f:
        f.write(json.dumps(moment_record) + '\n')

    return moment_record


def activate_at_checkpoint(
    checkpoint: str,
    slug: str,
    v_input: str = None
) -> Dict[str, Any]:
    """
    Activate VibeTeacher at a checkpoint.

    1. Analyze V's input for teaching opportunities
    2. Generate moment if found
    3. Store for later review (non-blocking)
    4. Return moment for display

    Returns:
    {
        "activated": bool,
        "moment_id": str or None,
        "teaching": {...} or None,
        "checkpoint": str
    }
    """
    if checkpoint not in ACTIVATION_POINTS:
        return {
            "activated": False,
            "moment_id": None,
            "teaching": None,
            "checkpoint": checkpoint,
            "error": f"Unknown checkpoint: {checkpoint}"
        }

    if not v_input:
        return {
            "activated": False,
            "moment_id": None,
            "teaching": None,
            "checkpoint": checkpoint,
            "note": "No input to analyze"
        }

    # Generate teaching moment
    moment_result = generate_moment(
        context=checkpoint,
        v_input=v_input,
        checkpoint=checkpoint
    )

    if not moment_result["has_moment"]:
        return {
            "activated": False,
            "moment_id": None,
            "teaching": None,
            "checkpoint": checkpoint,
            "note": "No teaching moment detected"
        }

    # Store moment (non-blocking)
    moment_record = _save_moment(slug, {
        "checkpoint": checkpoint,
        "teaching": moment_result["teaching"],
        "matched_term": moment_result["teaching"].get("precise_term")
    })

    # Update glossary if there's an update
    if moment_result.get("glossary_update"):
        glossary = moment_result["glossary_update"]
        save_glossary(glossary)

    return {
        "activated": True,
        "moment_id": moment_record["id"],
        "teaching": moment_result["teaching"],
        "checkpoint": checkpoint
    }


def get_pending_moments(slug: str) -> List[Dict[str, Any]]:
    """Get teaching moments that haven't been acknowledged."""
    moments = _load_moments(slug)

    pending = [
        moment for moment in moments
        if not moment.get("acknowledged", False)
    ]

    return pending


def acknowledge_moment(moment_id: str, absorbed: bool = False) -> Dict[str, Any]:
    """
    Acknowledge a teaching moment.
    absorbed=True marks term as learned.
    """
    # Find moment across all builds (inefficient but works for now)
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue

        moments_file = build_dir / "teaching_moments.jsonl"
        if not moments_file.exists():
            continue

        moments = []
        with open(moments_file) as f:
            for line in f:
                if line.strip():
                    moments.append(json.loads(line))

        # Find and update moment
        updated = False
        for moment in moments:
            if moment.get("id") == moment_id:
                moment["acknowledged"] = True
                if absorbed:
                    moment["absorbed"] = True

                    # Also mark in glossary
                    matched_term = moment.get("matched_term")
                    if matched_term:
                        mark_absorbed(matched_term)

                updated = True
                break

        if updated:
            # Rewrite file
            with open(moments_file, "w") as f:
                for moment in moments:
                    f.write(json.dumps(moment) + "\n")

            return {
                "success": True,
                "moment_id": moment_id,
                "acknowledged": True,
                "absorbed": absorbed
            }

    return {
        "success": False,
        "error": f"Moment {moment_id} not found"
    }


def get_all_moments(slug: str) -> List[Dict[str, Any]]:
    """Get all teaching moments for a build."""
    return _load_moments(slug)


def get_pending_for_sms() -> str:
    """
    Get summary of pending teaching moments for SMS display.

    Returns formatted text for SMS.
    """
    # Get most recent build with moments
    most_recent_build = None
    most_recent_time = None

    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue

        moments_file = build_dir / "teaching_moments.jsonl"
        if not moments_file.exists():
            continue

        # Check if has unacknowledged moments
        moments = _load_moments(build_dir.name)
        unack = [m for m in moments if not m.get("acknowledged", False)]

        if unack:
            # Get most recent moment
            for moment in unack:
                created_at = moment.get("created_at", "")
                if created_at > (most_recent_time or ""):
                    most_recent_time = created_at
                    most_recent_build = build_dir.name

    if not most_recent_build:
        return "✓ No pending teaching moments."

    # Build summary
    moments = _load_moments(most_recent_build)
    unack = [m for m in moments if not m.get("acknowledged", False)]

    # Load meta for title
    meta_path = BUILDS_DIR / most_recent_build / "meta.json"
    title = most_recent_build
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        title = meta.get("title", most_recent_build)

    summary = f"📚 Teaching moments from build \"{title}\":\n\n"
    for i, moment in enumerate(unack[:5], 1):  # Show top 5
        teaching = moment.get("moment", {})
        term = teaching.get("precise_term", "Unknown term")
        summary += f"{i}. {term}\n"

    if len(unack) > 5:
        summary += f"\n... and {len(unack) - 5} more\n"

    summary += "\nReply \"absorbed: <term>\" to mark as learned."

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Teaching Manager for VibeTeacher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # activate
    activate_parser = subparsers.add_parser("activate", help="Activate at checkpoint")
    activate_parser.add_argument("--checkpoint", required=True, choices=ACTIVATION_POINTS)
    activate_parser.add_argument("--slug", required=True, help="Build slug")
    activate_parser.add_argument("--input", help="V's input text")

    # pending
    pending_parser = subparsers.add_parser("pending", help="Get pending moments")
    pending_parser.add_argument("--slug", required=True, help="Build slug")

    # acknowledge
    ack_parser = subparsers.add_parser("acknowledge", help="Acknowledge a moment")
    ack_parser.add_argument("--moment-id", required=True, help="Moment ID")
    ack_parser.add_argument("--absorbed", action="store_true", help="Mark as absorbed")

    # sms-summary
    sms_parser = subparsers.add_parser("sms-summary", help="Get SMS summary")

    args = parser.parse_args()

    if args.command == "activate":
        result = activate_at_checkpoint(args.checkpoint, args.slug, args.input)
        print(json.dumps(result, indent=2))

    elif args.command == "pending":
        moments = get_pending_moments(args.slug)
        print(json.dumps(moments, indent=2))

    elif args.command == "acknowledge":
        result = acknowledge_moment(args.moment_id, args.absorbed)
        print(json.dumps(result, indent=2))

    elif args.command == "sms-summary":
        summary = get_pending_for_sms()
        print(summary)


if __name__ == "__main__":
    main()
