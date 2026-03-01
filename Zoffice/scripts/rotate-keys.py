#!/usr/bin/env python3
"""
API key rotation placeholder for Zoffice.

Usage:
    python rotate-keys.py [--dry-run] [--service SERVICE]

This is a Layer 1 placeholder. Full key rotation requires:
- A secrets backend (Zo env vars, vault, or encrypted file)
- Service-specific rotation logic per capability
- Audit logging of rotation events

Currently: lists configured services and their key status.
"""

import argparse
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

ZOFFICE_ROOT = "/home/workspace/Zoffice"


def get_capabilities():
    """Read capabilities config to find services that may need keys."""
    if not yaml:
        return {}

    cap_path = os.path.join(ZOFFICE_ROOT, "config", "capabilities.yaml")
    if not os.path.isfile(cap_path):
        return {}

    with open(cap_path) as f:
        data = yaml.safe_load(f)

    return data.get("capabilities", {})


def check_key_status(service_name):
    """Check if env var exists for a service key."""
    env_patterns = [
        f"ZO_{service_name.upper()}_KEY",
        f"ZO_{service_name.upper()}_API_KEY",
        f"{service_name.upper()}_API_KEY",
    ]
    for pattern in env_patterns:
        val = os.environ.get(pattern)
        if val:
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "****"
            return pattern, masked
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Zoffice key rotation utility")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be rotated")
    parser.add_argument("--service", help="Rotate keys for specific service only")
    args = parser.parse_args()

    print("Zoffice Key Rotation")
    print("=" * 40)

    capabilities = get_capabilities()
    if not capabilities:
        print("No capabilities configured or PyYAML not available.")
        print("This is a Layer 1 placeholder — full rotation requires secrets backend.")
        sys.exit(0)

    print(f"\nConfigured capabilities: {len(capabilities)}")
    print()

    for cap_name, cap_config in capabilities.items():
        if args.service and cap_name != args.service:
            continue

        status = cap_config.get("status", "unknown")
        env_var, masked = check_key_status(cap_name)

        if env_var:
            print(f"  {cap_name}: status={status}, key={env_var} ({masked})")
            if args.dry_run:
                print(f"    -> Would rotate {env_var}")
        else:
            print(f"  {cap_name}: status={status}, no key found in env")

    print()
    if args.dry_run:
        print("DRY RUN — no keys were rotated.")
    else:
        print("NOTE: Full key rotation not yet implemented.")
        print("This is a Layer 1 placeholder. Use --dry-run to preview.")


if __name__ == "__main__":
    main()
