#!/usr/bin/env python3
"""
Final teaching review at build close.
Summarizes all teaching moments and updates glossary.

Usage:
    python3 N5/pulse/teaching/build_review.py generate <slug>
    python3 N5/pulse/teaching/build_review.py mark-complete <slug>
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timezone

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"


def get_moments_path(slug: str) -> Path:
    """Get path to teaching moments file for a build."""
    return BUILDS_DIR / slug / "teaching_moments.jsonl"


def load_moments(slug: str) -> List[Dict]:
    """Load all teaching moments for a build."""
    moments_path = get_moments_path(slug)
    moments = []

    if moments_path.exists():
        with open(moments_path) as f:
            for line in f:
                if line.strip():
                    try:
                        moments.append(json.loads(line))
                    except:
                        pass

    return moments


def generate_build_teaching_summary(slug: str) -> Dict:
    """
    Generate summary of all teaching moments from this build.

    Returns:
    {
        "total_moments": 3,
        "new_terms_introduced": ["MECE", "decomposition"],
        "unabsorbed_terms": [...],
        "acknowledged_count": 2,
        "absorbed_count": 1,
        "summary_text": "..."
    }
    """
    moments = load_moments(slug)

    # Load meta for build title
    meta_path = BUILDS_DIR / slug / "meta.json"
    title = slug
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        title = meta.get("title", slug)

    # Analyze moments
    total = len(moments)
    acknowledged = sum(1 for m in moments if m.get("acknowledged", False))
    absorbed = sum(1 for m in moments if m.get("absorbed", False))
    unacknowledged = [m for m in moments if not m.get("acknowledged", False)]

    # Extract unique terms
    unique_terms = set()
    for moment in moments:
        teaching = moment.get("moment", {})
        term = teaching.get("precise_term", "")
        if term:
            unique_terms.add(term)

    # Generate SMS-friendly summary
    if len(unacknowledged) > 0:
        summary_lines = [f"📚 Teaching moments from build \"{title}\":\n"]
        for i, moment in enumerate(unacknowledged[:3], 1):  # Show top 3
            teaching = moment.get("moment", {})
            term = teaching.get("precise_term", "Unknown term")
            summary_lines.append(f"{i}. {term}")

        if len(unacknowledged) > 3:
            summary_lines.append(f"\n... and {len(unacknowledged) - 3} more")

        summary_lines.append("\nReply \"teach\" for a review or \"absorbed: <term>\" to mark as learned.")
        summary_text = "\n".join(summary_lines)
    else:
        summary_text = f"✓ No unacknowledged teaching moments from build \"{title}\"."

    return {
        "slug": slug,
        "title": title,
        "total_moments": total,
        "new_terms_introduced": list(unique_terms),
        "acknowledged_count": acknowledged,
        "absorbed_count": absorbed,
        "unabsorbed_terms": unacknowledged,
        "summary_text": summary_text
    }


def mark_build_teaching_complete(slug: str) -> Dict:
    """
    Mark all moments as reviewed (not necessarily absorbed).
    This acknowledges receipt, not comprehension.
    """
    moments = load_moments(slug)
    moments_path = get_moments_path(slug)

    if not moments:
        return {
            "success": False,
            "error": f"No teaching moments found for build {slug}"
        }

    updated_count = 0
    updated_moments = []

    for moment in moments:
        if not moment.get("acknowledged", False):
            moment["acknowledged"] = True
            moment["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
            updated_count += 1
        updated_moments.append(moment)

    # Rewrite file
    with open(moments_path, "w") as f:
        for moment in updated_moments:
            f.write(json.dumps(moment) + "\n")

    return {
        "success": True,
        "slug": slug,
        "acknowledged": updated_count,
        "total": len(moments)
    }


def get_pending_teaching_for_sms() -> str:
    """
    Get SMS-friendly summary of pending teaching moments.

    Used by SMS handler when V texts "teach".
    """
    # Find most recent build with unacknowledged moments
    most_recent_build = None
    most_recent_time = None

    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue

        moments_path = build_dir / "teaching_moments.jsonl"
        if not moments_path.exists():
            continue

        # Check if has unacknowledged moments
        moments = load_moments(build_dir.name)
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

    # Generate summary
    summary = generate_build_teaching_summary(most_recent_build)
    return summary.get("summary_text", "No teaching moments available.")


def mark_term_absorbed(term: str) -> Dict:
    """
    Mark a specific term as absorbed (V demonstrated understanding).

    Args:
        term: The term name (e.g., "MECE", "Pulse Drop")

    Returns:
        dict with operation result
    """
    # Update glossary
    from .moment_generator import mark_absorbed as mg_mark_absorbed
    glossary_result = mg_mark_absorbed(term)

    if not glossary_result.get("success"):
        return glossary_result

    # Also update in moments files
    updated_count = 0
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue

        moments_path = build_dir / "teaching_moments.jsonl"
        if not moments_path.exists():
            continue

        moments = load_moments(build_dir.name)
        updated_moments = []

        for moment in moments:
            teaching = moment.get("moment", {})
            precise_term = teaching.get("precise_term", "")

            # Match term (case-insensitive)
            if precise_term.lower() == term.lower() and not moment.get("absorbed", False):
                moment["absorbed"] = True
                moment["absorbed_at"] = datetime.now(timezone.utc).isoformat()
                updated_count += 1

            updated_moments.append(moment)

        # Rewrite file
        with open(moments_path, "w") as f:
            for moment in updated_moments:
                f.write(json.dumps(moment) + "\n")

    return {
        "success": True,
        "term": term,
        "glossary_updated": glossary_result.get("success"),
        "moments_updated": updated_count,
        "message": f"✓ Marked '{term}' as absorbed"
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Build teaching review for Pulse v2",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate teaching summary")
    gen_parser.add_argument("slug", help="Build slug")

    # mark-complete
    complete_parser = subparsers.add_parser("mark-complete", help="Mark all moments as acknowledged")
    complete_parser.add_argument("slug", help="Build slug")

    # sms-summary
    sms_parser = subparsers.add_parser("sms-summary", help="Get SMS-friendly summary")

    # absorb
    absorb_parser = subparsers.add_parser("absorb", help="Mark term as absorbed")
    absorb_parser.add_argument("term", help="Term name")

    args = parser.parse_args()

    if args.command == "generate":
        result = generate_build_teaching_summary(args.slug)
        print(json.dumps(result, indent=2))

    elif args.command == "mark-complete":
        result = mark_build_teaching_complete(args.slug)
        print(json.dumps(result, indent=2))

    elif args.command == "sms-summary":
        summary = get_pending_teaching_for_sms()
        print(summary)

    elif args.command == "absorb":
        result = mark_term_absorbed(args.term)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
