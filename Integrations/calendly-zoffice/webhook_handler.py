#!/usr/bin/env python3
"""Compatibility wrapper.

Historically, Drop D2.3 used this path.

Current implementation lives at:
  Integrations/calendly-zoffice/scripts/webhook_handler.py

This wrapper preserves `stdin` behavior.
"""

import os
import subprocess
import sys


def main() -> None:
    cmd = [
        'python3',
        '/home/workspace/Integrations/calendly-zoffice/scripts/webhook_handler.py',
        '--stdin',
    ]
    # Forward stdin directly
    proc = subprocess.run(cmd, stdin=sys.stdin)
    raise SystemExit(proc.returncode)


if __name__ == '__main__':
    main()
