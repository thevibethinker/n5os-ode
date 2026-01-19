---
created: 2026-01-19
last_edited: 2026-01-19
version: 1.0
provenance: con_ZoExvV6qS0wQiaYa
---

# Build Lesson Criteria

**Purpose:** Define what qualifies as a lesson worth logging to the Build Lesson Ledger.

The ledger exists for cross-worker communication during parallel builds. Its value depends entirely on logging the RIGHT things — not too much, not too little.

---

## What Qualifies as a Lesson

Log these to the ledger:

1. **Cross-cutting insights** — Information that applies to multiple workers, not just your scope
2. **Discovered constraints** — Things that contradict assumptions in the plan
3. **API/schema surprises** — Behavior, quirks, or data formats that differ from expectations
4. **Emergent patterns** — Conventions that emerged and should be consistent across workers
5. **V's clarifications** — Things V said that should propagate to other workers
6. **Anti-patterns discovered** — Mistakes you made that others should avoid
7. **Downstream decisions** — Choices you made that affect how other workers should proceed

---

## What Does NOT Belong

Do not log these:

- **Progress updates** → Goes in completion reports
- **Questions for V** → Ask directly in conversation
- **Scope-specific details** → Only relevant to your work
- **Blockers** → Goes in completion reports
- **Implementation minutiae** → "I used `datetime.fromisoformat()`" is not a lesson

---

## Trigger Moments

Ask yourself "should I log this?" when:

- V provides a clarification during your work
- You discover something that surprises you
- You make a decision that another worker might make differently
- You realize "I wish I'd known X earlier"
- You catch yourself about to make an assumption

---

## Examples

**Good lessons:**
- "The API returns snake_case, not camelCase. Adjust all parsers accordingly."
- "V clarified: all timestamps should be in user's timezone, not UTC."
- "The `config.enabled` field can be null, not just true/false. Check for null."
- "File paths in the schema are relative to project root, not the schema file."

**Bad lessons (don't log these):**
- "Finished implementing the parser." (progress update)
- "Should we use async here?" (question for V)
- "Used regex for validation." (implementation detail)
- "Stuck on authentication." (blocker — goes in completion report)

---

## How to Log

```bash
python3 N5/scripts/build_lesson_ledger.py append <slug> "Your lesson here" --source W#.#
```

Replace `W#.#` with your worker ID (e.g., `W1.2`), or use `V` if you're V, or `orchestrator` if you're the orchestrator.
