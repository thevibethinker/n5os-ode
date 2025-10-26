# Email Validation: Factual Corrections System

**Core Principle:** The email you send IS the correct version of reality. Generated draft = hypothesis. Sent email = ground truth. Differences = factual corrections to apply immediately.

**Not lessons. Facts.**

---

## Architecture

### 1. Email Generation Registry

**Purpose:** Track all generated follow-up emails and their send status

**Location:** `N5/registry/generated_emails.jsonl`

**Entry schema:**
```json
{
  "id": "email_2025-10-22_brin_001",
  "meeting_id": "2025-10-22_external-brin",
  "stakeholder": "Brinleigh Murphy-Reuter",
  "stakeholder_email": "brin@example.com",
  "generated_at": "2025-10-22T15:30:00Z",
  "draft_path": "N5/records/meetings/.../draft_v1.md",
  "status": "generated",  // generated | sent | abandoned
  "sent_at": null,
  "sent_email_path": null,
  "corrections_applied": false,
  "follow_up_after": "2025-10-24T15:30:00Z",  // 48hr default
  "tags": ["networking", "friend", "product_demo"]
}
```

### 2. Gmail Monitor (Automated)

**Frequency:** Every 30 mins (cron job or on-demand)

**Process:**
1. Load registry: get all `status: "generated"` entries
2. For each entry:
   - Search Gmail for sent email to stakeholder_email
   - Check: sent_date ≥ generated_at
   - If found:
     - Download email body
     - Save to `sent_email_path`
     - Update status → "sent"
     - Queue for diff extraction
   - If NOT found AND now > follow_up_after:
     - Notify user: "Draft for {stakeholder} generated {X} days ago, not sent. Follow up?"

### 3. Diff Engine (Factual Correction Extraction)

**Input:** draft.md + sent.eml  
**Output:** corrections.json (immediate applicability)

**Categories (factual only):**

```json
{
  "relationship_corrections": [
    {
      "field": "relationship_depth",
      "was": "warm_intro",
      "is": "friend_peer",
      "apply_to": "Knowledge/crm/individuals/brinleigh-murphy-reuter.md",
      "confidence": "certain"
    }
  ],
  "business_term_corrections": [
    {
      "field": "pricing",
      "context": "meeting_pipeline_service",
      "was": "$100/month",
      "is": "$100 one-time",
      "apply_to": "Knowledge/business/pricing.md",
      "confidence": "certain"
    }
  ],
  "content_library_corrections": [
    {
      "action": "deprecate",
      "item_id": "third_party_reference_template",
      "reason": "User removed this phrasing (friends don't need validation)",
      "apply_to": "N5/prefs/communication/content-library.json"
    },
    {
      "action": "promote",
      "content": "Your line about not having time to hire a Chief of Staff...",
      "type": "snippet",
      "tags": ["hook", "audience=founders", "topic=productivity"],
      "apply_to": "N5/prefs/communication/content-library.json"
    }
  ],
  "tone_adjustments": [
    {
      "context": "friend_stakeholder_email",
      "was": "formal_opener",
      "is": "casual_opener",
      "apply_as": "per_conversation_variable",  // NOT global default
      "confidence": "medium"
    }
  ],
  "link_corrections": [
    {
      "action": "removed_suggested",
      "link": "https://coffeespace.com",
      "reason": "User dropped from suggested resources",
      "counter": 2,  // Track repetition
      "apply_threshold": 3  // Stop suggesting after 3 removals
    }
  ]
}
```

### 4. Auto-Apply Rules (Immediate Patches)

**On diff extraction complete:**

```python
for correction in corrections['relationship_corrections']:
    if correction['confidence'] == 'certain':
        # Immediately patch CRM
        update_crm(correction['apply_to'], correction['field'], correction['is'])
        log_change(f"Patched {correction['field']}: {correction['was']} → {correction['is']}")

for correction in corrections['business_term_corrections']:
    if correction['confidence'] == 'certain':
        # Immediately update business knowledge
        update_knowledge(correction['apply_to'], correction['context'], correction['is'])

for correction in corrections['content_library_corrections']:
    if correction['action'] == 'deprecate':
        content_library.deprecate(correction['item_id'], reason=correction['reason'])
    elif correction['action'] == 'promote':
        content_library.add(correction['content'], tags=correction['tags'])

# Tone adjustments: apply as per-conversation variable (not global)
# Link discipline: increment counter, stop suggesting at threshold
```

**Fast-approve inline:**
- Obvious corrections (certain confidence, single-field) → auto-apply
- Complex corrections (multiple interrelated changes) → queue for quick review

### 5. Pre-Send Nudges (Pre-flight Checklist)

**When generating email:**
1. Load stakeholder CRM profile
2. Load past corrections for this stakeholder/type
3. If patterns detected, append preflight markdown:

```markdown
---
## Pre-flight Checklist

Based on past emails to **friends** like Brinleigh:
- [ ] Opener: casual (not formal "Dear X")
- [ ] Positioning: peer-to-peer (not consultant-to-client)
- [ ] CTA: soft ask (not presumptive)
- [ ] Sign-off: "—V" or "Best, Vrijen" (not "Sincerely")

**Link check:**
- Zo referral: ✓ (usually kept)
- Coffee Space: ⚠️ (you've removed this 2x for founders)

---
```

### 6. Knowledge Promotion Gating

**Rule:** Content from meetings cannot promote to stable knowledge until corrections applied.

**Implementation:**
```json
// Meeting artifact metadata
{
  "validation_required": true,
  "validation_status": "pending_sent_email",
  "generated_email_id": "email_2025-10-22_brin_001",
  "blocks_promotion": [
    "eloquent_lines",
    "resources",
    "stakeholder_intelligence"
  ]
}
```

**Promotion flow:**
1. Email generated → `validation_required: true`
2. Email sent → status updated, diff extracted
3. Corrections applied → `validation_required: false`
4. Only then: promote content to Knowledge/CRM/Content Library

### 7. Gmail Integration Commands

```bash
# Manual: Mark email as sent (with path to .eml file)
python3 N5/scripts/email_registry.py mark-sent \
  --email-id email_2025-10-22_brin_001 \
  --sent-path path/to/sent.eml

# Auto: Monitor Gmail for sent emails
python3 N5/scripts/gmail_monitor.py scan-for-sent

# Generate corrections from diff
python3 N5/scripts/email_corrections.py extract \
  --draft N5/records/.../draft.md \
  --sent N5/records/.../sent.eml \
  --output corrections.json

# Apply corrections (fast-approve)
python3 N5/scripts/email_corrections.py apply \
  --corrections corrections.json \
  --auto-apply-certain

# Follow-up reminder check
python3 N5/scripts/email_registry.py check-unsent
```

---

## Phase 1 Implementation (Today)

### Scope
1. **Registry system** (`N5/scripts/email_registry.py`)
   - Create/update entries
   - Mark as sent
   - Check for unsent (follow-up reminders)

2. **Gmail monitor** (`N5/scripts/gmail_monitor.py`)
   - Scan sent folder for matching emails
   - Download and save .eml
   - Update registry status

3. **Diff engine** (`N5/scripts/email_corrections.py`)
   - Extract semantic differences
   - Categorize as factual corrections
   - Generate corrections.json

4. **Auto-apply** (extension of email_corrections.py)
   - Apply certain corrections immediately
   - Queue uncertain for quick review

5. **Pre-flight nudges** (extension of email generator)
   - Generate checklist from past corrections
   - Append to draft

### Deliverables
- ✅ Registry JSONL with schema
- ✅ Gmail scan (every 30min or on-demand)
- ✅ Diff engine with 5 correction categories
- ✅ Auto-apply for certain corrections
- ✅ Pre-flight markdown generation
- ✅ Follow-up reminder system

### Acceptance Criteria
- Generate email → registry entry created
- Send via Gmail → detected within 30min
- Diff extracted → corrections.json produced
- Certain corrections → applied immediately
- CRM/pricing/content library → updated
- validation_required → cleared
- Unsent after 48hr → notification sent

---

**This is factual correction, not lesson learning. Immediate patches to ground truth.**

---

*Version 1.0.0 | 2025-10-22 | Factual Corrections System*
