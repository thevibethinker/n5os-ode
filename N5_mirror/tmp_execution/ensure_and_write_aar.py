#!/usr/bin/env python3
"""
Wrapper to run the orchestrator launcher and produce a deterministic AAR file.

Usage:
  python3 ensure_and_write_aar.py --plan-file <path> [--mirror-n5] [--execute]

This script runs the existing launcher, captures its output, finds the resolved command JSON,
and writes a stable AAR to N5/tmp_execution/AAR_<timestamp>.md so it won't be moved.
"""
import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import re

ROOT = Path('/home/workspace')
TMP_DIR = ROOT / 'N5' / 'tmp_execution'
LAUNCHER = ROOT / 'N5' / 'command_authoring' / 'orchestrator_launcher.py'
RESOLVED_GLOB = TMP_DIR.glob('resolved_command_*.json')


def _extract_intended(plan_text: str) -> str:
    m = re.search(r"\*\*Intended Outcome\*\*\s*:\s*(.+)", plan_text)
    if m:
        return m.group(1).strip()
    m = re.search(r"Intended Outcome\s*:\s*(.+)", plan_text)
    return m.group(1).strip() if m else '(not specified)'


def find_latest_resolved():
    files = sorted(TMP_DIR.glob('resolved_command_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if files:
        return files[0]
    # fallback to author-command directory
    alt = ROOT / 'N5' / 'scripts' / 'author-command' / 'resolved_command.json'
    return alt if alt.exists() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-file', required=True)
    parser.add_argument('--mirror-n5', action='store_true')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()

    plan = Path(args.plan_file)
    if not plan.exists():
        print('Plan file not found:', plan)
        sys.exit(1)

    cmd = [sys.executable, str(LAUNCHER), '--plan-file', str(plan)]
    if args.mirror_n5:
        cmd.append('--mirror-n5')
    if args.execute:
        cmd.append('--execute')

    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout
    err = proc.stderr
    rc = proc.returncode

    # locate resolved command
    resolved = find_latest_resolved()
    resolved_data = {}
    if resolved and resolved.exists():
        try:
            resolved_data = json.loads(resolved.read_text(encoding='utf-8'))
        except Exception:
            resolved_data = {}

    # build AAR
    plan_text = plan.read_text(encoding='utf-8')
    intended = _extract_intended(plan_text)
    resolved_name = resolved_data.get('resolved_command', {}).get('name') if isinstance(resolved_data, dict) else None
    if not resolved_name:
        resolved_name = resolved_data.get('name') if isinstance(resolved_data, dict) else '(unknown)'

    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    aar_path = TMP_DIR / f'AAR_{ts}.md'

    aar = []
    aar.append(f"# After-Action Report for Orchestrator Launch")
    aar.append(f"- **Execution Thread ID**: exec_{ts}")
    aar.append(f"- **Original Plan Reference**: {plan}")
    aar.append("")
    aar.append("## Intended vs. Actual")
    aar.append(f"- Intended: {intended}")
    aar.append(f"- Actual: Generated command: {resolved_name}; exit_code={rc}")
    aar.append("- Discrepancies: None identified automatically")
    aar.append("")
    aar.append("## Launcher stdout (trimmed)")
    for line in out.splitlines()[-50:]:
        aar.append(f"- {line}")
    if err:
        aar.append("")
        aar.append("## Launcher stderr (trimmed)")
        for line in err.splitlines()[-50:]:
            aar.append(f"- {line}")

    aar.append("")
    aar.append("## Resolved JSON (path)")
    aar.append(str(resolved) if resolved else 'None')

    aar_content = '\n'.join(aar)
    aar_path.write_text(aar_content, encoding='utf-8')

    print(str(aar_path))
    print('exit_code:', rc)
    # also print small preview
    print('\n--- AAR preview ---\n')
    print('\n'.join(aar[:30]))

if __name__ == '__main__':
    main()
