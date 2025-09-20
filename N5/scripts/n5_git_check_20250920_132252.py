import argparse

#!/usr/bin/env python3
"""
N5 Git Check: Launch git_change_checker.py for auditing staged changes.
"""

import sys
import subprocess
from pathlib import Path

def main():
    # Run the checker script
    checker_path = Path(__file__).parent / "git_change_checker_20250920_132252.py"
    if not checker_path.exists():
        print("❌ git_change_checker.py not found", file=sys.stderr)
        sys.exit(1)
    
    result = subprocess.run([sys.executable, str(checker_path)], cwd="/home/workspace/N5")
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()