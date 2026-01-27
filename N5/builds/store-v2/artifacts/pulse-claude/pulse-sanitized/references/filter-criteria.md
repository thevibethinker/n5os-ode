---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_T0QGg2ryaDjCTxVj
---

# Filter Criteria

The Filter is an LLM-based judge that validates Deposits against their briefs.

## Judgment Process

Filter receives:
1. The original Drop brief
2. The Deposit JSON
3. File contents of artifacts (if accessible)

Filter outputs:
```json
{
  "drop_id": "D1.1",
  "verdict": "PASS" | "FAIL" | "WARN",
  "confidence": 0.0-1.0,
  "reasoning": "Explanation of judgment",
  "criteria_results": [
    {"criterion": "Schema has 5 tables", "met": true},
    {"criterion": "Soft-delete pattern used", "met": true}
  ],
  "concerns": [],
  "timestamp": "ISO timestamp"
}
```

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | All success criteria met, no red flags | Mark complete, advance |
| **WARN** | Criteria met but concerns exist | Mark complete, log concerns, notify |
| **FAIL** | Criteria not met or artifacts missing | Mark failed, escalate via SMS |

## Evaluation Rubric

### 1. Artifact Existence (Required)
- Do all specified output files exist?
- Are they non-empty?

### 2. Success Criteria (Required)
- Each checkbox in the brief must be verifiable
- Check file contents when possible
- If a criterion cannot be verified, note it

### 3. Coherence (Advisory)
- Does the work make sense given the context?
- Any obvious errors or anti-patterns?

### 4. Scope Creep (Advisory)
- Did the Drop create unexpected files?
- Did it modify files outside its scope?

## Filter Prompt Template

```
You are the Filter, a quality judge for automated builds.

BRIEF:
{brief_content}

DEPOSIT:
{deposit_json}

ARTIFACTS (if available):
{artifact_contents}

Evaluate this Deposit against the brief's success criteria.

Return JSON:
{
  "drop_id": "...",
  "verdict": "PASS" | "FAIL" | "WARN",
  "confidence": 0.0-1.0,
  "reasoning": "...",
  "criteria_results": [...],
  "concerns": [...]
}

Be strict. If criteria cannot be verified, verdict is WARN not PASS.
```

## Escalation on FAIL

When Filter returns FAIL:
1. SMS sent immediately with drop_id and reasoning
2. Build continues (other Drops not blocked unless dependent)
3. Human review required before retry
