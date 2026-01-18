---
created: 2026-01-18
last_edited: 2026-01-18
version: 2.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 4
title: SMS Deal Interface
est_time: 2 hours
dependencies: [1, 3]
status: ready
---

# Worker 4: SMS Deal Interface

## Prerequisites (✅ All Complete)

Phase 1 artifacts are ready:
- ✅ `file 'N5/scripts/deal_signal_router.py'` — DealSignalRouter class
- ✅ `file 'N5/scripts/notion_deal_sync.py'` — Notion sync functions
- ✅ `file 'N5/data/deals.db'` — Database with deals + deal_contacts tables
- ✅ `file 'N5/config/deal_signal_config.json'` — Stage definitions

## Goal

Handle SMS messages like:
- `n5 deal darwinbox Ready to proceed with pilot`
- `n5 deal ribbon Christine confirmed budget`
- `n5 deal gloat Meeting scheduled for Tuesday`

## How to Use Phase 1 Artifacts

```python
# Import the signal router
import sys
sys.path.insert(0, '/home/workspace/N5/scripts')
from deal_signal_router import DealSignalRouter

# Initialize router
router = DealSignalRouter(
    db_path='/home/workspace/N5/data/deals.db',
    config_path='/home/workspace/N5/config/deal_signal_config.json'
)

# Match a deal from SMS content
match = router.match_deal(query="darwinbox", context="careerspan")
# Returns: DealMatch(deal_id='cs-acq-darwinbox', confidence=95, ...)

# Extract signal intelligence
if match.deal_id:
    deal = router.get_deal(match.deal_id)
    extraction = router.extract_signal(
        text="Ready to proceed with pilot",
        deal_context=deal
    )
    # Returns: SignalExtraction(stage_signal='positive', inferred_stage='qualified', ...)

# Process the full signal (updates DB)
result = router.process_signal(
    source='sms',
    content='n5 deal darwinbox Ready to proceed with pilot',
    context='careerspan',
    dry_run=False
)
```

## Deliverables

### 1. Create `N5/scripts/sms_deal_handler.py`

```python
#!/usr/bin/env python3
"""
SMS Deal Handler - Process 'n5 deal' commands from SMS

Usage:
  python3 sms_deal_handler.py --message "n5 deal darwinbox Ready to proceed"
  python3 sms_deal_handler.py --message "..." --dry-run
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from deal_signal_router import DealSignalRouter

def parse_sms_deal_command(message: str) -> dict:
    """Parse 'n5 deal <query> <update>' format."""
    pattern = r'^n5\s+deal\s+(\S+)\s+(.+)$'
    match = re.match(pattern, message.strip(), re.IGNORECASE)
    if not match:
        return {'valid': False, 'error': 'Invalid format. Use: n5 deal <company> <update>'}
    return {
        'valid': True,
        'query': match.group(1),
        'update': match.group(2)
    }

def handle_deal_sms(message: str, dry_run: bool = False) -> dict:
    """Process an SMS deal update."""
    parsed = parse_sms_deal_command(message)
    if not parsed['valid']:
        return {'success': False, 'response': parsed['error']}
    
    router = DealSignalRouter()
    result = router.process_signal(
        source='sms',
        content=message,
        context='',  # Auto-detect pipeline
        dry_run=dry_run
    )
    
    if result.success and result.matched:
        response = f"✓ Updated {result.deal_id}: {result.action_taken}"
    elif result.success:
        response = f"⚠️ No deal match found for '{parsed['query']}'"
    else:
        response = f"❌ Error: {result.notes}"
    
    return {
        'success': result.success,
        'matched': result.matched,
        'deal_id': result.deal_id,
        'response': response,
        'dry_run': dry_run
    }
```

### 2. Create SMS Rule

Add rule that triggers on "n5 deal" SMS messages:
- Condition: `When SMS contains "n5 deal"`
- Action: Route to `sms_deal_handler.py`

### 3. Create `N5/tests/test_sms_deal_handler.py`

Test cases:
- Valid command parsing
- Deal matching via router
- Stage inference
- Response formatting
- Dry-run mode

## Response Templates

| Scenario | Response |
|----------|----------|
| Success | `✓ Updated cs-acq-darwinbox: Stage → qualified, logged activity` |
| No match | `⚠️ No deal found for 'xyz'. Did you mean: darwinbox, deel, dayforce?` |
| Ambiguous | `🤔 Multiple matches: darwinbox (95%), darwin (72%). Reply with number.` |
| Error | `❌ Could not process. Try: n5 deal <company> <update>` |

## Acceptance Criteria

- [ ] Parses `n5 deal <query> <update>` format
- [ ] Uses DealSignalRouter for matching + extraction
- [ ] Updates deals.db via router.process_signal()
- [ ] Returns human-friendly SMS response
- [ ] Handles errors gracefully
- [ ] Tests pass
