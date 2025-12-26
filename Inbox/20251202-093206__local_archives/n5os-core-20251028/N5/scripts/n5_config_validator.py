#!/usr/bin/env python3
import sys
from pathlib import Path

N5_ROOT = Path("/home/workspace/N5")

def main():
    print("Validating N5 configuration...")
    commands_file = N5_ROOT / "config" / "commands.jsonl"
    if not commands_file.exists():
        print("✗ commands.jsonl not found")
        return 1
    print("✓ commands.jsonl OK")
    schemas_dir = N5_ROOT / "schemas"
    if not schemas_dir.exists():
        print("✗ schemas/ not found")
        return 1
    print("✓ schemas/ OK")
    print("\n✓ Config valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
