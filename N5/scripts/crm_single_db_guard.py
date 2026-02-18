#!/usr/bin/env python3
"""
CRM single-database guardrail.

Checks for active references to legacy CRM databases and emits migration readiness metrics.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

WORKSPACE = Path("/home/workspace")
N5_DIR = WORKSPACE / "N5"
N5_DATA = N5_DIR / "data"
N5_CORE_DB = N5_DATA / "n5_core.db"
LEGACY_DB = N5_DATA / "crm.db"
LEGACY_V3_DB = N5_DATA / "crm_v3.db"

SCAN_ROOTS = [N5_DIR / "scripts"]
INCLUDE_EXTENSIONS = {".py", ".sh"}
EXCLUDE_PATH_SUBSTRINGS = [
    "/__pycache__/",
    "/backups/",
    "/archive/",
    "/_archive/",
    "/builds/",
    "/tests/",
]

EXCLUDE_FILE_NAMES = {
    "crm_single_db_guard.py",
    "db_paths.py",
    "crm_paths.py",
    "migrate_to_n5_core.py",
    "migrate_legacy_crmdb_to_n5_core.py",
    "reindex_v3.py",
    "normalize_crm_v2.py",
    "crm_migrate_to_v3.py",
    "validate_crm_v3_arch.py",
}
EXCLUDE_FILE_PREFIXES = ("migrate_", "test_")

LEGACY_PATTERNS = [
    re.compile(r"(?:^|[^a-zA-Z0-9_])crm_v3\.db(?:[^a-zA-Z0-9_]|$)", re.IGNORECASE),
    re.compile(r"(?:^|[^a-zA-Z0-9_])N5/data/crm\.db(?:[^a-zA-Z0-9_]|$)"),
    re.compile(r"Personal/Knowledge/CRM/db/crm\.db"),
]


@dataclass
class Finding:
    path: Path
    line_no: int
    line: str
    pattern: str


@dataclass
class Metric:
    key: str
    value: int


def should_scan(path: Path) -> bool:
    as_posix = path.as_posix()
    if any(token in as_posix for token in EXCLUDE_PATH_SUBSTRINGS):
        return False
    if path.name in EXCLUDE_FILE_NAMES:
        return False
    if path.name.startswith(EXCLUDE_FILE_PREFIXES):
        return False
    return path.suffix in INCLUDE_EXTENSIONS


def iter_files() -> Iterable[Path]:
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and should_scan(path):
                yield path


def scan_legacy_references() -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            for pattern in LEGACY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            path=path,
                            line_no=idx,
                            line=line.strip(),
                            pattern=pattern.pattern,
                        )
                    )
    return findings


def sql_count(conn: sqlite3.Connection, query: str) -> int:
    row = conn.execute(query).fetchone()
    return int(row[0]) if row else 0


def compute_metrics() -> list[Metric]:
    metrics: list[Metric] = []

    if not N5_CORE_DB.exists():
        return [Metric("n5_core_exists", 0)]

    with sqlite3.connect(N5_CORE_DB) as core:
        metrics.extend(
            [
                Metric("n5_core_exists", 1),
                Metric("n5_people", sql_count(core, "SELECT COUNT(*) FROM people")),
                Metric("n5_organizations", sql_count(core, "SELECT COUNT(*) FROM organizations")),
                Metric("n5_interactions", sql_count(core, "SELECT COUNT(*) FROM interactions")),
                Metric("n5_calendar_events", sql_count(core, "SELECT COUNT(*) FROM calendar_events")),
                Metric(
                    "n5_duplicate_full_names",
                    sql_count(
                        core,
                        """
                        SELECT COUNT(*) FROM (
                            SELECT lower(trim(full_name)) AS key, COUNT(*) AS c
                            FROM people
                            WHERE full_name IS NOT NULL AND trim(full_name) != ''
                            GROUP BY key
                            HAVING c > 1
                        )
                        """,
                    ),
                ),
                Metric(
                    "n5_duplicate_emails",
                    sql_count(
                        core,
                        """
                        SELECT COUNT(*) FROM (
                            SELECT lower(trim(email)) AS key, COUNT(*) AS c
                            FROM people
                            WHERE email IS NOT NULL AND trim(email) != ''
                            GROUP BY key
                            HAVING c > 1
                        )
                        """,
                    ),
                ),
            ]
        )

        if LEGACY_DB.exists() and LEGACY_DB.stat().st_size > 0:
            core.execute(f"ATTACH DATABASE '{LEGACY_DB}' AS legacy")
            metrics.extend(
                [
                    Metric("legacy_crm_exists", 1),
                    Metric("legacy_individuals", sql_count(core, "SELECT COUNT(*) FROM legacy.individuals")),
                    Metric("legacy_organizations", sql_count(core, "SELECT COUNT(*) FROM legacy.organizations")),
                    Metric("legacy_interactions", sql_count(core, "SELECT COUNT(*) FROM legacy.interactions")),
                    Metric(
                        "legacy_email_overlap_in_n5",
                        sql_count(
                            core,
                            """
                            SELECT COUNT(*)
                            FROM legacy.individuals li
                            JOIN people p
                              ON lower(trim(li.email)) = lower(trim(p.email))
                            WHERE li.email IS NOT NULL AND trim(li.email) != ''
                            """,
                        ),
                    ),
                    Metric(
                        "legacy_name_missing_in_n5",
                        sql_count(
                            core,
                            """
                            SELECT COUNT(*)
                            FROM legacy.individuals li
                            LEFT JOIN people p
                              ON lower(trim(li.full_name)) = lower(trim(p.full_name))
                            WHERE li.full_name IS NOT NULL
                              AND trim(li.full_name) != ''
                              AND p.id IS NULL
                            """,
                        ),
                    ),
                ]
            )
        else:
            metrics.append(Metric("legacy_crm_exists", 0))

    metrics.append(
        Metric(
            "legacy_crm_v3_nonzero_bytes",
            1 if LEGACY_V3_DB.exists() and LEGACY_V3_DB.stat().st_size > 0 else 0,
        )
    )
    return metrics


def write_report(findings: list[Finding], metrics: list[Metric], output_path: Path) -> None:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    findings_by_file: dict[str, list[Finding]] = {}
    for f in findings:
        findings_by_file.setdefault(str(f.path.relative_to(WORKSPACE)), []).append(f)

    lines: list[str] = []
    lines.append("---")
    lines.append(f"created: {datetime.utcnow().strftime('%Y-%m-%d')}")
    lines.append(f"last_edited: {datetime.utcnow().strftime('%Y-%m-%d')}")
    lines.append("version: 1.0")
    lines.append("provenance: con_aobUiRmCIj5rHnQf")
    lines.append("---")
    lines.append("")
    lines.append("# CRM Single-DB Guard Report")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Active legacy DB references found: **{len(findings)}**")
    lines.append(f"- Files with violations: **{len(findings_by_file)}**")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    for metric in metrics:
        lines.append(f"- `{metric.key}`: {metric.value}")

    lines.append("")
    lines.append("## Violations")
    lines.append("")
    if not findings:
        lines.append("- None")
    else:
        for rel_path, file_findings in sorted(findings_by_file.items()):
            lines.append(f"### `{rel_path}`")
            for item in file_findings:
                lines.append(f"- L{item.line_no}: `{item.line}`")
            lines.append("")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def print_json(findings: list[Finding], metrics: list[Metric]) -> None:
    payload = {
        "findings": [
            {
                "path": str(f.path),
                "line_no": f.line_no,
                "line": f.line,
                "pattern": f.pattern,
            }
            for f in findings
        ],
        "metrics": [{"key": m.key, "value": m.value} for m in metrics],
    }
    print(json.dumps(payload, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CRM single-DB guardrail")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if legacy references exist")
    parser.add_argument("--report", action="store_true", help="Write markdown report artifact")
    parser.add_argument(
        "--report-path",
        default="/home/workspace/N5/builds/crm-unified-core/artifacts/migration-readiness.md",
        help="Output path for markdown report",
    )
    parser.add_argument("--json", action="store_true", help="Print findings and metrics as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = scan_legacy_references()
    metrics = compute_metrics()

    if args.report:
        write_report(findings, metrics, Path(args.report_path))
        print(f"Wrote report: {args.report_path}")

    if args.json:
        print_json(findings, metrics)
    else:
        print(f"Legacy reference findings: {len(findings)}")
        for finding in findings[:50]:
            rel = finding.path.relative_to(WORKSPACE)
            print(f"- {rel}:{finding.line_no} -> {finding.line}")
        if len(findings) > 50:
            print(f"... {len(findings) - 50} more")

    if args.check and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
