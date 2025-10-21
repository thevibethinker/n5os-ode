# Proposed Conditional Rule: Output Review Reminder

## Rule Draft

**CONDITION:** At conversation-end, when major deliverables detected OR when user explicitly closes thread

**RULE:** Check if significant outputs were flagged for review. If not, remind user with list of candidates and one-line instructions to flag with improvement context.

---

## Pithier Version

**CONDITION:** When closing conversation → **RULE:** Remind to flag major deliverables for review with "what to improve" notes if none were tracked

---

## Ultra-Pithy Version

**CONDITION:** On conversation-end → **RULE:** Prompt to review-flag deliverables with improvement notes

---

## Full Rule Text (for prefs.md)

```markdown
- CONDITION: At conversation-end (explicit or detected) -> RULE: ```markdown
Check if outputs were added to review tracker during conversation. If none 
and major deliverables detected (emails, docs, images, reports >500 words), 
show reminder with list of candidates:

"⚠️ Consider flagging these for review to refine future outputs:
   n5 review add <file> --sentiment <rating> --improve '<what to change>'"

Include: what needs to change, optimal state. Non-blocking reminder.
```
```

---

## Alternative Phrasings

### Option 1: Focus on continuous improvement
**CONDITION:** When ending conversation with deliverables → **RULE:** Remind to capture "what would make this optimal" for any significant outputs

### Option 2: Focus on training pipeline
**CONDITION:** On conversation-end → **RULE:** Check for unflagged deliverables; prompt to add with improvement notes for training refinement

### Option 3: Most concise
**CONDITION:** conversation-end → **RULE:** Prompt review-flag deliverables with improvement context

---

## Recommended Integration Point

Add to `N5/prefs/prefs.md` under **Critical Always-Load Rules** → **Safety & Review** section:

```markdown
### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`; sticky safety may enforce it
- Require explicit approval for side-effect actions
- Always search for existing protocols before creating new ones
- **Whenever a new file is created, always ask where the file should be located**
- **At conversation-end, remind to flag major deliverables for review with improvement notes**
```

Or under **CONDITIONAL RULES** (more specific):

```markdown
- CONDITION: At conversation-end (user says "end", "close", "wrap up") -> RULE: ```markdown
Before executing conversation-end workflow, check if outputs were added 
to review tracker. If none and major deliverables detected, show reminder:

"⚠️ Consider flagging outputs for review to improve future generations:
   n5 review add <file> --sentiment <rating> \\
     --improve '<specific changes needed>' \\
     --optimal '<ideal state description>'"

List candidates: emails, docs >500 words, images, meeting notes, reports.
Non-blocking reminder - user can skip.
```
```

---

## Behavior Specification

1. **Detection Phase** (runs during conversation-end Phase 2.75):
   - Query: Were any outputs added to review tracker this conversation?
   - If YES → Show summary of tracked outputs
   - If NO → Scan for deliverables

2. **Deliverable Scanning:**
   - Emails: `*email*.md`, `*follow*up*.md` (>50 words)
   - Meeting notes: `*meeting*.md`, `YYYY-MM-DD*.md` (>200 words)
   - Documents: `Documents/*.md` (>100 words)
   - Reports: `*{report,analysis,memo,strategy}*.md` (>500 words)
   - Images: `Images/*.{png,jpg}` (generated this conversation)
   - Exclude: `temp_*`, `test_*`, `scratch_*`, `BUILD_MAP*`, `SESSION_STATE*`

3. **Reminder Display:**
   ```
   ⚠️ DELIVERABLE REVIEW REMINDER
   
   Found 2 potential output(s) for review:
     • Documents/partnership-proposal.md (document, 1,240 words)
     • Images/system-architecture.png (diagram)
   
   💡 Flag for review to refine future outputs:
      n5 review add <file> --sentiment <excellent|good|issue|bad> \\
        --improve '<what to change>' \\
        --optimal '<ideal state>'
   
   Example:
      n5 review add Documents/partnership-proposal.md \\
        --sentiment issue \\
        --improve "Too formal in tone, missing specific pricing" \\
        --optimal "Conversational voice, concrete numbers, max 2 pages"
   
   Skip? (Y/n):
   ```

4. **User Options:**
   - Skip (Y): Continue conversation-end
   - Flag now (n): Pause conversation-end, wait for user to add reviews
   - Auto mode: Always skip

---

## Implementation Notes

- **Non-blocking:** Should not prevent conversation-end
- **Informational:** Nudge, not requirement
- **Context-aware:** Only show if deliverables detected
- **Actionable:** Show exact command with example
- **Skippable:** Default to continue (Y)

---

## Success Metrics

Track over 30 days:
- % of conversations with deliverables
- % where deliverables were flagged
- % where reminder led to flagging
- Quality improvement in flagged outputs over time

---

**Recommendation:** Go with Option 3 (most concise) in CONDITIONAL RULES section.

