#!/usr/bin/env python3
"""Mark a processed meeting as C-state by renaming its Inbox folder.

Usage examples:
  python3 N5/scripts/meeting_pipeline/mark_meeting_c_state.py 2025-11-20_laurensalitangmailcom

Behavior:
- Looks in /home/workspace/Personal/Meetings/Inbox
- Finds a single folder whose name starts with the given prefix and ends with _[P] or _[C]
- If it ends with _[P], renames it to _[C]
- If it already ends with _[C], reports and exits with code 0
- If multiple or zero matches are found, prints an error and exits non-zero
"""

import argparse
from pathlib import Path
import sys

INBOX_DIR = Path("/home/workspace/Personal/Meetings/Inbox")


def find_matching_folder(prefix: str) -> Path | None:
    if not INBOX_DIR.exists():
        print(f"ERROR: Inbox directory not found: {INBOX_DIR}")
        return None

    candidates = []
    for p in sorted(INBOX_DIR.iterdir()):
        if not p.is_dir():
            continue
        name = p.name
        if not name.startswith(prefix):
            continue
        if name.endswith("_[P]") or name.endswith("_[C]"):
            candidates.append(p)

    if not candidates:
        print(f"ERROR: No matching [P]/[C] meeting folder found in Inbox for prefix: {prefix}")
        return None

    if len(candidates) > 1:
        print("ERROR: Multiple matching folders found for prefix. Be more specific:")
        for c in candidates:
            print(f"  - {c.name}")
        return None

    return candidates[0]


def mark_c_state(prefix: str) -> int:
    folder = find_matching_folder(prefix)
    if folder is None:
        return 1

    name = folder.name
    if name.endswith("_[C]"):
        print(f"Already in C-state: {name}")
        return 0

    if not name.endswith("_[P]"):
        print(f"ERROR: Folder does not end with _[P] or _[C]: {name}")
        return 1

    new_name = name[:-3] + "[C]"  # replace trailing [P] with [C]
    new_path = folder.with_name(new_name)

    if new_path.exists():
        print(f"ERROR: Target C-state folder already exists: {new_path.name}")
        return 1

    folder.rename(new_path)
    print(f"Renamed: {name} → {new_path.name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mark a processed meeting as C-state (_[C]) in Inbox.")
    parser.add_argument("prefix", help="Meeting ID prefix, e.g. 2025-11-20_laurensalitangmailcom")
    args = parser.parse_args()

    return mark_c_state(args.prefix)


if __name__ == "__main__":
    raise SystemExit(main())

