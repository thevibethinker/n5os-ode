#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import shlex

# Define patterns for files that should be tracked
TRACKED_PATHS = [
    'N5/prefs.md',
    'N5/commands.jsonl',
    'N5/lists',
    'N5/knowledge',
    'N5/modules',
    'N5/flows',
    'N5/schemas',
    'N5/scripts',
    'N5/examples'
]


def is_under_path(path, roots):
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
    # Returns set of tracked file paths
    result = subprocess.run(['git', 'ls-files'], stdout=subprocess.PIPE, text=True, check=True)
    tracked = set(result.stdout.strip().splitlines())
    return tracked


def get_all_files():
    # Returns list of all files under N5/ matching tracked prefixes
    base = Path('N5')
    files = []
    if not base.exists():
        return files
    for p in base.rglob('*'):
        if p.is_file():
            files.append(str(p))
    return files


def is_ignored_by_git(path):
    result = subprocess.run(['git', 'check-ignore', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def filter_should_track_files(all_files, tracked_files):
    to_check = []
    for f in all_files:
        if is_under_path(f, TRACKED_PATHS) and f not in tracked_files and not is_ignored_by_git(f):
            to_check.append(f)
    return to_check


def main():
    tracked_files = get_git_tracked_files()
    all_files = get_all_files()
    should_track = filter_should_track_files(all_files, tracked_files)

    if not should_track:
        print("No untracked files found that should be tracked.")
        return

    print("The following files should be added to Git to keep tracking current:")
    for f in should_track:
        print(f"  {f}")
    print()
    files_string = ' '.join(shlex.quote(f) for f in should_track)
    print(f"Run this command to add them all to Git:\n\ngit add {files_string}\n")


if __name__ == '__main__':
    main()
