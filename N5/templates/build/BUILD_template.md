---
created: {{DATE}}
last_edited: {{DATE}}
version: 1.0
type: build_orchestrator
status: draft
provenance: {{CONVO_ID}}
---

# Build: {{TITLE}}

**Slug:** `{{SLUG}}`  
**Objective:** {{OBJECTIVE}}  
**Type:** {{TYPE}}  
**Created:** {{DATE}}  
**Orchestrator Thread:** This conversation

---

## Current Status

**Phase:** {{CURRENT_PHASE}}  
**Last Update:** {{LAST_UPDATE}}

{{STATUS_SUMMARY}}

---

## Wave Progress

| Wave | Drops | Status | Notes |
|------|---------|--------|-------|
| 1 | D1.1, D1.2, ... | 🟡 In Progress | {{WAVE_1_NOTES}} |
| 2 | D2.1, D2.2, ... | ⚪ Pending | Depends on Wave 1 |

**Legend:** ⚪ Pending | 🟡 In Progress | ✅ Complete | 🔴 Blocked

---

## Drop Status

| Drop | Title | Status | Thread | Notes |
|--------|-------|--------|--------|-------|
| D1.1 | {{W1.1_TITLE}} | ⚪ Pending | — | — |
| D1.2 | {{W1.2_TITLE}} | ⚪ Pending | — | — |
| D2.1 | {{W2.1_TITLE}} | ⚪ Pending | Depends: D1.1 | — |

**Status Key:**
- ⚪ **Pending** — Not started, waiting for dependencies or wave launch
- 🟡 **In Progress** — Drop thread active
- ✅ **Complete** — Drop deposit received and verified
- 🔴 **Blocked** — Cannot proceed, needs intervention
- ⏸️ **Paused** — Started but on hold

---

## Build Lesson Ledger

**Read lessons from all Drops:**
```bash
python3 N5/scripts/build_lesson_ledger.py read {{SLUG}}
```

Lessons are logged by Drops in real-time to `BUILD_LESSONS.json`. Review after each wave completion and incorporate relevant insights into subsequent Drop briefs.

**Current lesson count:** _Check via command above_

---

## Blockers & Concerns

<!-- Active issues requiring attention. Remove when resolved. -->

| Issue | Drop | Severity | Action Needed |
|-------|--------|----------|---------------|
| _None currently_ | — | — | — |

---

## Next Actions

<!-- What the orchestrator should do next. Update after each action. -->

1. [ ] Launch or prepare Wave 1 Drops
2. [ ] Monitor for deposits
3. [ ] Review and verify deposits
4. [ ] Launch Wave 2 when Wave 1 complete
5. [ ] Final integration and close

---

## References

- **PLAN.md:** `N5/builds/{{SLUG}}/PLAN.md`
- **Drop Briefs:** `N5/builds/{{SLUG}}/drops/`
- **Deposits:** `N5/builds/{{SLUG}}/deposits/`
- **Artifacts:** `N5/builds/{{SLUG}}/artifacts/`
- **meta.json:** `N5/builds/{{SLUG}}/meta.json`

---

## Closure Checklist

_Complete before marking build as done._

- [ ] All Drops complete
- [ ] All deposits reviewed
- [ ] Learnings aggregated
- [ ] meta.json status updated to "complete"
- [ ] PLAN.md checklist fully checked
- [ ] Final verification performed
