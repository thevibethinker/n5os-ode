#!/usr/bin/env python3
"""
Pulse Sentinel: Lightweight monitor for active builds.

Designed to run as a scheduled agent every 3 minutes.
- If no active builds: exits immediately (cheap)
- If active builds: runs pulse tick for each
- Checks for pause/stop signals before running

Control signals (set via N5/config/pulse_control.json):
  - "active": normal operation
  - "paused": skip ticks, stay alive
  - "stopped": exit, agent should be deleted
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from pulse_common import PATHS, WORKSPACE

BUILDS_DIR = PATHS.BUILDS
CONTROL_FILE = PATHS.WORKSPACE / "N5" / "config" / "pulse_control.json"

def get_control_state() -> dict:
    """Read control state, create default if missing"""
    if not CONTROL_FILE.exists():
        CONTROL_FILE.parent.mkdir(parents=True, exist_ok=True)
        default = {"state": "active", "updated_at": datetime.now(timezone.utc).isoformat()}
        with open(CONTROL_FILE, 'w') as f:
            json.dump(default, f, indent=2)
        return default
    
    with open(CONTROL_FILE) as f:
        return json.load(f)

def find_active_builds() -> list[str]:
    """Find all builds with status=active"""
    active = []
    if not BUILDS_DIR.exists():
        return active
    
    for meta_path in BUILDS_DIR.glob("*/meta.json"):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            if meta.get("status") == "active":
                active.append(meta.get("slug", meta_path.parent.name))
        except (json.JSONDecodeError, KeyError):
            continue
    
    return active

def main():
    # Check control state
    control = get_control_state()
    state = control.get("state", "active")
    
    if state == "stopped":
        print("[SENTINEL] Stop signal detected. Agent should be deleted.")
        sys.exit(0)
    
    if state == "paused":
        print("[SENTINEL] Paused. Skipping tick.")
        sys.exit(0)
    
    # Find active builds
    active_builds = find_active_builds()
    
    if not active_builds:
        print("[SENTINEL] No active builds. Idle.")
        sys.exit(0)
    
    print(f"[SENTINEL] Found {len(active_builds)} active build(s): {', '.join(active_builds)}")
    
    # Import and run pulse tick for each
    # We import here to avoid loading heavy deps when idle
    from pulse import tick
    import asyncio
    
    for slug in active_builds:
        print(f"[SENTINEL] Ticking {slug}...")
        try:
            asyncio.run(tick(slug))
        except Exception as e:
            print(f"[SENTINEL] Error ticking {slug}: {e}")
    
    print("[SENTINEL] Tick cycle complete.")

if __name__ == "__main__":
    main()
