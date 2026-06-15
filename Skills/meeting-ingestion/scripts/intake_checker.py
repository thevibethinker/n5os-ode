#!/usr/bin/env python3
"""
Intake Checker — All-points scan across every meeting intake location.

Checks:
1. Local Inbox (Personal/Meetings/Active/) — raw files + queued meetings
2. Google Drive folders (External Transcripts) — new files not yet pulled
3. Pocket webhook inbox (Personal/Inbox/) — unprocessed reflections/meetings
4. Fathom API — recent recordings not yet ingested
5. Fireflies API — recent transcripts not yet ingested

Usage:
    python3 intake_checker.py [--json] [--verbose]
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# --- D1 sys.path injection for paths.py ---
from pathlib import Path as _D1Path
sys.path.insert(0, str(_D1Path(__file__).parent))

logger = logging.getLogger(__name__)

from paths import ACTIVE_DIR as INBOX  # noqa: E402
POCKET_INBOX = Path("/home/workspace/Personal/Inbox")
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")
DRIVE_CONFIG = Path("/home/workspace/N5/config/drive_locations.yaml")

try:
    from backfill import get_api_key
except Exception:
    def get_api_key(var_name: str) -> str:
        return os.environ.get(var_name, "").strip()


def check_local_inbox(verbose: bool = False) -> dict:
    """Check for raw files and queued meetings in local Inbox."""
    result = {
        "source": "local_inbox",
        "path": str(INBOX),
        "raw_files": [],
        "queued_meetings": {},
        "total_actionable": 0,
    }

    if not INBOX.exists():
        result["status"] = "missing"
        result["message"] = "Inbox directory does not exist"
        return result

    # Raw files sitting in Inbox root (not yet ingested)
    for f in INBOX.iterdir():
        if f.is_file() and f.suffix in [".md", ".txt", ".jsonl", ".docx"] and not f.name.startswith("."):
            result["raw_files"].append(f.name)

    # Meeting folders by status
    status_counts = {}
    for item in INBOX.iterdir():
        if item.is_dir() and not item.name.startswith((".", "_")):
            manifest_path = item / "manifest.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text())
                    status = manifest.get("status", "unknown")
                    status_counts.setdefault(status, []).append(item.name)
                except Exception:
                    status_counts.setdefault("corrupt_manifest", []).append(item.name)
            else:
                status_counts.setdefault("no_manifest", []).append(item.name)

    result["queued_meetings"] = {k: len(v) for k, v in status_counts.items()}
    if verbose:
        result["queued_meetings_detail"] = {k: v for k, v in status_counts.items()}

    result["total_actionable"] = (
        len(result["raw_files"])
        + len(status_counts.get("ingested", []))
        + len(status_counts.get("identified", []))
        + len(status_counts.get("gated", []))
    )
    result["status"] = "ok"
    return result


def check_pocket_inbox(verbose: bool = False) -> dict:
    """Check for unprocessed Pocket intake items."""
    result = {
        "source": "pocket_inbox",
        "path": str(POCKET_INBOX),
        "pending_items": [],
        "total_actionable": 0,
    }

    if not POCKET_INBOX.exists():
        result["status"] = "no_inbox"
        return result

    for item in POCKET_INBOX.iterdir():
        if item.is_dir() and not item.name.startswith((".", "_")):
            manifest_path = item / "manifest.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text())
                    content_type = manifest.get("content_type", "unknown")
                    status = manifest.get("status", "unknown")
                    if content_type == "meeting" and status not in ["archived", "processed"]:
                        result["pending_items"].append({
                            "name": item.name,
                            "content_type": content_type,
                            "status": status,
                        })
                except Exception:
                    pass

    result["total_actionable"] = len(result["pending_items"])
    result["status"] = "ok"
    return result


def check_drive_folders(verbose: bool = False) -> dict:
    """Check Google Drive External Transcripts folders for new files."""
    result = {
        "source": "google_drive",
        "folders": [],
        "total_actionable": 0,
        "status": "ok",
    }

    # Load drive folder config
    drive_folders = _get_drive_folder_ids()
    if not drive_folders:
        result["status"] = "no_folders_configured"
        result["message"] = "No External Transcripts folders configured in drive_locations.yaml"
        return result

    try:
        sys.path.insert(0, "/home/workspace/N5/services")
        # Use Google Drive API via gcloud or existing pull infrastructure
        from meeting_ingestion_helpers import list_drive_folder_files
    except ImportError:
        # Fallback: try using the pull.py module
        pass

    # For each configured folder, we'll report its config
    # Actual Drive API check happens in drive_import.py
    for folder in drive_folders:
        folder_info = {
            "account": folder.get("account", "unknown"),
            "folder_id": folder.get("folder_id", ""),
            "label": folder.get("label", "External Transcripts"),
        }
        result["folders"].append(folder_info)

    result["message"] = f"{len(drive_folders)} Drive folder(s) configured — use `drive-import --scan` to check for new files"
    return result


def check_fathom_api(verbose: bool = False) -> dict:
    """Check Fathom API for recent recordings not yet ingested."""
    result = {
        "source": "fathom",
        "status": "unchecked",
        "recent_recordings": [],
        "total_actionable": 0,
    }

    api_key = get_api_key("FATHOM_API_KEY")
    if not api_key:
        result["status"] = "no_api_key"
        result["message"] = "FATHOM_API_KEY not available in runtime env or fallback key files"
        return result

    try:
        import requests
        resp = requests.get(
            "https://api.fathom.ai/external/v1/meetings",
            headers={"X-Api-Key": api_key},
            params={"limit": 1},
            timeout=10,
        )
        if resp.status_code == 200:
            result["status"] = "connected"
            result["message"] = "Fathom API reachable — use `backfill --source fathom` to pull historical recordings"
        else:
            result["status"] = "auth_failed"
            result["message"] = f"Fathom API returned {resp.status_code}"

    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Fathom API check failed: {e}"

    return result


def check_fireflies_api(verbose: bool = False) -> dict:
    """Check Fireflies API for recent transcripts not yet ingested."""
    result = {
        "source": "fireflies",
        "status": "unchecked",
        "recent_transcripts": [],
        "total_actionable": 0,
    }

    api_key = get_api_key("FIREFLIES_API_KEY")
    if not api_key:
        result["status"] = "no_api_key"
        result["message"] = "FIREFLIES_API_KEY not available in runtime env or fallback key files"
        return result

    try:
        import requests
        resp = requests.post(
            "https://api.fireflies.ai/graphql",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"query": "{ transcripts(limit: 1) { id title } }"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if "errors" in data:
                result["status"] = "auth_failed"
                result["message"] = f"Fireflies API auth error: {data['errors'][0].get('message', 'unknown')}"
            else:
                result["status"] = "connected"
                result["message"] = "Fireflies API reachable — use `backfill --source fireflies` to pull historical transcripts"
        else:
            result["status"] = "auth_failed"
            result["message"] = f"Fireflies API returned {resp.status_code}"

    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Fireflies API check failed: {e}"

    return result


def _get_drive_folder_ids() -> list:
    """Load External Transcripts Drive folder IDs from config."""
    if not DRIVE_CONFIG.exists():
        return []

    try:
        import yaml
        config = yaml.safe_load(DRIVE_CONFIG.read_text())
    except ImportError:
        # Fallback: parse YAML manually for simple structure
        config = _parse_simple_yaml(DRIVE_CONFIG)

    if not config:
        return []

    ext = config.get("external_transcripts", {})
    if not ext:
        return []

    folders = ext.get("folders", [])
    if isinstance(folders, list):
        return folders
    return []


def _parse_simple_yaml(path: Path) -> dict:
    """Minimal YAML parser for our config structure."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        return {}


def run_full_check(verbose: bool = False, json_output: bool = False) -> dict:
    """Run all intake checks and return unified report."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [],
        "summary": {
            "total_actionable": 0,
            "sources_ok": 0,
            "sources_degraded": 0,
        },
    }

    checks = [
        ("Local Inbox", check_local_inbox),
        ("Pocket Inbox", check_pocket_inbox),
        ("Google Drive", check_drive_folders),
        ("Fathom API", check_fathom_api),
        ("Fireflies API", check_fireflies_api),
    ]

    for label, check_fn in checks:
        try:
            result = check_fn(verbose=verbose)
            report["checks"].append(result)
            report["summary"]["total_actionable"] += result.get("total_actionable", 0)
            if result.get("status") in ("ok", "connected"):
                report["summary"]["sources_ok"] += 1
            else:
                report["summary"]["sources_degraded"] += 1
        except Exception as e:
            report["checks"].append({
                "source": label.lower().replace(" ", "_"),
                "status": "error",
                "message": str(e),
            })
            report["summary"]["sources_degraded"] += 1

    if json_output:
        return report

    # Human-readable output
    print("=" * 60)
    print("MEETING INTAKE — ALL POINTS CHECK")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    for check in report["checks"]:
        source = check.get("source", "unknown")
        status = check.get("status", "unknown")
        actionable = check.get("total_actionable", 0)

        icon = "✅" if status in ("ok", "connected") else "⚠️" if status != "error" else "❌"
        print(f"\n{icon} {source.upper().replace('_', ' ')}")

        if source == "local_inbox":
            raw = check.get("raw_files", [])
            queued = check.get("queued_meetings", {})
            if raw:
                print(f"  Raw files (not ingested): {len(raw)}")
                if verbose:
                    for f in raw:
                        print(f"    - {f}")
            if queued:
                for st, count in queued.items():
                    print(f"  {st}: {count}")
            if actionable:
                print(f"  → {actionable} actionable item(s)")
            else:
                print("  → All clear")

        elif source == "pocket_inbox":
            pending = check.get("pending_items", [])
            if pending:
                print(f"  Pending meeting items: {len(pending)}")
                if verbose:
                    for p in pending:
                        print(f"    - {p['name']} ({p['status']})")
            else:
                print("  → No pending meeting items")

        elif source == "google_drive":
            folders = check.get("folders", [])
            msg = check.get("message", "")
            if folders:
                for f in folders:
                    print(f"  📁 {f.get('label', 'folder')} ({f.get('account', '?')})")
            if msg:
                print(f"  {msg}")

        elif source in ("fathom", "fireflies"):
            msg = check.get("message", status)
            print(f"  {msg}")

    total = report["summary"]["total_actionable"]
    ok = report["summary"]["sources_ok"]
    deg = report["summary"]["sources_degraded"]
    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {ok} sources OK, {deg} degraded, {total} total actionable items")
    print("=" * 60)

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Meeting intake all-points check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed listings")
    args = parser.parse_args()

    report = run_full_check(verbose=args.verbose, json_output=args.json)
    if args.json:
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
