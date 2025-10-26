#!/usr/bin/env python3
"""
AI-Based Meeting Transcript Deduplicator

Uses LLM to semantically compare new meeting transcripts against recent meetings
to catch duplicates that differ in timestamp but represent the same meeting.

Integrated with: n5_meeting_transcript_scanner.py
Architectural Principle: P16 (Accuracy Over Sophistication)
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


class MeetingAIDeduplicator:
    """AI-powered semantic meeting deduplication."""
    
    def __init__(self):
        self.meetings_dir = Path('/home/workspace/N5/records/meetings')
        self.requests_dir = Path('/home/workspace/N5/inbox/meeting_requests')
        
    def get_recent_meetings(self, date_str: str, lookback_hours: int = 24) -> List[Dict]:
        """
        Get meetings from target date plus lookback window.
        
        Args:
            date_str: Target date in YYYY-MM-DD format
            lookback_hours: Hours to look back from target date
            
        Returns:
            List of meeting metadata dicts with meeting_id, date, participants, filename
        """
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        start_date = target_date - timedelta(hours=lookback_hours)
        
        recent_meetings = []
        
        # Check processed meetings in meetings_dir
        if self.meetings_dir.exists():
            for meeting_dir in self.meetings_dir.iterdir():
                if not meeting_dir.is_dir():
                    continue
                    
                metadata_file = meeting_dir / '_metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            meta = json.load(f)
                            meeting_date_str = meta.get('meeting_date') or meta.get('date')
                            if meeting_date_str:
                                meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d')
                                if start_date <= meeting_date <= target_date:
                                    recent_meetings.append({
                                        'meeting_id': meta.get('meeting_id', meeting_dir.name),
                                        'date': meeting_date_str,
                                        'participants': meta.get('participants', {}),
                                        'original_filename': meta.get('original_filename', ''),
                                        'source': 'processed'
                                    })
                    except Exception as e:
                        logger.debug(f"Error reading metadata {metadata_file}: {e}")
        
        # Check pending/processed requests
        for req_subdir in ['', 'processed', 'completed']:
            req_path = self.requests_dir / req_subdir if req_subdir else self.requests_dir
            if req_path.exists():
                for req_file in req_path.glob('*_request.json'):
                    try:
                        with open(req_file, 'r') as f:
                            req = json.load(f)
                            meeting_date_str = req.get('date')
                            if meeting_date_str:
                                meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d')
                                if start_date <= meeting_date <= target_date:
                                    recent_meetings.append({
                                        'meeting_id': req.get('meeting_id', ''),
                                        'date': meeting_date_str,
                                        'participants': req.get('participants', ''),
                                        'original_filename': req.get('original_filename', ''),
                                        'gdrive_id': req.get('gdrive_id', ''),
                                        'source': 'request'
                                    })
                    except Exception as e:
                        logger.debug(f"Error reading request {req_file}: {e}")
        
        return recent_meetings
    
    def check_duplicate(
        self,
        new_meeting_context: Dict,
        use_llm: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if new meeting is a duplicate of existing meeting.
        
        Args:
            new_meeting_context: Dict with date, title/participants, filename
            use_llm: Whether to use AI comparison (True) or simple heuristic (False)
            
        Returns:
            Tuple of (is_duplicate: bool, matching_meeting_id: Optional[str])
        """
        date = new_meeting_context['date']
        new_title = new_meeting_context.get('title') or new_meeting_context.get('participants', '')
        new_filename = new_meeting_context.get('original_filename', '')
        
        # Get recent meetings from same date + 24h window
        recent_meetings = self.get_recent_meetings(date, lookback_hours=24)
        
        if not recent_meetings:
            logger.info(f"No recent meetings found for date {date}")
            return (False, None)
        
        logger.info(f"Checking against {len(recent_meetings)} recent meetings")
        
        if use_llm:
            return self._check_with_llm(new_meeting_context, recent_meetings)
        else:
            return self._check_with_heuristics(new_meeting_context, recent_meetings)
    
    def _check_with_heuristics(
        self,
        new_meeting: Dict,
        recent_meetings: List[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Simple heuristic deduplication (fallback if LLM unavailable).
        
        Checks:
        1. Exact gdrive_id match (already handled upstream)
        2. Same date + similar base filename (strip timestamp)
        """
        import re
        
        new_filename = new_meeting.get('original_filename', '')
        # Extract base name (before -transcript-)
        new_base = re.sub(r'-transcript-.*$', '', new_filename.lower())
        
        for existing in recent_meetings:
            existing_filename = existing.get('original_filename', '')
            existing_base = re.sub(r'-transcript-.*$', '', existing_filename.lower())
            
            # If base names match (ignoring timestamp), likely duplicate
            if new_base and existing_base and new_base == existing_base:
                if new_meeting['date'] == existing['date']:
                    logger.info(f"Heuristic match: {new_base} == {existing_base}")
                    return (True, existing['meeting_id'])
        
        return (False, None)
    
    def _check_with_llm(
        self,
        new_meeting: Dict,
        recent_meetings: List[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Use LLM to semantically compare new meeting against recent meetings.
        
        This handles fuzzy matches like:
        - "Alex x Vrijen" vs "Ale, Vrijen"
        - "Daily team stand-up" at 14:15 vs 14:17
        - Different timestamp suffixes from Fireflies
        """
        # Import LLM helper
        try:
            from pathlib import Path
            import sys
            helpers_path = Path(__file__).parent / 'helpers'
            if str(helpers_path) not in sys.path:
                sys.path.insert(0, str(helpers_path))
            from llm_helper import call_llm
            logger.info("Using AI mode for deduplication")
        except ImportError as e:
            logger.warning(f"llm_helper not available ({e}), using heuristics")
            return self._check_with_heuristics(new_meeting, recent_meetings)
        
        # Build comparison prompt
        new_date = new_meeting['date']
        new_title = new_meeting.get('title') or new_meeting.get('participants', '')
        new_filename = new_meeting.get('original_filename', '')
        
        # Format recent meetings for comparison
        existing_meetings_text = "\n".join([
            f"- ID: {m['meeting_id']}\n  Title: {m.get('participants', 'N/A')}\n  Filename: {m.get('original_filename', 'N/A')}"
            for m in recent_meetings[:10]  # Limit to 10 most recent
        ])
        
        prompt = f"""You are analyzing meeting transcripts to detect duplicates.

NEW MEETING TO CHECK:
Date: {new_date}
Title/Participants: {new_title}
Filename: {new_filename}

RECENT EXISTING MEETINGS (same date or within 24h):
{existing_meetings_text}

TASK: Determine if the NEW MEETING is a duplicate of any EXISTING MEETING.

A meeting is a DUPLICATE if:
- Same date AND same core participants/meeting name
- Only difference is the timestamp in the filename (Fireflies uploads multiple versions)
- Semantic equivalence (e.g., "Alex x Vrijen" same as "Ale, Vrijen")

A meeting is NOT a duplicate if:
- Different participants or meeting purpose
- Different date (even if similar name)
- Genuinely different meetings with similar names

RESPOND IN THIS EXACT FORMAT:
IS_DUPLICATE: yes/no
MATCHING_ID: [meeting_id if duplicate, or "none"]
REASON: [1 sentence explanation]

Example responses:
IS_DUPLICATE: yes
MATCHING_ID: 2025-10-24_external-sam-partnership-discovery-call
REASON: Same date and participants, only timestamp differs (17:32 vs 17:33)

IS_DUPLICATE: no
MATCHING_ID: none
REASON: Different external participant (sam vs alexis)
"""
        
        # Make LLM call
        try:
            logger.info("Requesting AI comparison...")
            response = call_llm(prompt, timeout=20)
            
            if not response:
                logger.info("LLM unavailable or timed out, falling back to heuristics")
                return self._check_with_heuristics(new_meeting, recent_meetings)
            
            # Parse response
            is_dup_line = [l for l in response.split('\n') if 'IS_DUPLICATE:' in l]
            match_id_line = [l for l in response.split('\n') if 'MATCHING_ID:' in l]
            reason_line = [l for l in response.split('\n') if 'REASON:' in l]
            
            if is_dup_line and match_id_line:
                is_dup = 'yes' in is_dup_line[0].lower()
                match_id = match_id_line[0].split(':', 1)[1].strip()
                reason = reason_line[0].split(':', 1)[1].strip() if reason_line else "No reason provided"
                
                if match_id.lower() == 'none':
                    match_id = None
                
                logger.info(f"AI analysis complete: duplicate={is_dup}, match={match_id}")
                logger.info(f"AI reason: {reason}")
                return (is_dup, match_id)
            else:
                logger.warning("Could not parse AI response, using heuristics")
                logger.debug(f"AI response was: {response[:200]}")
                return self._check_with_heuristics(new_meeting, recent_meetings)
                
        except Exception as e:
            logger.warning(f"AI call failed, falling back to heuristics: {e}")
            return self._check_with_heuristics(new_meeting, recent_meetings)


def main():
    """Test the deduplicator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test AI meeting deduplicator')
    parser.add_argument('--date', default='2025-10-24', help='Date to check (YYYY-MM-DD)')
    parser.add_argument('--title', required=True, help='Meeting title/participants')
    parser.add_argument('--filename', required=True, help='Original filename')
    parser.add_argument('--no-llm', action='store_true', help='Use heuristics only')
    
    args = parser.parse_args()
    
    dedup = MeetingAIDeduplicator()
    
    new_meeting = {
        'date': args.date,
        'title': args.title,
        'original_filename': args.filename
    }
    
    is_dup, match_id = dedup.check_duplicate(new_meeting, use_llm=not args.no_llm)
    
    if is_dup:
        print(f"✗ DUPLICATE of: {match_id}")
        return 1
    else:
        print(f"✓ NOT a duplicate - safe to process")
        return 0


if __name__ == '__main__':
    sys.exit(main())
