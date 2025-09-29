#!/usr/bin/env python3
"""
N5 Run Record Writer

Records run telemetry in JSONL format for observability.
Format: N5/runtime/runs/<command>/<date>/<run_id>.jsonl
Each file contains: header, entries, summary.
"""

import json
import sys
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "runtime" / "runs"

class RunRecorder:
    def __init__(self, command: str, inputs_hash: str, layers_used: List[str], dry_run: bool = False):
        self.command = command
        self.run_id = str(uuid.uuid4())
        self.start_time = datetime.now(timezone.utc)
        self.inputs_hash = inputs_hash
        self.layers_used = layers_used
        self.dry_run = dry_run
        self.entries: List[Dict[str, Any]] = []
        self.artifacts: List[str] = []
        self.errors: List[str] = []
        self.status = "running"

        # Create file path
        date_str = self.start_time.strftime("%Y-%m-%d")
        self.file_path = RUNS_DIR / command / date_str / f"{self.run_id}.jsonl"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write header
        self._write_header()

    def log(self, level: str, event: str, data: Optional[Dict[str, Any]] = None):
        """Log an entry to the run record."""
        entry = {
            "level": level,
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "data": data or {}
        }
        self.entries.append(entry)
        self._write_entry(entry)

    def add_artifact(self, artifact: str):
        """Add an artifact path to the run record."""
        self.artifacts.append(artifact)

    def add_error(self, error: str):
        """Add an error to the run record."""
        self.errors.append(error)

    def complete(self, status: str = "success"):
        """Complete the run and write summary."""
        self.status = status
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - self.start_time).total_seconds() * 1000)

        summary = {
            "status": self.status,
            "duration_ms": duration_ms,
            "artifacts": self.artifacts,
            "errors": self.errors
        }
        self._write_summary(summary)

    def _write_header(self):
        """Write the run header."""
        header = {
            "run_id": self.run_id,
            "command": self.command,
            "inputs_hash": self.inputs_hash,
            "layers_used": self.layers_used,
            "dry_run": self.dry_run,
            "start_time": self.start_time.isoformat()
        }
        self._write_line("header", header)

    def _write_entry(self, entry: Dict[str, Any]):
        """Write a log entry."""
        self._write_line("entry", entry)

    def _write_summary(self, summary: Dict[str, Any]):
        """Write the run summary."""
        self._write_line("summary", summary)

    def _write_line(self, record_type: str, data: Dict[str, Any]):
        """Write a line to the JSONL file."""
        line = {
            "type": record_type,
            "data": data
        }
        with self.file_path.open("a", encoding="utf-8") as f:
            json.dump(line, f, ensure_ascii=False)
            f.write("\n")


def compute_inputs_hash(inputs: Dict[str, Any]) -> str:
    """Compute a hash of the command inputs for deduplication."""
    # Sort keys for consistent hashing
    sorted_items = sorted(inputs.items())
    input_str = json.dumps(sorted_items, sort_keys=True, default=str)
    return hashlib.sha256(input_str.encode('utf-8')).hexdigest()[:16]


def main():
    """CLI interface for run recording."""
    if len(sys.argv) < 2:
        print("Usage: python n5_run_record.py <command> [--dry-run] [--help]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    help_requested = "--help" in sys.argv

    if help_requested:
        print("""
N5 Run Record Writer

Records run telemetry in JSONL format for observability.

Usage:
  python n5_run_record.py <command> [--dry-run]

Arguments:
  command    The command name being executed
  --dry-run  Mark this as a dry run (no actual execution)
  --help     Show this help message

The script expects JSON input on stdin with:
{
  "inputs": {...},        // Command inputs for hashing
  "layers_used": [...],   // Layers/modules used
  "status": "success|error",  // Final status
  "artifacts": [...],     // Artifact paths
  "errors": [...]         // Error messages
}
        """)
        return

    # Read JSON config from stdin
    try:
        config = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    inputs = config.get("inputs", {})
    layers_used = config.get("layers_used", [])
    status = config.get("status", "success")
    artifacts = config.get("artifacts", [])
    errors = config.get("errors", [])

    # Create recorder
    inputs_hash = compute_inputs_hash(inputs)
    recorder = RunRecorder(command, inputs_hash, layers_used, dry_run)

    # Log initial entry
    recorder.log("info", "run_started", {"inputs": inputs, "layers_used": layers_used})

    # Add artifacts and errors
    for artifact in artifacts:
        recorder.add_artifact(artifact)
    for error in errors:
        recorder.add_error(error)

    # Complete the run
    recorder.complete(status)

    # Output the run file path for use by calling scripts
    print(str(recorder.file_path))


if __name__ == "__main__":
    main()