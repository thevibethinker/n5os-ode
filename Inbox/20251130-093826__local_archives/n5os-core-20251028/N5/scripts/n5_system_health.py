#!/usr/bin/env python3
import sys
from pathlib import Path

N5_ROOT = Path("/home/workspace/N5")

def main():
    print("\nN5 SYSTEM HEALTH CHECK")
    print("=" * 40)
    
    required = [
        N5_ROOT / "commands",
        N5_ROOT / "scripts",
        N5_ROOT / "config",
        N5_ROOT / "schemas"
    ]
    
    issues = []
    for directory in required:
        if not directory.exists():
            print(f"✗ {directory.name} missing")
            issues.append(directory.name)
        else:
            print(f"✓ {directory.name} OK")
    
    if issues:
        print(f"\n✗ UNHEALTHY: Missing {', '.join(issues)}")
        return 1
    
    print("\n✓ HEALTHY")
    return 0

if __name__ == "__main__":
    sys.exit(main())
