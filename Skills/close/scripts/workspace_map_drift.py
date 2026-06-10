#!/usr/bin/env python3
"""Audit-only drift detector for WORKSPACE_MAP.md.

Compares the curated workspace map against actual filesystem state and emits
a structured report. Never edits the map. Designed to be invoked from
build-close so synthesis can flag stale navigation docs.

The map is hand-curated (single provenance, version-tracked), so this script
*suggests* — it does not auto-rewrite. Output is a JSON or human-readable
diff that the LLM/operator can act on.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

WORKSPACE = Path("/home/workspace")
MAP_PATH = WORKSPACE / "WORKSPACE_MAP.md"
SKILLS_DIR = WORKSPACE / "Skills"
BUILDS_DIR = WORKSPACE / "N5" / "builds"

# Top-level entries that are not navigation-relevant root surfaces.
# Files, dotfiles, scratch caches, tracking artifacts, and entries the map
# already covers via narrative rather than a directory listing.
ROOT_EXCLUDES = {
    ".git",
    ".claude",
    ".gitignore",
    "Trash",
    "Inbox",
    "Zoffice",  # transient overlay area
    "Zo",       # owner profile area, narrative-only
}

SCHEMA_VERSION = "1.0"


@dataclass
class DriftReport:
    map_path: str
    last_edited: str | None
    map_version: int | float | str | None
    age_days: int | None
    roots: dict[str, Any] = field(default_factory=dict)
    skills: dict[str, Any] = field(default_factory=dict)
    builds: dict[str, Any] = field(default_factory=dict)
    drift_score: int = 0
    needs_attention: bool = False
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "map_path": self.map_path,
            "last_edited": self.last_edited,
            "map_version": self.map_version,
            "age_days": self.age_days,
            "roots": self.roots,
            "skills": self.skills,
            "builds": self.builds,
            "drift_score": self.drift_score,
            "needs_attention": self.needs_attention,
            "recommendation": self.recommendation,
        }


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm: dict[str, Any] = {}
    if yaml is not None:
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            fm = {}
    return fm, parts[2]


def parse_workspace_roots_table(body: str) -> list[str]:
    """Extract directory names from the 'Workspace Roots' markdown table."""
    section_re = re.compile(
        r"##\s+Workspace Roots\s*\n(.+?)(?=\n## |\Z)", re.DOTALL | re.IGNORECASE
    )
    match = section_re.search(body)
    if not match:
        return []
    block = match.group(1)
    roots: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip header and separator rows
        if line.startswith("|---") or line.lower().startswith("| directory"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        token = cells[0]
        # Pull `Name/` or `Name` out of inline code spans
        m = re.search(r"`([^`]+)`", token)
        name = (m.group(1) if m else token).rstrip("/")
        if name:
            roots.append(name)
    return roots


def discover_filesystem_roots() -> list[str]:
    discovered: list[str] = []
    for entry in sorted(WORKSPACE.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("."):
            continue
        if name in ROOT_EXCLUDES:
            continue
        discovered.append(name)
    return discovered


def discover_skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return []
    out: list[str] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_"):
            continue
        if (entry / "SKILL.md").exists():
            out.append(entry.name)
    return out


def discover_recent_builds(since_ts: float | None) -> list[dict[str, Any]]:
    """Return finalized builds whose meta.json was modified after since_ts."""
    if not BUILDS_DIR.exists():
        return []
    recent: list[dict[str, Any]] = []
    for build_dir in sorted(BUILDS_DIR.iterdir()):
        if not build_dir.is_dir():
            continue
        meta_path = build_dir / "meta.json"
        if not meta_path.exists():
            continue
        try:
            mtime = meta_path.stat().st_mtime
        except OSError:
            continue
        if since_ts is not None and mtime <= since_ts:
            continue
        try:
            meta = json.loads(meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        status = meta.get("status")
        if status not in ("complete", "closed"):
            continue
        recent.append(
            {
                "slug": build_dir.name,
                "status": status,
                "title": meta.get("title"),
                "mtime": datetime.fromtimestamp(mtime, tz=timezone.utc)
                .date()
                .isoformat(),
            }
        )
    return recent


def parse_iso_date(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def build_report() -> DriftReport:
    text = MAP_PATH.read_text() if MAP_PATH.exists() else ""
    fm, body = parse_frontmatter(text)
    last_edited = fm.get("last_edited")
    map_version = fm.get("version")

    edited_date = parse_iso_date(last_edited)
    age_days = (
        (date.today() - edited_date).days if edited_date is not None else None
    )
    edited_ts = (
        datetime.combine(edited_date, datetime.min.time(), tzinfo=timezone.utc).timestamp()
        if edited_date is not None
        else None
    )

    roots_in_map = parse_workspace_roots_table(body)
    fs_roots = discover_filesystem_roots()
    new_roots = [r for r in fs_roots if r not in roots_in_map]
    stale_roots = [r for r in roots_in_map if r not in fs_roots]

    skills = discover_skills()
    recent_builds = discover_recent_builds(edited_ts)

    drift_score = (
        len(new_roots) * 3
        + len(stale_roots) * 2
        + len(recent_builds)
        + (1 if age_days is not None and age_days >= 30 else 0)
    )
    needs_attention = bool(new_roots or stale_roots or recent_builds) or (
        age_days is not None and age_days >= 60
    )

    parts: list[str] = []
    if new_roots:
        parts.append(f"{len(new_roots)} new top-level dir(s)")
    if stale_roots:
        parts.append(f"{len(stale_roots)} stale entry(ies)")
    if recent_builds:
        parts.append(f"{len(recent_builds)} new finalized build(s)")
    if age_days is not None and age_days >= 60:
        parts.append(f"map is {age_days}d old")
    if not parts:
        recommendation = "Map is current — no action needed."
    else:
        recommendation = (
            "Review WORKSPACE_MAP.md: " + ", ".join(parts) + ". "
            "Decide whether to update the map or accept current scope."
        )

    return DriftReport(
        map_path=str(MAP_PATH),
        last_edited=str(last_edited) if last_edited else None,
        map_version=map_version if isinstance(map_version, (int, float, str)) else None,
        age_days=age_days,
        roots={
            "in_map": roots_in_map,
            "in_filesystem": fs_roots,
            "new_in_filesystem": new_roots,
            "stale_in_map": stale_roots,
        },
        skills={
            "count_in_filesystem": len(skills),
        },
        builds={
            "recently_finalized": recent_builds,
        },
        drift_score=drift_score,
        needs_attention=needs_attention,
        recommendation=recommendation,
    )


def print_human(report: DriftReport) -> None:
    print("🗺️  Workspace map drift (audit-only):")
    print(f"   map:         {report.map_path}")
    print(
        f"   last edited: {report.last_edited or 'unknown'}"
        f"  age: {report.age_days if report.age_days is not None else '?'}d"
        f"  version: {report.map_version if report.map_version is not None else '?'}"
    )
    roots = report.roots
    print(
        f"   roots:       {len(roots.get('in_map', []))} in map,"
        f" {len(roots.get('in_filesystem', []))} on disk"
    )
    if roots.get("new_in_filesystem"):
        print("   new on disk:")
        for name in roots["new_in_filesystem"]:
            print(f"     + {name}/")
    if roots.get("stale_in_map"):
        print("   stale in map:")
        for name in roots["stale_in_map"]:
            print(f"     - {name}/")
    builds = report.builds.get("recently_finalized", [])
    if builds:
        print("   newly finalized builds:")
        for b in builds[:5]:
            print(f"     · {b['slug']} ({b['status']}, {b['mtime']})")
        if len(builds) > 5:
            print(f"     · ... and {len(builds) - 5} more")
    print(
        f"   drift_score: {report.drift_score}"
        f"  needs_attention: {report.needs_attention}"
    )
    print(f"   → {report.recommendation}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit-only drift detector for WORKSPACE_MAP.md"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human-readable text"
    )
    args = parser.parse_args()

    if not MAP_PATH.exists():
        payload = {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "error": f"WORKSPACE_MAP.md not found at {MAP_PATH}",
        }
        print(json.dumps(payload) if args.json else payload["error"])
        return 1

    report = build_report()
    if args.json:
        print(json.dumps({"ok": True, "report": report.to_dict()}, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
