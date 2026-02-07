#!/usr/bin/env python3
"""
Port Conflict Detector - Runtime detection of port allocation conflicts.

Performs three-way comparison:
1. PORT_REGISTRY.md (intended state)
2. list_user_services API (registered state)  
3. lsof (actual runtime state)

Usage:
    python3 port_conflict_detector.py check              # Human-readable report
    python3 port_conflict_detector.py check --json       # JSON output
    python3 port_conflict_detector.py check --exit-code  # Exit 1 if conflicts
    python3 port_conflict_detector.py alert              # Check + SMS if new conflicts
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

# Paths
REGISTRY_PATH = Path("/home/workspace/N5/config/PORT_REGISTRY.md")
STATE_PATH = Path("/home/workspace/N5/data/port_conflict_state.json")
SITES_DIR = Path("/home/workspace/Sites")

# Constants
ALERT_COOLDOWN_HOURS = 2


class ConflictType(Enum):
    DUPLICATE_REGISTRATION = "duplicate_registration"  # Two services on same port
    ZOMBIE_PORT = "zombie_port"  # Registered but nothing listening
    UNREGISTERED_LISTENER = "unregistered_listener"  # Listening but not registered
    REGISTRY_DRIFT = "registry_drift"  # Service exists but not in registry


class Severity(Enum):
    CRITICAL = "critical"  # Immediate action needed
    WARNING = "warning"  # Should investigate
    INFO = "info"  # For awareness


@dataclass
class Conflict:
    port: int
    conflict_type: ConflictType
    severity: Severity
    description: str
    details: dict

    def to_dict(self) -> dict:
        return {
            "port": self.port,
            "conflict_type": self.conflict_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "details": self.details,
        }


def get_registry_ports() -> dict[int, str]:
    """Parse PORT_REGISTRY.md for intended allocations."""
    if not REGISTRY_PATH.exists():
        return {}

    content = REGISTRY_PATH.read_text()
    ports = {}

    in_table = False
    for line in content.split("\n"):
        if "| Port |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|"):
            match = re.match(r"\|\s*(\d+)\s*\|\s*([^|]+)\s*\|", line)
            if match:
                port = int(match.group(1))
                service = match.group(2).strip()
                if service and not service.startswith("-"):
                    ports[port] = service
        elif in_table and not line.strip().startswith("|"):
            in_table = False

    return ports


def get_zosite_ports() -> dict[int, str]:
    """Scan Sites/ for zosite.json files and extract ports."""
    ports = {}
    if not SITES_DIR.exists():
        return ports

    for zosite in SITES_DIR.glob("*/zosite.json"):
        try:
            data = json.loads(zosite.read_text())
            port = data.get("local_port")
            if port:
                ports[port] = zosite.parent.name
        except (json.JSONDecodeError, KeyError):
            pass

    return ports


def get_service_ports() -> dict[int, list[dict]]:
    """Get ports from Zo user services API. Returns port -> list of services.
    
    Tries multiple methods:
    1. Direct curl to localhost:8111/services
    2. Fallback to cached services file
    """
    # Method 1: Try the API
    try:
        result = subprocess.run(
            ["curl", "-s", "-f", "http://localhost:8111/services"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            services = json.loads(result.stdout)
            if services:  # Non-empty list
                return _parse_services(services)
    except Exception:
        pass
    
    # Method 2: Try the Zo API via ZO_CLIENT_IDENTITY_TOKEN
    try:
        import requests
        token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        if token:
            # Use zo/ask to get services list
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": token,
                    "content-type": "application/json",
                },
                json={
                    "input": "List all user services using list_user_services tool. Return ONLY the raw JSON array, no commentary.",
                    "output_format": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "service_id": {"type": "string"},
                                "label": {"type": "string"},
                                "local_port": {"type": "integer"},
                                "protocol": {"type": "string"},
                                "created_at": {"type": "string"}
                            }
                        }
                    }
                },
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                services = data.get("output", [])
                if services:
                    return _parse_services(services)
    except Exception:
        pass
    
    # Method 3: Try cached services file
    cache_path = Path("/home/workspace/N5/data/services_cache.json")
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text())
            if data.get("services"):
                print("Warning: Using cached services data", file=sys.stderr)
                return _parse_services(data["services"])
        except Exception:
            pass
    
    print("Warning: Could not fetch services from any source", file=sys.stderr)
    return {}


def _parse_services(services: list[dict]) -> dict[int, list[dict]]:
    """Parse services list into port -> services mapping."""
    ports = {}
    for svc in services:
        port = svc.get("local_port")
        if port:
            if port not in ports:
                ports[port] = []
            ports[port].append({
                "service_id": svc.get("service_id"),
                "label": svc.get("label"),
                "protocol": svc.get("protocol"),
                "created_at": svc.get("created_at"),
            })
    return ports


def get_listening_ports() -> dict[int, list[str]]:
    """Get ports with active listeners via lsof. Returns port -> list of process names."""
    try:
        result = subprocess.run(
            ["lsof", "-i", "-P", "-n"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        ports = {}
        for line in result.stdout.split("\n"):
            if "LISTEN" in line:
                parts = line.split()
                if len(parts) >= 9:
                    process = parts[0]
                    # Extract port from address like *:8080 or 127.0.0.1:8080
                    addr = parts[8]
                    if ":" in addr:
                        try:
                            port = int(addr.split(":")[-1])
                            if port not in ports:
                                ports[port] = []
                            if process not in ports[port]:
                                ports[port].append(process)
                        except ValueError:
                            pass
        return ports
    except Exception as e:
        print(f"Warning: Could not get listening ports: {e}", file=sys.stderr)
    return {}


def detect_conflicts() -> list[Conflict]:
    """Perform three-way comparison and detect conflicts."""
    conflicts = []

    # Gather data from all sources
    registry_ports = get_registry_ports()
    zosite_ports = get_zosite_ports()
    service_ports = get_service_ports()
    listening_ports = get_listening_ports()

    # Combine registry + zosite as "intended"
    intended_ports = {**registry_ports}
    for port, name in zosite_ports.items():
        if port not in intended_ports:
            intended_ports[port] = f"{name} (zosite)"

    # Check 1: Duplicate registrations (CRITICAL)
    for port, services in service_ports.items():
        if len(services) > 1:
            conflicts.append(Conflict(
                port=port,
                conflict_type=ConflictType.DUPLICATE_REGISTRATION,
                severity=Severity.CRITICAL,
                description=f"Port {port} has {len(services)} services registered",
                details={
                    "services": [s["label"] for s in services],
                    "service_ids": [s["service_id"] for s in services],
                },
            ))

    # Check 2: Registry drift - service registered but not in registry (WARNING)
    for port, services in service_ports.items():
        if port not in registry_ports:
            # Check if it's a known zosite
            if port in zosite_ports:
                continue  # Zosites are okay
            for svc in services:
                conflicts.append(Conflict(
                    port=port,
                    conflict_type=ConflictType.REGISTRY_DRIFT,
                    severity=Severity.WARNING,
                    description=f"Service '{svc['label']}' on port {port} not in PORT_REGISTRY.md",
                    details={
                        "service": svc["label"],
                        "service_id": svc["service_id"],
                    },
                ))

    # Check 3: Unregistered listeners (INFO)
    all_registered_ports = set(service_ports.keys()) | set(zosite_ports.keys())
    for port, processes in listening_ports.items():
        # Skip well-known system ports
        if port < 1024 or port in [3100, 8111]:  # Loki, Zo internal
            continue
        if port not in all_registered_ports and port not in registry_ports:
            # Check if it's in a known range we don't track
            if 49152 <= port <= 65535:  # Ephemeral range
                continue
            conflicts.append(Conflict(
                port=port,
                conflict_type=ConflictType.UNREGISTERED_LISTENER,
                severity=Severity.INFO,
                description=f"Port {port} has listener(s) but is not registered",
                details={
                    "processes": processes,
                },
            ))

    # Sort by severity (critical first) then port
    severity_order = {Severity.CRITICAL: 0, Severity.WARNING: 1, Severity.INFO: 2}
    conflicts.sort(key=lambda c: (severity_order[c.severity], c.port))

    return conflicts


def format_report(conflicts: list[Conflict]) -> str:
    """Format conflicts as human-readable report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
    
    lines = [
        "=== PORT CONFLICT REPORT ===",
        f"Timestamp: {now}",
        "",
    ]

    if not conflicts:
        lines.append("✅ No conflicts detected")
        return "\n".join(lines)

    # Group by severity
    critical = [c for c in conflicts if c.severity == Severity.CRITICAL]
    warning = [c for c in conflicts if c.severity == Severity.WARNING]
    info = [c for c in conflicts if c.severity == Severity.INFO]

    if critical:
        lines.append("🔴 CRITICAL - Duplicate Registrations:")
        for c in critical:
            lines.append(f"   Port {c.port}:")
            for svc in c.details.get("services", []):
                lines.append(f"   - {svc}")
        lines.append("")

    if warning:
        lines.append("🟡 WARNING - Registry Drift:")
        for c in warning:
            lines.append(f"   Port {c.port}: {c.details.get('service', 'unknown')} not in PORT_REGISTRY.md")
        lines.append("")

    if info:
        lines.append("🔵 INFO - Unregistered Listeners:")
        for c in info:
            procs = ", ".join(c.details.get("processes", []))
            lines.append(f"   Port {c.port}: {procs}")
        lines.append("")

    lines.extend([
        f"Total conflicts: {len(conflicts)} ({len(critical)} critical, {len(warning)} warning, {len(info)} info)",
    ])

    return "\n".join(lines)


def load_state() -> dict:
    """Load alert state from disk."""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {"last_check": None, "known_conflicts": {}}


def save_state(state: dict) -> None:
    """Save alert state to disk."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def should_alert(conflict: Conflict, state: dict) -> bool:
    """Check if we should alert for this conflict (cooldown logic)."""
    key = f"{conflict.port}:{conflict.conflict_type.value}"
    known = state.get("known_conflicts", {}).get(key)
    
    if not known:
        return True  # New conflict
    
    # Check cooldown
    last_alerted = known.get("last_alerted")
    if last_alerted:
        last_time = datetime.fromisoformat(last_alerted.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) - last_time < timedelta(hours=ALERT_COOLDOWN_HOURS):
            return False  # Within cooldown
    
    return True  # Cooldown expired


def send_sms_alert(conflicts: list[Conflict]) -> bool:
    """Send SMS alert for conflicts. Returns True if sent."""
    if not conflicts:
        return False

    # Build message
    lines = ["🔴 Port Conflict Detected\n"]
    
    critical = [c for c in conflicts if c.severity == Severity.CRITICAL]
    if critical:
        for c in critical:
            services = c.details.get("services", [])
            lines.append(f"Port {c.port} has duplicate services:")
            for svc in services[:3]:  # Limit to avoid SMS length issues
                lines.append(f"- {svc}")
    else:
        # Summarize non-critical
        lines.append(f"{len(conflicts)} port issue(s) detected.")
        lines.append("Run: python3 N5/scripts/port_conflict_detector.py check")
    
    lines.append("\nFix: Delete duplicate or reassign port.")
    
    message = "\n".join(lines)
    
    # Use zo/ask to send SMS (we're in a script context)
    try:
        import requests
        token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
        if not token:
            print("Warning: No ZO_CLIENT_IDENTITY_TOKEN, cannot send SMS", file=sys.stderr)
            return False
        
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json",
            },
            json={
                "input": f"Send this SMS to V immediately (use send_sms_to_user tool): {message}"
            },
            timeout=30,
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Warning: Could not send SMS: {e}", file=sys.stderr)
        return False


def cmd_check(args) -> int:
    """Run conflict detection and report."""
    conflicts = detect_conflicts()
    
    if args.json:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conflicts": [c.to_dict() for c in conflicts],
            "summary": {
                "total": len(conflicts),
                "critical": len([c for c in conflicts if c.severity == Severity.CRITICAL]),
                "warning": len([c for c in conflicts if c.severity == Severity.WARNING]),
                "info": len([c for c in conflicts if c.severity == Severity.INFO]),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_report(conflicts))
    
    if args.exit_code and conflicts:
        # Exit 1 if any critical conflicts
        if any(c.severity == Severity.CRITICAL for c in conflicts):
            return 1
    return 0


def cmd_alert(args) -> int:
    """Check for conflicts and alert if new ones found."""
    conflicts = detect_conflicts()
    state = load_state()
    
    # Filter to alertable conflicts
    alertable = [c for c in conflicts if c.severity == Severity.CRITICAL and should_alert(c, state)]
    
    if alertable:
        print(f"Found {len(alertable)} new/recurring conflict(s), sending alert...")
        if send_sms_alert(alertable):
            print("SMS alert sent.")
            # Update state
            now = datetime.now(timezone.utc).isoformat()
            for c in alertable:
                key = f"{c.port}:{c.conflict_type.value}"
                if key not in state.get("known_conflicts", {}):
                    state.setdefault("known_conflicts", {})[key] = {
                        "first_seen": now,
                    }
                state["known_conflicts"][key]["last_alerted"] = now
        else:
            print("Failed to send SMS alert.")
    else:
        print(f"No new conflicts to alert. ({len(conflicts)} total, {len([c for c in conflicts if c.severity == Severity.CRITICAL])} critical)")
    
    # Always update last_check
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    
    # Clean up resolved conflicts
    current_keys = {f"{c.port}:{c.conflict_type.value}" for c in conflicts}
    state["known_conflicts"] = {
        k: v for k, v in state.get("known_conflicts", {}).items()
        if k in current_keys
    }
    
    save_state(state)
    
    # Print summary
    print(format_report(conflicts))
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Port Conflict Detector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check command
    check_parser = subparsers.add_parser("check", help="Check for conflicts")
    check_parser.add_argument("--json", action="store_true", help="JSON output")
    check_parser.add_argument("--exit-code", action="store_true", help="Exit 1 if conflicts")

    # alert command
    subparsers.add_parser("alert", help="Check and alert if new conflicts")

    args = parser.parse_args()

    if args.command == "check":
        sys.exit(cmd_check(args))
    elif args.command == "alert":
        sys.exit(cmd_alert(args))


if __name__ == "__main__":
    main()
