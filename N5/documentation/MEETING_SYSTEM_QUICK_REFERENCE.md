# Meeting Processing System — Quick Reference

**Quick access guide for common tasks**

---

## Common Commands

### Process a Single Meeting

```bash
# From local file
N5: meeting-process /path/to/transcript.txt \
  --type sales \
  --stakeholder customer_founder

# From Google Drive
N5: meeting-process <gdrive_file_id> \
  --type coaching \
  --stakeholder candidate_job_seeker

# Quick mode (action items only)
N5: meeting-process transcript.txt \
  --type networking \
  --stakeholder community_manager \
  --mode quick

# Auto-create Gmail draft
N5: meeting-process transcript.txt \
  --type sales \
  --stakeholder customer_founder \
  --output-format gmail-draft
```

### Batch Process from Google Drive Folder

```bash
N5: transcript-ingest <gdrive_folder_id> \
  --auto-classify \
  --batch-size 5
```

---

## Meeting Types

| Type | Use When | Key Blocks Generated |
|------|----------|---------------------|
| `sales` | Customer/prospect meetings | Deal intelligence, buying signals |
| `community_partnerships` | Partnership discussions | Partnership scope, collaboration terms |
| `coaching` | Career coaching sessions | Career insights, development plans |
| `networking` | Networking conversations | Warm intros, connection opportunities |
| `fundraising` | Investor meetings | Investor thesis, due diligence |

**Multi-classification:** Use comma-separated types
```bash
--type sales,community_partnerships
```

---

## Stakeholder Types

| Type | Description |
|------|-------------|
| `customer_founder` | Company founder/CEO customer |
| `customer_hiring_manager` | Hiring manager customer |
| `customer_recruiting_lead` | Recruiting lead customer |
| `customer_channel_partner` | Channel/referral partner |
| `community_manager` | Community leader/organizer |
| `candidate_job_seeker` | Job seeker you're coaching |
| `investor` | Angel investor |
| `vc` | Venture capital investor |

**Multi-stakeholder:** Use comma-separated types
```bash
--stakeholder vc,customer_channel_partner
```

---

## Processing Modes

| Mode | Blocks | Duration | Best For |
|------|--------|----------|----------|
| `quick` | Action items only | ~30s | Quick extraction |
| `essential` | Follow-up email, action items, decisions | ~1-2 min | Standard workflow |
| `full` | All applicable blocks | ~3-5 min | Complete analysis |

**Default:** `full`

---

## File Locations Reference

### Commands
- Main command: `file 'N5/commands/meeting-process.md'`
- Batch ingest: `file 'N5/commands/transcript-ingest.md'`
- Follow-up generator: `file 'N5/commands/follow-up-email-generator.md'`

### Scripts
- **Orchestrator:** `file 'N5/scripts/meeting_intelligence_orchestrator.py'`
- **Blocks:** `file 'N5/scripts/blocks/'`
  - `meeting_info_extractor.py`
  - `follow_up_email_generator.py`
  - `action_items_extractor.py`
  - `decisions_extractor.py`
  - `key_insights_extractor.py`
  - `stakeholder_profile_generator.py`
  - `warm_intro_detector.py`
  - `risks_detector.py`
  - `opportunities_detector.py`
  - `user_research_extractor.py`
  - `competitive_intel_extractor.py`
  - `deal_intelligence_generator.py`
  - `career_insights_generator.py`
  - `investor_thesis_generator.py`
  - `partnership_scope_generator.py`
  - `dashboard_generator.py`
  - `list_integrator.py`

### Schemas
- **Metadata:** `file 'N5/schemas/meeting-metadata.schema.json'`
- **Index:** `file 'N5/schemas/index.schema.json'`
- **Lists:** `file 'N5/schemas/lists.item.schema.json'`

### Outputs
- **Meetings directory:** `file 'Careerspan/Meetings/'`
- **Lists integration:** `file 'N5/lists/'`
- **Logs:** `file 'N5/logs/meeting-process/'`

---

## Output Files Guide

### What to Review First

1. **`REVIEW_FIRST.md`** - Executive dashboard
   - Priority actions
   - Key metrics
   - Quick links to all blocks

### Ready-to-Use Outputs

2. **`OUTPUTS/follow_up_email.md`** - Copy/paste into email
3. **`OUTPUTS/warm_intro_*.md`** - One file per intro

### Intelligence Files

4. **`INTELLIGENCE/action_items.md`** - Your tasks + their tasks
5. **`INTELLIGENCE/decisions.md`** - Decisions made
6. **`INTELLIGENCE/key_insights.md`** - Strategic takeaways
7. **`INTELLIGENCE/stakeholder_profile.md`** - CRM enrichment

### Optional Intelligence (if detected)

8. **`INTELLIGENCE/risks.md`** - Concerns, blockers
9. **`INTELLIGENCE/opportunities.md`** - Upsells, partnerships
10. **`INTELLIGENCE/user_research.md`** - Pain points, quotes
11. **`INTELLIGENCE/competitive_intel.md`** - Competitors mentioned

### Category-Specific

12. **`INTELLIGENCE/deal_intelligence.md`** (sales)
13. **`INTELLIGENCE/career_insights.md`** (coaching/networking)
14. **`INTELLIGENCE/investor_thesis.md`** (fundraising)
15. **`INTELLIGENCE/partnership_scope.md`** (community_partnerships)

---

## Block Generation Logic

### Universal Blocks
*Always generated*
- Follow-up email
- Action items
- Decisions
- Key insights
- Stakeholder profile

### Conditional Blocks
*Generated only if content detected (70%+ confidence)*
- Warm intros
- Risks
- Opportunities
- User research (80%+ confidence)
- Competitive intel (80%+ confidence)

### Category-Specific Blocks
*Generated based on meeting type*
- Deal intelligence → `--type sales`
- Career insights → `--type coaching` or `networking`
- Investor thesis → `--type fundraising`
- Partnership scope → `--type community_partnerships`

---

## Metadata Quick Reference

### Finding Meeting ID
```bash
# In _metadata.json
cat _metadata.json | jq '.meeting_id'
```

### Checking Processing Status
```bash
# View approval status
cat _metadata.json | jq '.approval.status'

# View blocks generated
cat _metadata.json | jq '.processing.blocks_generated'

# View any errors
cat _metadata.json | jq '.processing.errors'
```

### Intelligence Metrics
```bash
# View all intelligence counts
cat _metadata.json | jq '.intelligence'
```

---

## Troubleshooting

### Transcript Not Found
**Error:** `FileNotFoundError: Transcript not found`  
**Solution:** Check path, ensure file exists, use absolute path

### Google Drive Error
**Error:** `Google Drive fetch failed`  
**Solution:** Verify app connection, check file permissions, ensure valid file ID

### Block Generation Failed
**Error:** Block failed but processing continued  
**Solution:** Check `_metadata.json` → `processing.errors`, review logs in `N5/logs/meeting-process/`

### No Email History
**Message:** "Email history: not found"  
**Note:** Non-critical, processing continues. Check Gmail app connection if needed.

### Low Confidence Blocks Skipped
**Message:** Block skipped (confidence < 70%)  
**Explanation:** System detected content but confidence too low. Review transcript manually if needed.

---

## Integration with N5 Lists

### Automatic List Population

**Action Items:**
```bash
# View your action items from meeting
N5: lists-find action-items --filter "meeting_id=a83f92"
```

**Warm Intros:**
```bash
# View pending intros
N5: lists-find warm-intros --status pending
```

**Must Contact:**
```bash
# High-priority follow-ups
N5: lists-find must-contact --urgency high
```

### Manual List Operations

**Add item to list:**
```bash
N5: lists-add action-items "Follow up with Logan about pricing"
```

**Update item:**
```bash
N5: lists-set action-items <item_id> --status completed
```

---

## Tips & Best Practices

### For Best Results

1. **Include meeting context in filename:** `2025-10-09_sales_call_acme_corp.txt`
2. **Use consistent speaker labeling:** `Logan:` vs `LC:` (pick one format)
3. **Include timestamps if available:** Improves duration estimation
4. **Add meeting date in transcript header:** Improves metadata extraction

### Workflow Recommendations

**Post-Meeting Checklist:**
1. Run `meeting-process` with appropriate flags
2. Review `REVIEW_FIRST.md`
3. Edit `OUTPUTS/follow_up_email.md` if needed
4. Send follow-up email
5. Check action items added to lists
6. (Optional) Run `meeting-approve` to mark as complete

### When to Use Each Mode

- **Quick:** In a rush, just need action items
- **Essential:** Standard post-meeting workflow
- **Full:** Important meetings, want complete intelligence

---

## Example Workflows

### Workflow 1: Standard Sales Call

```bash
# 1. Process meeting
N5: meeting-process transcript.txt \
  --type sales \
  --stakeholder customer_founder \
  --mode essential

# 2. Review output
cat REVIEW_FIRST.md

# 3. Send follow-up
# (Copy from OUTPUTS/follow_up_email.md)

# 4. Check action items added
N5: lists-find action-items --recent 5
```

### Workflow 2: Quick Networking Call

```bash
# Fast extraction
N5: meeting-process transcript.txt \
  --type networking \
  --stakeholder candidate_job_seeker \
  --mode quick

# Review action items only
cat INTELLIGENCE/action_items.md
```

### Workflow 3: Important Partnership Discussion

```bash
# Full analysis
N5: meeting-process transcript.txt \
  --type community_partnerships,sales \
  --stakeholder customer_channel_partner \
  --mode full

# Review everything
cat REVIEW_FIRST.md

# Check for warm intros
ls OUTPUTS/warm_intro_*

# Review partnership scope
cat INTELLIGENCE/partnership_scope.md
```

---

## Related Commands

**After meeting processing:**
```bash
# Approve meeting outputs
N5: meeting-approve <meeting_folder_name>

# Search previous meetings
N5: meeting-search --stakeholder logan-currie

# Generate cross-meeting insights
N5: meeting-summary --stakeholder logan-currie --last 3
```

---

## Quick Links

- **Full Architecture:** `file 'N5/documentation/MEETING_SYSTEM_ARCHITECTURE.md'`
- **Command Docs:** `file 'N5/commands/meeting-process.md'`
- **Example Outputs:** `file 'Careerspan/Meetings/External/2025-09-19_logan-currie_shujaat-ahmad_vrijen-attawar/'`
- **Schemas:** `file 'N5/schemas/meeting-metadata.schema.json'`
