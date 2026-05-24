#!/usr/bin/env python3
"""
Classify whether the current Git context should stay on main, use a branch,
or use a separate worktree.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

BRANCH_REQUIRED_PREFIXES = (
    "N5/scripts/",
    "N5/lib/",
    "Skills/",
    "Sites/",
    "Integrations/",
    "Prompts/",
)

MAIN_OK_PREFIXES = (
    "N5/builds/",
    "Research/",
    "Personal/Meetings/",
    "Documents/",
    "Knowledge/content-library/",
    "Articles/",
)

RUNTIME_PREFIXES = (
    "N5/data/",
    "Skills/codebase-graph/data/",
    "Skills/sentience-sync/data/",
)


@dataclass
class GitState:
    branch: str
    porcelain: list[str]
    worktree_count: int


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout


def current_state() -> GitState:
    branch = run_git(["branch", "--show-current"]).strip() or "DETACHED"
    porcelain = run_git(["status", "--short", "--untracked-files=all", "--no-renames"]).splitlines()
    worktree_count = run_git(["worktree", "list", "--porcelain"]).count("worktree ")
    return GitState(branch=branch, porcelain=porcelain, worktree_count=worktree_count)


def status_path(line: str) -> str:
    value = line[3:] if len(line) > 3 else ""
    if " -> " in value:
        value = value.rsplit(" -> ", 1)[-1]
    return value.strip().strip('"')


def path_matches(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == prefix.rstrip("/") or path.startswith(prefix) for prefix in prefixes)


def classify(paths: list[str], intent: str, concurrent: bool) -> tuple[str, list[str]]:
    reasons: list[str] = []
    intent_l = intent.lower()

    if concurrent or "concurrent" in intent_l or "parallel branch" in intent_l:
        reasons.append("intent implies concurrent branch work")
        return "worktree-required", reasons

    branch_paths = [p for p in paths if path_matches(p, BRANCH_REQUIRED_PREFIXES)]
    runtime_paths = [p for p in paths if path_matches(p, RUNTIME_PREFIXES)]
    main_paths = [p for p in paths if path_matches(p, MAIN_OK_PREFIXES)]

    if branch_paths:
        reasons.append("shared source/runtime surfaces changed: " + ", ".join(branch_paths[:8]))
        return "branch-required", reasons

    if runtime_paths:
        reasons.append("runtime/generated state is dirty and should be committed only deliberately: " + ", ".join(runtime_paths[:8]))
        return "blocked", reasons

    if main_paths:
        reasons.append("durable docs/research/meeting/build artifacts can usually stay on main")
        return "main-ok", reasons

    if paths:
        reasons.append("dirty paths need human classification before branch/worktree changes")
        return "blocked", reasons

    reasons.append("clean checkout; main is the default operator base")
    return "main-ok", reasons


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Git branch/worktree needs for N5 workspace work.")
    parser.add_argument("--intent", default="", help="Short description of intended work.")
    parser.add_argument("--concurrent", action="store_true", help="Declare that this requires parallel branch work.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    state = current_state()
    paths = [status_path(line) for line in state.porcelain if status_path(line)]
    disposition, reasons = classify(paths, args.intent, args.concurrent)

    if state.branch != "main" and disposition == "main-ok":
        reasons.append(f"current checkout is {state.branch}; return /home/workspace to main for operator-base work")
        disposition = "blocked"

    if state.worktree_count > 1:
        reasons.append(f"{state.worktree_count} worktrees exist; confirm each has an active disposition")

    if args.json:
        import json

        print(json.dumps({
            "disposition": disposition,
            "branch": state.branch,
            "dirty_count": len(paths),
            "worktree_count": state.worktree_count,
            "reasons": reasons,
            "paths_sample": paths[:20],
        }, indent=2))
    else:
        print(f"disposition: {disposition}")
        print(f"branch: {state.branch}")
        print(f"dirty_count: {len(paths)}")
        print(f"worktree_count: {state.worktree_count}")
        for reason in reasons:
            print(f"- {reason}")

    return 2 if disposition == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
