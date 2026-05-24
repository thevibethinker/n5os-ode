#!/usr/bin/env python3
"""
Implementation notes support for Pulse builds.

Workers report structured deviations in their deposit. Pulse records those
reports as immutable JSONL events, then renders a human-readable Markdown view
for the orchestrator.
"""

import argparse
import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pulse_common import PATHS, load_meta

DEVIATION_FIELDS = [
    "plan_deviations",
    "schema_deviations",
    "assumption_changes",
    "scope_deviations",
    "collision_risks",
    "followup_required",
]

FIELD_LABELS = {
    "plan_deviations": "Plan Deviations",
    "schema_deviations": "Schema Deviations",
    "assumption_changes": "Assumption Changes",
    "scope_deviations": "Scope Deviations",
    "collision_risks": "Collision Risks",
    "followup_required": "Follow-up Required",
}

DEVIATION_INSTRUCTIONS = """**IMPLEMENTATION NOTES / DEVIATION LOGGING:**
The orchestrator owns plan updates. Your job is to report deterministic facts and suggestions.

Include these fields in your deposit:
- `files_touched`: exact workspace-relative paths you created or modified.
- `plan_deviations`: changes from the assigned plan, brief, task order, or success criteria.
- `schema_deviations`: changes to expected data shapes, deposit formats, config keys, API contracts, or compatibility behavior.
- `assumption_changes`: assumptions you made, invalidated, or discovered while executing.
- `scope_deviations`: work outside the brief, including extra files touched because the brief was incomplete.
- `collision_risks`: files, interfaces, or decisions likely to conflict with parallel Drops.
- `followup_required`: concrete orchestrator actions needed before later Waves proceed.

Use empty arrays when there are no entries. Do not edit `IMPLEMENTATION_NOTES.md` directly.
Pulse will record your deposit into `implementation_notes.jsonl` and render the Markdown summary.

Examples:
- Plan deviation: "Implemented locked JSONL notes instead of direct Markdown append because concurrent workers can collide."
- Schema deviation: "Added optional `collision_risks[]` to deposits; older deposits remain valid with an empty default."
- Assumption change: "Assumed all target files existed; discovered `wave_debug_review.py` is referenced but missing."
- Scope deviation: "Touched `pulse.py` command routing in addition to the notes module so operators can render notes."
- Collision risk: "D2 and D4 both mention `Skills/pulse/scripts/pulse.py`; orchestrator should sequence router edits."
- Follow-up required: "Review this deviation before spawning Wave 2 because D3 depends on the new deposit fields."
"""


def note_paths(slug: str) -> tuple[Path, Path]:
    build_dir = PATHS.build(slug)
    return build_dir / "implementation_notes.jsonl", build_dir / "IMPLEMENTATION_NOTES.md"


def normalize_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [line.strip("- ").strip() for line in value.splitlines() if line.strip("- ").strip()]
    return [str(value).strip()]


def normalize_deposit(slug: str, drop_id: str, deposit: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    event = {
        "event_id": f"{slug}:{drop_id}:{deposit.get('timestamp') or now}",
        "build_slug": slug,
        "drop_id": drop_id,
        "recorded_at": now,
        "deposit_timestamp": deposit.get("timestamp"),
        "status": deposit.get("status", "unknown"),
        "summary": deposit.get("summary", ""),
        "files_touched": normalize_list(deposit.get("files_touched") or deposit.get("artifacts")),
        "orchestrator_review": deposit.get("orchestrator_review", "pending"),
    }
    for field in DEVIATION_FIELDS:
        event[field] = normalize_list(deposit.get(field))
    return event


def load_events(slug: str) -> list[dict[str, Any]]:
    jsonl_path, _ = note_paths(slug)
    if not jsonl_path.exists():
        return []
    events = []
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                events.append({"error": "invalid_jsonl_line", "raw": line.rstrip("\n")})
    return events


def append_event(slug: str, event: dict[str, Any]) -> bool:
    jsonl_path, _ = note_paths(slug)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    existing_ids = {item.get("event_id") for item in load_events(slug)}
    if event.get("event_id") in existing_ids:
        return False
    with open(jsonl_path, "a+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.seek(0)
        existing_ids = set()
        for line in f:
            if not line.strip():
                continue
            try:
                existing_ids.add(json.loads(line).get("event_id"))
            except json.JSONDecodeError:
                continue
        if event.get("event_id") in existing_ids:
            return False
        f.write(json.dumps(event, sort_keys=True) + "\n")
        f.flush()
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return True


def record_deposit_notes(slug: str, drop_id: str, deposit: dict[str, Any]) -> bool:
    event = normalize_deposit(slug, drop_id, deposit)
    changed = append_event(slug, event)
    render_notes(slug)
    return changed


def render_notes(slug: str) -> Path:
    _, markdown_path = note_paths(slug)
    events = sorted(load_events(slug), key=lambda item: (item.get("drop_id", ""), item.get("recorded_at", "")))
    today = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "---",
        f"created: {today}",
        f"last_edited: {today}",
        "version: 1.0",
        f"provenance: pulse:{slug}",
        "---",
        "",
        f"# Implementation Notes: {slug}",
        "",
        "This file is rendered from `implementation_notes.jsonl`. Do not edit it directly.",
        "Workers propose deviations; the orchestrator reviews and updates future plans centrally.",
        "",
        "## Review Queue",
        "",
    ]

    actionable = [
        event for event in events
        if any(event.get(field) for field in DEVIATION_FIELDS)
        or event.get("orchestrator_review") not in ("accepted", "none")
    ]
    if not actionable:
        lines.append("- No reported deviations or follow-ups yet.")
    else:
        for event in actionable:
            lines.append(f"- `{event.get('drop_id', 'unknown')}`: {event.get('summary') or 'No summary'}")
            for field in DEVIATION_FIELDS:
                values = event.get(field) or []
                if values:
                    lines.append(f"  - {FIELD_LABELS[field]}: {len(values)} item(s)")
    lines.extend(["", "## Drop Notes", ""])

    if not events:
        lines.append("_No implementation notes recorded yet._")
    for event in events:
        lines.extend([
            f"### {event.get('drop_id', 'unknown')}",
            "",
            f"- Status: `{event.get('status', 'unknown')}`",
            f"- Recorded: `{event.get('recorded_at', '')}`",
            f"- Summary: {event.get('summary') or 'No summary'}",
        ])
        files = event.get("files_touched") or []
        lines.append(f"- Files touched: {', '.join(f'`{path}`' for path in files) if files else 'None reported'}")
        for field in DEVIATION_FIELDS:
            values = event.get(field) or []
            lines.append(f"- {FIELD_LABELS[field]}:")
            if values:
                for value in values:
                    lines.append(f"  - {value}")
            else:
                lines.append("  - None")
        lines.append("")

    markdown_path.write_text("\n".join(lines).rstrip() + "\n")
    return markdown_path


def summarize_review(slug: str) -> dict[str, Any]:
    meta = load_meta(slug) or {}
    events = load_events(slug)
    drops = meta.get("drops", {})
    recorded_drops = {event.get("drop_id") for event in events}
    missing = []
    for drop_id, info in drops.items():
        if info.get("status") == "complete" and drop_id not in recorded_drops:
            missing.append(drop_id)
    counts = {field: sum(len(event.get(field) or []) for event in events) for field in DEVIATION_FIELDS}
    return {
        "slug": slug,
        "events": len(events),
        "completed_drops_missing_notes": sorted(missing),
        "counts": counts,
        "requires_orchestrator_review": any(counts.values()) or bool(missing),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pulse implementation notes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="Render IMPLEMENTATION_NOTES.md")
    render_parser.add_argument("slug")

    review_parser = subparsers.add_parser("review", help="Print implementation-note review summary")
    review_parser.add_argument("slug")
    review_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "render":
        path = render_notes(args.slug)
        print(path)
        return 0
    if args.command == "review":
        summary = summarize_review(args.slug)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"Implementation notes: {summary['events']} event(s)")
            print(f"Requires orchestrator review: {summary['requires_orchestrator_review']}")
            if summary["completed_drops_missing_notes"]:
                print("Completed drops missing notes: " + ", ".join(summary["completed_drops_missing_notes"]))
            for field, count in summary["counts"].items():
                print(f"{field}: {count}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
