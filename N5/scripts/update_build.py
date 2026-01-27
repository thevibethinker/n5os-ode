#!/usr/bin/env python3
"""Build state management for v2/Pulse builds.

Commands:
  status <slug>     Show build status
  complete <slug> <drop_id>   Mark drop complete with deposit
  close <slug>      Close build (mark as complete)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def get_build_dir(slug: str) -> Path:
    return Path(f"/home/workspace/N5/builds/{slug}")

def cmd_status(slug: str) -> int:
    """Show build status."""
    build_dir = get_build_dir(slug)
    meta_path = build_dir / "meta.json"
    
    if not meta_path.exists():
        print(f"Build not found: {slug}", file=sys.stderr)
        return 1
    
    meta = json.loads(meta_path.read_text())
    
    print(f"Build: {slug}")
    print(f"Title: {meta.get('title', 'Untitled')}")
    print(f"Status: {meta.get('status', 'unknown')}")
    print(f"Streams: {meta.get('current_stream', 0)}/{meta.get('total_streams', 0)}")
    print()
    print("Drops:")
    
    for drop_id, drop in sorted(meta.get('drops', {}).items()):
        status_emoji = {
            'pending': '⏳',
            'spawned': '🚀',
            'complete': '✅',
            'failed': '❌',
            'dead': '💀',
        }.get(drop.get('status', 'pending'), '❓')
        print(f"  {status_emoji} {drop_id}: {drop.get('name', 'Unnamed')} [{drop.get('status', 'pending')}]")
    
    # Show deposits
    deposits_dir = build_dir / "deposits"
    if deposits_dir.exists():
        deposits = list(deposits_dir.glob("D*.json"))
        deposits = [d for d in deposits if '_filter' not in d.name and '_forensics' not in d.name]
        if deposits:
            print()
            print(f"Deposits: {len(deposits)}")
            for d in sorted(deposits):
                print(f"  - {d.name}")
    
    return 0

def cmd_complete(slug: str, drop_id: str, status: str = "complete", 
                 summary: str = None, artifacts: str = None,
                 learnings: str = None, concerns: str = None,
                 decisions: str = None) -> int:
    """Mark a drop as complete and write deposit."""
    build_dir = get_build_dir(slug)
    meta_path = build_dir / "meta.json"
    
    if not meta_path.exists():
        print(f"Build not found: {slug}", file=sys.stderr)
        return 1
    
    # Update meta.json
    meta = json.loads(meta_path.read_text())
    if drop_id not in meta.get('drops', {}):
        print(f"Drop not found: {drop_id}", file=sys.stderr)
        return 1
    
    meta['drops'][drop_id]['status'] = status
    meta['drops'][drop_id]['completed_at'] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=2))
    
    # Write deposit
    deposit = {
        'drop_id': drop_id,
        'status': status,
        'completed_at': datetime.now(timezone.utc).isoformat(),
        'summary': summary or '',
        'artifacts': artifacts.split(',') if artifacts else [],
        'learnings': learnings or '',
        'concerns': concerns or '',
        'decisions': json.loads(decisions) if decisions else [],
    }
    
    deposits_dir = build_dir / "deposits"
    deposits_dir.mkdir(exist_ok=True)
    deposit_path = deposits_dir / f"{drop_id}.json"
    deposit_path.write_text(json.dumps(deposit, indent=2))
    
    print(f"✓ {drop_id} marked {status}")
    print(f"  Deposit: {deposit_path}")
    return 0

def cmd_close(slug: str) -> int:
    """Close/finalize a build."""
    build_dir = get_build_dir(slug)
    meta_path = build_dir / "meta.json"
    
    if not meta_path.exists():
        print(f"Build not found: {slug}", file=sys.stderr)
        return 1
    
    meta = json.loads(meta_path.read_text())
    
    # Check all drops are terminal
    non_terminal = [
        d_id for d_id, d in meta.get('drops', {}).items()
        if d.get('status') not in ('complete', 'failed', 'dead', 'skipped')
    ]
    
    if non_terminal:
        print(f"Cannot close: {len(non_terminal)} drops not terminal")
        for d_id in non_terminal:
            print(f"  - {d_id}: {meta['drops'][d_id].get('status', 'pending')}")
        return 1
    
    # Count outcomes
    complete = len([d for d in meta['drops'].values() if d.get('status') == 'complete'])
    failed = len([d for d in meta['drops'].values() if d.get('status') in ('failed', 'dead')])
    total = len(meta['drops'])
    
    if failed == 0:
        meta['status'] = 'complete'
    elif complete > 0:
        meta['status'] = 'partial'
    else:
        meta['status'] = 'failed'
    
    meta['closed_at'] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, indent=2))
    
    print(f"✓ Build {slug} closed as {meta['status']}")
    print(f"  {complete}/{total} complete, {failed} failed")
    return 0

def main():
    parser = argparse.ArgumentParser(description='Build state management')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # status
    p_status = subparsers.add_parser('status', help='Show build status')
    p_status.add_argument('slug', help='Build slug')
    
    # complete
    p_complete = subparsers.add_parser('complete', help='Mark drop complete')
    p_complete.add_argument('slug', help='Build slug')
    p_complete.add_argument('drop_id', help='Drop ID (e.g., D1.1)')
    p_complete.add_argument('--status', default='complete', 
                           choices=['complete', 'partial', 'failed', 'blocked'])
    p_complete.add_argument('--summary', help='Summary of work done')
    p_complete.add_argument('--artifacts', help='Comma-separated artifact paths')
    p_complete.add_argument('--learnings', help='Key learnings')
    p_complete.add_argument('--concerns', help='Concerns for orchestrator')
    p_complete.add_argument('--decisions', help='JSON array of {decision, rationale}')
    
    # close
    p_close = subparsers.add_parser('close', help='Close/finalize build')
    p_close.add_argument('slug', help='Build slug')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        return cmd_status(args.slug)
    elif args.command == 'complete':
        return cmd_complete(
            args.slug, args.drop_id, args.status,
            args.summary, args.artifacts, args.learnings,
            args.concerns, args.decisions
        )
    elif args.command == 'close':
        return cmd_close(args.slug)
    
    return 1

if __name__ == '__main__':
    sys.exit(main())