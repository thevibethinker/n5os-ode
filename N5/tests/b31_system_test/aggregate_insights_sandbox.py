#!/usr/bin/env python3
"""
B31 Insights Aggregation - SANDBOX VERSION

Test version that operates only in sandbox directory.
Safe to experiment without affecting production.
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# SANDBOX PATHS
SANDBOX_ROOT = Path("/home/workspace/N5/tests/b31_system_test")
MEETINGS_DIR = SANDBOX_ROOT / "meetings"
AGGREGATED_FILE = SANDBOX_ROOT / "market_intelligence/aggregated_insights.md"

def load_existing_aggregated_insights() -> str:
    """Load existing aggregated insights file or create if doesn't exist."""
    if AGGREGATED_FILE.exists():
        logger.info(f"Loading existing aggregated insights: {AGGREGATED_FILE}")
        return AGGREGATED_FILE.read_text()
    else:
        logger.info("No existing aggregated insights found. Creating new file.")
        AGGREGATED_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        template = f"""# Market Intelligence: Aggregated Research Insights (SANDBOX TEST)

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}  
**Total Meetings Analyzed:** 0  
**Total Insights:** 0

---

## Strong Signals (Verified ≥3 Primary Sources)

*No strong signals identified yet.*

---

## Emerging Signals (Verified 2 Primary Sources)

*No emerging signals identified yet.*

---

## Single-Source Insights (1 High-Quality Source)

*No single-source insights yet.*

---

## Contradictions & Tensions

*No contradictions identified yet.*

---

## Opportunity Map

*No opportunities mapped yet.*

---

## Change Log

**{datetime.now().strftime('%Y-%m-%d')}:** Initial aggregation file created (SANDBOX)
"""
        AGGREGATED_FILE.write_text(template)
        logger.info(f"✅ Created sandbox aggregated insights: {AGGREGATED_FILE}")
        return template

def extract_b31_insights(b31_path: Path) -> List[Dict]:
    """Extract insights from B31 file (handles both old and new formats)."""
    try:
        content = b31_path.read_text()
        meeting_id = b31_path.parent.name
        
        insights = []
        
        # Extract perspective
        perspective_match = re.search(r'\*\*Perspective:\*\*\s*(.+?)(?:\n|$)', content)
        perspective = perspective_match.group(1).strip() if perspective_match else "Unknown"
        
        # TRY NEW FORMAT FIRST
        insight_pattern = r'###\s+(.+?)\n(.*?)(?=\n###|\Z)'
        matches = list(re.finditer(insight_pattern, content, re.DOTALL))
        
        new_format_found = False
        for match in matches:
            title = match.group(1).strip()
            body = match.group(2).strip()
            
            if any(keyword in title.lower() for keyword in ['perspective', 'key insights', 'overview']):
                continue
            
            if '**Evidence:**' in body or '**Signal strength:**' in body:
                new_format_found = True
                
                evidence_match = re.search(r'\*\*Evidence:\*\*\s*"(.+?)"', body)
                why_match = re.search(r'\*\*Why it matters:\*\*\s*(.+?)(?:\n|$)', body)
                signal_match = re.search(r'\*\*Signal strength:\*\*\s*([●○]+)', body)
                category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', body)
                credibility_match = re.search(r'\*\*Domain credibility:\*\*\s*([●○]+)', body)
                source_type_match = re.search(r'\*\*Source type:\*\*\s*(PRIMARY|SECONDARY|SPECULATIVE)', body)
                
                insight = {
                    'title': title,
                    'evidence': evidence_match.group(1) if evidence_match else None,
                    'why_matters': why_match.group(1).strip() if why_match else None,
                    'signal_strength': signal_match.group(1) if signal_match else None,
                    'category': category_match.group(1).strip() if category_match else "Uncategorized",
                    'domain_credibility': credibility_match.group(1) if credibility_match else None,
                    'source_type': source_type_match.group(1) if source_type_match else "UNKNOWN",
                    'perspective': perspective,
                    'meeting_id': meeting_id,
                    'b31_path': str(b31_path.relative_to(SANDBOX_ROOT)),
                    'format': 'new'
                }
                
                insights.append(insight)
        
        # TRY OLD FORMAT if no new format found
        if not new_format_found:
            logger.info(f"Detected old B31 format in {b31_path.name}")
            
            old_pattern = r'(\d+)\.\s+(.+?)(?:- Implication:\s*(.+?))?(?=\n\d+\.|\Z)'
            matches = re.finditer(old_pattern, content, re.DOTALL)
            
            for match in matches:
                title = match.group(2).strip()
                implication = match.group(3).strip() if match.group(3) else None
                
                insight = {
                    'title': title,
                    'evidence': None,
                    'why_matters': implication,
                    'signal_strength': "●●●○○",  # Default 3/5
                    'category': "Uncategorized",
                    'domain_credibility': None,
                    'source_type': "UNKNOWN",
                    'perspective': perspective,
                    'meeting_id': meeting_id,
                    'b31_path': str(b31_path.relative_to(SANDBOX_ROOT)),
                    'format': 'old'
                }
                
                insights.append(insight)
        
        logger.info(f"Extracted {len(insights)} insights from {b31_path.name} (format: {'new' if new_format_found else 'old'})")
        return insights
    
    except Exception as e:
        logger.error(f"Error extracting insights from {b31_path}: {e}", exc_info=True)
        return []

def count_dots(dot_string: str) -> int:
    """Count filled dots in signal strength string."""
    return dot_string.count('●') if dot_string else 0

def process_new_meeting(meeting_id: str) -> Dict:
    """Process a new meeting's B31 file and extract insights."""
    
    b31_path = MEETINGS_DIR / meeting_id / "B31_STAKEHOLDER_RESEARCH.md"
    
    if not b31_path.exists():
        logger.error(f"B31 file not found: {b31_path}")
        return {'status': 'error', 'message': 'B31 file not found'}
    
    insights = extract_b31_insights(b31_path)
    
    if not insights:
        logger.warning(f"No insights extracted from {b31_path}")
        return {'status': 'warning', 'message': 'No insights found', 'insights_count': 0}
    
    # Categorize by signal strength
    strong = [i for i in insights if count_dots(i.get('signal_strength', '')) >= 4]
    medium = [i for i in insights if count_dots(i.get('signal_strength', '')) == 3]
    weak = [i for i in insights if count_dots(i.get('signal_strength', '')) <= 2]
    
    logger.info(f"Breakdown: {len(strong)} strong, {len(medium)} medium, {len(weak)} weak")
    
    return {
        'status': 'success',
        'insights_count': len(insights),
        'insights': insights,
        'breakdown': {'strong': len(strong), 'medium': len(medium), 'weak': len(weak)}
    }

def list_available_meetings():
    """List all meetings in sandbox."""
    meetings = sorted([d.name for d in MEETINGS_DIR.iterdir() if d.is_dir()])
    logger.info(f"Found {len(meetings)} meetings in sandbox:")
    for m in meetings:
        b31_exists = (MEETINGS_DIR / m / "B31_STAKEHOLDER_RESEARCH.md").exists()
        logger.info(f"  {'✓' if b31_exists else '✗'} {m}")
    return meetings

def process_all_meetings():
    """Process all meetings in sandbox incrementally."""
    meetings = list_available_meetings()
    
    all_insights = []
    for meeting_id in meetings:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {meeting_id}")
        logger.info(f"{'='*60}")
        
        result = process_new_meeting(meeting_id)
        
        if result['status'] == 'success':
            all_insights.extend(result['insights'])
            logger.info(f"✅ Extracted {result['insights_count']} insights")
        else:
            logger.warning(f"⚠️  {result['message']}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TOTAL: {len(all_insights)} insights from {len(meetings)} meetings")
    logger.info(f"{'='*60}")
    
    return all_insights

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='B31 Aggregation Sandbox Test')
    parser.add_argument('--list', action='store_true', help='List available meetings')
    parser.add_argument('--meeting-id', help='Process specific meeting')
    parser.add_argument('--all', action='store_true', help='Process all meetings')
    
    args = parser.parse_args()
    
    logger.info("🧪 SANDBOX MODE - Safe to experiment!")
    logger.info(f"Sandbox location: {SANDBOX_ROOT}")
    
    if args.list:
        list_available_meetings()
    elif args.meeting_id:
        result = process_new_meeting(args.meeting_id)
        print(json.dumps(result, indent=2, default=str))
    elif args.all:
        insights = process_all_meetings()
        
        # Save insights JSON for review
        output_file = SANDBOX_ROOT / "extracted_insights.json"
        output_file.write_text(json.dumps(insights, indent=2, default=str))
        logger.info(f"\n✅ Saved all insights to: {output_file}")
    else:
        parser.print_help()
