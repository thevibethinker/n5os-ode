#!/usr/bin/env python3
"""
Content Type Classifier — Determines meeting vs reflection for intake items.

Usage:
    python3 classifier.py Personal/Inbox/<folder>/                    # Classify one item
    python3 classifier.py --batch Personal/Inbox/                     # Classify all unclassified
    python3 classifier.py --batch --dry-run Personal/Inbox/           # Preview batch
    python3 classifier.py --reclassify Personal/Inbox/<folder>/ --type meeting --reason "2 participants found"

Classification priority:
1. Source default (Fireflies/Fathom → always meeting)
2. Speaker count (1 → reflection, 2+ → meeting)
3. Duration heuristic (short multi-speaker → reflection)
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def count_speakers_from_jsonl(transcript_jsonl_path: Path) -> int:
    """Count unique speakers from transcript.jsonl."""
    speakers = set()
    try:
        for line in transcript_jsonl_path.read_text().strip().split("\n"):
            if line.strip():
                entry = json.loads(line)
                speaker = entry.get("speaker", "").strip()
                if speaker:
                    speakers.add(speaker)
    except (json.JSONDecodeError, FileNotFoundError):
        return 0
    return len(speakers)


def count_speakers_from_md(transcript_md_path: Path) -> int:
    """Count unique speakers from transcript.md using speaker label patterns."""
    speakers = set()
    try:
        text = transcript_md_path.read_text()
        # Match patterns like "**Speaker Name:**" or "Speaker Name:" at line start
        patterns = [
            r"^\*\*([^*]+)\*\*:", # **Name:**
            r"^([A-Z][a-zA-Z\s]+):",  # Name: (at line start, capitalized)
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                name = match.group(1).strip()
                if name and len(name) < 50:  # Sanity check
                    speakers.add(name)
        # If first pattern found speakers, use those (more reliable)
        if speakers:
            return len(speakers)
        # Fallback: look for "Speaker N" patterns
        for match in re.finditer(r"Speaker\s+(\d+)", text):
            speakers.add(f"Speaker {match.group(1)}")
    except FileNotFoundError:
        return 0
    return len(speakers)


def classify(manifest: dict, folder_path: Path) -> dict:
    """Classify an intake item as meeting or reflection.

    Returns classification dict with content_type, confidence, method, signals.
    """
    source_type = manifest.get("source", {}).get("type", "manual")

    # Rule 1: Source default for Fireflies/Fathom
    if source_type in ("fireflies", "fathom"):
        return {
            "content_type": "meeting",
            "confidence": 1.0,
            "method": "source_default",
            "signals": [f"Source type '{source_type}' always produces meetings"],
            "speaker_count": None,
            "duration_seconds": None,
        }

    # Get speaker count
    speaker_count = 0
    jsonl_path = folder_path / "transcript.jsonl"
    md_path = folder_path / "transcript.md"

    if jsonl_path.exists():
        speaker_count = count_speakers_from_jsonl(jsonl_path)
    elif md_path.exists():
        speaker_count = count_speakers_from_md(md_path)

    # Get duration from existing classification or content
    duration = manifest.get("classification", {}).get("duration_seconds")
    if duration is None:
        duration = 0

    # Rule 2: Speaker count classification (same as pocket_adapter DP-2 rules)
    if speaker_count <= 1:
        return {
            "content_type": "reflection",
            "confidence": 0.9,
            "method": "speaker_count",
            "signals": [f"{speaker_count} speaker(s) detected"],
            "speaker_count": speaker_count,
            "duration_seconds": duration,
        }
    elif duration > 300:
        return {
            "content_type": "meeting",
            "confidence": 0.85,
            "method": "speaker_count",
            "signals": [
                f"{speaker_count} distinct speakers",
                f"duration {duration}s > 300s threshold",
            ],
            "speaker_count": speaker_count,
            "duration_seconds": duration,
        }
    else:
        return {
            "content_type": "reflection",
            "confidence": 0.6,
            "method": "speaker_count",
            "signals": [
                f"{speaker_count} speakers but short duration ({duration}s <= 300s)",
                "flagged for review",
            ],
            "speaker_count": speaker_count,
            "duration_seconds": duration,
        }


def classify_folder(folder_path: Path, dry_run: bool = False) -> dict:
    """Classify a single intake folder."""
    manifest_path = folder_path / "manifest.json"
    if not manifest_path.exists():
        return {"status": "error", "error": f"No manifest.json in {folder_path}"}

    manifest = json.loads(manifest_path.read_text())

    # Skip if already classified (unless unclassified)
    if manifest.get("status") not in ("landed", "classified") and manifest.get("content_type") != "unclassified":
        # Already past classification — check if re-classification needed
        existing_class = manifest.get("classification", {})
        if existing_class and existing_class.get("content_type"):
            return {
                "status": "skipped",
                "reason": f"Already classified as {existing_class['content_type']}",
                "folder": folder_path.name,
            }

    result = classify(manifest, folder_path)

    if dry_run:
        print(f"[DRY RUN] {folder_path.name}: {result['content_type']} (confidence: {result['confidence']}, method: {result['method']})")
        return {"status": "dry_run", "classification": result, "folder": folder_path.name}

    # Update manifest
    manifest["classification"] = result
    manifest["content_type"] = result["content_type"]
    if manifest.get("status") == "landed":
        manifest["status"] = "classified"
    manifest.setdefault("timestamps", {})["classified_at"] = datetime.now(timezone.utc).isoformat()

    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Classified {folder_path.name}: {result['content_type']} (confidence: {result['confidence']})")

    return {"status": "classified", "classification": result, "folder": folder_path.name}


def reclassify_folder(folder_path: Path, new_type: str, reason: str) -> dict:
    """Manually reclassify an item (DP-6 resolution)."""
    manifest_path = folder_path / "manifest.json"
    if not manifest_path.exists():
        return {"status": "error", "error": f"No manifest.json in {folder_path}"}

    manifest = json.loads(manifest_path.read_text())

    old_type = manifest.get("content_type", "unknown")
    manifest["content_type"] = new_type
    manifest["classification"] = {
        "content_type": new_type,
        "confidence": 1.0,
        "method": "manual",
        "signals": [f"Manual reclassification from '{old_type}': {reason}"],
        "speaker_count": manifest.get("classification", {}).get("speaker_count"),
        "duration_seconds": manifest.get("classification", {}).get("duration_seconds"),
    }
    manifest.setdefault("timestamps", {})["classified_at"] = datetime.now(timezone.utc).isoformat()

    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Reclassified {folder_path.name}: {old_type} → {new_type} (reason: {reason})")

    return {"status": "reclassified", "old_type": old_type, "new_type": new_type, "folder": folder_path.name}


def batch_classify(inbox_path: Path, dry_run: bool = False) -> dict:
    """Classify all unclassified items in inbox."""
    if not inbox_path.exists():
        return {"status": "error", "error": f"Inbox not found: {inbox_path}"}

    classified = 0
    skipped = 0
    errors = 0

    for item in sorted(inbox_path.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue
        manifest_path = item / "manifest.json"
        if not manifest_path.exists():
            continue

        result = classify_folder(item, dry_run=dry_run)
        if result["status"] in ("classified", "dry_run"):
            classified += 1
        elif result["status"] == "skipped":
            skipped += 1
        else:
            errors += 1

    print(f"\nBatch complete: {classified} classified, {skipped} skipped, {errors} errors")
    return {"classified": classified, "skipped": skipped, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Content type classifier for intake items")
    parser.add_argument("path", type=Path, help="Inbox item folder or inbox directory (with --batch)")
    parser.add_argument("--batch", action="store_true", help="Process all unclassified items in directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing changes")
    parser.add_argument("--reclassify", action="store_true", help="Manually reclassify an item")
    parser.add_argument("--type", choices=["meeting", "reflection"], help="New content type (with --reclassify)")
    parser.add_argument("--reason", type=str, help="Reason for reclassification")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.reclassify:
        if not args.type or not args.reason:
            parser.error("--reclassify requires --type and --reason")
        result = reclassify_folder(args.path, args.type, args.reason)
    elif args.batch:
        result = batch_classify(args.path, dry_run=args.dry_run)
    else:
        result = classify_folder(args.path, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2))

    if result.get("status") == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
