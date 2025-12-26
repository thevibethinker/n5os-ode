#!/usr/bin/env python3
"""
Preventive pre-flight guard for bulk operations (hygiene, renames, upgrades).
Fails fast if core-manifest files are missing, empty, or ignored.
"""

import json
import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "core_manifest.json"

# Re-use auditor engine from core_audit (no separate log needed; we log the same line)
sys.path.insert(0, str(ROOT / "scripts"))
from core_audit import run_audit  # returns the dict, logs line


def main():
    """Fail-fast entry point before hygiene/rename.
    Returns 0 only if all checks pass."""
    report = run_audit()

    if not report["pass"]:
        # Fail-fast: print a concise message and exit 1
        concise = "; ".join(report["issues"][:3])  # show first 3
        sys.stderr.write(f"HYGIENE_PREFLIGHT_FAILED: {concise}\n")
        sys.stderr.write("Fix above issues or use --fix-override before hygiene run.\n")
        sys.exit(1)

    print(json.dumps({"pass": True, "timestamp": report["timestamp"]}, indent=2))
    # log already appended by core_audit


if __name__ == "__main__":
    main()