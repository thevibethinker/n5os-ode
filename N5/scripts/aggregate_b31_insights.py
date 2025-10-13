#!/usr/bin/env python3
"""
B31 Insights Incremental Aggregation Script

Implements incremental pattern detection across B31 insights.
Loads existing aggregated_insights.md and updates with new meeting insights.
Compacts when 5+ similar insights accumulate.

Version: 1.0
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

WORKSPACE = Path("/home/workspace")
AGGREGATED_FILE = WORKSPACE / "Knowledge/market_intelligence/aggregated_insights.md"
B31_PATTERN = "N5/records/meetings/*/B31_STAKEHOLDER_RESEARCH.md"

def load_existing_aggregated_insights() -> str:
    """Load existing aggregated insights file or create if doesn't exist."""
    if AGGREGATED_FILE.exists():
        logger.info(f"Loading existing aggregated insights: {AGGREGATED_FILE}")
        return AGGREGATED_FILE.read_text()
    else:
        logger.info("No existing aggregated insights found. Creating new file.")
        AGGREGATED_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Create initial template
        template = f"""# Market Intelligence: Aggregated Research Insights

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

**{datetime.now().strftime('%Y-%m-%d')}:** Initial aggregation file created
"""
        AGGREGATED_FILE.write_text(template)
        return template

def extract_b31_insights(b31_path: Path) -> List[Dict]:
    """Extract insights from B31 file (handles both old and new formats)."""
    try:
        content = b31_path.read_text()
        meeting_id = b31_path.parent.name
        
        insights = []
        
        # Extract perspective/stakeholder context
        perspective_match = re.search(r'\*\*Perspective:\*\*\s*(.+?)(?:\n|$)', content)
        perspective = perspective_match.group(1).strip() if perspective_match else "Unknown"
        
        # TRY NEW FORMAT FIRST (with Evidence, Signal strength, etc)
        insight_pattern = r'###\s+(.+?)\n(.*?)(?=\n###|\Z)'
        matches = list(re.finditer(insight_pattern, content, re.DOTALL))
        
        new_format_found = False
        for match in matches:
            title = match.group(1).strip()
            body = match.group(2).strip()
            
            # Skip section headers
            if any(keyword in title.lower() for keyword in ['perspective', 'key insights', 'overview']):
                continue
            
            # Check if this looks like new format
            if '**Evidence:**' in body or '**Signal strength:**' in body:
                new_format_found = True
                
                # Extract components (new format)
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
                    'b31_path': str(b31_path.relative_to(WORKSPACE)),
                    'format': 'new'
                }
                
                insights.append(insight)
        
        # IF NO NEW FORMAT FOUND, TRY OLD FORMAT (numbered list with "Implication:")
        if not new_format_found:
            logger.info(f"Detected old B31 format in {b31_path}")
            
            # Old format: numbered list under "### Key Insights"
            old_pattern = r'(\d+)\.\s+(.+?)(?:- Implication:\s*(.+?))?(?=\n\d+\.|\Z)'
            matches = re.finditer(old_pattern, content, re.DOTALL)
            
            for match in matches:
                title = match.group(2).strip()
                implication = match.group(3).strip() if match.group(3) else None
                
                # Estimate signal strength from old format (default to medium)
                signal_strength = "●●●○○"  # Default 3/5 for old format
                
                insight = {
                    'title': title,
                    'evidence': None,  # Old format doesn't have explicit evidence
                    'why_matters': implication,
                    'signal_strength': signal_strength,
                    'category': "Uncategorized",  # Old format doesn't have categories
                    'domain_credibility': None,  # Old format doesn't track this
                    'source_type': "UNKNOWN",  # Old format doesn't specify
                    'perspective': perspective,
                    'meeting_id': meeting_id,
                    'b31_path': str(b31_path.relative_to(WORKSPACE)),
                    'format': 'old'
                }
                
                insights.append(insight)
        
        logger.info(f"Extracted {len(insights)} insights from {b31_path} (format: {'new' if new_format_found else 'old'})")
        return insights
    
    except Exception as e:
        logger.error(f"Error extracting insights from {b31_path}: {e}", exc_info=True)
        return []

def count_dots(dot_string: str) -> int:
    """Count filled dots in signal strength string."""
    return dot_string.count('●') if dot_string else 0

def aggregate_incremental(new_insights: List[Dict], existing_content: str) -> str:
    """
    Incrementally update aggregated insights with new meeting insights.
    
    This is the LLM-assisted part - creates a prompt for updating the doc.
    In production, this would call an LLM. For now, returns instruction.
    """
    
    # Count insights
    total_new = len(new_insights)
    
    # Categorize by signal strength
    strong = [i for i in new_insights if count_dots(i.get('signal_strength', '')) >= 4]
    medium = [i for i in new_insights if count_dots(i.get('signal_strength', '')) == 3]
    weak = [i for i in new_insights if count_dots(i.get('signal_strength', '')) <= 2]
    
    logger.info(f"New insights breakdown: {len(strong)} strong, {len(medium)} medium, {len(weak)} weak")
    
    # Create update instruction
    instruction = f"""
UPDATE AGGREGATED INSIGHTS

You are updating the aggregated market intelligence document with new insights from a recent meeting.

EXISTING DOCUMENT:
---
{existing_content}
---

NEW INSIGHTS TO INTEGRATE ({total_new} total):
"""
    
    for i, insight in enumerate(new_insights, 1):
        instruction += f"""
{i}. **{insight['title']}**
   - Evidence: "{insight.get('evidence', 'N/A')}"
   - Why it matters: {insight.get('why_matters', 'N/A')}
   - Signal: {insight.get('signal_strength', 'N/A')} | Credibility: {insight.get('domain_credibility', 'N/A')}
   - Source type: {insight['source_type']}
   - Category: {insight['category']}
   - From: {insight['perspective']} (Meeting: {insight['meeting_id']})
"""
    
    instruction += f"""

INSTRUCTIONS:

1. **Cross-reference with existing insights:**
   - Check if any new insights confirm/contradict existing ones
   - If similar insight exists: UPDATE that section with additional verification
   - If new insight: ADD to appropriate section

2. **Signal strength promotion:**
   - Single-source (●●●●○ or ●●●●●) from PRIMARY source → Add to "Single-Source Insights"
   - If existing insight gains 2nd PRIMARY source → Promote to "Emerging Signals"
   - If existing insight gains 3rd+ PRIMARY source → Promote to "Strong Signals"

3. **Compaction:**
   - If 5+ similar insights exist, compact them into one consolidated insight with "[X] sources confirm"

4. **Contradictions:**
   - Flag when two PRIMARY sources disagree on same topic
   - Add to "Contradictions & Tensions" section

5. **Opportunity Map:**
   - When Strong Signal emerges, assess if it represents actionable opportunity
   - Add to Opportunity Map with recommended action

6. **Update metadata:**
   - Increment total meetings analyzed
   - Increment total insights
   - Add change log entry with date and meeting ID

OUTPUT: The complete updated aggregated_insights.md file.
"""
    
    return instruction

def process_new_meeting(meeting_id: str, dry_run: bool = False) -> Dict:
    """
    Process a new meeting's B31 file and update aggregated insights.
    
    Args:
        meeting_id: Meeting folder name
        dry_run: If True, show what would be done without writing files
    
    Returns:
        Dict with status and results
    """
    
    # Find B31 file
    b31_path = WORKSPACE / f"N5/records/meetings/{meeting_id}/B31_STAKEHOLDER_RESEARCH.md"
    
    if not b31_path.exists():
        logger.error(f"B31 file not found: {b31_path}")
        return {'status': 'error', 'message': 'B31 file not found'}
    
    # Extract insights
    insights = extract_b31_insights(b31_path)
    
    if not insights:
        logger.warning(f"No insights extracted from {b31_path}")
        return {'status': 'warning', 'message': 'No insights found', 'insights_count': 0}
    
    # Load existing aggregated doc
    existing_content = load_existing_aggregated_insights()
    
    # Generate update instruction
    update_instruction = aggregate_incremental(insights, existing_content)
    
    if dry_run:
        logger.info("[DRY RUN] Would update aggregated insights")
        logger.info(f"Update instruction length: {len(update_instruction)} chars")
        return {
            'status': 'dry-run',
            'insights_count': len(insights),
            'instruction_length': len(update_instruction)
        }
    
    # In production, this would call LLM with the instruction
    # For now, save the instruction for manual review
    instruction_file = WORKSPACE / f"Knowledge/market_intelligence/update_instruction_{meeting_id}.txt"
    instruction_file.write_text(update_instruction)
    
    logger.info(f"✅ Update instruction saved: {instruction_file}")
    logger.info("NEXT: Run this instruction through LLM to generate updated aggregated_insights.md")
    
    return {
        'status': 'success',
        'insights_count': len(insights),
        'instruction_file': str(instruction_file),
        'message': 'Update instruction generated. Ready for LLM processing.'
    }

def full_rebuild(dry_run: bool = False):
    """
    Full rebuild of aggregated insights from all B31 files.
    Only use when starting fresh or fixing corruption.
    """
    
    logger.warning("⚠️  FULL REBUILD MODE - This will reprocess all B31 files")
    
    # Find all B31 files
    b31_files = sorted(WORKSPACE.glob(B31_PATTERN))
    logger.info(f"Found {len(b31_files)} B31 files")
    
    if dry_run:
        logger.info("[DRY RUN] Would rebuild from scratch")
        return
    
    # Reset aggregated file
    if AGGREGATED_FILE.exists():
        backup_path = AGGREGATED_FILE.with_suffix('.md.backup')
        AGGREGATED_FILE.rename(backup_path)
        logger.info(f"Backed up existing file to {backup_path}")
    
    # Create fresh template
    load_existing_aggregated_insights()
    
    logger.info("⚠️  Full rebuild requires LLM processing of all B31 files")
    logger.info("⚠️  Recommendation: Use incremental updates instead")
    logger.info("✅ Fresh template created. Add meetings incrementally.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Aggregate B31 insights incrementally')
    parser.add_argument('--meeting-id', help='Process this specific meeting')
    parser.add_argument('--full-rebuild', action='store_true', help='Full rebuild from all B31 files (rare use)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without writing')
    
    args = parser.parse_args()
    
    if args.full_rebuild:
        full_rebuild(dry_run=args.dry_run)
    elif args.meeting_id:
        result = process_new_meeting(args.meeting_id, dry_run=args.dry_run)
        logger.info(f"Result: {json.dumps(result, indent=2)}")
    else:
        logger.error("Must specify --meeting-id or --full-rebuild")
        parser.print_help()
