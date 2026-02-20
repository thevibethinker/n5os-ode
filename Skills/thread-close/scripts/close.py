#!/usr/bin/env python3
"""
Thread close — finalize a normal conversation thread.

Reads SESSION_STATE.md, generates a close summary, and optionally marks the session closed.

Usage:
    python3 close.py --convo-id <conversation_id> [--dry-run]
"""

import argparse
import datetime
import os
import re
import sys


DEFAULT_WORKSPACE_ROOT = "/home/.z/workspaces"


def find_session_state(convo_id: str) -> str | None:
    workspace = os.path.join(DEFAULT_WORKSPACE_ROOT, convo_id)
    path = os.path.join(workspace, "SESSION_STATE.md")
    if os.path.isfile(path):
        return path
    return None


def parse_session_state(path: str) -> dict:
    with open(path, "r") as f:
        content = f.read()

    state: dict = {
        "type": None,
        "status": None,
        "message": None,
        "tasks_completed": [],
        "tasks_remaining": [],
        "artifacts": [],
        "decisions": [],
        "raw": content,
    }

    in_section = None

    for line in content.splitlines():
        stripped = line.strip()

        match = re.match(r"^type:\s*(.+)$", stripped)
        if match:
            state["type"] = match.group(1).strip()
            continue

        match = re.match(r"^status:\s*(.+)$", stripped)
        if match:
            state["status"] = match.group(1).strip()
            continue

        match = re.match(r"^message:\s*(.+)$", stripped)
        if match:
            state["message"] = match.group(1).strip().strip('"').strip("'")
            continue

        if stripped.startswith("## "):
            section_name = stripped[3:].strip().lower()
            if "completed" in section_name or "done" in section_name:
                in_section = "completed"
            elif "remaining" in section_name or "todo" in section_name:
                in_section = "remaining"
            elif "artifact" in section_name:
                in_section = "artifacts"
            elif "decision" in section_name:
                in_section = "decisions"
            else:
                in_section = None
            continue

        if stripped.startswith("- ") and in_section:
            item = stripped[2:].strip()
            item = re.sub(r"^\[[ x]\]\s*", "", item)
            if in_section == "completed":
                state["tasks_completed"].append(item)
            elif in_section == "remaining":
                state["tasks_remaining"].append(item)
            elif in_section == "artifacts":
                state["artifacts"].append(item)
            elif in_section == "decisions":
                state["decisions"].append(item)

    return state


def generate_summary(state: dict, convo_id: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append("=" * 60)
    lines.append("THREAD CLOSE SUMMARY")
    lines.append("=" * 60)
    lines.append(f"Conversation: {convo_id}")
    lines.append(f"Type:         {state.get('type') or 'unknown'}")
    lines.append(f"Closed at:    {now}")
    lines.append("")

    completed = state.get("tasks_completed", [])
    remaining = state.get("tasks_remaining", [])
    total = len(completed) + len(remaining)

    if total > 0:
        pct = int(len(completed) / total * 100)
        lines.append(f"Progress: {len(completed)}/{total} ({pct}%)")
    else:
        lines.append("Progress: No tracked tasks")
    lines.append("")

    if completed:
        lines.append("Completed:")
        for item in completed:
            lines.append(f"  ✓ {item}")
        lines.append("")

    if remaining:
        lines.append("Remaining:")
        for item in remaining:
            lines.append(f"  ○ {item}")
        lines.append("")

    artifacts = state.get("artifacts", [])
    if artifacts:
        lines.append("Artifacts:")
        for item in artifacts:
            lines.append(f"  • {item}")
        lines.append("")

    decisions = state.get("decisions", [])
    if decisions:
        lines.append("Decisions:")
        for item in decisions:
            lines.append(f"  → {item}")
        lines.append("")

    if completed:
        subject = ", ".join(completed[:3])
        if len(completed) > 3:
            subject += f" (+{len(completed) - 3} more)"
        lines.append(f'Suggested commit: "chore: {subject}"')

    lines.append("=" * 60)
    return "\n".join(lines)


def mark_closed(path: str):
    with open(path, "r") as f:
        content = f.read()

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = re.sub(
        r"^status:\s*.+$",
        f"status: closed",
        content,
        flags=re.MULTILINE,
    )

    if "closed_at:" not in content:
        content = re.sub(
            r"^(status:\s*closed)$",
            f"\\1\nclosed_at: {now}",
            content,
            flags=re.MULTILINE,
        )

    with open(path, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Close a normal conversation thread with a structured summary."
    )
    parser.add_argument(
        "--convo-id",
        required=True,
        help="Conversation ID (used to locate the workspace)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the close summary without modifying session state",
    )
    args = parser.parse_args()

    session_path = find_session_state(args.convo_id)

    if not session_path:
        print(f"SESSION_STATE.md not found for conversation {args.convo_id}")
        print("Nothing to close.")
        sys.exit(1)

    state = parse_session_state(session_path)
    summary = generate_summary(state, args.convo_id)

    print(summary)

    if args.dry_run:
        print("\n(dry run — session state not modified)")
    else:
        mark_closed(session_path)
        print(f"\nSession state updated: {session_path}")


if __name__ == "__main__":
    main()
