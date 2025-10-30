#!/usr/bin/env python3
"""
Extract action items from meeting Smart Blocks and email for approval.
Usage: python3 extract_meeting_actions.py --meeting-dir /path/to/meeting
"""
import json
import argparse
import logging
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services/task_intelligence"))
from calendar_scheduler import schedule_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
INBOX = WORKSPACE / "N5/inbox/meeting_actions"

def extract_actions_from_blocks(meeting_dir: Path) -> List[Dict[str, Any]]:
    """Extract action items from Smart Blocks."""
    actions = []
    
    # Read B01 for Critical Next Actions
    b01 = meeting_dir / "B01_DETAILED_RECAP.md"
    if b01.exists():
        text = b01.read_text()
        
        # Look for "Critical Next Action" section
        if "Critical Next Action" in text or "Key Decisions" in text:
            # Parse deliverable table or list
            for line in text.split('\n'):
                if '|' in line and ('NEED' in line or 'TODO' in line):
                    # Table format
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 2:
                        actions.append({
                            'text': parts[1],
                            'source_file': str(b01.name),
                            'source_block': 'B01',
                            'context': 'From Critical Next Actions'
                        })
                elif line.strip():
                    actions.append({
                        'text': line.strip().lstrip('-•*').strip(),
                        'source_file': str(b01.name),
                        'source_block': 'B01',
                        'context': 'From meeting recap'
                    })
    
    # Read B25 (Deliverable Content Map) - handle both naming conventions
    b25_files = list(meeting_dir.glob("B25_*DELIVERABLE*.md")) + list(meeting_dir.glob("B25_*Deliverable*.md"))
    if b25_files:
        b25 = b25_files[0]
        logger.info(f"Reading {b25.name}")
        actions.extend(parse_deliverables(b25.read_text(), "B25"))
    
    # Read B21 (Salient Questions/Key Moments) - handle both naming conventions
    b21_files = list(meeting_dir.glob("B21_*.md"))
    if b21_files:
        b21 = b21_files[0]
        logger.info(f"Reading {b21.name}")
        actions.extend(parse_questions(b21.read_text(), "B21"))
    
    return actions

def parse_block_for_actions(text: str, source: str) -> List[Dict[str, Any]]:
    """Parse text for action patterns."""
    actions = []
    action_patterns = [
        r"(?:will|need to|should|must|going to)\s+(.+?)(?:\.|$)",
        r"(?:action|todo|task):\s*(.+?)(?:\.|$)",
        r"by\s+(?:tomorrow|next week|friday|monday|tuesday|wednesday|thursday)\s*[:-]?\s*(.+?)(?:\.|$)"
    ]
    
    for pattern in action_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            action_text = match.group(1).strip()
            if len(action_text) > 10 and len(action_text) < 200:  # Filter noise
                actions.append({
                    "text": action_text,
                    "context": extract_context(text, match.start(), match.end()),
                    "source_block": source,
                    "confidence": "medium"
                })
    
    return actions

def parse_deliverables(text: str, source: str) -> List[Dict[str, Any]]:
    """Parse deliverables from B25."""
    actions = []
    lines = text.split('\n')
    
    for line in lines:
        # Look for bullet points or numbered lists
        if re.match(r'^\s*[-*•]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            clean_line = re.sub(r'^\s*[-*•\d.]+\s+', '', line).strip()
            if len(clean_line) > 10:
                actions.append({
                    "text": clean_line,
                    "context": f"Deliverable from meeting",
                    "source_block": source,
                    "confidence": "high"
                })
    
    return actions

def parse_questions(text: str, source: str) -> List[Dict[str, Any]]:
    """Extract follow-up actions from questions."""
    actions = []
    lines = text.split('\n')
    
    for line in lines:
        if '?' in line and ('follow up' in line.lower() or 'get back' in line.lower()):
            clean_line = line.strip().rstrip('?')
            if len(clean_line) > 10:
                actions.append({
                    "text": f"Follow up: {clean_line}",
                    "context": "Question requiring follow-up from meeting",
                    "source_block": source,
                    "confidence": "low"
                })
    
    return actions

def extract_context(text: str, start: int, end: int, window: int = 100) -> str:
    """Extract surrounding context for an action."""
    context_start = max(0, start - window)
    context_end = min(len(text), end + window)
    context = text[context_start:context_end].strip()
    return context[:200]  # Limit length

def enrich_actions(actions: List[Dict[str, Any]], meeting_dir: Path) -> List[Dict[str, Any]]:
    """Add suggested timing, priority, project based on context."""
    meeting_name = meeting_dir.name
    
    for i, action in enumerate(actions):
        action['id'] = f"act_{i+1:03d}"
        
        # Suggest timing
        text_lower = action['text'].lower()
        if 'urgent' in text_lower or 'asap' in text_lower:
            action['suggested_when'] = 'Today 3:00pm'
            action['suggested_priority'] = 'High'
        elif 'today' in text_lower:
            action['suggested_when'] = 'Today 5:00pm'
            action['suggested_priority'] = 'High'
        elif 'tomorrow' in text_lower:
            action['suggested_when'] = 'Tomorrow 10:00am'
            action['suggested_priority'] = 'Normal'
        else:
            # Default to next business day
            tomorrow = datetime.now() + timedelta(days=1)
            action['suggested_when'] = tomorrow.strftime('%A 2:00pm')
            action['suggested_priority'] = 'Normal'
        
        # Suggest duration
        if 'quick' in text_lower or 'brief' in text_lower:
            action['suggested_duration'] = '15m'
        elif 'review' in text_lower or 'meeting' in text_lower:
            action['suggested_duration'] = '30m'
        else:
            action['suggested_duration'] = '30m'
        
        # Suggest project based on keywords
        if 'hire' in text_lower or 'recruit' in text_lower or 'candidate' in text_lower:
            action['suggested_project'] = 'Personnel'
        elif 'network' in text_lower or 'intro' in text_lower or 'connect' in text_lower:
            action['suggested_project'] = 'Networking'
        elif 'recap' in text_lower or 'summary' in text_lower:
            action['suggested_project'] = 'Operations'
        elif 'product' in text_lower or 'feature' in text_lower:
            action['suggested_project'] = 'Product'
        else:
            action['suggested_project'] = 'Operations'
        
        # Suggest tags
        action['suggested_tags'] = []
        if 'meeting' in text_lower or 'recap' in text_lower:
            action['suggested_tags'].append('meeting')
        if 'follow' in text_lower:
            action['suggested_tags'].append('follow_up')
        if action['source_block'] == 'B25':
            action['suggested_tags'].append('deliverable')
    
    # Enrich each action with calendar-aware scheduling
    for i, action in enumerate(actions):
        actions[i] = enrich_action_with_scheduling(action)
    
    return actions

def enrich_action_with_scheduling(action: Dict) -> Dict:
    """Use calendar-aware scheduling to enhance timing."""
    try:
        scheduled = schedule_task(action)
        return scheduled
    except Exception as e:
        logger.warning(f"Scheduling failed for {action['title']}: {e}")
        return action

def save_actions(actions: List[Dict[str, Any]], meeting_dir: Path) -> Path:
    """Save extracted actions to inbox."""
    meeting_id = meeting_dir.name
    meeting_date = meeting_dir.parent.name  # YYYY-MM-DD
    
    data = {
        "meeting_id": meeting_id,
        "meeting_title": meeting_id.replace('_', ' '),
        "meeting_date": meeting_date,
        "meeting_path": str(meeting_dir),
        "actions": actions,
        "extracted_at": datetime.now().isoformat(),
        "status": "pending_review"
    }
    
    output_file = INBOX / f"{meeting_date}_{meeting_id}.json"
    output_file.write_text(json.dumps(data, indent=2))
    logger.info(f"✓ Saved {len(actions)} actions to {output_file}")
    
    return output_file

def format_approval_email(data: Dict[str, Any]) -> Dict[str, str]:
    """Format actions for email approval."""
    actions = data['actions']
    meeting_title = data['meeting_title']
    meeting_date = data['meeting_date']
    
    body_parts = [
        f"Hi V,\n",
        f"I extracted {len(actions)} action items from your {meeting_title} meeting ({meeting_date}).",
        "Please review and reply with your approval:\n",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    ]
    
    for i, action in enumerate(actions, 1):
        priority_emoji = "🔴" if action['suggested_priority'] == 'High' else "🟡"
        
        body_parts.append(f"**{i}. {action['text']}**")
        body_parts.append(f"   📅 {action['suggested_when']} | ⏱ {action['suggested_duration']} | {priority_emoji} {action['suggested_priority']}")
        body_parts.append(f"   📁 {action['suggested_project']} | 🏷 {', '.join(action['suggested_tags']) if action['suggested_tags'] else 'none'}")
        body_parts.append(f"   📝 {action['context'][:100]}...\n")
    
    body_parts.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "**Reply with:**",
        '• "approve all" → Push all to Akiflow',
        f'• "approve 1,{len(actions)}" → Push only #1 and #{len(actions)}',
        '• "skip 2" → Don\'t create #2',
        '• "edit 1: tomorrow 8am, 30m" → Modify then push\n',
        'Or just reply "approved" and I\'ll push everything!\n',
        "—Zo"
    ])
    
    return {
        "subject": f"[N5] {len(actions)} action items from {meeting_title}",
        "body": "\n".join(body_parts)
    }

def main(meeting_dir: str, dry_run: bool = False) -> int:
    """Main extraction workflow."""
    try:
        meeting_path = Path(meeting_dir).resolve()
        
        if not meeting_path.exists():
            logger.error(f"Meeting directory not found: {meeting_path}")
            return 1
        
        logger.info(f"Extracting actions from: {meeting_path.name}")
        
        # Extract actions
        actions = extract_actions_from_blocks(meeting_path)
        
        if not actions:
            logger.info("No actions found in meeting blocks")
            return 0
        
        logger.info(f"Found {len(actions)} raw actions")
        
        # Enrich with suggestions
        actions = enrich_actions(actions, meeting_path)
        
        # Save to inbox
        if not dry_run:
            output_file = save_actions(actions, meeting_path)
            
            # Prepare email
            data = json.loads(output_file.read_text())
            email_content = format_approval_email(data)
            
            logger.info(f"\n✓ Actions ready for email approval")
            logger.info(f"Subject: {email_content['subject']}")
            
            # Send email via stored JSON that reply monitor can reference
            email_request_file = output_file.parent / f"{output_file.stem}_email_request.json"
            email_request = {
                "to": "attawar.v@gmail.com",
                "subject": email_content['subject'],
                "body": email_content['body'],
                "actions_file": str(output_file),
                "sent_at": None,
                "thread_id": None
            }
            email_request_file.write_text(json.dumps(email_request, indent=2))
            
            logger.info(f"✓ Email request saved: {email_request_file}")
            logger.info("✓ Reply monitor will send email and track thread")
            
        else:
            logger.info("[DRY RUN] Would save actions and send email")
        
        logger.info(f"\n✓ Complete: Extracted {len(actions)} actions")
        return 0
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract meeting actions')
    parser.add_argument('--meeting-dir', required=True, help='Path to meeting directory')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    args = parser.parse_args()
    
    exit(main(args.meeting_dir, args.dry_run))
