#!/usr/bin/env python3
"""
git_audit.py — Audit a git repo for untracked files that should be tracked.

Scans specified directories for files not yet tracked by git (and not gitignored),
then reports them with a ready-to-run `git add` command.

Usage:
    python3 git_audit.py [--paths PATH [PATH ...]] [--help]

Options:
    --paths     Directories or files to audit (default: current directory)
    -h, --help  Show this help message and exit
"""
import argparse
import os
import subprocess
import shlex
from pathlib import Path


def is_under_path(path, roots):
    """Check if a file path falls under any of the given root paths."""
    path = Path(path).resolve()
    for root in roots:
        try:
            root_path = Path(root).resolve()
            if root_path in path.parents or path == root_path:
                return True
        except Exception:
            pass
    return False


def get_git_tracked_files():
    """Return set of files currently tracked by git."""
    result = subprocess.run(
        ["git", "ls-files"], stdout=subprocess.PIPE, text=True, check=True
    )
    return set(result.stdout.strip().splitlines())


def get_all_files(roots):
    """Return list of all files under the given root paths."""
    files = []
    for root in roots:
        base = Path(root)
        if not base.exists():
            continue
        if base.is_file():
            files.append(str(base))
        else:
            for p in base.rglob("*"):
                if p.is_file():
                    files.append(str(p))
    return files


def is_ignored_by_git(path):
    """Check whether a path is covered by .gitignore rules."""
    result = subprocess.run(
        ["git", "check-ignore", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0


def filter_should_track(all_files, tracked_files, roots):
    """Find files under roots that are neither tracked nor gitignored."""
    to_check = []
    for f in all_files:
        if is_under_path(f, roots) and f not in tracked_files and not is_ignored_by_git(f):
            to_check.append(f)
    return to_check


def main():
    parser = argparse.ArgumentParser(
        description="Audit a git repo for untracked files that should be tracked."
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["."],
        help="Directories or files to audit (default: current directory)",
    )
    args = parser.parse_args()

    tracked_files = get_git_tracked_files()
    all_files = get_all_files(args.paths)
    should_track = filter_should_track(all_files, tracked_files, args.paths)

    if not should_track:
        print("No untracked files found that should be tracked.")
        return

    print("The following files should be added to Git to keep tracking current:")
    for f in should_track:
        print(f"  {f}")
    print()
    files_string = " ".join(shlex.quote(f) for f in should_track)
    print(f"Run this command to add them all to Git:\n\ngit add {files_string}\n")


if __name__ == "__main__":
    main()
