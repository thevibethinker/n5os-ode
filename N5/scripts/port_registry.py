#!/usr/bin/env python3
"""
Port Registry Manager - Single source of truth for port allocations.

Usage:
    python3 port_registry.py check <port>       Check if port is in use
    python3 port_registry.py next [range]       Get next available port
    python3 port_registry.py list               List all allocated ports
    python3 port_registry.py sync               Sync registry from services + zosites
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from N5.lib.paths import N5_CONFIG_DIR, WORKSPACE_ROOT
    REGISTRY_PATH = N5_CONFIG_DIR / "PORT_REGISTRY.md"
    SITES_DIR = WORKSPACE_ROOT / "Sites"
except ImportError:
    REGISTRY_PATH = Path("/home/workspace/N5/config/PORT_REGISTRY.md")
    SITES_DIR = Path("/home/workspace/Sites")

# Define port ranges
RANGES = {
    "sites": (3000, 3499),
    "n5-services": (8763, 8844),
    "webhooks": (8845, 8899),
    "automation": (8900, 8999),
    "mid-ephemeral": (50000, 51999),
    "high-ephemeral": (52000, 58999),
}


def get_allocated_ports() -> dict[int, str]:
    """Parse PORT_REGISTRY.md and return allocated ports."""
    if not REGISTRY_PATH.exists():
        return {}
    
    content = REGISTRY_PATH.read_text()
    ports = {}
    
    # Parse the table - look for lines like "| 8765 | service-name |"
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
                site_name = zosite.parent.name
                ports[port] = site_name
        except (json.JSONDecodeError, KeyError):
            pass
    
    return ports


def get_service_ports() -> dict[int, str]:
    """Get ports from Zo user services."""
    try:
        # Try to get from the zo services API endpoint
        result = subprocess.run(
            ["curl", "-s", "http://localhost:8111/services"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            services = json.loads(result.stdout)
            return {s["local_port"]: s["label"] for s in services if "local_port" in s}
    except Exception:
        pass
    return {}


def check_port(port: int) -> None:
    """Check if a port is allocated or in use."""
    allocated = get_allocated_ports()
    zosite_ports = get_zosite_ports()
    
    # Check registry first
    if port in allocated:
        print(f"❌ Port {port} is ALLOCATED to: {allocated[port]}")
        print(f"   Source: PORT_REGISTRY.md")
        sys.exit(1)
    
    # Check zosite.json files (might not be in registry yet)
    if port in zosite_ports:
        print(f"⚠️  Port {port} is used by zosite: {zosite_ports[port]}")
        print(f"   (Not in registry - run 'sync' to update)")
        sys.exit(1)
    
    # Check if anything is actually listening
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-P", "-n"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "LISTEN" in result.stdout:
            lines = [l for l in result.stdout.split("\n") if "LISTEN" in l]
            if lines:
                process = lines[0].split()[0]
                print(f"⚠️  Port {port} has active listener: {process}")
                print(f"   (Not in registry - may be orphaned)")
                sys.exit(1)
    except Exception:
        pass
    
    print(f"✅ Port {port} is AVAILABLE")
    for name, (low, high) in RANGES.items():
        if low <= port <= high:
            print(f"   Range: {name} ({low}-{high})")
            break
    sys.exit(0)


def get_next_port(range_name: str = "n5-services") -> None:
    """Get next available port in a range."""
    if range_name not in RANGES:
        print(f"Unknown range: {range_name}")
        print(f"Available: {', '.join(RANGES.keys())}")
        sys.exit(1)
    
    low, high = RANGES[range_name]
    allocated = get_allocated_ports()
    zosite_ports = get_zosite_ports()
    all_used = set(allocated.keys()) | set(zosite_ports.keys())
    
    for port in range(low, high + 1):
        if port not in all_used:
            print(f"✅ Next available in {range_name}: {port}")
            sys.exit(0)
    
    print(f"❌ No ports available in {range_name} ({low}-{high})")
    sys.exit(1)


def list_ports() -> None:
    """List all allocated ports from all sources."""
    allocated = get_allocated_ports()
    zosite_ports = get_zosite_ports()
    
    # Merge, noting source
    all_ports = {}
    for port, service in allocated.items():
        all_ports[port] = (service, "registry")
    for port, service in zosite_ports.items():
        if port not in all_ports:
            all_ports[port] = (service, "zosite-only")
        else:
            all_ports[port] = (all_ports[port][0], "registry+zosite")
    
    if not all_ports:
        print("No ports allocated.")
        return
    
    print(f"{'Port':<8} {'Service':<35} {'Source':<15}")
    print("-" * 60)
    for port in sorted(all_ports.keys()):
        service, source = all_ports[port]
        print(f"{port:<8} {service:<35} {source:<15}")
    
    print(f"\nTotal: {len(all_ports)} ports")
    
    # Check for untracked zosite ports
    untracked = set(zosite_ports.keys()) - set(allocated.keys())
    if untracked:
        print(f"\n⚠️  {len(untracked)} zosite ports NOT in registry: {sorted(untracked)}")
        print("   Run 'sync' to update registry")


def sync_registry() -> None:
    """Sync registry with current services and zosites."""
    print("Scanning for port allocations...")
    
    allocated = get_allocated_ports()
    zosite_ports = get_zosite_ports()
    service_ports = get_service_ports()
    
    # Find gaps
    missing_zosites = set(zosite_ports.keys()) - set(allocated.keys())
    missing_services = set(service_ports.keys()) - set(allocated.keys())
    
    print(f"\nRegistry has {len(allocated)} entries")
    print(f"Zosite.json files have {len(zosite_ports)} ports")
    print(f"Running services have {len(service_ports)} ports")
    
    if missing_zosites:
        print(f"\n⚠️  Zosite ports missing from registry:")
        for port in sorted(missing_zosites):
            print(f"   {port}: {zosite_ports[port]}")
    
    if missing_services:
        print(f"\n⚠️  Service ports missing from registry:")
        for port in sorted(missing_services):
            print(f"   {port}: {service_ports[port]}")
    
    if not missing_zosites and not missing_services:
        print("\n✅ Registry is in sync")
    else:
        print("\n→ Update PORT_REGISTRY.md manually with missing entries")


def main():
    parser = argparse.ArgumentParser(description="Port Registry Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check if port is available")
    check_parser.add_argument("port", type=int)
    
    # next command
    next_parser = subparsers.add_parser("next", help="Get next available port")
    next_parser.add_argument("range", nargs="?", default="n5-services",
                            help=f"Range name: {', '.join(RANGES.keys())}")
    
    # list command
    subparsers.add_parser("list", help="List all allocated ports")
    
    # sync command
    subparsers.add_parser("sync", help="Sync registry from services + zosites")
    
    args = parser.parse_args()
    
    if args.command == "check":
        check_port(args.port)
    elif args.command == "next":
        get_next_port(args.range)
    elif args.command == "list":
        list_ports()
    elif args.command == "sync":
        sync_registry()


if __name__ == "__main__":
    main()


