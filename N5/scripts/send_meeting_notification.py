#!/usr/bin/env python3
"""
Send SMS notification after meeting processing.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

async def send_sms_notification(meeting_dir: Path):
    """
    Send SMS notification with meeting summary and recommendations.
    """
    # Load metadata
    metadata_file = meeting_dir / "_metadata.json"
    if not metadata_file.exists():
        print("❌ No metadata found")
        return
    
    metadata = json.loads(metadata_file.read_text())
    
    # Load action items count
    action_items_file = meeting_dir / "action-items.md"
    action_count = 0
    if action_items_file.exists():
        content = action_items_file.read_text()
        action_count = content.count('- [ ]')
    
    # Load decisions count
    decisions_file = meeting_dir / "decisions.md"
    decision_count = 0
    if decisions_file.exists():
        content = decisions_file.read_text()
        # Count decision headers (rough estimate)
        decision_count = content.count('### ')
    
    # Get meeting name from folder
    meeting_name = meeting_dir.name.split('_', 3)[-1] if '_' in meeting_dir.name else meeting_dir.name
    meeting_name = meeting_name.replace('_', ' ').replace('-', ' ').title()
    
    # Get recommendations
    recommendations = metadata.get('recommendations', {})
    recommended = recommendations.get('recommended', [])
    rec_list = ', '.join([r['type'].replace('_', ' ') for r in recommended[:2]]) if recommended else 'none'
    
    # Build SMS message (160 chars max for standard SMS, but we can go longer)
    message = f"""Meeting processed: {meeting_name}

{action_count} action items, {decision_count} decisions

Recommended: {rec_list}

Review: https://va.zo.computer/workspace#{meeting_dir.name}

Reply with deliverables you want (e.g., "blurb + email")"""
    
    # Send via Zo's send_sms_to_user tool
    # This will be called by the orchestrator which has access to the tool
    return message

async def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: send_meeting_notification.py <meeting_folder_path>")
        sys.exit(1)
    
    meeting_dir = Path(sys.argv[1])
    message = await send_sms_notification(meeting_dir)
    print(message)

if __name__ == "__main__":
    asyncio.run(main())
