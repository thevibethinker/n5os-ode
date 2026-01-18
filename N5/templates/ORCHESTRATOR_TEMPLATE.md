---
created: YYYY-MM-DD
last_edited: YYYY-MM-DD
version: 1
provenance: {ORCHESTRATOR_CONVO_ID}
---
# {PROJECT_NAME} — Build Orchestrator

## Current Status: Phase 1 In Progress

{Brief status summary}

## Worker Overview

| Worker | Title | Status | Notes |
|--------|-------|--------|-------|
| 1 | {Worker 1 Name} | ⏳ Pending | |
| 2 | {Worker 2 Name} | ⏳ Pending | |
| 3 | {Worker 3 Name} | ⏳ Pending | |

## Spawn Instructions

### Worker 1: {Worker 1 Name}

Copy and paste this into a **new conversation**:

```
Execute Worker 1 ({Worker 1 Name}):

BUILD_CONTEXT:
  build: {build-slug}
  worker: 1
  parent_topic: {Project Name}

CONTEXT:
- {Key context item 1}
- {Key context item 2}

INSTRUCTIONS:
- Read: `file 'N5/builds/{build-slug}/DESIGN.md'`
- Read: `file 'N5/builds/{build-slug}/workers/WORKER-1-{slug}.md'`

DELIVERABLES:
1. {Deliverable 1}
2. {Deliverable 2}
3. Update STATUS.md when done
```

### Worker 2: {Worker 2 Name}

Copy and paste this into a **new conversation**:

```
Execute Worker 2 ({Worker 2 Name}):

BUILD_CONTEXT:
  build: {build-slug}
  worker: 2
  parent_topic: {Project Name}

CONTEXT:
- {Key context item 1}
- {Key context item 2}

INSTRUCTIONS:
- Read: `file 'N5/builds/{build-slug}/DESIGN.md'`
- Read: `file 'N5/builds/{build-slug}/workers/WORKER-2-{slug}.md'`

DELIVERABLES:
1. {Deliverable 1}
2. {Deliverable 2}
3. Update STATUS.md when done
```

---

## Activity Log

| Timestamp (ET) | Event |
|----------------|-------|
| YYYY-MM-DD HH:MM | Build initialized |

## Integration Test

After all workers complete:

```
Run integration test for {Project Name}:

1. Test {flow 1}:
   - {Step 1}
   - {Step 2}
   - Verify: {Expected result}

2. Test {flow 2}:
   - {Step 1}
   - {Step 2}
   - Verify: {Expected result}

Report results in STATUS.md
```

---

## Notes

- {Important note 1}
- {Important note 2}
