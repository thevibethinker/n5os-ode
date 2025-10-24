# Phase 1: Factual Corrections System — READY

**Built:** 2025-10-22  
**Status:** Registry + Monitor complete, ready for diff engine

---

## What's Operational

### 1. Email Registry ✅
**File:** `N5/scripts/email_registry.py`  
**Purpose:** Track all generated follow-up emails

**Commands:**
```bash
# Create entry when email generated
python3 N5/scripts/email_registry.py create \
  --id email_2025-10-22_brin_001 \
  --meeting-id 2025-10-22_external-brin \
  --stakeholder "Brinleigh Murphy-Reuter" \
  --email brin@example.com \
  --draft-path N5/records/.../draft.md

# Mark as sent (manual)
python3 N5/scripts/email_registry.py mark-sent \
  --id email_2025-10-22_brin_001 \
  --sent-path N5/records/.../sent.eml

# Check unsent (follow-up reminders)
python3 N5/scripts/email_registry.py check-unsent

# List all entries
python3 N5/scripts/email_registry.py list --status generated
```

### 2. Gmail Monitor ✅
**File:** `N5/scripts/gmail_monitor.py`  
**Purpose:** Auto-detect when generated emails were sent

**Commands:**
```bash
# Scan Gmail for sent emails (auto-update registry)
python3 N5/scripts/gmail_monitor.py scan --lookback-days 7

# Dry run (preview only)
python3 N5/scripts/gmail_monitor.py scan --dry-run
```

**Integration:** Ready for use_app_gmail hookup (placeholder in place)

---

## Next: Diff Engine

**Remaining for Phase 1:**
1. Diff engine (`email_corrections.py`)
   - Extract semantic differences
   - Generate factual corrections JSON
   - Auto-apply certain corrections
   
2. Integration with email generator
   - Auto-create registry entry on generation
   - Append pre-flight checklist
   
3. Cron job for Gmail monitor (every 30min)

---

## Key Design Decisions

**Facts, not lessons:**
- Immediate patches to ground truth
- No interpretive review needed for certain corrections
- Fast-approve inline for obvious fixes

**Tone adjustments:**
- Per-conversation variables (not global defaults)
- System can nudge within context

**Knowledge gating:**
- Meeting content blocked until corrections applied
- validation_required flag cleared after corrections

---

**Status:** Registry + Monitor operational. Ready for diff engine build.

---
*Built 2025-10-22 | Conversation con_frSxWyuzF9e9DgbU | Phase 1 Partial*
