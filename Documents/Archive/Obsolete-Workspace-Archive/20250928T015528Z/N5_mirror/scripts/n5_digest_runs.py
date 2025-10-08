#!/usr/bin/env python3
"""
N5 Run Digest Generator

Aggregates run records by period and generates summary reports.
Supports filtering by command, date range, status, etc.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import argparse

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "runtime" / "runs"

class RunDigest:
    def __init__(self):
        self.runs: List[Dict[str, Any]] = []
        self.stats = {
            "total_runs": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration_ms": 0,
            "avg_duration_ms": 0,
            "commands": defaultdict(int),
            "errors": [],
            "artifacts": []
        }

    def load_runs(self, command: Optional[str] = None, since: Optional[datetime] = None,
                  until: Optional[datetime] = None, limit: Optional[int] = None):
        """Load run records from JSONL files with optional filtering."""
        if not RUNS_DIR.exists():
            return

        run_files = []
        if command:
            # Filter by specific command
            cmd_dir = RUNS_DIR / command
            if cmd_dir.exists():
                for date_dir in cmd_dir.iterdir():
                    if date_dir.is_dir():
                        run_files.extend(date_dir.glob("*.jsonl"))
        else:
            # Load all commands
            for cmd_dir in RUNS_DIR.iterdir():
                if cmd_dir.is_dir():
                    for date_dir in cmd_dir.iterdir():
                        if date_dir.is_dir():
                            run_files.extend(date_dir.glob("*.jsonl"))

        # Sort by modification time (newest first)
        run_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        loaded = 0
        for run_file in run_files:
            if limit and loaded >= limit:
                break

            try:
                run_data = self._parse_run_file(run_file)
                if run_data:
                    run_date = datetime.fromisoformat(run_data["header"]["start_time"].replace('Z', '+00:00'))

                    # Apply date filters
                    if since and run_date < since:
                        continue
                    if until and run_date > until:
                        continue

                    self.runs.append(run_data)
                    loaded += 1
            except Exception as e:
                print(f"Warning: Failed to parse {run_file}: {e}", file=sys.stderr)

        # Sort runs by start time
        self.runs.sort(key=lambda r: r["header"]["start_time"])

    def _parse_run_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single run JSONL file."""
        lines = []
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    lines.append(json.loads(line.strip()))
        except Exception:
            return None

        if not lines:
            return None

        # Separate header, entries, and summary
        header = None
        entries = []
        summary = None

        for line in lines:
            if line["type"] == "header":
                header = line["data"]
            elif line["type"] == "entry":
                entries.append(line["data"])
            elif line["type"] == "summary":
                summary = line["data"]

        if not header or not summary:
            return None

        return {
            "header": header,
            "entries": entries,
            "summary": summary,
            "file_path": str(path)
        }

    def compute_stats(self):
        """Compute aggregate statistics from loaded runs."""
        if not self.runs:
            return

        self.stats["total_runs"] = len(self.runs)
        self.stats["success_count"] = sum(1 for r in self.runs if r["summary"]["status"] == "success")
        self.stats["error_count"] = sum(1 for r in self.runs if r["summary"]["status"] == "error")

        total_duration = sum(r["summary"]["duration_ms"] for r in self.runs if "duration_ms" in r["summary"])
        self.stats["total_duration_ms"] = total_duration
        self.stats["avg_duration_ms"] = total_duration // len(self.runs) if self.runs else 0

        # Command distribution
        for run in self.runs:
            self.stats["commands"][run["header"]["command"]] += 1

        # Collect all errors and artifacts
        for run in self.runs:
            if run["summary"].get("errors"):
                self.stats["errors"].extend(run["summary"]["errors"])
            if run["summary"].get("artifacts"):
                self.stats["artifacts"].extend(run["summary"]["artifacts"])

    def generate_report(self, format: str = "json") -> str:
        """Generate a digest report in the specified format."""
        self.compute_stats()

        if format == "json":
            return json.dumps({
                "stats": dict(self.stats),
                "runs": self.runs
            }, indent=2, ensure_ascii=False)

        elif format == "markdown":
            return self._generate_markdown_report()

        elif format == "summary":
            return self._generate_summary_report()

        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self) -> str:
        """Generate a detailed markdown report."""
        lines = ["# N5 Run Digest Report\n", f"Generated at: {datetime.now(timezone.utc).isoformat()}\n\n"]

        # Stats section
        lines.append("## Statistics\n\n")
        lines.append(f"- Total Runs: {self.stats['total_runs']}\n")
        lines.append(f"- Success Rate: {self.stats['success_count']}/{self.stats['total_runs']} ({self.stats['success_count']/self.stats['total_runs']*100:.1f}%)\n")
        lines.append(f"- Average Duration: {self.stats['avg_duration_ms']}ms\n")
        lines.append(f"- Total Duration: {self.stats['total_duration_ms']}ms\n\n")

        # Commands section
        if self.stats["commands"]:
            lines.append("## Commands\n\n")
            for cmd, count in sorted(self.stats["commands"].items()):
                lines.append(f"- `{cmd}`: {count} runs\n")
            lines.append("\n")

        # Errors section
        if self.stats["errors"]:
            lines.append("## Errors\n\n")
            for error in self.stats["errors"][:10]:  # Limit to first 10
                lines.append(f"- {error}\n")
            if len(self.stats["errors"]) > 10:
                lines.append(f"- ... and {len(self.stats['errors']) - 10} more\n")
            lines.append("\n")

        # Recent runs section
        if self.runs:
            lines.append("## Recent Runs\n\n")
            lines.append("| Command | Status | Duration | Started |\n")
            lines.append("|---------|--------|----------|--------|\n")

            for run in self.runs[-10:]:  # Last 10 runs
                cmd = run["header"]["command"]
                status = run["summary"]["status"]
                duration = run["summary"].get("duration_ms", 0)
                started = run["header"]["start_time"][:19]  # YYYY-MM-DDTHH:MM:SS
                lines.append(f"| `{cmd}` | {status} | {duration}ms | {started} |\n")

        return "".join(lines)

    def _generate_summary_report(self) -> str:
        """Generate a concise summary report."""
        success_rate = self.stats["success_count"] / self.stats["total_runs"] * 100 if self.runs else 0

        lines = [
            f"N5 Run Digest Summary",
            f"Total runs: {self.stats['total_runs']}",
            f"Success rate: {success_rate:.1f}%",
            f"Average duration: {self.stats['avg_duration_ms']}ms",
            f"Errors: {len(self.stats['errors'])}"
        ]

        if self.stats["commands"]:
            lines.append("Top commands:")
            for cmd, count in sorted(self.stats["commands"].items(), key=lambda x: x[1], reverse=True)[:3]:
                lines.append(f"  - {cmd}: {count}")

        return "\n".join(lines)


def main():
    """CLI interface for run digest generation."""
    parser = argparse.ArgumentParser(description="Generate N5 run digest reports")
    parser.add_argument("command", nargs="?", help="Specific command to analyze (optional)")
    parser.add_argument("--format", choices=["json", "markdown", "summary"], default="markdown",
                       help="Output format")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Maximum number of runs to analyze")
    parser.add_argument("--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Parse dates
    since = None
    if args.since:
        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    until = None
    if args.until:
        until = datetime.strptime(args.until, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    # Generate digest
    digest = RunDigest()
    digest.load_runs(command=args.command, since=since, until=until, limit=args.limit)
    report = digest.generate_report(format=args.format)

    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Digest written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()