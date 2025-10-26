# Stakeholder Profile Update Safeguards

**Date:** 2025-10-12  
**Purpose:** Protect manually-crafted profile content from accidental overwriting  
**Status:** Active — Required for all profile updates

---

## Problem Statement

Stakeholder profiles (like `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/stakeholder_profile.md'`) contain:

1. **Auto-generated metadata** (dates, interaction counts)
2. **LLM-synthesized content** (email summaries, tag suggestions)
3. **Manually-crafted insights** (founder motivations, strategic posture, key quotes)

**Risk:** When auto-updating from new meetings/emails, we could accidentally overwrite rich manual content with generic LLM output.

---

## Protection Strategy

### 1. Append-Only Interaction History

**Rule:** New meetings ALWAYS append to "Interaction History" section. Never replace existing entries.

**Implementation:**
```python
from safe_stakeholder_updater import append_interaction

append_interaction(
    profile_path=profile_path,
    interaction_date="2025-10-15",
    interaction_title="Follow-up Meeting",
    summary="Discussed next steps",
    key_points=["Point 1", "Point 2"],
    outcomes=["Action 1", "Action 2"],
    linked_artifact="N5/records/meetings/...",
    dry_run=False  # Set True to preview
)
```

**Guarantees:**
- ✅ Existing interactions preserved
- ✅ New interaction inserted before "## Quick Reference" section
- ✅ Metadata updated (last_updated, interaction_count)
- ✅ Backup created before modification

---

### 2. Tag Addition (Never Removal)

**Rule:** Tags can be ADDED but never automatically REMOVED. Removal requires explicit V confirmation.

**Implementation:**
```python
from safe_stakeholder_updater import add_tag_safely

add_tag_safely(
    profile_path=profile_path,
    tag="#stakeholder:advisor",
    tag_category="Verified",
    verification_source="Confirmed via Oct 15 meeting",
    dry_run=False
)
```

**Guarantees:**
- ✅ Checks if tag already exists (no-op if present)
- ✅ Adds to verified tags section without removing others
- ✅ Updates "Last reviewed" timestamp
- ✅ Backup created before modification

---

### 3. Section Enrichment (Merge Strategies)

**Rule:** Content sections can be enriched but not replaced. Three strategies:

#### Strategy A: Append (Default)
**Use case:** Adding new insights to existing section

```python
from safe_stakeholder_updater import enrich_section_safely

enrich_section_safely(
    profile_path=profile_path,
    section_name="Product & Mission",
    new_content="**Recent Update:** Launched new feature X",
    merge_strategy="append",  # Add to end
    dry_run=False
)
```

**Result:** New content appears after existing content in section

---

#### Strategy B: Prepend
**Use case:** Adding urgent/important context at top

```python
enrich_section_safely(
    profile_path=profile_path,
    section_name="Founder Motivation & Values",
    new_content="**Critical Update:** Founder announced pivot",
    merge_strategy="prepend",  # Add to start
    dry_run=False
)
```

**Result:** New content appears after section header, before existing content

---

#### Strategy C: Conflict (Safest)
**Use case:** Only add if section is empty

```python
enrich_section_safely(
    profile_path=profile_path,
    section_name="Product & Mission",
    new_content="Auto-generated product description",
    merge_strategy="conflict",  # Raise error if exists
    dry_run=False
)
```

**Result:** Raises `StakeholderUpdateConflict` if section has substantial content (>3 lines)

**Use this strategy when:**
- First-time population of a section
- Content should not be merged with existing
- Manual review required if conflicts

---

### 4. Automatic Backups

**Rule:** Every modification creates timestamped backup.

**Location:** `Knowledge/crm/profiles/.backups/`

**Format:** `{slug}_{YYYYMMDD_HHMMSS}.md`

**Example:**
```
Knowledge/crm/profiles/.backups/
├── hamoon-ekhtiari_20251012_143022.md
├── hamoon-ekhtiari_20251012_150145.md
└── hamoon-ekhtiari_20251015_091234.md
```

**Recovery:**
```bash
# List backups for stakeholder
ls -lt Knowledge/crm/profiles/.backups/hamoon-ekhtiari_*.md

# Restore from backup
cp Knowledge/crm/profiles/.backups/hamoon-ekhtiari_20251012_143022.md \
   Knowledge/crm/profiles/hamoon-ekhtiari.md
```

---

### 5. Update Preview (Dry-Run Mode)

**Rule:** Always preview changes before applying.

**Individual Operation Preview:**
```python
# Preview single update
_, diff = append_interaction(
    profile_path=profile_path,
    interaction_date="2025-10-15",
    interaction_title="Test Meeting",
    summary="Test summary",
    key_points=["Test"],
    outcomes=["Test"],
    dry_run=True  # Preview only
)

print(diff)  # Shows unified diff
```

---

**Batch Operation Preview:**
```python
from safe_stakeholder_updater import preview_update

update_operations = [
    {
        'type': 'append_interaction',
        'params': {
            'interaction_date': '2025-10-15',
            'interaction_title': 'Meeting 1',
            'summary': 'Summary 1',
            'key_points': ['Point 1'],
            'outcomes': ['Outcome 1']
        }
    },
    {
        'type': 'add_tag',
        'params': {
            'tag': '#stakeholder:advisor',
            'tag_category': 'Verified',
            'verification_source': 'Meeting 1 confirmed'
        }
    }
]

preview_path = preview_update(
    profile_path=profile_path,
    update_operations=update_operations
)

# Review file: Knowledge/crm/profiles/.pending_updates/{slug}_update_preview_*.md
```

**Preview includes:**
- All proposed changes
- Unified diffs for each operation
- Parameters for each operation
- Error messages if conflicts detected

---

## Integration Points

### A. Meeting Transcript Processing

**Hook:** After transcript ingestion, auto-update stakeholder profile

```python
from stakeholder_manager import update_profile_from_transcript

# Extract from meeting transcript
summary = llm.extract_summary(transcript)
key_points = llm.extract_key_points(transcript)
outcomes = llm.extract_outcomes(transcript)

# Update profile safely
update_profile_from_transcript(
    email="hamoon@futurefit.ai",
    meeting_date="2025-10-15",
    meeting_title="Follow-up: Partnership",
    transcript_summary=summary,
    key_points=key_points,
    outcomes=outcomes,
    linked_artifact="N5/records/meetings/2025-10-15_hamoon/meeting_note.md",
    dry_run=False
)
```

**Result:**
- ✅ New interaction appended to profile
- ✅ Backup created automatically
- ✅ Index updated with last_interaction date
- ✅ Existing content preserved

---

### B. Auto-Profile Creation (New Stakeholders)

**Hook:** When new meeting is scheduled with external stakeholder

```python
from auto_create_stakeholder_profiles import create_stakeholder_profile_auto

# Detect new stakeholder from calendar
profile_path = create_stakeholder_profile_auto(
    email="new-person@company.com",
    name="New Person",
    calendar_event={
        'meeting_date': '2025-10-20',
        'meeting_summary': 'Intro Call',
        'description': 'Partnership exploration',
        'calendar_event_id': 'abc123'
    }
)

# Profile created with:
# - Email history (up to 100 messages)
# - LLM-analyzed fields (org, role, lead type)
# - Questions for V if uncertain
```

---

### C. Tag Suggestion (Weekly Review)

**Hook:** Sunday evening digest with suggested tags for new contacts

```python
# Generate suggested tags from email analysis
suggested_tags = analyze_stakeholder_patterns(email_history)

# V reviews digest and approves
approved_tags = ["#stakeholder:advisor", "#priority:high"]

# Apply verified tags safely
for tag in approved_tags:
    add_tag_safely(
        profile_path=profile_path,
        tag=tag,
        tag_category="Verified",
        verification_source="Weekly review 2025-10-13",
        dry_run=False
    )
```

---

## Error Handling

### Conflict Detection

**When raised:** `StakeholderUpdateConflict`

**Scenarios:**
1. Section enrichment with `merge_strategy="conflict"` encounters existing content
2. Unexpected profile format (missing expected sections)
3. Unable to find safe insertion point

**Handling:**
```python
from safe_stakeholder_updater import StakeholderUpdateConflict

try:
    enrich_section_safely(
        profile_path=profile_path,
        section_name="Product & Mission",
        new_content=auto_generated_content,
        merge_strategy="conflict",
        dry_run=False
    )
except StakeholderUpdateConflict as e:
    logger.warning(f"Conflict detected: {e}")
    # Flag for manual review
    flag_for_v_review(profile_path, error=str(e))
```

---

### Profile Format Validation

**Check before updates:**
```python
def validate_profile_format(profile_path: Path) -> bool:
    """Check if profile has expected sections."""
    content = profile_path.read_text()
    
    required_sections = [
        "## Relationship Context",
        "## Interaction History",
        "## Quick Reference"
    ]
    
    for section in required_sections:
        if section not in content:
            logger.error(f"Missing section: {section}")
            return False
    
    return True
```

---

## Best Practices

### 1. Always Use Dry-Run First
```python
# Preview changes
update_profile_from_transcript(..., dry_run=True)

# Review output
# If satisfied, run again with dry_run=False
update_profile_from_transcript(..., dry_run=False)
```

---

### 2. Batch Updates → Single Preview
```python
# Multiple operations
operations = [
    {'type': 'append_interaction', 'params': {...}},
    {'type': 'add_tag', 'params': {...}},
    {'type': 'enrich_section', 'params': {...}}
]

# Preview all at once
preview_path = preview_update(profile_path, operations)

# Review file, then apply if approved
for op in operations:
    # Apply each operation
    ...
```

---

### 3. Manual Edits → Mark as "Human-Verified"
```markdown
## Product & Mission
<!-- HUMAN-VERIFIED: 2025-10-12 by V -->

**What FutureFit does**: Large-scale career support platform...
```

**Purpose:** Signal to future automation that this content is V-curated

---

### 4. Never Auto-Delete Content
- ❌ Never remove sections automatically
- ❌ Never remove existing tags automatically
- ❌ Never replace existing interaction entries
- ✅ Only ADD or APPEND content
- ✅ Deletions require explicit V command

---

## Monitoring & Recovery

### Backup Retention
**Policy:** Keep all backups for 90 days, then archive

```bash
# Cleanup script (manual)
find Knowledge/crm/profiles/.backups -type f -mtime +90 -name "*.md" \
  -exec gzip {} \; \
  -exec mv {}.gz Knowledge/crm/profiles/.backups/archive/ \;
```

---

### Audit Log
**Location:** `Knowledge/crm/profiles/.update_log.jsonl`

**Format:**
```json
{"timestamp": "2025-10-12T14:30:22Z", "profile": "hamoon-ekhtiari.md", "operation": "append_interaction", "dry_run": false, "backup": "hamoon-ekhtiari_20251012_143022.md"}
{"timestamp": "2025-10-12T15:01:45Z", "profile": "hamoon-ekhtiari.md", "operation": "add_tag", "tag": "#stakeholder:partner:collaboration", "backup": "hamoon-ekhtiari_20251012_150145.md"}
```

**Query recent updates:**
```bash
# Last 10 updates
tail -n 10 Knowledge/crm/profiles/.update_log.jsonl | jq

# Updates to specific profile
grep "hamoon-ekhtiari" Knowledge/crm/profiles/.update_log.jsonl | jq
```

---

## Testing

### Unit Test: Append Interaction
```python
def test_append_interaction_preserves_content():
    # Create test profile with manual content
    profile = create_test_profile_with_manual_content()
    
    # Append new interaction
    append_interaction(
        profile_path=profile,
        interaction_date="2025-10-15",
        interaction_title="Test Meeting",
        summary="Test",
        key_points=["Test"],
        outcomes=["Test"],
        dry_run=False
    )
    
    # Verify manual content still present
    updated_content = profile.read_text()
    assert "Manually-crafted insight" in updated_content
    assert "## Interaction History" in updated_content
    assert "2025-10-15: Test Meeting" in updated_content
```

---

### Integration Test: Full Workflow
```python
def test_meeting_to_profile_update_workflow():
    # 1. Schedule meeting with new stakeholder
    calendar_event = create_test_calendar_event()
    
    # 2. Auto-create profile
    profile = create_stakeholder_profile_auto(
        email="test@example.com",
        name="Test Person",
        calendar_event=calendar_event
    )
    
    # 3. Add manual insights
    add_manual_content(profile, "Product & Mission", "Detailed analysis")
    
    # 4. Process meeting transcript
    update_profile_from_transcript(
        email="test@example.com",
        meeting_date="2025-10-15",
        meeting_title="Follow-up",
        transcript_summary="Summary",
        key_points=["Point 1"],
        outcomes=["Outcome 1"],
        linked_artifact="...",
        dry_run=False
    )
    
    # 5. Verify manual content preserved
    updated_content = profile.read_text()
    assert "Detailed analysis" in updated_content  # Manual content
    assert "2025-10-15: Follow-up" in updated_content  # New interaction
```

---

## Summary

### Protected Operations ✅
- ✅ Append interactions (never overwrite)
- ✅ Add tags (never remove)
- ✅ Enrich sections (merge strategies)
- ✅ Automatic backups
- ✅ Preview/dry-run mode
- ✅ Audit logging

### Prohibited Operations ❌
- ❌ Replace existing sections
- ❌ Remove tags automatically
- ❌ Delete interaction entries
- ❌ Modify without backup
- ❌ Updates without conflict detection

### Key Files
- **Implementation:** `file 'N5/scripts/safe_stakeholder_updater.py'`
- **Integration:** `file 'N5/scripts/stakeholder_manager.py'`
- **Backups:** `Knowledge/crm/profiles/.backups/`
- **Previews:** `Knowledge/crm/profiles/.pending_updates/`
- **Audit Log:** `Knowledge/crm/profiles/.update_log.jsonl`

---

**Next Steps:**
1. Test safe updater with Hamoon's profile (dry-run)
2. Integrate with meeting transcript workflow
3. Add audit logging
4. Deploy to scheduled meeting prep task

---

**Related Documentation:**
- `file 'N5/docs/STAKEHOLDER-TAGGING-COMPLETE.md'` — Tag taxonomy
- `file 'N5/docs/TAG-TAXONOMY-MASTER.md'` — Tag reference
- `file 'N5/commands/deep-research-due-diligence.md'` — Profile enrichment
