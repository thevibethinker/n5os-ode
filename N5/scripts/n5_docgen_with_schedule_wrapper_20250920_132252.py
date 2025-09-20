import argparse

#!/usr/bin/env python3
"""
N5 docgen command wrapped with scheduling wrapper invocation
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    # Forward all args except command name
    args = sys.argv[1:]

    wrapper_script = ROOT / "scripts" / "n5_schedule_wrapper.py"
    if not wrapper_script.exists():
        print(f"Scheduling wrapper script not found: {wrapper_script}", file=sys.stderr)
        return 1

    command = [sys.executable, str(wrapper_script), "docgen"] + args

    print(f"Running docgen with scheduling wrapper...")

    result = subprocess.run(command, capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
