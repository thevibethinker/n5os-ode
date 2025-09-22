#!/usr/bin/env python3
"""
N5 core-manifest audit
Lightweight daily check that engine-layer files exist, are non-empty, and remain tracked.
"""

import json
import sys
import subprocess
import time
import typing
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "core_manifest.json"
AUDIT_LOG = ROOT / "runtime" / "audit" / "core_audit.log"

# Ensure audit directory exists (logs are append-only)
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)


class CoreAuditor:
    """Single-call auditor that reads manifest and emits pass/fail + log"""

    def __init__(self) -> None:
        self.manifest = self._load_manifest()
        self.issues: list[str] = []

    def _load_manifest(self) -> dict:
        with MANIFEST.open() as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Check helpers
    # ------------------------------------------------------------------
    def _resolve_path(self, path: str) -> Path:
        """Convert manifest path to absolute Path object"""
        # For registry files that start with N5/, use the workspace root
        if path.startswith("N5/"):
            return ROOT / path[3:]  # Remove N5/ prefix
        return ROOT / path

    def _exists_nonempty(self, entry: dict) -> bool:
        p: Path = self._resolve_path(entry["path"])
        return p.is_file() and p.stat().st_size >= entry.get("min_bytes", 1)

    def _tracked(self, entry: dict) -> bool:
        path = entry["path"]
        # git check-ignore quiet => 0 means *ignored*
        ignored = subprocess.run("git".split() + ["check-ignore", "--quiet", path], cwd=ROOT, capture_output=True).returncode == 0
        return not ignored

    def _regex_present(self, entry: dict) -> bool:
        content = self._resolve_path(entry["path"]).read_text()
        rx = entry["must_contain_regex"]
        return bool(re.search(rx, content))

    # ------------------------------------------------------------------
    # Registry lookup (JSONL)
    # ------------------------------------------------------------------
    def _registry_contains(self, entry: dict) -> bool:
        reg_file = self._resolve_path(entry["registry_file"])
        tgt_cmd = entry["must_contain_command"]
        
        count = 0
        with reg_file.open() as f:
            for line in f:
                # registry entry is valid JSON on each line
                try:
                    obj = json.loads(line.strip())
                    if obj.get("name") == tgt_cmd:
                        return True
                except (json.JSONDecodeError, AttributeError):
                    continue
        return False

    # ------------------------------------------------------------------
    # Append-only reservoirs (timestamp heuristic)
    # ------------------------------------------------------------------
    def _reservoir_append_safe(self, path: str) -> bool:
        p = self._resolve_path(path)
        now = time.time()
        last_mod = p.stat().st_mtime if p.exists() else 0
        # assume “append recently” if mod < 7 days ago; coarse but safe
        return (now - last_mod) < 604800  

    # ------------------------------------------------------------------
    # Main audit
    # ------------------------------------------------------------------
    def audit(self) -> dict:
        core_files = self.manifest.get("core_files",[])
        registry_checks = self.manifest.get("command_registry_checks",[])
        reservoirs = self.manifest.get("append_only_reservoirs",[])

        for item in core_files:
            path_key = item["path"]
            if not self._exists_nonempty(item):
                self.issues.append(f"missing or empty: {path_key}")
            elif item.get("must_be_tracked", True) and not self._tracked(item):
                self.issues.append(f"untracked or ignored: {path_key}")
            elif "must_contain_regex" in item and not self._regex_present(item):
                self.issues.append(f"regex missing: {path_key}")

        for item in registry_checks:
            if not self._registry_contains(item):
                self.issues.append(f"command entry missing: {item['must_contain_command']}")

        for path in reservoirs:
            if not self._reservoir_append_safe(path):
                self.issues.append(f"possible overwrite: {path} (recent modification)")

        return {"pass": len(self.issues) == 0, "timestamp": time.time(), "issues": self.issues}

    # ------------------------------------------------------------------
    # Logging (append-only)
    # ------------------------------------------------------------------
    def log_audit(self, result: dict) -> None:
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(result) + "\n")


# ----------------------------------------------------------------------
# Entry points
# - CLI call for daily cron
# - Importable call for scheduled-task runner
# ----------------------------------------------------------------------

AUDIT_RESULT: typing.Final[dict] = {}

def run_audit() -> dict:
    """Importable/invokable entry point"""
    auditor = CoreAuditor()
    result = auditor.audit()
    auditor.log_audit(result)
    global AUDIT_RESULT; AUDIT_RESULT = result  # side-channel for command run
    return result


def main():
    """CLI wrapper for run-system / cron"""
    try:
        report = run_audit()
        print(json.dumps(report, indent=2))  # stdout for humans/command echo
        sys.exit(0 if report["pass"] else 1)
    except Exception as e:
        err_obj = {"pass": False, "timestamp": time.time(), "error": str(e)}
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(err_obj) + "\n")
        print(json.dumps(err_obj, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()