#!/usr/bin/env python3
"""
Zo Troubleshooting Quick-Add Tool

Captures issues with full telemetry and context automatically.
"""
import json
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import os

ROOT = Path(__file__).resolve().parents[1]

def get_conversation_id():
    """Extract conversation ID from current workspace path or environment."""
    workspace_path = os.getcwd()
    if '.z/workspaces/' in workspace_path:
        parts = workspace_path.split('.z/workspaces/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
    return "unknown"

def get_recent_commands():
    """Get recent command history (bash history)."""
    try:
        result = subprocess.run(
            ['tail', '-n', '20', os.path.expanduser('~/.bash_history')],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    return "Unable to capture command history"

def get_system_context():
    """Gather system context."""
    context = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conversation_id": get_conversation_id(),
        "pwd": os.getcwd(),
        "user": os.environ.get('USER', 'unknown'),
    }
    return context

def format_telemetry(args, context):
    """Format full telemetry data."""
    telemetry = f"""
## Telemetry Data

**Timestamp**: {context['timestamp']}
**Conversation ID**: {context['conversation_id']}
**Working Directory**: {context['pwd']}
**User**: {context['user']}

## Issue Details

{args.details}
"""
    
    if args.error_code:
        telemetry += f"\n**Error Code**: `{args.error_code}`\n"
    
    if args.stack_trace:
        telemetry += f"\n**Stack Trace**:\n```\n{args.stack_trace}\n```\n"
    
    if args.tool_calls:
        telemetry += f"\n**Tool Calls**: {args.tool_calls}\n"
    
    if args.files:
        telemetry += f"\n**Files Involved**: {', '.join(args.files)}\n"
    
    if args.reproducible:
        telemetry += f"\n**Reproducible**: Yes\n"
        if args.reproduce_steps:
            telemetry += f"**Steps to Reproduce**:\n{args.reproduce_steps}\n"
    else:
        telemetry += f"\n**Reproducible**: No/Unknown\n"
    
    if args.impact:
        telemetry += f"\n**Impact**: {args.impact}\n"
    
    if args.workaround:
        telemetry += f"\n**Workaround**: {args.workaround}\n"
    
    if args.include_history:
        telemetry += f"\n## Recent Command History\n```bash\n{get_recent_commands()}\n```\n"
    
    return telemetry

def main():
    parser = argparse.ArgumentParser(
        description='Quick-add Zo troubleshooting issue with full telemetry'
    )
    
    parser.add_argument('title', help='Brief issue title')
    parser.add_argument('--details', required=True, help='Full description of the issue')
    parser.add_argument('--error-code', help='Error code or message')
    parser.add_argument('--stack-trace', help='Stack trace if available')
    parser.add_argument('--tool-calls', help='Tools that were called')
    parser.add_argument('--files', nargs='+', help='Files involved in the issue')
    parser.add_argument('--tags', nargs='+', default=['error'], help='Tags for categorization')
    parser.add_argument('--reproducible', action='store_true', help='Issue is reproducible')
    parser.add_argument('--reproduce-steps', help='Steps to reproduce')
    parser.add_argument('--impact', choices=['blocking', 'workaround-available', 'minor'], 
                       help='Impact level')
    parser.add_argument('--workaround', help='Workaround if available')
    parser.add_argument('--include-history', action='store_true', default=True,
                       help='Include recent command history (default: true)')
    parser.add_argument('--no-history', action='store_false', dest='include_history',
                       help='Do not include command history')
    
    args = parser.parse_args()
    
    # Gather context
    context = get_system_context()
    
    # Format full telemetry
    full_details = format_telemetry(args, context)
    
    # Add to list using standard list add script
    tags = args.tags + ['zo-issue']
    
    cmd = [
        'python3',
        str(ROOT / 'scripts/n5_lists_add.py'),
        'zo-troubleshooting',
        args.title,
        '--body', full_details,
        '--tags'
    ] + tags
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Issue logged to Zo Troubleshooting list")
        print(f"\nConversation ID: {context['conversation_id']}")
        print(f"Tags: {', '.join(tags)}")
        if args.impact:
            print(f"Impact: {args.impact}")
    else:
        print("❌ Failed to log issue")
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
