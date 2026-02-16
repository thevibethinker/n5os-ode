#!/usr/bin/env python3
"""
Trusted third-party read-only bundle preflight checks.

Checks:
- Branch safety (block main by default)
- Required files exist
- Forbidden/high-risk files are not part of the bundle
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "Skills/pulse/SKILL.md",
    "Skills/pulse/scripts/pulse.py",
    "N5/prefs/operations/scheduled-task-protocol.md",
    "N5/prefs/system/persona_routing_contract.md",
    "N5/scripts/session_state_manager.py",
    "N5/scripts/conversation_registry.py",
    "N5/scripts/conversation_sync.py",
    "N5/config/architectural_prefs_active.json",
    "Prompts/Close Conversation.prompt.md",
]

FORBIDDEN_PREFIXES = [
    ".secrets/",
    "Trash/",
    "N5/data/",
    "Personal/",
]


def current_branch(repo: Path) -> str:
    head = repo / ".git" / "HEAD"
    if not head.exists():
        return "unknown"
    text = head.read_text().strip()
    if text.startswith("ref: refs/heads/"):
        return text.replace("ref: refs/heads/", "", 1)
    return "detached"


def main() -> int:
    parser = argparse.ArgumentParser(description="Trusted third-party preflight")
    parser.add_argument("--repo-path", default=".", help="Path to n5os-ode checkout")
    parser.add_argument("--allow-main", action="store_true", help="Allow main branch")
    parser.add_argument(
        "--bundle-path",
        action="append",
        default=[],
        help="Explicit bundle path to verify against forbidden prefixes (repeatable)",
    )
    args = parser.parse_args()

    repo = Path(args.repo_path).resolve()
    if not (repo / ".git").exists():
        print(f"FAIL: not a git checkout: {repo}")
        return 1

    branch = current_branch(repo)
    print(f"Branch: {branch}")
    if branch == "main" and not args.allow_main:
        print("FAIL: branch is main (use feature/<slug>)")
        return 1

    missing = [p for p in REQUIRED_PATHS if not (repo / p).exists()]
    if missing:
        print("FAIL: missing required files:")
        for item in missing:
            print(f"  - {item}")
        return 1

    bad_paths = []
    for path in args.bundle_path:
        raw = Path(path.strip())
        # Normalize to a repo-relative POSIX path so absolute inputs cannot bypass checks.
        if raw.is_absolute():
            try:
                normalized = raw.resolve().relative_to(repo).as_posix()
            except ValueError:
                normalized = raw.resolve().as_posix().lstrip("/")
        else:
            normalized = raw.as_posix().lstrip("./")
        if any(normalized.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            bad_paths.append(normalized)
    if bad_paths:
        print("FAIL: forbidden bundle paths detected:")
        for item in bad_paths:
            print(f"  - {item}")
        return 1

    print("PASS: trusted third-party preflight checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
