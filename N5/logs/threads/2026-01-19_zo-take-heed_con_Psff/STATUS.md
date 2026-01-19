---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.1
provenance: con_PsffYknEXs0T7a81
---

# Build Status: Zo Take Heed

## Current Status: ✓ BUILD COMPLETE (v1.1)

All features implemented. Ready for live testing.

---

## Feature Summary

### Core ZTH (v1.0)
- ✅ B00 extraction from transcripts
- ✅ Task type classification
- ✅ Worker file generation for blurb/email/warm-intro/research/custom
- ✅ MG-2 pipeline integration
- ✅ MG-3 and MG-5 agents deprecated

### Extensions (v1.1)
- ✅ **Speaker validation** — Only V/Vrijen can trigger ZTH
- ✅ **List integration** — "add to [list]" → appends to N5/lists/*.jsonl
- ✅ **Deal integration** — "add as deal" → syncs via deal system
- ✅ **CRM contacts** — "add as broker/lead" → must-contact.jsonl
- ✅ **Intro leads** — "can intro me to" → intro-leads.jsonl

---

## Task Type Summary

| Say This | Task Type | Behavior |
|----------|-----------|----------|
| "omit pricing from recap" | `directive` | Influences B01/B14 inline |
| "prep a follow-up email" | `follow_up_email` | Auto-executes email gen |
| "generate a blurb" | `blurb` | Auto-executes blurb gen |
| "draft warm intro to Sarah" | `warm_intro` | Auto-executes intro gen |
| "research their funding" | `research` | Queues worker file (HITL) |
| "add to startup ideas list" | `list_add` | Direct add to N5/lists/ |
| "add Handshake as a deal" | `deal_add` | Direct add via deal system |
| "update deal status" | `deal_update` | Direct update via deal system |
| "add Sarah as a broker" | `crm_contact` | Direct add to must-contact |
| "Jake can intro me to Lisa" | `intro_lead` | Direct add to intro-leads |

---

## Artifacts Created

| Path | Purpose |
|------|---------|
| `file 'Prompts/Blocks/Generate_B00.prompt.md'` | B00 extraction (v1.1 with speaker validation) |
| `file 'N5/schemas/B00_ZO_TAKE_HEED.schema.json'` | JSONL schema |
| `file 'N5/scripts/zth_spawn_worker.py'` | Worker generator + direct execution |
| `file 'N5/scripts/zth_validate_b00.py'` | Validation utility |
| `file 'N5/templates/zth_worker.md'` | Worker file template |
| `file 'N5/lists/intro-leads.jsonl'` | Intro lead tracking |
| `file 'Prompts/Meeting Block Generation.prompt.md'` | MG-2 (v2.4 with B00) |

---

## Agents Modified

| Agent | Status | Notes |
|-------|--------|-------|
| MG-3 (Blurb Generation) | **DISABLED** | Replaced by ZTH trigger |
| MG-5 (Follow-Up Generation) | **DISABLED** | Replaced by ZTH trigger |

---

## How to Use

**During a meeting, say:**
> "Zo take heed, [instruction]"

Examples:
- "Zo take heed, prep a follow-up email for Jake"
- "Zo take heed, add Handshake as a deal, Jake can intro me"
- "Zo take heed, add this business model to the startup ideas list"
- "Zo take heed, Sarah mentioned she can connect me to Lisa at Stripe, track that"
- "Zo take heed, omit the pricing discussion from the recap"

**Manual trigger (any meeting):**
```bash
# Run blurb generator
file 'Prompts/Blurb-Generator.prompt.md'

# Run follow-up email generator  
file 'Prompts/Follow-Up Email Generator.prompt.md'
```

---

## Test Commands

```bash
# Validate B00 schema
python3 N5/scripts/zth_validate_b00.py --test

# Test worker generation
python3 N5/scripts/zth_spawn_worker.py --test

# Process B00 for a meeting
python3 N5/scripts/zth_spawn_worker.py --meeting-folder <path> --json
```
