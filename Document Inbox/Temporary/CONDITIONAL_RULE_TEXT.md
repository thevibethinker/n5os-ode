# Conditional Rule for Output Review Reminder

## Final Recommended Text

Add this to `file 'N5/prefs/prefs.md'` under **CONDITIONAL RULES** section:

---

```markdown
- CONDITION: At conversation-end (user says "end conversation", "close thread", "wrap up") -> RULE: Check if outputs were added to review tracker during this conversation. If none flagged and major deliverables detected (emails, documents >500 words, images, meeting notes, reports), show non-blocking reminder listing candidates with instruction to flag using `n5 review add <file> --sentiment <rating> --improve '<what to change>' --optimal '<ideal state>'`. User can skip (default Y) or flag before continuing.
```

---

## Alternative Versions

### Ultra-Concise Version
```markdown
- CONDITION: At conversation-end -> RULE: Remind to review-flag deliverables with improvement notes if none tracked during conversation
```

### Medium Version  
```markdown
- CONDITION: At conversation-end -> RULE: If no outputs flagged for review and major deliverables exist, show reminder to add with --improve and --optimal flags describing what to change and ideal state. Non-blocking, user can skip.
```

### Detailed Version (Original Proposal)
```markdown
- CONDITION: At conversation-end (explicit or detected) -> RULE: ```markdown
Check if outputs were added to review tracker during conversation. If none 
and major deliverables detected (emails, docs >500 words, images, reports), 
show non-blocking reminder with list of candidates:

"⚠️ Consider flagging for review to improve future outputs:
   n5 review add <file> --sentiment <rating> \\
     --improve '<specific changes needed>' \\
     --optimal '<ideal state description>'"

Major deliverables: emails (>50 words), documents (>100 words), reports (>500 words),
meeting notes, images. Exclude temp_*, test_*, system files. Default skip (Y).
```
```

---

## Placement in prefs.md

**Option 1: In CONDITIONAL RULES (Recommended)**

Place after the "Before executing system operations" rule:

```markdown
CONDITIONAL RULES:
...
- CONDITION: Before executing system operations -> RULE: Check if registered command exists...

- CONDITION: At conversation-end -> RULE: Check if outputs were added to review tracker during this conversation. If none flagged and major deliverables detected, show non-blocking reminder to flag using `n5 review add` with --improve and --optimal flags. User can skip (default Y).

- CONDITION: When I request building, refactoring, or modifying significant system components -> RULE: Load architectural principles first...
```

**Option 2: In ALWAYS APPLIED RULES → Safety & Review**

```markdown
ALWAYS APPLIED RULES:
...

### Safety & Review
- Never schedule anything without explicit consent
- Always support `--dry-run`
- Require explicit approval for side-effect actions
- Always search for existing protocols before creating new ones
- **Whenever a new file is created, always ask where the file should be located**
- **At conversation-end, remind to flag major deliverables for review with improvement context if none were tracked**
```

---

## Recommendation

Use **Final Recommended Text** in **CONDITIONAL RULES** section (Option 1).

**Rationale:**
- Conditional rules are checked based on context (conversation-end)
- Fits naturally after system operations rule
- Clear trigger condition
- Detailed enough to be actionable
- Not so detailed it becomes noise

---

## Implementation Note

When adding this rule, also add a corresponding entry to conversation-end.md documenting Phase 2.75 behavior. The rule tells AI *when* to remind, the phase documentation tells *how* to implement it.

