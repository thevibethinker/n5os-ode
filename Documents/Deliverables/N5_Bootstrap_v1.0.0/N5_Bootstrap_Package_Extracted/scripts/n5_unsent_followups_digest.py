#!/usr/bin/env python3
"""
N5 Unsent Follow-Ups Digest
Daily digest tracking generated follow-up emails that haven't been sent yet.

Usage:
    python3 n5_unsent_followups_digest.py [--dry-run] [--debug]

Version: 1.1.0
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from difflib import SequenceMatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
MEETINGS_DIR = Path("/home/workspace/N5/records/meetings")
REGISTRY_PATH = Path("/home/workspace/N5/logs/processed_meetings.jsonl")
OUTPUT_DIR = Path("/home/workspace/N5/logs")

# Gmail API integration flag
GMAIL_AVAILABLE = False
try:
    # Check if we're running in Zo environment with Gmail tools
    GMAIL_AVAILABLE = True
except:
    pass


class UnsentFollowupsDigest:
    """Generate digest of unsent follow-up emails."""
    
    def __init__(self, dry_run: bool = False, debug: bool = False, use_app_gmail_fn=None):
        self.dry_run = dry_run
        self.use_app_gmail = use_app_gmail_fn
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def load_registry(self) -> Dict[str, Dict]:
        """Load meeting registry with follow-up tracking."""
        registry = {}
        if REGISTRY_PATH.exists():
            with open(REGISTRY_PATH, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        registry[entry['meeting_id']] = entry
        return registry
    
    def update_registry(self, meeting_id: str, updates: Dict) -> None:
        """Update a meeting entry in the registry."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update registry for {meeting_id}: {updates}")
            return
        
        # Load all entries
        entries = []
        if REGISTRY_PATH.exists():
            with open(REGISTRY_PATH, 'r') as f:
                entries = [json.loads(line) for line in f if line.strip()]
        
        # Update target entry
        found = False
        for entry in entries:
            if entry['meeting_id'] == meeting_id:
                entry.update(updates)
                found = True
                break
        
        if not found:
            entries.append({'meeting_id': meeting_id, **updates})
        
        # Write back
        with open(REGISTRY_PATH, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')
        
        logger.info(f"✓ Updated registry for {meeting_id}")
    
    def scan_meetings_with_followups(self) -> List[Dict]:
        """Scan meeting folders for generated follow-ups."""
        logger.info(f"Scanning meetings in: {MEETINGS_DIR}")
        
        meetings_with_followups = []
        
        for meeting_dir in sorted(MEETINGS_DIR.iterdir()):
            if not meeting_dir.is_dir():
                continue
            
            # Check metadata
            metadata_path = meeting_dir / "_metadata.json"
            if not metadata_path.exists():
                continue
            
            with open(metadata_path, 'r') as f:
                metadata = json.loads(f.read())
            
            # Skip if not external (check folder name since classification field varies)
            is_external = 'external' in meeting_dir.name
            if not is_external:
                continue
            
            # Check if follow-up was generated
            deliverables = metadata.get('generated_deliverables', [])
            followup_deliverable = None
            for deliv in deliverables:
                if deliv.get('type') == 'follow_up_email':
                    followup_deliverable = deliv
                    break
            
            # Fallback: scan B25 directly if no metadata entry
            if not followup_deliverable:
                logger.debug(f"No metadata entry, scanning B25 for {meeting_dir.name}")
                b25_path = meeting_dir / "B25_DELIVERABLE_CONTENT_MAP.md"
                try:
                    if b25_path.exists():
                        b25_content = b25_path.read_text()
                        # Check for follow-up email section
                        patterns = [
                            r'###\s*Section 2:\s*Follow-Up Email',
                            r'##\s*Follow-Up Email\s*Draft',
                            r'##\s*Section 2.*Follow.*Up'
                        ]
                        
                        if any(re.search(p, b25_content, re.IGNORECASE) for p in patterns):
                            # Extract subject line
                            subject_match = re.search(r'\*\*Subject\*\*:?\s*(.+?)(?:\n|$)', b25_content)
                            subject = subject_match.group(1).strip() if subject_match else "Unknown Subject"
                            
                            # Extract email (look for email patterns)
                            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', b25_content)
                            email = email_match.group(0) if email_match else ""
                            
                            # Extract stakeholder name from B08 if available
                            b08_path = meeting_dir / "B08_STAKEHOLDER_INTELLIGENCE.md"
                            stakeholder_name = "Unknown"
                            if b08_path.exists():
                                b08_content = b08_path.read_text()
                                # Try to get name from title or first heading
                                name_match = re.search(r'^#\s*(.+?)(?:\n|$)', b08_content, re.MULTILINE)
                                if name_match:
                                    stakeholder_name = name_match.group(1).strip()
                            
                            followup_deliverable = {
                                'type': 'follow_up_email',
                                'path': str(b25_path.relative_to(Path('/home/workspace'))),
                                'section': 'Section 2',
                                'status': 'pending',
                                'subject': subject,
                                'email': email,
                                'stakeholder_name': stakeholder_name,
                                'backfilled': False,
                                'fallback_detected': True
                            }
                except Exception as e:
                    logger.debug(f"Error scanning B25 for {meeting_dir.name}: {e}")
            
            if not followup_deliverable:
                continue
            
            # Check if declined
            if metadata.get('followup_status') == 'declined':
                logger.debug(f"Skipping {meeting_dir.name} - marked as declined")
                continue
            
            # Extract meeting info
            # Parse date from meeting_id (format: YYYY-MM-DD_...)
            meeting_id = metadata.get('meeting_id', meeting_dir.name)
            date_str = meeting_id.split('_')[0]  # Extract YYYY-MM-DD
            meeting_date = datetime.strptime(date_str, '%Y-%m-%d')
            days_ago = (datetime.now() - meeting_date).days
            
            # Skip if older than 30 days
            if days_ago > 30:
                continue
            
            stakeholder_name = metadata.get('stakeholder_primary', 'Unknown')
            email = metadata.get('email', '')
            
            # Get subject line from draft
            followup_path = Path(followup_deliverable['path'])
            subject_line = self._extract_subject_line(followup_path)
            
            # Get action steps from metadata or deliverable map
            action_steps = metadata.get('follow_up_action', '')
            
            # Override with deliverable metadata if available
            if followup_deliverable.get('stakeholder_name'):
                stakeholder_name = followup_deliverable['stakeholder_name']
            if followup_deliverable.get('email'):
                email = followup_deliverable['email']
            if followup_deliverable.get('subject'):
                subject_line = followup_deliverable['subject']

            meetings_with_followups.append({
                'meeting_id': meeting_id,
                'meeting_date': date_str,
                'days_ago': days_ago,
                'stakeholder_name': stakeholder_name,
                'email': email,
                'subject_line': subject_line,
                'action_steps': action_steps,
                'followup_path': str(followup_path)
            })
        
        logger.info(f"✓ Found {len(meetings_with_followups)} meetings with follow-ups")
        return meetings_with_followups
    
    def _extract_subject_line(self, email_path: Path) -> str:
        """Extract subject line from follow-up email draft."""
        if not email_path.exists():
            return "Unknown Subject"
        
        with open(email_path, 'r') as f:
            for line in f:
                if line.startswith('**Subject:**'):
                    return line.replace('**Subject:**', '').strip()
        
        return "Unknown Subject"
    
    def _fuzzy_match_strings(self, s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings."""
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    def _check_gmail_for_match(self, meeting: Dict) -> bool:
        """Check if follow-up email was sent via Gmail API."""
        if not self.use_app_gmail:
            logger.debug("Gmail API not available")
            return False
        
        try:
            # Search sent emails from past 30 days
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
            
            # Build search query
            subject_keywords = self._extract_keywords(meeting['subject_line'])
            recipient_email = meeting['email']
            
            # Search by recipient first (more specific)
            if recipient_email:
                search_query = f"to:{recipient_email} after:{cutoff_date} in:sent"
            else:
                # Fall back to subject keywords
                search_query = f"subject:{subject_keywords} after:{cutoff_date} in:sent"
            
            logger.debug(f"Gmail search query: {search_query}")
            
            # Call Gmail API
            result = self.use_app_gmail(
                tool_name='gmail-find-email',
                configured_props={
                    'q': search_query,
                    'maxResults': 20,
                    'withTextPayload': False,
                    'metadataOnly': True
                }
            )
            
            if not result or 'messages' not in result:
                logger.debug(f"No sent emails found for {meeting['stakeholder_name']}")
                return False
            
            messages = result['messages']
            logger.debug(f"Found {len(messages)} sent emails to check")
            
            # Check each message for fuzzy match
            for msg in messages:
                msg_subject = msg.get('subject', '')
                msg_to = msg.get('to', [])
                
                # Extract recipient emails from 'to' field
                recipient_emails = []
                if isinstance(msg_to, list):
                    for recipient in msg_to:
                        if isinstance(recipient, dict):
                            recipient_emails.append(recipient.get('email', '').lower())
                        elif isinstance(recipient, str):
                            recipient_emails.append(recipient.lower())
                
                # Check subject similarity
                subject_similarity = self._fuzzy_match_strings(meeting['subject_line'], msg_subject)
                
                # Check recipient match
                recipient_match = False
                if recipient_email:
                    recipient_match = recipient_email.lower() in recipient_emails
                
                # Match criteria: high subject similarity (>0.7) OR exact recipient + moderate subject (>0.5)
                confidence = 0.0
                if subject_similarity > 0.7:
                    confidence = subject_similarity
                elif recipient_match and subject_similarity > 0.5:
                    confidence = 0.8  # High confidence if recipient + subject match
                
                if confidence > 0.7:
                    logger.info(f"✓ Found match for {meeting['stakeholder_name']}: '{msg_subject}' (confidence: {confidence:.2f})")
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking Gmail for {meeting['stakeholder_name']}: {e}")
            return False
    
    def _extract_keywords(self, subject: str) -> str:
        """Extract meaningful keywords from subject line for search."""
        # Remove common words and extract core terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = subject.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return ' '.join(keywords[:3])  # Use top 3 keywords
    
    def check_gmail_sent(self, meetings: List[Dict]) -> List[Dict]:
        """Check Gmail for sent follow-ups and filter unsent."""
        if not self.use_app_gmail:
            logger.warning("Gmail API not available - treating all as unsent")
            return meetings
        
        logger.info("Checking Gmail for sent follow-ups...")
        unsent = []
        
        for meeting in meetings:
            was_sent = self._check_gmail_for_match(meeting)
            if not was_sent:
                unsent.append(meeting)
            else:
                logger.info(f"✓ Skipping {meeting['stakeholder_name']} - already sent")
        
        logger.info(f"✓ Found {len(unsent)} unsent follow-ups (out of {len(meetings)} total)")
        return unsent
    
    def generate_digest(self, unsent: List[Dict]) -> str:
        """Generate markdown digest."""
        if not unsent:
            logger.info("✓ No unsent follow-ups")
            return ""
        
        # Sort FIFO (oldest first)
        unsent_sorted = sorted(unsent, key=lambda x: x['meeting_date'])
        
        digest = f"""# Unsent Follow-Up Emails

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}  
**Count:** {len(unsent_sorted)} pending

---

"""
        
        for i, meeting in enumerate(unsent_sorted, 1):
            digest += f"""## {i}. **{meeting['stakeholder_name']}**

- **Meeting date:** {meeting['meeting_date']} ({meeting['days_ago']} days ago)
- **Subject:** {meeting['subject_line']}
- **Email:** {meeting['email']}
- **Action required:** {meeting['action_steps']}
- **Draft:** `file '{meeting['followup_path']}'`

**To drop this follow-up:** `drop-followup "{meeting['stakeholder_name']}"`

---

"""
        
        return digest
    
    def save_digest(self, content: str) -> str:
        """Save digest to file."""
        if not content:
            return ""
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        output_path = OUTPUT_DIR / f"unsent_followups_digest_{timestamp}.md"
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would save to: {output_path}")
            logger.info(f"\n{content}")
            return str(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)
        
        logger.info(f"✓ Digest saved: {output_path}")
        return str(output_path)


def main(dry_run: bool = False, debug: bool = False) -> int:
    """Main execution."""
    logger.info("=== N5 Unsent Follow-Ups Digest Generator v1.1.0 ===")
    if dry_run:
        logger.info("[DRY RUN MODE]")
    
    try:
        # Gmail API integration - will be injected by scheduled task
        digest_gen = UnsentFollowupsDigest(dry_run=dry_run, debug=debug, use_app_gmail_fn=None)
        
        # Scan meetings with follow-ups
        meetings = digest_gen.scan_meetings_with_followups()
        
        if not meetings:
            logger.info("✓ No meetings with follow-ups found")
            return 0
        
        # Check Gmail for sent emails
        unsent = digest_gen.check_gmail_sent(meetings)
        
        # Generate and save digest
        digest_content = digest_gen.generate_digest(unsent)
        if digest_content:
            output_path = digest_gen.save_digest(digest_content)
            logger.info(f"✓ Complete: {len(unsent)} unsent follow-ups")
        else:
            logger.info("✓ All follow-ups have been sent")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unsent follow-ups digest")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run, debug=args.debug))
