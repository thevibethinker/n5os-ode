#!/usr/bin/env python3
"""
Squawk Auto-Proposer - Intelligent Issue Resolution Proposals

Runs every 3 days at 20:30 ET.
Model: Claude Sonnet 4.5

Generates actionable proposals for resolving issues from:
- Squawk List (critical/urgent issues)
- System Upgrades List (planned enhancements)

Selection Criteria:
1. Low lift, high reward
2. Highest likelihood of implementation success
3. Priority-weighted
4. Age-weighted (FIFO for equal priority)
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path("/home/workspace/N5/logs/maintenance/squawk")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "proposals.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

SQUAWK_LIST = Path("/home/workspace/Lists/squawk.jsonl")
UPGRADES_LIST = Path("/home/workspace/Lists/system-upgrades.jsonl")
PROPOSALS_DIR = Path("/home/workspace/N5/maintenance/proposals")

PRIORITY_WEIGHTS = {
    'HIGH': 100,
    'H': 100,
    'MEDIUM': 50,
    'M': 50,
    'LOW': 10,
    'L': 10,
}


def load_jsonl(filepath):
    """Load JSONL file."""
    items = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        return items
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return []


def calculate_selection_score(item, source):
    """
    Calculate selection score based on:
    - Priority weight
    - Age (older = higher score)
    - Estimated lift (lower = higher score)
    - Implementation likelihood (higher = higher score)
    """
    score = 0
    
    # Priority weight (0-100 points)
    priority = item.get('priority', 'L').upper()
    score += PRIORITY_WEIGHTS.get(priority, 10)
    
    # Age weight (0-50 points)
    created_at = item.get('created_at')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now() - created_date.replace(tzinfo=None)).days
            # Give more points for older items (capped at 50)
            score += min(age_days / 10, 50)
        except:
            pass
    
    # Source bias: squawk items get slight priority boost (critical issues)
    if source == 'squawk':
        score += 20
    
    # Status filter: only consider open/planned items
    status = item.get('status', '').lower()
    if status not in ['open', 'planned', 'pending']:
        score = 0  # Exclude completed/closed items
    
    return score


def select_item_for_proposal(items_squawk, items_upgrades):
    """Select the best item for proposal generation."""
    logger.info("=== Item Selection Process ===")
    
    # Score all items
    candidates = []
    
    for item in items_squawk:
        score = calculate_selection_score(item, 'squawk')
        if score > 0:
            candidates.append({
                'source': 'squawk',
                'item': item,
                'score': score
            })
    
    for item in items_upgrades:
        score = calculate_selection_score(item, 'upgrades')
        if score > 0:
            candidates.append({
                'source': 'upgrades',
                'item': item,
                'score': score
            })
    
    if not candidates:
        logger.warning("No eligible items found for proposal")
        return None
    
    # Sort by score (highest first)
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Log top 5 candidates
    logger.info(f"Found {len(candidates)} eligible item(s)")
    logger.info("Top 5 candidates by score:")
    for i, candidate in enumerate(candidates[:5], 1):
        item = candidate['item']
        logger.info(f"  {i}. [{candidate['source']}] {item.get('id')}: {item.get('title')} (score: {candidate['score']:.1f})")
    
    # Select top candidate
    selected = candidates[0]
    logger.info(f"✓ Selected: [{selected['source']}] {selected['item'].get('id')}")
    
    return selected


def generate_proposal_content(source, item):
    """Generate proposal document content."""
    
    item_id = item.get('id', 'unknown')
    title = item.get('title', 'Untitled')
    summary = item.get('summary', '')
    priority = item.get('priority', 'MEDIUM')
    status = item.get('status', 'open')
    tags = item.get('tags', [])
    
    # Extract additional context
    body = item.get('body', '')
    error_details = item.get('error_details', '')
    affected_components = item.get('affected_components', [])
    impact = item.get('impact', '')
    
    content = f"""# Proposed Solution: {title}

**Source:** {source.title()} List  
**Item ID:** {item_id}  
**Priority:** {priority}  
**Status:** {status}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M ET')}  
**Tags:** {', '.join(tags) if tags else 'None'}

---

## Issue Summary

{summary if summary else 'No summary provided.'}

"""
    
    if body:
        content += f"""
### Additional Context

{body}

"""
    
    if error_details:
        content += f"""
### Error Details

```
{error_details}
```

"""
    
    if affected_components:
        content += f"""
### Affected Components

{chr(10).join('- ' + c for c in affected_components)}

"""
    
    if impact:
        content += f"""
### Impact

{impact}

"""
    
    # Placeholder sections for AI to fill in during scheduled task
    content += """---

## Root Cause Analysis

**[TO BE FILLED BY SONNET 4.5]**

*AI Analysis:* Investigate the underlying cause of this issue by reviewing:
- Affected component source code
- Related configuration files
- System logs and error traces
- Historical changes (git history)

Provide a clear explanation of why this issue exists.

---

## Proposed Solution

**[TO BE FILLED BY SONNET 4.5]**

*AI Proposal:* Provide a step-by-step implementation plan:

1. **Step 1:** [Description]
2. **Step 2:** [Description]
3. **Step 3:** [Description]
...

Include:
- Specific files to modify
- Code changes or configuration updates
- Commands to execute
- Dependencies to install (if any)

---

## Risk Assessment

**[TO BE FILLED BY SONNET 4.5]**

*AI Analysis:* Evaluate potential risks:

### High Risk Areas
- [Risk 1]
- [Risk 2]

### Mitigation Strategies
- [Strategy 1]
- [Strategy 2]

### Reversibility
- How easily can this change be rolled back?

---

## Test Validation Steps

**[TO BE FILLED BY SONNET 4.5]**

*AI Proposal:* How to verify the solution works:

1. **Pre-implementation verification:**
   - [ ] [Check 1]
   - [ ] [Check 2]

2. **Post-implementation verification:**
   - [ ] [Test 1]
   - [ ] [Test 2]

3. **Integration checks:**
   - [ ] [Check 1]
   - [ ] [Check 2]

---

## Rollback Procedure

**[TO BE FILLED BY SONNET 4.5]**

*AI Proposal:* If the solution causes issues:

1. **Immediate rollback:**
   ```bash
   # [Commands to undo changes]
   ```

2. **Data recovery (if applicable):**
   - [Steps to recover data]

3. **Verification after rollback:**
   - [How to verify system is back to original state]

---

## Clarifying Questions

**[TO BE FILLED BY SONNET 4.5]**

*Before implementation, please clarify:*

### Intent
- [ ] What is the underlying goal or desired outcome?
- [ ] Are there any constraints or requirements not mentioned?

### Functionality
- [ ] What specific behavior or features are expected?
- [ ] Are there edge cases to consider?

### Output
- [ ] What should the end result look like?
- [ ] How should success be measured?

### Considerations
- [ ] Are there dependencies on other systems or workflows?
- [ ] What is the timeline or urgency for this fix?
- [ ] Who should be notified when this is completed?

---

## Implementation Checklist

- [ ] Review and answer clarifying questions above
- [ ] Approve proposed solution
- [ ] Create backup of affected files
- [ ] Execute implementation steps
- [ ] Run validation tests
- [ ] Verify system stability
- [ ] Update source list item status to "completed"
- [ ] Document any deviations from the plan

---

## Notes

*Add any additional notes, observations, or decisions here during implementation.*

"""
    
    return content


def save_proposal(source, item, content):
    """Save proposal to file."""
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    
    item_id = item.get('id', 'unknown')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Clean item_id for filename
    clean_id = item_id.replace('/', '-').replace(' ', '_')
    filename = f"{source}_{clean_id}_{date_str}.md"
    
    filepath = PROPOSALS_DIR / filename
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    logger.info(f"✓ Proposal saved to: {filepath}")
    return filepath


def main():
    """Run squawk auto-proposer."""
    parser = argparse.ArgumentParser(description="Generate proposals for squawk/upgrade items")
    parser.add_argument('--item-id', help="Target specific item ID")
    parser.add_argument('--source', choices=['squawk', 'upgrades'], help="Specify source list")
    parser.add_argument('--dry-run', action='store_true', help="Show selection without generating proposal")
    
    args = parser.parse_args()
    
    logger.info("=== Squawk Auto-Proposer Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load lists
    items_squawk = load_jsonl(SQUAWK_LIST)
    items_upgrades = load_jsonl(UPGRADES_LIST)
    
    logger.info(f"Loaded {len(items_squawk)} squawk item(s)")
    logger.info(f"Loaded {len(items_upgrades)} upgrade item(s)")
    
    # Handle specific item ID
    if args.item_id:
        logger.info(f"Targeting specific item: {args.item_id}")
        
        # Search in specified source or both
        target_item = None
        target_source = None
        
        if not args.source or args.source == 'squawk':
            for item in items_squawk:
                if item.get('id') == args.item_id:
                    target_item = item
                    target_source = 'squawk'
                    break
        
        if not target_item and (not args.source or args.source == 'upgrades'):
            for item in items_upgrades:
                if item.get('id') == args.item_id:
                    target_item = item
                    target_source = 'upgrades'
                    break
        
        if not target_item:
            logger.error(f"Item {args.item_id} not found")
            return 1
        
        selected = {'source': target_source, 'item': target_item}
    else:
        # Auto-select best item
        selected = select_item_for_proposal(items_squawk, items_upgrades)
        
        if not selected:
            logger.warning("No eligible items for proposal generation")
            return 0
    
    if args.dry_run:
        logger.info("DRY RUN - Would generate proposal for:")
        logger.info(f"  Source: {selected['source']}")
        logger.info(f"  ID: {selected['item'].get('id')}")
        logger.info(f"  Title: {selected['item'].get('title')}")
        return 0
    
    # Generate proposal
    content = generate_proposal_content(selected['source'], selected['item'])
    filepath = save_proposal(selected['source'], selected['item'], content)
    
    logger.info("=== Squawk Auto-Proposer Completed ===")
    logger.info(f"Next step: Review proposal at {filepath}")
    logger.info("Note: AI analysis sections will be filled when this runs as scheduled task with Sonnet 4.5")
    
    return 0


if __name__ == "__main__":
    exit(main())
