
# Email Validation Workflow — Learning from Ground Truth

**Core Principle:** The email YOU send is ground truth. Differences reveal calibration errors that must be corrected before promoting content to stable knowledge.

---

## The Problem

**Without validation:**
- Generated emails make assumptions (relationship depth, pricing, formality)
- Errors propagate into CRM ("warm contact" when actually "friend")
- Knowledge base gets polluted with wrong information
- System never learns from its mistakes

**With validation:**
- Your sent email = ground truth
- System diffs generated vs sent
- Extracts learning signals
- BLOCKS knowledge promotion until validated
- CRM/notes updated with corrections

---

## Workflow

```
1. Generate Draft
   ↓
2. User Edits & Sends
   ↓
3. System Compares [Draft vs Sent]
   ↓
4. Extract Learning Signals
   ├─ Relationship depth mismatches
   ├─ Pricing/fact errors
   ├─ Tone calibration
   └─ Missing context
   ↓
5. Critical Errors? 
   ├─ YES → BLOCK knowledge promotion
   └─ NO → Allow promotion
   ↓
6. Apply Learnings
   ├─ Update CRM records
   ├─ Flag meeting notes
   └─ Log preferences
```

---

## Learning Signal Categories

### 1. **Relationship Depth** (Critical)
**Detects:**
- Third-party references when should be direct ("Logan speaks highly" → remove, you're friends)
- Formality mismatch (formal language with friends)
- Missing shared context

**Actions:**
- Update CRM: `relationship_depth` field
- Adjust tone calibration for future emails
- BLOCK promotion if wrong by 2+ levels

**Example:**
```
Generated: "Logan speaks highly of you"
Sent: [removed line]
Signal: You, Logan, and Brinleigh are FRIENDS, not professional contacts
Action: Update CRM from "warm_contact" to "friend"
```

---

### 2. **Pricing/Facts** (Critical)
**Detects:**
- Wrong amounts ($100 vs $100/month)
- Incorrect frequencies (one-time vs recurring)
- Misquoted commitments

**Actions:**
- Flag meeting notes with correction
- Update pricing in CRM deal stage
- BLOCK promotion until corrected

**Example:**
```
Generated: "$100/month"
Sent: "$100"
Signal: Payment is ONE-TIME, not recurring
Action: Update meeting notes, block promotion
```

---

### 3. **Tone/Formality** (Important)
**Detects:**
- Corporate jargon removed ("circle back", "synergize")
- Casual language added
- Voice shift

**Actions:**
- Log tone preference for stakeholder
- Adjust future email generation
- Update formality level in CRM

**Example:**
```
Generated: "Let's touch base to circle back"
Sent: "Let's chat again"
Signal: User prefers direct language
Action: Log preference, adjust tone model
```

---

### 4. **Context Depth** (Important)
**Detects:**
- User added significant content (>20% more text)
- Missing background/history
- Incomplete recall

**Actions:**
- Flag B-blocks as incomplete
- Review meeting processing pipeline
- Add missing context to notes

**Example:**
```
Generated: 800 chars
Sent: 1200 chars (+50%)
Signal: System missed context
Action: Review B-blocks for gaps
```

---

## Usage

### Basic Comparison
```bash
python3 N5/scripts/email_validation_learner.py \
  --meeting-folder N5/records/meetings/2025-10-22_external-brin \
  --generated-email generated_draft.txt \
  --sent-email sent_email.txt \
  --output learning_signals.json
```

### Apply Learnings
```bash
python3 N5/scripts/email_validation_learner.py \
  --meeting-folder N5/records/meetings/2025-10-22_external-brin \
  --generated-email generated_draft.txt \
  --sent-email sent_email.txt \
  --apply \
  --output learning_signals.json
```

### Dry Run (preview changes)
```bash
python3 N5/scripts/email_validation_learner.py \
  --meeting-folder N5/records/meetings/2025-10-22_external-brin \
  --generated-email generated_draft.txt \
  --sent-email sent_email.txt \
  --apply \
  --dry-run
```

---

## Output Format

```json
{
  "validation_passed": false,
  "total_signals": 3,
  "critical_errors": 2,
  "signals": [
    {
      "category": "relationship",
      "field": "relationship_depth",
      "generated_value": "Third-party reference via Logan",
      "sent_value": "Direct relationship",
      "confidence": "high",
      "impact": "critical",
      "suggested_action": "Update CRM: stakeholder is DIRECT friend"
    },
    {
      "category": "pricing",
      "field": "payment_frequency",
      "generated_value": "$100/month",
      "sent_value": "$100",
      "confidence": "high",
      "impact": "critical",
      "suggested_action": "Update meeting notes: pricing is $100 ONE-TIME"
    }
  ]
}
```

---

## Integration with Content Library

### Knowledge Promotion Gate

**Before validation:**
```
Meeting → B-Blocks → Draft Email
                         ↓
                    [STAGING AREA]
                         ↓
                    NOT in Knowledge/
```

**After validation:**
```
Draft Email → User Sends → Validation
                              ↓
                     Critical Errors?
                     ├─ YES → BLOCKED
                     └─ NO → Promoted
                              ↓
                        Knowledge/
                        CRM updated
```

**Critical errors = BLOCKER:**
- Relationship depth wrong by 2+ levels
- Pricing/fact errors
- Major context misses

**Non-critical = ALLOWED:**
- Tone adjustments
- Minor wording changes
- Style preferences

---

## Benefits

### 1. **Self-Correcting System**
- Learns from every email you send
- Calibrates to your actual communication style
- Reduces errors over time

### 2. **Trust in Knowledge Base**
- Only validated facts get promoted
- CRM stays clean
- No hallucination pollution

### 3. **Continuous Improvement**
- Relationship depth accuracy improves
- Pricing/fact checking improves
- Tone matching improves

### 4. **Audit Trail**
- Every correction logged
- Learning signals tracked
- Can review what system learned

---

## Workflow Integration

### Standalone Mode (Now)
```bash
# 1. Generate email
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder meetings/brin \
  --use-content-library \
  --output-dir drafts/

# 2. Edit and send manually

# 3. Validate
python3 N5/scripts/email_validation_learner.py \
  --meeting-folder meetings/brin \
  --generated-email drafts/email.txt \
  --sent-email sent/brin_email.txt \
  --apply
```

### Integrated Mode (Future)
```bash
# Single command workflow
python3 N5/scripts/email_workflow.py \
  --meeting-folder meetings/brin \
  --interactive \
  --auto-validate
  
# Generates draft → Opens editor → User sends → Auto-validates → Updates CRM
```

---

## Next Steps

1. **Build email editor integration** - One-click send + validate
2. **Add Gmail API** - Auto-fetch sent emails for comparison
3. **Build learning dashboard** - Visualize calibration improvements
4. **Add A/B testing** - Compare reply rates with/without validation

---

## Files

- **Script:** `N5/scripts/email_validation_learner.py`
- **Docs:** `N5/docs/email-validation-workflow.md`
- **Integration:** `N5/scripts/n5_follow_up_email_generator.py` (future)

---

**Version:** 1.0.0 | **Date:** 2025-10-22
