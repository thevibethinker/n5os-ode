# Output Review Integration - Implementation Proposal

**Date:** 2025-10-20  
**Status:** Awaiting V approval  
**Effort:** ~2-3 hours

---

## Summary

Integrate the existing Output Review Tracker system with conversation-end workflow to:
1. **Track outputs flagged during conversations** - show summary at end
2. **Capture "what would make this optimal"** - not just scores, but improvement context
3. **Remind about unflagged deliverables** - nudge to review major outputs

---

## Current State

✅ **Already implemented:**
- Output Review Tracker system (`N5/scripts/review_*.py`)
- CLI commands: `n5 review add|list|show|status|comment|export`
- JSONL storage with provenance tracking
- Commands registered in `commands.jsonl`

❌ **Missing:**
- Integration with conversation-end workflow
- Improvement notes field (what to change, optimal state)
- Deliverable detection at conversation-end
- Reminder when major outputs aren't flagged

---

## Proposed Changes

### 1. Add Improvement Notes Field

**Current:** Review entries have `flagged_reason` (why flagged) and `sentiment` (rating)

**Proposed:** Add rich improvement context:

```json
{
  "review": {
    "sentiment": "issue",
    "flagged_reason": "Tone too formal",
    "improvement_notes": {
      "what_to_change": "Use 'you' instead of 'one'; cut corporate speak in para 3",
      "optimal_state": "Conversational coaching voice, 800-1000 words, personal pronouns",
      "priority": "high"
    }
  }
}
```

**CLI enhancement:**
```bash
n5 review add Documents/email.md \
  --sentiment issue \
  --reason "Too formal" \
  --improve "Use 'you' not 'one', cut jargon in para 2" \
  --optimal "Warm professional, max 150 words, conversational"
```

---

### 2. Conversation-End Integration

**New Phase 2.75: Output Review Summary**

Insert between placeholder scan (Phase 2.5) and personal intelligence (Phase 3):

**Scenario A: Outputs were flagged**
```
======================================================================
PHASE 2.75: OUTPUT REVIEW SUMMARY
======================================================================

📋 2 output(s) flagged for review in this conversation:

  • Follow-up email to Michael
    Sentiment: issue
    📝 Change: Add personal touch in opening, use "you" throughout
    📝 Optimal: Warm professional voice, max 150 words

  • Cornell strategy doc
    Sentiment: excellent
    📝 Change: None - target quality for training

💡 Tracked in Lists/output_reviews.jsonl
```

**Scenario B: No outputs flagged but deliverables detected**
```
======================================================================
⚠️  DELIVERABLE REVIEW REMINDER
======================================================================

Found 2 potential output(s) for review:

  • Documents/partnership-proposal.md (document, 1,240 words)
  • Images/system-diagram.png (diagram)

💡 Flag for review to improve future outputs:
   n5 review add <file> --sentiment <rating> \\
     --improve '<what to change>' \\
     --optimal '<ideal state>'

Skip? (Y/n):
```

---

### 3. Deliverable Detection

Auto-detect major outputs in conversation workspace:

**Detection patterns:**
- Emails: `*email*.md`, `*follow*up*.md` (>50 words)
- Meeting notes: `*meeting*.md`, `YYYY-MM-DD*.md` (>200 words)  
- Documents: `Documents/*.md` (>100 words)
- Reports: `*{report,analysis,memo,strategy}*.md` (>500 words)
- Images: `Images/*.{png,jpg}` (created this conversation)

**Exclusions:**
- `temp_*`, `test_*`, `scratch_*`
- `BUILD_MAP*`, `SESSION_STATE*`
- System files

---

### 4. Conditional Rule

Add to `file 'N5/prefs/prefs.md'` under **CONDITIONAL RULES**:

```markdown
- CONDITION: At conversation-end -> RULE: Check if outputs were flagged for 
  review. If none and major deliverables detected, show non-blocking reminder 
  with candidates and example command including --improve and --optimal flags.
```

**Pithy version:** "On conversation-end → remind to review-flag deliverables with improvement notes"

---

## Implementation Tasks

### Task 1: Enhance Review Manager (45 min)
- Add `improvement_notes` field to schema
- Add `get_reviews_for_conversation(convo_id)` method
- Add `add_improvement_notes(output_id, what, optimal, priority)` method
- Update `Lists/schemas/output-review.schema.json`

### Task 2: Enhance Review CLI (30 min)
- Add `--improve` and `--optimal` flags to `add` command
- Add new `improve` subcommand for updating existing entries
- Update help text and examples

### Task 3: Add Deliverable Detection (30 min)
- Create `scan_for_deliverables(workspace_path)` function
- Pattern matching logic
- Word count checks
- Exclusion filters

### Task 4: Conversation-End Integration (45 min)
- Add Phase 2.75 to `N5/scripts/n5_conversation_end.py`
- Query review tracker for conversation outputs
- Call deliverable detection if needed
- Format and display summary/reminder
- Handle skip/continue logic

### Task 5: Documentation (30 min)
- Update `N5/commands/conversation-end.md` with new phase
- Update `N5/commands/review-cli.md` with new flags
- Add conditional rule to `N5/prefs/prefs.md`
- Update Output Review Tracker README

**Total: ~3 hours**

---

## Example Workflows

### Workflow 1: Flag during conversation
```bash
# While working
n5 review add Documents/email-draft.md \
  --sentiment issue \
  --improve "Too formal, missing warmth in opening" \
  --optimal "Conversational but professional, max 150 words"

# At conversation-end
# Shows: "1 output flagged for review: email-draft.md"
```

### Workflow 2: Reminded at end
```bash
# During conversation: create email, forget to flag

# At conversation-end
# Shows: "Found 1 deliverable: email-draft.md"
# User adds review before ending

n5 review add Documents/email-draft.md \
  --sentiment good \
  --improve "Could be more concise" \
  --optimal "Same warmth, cut 20%"
```

### Workflow 3: Skip reminder
```bash
# At conversation-end
# Shows: "Found 2 deliverables"
# User: Y (skip)
# Continues with conversation-end
```

---

## Open Questions for V

1. **Blocking behavior:** Should reminder block conversation-end (require response) or just show info?
   - **Recommendation:** Non-blocking, default to skip (Y)

2. **Word count thresholds:** What defines "major deliverable"?
   - Email: >50 words
   - Document: >100 words  
   - Report: >500 words
   - **Adjustable?**

3. **Auto-flagging:** Should excellent outputs auto-flag for training data?
   - **Recommendation:** No, keep it manual

4. **Improvement tracking:** Track "flagged → improved → verified" lifecycle?
   - **Recommendation:** Phase 2 enhancement, not MVP

5. **Reminder frequency:** Every conversation or only when >X deliverables?
   - **Recommendation:** Every conversation with detectable deliverables

---

## Benefits

1. **Continuous improvement loop:** Every output becomes training data
2. **Context preservation:** Capture improvement notes when context is fresh  
3. **Reduced friction:** Automatic reminder prevents forgetting
4. **Training pipeline:** Direct path from output → feedback → refinement
5. **Quality tracking:** Measure improvement over time
6. **Explicit optimal state:** Not just "wrong" but "how to make it right"

---

## Risk Mitigation

**Risk:** Reminder fatigue (shown every conversation)
- **Mitigation:** Only show if deliverables >threshold detected
- **Mitigation:** Non-blocking, easy to skip
- **Mitigation:** Can disable with flag

**Risk:** False positives in deliverable detection
- **Mitigation:** Conservative word count thresholds
- **Mitigation:** Explicit exclusion patterns
- **Mitigation:** User can skip without reviewing list

**Risk:** Too much friction at conversation-end
- **Mitigation:** Non-blocking reminder (default skip)
- **Mitigation:** Phase runs after file organization (users already in "review mode")
- **Mitigation:** Can be disabled with `--auto` flag

---

## Next Steps

1. **V Review & Approval** - Answer open questions, approve design
2. **Implementation** - 3 hours of focused work
3. **Testing** - Run through workflows 1-3
4. **Documentation** - Update all affected docs
5. **Trial Period** - Use for 2 weeks, gather feedback
6. **Iteration** - Adjust thresholds, behavior based on usage

---

## Files to Modify

- `N5/scripts/review_manager.py` - Add improvement notes
- `N5/scripts/review_cli.py` - Add --improve, --optimal flags
- `N5/scripts/n5_conversation_end.py` - Add Phase 2.75
- `N5/commands/conversation-end.md` - Document new phase
- `N5/commands/review-cli.md` - Document new flags
- `N5/prefs/prefs.md` - Add conditional rule
- `Lists/schemas/output-review.schema.json` - Update schema

---

**Status:** Ready to implement pending V approval  
**Priority:** Medium (quality infrastructure)  
**Effort:** 3 hours  

