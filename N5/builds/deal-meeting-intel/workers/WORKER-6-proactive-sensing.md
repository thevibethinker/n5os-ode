---
created: 2026-01-18
last_edited: 2026-01-18
version: 2.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 6
title: Proactive Deal Sensing
est_time: 2 hours
dependencies: [1, 4]
status: blocked_on_4
---

# Worker 6: Proactive Deal Sensing

## Prerequisites

- ✅ `file 'N5/scripts/deal_signal_router.py'` — DealSignalRouter class
- ✅ `file 'N5/data/deals.db'` — Database with deals + deal_contacts
- ⏳ Worker 4 (SMS Handler) — needed for approval flow

## Goal

Detect potential NEW deals/contacts that don't exist in the database yet:

1. **Broker Detection**: Someone promises introductions → potential broker
2. **Deal Detection**: Company mentioned in positive context → potential acquirer/partner
3. **Leadership Detection**: Executive at target company → potential leadership contact

Then send SMS approval request to V before creating.

## Signal Detection Patterns

### Broker Signals
- "I can introduce you to..."
- "Let me connect you with..."
- "I know someone at X who..."
- "I'll make an intro to..."

### Deal Signals
- Company mentioned + acquisition/partnership keywords
- "They're looking to acquire..."
- "Interested in your technology..."

### Leadership Signals
- Person at known target company
- C-level/VP title mentioned
- Decision maker context

## SMS Approval Flow

```
[Signal Detected]
     ↓
[Check: Already in DB?] → Yes → Skip
     ↓ No
[Send SMS to V]
"🆕 New broker detected: John Smith from Acme Corp
   Context: 'I can introduce you to 3 HR tech CEOs'
   Add as broker? Y/N/Info"
     ↓
[V Replies]
  Y → Create contact, confirm
  N → Log as declined, skip
  Info → Send more context
```

## Deliverables

### 1. Create `N5/scripts/deal_proactive_sensor.py`

```python
#!/usr/bin/env python3
"""
Proactive Deal Sensor - Detect potential new deals/contacts

Usage:
  # Check a signal for new entities
  python3 deal_proactive_sensor.py --text "John can intro us to Workday CEO" --source meeting
  
  # Process pending approvals
  python3 deal_proactive_sensor.py --process-approval "Y" --pending-id abc123
"""

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

DB_PATH = '/home/workspace/N5/data/deals.db'

@dataclass
class DetectedEntity:
    entity_type: str  # 'broker', 'deal', 'leadership'
    name: str
    company: Optional[str]
    context: str
    confidence: int
    source_text: str

BROKER_PATTERNS = [
    r'(?:can|will|let me)\s+(?:introduce|connect|intro)\s+(?:you\s+)?(?:to|with)',
    r'I\s+know\s+(?:someone|people)\s+(?:at|from)',
    r"I'll\s+make\s+(?:an?\s+)?intro",
]

def detect_new_entities(text: str, source: str) -> List[DetectedEntity]:
    """Detect potential new contacts/deals in text."""
    entities = []
    text_lower = text.lower()
    
    # Check for broker signals
    for pattern in BROKER_PATTERNS:
        if re.search(pattern, text_lower):
            # Extract potential name (heuristic)
            # This would be enhanced with LLM in production
            entities.append(DetectedEntity(
                entity_type='broker',
                name='[Detected - needs extraction]',
                company=None,
                context=text[:200],
                confidence=70,
                source_text=text
            ))
            break
    
    return entities

def is_entity_known(entity: DetectedEntity) -> bool:
    """Check if entity already exists in database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if entity.entity_type in ['broker', 'leadership']:
        c.execute("""
            SELECT 1 FROM deal_contacts 
            WHERE LOWER(full_name) LIKE ?
        """, (f'%{entity.name.lower()}%',))
    else:
        c.execute("""
            SELECT 1 FROM deals 
            WHERE LOWER(company) LIKE ?
        """, (f'%{entity.name.lower()}%',))
    
    result = c.fetchone()
    conn.close()
    return result is not None

def queue_approval(entity: DetectedEntity) -> str:
    """Queue entity for SMS approval."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create pending_approvals table if needed
    c.execute("""
        CREATE TABLE IF NOT EXISTS pending_approvals (
            id TEXT PRIMARY KEY,
            entity_type TEXT,
            name TEXT,
            company TEXT,
            context TEXT,
            source_text TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    import uuid
    approval_id = str(uuid.uuid4())[:8]
    
    c.execute("""
        INSERT INTO pending_approvals (id, entity_type, name, company, context, source_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (approval_id, entity.entity_type, entity.name, entity.company, 
          entity.context, entity.source_text, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return approval_id

def format_approval_sms(entity: DetectedEntity, approval_id: str) -> str:
    """Format SMS for approval request."""
    emoji = {'broker': '🤝', 'deal': '🏢', 'leadership': '👔'}.get(entity.entity_type, '🆕')
    
    return f"""{emoji} New {entity.entity_type} detected:
{entity.name}{f' ({entity.company})' if entity.company else ''}

Context: "{entity.context[:100]}..."

Add to database? Reply:
Y - Add
N - Skip
Info - More details

[{approval_id}]"""

def process_approval(approval_id: str, response: str) -> dict:
    """Process V's approval response."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM pending_approvals WHERE id = ?", (approval_id,))
    pending = c.fetchone()
    
    if not pending:
        return {'success': False, 'error': 'Approval not found'}
    
    response = response.strip().upper()
    
    if response == 'Y':
        # Create the contact
        if pending['entity_type'] in ['broker', 'leadership']:
            contact_id = f"{pending['entity_type'][:4]}-{pending['name'].lower().replace(' ', '')[:15]}"
            c.execute("""
                INSERT INTO deal_contacts (id, contact_type, pipeline, full_name, company, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (contact_id, pending['entity_type'], 'careerspan', 
                  pending['name'], pending['company'], datetime.now().isoformat()))
        
        c.execute("UPDATE pending_approvals SET status = 'approved' WHERE id = ?", (approval_id,))
        conn.commit()
        conn.close()
        return {'success': True, 'action': 'created', 'id': contact_id}
    
    elif response == 'N':
        c.execute("UPDATE pending_approvals SET status = 'declined' WHERE id = ?", (approval_id,))
        conn.commit()
        conn.close()
        return {'success': True, 'action': 'declined'}
    
    elif response == 'INFO':
        conn.close()
        return {'success': True, 'action': 'info', 'context': pending['source_text']}
    
    conn.close()
    return {'success': False, 'error': f'Unknown response: {response}'}
```

### 2. Integrate with Signal Router

Add proactive sensing to the signal processing flow:

```python
# In deal_signal_router.py process_signal():
if not match.matched:
    # No existing deal matched - check for new entity signals
    from deal_proactive_sensor import detect_new_entities, is_entity_known, queue_approval
    
    entities = detect_new_entities(content, source)
    for entity in entities:
        if not is_entity_known(entity):
            approval_id = queue_approval(entity)
            # SMS sent via Zo tool
```

### 3. Create `N5/tests/test_proactive_sensor.py`

Test cases:
- Broker pattern detection
- Known entity checking
- Approval queueing
- Response processing (Y/N/Info)

## Acceptance Criteria

- [ ] Detects broker/deal/leadership signals in text
- [ ] Checks against existing database before alerting
- [ ] Queues pending approvals with unique IDs
- [ ] Formats clear SMS approval requests
- [ ] Processes Y/N/Info responses correctly
- [ ] Creates contacts on approval
- [ ] Tests pass
