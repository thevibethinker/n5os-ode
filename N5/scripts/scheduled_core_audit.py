#!/usr/bin/env python3
"""
Daily core-manifest audit runner
Lightweight scheduled task that calls the audit engine and exits silently
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Just re-use the audit engine, no extra logic
cmd = [sys.executable, str(ROOT / "scripts" / "core_audit.py")]
proc = subprocess.run(cmd, capture_output=True, text=True)
sys.exit(proc.returncode)  # 0 if all good, 1 if issues found