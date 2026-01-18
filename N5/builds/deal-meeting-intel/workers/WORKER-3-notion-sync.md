---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 3
title: Notion Bidirectional Sync
estimated_time: 3 hours
dependencies: [1]
---

# Worker 3: Notion Bidirectional Sync

## Objective

Build robust bidirectional sync between local deals.db and Notion:
1. Pull: Notion → Local (existing deals, contacts, manual edits)
2. Push: Local → Notion (intelligence updates, stage changes)
3. Append-only intelligence field (never overwrite history)

## Deliverables

- [ ] `N5/scripts/notion_deal_sync.py` — bidirectional sync engine
- [ ] `N5/config/notion_field_mapping.json` — field mapping config
- [ ] Conflict resolution logic
- [ ] Scheduled sync agent update

## Implementation Details

### 1. Field Mapping Configuration

```json
{
  "acquirer_targets": {
    "database_id": "3a2d606f-99fb-4ecf-9f92-374d324f7247",
    "fields": {
      "company": {"notion": "Company", "local": "company", "direction": "notion_to_local", "type": "title"},
      "deal_temp": {"notion": "Deal Temp", "local": "temperature", "direction": "bidirectional", "type": "select"},
      "status": {"notion": "Status", "local": "stage", "direction": "bidirectional", "type": "select"},
      "category": {"notion": "Category", "local": "category", "direction": "notion_to_local", "type": "select"},
      "proximity": {"notion": "Proximity", "local": "proximity", "direction": "notion_to_local", "type": "select"},
      "intelligence_summary": {"notion": "Intelligence Summary", "local": null, "direction": "local_to_notion", "type": "rich_text"},
      "last_meeting": {"notion": "Last Meeting", "local": "last_touched", "direction": "local_to_notion", "type": "date"},
      "next_action": {"notion": "Next Action", "local": "next_action", "direction": "bidirectional", "type": "rich_text"}
    }
  },
  "deal_brokers": {
    "database_id": "2ec5c3d6-a5db-8007-a821-000bf97dee8b",
    "fields": {
      "contact": {"notion": "Contact", "local": "full_name", "direction": "notion_to_local", "type": "title"},
      "blurb": {"notion": "Blurb", "local": "notes", "direction": "bidirectional", "type": "rich_text"},
      "angle_strategy": {"notion": "Angle / Strategy", "local": "strategy", "direction": "bidirectional", "type": "rich_text"}
    }
  },
  "leadership_targets": {
    "database_id": "2438ec09-5208-45d5-88b3-2d761099da9a",
    "fields": {
      "person": {"notion": "Person", "local": "full_name", "direction": "notion_to_local", "type": "title"},
      "linkedin_url": {"notion": "LinkedIn URL", "local": "linkedin_url", "direction": "notion_to_local", "type": "url"},
      "notes_thesis": {"notion": "Notes / thesis", "local": "notes", "direction": "bidirectional", "type": "rich_text"},
      "second_degree": {"notion": "2nd degree connects", "local": "second_degree_connects", "direction": "bidirectional", "type": "rich_text"}
    }
  }
}
```

### 2. Append-Only Intelligence Push

```python
def append_intelligence(deal_id: str, intel: DealIntel) -> bool:
    """
    Append new intelligence to Notion's Intelligence Summary field.
    Never overwrites — always prepends with timestamp.
    """
    deal = db.get_deal(deal_id)
    notion_page_id = deal.get('notion_id')
    
    if not notion_page_id:
        logger.warning(f"No Notion page for deal {deal_id}")
        return False
    
    # Format the new entry
    new_entry = format_intel_entry(intel)
    
    # Get current content
    current = notion.get_page_property(notion_page_id, 'Intelligence Summary')
    
    # Prepend new entry (most recent first)
    updated = new_entry + "\n\n" + current
    
    # Update Notion
    notion.update_page(notion_page_id, {
        'Intelligence Summary': updated,
        'Last Meeting': intel.meeting_date,
        'Next Action': intel.next_action
    })
    
    return True


def format_intel_entry(intel: DealIntel) -> str:
    """Format intelligence as markdown entry."""
    entry = f"""---
## [{intel.date}] {intel.source_title}

**Source:** {intel.source_type}
"""
    
    if intel.stage_change:
        entry += f"**Stage:** {intel.stage_before} → {intel.stage_after}\n"
    
    if intel.key_facts:
        entry += "\n**Key Intel:**\n"
        for fact in intel.key_facts:
            entry += f"- {fact}\n"
    
    if intel.next_action:
        entry += f"\n**Next:** {intel.next_action}"
        if intel.next_action_date:
            entry += f" (by {intel.next_action_date})"
    
    return entry
```

### 3. Pull Sync (Notion → Local)

```python
def pull_from_notion(full_sync: bool = False):
    """
    Pull updates from Notion to local.
    
    Args:
        full_sync: If True, sync all records. If False, only changed since last sync.
    """
    for db_name, config in FIELD_MAPPING.items():
        pages = notion.query_database(
            config['database_id'],
            filter=None if full_sync else {'last_edited_time': {'after': last_sync_time}}
        )
        
        for page in pages:
            local_record = transform_notion_to_local(page, config['fields'])
            
            existing = db.get_by_notion_id(page['id'])
            if existing:
                # Merge with conflict resolution
                merged = resolve_conflicts(existing, local_record)
                db.update(existing['id'], merged)
            else:
                # New record from Notion
                db.insert(local_record)
        
        logger.info(f"Pulled {len(pages)} records from {db_name}")
```

### 4. Conflict Resolution

```python
def resolve_conflicts(local: dict, notion: dict) -> dict:
    """
    Resolve conflicts between local and Notion data.
    
    Rules:
    1. For "notion_to_local" fields: Notion always wins
    2. For "local_to_notion" fields: Local always wins
    3. For "bidirectional" fields: Most recently modified wins
    """
    merged = {}
    
    for field, config in FIELD_CONFIG.items():
        direction = config['direction']
        
        if direction == 'notion_to_local':
            merged[field] = notion.get(field)
        elif direction == 'local_to_notion':
            merged[field] = local.get(field)
        else:  # bidirectional
            # Compare timestamps
            if notion.get('last_edited') > local.get('updated_at'):
                merged[field] = notion.get(field)
            else:
                merged[field] = local.get(field)
    
    return merged
```

### 5. Scheduled Sync

Update the existing scheduled agent to include bidirectional sync:

```python
# Every 6 hours
def scheduled_deal_sync():
    # 1. Pull from Notion (catches manual edits)
    pull_from_notion(full_sync=False)
    
    # 2. Push pending intelligence updates
    pending = db.get_pending_notion_updates()
    for update in pending:
        append_intelligence(update['deal_id'], update['intel'])
        db.mark_synced(update['id'])
    
    # 3. Sync stage changes
    stage_changes = db.get_unsynced_stage_changes()
    for change in stage_changes:
        notion.update_page(change['notion_id'], {'Status': change['new_stage']})
        db.mark_stage_synced(change['id'])
```

## Notion API Usage

Uses `use_app_notion` tool with these actions:
- `notion-retrieve-database-content` — bulk read
- `notion-update-page` — update fields
- `notion-query-database` — filtered queries

## Testing

```bash
# Test append intelligence
python3 N5/scripts/notion_deal_sync.py append \
    --deal-id cs-acq-darwinbox \
    --intel '{"date": "2026-01-18", "source": "SMS", "key_facts": ["Ready to proceed"]}'

# Test pull sync
python3 N5/scripts/notion_deal_sync.py pull --dry-run

# Test full bidirectional
python3 N5/scripts/notion_deal_sync.py sync --dry-run
```

## Success Criteria

- [ ] Intelligence appends correctly without data loss
- [ ] Manual Notion edits sync back to local
- [ ] Stage changes propagate bidirectionally
- [ ] Sync completes in <30s for normal operations
- [ ] Graceful handling of Notion API errors
