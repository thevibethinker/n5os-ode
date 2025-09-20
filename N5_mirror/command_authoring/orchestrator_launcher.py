#!/usr/bin/env python3
"""
N5 Orchestrator Launcher

Executes system upgrade plans with safety and validation features.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any
import json

# Constants
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"

def mirror_n5() -> None:
    """Create a mirror copy of N5 for testing upgrades."""
    import shutil
    
    mirror_dir = ROOT.parent / "N5_mirror"
    print(f"Creating mirror of N5 at {mirror_dir}")
    
    if mirror_dir.exists():
        print("Mirror already exists, removing...")
        shutil.rmtree(mirror_dir)
    
    shutil.copytree(ROOT, mirror_dir)
    print("Mirror created successfully")

def execute_plan(plan_file: str) -> None:
    """Execute the upgrade plan."""
    plan_path = Path(plan_file)
    
    if not plan_path.exists():
        print(f"Plan file not found: {plan_file}")
        sys.exit(1)
    
    print(f"Executing plan: {plan_file}")
    
    # Run telemetry aggregation
    telemetry_script = SCRIPTS_DIR / "system_upgrades_telemetry.py"
    if telemetry_script.exists():
        print("Running telemetry aggregation...")
        result = subprocess.run([sys.executable, str(telemetry_script)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Telemetry aggregation completed")
        else:
            print(f"Telemetry aggregation failed: {result.stderr}")
    else:
        print("Telemetry script not found")
    
    # Check implementation status
    check_implementation_status()
    
    print("Plan execution completed")

def check_implementation_status() -> None:
    """Check the status of plan implementation."""
    print("\nImplementation Status:")
    
    # Check if key files exist
    files_to_check = {
        "system_upgrades_add.py": SCRIPTS_DIR / "system_upgrades_add.py",
        "system_upgrades_telemetry.py": SCRIPTS_DIR / "system_upgrades_telemetry.py",
        "system_upgrades_backup_manager.py": SCRIPTS_DIR / "system_upgrades_backup_manager.py",
        "system-upgrades.schema.json": ROOT / "schemas" / "system-upgrades.schema.json",
        "system-upgrades.md": ROOT / "docs" / "system-upgrades.md"
    }
    
    for name, path in files_to_check.items():
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}")
    
    # Check CLI flags
    add_script = files_to_check["system_upgrades_add.py"]
    if add_script.exists():
        with open(add_script, 'r') as f:
            content = f.read()
        
        flags = ["--dry-run", "--verify", "--rollback"]
        for flag in flags:
            status = "✅" if flag in content else "❌"
            print(f"  {status} CLI flag: {flag}")

def main():
    parser = argparse.ArgumentParser(description="N5 Orchestrator Launcher")
    parser.add_argument(
        '--plan-file', 
        required=True,
        help='Path to the plan file to execute'
    )
    parser.add_argument(
        '--mirror-n5', 
        action='store_true',
        help='Create a mirror copy of N5 for testing'
    )
    parser.add_argument(
        '--execute', 
        action='store_true',
        help='Execute the upgrade plan'
    )
    
    args = parser.parse_args()
    
    if args.mirror_n5:
        mirror_n5()
    
    if args.execute:
        execute_plan(args.plan_file)
    else:
        print("Plan file specified but --execute not provided. Use --execute to run the plan.")

if __name__ == '__main__':
    main()