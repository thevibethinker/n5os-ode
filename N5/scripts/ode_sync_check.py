#!/usr/bin/env python3
"""
Pre-push validation for N5OS Ode repo.
Run before pushing to verify local/remote sync and branch safety.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(args: list[str], cwd: Path) -> tuple[str, int]:
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(cwd))
    return result.stdout.strip(), result.returncode


def detect_repo_path(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"Explicit repo path not found: {p}")

    candidates = [
        Path("/home/workspace/Build Exports/n5os-ode"),
        Path("/home/workspace/N5/export/n5os-ode"),
        Path.cwd(),
    ]
    for candidate in candidates:
        if (candidate / ".git").exists():
            return candidate.resolve()
    raise FileNotFoundError("Could not find n5os-ode repo. Use --repo-path.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-push validation for N5OS Ode")
    parser.add_argument("--repo-path", help="Path to n5os-ode checkout")
    parser.add_argument(
        "--allow-main",
        action="store_true",
        help="Allow running on main branch (default blocks)",
    )
    args = parser.parse_args()

    print("N5OS Ode Sync Check")
    print("=" * 40)

    try:
        repo_path = detect_repo_path(args.repo_path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"Repo: {repo_path}")

    git_dir, rc = run(["git", "rev-parse", "--git-dir"], repo_path)
    if rc != 0:
        print("ERROR: Not a git repository")
        return 1
    print(f"Git dir: {git_dir}")

    branch, rc = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    if rc != 0:
        print("ERROR: Could not determine current branch")
        return 1
    print(f"Branch: {branch}")
    if branch == "main" and not args.allow_main:
        print("ERROR: Build safety rule violation: current branch is main.")
        print("Create/use feature/<slug> or rerun with --allow-main.")
        return 1

    print("\n1) Fetching from origin...")
    _, rc = run(["git", "fetch", "origin"], repo_path)
    if rc != 0:
        print("ERROR: Failed to fetch from origin")
        return 1

    upstream, rc = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo_path)
    if rc != 0 or not upstream:
        print("WARN: No upstream configured for current branch")
        upstream = "origin/main"
    print(f"Upstream: {upstream}")

    print("\n2) Comparing commit counts...")
    local_count, rc_local = run(["git", "rev-list", "--count", "HEAD"], repo_path)
    remote_count, rc_remote = run(["git", "rev-list", "--count", upstream], repo_path)
    if rc_local != 0 or rc_remote != 0:
        print("ERROR: Could not compare commit counts")
        return 1

    print(f"Local:  {local_count} commits")
    print(f"Remote: {remote_count} commits")
    if int(remote_count) > int(local_count):
        print("WARN: Remote has more commits than local; pull/rebase before push.")
        return 1

    print("\n3) Checking working tree...")
    status, _ = run(["git", "status", "--porcelain"], repo_path)
    if status:
        lines = status.splitlines()
        print("Uncommitted changes:")
        for line in lines[:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... and {len(lines) - 5} more")
    else:
        print("Working tree clean")

    print("\n4) Commits ahead of upstream...")
    ahead, _ = run(["git", "log", f"{upstream}..HEAD", "--oneline"], repo_path)
    if ahead:
        lines = ahead.splitlines()
        for line in lines[:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... and {len(lines) - 5} more commits")
    else:
        print("  (nothing ahead)")

    print("\nPASS: Sync check complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
