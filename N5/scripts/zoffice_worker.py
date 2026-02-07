#!/usr/bin/env python3
"""Worker runner for the Zoffice Consultancy Stack."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/home/workspace/Skills/audit-system/scripts")
from audit_logger import log_entry, ZO_INSTANCE

MANIFEST_DIR = Path("/home/workspace/ZOFFICE_WORKERS")
STATE_FILE = MANIFEST_DIR / "worker_state.json"
AUDIT_DIRECTION = "worker-activation"


def parse_manifest(path: Path) -> dict:
    data = {"name": path.stem}
    for line in path.read_text().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"')
    return data


def list_manifests() -> list:
    if not MANIFEST_DIR.exists():
        return []
    return [f for f in MANIFEST_DIR.glob("*.manifest") if f.is_file()]


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except json.JSONDecodeError:
        return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def list_workers() -> None:
    manifests = list_manifests()
    if not manifests:
        print("No worker manifests found in ZOFFICE_WORKERS")
        return
    print(f"{'Name':<12} {'Persona':<12} {'Schedule/Trigger':<30} {'Type':<12}")
    print("-" * 70)
    for manifest_path in manifests:
        manifest = parse_manifest(manifest_path)
        persona = manifest.get("persona_id", "n/a")
        schedule = manifest.get("schedule") or manifest.get("activation") or "n/a"
        wtype = manifest.get("type", "scheduled")
        print(f"{manifest['name']:<12} {persona:<12} {schedule:<30} {wtype:<12}")


def record_activation(name: str, manifest: dict) -> None:
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    state[name] = {
        "last_activated": now,
        "status": "active",
        "persona": manifest.get("persona_id"),
        "command": manifest.get("activation", manifest.get("command"))
    }
    save_state(state)


def record_deactivation(name: str) -> None:
    state = load_state()
    if name not in state:
        state[name] = {"status": "inactive"}
    state[name]["status"] = "inactive"
    state[name]["last_deactivated"] = datetime.now(timezone.utc).isoformat()
    save_state(state)


def log_activation(name: str, manifest: dict, notes: str) -> None:
    payload = json.dumps({
        "worker": name,
        "persona": manifest.get("persona_id"),
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    log_entry(
        entry_type="worker_activation",
        direction=f"{ZO_INSTANCE}-internal",
        payload=payload,
        metadata={
            "worker": name,
            "schedule": manifest.get("schedule"),
            "type": manifest.get("type", "scheduled")
        }
    )


def log_deactivation(name: str, notes: str) -> None:
    payload = json.dumps({
        "worker": name,
        "notes": notes,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    log_entry(
        entry_type="worker_deactivation",
        direction=f"{ZO_INSTANCE}-internal",
        payload=payload,
        metadata={
            "worker": name
        }
    )


def activate_worker(name: str) -> None:
    manifest_path = MANIFEST_DIR / f"{name}.manifest"
    if not manifest_path.exists():
        print(f"Worker manifest not found for {name}")
        sys.exit(1)
    manifest = parse_manifest(manifest_path)
    record_activation(name, manifest)
    log_activation(name, manifest, "Activated via CLI")
    persona = manifest.get("persona_id", "unknown")
    command = manifest.get("activation", manifest.get("command", "n/a"))
    print(f"Worker '{name}' activated (persona={persona})")
    print(f"Run: {command}")
    print("Remember to revert to the default persona when the work is done.")


def deactivate_worker(name: str) -> None:
    state = load_state()
    if name not in state:
        print(f"Worker '{name}' has no recorded state yet; marking inactive anyway.")
    record_deactivation(name)
    log_deactivation(name, "Deactivated via CLI")
    print(f"Worker '{name}' marked inactive")


def show_status() -> None:
    state = load_state()
    if not state:
        print("No worker activations recorded yet.")
        return
    print(f"{'Worker':<12} {'Status':<10} {'Last Activated':<25}")
    print("-" * 50)
    for worker, details in state.items():
        print(f"{worker:<12} {details.get('status'):<10} {details.get('last_activated'):<25}")


def deactivate_all() -> None:
    state = load_state()
    for details in state.values():
        details["status"] = "inactive"
    save_state(state)
    print("All workers marked inactive.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Zoffice workers")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List configured workers")

    activate_parser = subparsers.add_parser("activate", help="Activate a worker")
    activate_parser.add_argument("worker", help="Worker name (librarian, consultant, debugger)")

    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate a worker")
    deactivate_parser.add_argument("worker", help="Worker name (librarian, consultant, debugger)")

    subparsers.add_parser("status", help="Show worker activation status")
    subparsers.add_parser("deactivate-all", help="Mark all workers inactive")

    args = parser.parse_args()

    if args.command == "list":
        list_workers()
    elif args.command == "activate":
        activate_worker(args.worker)
    elif args.command == "deactivate":
        deactivate_worker(args.worker)
    elif args.command == "status":
        show_status()
    elif args.command == "deactivate-all":
        deactivate_all()


if __name__ == "__main__":
    main()
