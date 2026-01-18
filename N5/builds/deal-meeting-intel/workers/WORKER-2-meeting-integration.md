---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_GCktM2iwLZIi5cHK
worker_id: 2
title: Meeting Integration
estimated_time: 2 hours
dependencies: [1]
---

# Worker 2: Meeting Integration

## Objective

Integrate deal intelligence extraction into the meeting processing pipeline:
1. Detect when a meeting involves a deal-related contact
2. Generate B37_DEAL_INTEL.md block with extracted intelligence
3. Trigger Notion sync automatically

## Deliverables

- [ ] `N5/scripts/meeting_deal_intel.py` — B37 block generator
- [ ] Update `meeting_pipeline.py` to call deal intel extraction
- [ ] B37 block template
- [ ] Integration tests

## Implementation Details

### 1. B37 Block Structure

```markdown
---
block: B37
title: Deal Intelligence
generated: 2026-01-18T14:30:00
deal_id: cs-acq-darwinbox
pipeline: careerspan
---

# Deal Intelligence: Darwinbox

## Meeting Context
- **Date:** 2026-01-18
- **Attendees:** Christine Song, V
- **Meeting Type:** Partnership sync

## Signal Analysis
- **Stage Before:** qualified
- **Stage After:** negotiating
- **Confidence:** 85%

## Key Intelligence Extracted

### From B01 (Strategic Recap)
- Budget confirmed for Q1 implementation
- CEO (Nikos) is final decision maker
- Timeline: 60-day evaluation period

### From B08 (Stakeholder Intel)
- Christine: Champion, reports to CEO
- Technical team supportive but wants pilot

### From B13 (Risks & Opportunities)
- **Risk:** Competitor also in talks
- **Opportunity:** They need solution before March

## Recommended Actions
1. Send proposal by Friday
2. Schedule technical deep-dive with their team
3. Prepare pilot program scope

## Raw Signal Data
```json
{
  "stage_change": true,
  "sentiment": "positive",
  "urgency": "high",
  "next_action": "Send proposal",
  "next_action_date": "2026-01-24"
}
```
```

### 2. Detection Logic

```python
def detect_deal_meeting(meeting_folder: Path) -> Optional[DealMatch]:
    """
    Check if meeting involves a deal-related contact.
    
    Checks:
    1. Meeting title for company names
    2. B03/B08 attendees against deal_contacts
    3. Transcript/recap for deal company mentions
    """
    # Load meeting manifest
    manifest = load_manifest(meeting_folder / 'manifest.json')
    
    # Check title
    title = manifest.get('title', meeting_folder.name)
    title_match = router.match_deal(title)
    if title_match and title_match.confidence > 80:
        return title_match
    
    # Check attendees
    attendees = extract_attendees(meeting_folder)
    for attendee in attendees:
        contact_match = router.match_contact(attendee)
        if contact_match:
            return contact_match
    
    # Check content (more expensive)
    recap = load_block(meeting_folder, 'B01')
    if recap:
        content_match = router.match_deal(recap[:2000])
        if content_match and content_match.confidence > 75:
            return content_match
    
    return None
```

### 3. Intel Extraction from B-Blocks

```python
def extract_deal_intel_from_blocks(meeting_folder: Path, deal: Deal) -> DealIntel:
    """
    Extract deal-relevant intelligence from meeting B-blocks.
    """
    intel = DealIntel(deal_id=deal.id)
    
    # B01: Strategic insights
    b01 = load_block(meeting_folder, 'B01')
    if b01:
        intel.strategic = extract_strategic_intel(b01, deal)
    
    # B08: Stakeholder mapping
    b08 = load_block(meeting_folder, 'B08')
    if b08:
        intel.stakeholders = extract_stakeholder_intel(b08, deal)
    
    # B13: Risks and opportunities
    b13 = load_block(meeting_folder, 'B13')
    if b13:
        intel.risks_opps = extract_risks_opps(b13, deal)
    
    # B25: Next steps / deliverables
    b25 = load_block(meeting_folder, 'B25')
    if b25:
        intel.next_steps = extract_next_steps(b25, deal)
    
    # Synthesize stage inference
    intel.infer_stage_change()
    
    return intel
```

### 4. Pipeline Integration Hook

Add to meeting processing pipeline (after B25 generation):

```python
# In meeting_pipeline.py or equivalent

def process_meeting(meeting_folder: Path):
    # ... existing block generation ...
    
    # NEW: Deal intelligence extraction
    deal_match = detect_deal_meeting(meeting_folder)
    if deal_match:
        logger.info(f"Deal-related meeting detected: {deal_match.deal_id}")
        
        # Generate B37
        intel = extract_deal_intel_from_blocks(meeting_folder, deal_match.deal)
        write_b37_block(meeting_folder, intel)
        
        # Update local DB
        db.update_deal_from_meeting(deal_match.deal_id, intel)
        db.log_activity(deal_match.deal_id, 'meeting', meeting_folder.name)
        
        # Queue Notion sync
        notion_sync_queue.add(deal_match.deal_id, intel)
```

## Testing

```bash
# Test on a known deal meeting
python3 N5/scripts/meeting_deal_intel.py \
    --meeting-folder "2026-01-15_Christine-Song-Ribbon-Sync" \
    --dry-run

# Batch test on recent meetings
python3 N5/scripts/meeting_deal_intel.py \
    --scan-recent 10 \
    --dry-run
```

## Success Criteria

- [ ] Correctly identifies deal-related meetings (>95% recall)
- [ ] Generates accurate B37 blocks
- [ ] Integrates seamlessly with existing pipeline
- [ ] No false positives on internal meetings
