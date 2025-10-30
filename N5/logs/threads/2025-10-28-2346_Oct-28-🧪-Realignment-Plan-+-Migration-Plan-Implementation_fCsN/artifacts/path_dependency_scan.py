#!/usr/bin/env python3
"""Scan for path dependencies in scripts and recipes."""
import re
from pathlib import Path
from collections import defaultdict

# Directories to scan
SCAN_DIRS = [
    Path("/home/workspace/N5/scripts"),
    Path("/home/workspace/Recipes"),
]

# Regex for N5 path references
PATH_PATTERN = re.compile(r'["\']([/\w\-\.]*N5/[\w\-_/\.]+)["\']')

dependencies = defaultdict(set)

for scan_dir in SCAN_DIRS:
    if not scan_dir.exists():
        continue
    for file in scan_dir.rglob("*"):
        if not file.is_file() or file.suffix not in [".py", ".md", ".sh"]:
            continue
        try:
            content = file.read_text()
            matches = PATH_PATTERN.findall(content)
            for match in matches:
                if "N5/" in match:
                    # Extract N5 subdirectory
                    parts = match.split("N5/")
                    if len(parts) > 1:
                        subdir = parts[1].split("/")[0]
                        dependencies[subdir].add(str(file.relative_to("/home/workspace")))
        except Exception as e:
            pass

# Output
print("=== N5 SUBDIRECTORY PATH DEPENDENCIES ===\n")
for subdir in sorted(dependencies.keys()):
    count = len(dependencies[subdir])
    print(f"{subdir}: {count} files reference this path")
    if count <= 5:
        for f in sorted(dependencies[subdir]):
            print(f"  - {f}")
    else:
        for f in sorted(list(dependencies[subdir])[:3]):
            print(f"  - {f}")
        print(f"  ... and {count-3} more")
    print()
