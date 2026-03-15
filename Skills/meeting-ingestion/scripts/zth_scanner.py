#!/usr/bin/env python3
"""
Zo Take Heed Scanner — Extracts trigger blocks from transcripts.

Usage:
    python3 zth_scanner.py scan Personal/Inbox/<folder>/               # Scan one item
    python3 zth_scanner.py scan --batch Personal/Inbox/                # Scan all unscanned
    python3 zth_scanner.py scan --dry-run Personal/Inbox/<folder>/     # Preview triggers

Trigger Protocol:
    Open:   "zo take heed" (and phonetic variants)
    Close:  "zo at ease" (and phonetic variants)
    Inline: Single sentence with "zo" + action verb (no explicit open/close)

Only V/Vrijen can trigger ZTH. Other speakers are rejected.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Phonetic variant patterns for open/close phrases
OPEN_PATTERNS = [
    r"zo[\s,]+take[\s]+heed",
    r"zo[\s]*takeheed",
    r"zotakeheed",
    r"so[\s,]+take[\s]+heed",  # Common transcription error
    r"zo[\s,]+take[\s]+heat",  # Common transcription error
]

CLOSE_PATTERNS = [
    r"zo[\s,]+at[\s]+ease",
    r"zo[\s]*atease",
    r"zoatease",
    r"so[\s,]+at[\s]+ease",  # Common transcription error
]

# Inline trigger pattern: "zo" + action verb in same sentence
INLINE_PATTERN = r"(?:^|\.\s+)([^.]*\bzo[\s,]+(?:add|send|draft|write|create|update|research|remind|note|schedule|email|message|contact|follow up|introduce|look into)[^.]*\.?)"

# V/Vrijen speaker name patterns
V_SPEAKER_PATTERNS = [
    r"^v$",
    r"^vrijen",
    r"^vrij$",
    r"^va$",
    r"^speaker\s*0$",  # Often V is Speaker 0 in Pocket
]

# Task type classification keywords
TASK_TYPE_KEYWORDS = {
    "follow_up_email": ["email", "follow up email", "follow-up email", "send email", "draft email", "write email"],
    "warm_intro": ["introduce", "intro", "warm intro", "warm introduction", "connect them"],
    "blurb": ["blurb", "write a blurb", "draft a blurb", "write up"],
    "research": ["research", "look into", "investigate", "find out", "dig into"],
    "list_add": ["add to list", "add to the list", "add this to", "put on the list", "add to research"],
    "deal_add": ["add deal", "new deal", "create deal", "add to deals"],
    "deal_update": ["update deal", "update the deal", "change deal"],
    "crm_contact": ["add contact", "add to crm", "save contact", "new contact"],
    "intro_lead": ["intro lead", "introduction lead", "add to intro"],
    "directive": ["note that", "remember that", "keep in mind", "going forward"],
    "custom": [],  # Fallback
}

# Execution policy by task type
EXECUTION_POLICY = {
    "directive": "inline",
    "blurb": "auto_execute",
    "follow_up_email": "auto_execute",
    "warm_intro": "auto_execute",
    "research": "queue",
    "list_add": "auto_execute",
    "deal_add": "auto_execute",
    "deal_update": "auto_execute",
    "crm_contact": "auto_execute",
    "intro_lead": "auto_execute",
    "custom": "queue",
}


def is_v_speaker(speaker: str) -> bool:
    """Check if speaker is V/Vrijen."""
    speaker_lower = speaker.strip().lower()
    return any(re.match(p, speaker_lower) for p in V_SPEAKER_PATTERNS)


def classify_task_type(instruction: str) -> str:
    """Classify instruction into one of 11 task types."""
    instruction_lower = instruction.lower()
    for task_type, keywords in TASK_TYPE_KEYWORDS.items():
        if task_type == "custom":
            continue
        for keyword in keywords:
            if keyword in instruction_lower:
                return task_type
    return "custom"


def extract_speaker_for_line(text: str, transcript_lines: list[str], line_idx: int) -> Optional[str]:
    """Try to determine the speaker for a given line by looking backwards."""
    def _extract_name(line: str) -> Optional[str]:
        m = re.match(r"^\*\*(.+?)\*\*", line)
        if m:
            return m.group(1).strip().rstrip(":")
        m = re.match(r"^([A-Z][a-zA-Z\s]{1,30}):", line)
        if m:
            return m.group(1).strip()
        return None

    # Check if line itself has a speaker label
    name = _extract_name(text)
    if name:
        return name

    # Look backwards for the most recent speaker label
    for i in range(line_idx - 1, max(-1, line_idx - 21), -1):
        if 0 <= i < len(transcript_lines):
            name = _extract_name(transcript_lines[i])
            if name:
                return name
    return None


def scan_transcript(transcript_text: str, content_date: str = "") -> dict:
    """Scan transcript text for ZTH triggers.

    Returns dict with triggers list and rejections list.
    """
    if not content_date:
        content_date = datetime.now().strftime("%Y%m%d")
    else:
        content_date = content_date.replace("-", "")

    triggers = []
    rejections = []
    trigger_counter = 0
    lines = transcript_text.split("\n")
    full_text = transcript_text

    # Phase 1: Find open/close blocks
    open_regex = re.compile("|".join(OPEN_PATTERNS), re.IGNORECASE)
    close_regex = re.compile("|".join(CLOSE_PATTERNS), re.IGNORECASE)

    open_positions = [(m.start(), m.end()) for m in open_regex.finditer(full_text)]
    close_positions = [(m.start(), m.end()) for m in close_regex.finditer(full_text)]

    used_close_positions = set()
    block_ranges = []  # Track (open_start, block_end) for inline overlap check

    for open_start, open_end in open_positions:
        # Find speaker for this open phrase
        # Get line index
        text_before = full_text[:open_start]
        line_idx = text_before.count("\n")
        line_text = lines[line_idx] if line_idx < len(lines) else ""
        speaker = extract_speaker_for_line(line_text, lines, line_idx)

        # Find the nearest close after this open
        close_end_pos = None
        body_end = None
        for c_start, c_end in close_positions:
            if c_start > open_end and c_start not in used_close_positions:
                body_end = c_start
                close_end_pos = c_end
                used_close_positions.add(c_start)
                break

        # If no close found, treat as unclosed — body extends to next speaker label or 500 chars
        if body_end is None:
            # Find next speaker label after the open phrase
            next_speaker = re.search(r"\n\*\*[^*]+\*\*:", full_text[open_end:])
            if next_speaker:
                body_end = open_end + next_speaker.start()
            else:
                body_end = min(open_end + 500, len(full_text))

        block_ranges.append((open_start, close_end_pos or body_end))

        # Extract body
        body = full_text[open_end:body_end].strip()
        # Clean up speaker labels from body
        body = re.sub(r"^\*\*[^*]+\*\*:\s*", "", body)
        body = re.sub(r"^[A-Z][a-zA-Z\s]{1,30}:\s*", "", body)
        body = body.strip(" ,.")

        if not body:
            continue

        # Speaker validation
        if speaker and not is_v_speaker(speaker):
            rejections.append({
                "raw_cue": full_text[open_start:close_end_pos or (open_end + len(body))].strip(),
                "speaker": speaker,
                "reason": f"Speaker '{speaker}' is not V/Vrijen",
            })
            continue

        trigger_counter += 1
        task_type = classify_task_type(body)

        triggers.append({
            "id": f"ZTH-{content_date}-{trigger_counter:03d}",
            "raw_cue": full_text[open_start:close_end_pos or (open_end + len(body) + 10)].strip()[:500],
            "instruction": body[:500],
            "task_type": task_type,
            "execution_policy": EXECUTION_POLICY.get(task_type, "queue"),
            "status": "pending",
            "executed_at": None,
            "execution_result": None,
            "block_type": "open_close",
        })

    # Phase 2: Find inline triggers (not already captured in open/close blocks)
    inline_regex = re.compile(INLINE_PATTERN, re.IGNORECASE | re.MULTILINE)
    for match in inline_regex.finditer(full_text):
        sentence = match.group(1).strip()
        match_start = match.start()

        # Skip if this overlaps with an open/close block
        in_block = False
        for block_start, block_end in block_ranges:
            if block_start <= match_start <= block_end:
                in_block = True
                break
        if in_block:
            continue

        # Get speaker
        text_before = full_text[:match_start]
        line_idx = text_before.count("\n")
        line_text = lines[line_idx] if line_idx < len(lines) else ""
        speaker = extract_speaker_for_line(line_text, lines, line_idx)

        if speaker and not is_v_speaker(speaker):
            rejections.append({
                "raw_cue": sentence[:200],
                "speaker": speaker,
                "reason": f"Speaker '{speaker}' is not V/Vrijen",
            })
            continue

        # Extract instruction (remove the "zo, " prefix)
        instruction = re.sub(r"^.*?\bzo[\s,]+", "", sentence, flags=re.IGNORECASE).strip()
        if not instruction:
            continue

        trigger_counter += 1
        task_type = classify_task_type(instruction)

        triggers.append({
            "id": f"ZTH-{content_date}-{trigger_counter:03d}",
            "raw_cue": sentence[:500],
            "instruction": instruction[:500],
            "task_type": task_type,
            "execution_policy": EXECUTION_POLICY.get(task_type, "queue"),
            "status": "pending",
            "executed_at": None,
            "execution_result": None,
            "block_type": "inline",
        })

    return {"triggers": triggers, "rejections": rejections}


def scan_folder(folder_path: Path, dry_run: bool = False) -> dict:
    """Scan an intake folder for ZTH triggers and update manifest."""
    manifest_path = folder_path / "manifest.json"
    if not manifest_path.exists():
        return {"status": "error", "error": f"No manifest.json in {folder_path}"}

    manifest = json.loads(manifest_path.read_text())

    # Check if already scanned
    zth = manifest.get("zo_take_heed", {})
    if zth.get("scanned") and manifest.get("status") == "heed_scanned":
        return {"status": "skipped", "reason": "Already scanned", "folder": folder_path.name}

    # Read transcript
    transcript_path = folder_path / "transcript.md"
    if not transcript_path.exists():
        return {"status": "error", "error": f"No transcript.md in {folder_path}"}

    transcript_text = transcript_path.read_text()
    content_date = manifest.get("content", {}).get("date", "")

    result = scan_transcript(transcript_text, content_date)
    triggers = result["triggers"]
    rejections = result["rejections"]

    if dry_run:
        print(f"[DRY RUN] {folder_path.name}: {len(triggers)} trigger(s) found, {len(rejections)} rejected")
        for t in triggers:
            print(f"  [{t['task_type']}] {t['instruction'][:80]}")
        for r in rejections:
            print(f"  [REJECTED] Speaker '{r['speaker']}': {r['raw_cue'][:60]}")
        return {
            "status": "dry_run",
            "triggers_found": len(triggers),
            "rejections": len(rejections),
            "triggers": triggers,
        }

    # Remove block_type from triggers before storing in manifest (not in schema)
    manifest_actions = []
    for t in triggers:
        action = {k: v for k, v in t.items() if k != "block_type"}
        manifest_actions.append(action)

    # Update manifest
    manifest["zo_take_heed"] = {
        "scanned": True,
        "triggers_found": len(triggers),
        "actions": manifest_actions,
    }
    manifest["status"] = "heed_scanned"
    manifest.setdefault("timestamps", {})["heed_scanned_at"] = datetime.now(timezone.utc).isoformat()

    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Scanned {folder_path.name}: {len(triggers)} trigger(s), {len(rejections)} rejected")

    return {
        "status": "scanned",
        "triggers_found": len(triggers),
        "rejections": len(rejections),
        "triggers": triggers,
        "folder": folder_path.name,
    }


def batch_scan(inbox_path: Path, dry_run: bool = False) -> dict:
    """Scan all unscanned items in inbox."""
    if not inbox_path.exists():
        return {"status": "error", "error": f"Inbox not found: {inbox_path}"}

    scanned = 0
    skipped = 0
    total_triggers = 0

    for item in sorted(inbox_path.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue
        if not (item / "manifest.json").exists():
            continue

        result = scan_folder(item, dry_run=dry_run)
        if result["status"] in ("scanned", "dry_run"):
            scanned += 1
            total_triggers += result.get("triggers_found", 0)
        else:
            skipped += 1

    print(f"\nBatch complete: {scanned} scanned, {skipped} skipped, {total_triggers} total triggers")
    return {"scanned": scanned, "skipped": skipped, "total_triggers": total_triggers}


def main():
    parser = argparse.ArgumentParser(description="Zo Take Heed Scanner")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan for ZTH triggers")
    scan_parser.add_argument("path", type=Path, help="Folder or inbox directory (with --batch)")
    scan_parser.add_argument("--batch", action="store_true", help="Scan all unscanned items")
    scan_parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    scan_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.batch:
        result = batch_scan(args.path, dry_run=args.dry_run)
    else:
        result = scan_folder(args.path, dry_run=args.dry_run)

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2, default=str))

    if result.get("status") == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
