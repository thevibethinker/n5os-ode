#!/usr/bin/env python3
"""Analyze N5 directory structure for realignment planning."""
import json
from pathlib import Path
from collections import defaultdict

n5_path = Path("/home/workspace/N5")
output = {
    "directories": {},
    "platonic_ideal": ["commands", "config", "data", "prefs", "schemas", "scripts"],
    "analysis": {}
}

# Scan each N5 subdir
for subdir in sorted(n5_path.iterdir()):
    if not subdir.is_dir() or subdir.name.startswith("."):
        continue
    
    info = {
        "name": subdir.name,
        "size_mb": sum(f.stat().st_size for f in subdir.rglob("*") if f.is_file()) / (1024*1024),
        "file_count": sum(1 for _ in subdir.rglob("*") if _.is_file()),
        "has_py": any(subdir.glob("**/*.py")),
        "has_md": any(subdir.glob("**/*.md")),
        "has_json": any(subdir.glob("**/*.json")),
        "subdirs": len([d for d in subdir.iterdir() if d.is_dir()]),
    }
    output["directories"][subdir.name] = info

# Categorize
platonic = set(output["platonic_ideal"])
current = set(output["directories"].keys())
output["analysis"]["in_platonic"] = sorted(current & platonic)
output["analysis"]["extra_dirs"] = sorted(current - platonic)
output["analysis"]["missing_dirs"] = sorted(platonic - current)

# Size ranking
by_size = sorted(output["directories"].items(), key=lambda x: x[1]["size_mb"], reverse=True)
output["analysis"]["largest_10"] = [(k, f"{v['size_mb']:.2f}MB") for k, v in by_size[:10]]

print(json.dumps(output, indent=2))
