#!/usr/bin/env python3
"""Lightweight smoke tests for stakeholder_intel viewer.

Read-only checks to verify that:
- The stakeholder_intel script runs for a known person_id (if present)
- The script handles missing people and bogus meeting IDs gracefully

This is for manual / CI-style health checks only; it never writes to CRM or DBs.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

WORKSPACE = Path("/home/workspace")
SCRIPT = WORKSPACE / "N5/scripts/stakeholder_intel.py"


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(WORKSPACE))
    print("exit:", proc.returncode)
    print("-" * 60)
    return proc.returncode


def main() -> None:
    # 1) Basic existence check
    if not SCRIPT.exists():
        print("❌ stakeholder_intel.py not found at", SCRIPT)
        raise SystemExit(1)

    # 2) Known-good person slug (if present)
    known_slug = "lauren-salitan"
    crm_file = WORKSPACE / f"Personal/Knowledge/CRM/individuals/{known_slug}.md"
    if crm_file.exists():
        run(["python3", str(SCRIPT), "--person-id", known_slug])
    else:
        print(f"⚠️ CRM file for {known_slug} not found, skipping positive test")
        print("-" * 60)

    # 3) Negative tests: bogus person + bogus meeting id
    run(["python3", str(SCRIPT), "--person-id", "__nonexistent_person__"])
    run(["python3", str(SCRIPT), "--meeting-id", "__bogus_meeting_id__"])


if __name__ == "__main__":
    main()

