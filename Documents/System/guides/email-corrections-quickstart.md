# Email Factual Corrections — Quick Start

**Purpose:** Learn from draft vs sent email differences (factual corrections, not lessons)  
**Version:** 1.0.0  
**Date:** 2025-10-22

---

## What This Does

The email you send = ground truth. System extracts factual corrections from differences, applies auto-fix rules, queues critical changes for review.

---

## Complete Workflow

### 1. Generate Email (Auto-registers)
```bash
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-22_external-brin \
  --use-content-library
```

**Output:** Draft email with pre-flight checklist + registry entry created

### 2. Edit & Send
- Review draft
- Make corrections
- Send from Gmail

### 3. Auto-Detection (Runs every 30min via cron)
```bash
python3 N5/scripts/gmail_monitor.py scan --lookback-days 7
```

**Action:** Detects sent email, updates registry, queues for diff

### 4. Extract Corrections
```bash
python3 N5/scripts/email_corrections.py extract \
  --draft N5/records/.../draft.md \
  --sent N5/records/.../sent.eml \
  --meeting-id 2025-10-22_external-brin \
  --stakeholder "Brinleigh Murphy-Reuter" \
  --output corrections.json \
  --apply \
  --dry-run
```

**Output:**
- Auto-apply corrections (relationship depth, link additions)
- Queue critical corrections (pricing, business terms)

### 5. Review Critical Corrections
```bash
# View queued corrections
cat corrections.json | jq '.corrections[] | select(.auto_apply == false)'

# Apply after review
python3 N5/scripts/email_corrections.py extract \
  --draft ... --sent ... \
  --apply  # Remove --dry-run
```

---

## Correction Categories

| Category | Examples | Auto-Apply? |
|----------|----------|-------------|
| Stakeholder | Relationship depth, formality | ✅ Yes |
| Business Terms | Pricing model, product names | ❌ No (critical) |
| Links | Link additions, removals | ✅ Additions only |
| Content Library | Deprecated snippets | ❌ No (review) |
| Tone | Sentence length, casualness | ✅ Yes (per-convo) |

---

## Key Commands

### Registry
```bash
# Check unsent emails (follow-up reminders)
python3 N5/scripts/email_registry.py check-unsent

# Mark email as sent manually
python3 N5/scripts/email_registry.py mark-sent \
  --id email_2025-10-22_brin_001 \
  --sent-path sent.eml

# List all generated emails
python3 N5/scripts/email_registry.py list
```

### Gmail Monitor
```bash
# Manual scan
python3 N5/scripts/gmail_monitor.py scan --lookback-days 7

# Dry run (preview only)
python3 N5/scripts/gmail_monitor.py scan --dry-run
```

### Corrections
```bash
# Extract only (no apply)
python3 N5/scripts/email_corrections.py extract \
  --draft draft.md --sent sent.eml \
  --meeting-id ... --stakeholder "..." \
  --output corrections.json

# Extract + auto-apply
python3 N5/scripts/email_corrections.py extract \
  --draft draft.md --sent sent.eml \
  --meeting-id ... --stakeholder "..." \
  --apply

# Dry run (preview changes)
python3 N5/scripts/email_corrections.py extract \
  --draft draft.md --sent sent.eml \
  --meeting-id ... --stakeholder "..." \
  --apply --dry-run
```

---

## Files

- **Registry:** `N5/registry/generated_emails.jsonl`
- **Scripts:**
  - `N5/scripts/email_registry.py`
  - `N5/scripts/gmail_monitor.py`
  - `N5/scripts/email_corrections.py`
- **Integration:** `N5/scripts/n5_follow_up_email_generator.py` (auto-registers)

---

## Cron Setup (Recommended)

```cron
# Scan Gmail every 30 minutes
*/30 * * * * cd /home/workspace && python3 N5/scripts/gmail_monitor.py scan --lookback-days 7 >> N5/logs/gmail_monitor.log 2>&1
```

---

**Version:** 1.0.0 | **Date:** 2025-10-22
