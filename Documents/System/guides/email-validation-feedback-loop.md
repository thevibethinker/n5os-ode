# Email Validation Feedback Loop

**Purpose:** Human-in-the-loop validation gate that prevents polluting stable knowledge with incorrect interpretations  
**Version:** 1.0.0  
**Date:** 2025-10-22

---

## Core Concept

**The Problem:** AI-generated drafts may misinterpret relationships, business details, or context. Without validation, these errors propagate into stable knowledge.

**The Solution:** Treat the sent email as ground truth. Compare draft vs sent, extract corrections, update stable knowledge only after validation.

---

## Architecture

```
Meeting → Draft Email (tentative) → V edits → Sent Email (ground truth) → Diff → Update Knowledge
                ↓                                        ↓
         [Staging Area]                          [Stable Knowledge]
```

### Flow

1. **Generate Draft** - System creates email from meeting context
2. **V Edits** - You review, correct relationship nuances, business details, tone
3. **Send** - You send the actual email
4. **Compare** - System diffs draft vs sent
5. **Learn** - System extracts corrections and updates stable knowledge
6. **Validate** - Only validated info moves to Knowledge/ and CRM

---

## What Gets Compared

### 1. Relationship Depth
- **Draft says:** "Logan speaks highly of you"
- **Sent says:** "Logan told me you'd be perfect for this"
- **Learning:** Not a warm intro—existing friendship, peer-level

### 2. Business Details
- **Draft says:** "$100/month"
- **Sent says:** "$100 one-time"
- **Learning:** One-time purchase, not recurring

### 3. Tone & Formality
- **Draft says:** "Dear Brinleigh,"
- **Sent says:** "Hey Brin,"
- **Learning:** Casual friendship, nickname basis

### 4. Commitments & Next Steps
- **Draft says:** "I'll send the sample this week"
- **Sent says:** "Attached is the sample"
- **Learning:** Immediate delivery, not deferred

### 5. Context Additions
- **Draft:** No mention of shared history
- **Sent:** "Remember when we talked about this at Logan's?"
- **Learning:** Add shared history to relationship context

---

## Implementation Phases

### Phase 1: Manual Diff (Immediate)
**Tool:** `email_validation_diff.py`

```bash
# Compare draft vs sent, output corrections
python3 N5/scripts/email_validation_diff.py \
  --draft meeting_folder/draft_email.txt \
  --sent meeting_folder/sent_email.txt \
  --output corrections.json
```

**Outputs:**
- `corrections.json` - Structured diffs
- `learning_report.md` - Human-readable summary
- `profile_updates.json` - Proposed CRM changes

### Phase 2: Semi-Automated (Week 2)
**Flow:**
1. System detects sent email (via Gmail integration or manual paste)
2. Auto-loads corresponding draft
3. Generates diff report
4. Proposes knowledge updates
5. **You approve** before committing to stable knowledge

### Phase 3: Automated with Review (Month 2)
**Flow:**
1. System auto-detects sent emails
2. Auto-diffs, auto-proposes updates
3. **You review summary weekly**
4. Batch-approve/reject changes
5. System learns from approval patterns

---

## Diff Categories

### Critical (Always Review)
- Relationship depth changes
- Business terms (pricing, commitments)
- Person/company name corrections
- Timeline/deadline shifts

### Important (Review Weekly)
- Tone adjustments
- Link additions/removals
- Next step clarifications
- Shared history additions

### Minor (Auto-learn)
- Typo fixes
- Formatting changes
- Salutation variations
- Sign-off changes

---

## Knowledge Update Rules

### Rule 1: Relationship Depth
**Trigger:** Draft formality ≠ Sent formality  
**Action:** Update `Knowledge/crm/individuals/{person}.md` → Relationship Depth  
**Example:** "Warm intro" → "Existing friendship"

### Rule 2: Business Terms
**Trigger:** Pricing/commitment changes  
**Action:** Update engagement history with corrections  
**Example:** "$100/month" → "$100 one-time"

### Rule 3: Shared History
**Trigger:** Sent email references events not in CRM  
**Action:** Add to relationship timeline  
**Example:** "Logan's party" → Add shared event to history

### Rule 4: Person Details
**Trigger:** Nicknames, role corrections, company changes  
**Action:** Update Basic Information section  
**Example:** "Brinleigh" → "Brin (preferred nickname)"

### Rule 5: Context Additions
**Trigger:** Sent email includes context not in meeting notes  
**Action:** Append to Notes section with [VALIDATED] tag  
**Example:** "Tool evaluation criteria" → Add to Business Context

---

## Validation Gates

### Gate 1: Draft Generation (Permissive)
- Allow tentative interpretations
- Flag low-confidence items
- Mark as `[DRAFT - NEEDS VALIDATION]`

### Gate 2: Email Sent (Validation Point)
- Diff draft vs sent
- Extract corrections
- **Hold updates in staging**

### Gate 3: Human Review (Approval)
- Review proposed changes
- Approve/reject/modify
- **Only then** commit to stable knowledge

---

## File Structure

```
N5/records/meetings/{meeting_id}/
├── draft_email.txt          # Generated draft
├── sent_email.txt           # Actual sent email (paste or auto-sync)
├── email_diff.json          # Structured diff
├── validation_report.md     # Human-readable summary
└── knowledge_updates.json   # Proposed CRM/Knowledge changes

N5/staging/knowledge_updates/
├── pending/                 # Awaiting approval
├── approved/                # Ready to commit
└── rejected/                # Declined updates
```

---

## CLI Commands

### Generate Diff
```bash
n5 email diff \
  --meeting 2025-10-22_external-brin \
  --show-learning
```

### Review Pending Updates
```bash
n5 email review-updates \
  --category relationship  # or business, context, all
```

### Approve Updates
```bash
n5 email approve-updates \
  --batch pending/*.json
```

### Reject Updates
```bash
n5 email reject-updates \
  --id update_12345 \
  --reason "Incorrect interpretation"
```

---

## Success Metrics

### Accuracy Improvement
- Track: % of drafts requiring major corrections
- Goal: <20% after 10 iterations

### Knowledge Quality
- Track: CRM profile completeness over time
- Goal: 80%+ complete after 20 validated emails

### Learning Rate
- Track: Corrections per category over time
- Goal: 50% reduction in repeat errors after 20 emails

---

## Implementation Priority

**Phase 1 (This Week):**
- [ ] Build `email_validation_diff.py`
- [ ] Create manual diff workflow
- [ ] Test on Brinleigh email

**Phase 2 (Next Week):**
- [ ] Semi-automated detection
- [ ] Batch review interface
- [ ] Integration with CRM update scripts

**Phase 3 (Month 2):**
- [ ] Gmail integration for auto-sync
- [ ] Pattern learning from approvals
- [ ] Auto-categorize critical vs minor

---

## Key Insight

**"The sent email is the blocker that prevents pollution of stable knowledge."**

This architecture ensures:
1. ✅ System can experiment with interpretations
2. ✅ Human validates before commitment
3. ✅ Knowledge base stays clean
4. ✅ System learns from corrections
5. ✅ Compound improvement over time

**Status:** Spec complete, ready for implementation

---
*Version 1.0.0 | 2025-10-22 | System Upgrade*
