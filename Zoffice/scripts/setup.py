#!/usr/bin/env python3
"""
Zoffice First-Run Setup — customizes a fresh Zoffice installation.

Usage:
    python setup.py [--dry-run]
    python setup.py --name "My Office" --owner "Alice" --handle "alice" [--parent va.zo.computer]

Interactive mode (no args): prompts for each value.
Non-interactive mode: pass values as flags.

Writes values into:
  - Zoffice/config/office.yaml
  - Zoffice/MANIFEST.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ZOFFICE_ROOT = "/home/workspace/Zoffice"

try:
    import yaml
except ImportError:
    yaml = None


def read_yaml(path):
    if not yaml:
        print("ERROR: PyYAML not installed")
        sys.exit(1)
    with open(path) as f:
        return yaml.safe_load(f)


def write_yaml(path, data):
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def prompt_value(label, current=None, required=False):
    """Prompt user for a value with optional current default."""
    suffix = f" [{current}]" if current else ""
    while True:
        val = input(f"  {label}{suffix}: ").strip()
        if not val and current:
            return current
        if not val and required:
            print(f"    {label} is required.")
            continue
        return val if val else None


def setup_interactive(dry_run=False):
    """Interactive first-run setup."""
    print("=" * 50)
    print("  Zoffice First-Run Setup")
    print("=" * 50)
    print()

    office_yaml_path = os.path.join(ZOFFICE_ROOT, "config", "office.yaml")
    manifest_path = os.path.join(ZOFFICE_ROOT, "MANIFEST.json")

    if not os.path.isfile(office_yaml_path):
        print(f"ERROR: {office_yaml_path} not found. Run install.py first.")
        sys.exit(1)

    office_data = read_yaml(office_yaml_path)
    manifest_data = read_json(manifest_path)

    office = office_data.get("office", {})

    print("Configure your Zoffice identity:\n")
    name = prompt_value("Office name", office.get("name"), required=True)
    owner = prompt_value("Owner name", office.get("owner"), required=True)
    handle = prompt_value("Zo handle", office.get("handle"))
    domain = prompt_value("Domain (optional)", office.get("domain"))
    parent = prompt_value("Parent Zo instance (optional)", office.get("parent"))

    now = datetime.now(timezone.utc).isoformat()

    print()
    print("-" * 50)
    print("Review:")
    print(f"  Name:    {name}")
    print(f"  Owner:   {owner}")
    print(f"  Handle:  {handle or '(none)'}")
    print(f"  Domain:  {domain or '(none)'}")
    print(f"  Parent:  {parent or '(none)'}")
    print(f"  Time:    {now}")
    print("-" * 50)

    if dry_run:
        print("\nDRY RUN — no changes written.")
        return

    # Update office.yaml
    office["name"] = name
    office["owner"] = owner
    office["handle"] = handle
    office["domain"] = domain
    office["parent"] = parent
    office["installed_at"] = now
    office_data["office"] = office
    write_yaml(office_yaml_path, office_data)
    print(f"\nUpdated: {office_yaml_path}")

    # Update MANIFEST.json
    manifest_data["instance"] = {
        "name": name,
        "handle": handle,
        "owner": owner,
        "parent": parent,
    }
    manifest_data["installed_at"] = now
    manifest_data["installed_by"] = "setup.py"
    write_json(manifest_path, manifest_data)
    print(f"Updated: {manifest_path}")

    print("\nSetup complete. Run healthcheck.py to verify.")


def setup_noninteractive(args):
    """Non-interactive setup using CLI flags."""
    office_yaml_path = os.path.join(ZOFFICE_ROOT, "config", "office.yaml")
    manifest_path = os.path.join(ZOFFICE_ROOT, "MANIFEST.json")

    if not os.path.isfile(office_yaml_path):
        print(f"ERROR: {office_yaml_path} not found. Run install.py first.")
        sys.exit(1)

    office_data = read_yaml(office_yaml_path)
    manifest_data = read_json(manifest_path)

    now = datetime.now(timezone.utc).isoformat()

    office = office_data.get("office", {})
    office["name"] = args.name
    office["owner"] = args.owner
    office["handle"] = args.handle
    office["domain"] = args.domain
    office["parent"] = args.parent
    office["installed_at"] = now
    office_data["office"] = office

    manifest_data["instance"] = {
        "name": args.name,
        "handle": args.handle,
        "owner": args.owner,
        "parent": args.parent,
    }
    manifest_data["installed_at"] = now
    manifest_data["installed_by"] = "setup.py"

    if args.dry_run:
        print("DRY RUN — would update:")
        print(f"  office.yaml: name={args.name}, owner={args.owner}, handle={args.handle}")
        print(f"  MANIFEST.json: instance updated, installed_at={now}")
        return

    write_yaml(office_yaml_path, office_data)
    write_json(manifest_path, manifest_data)
    print(f"Setup complete: {args.name} (owner: {args.owner})")


def main():
    parser = argparse.ArgumentParser(description="Zoffice first-run setup")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--name", help="Office name")
    parser.add_argument("--owner", help="Owner name")
    parser.add_argument("--handle", help="Zo handle")
    parser.add_argument("--domain", help="Domain (optional)")
    parser.add_argument("--parent", help="Parent Zo instance (optional)")
    args = parser.parse_args()

    if args.name and args.owner:
        setup_noninteractive(args)
    elif args.name or args.owner:
        print("ERROR: Both --name and --owner are required for non-interactive mode.")
        sys.exit(1)
    else:
        setup_interactive(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
