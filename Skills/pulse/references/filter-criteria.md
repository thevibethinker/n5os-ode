---
created: 2026-01-24
last_edited: 2026-02-21
version: 3.0
provenance: con_mG5yzbSSJUnMnZcK
---

# Filter Criteria

The Filter is an LLM-based judge that validates Deposits against their briefs.

## Judgment Process

Filter receives:
1. The original Drop brief (including Scenarios section)
2. The Deposit JSON
3. File contents of artifacts (if accessible)
4. Holdout scenarios (if any exist in `holdout_scenarios/` directory)

Filter outputs:
```json
{
  "drop_id": "D1.1",
  "satisfaction": 0.85,
  "verdict": "PASS",
  "scenario_results": [
    {"id": "S1", "score": 1.0, "method": "command", "detail": "curl returned 200 with expected shape"},
    {"id": "S2", "score": 0.7, "method": "llm_judge", "detail": "Error message exists but lacks remediation steps"},
    {"id": "S3", "score": 1.0, "method": "command", "detail": "File exists with 150 rows"}
  ],
  "holdout_results": [
    {"id": "H1", "score": 0.5, "method": "llm_judge", "detail": "Partial handling of edge case"}
  ],
  "structural_results": [
    {"criterion": "Schema has 5 tables", "met": true},
    {"criterion": "Soft-delete pattern used", "met": true}
  ],
  "advisory_concerns": [
    {"area": "skills_utilization", "detail": "Built functionality that exists in existing skill X"}
  ],
  "retry_guidance": null,
  "timestamp": "ISO timestamp"
}
```

## Verdict Definitions

Verdicts are determined by the `satisfaction` score — the weighted average of all scenario scores.

| Satisfaction | Verdict | Action |
|-------------|---------|--------|
| >= 0.9 | **PASS** | Mark complete, auto-advance |
| 0.7 - 0.89 | **WARN** | Mark complete, log concerns, advance with noted gaps |
| < 0.7 | **FAIL** | Auto-retry with scenario-specific feedback injected into brief |

Thresholds are configurable in `pulse_control.json` under `filter_thresholds`.

**Scoring:**
- Each scenario scored 0.0 - 1.0
- Public scenarios (from brief) weighted at 1.0
- Holdout scenarios (from holdout_scenarios/) weighted at configurable value (default 0.5)
- Satisfaction = weighted average of all scenario scores
- If no Scenarios section exists in brief, fall back to structural-only evaluation (legacy mode)

## Evaluation Rubric

### 0. Scenario Evaluation (PRIMARY — when Scenarios exist in brief)

**Parse scenarios from the `## Scenarios` section of the brief.**

For each scenario:

1. **If Verify clause is an executable command** (`curl`, `duckdb`, `test`, `python3`, `grep`, etc.):
   - Run the command against the artifacts/environment
   - Score 1.0 if command succeeds and output matches Then clause
   - Score 0.0-0.9 based on partial match
   - Record method as `"command"` with command output as detail

2. **If Verify clause starts with `LLM:`**:
   - Use LLM judgment to evaluate the Then clause against artifacts
   - Read relevant artifact files
   - Score based on how well the implementation satisfies the scenario
   - Record method as `"llm_judge"` with reasoning as detail

3. **If Verify clause is ambiguous or missing**:
   - Use best-effort LLM judgment
   - Record method as `"llm_inferred"` with note about missing verification

**Retry on FAIL:** When satisfaction < 0.7, generate retry_guidance that:
- Lists each failed scenario by ID with its score and what went wrong
- Provides specific instructions for fixing each failure
- Does NOT repeat the entire brief — only the delta needed

### 1. Artifact Existence (Required)
- Do all specified output files exist?
- Are they non-empty?

### 2. Success Criteria / Structural Checks (Required)
- Each checkbox in the brief must be verifiable
- Check file contents when possible
- If a criterion cannot be verified, note it

### 3. Coherence (Advisory)
- Does the work make sense given the context?
- Any obvious errors or anti-patterns?

### 4. Scope Creep (Advisory)
- Did the Drop create unexpected files?
- Did it modify files outside its scope?

### 5. Skills Utilization (Advisory)
Evaluate whether the Drop used skills appropriately:

**Check for existing skills:**
- Did the Drop check for existing skills before building?
- If a relevant skill existed, did the Drop use it?
- If the Drop built functionality that exists in a skill, this is a WARN

**Check for skill creation:**
- Did the Drop create reusable functionality?
- If yes, was it packaged as a skill (under `Skills/`) or a one-off script?
- Reusable functionality as one-off script → WARN with note "Consider extracting to skill"

### 6. Technique Selection (Advisory)
Evaluate whether the Drop used the right tool for the job:

| Task Type | Should Use |
|-----------|------------|
| Extract meaning from unstructured text | LLM |
| Classify or categorize content | LLM |
| Parse natural language | LLM |
| Structured data (JSON, CSV) parsing | Code |
| Math/calculations | Code |
| File operations | Code |
| Pattern matching on structured data | Regex |
| Pattern matching on natural language | LLM |

### 7. Learning Annotations (Advisory)
Evaluate whether the Drop captured learning-relevant metadata:
- Did the deposit include `concepts_exercised`?
- If the Drop involved a Decision Point, was V's decision recorded?

## Filter Prompt Template

```
You are the Filter, a quality judge for automated builds.

BRIEF:
{brief_content}

DEPOSIT:
{deposit_json}

ARTIFACTS (if available):
{artifact_contents}

HOLDOUT SCENARIOS (if any):
{holdout_scenarios}

## Primary Evaluation: Scenarios

Parse the ## Scenarios section from the brief. For each scenario (S1, S2, ...):

1. Read the Given/When/Then/Verify clauses
2. If Verify is an executable command: evaluate whether the implementation would satisfy it
3. If Verify starts with "LLM:": use your judgment to evaluate the Then clause against artifacts
4. Score each scenario 0.0-1.0 based on how well the deposit satisfies it

Then parse any holdout scenarios (H1, H2, ...) and evaluate the same way.

Compute satisfaction = weighted average of all scenario scores.
(Public scenarios weight 1.0, holdout scenarios weight per their `weight` field, default 0.5)

## Secondary Evaluation: Structural

1. **Artifact Existence**: Do all required files exist and have content?
2. **Success Criteria**: Are all checkboxes from the brief satisfied?

## Advisory Evaluation

3. **Coherence**: Does the work make sense? Any obvious errors?
4. **Scope Creep**: Did the Drop stay within its scope?
5. **Skills Utilization**: Did the Drop use existing skills where available?
6. **Technique Selection**: Did the Drop use LLM for semantic tasks and code for structural tasks?
7. **Learning Annotations**: If pedagogical, did it capture concept tracking?

Return JSON:
{
  "drop_id": "...",
  "satisfaction": 0.0-1.0,
  "verdict": "PASS" | "FAIL" | "WARN",
  "scenario_results": [
    {"id": "S1", "score": 0.0-1.0, "method": "command|llm_judge|llm_inferred", "detail": "..."}
  ],
  "holdout_results": [
    {"id": "H1", "score": 0.0-1.0, "method": "...", "detail": "..."}
  ],
  "structural_results": [
    {"criterion": "...", "met": true/false}
  ],
  "advisory_concerns": [
    {"area": "skills_utilization|technique_selection|learning_annotations|scope|coherence", "detail": "..."}
  ],
  "retry_guidance": null or "Specific instructions for fixing failed scenarios"
}

Scoring rules:
- satisfaction >= 0.9 → verdict "PASS"
- 0.7 <= satisfaction < 0.9 → verdict "WARN"
- satisfaction < 0.7 → verdict "FAIL" (must include retry_guidance)
- If no Scenarios section exists: fall back to structural evaluation only, use confidence-based verdict (legacy mode)
```

## Escalation on FAIL

When Filter returns FAIL:
1. SMS sent immediately with drop_id, satisfaction score, and failed scenarios
2. Build continues (other Drops not blocked unless dependent)
3. Auto-retry with scenario-specific feedback injected into brief
4. After 2 failed retries: escalate to V for human review

## Escalation on WARN

When Filter returns WARN:
1. Log advisory_concerns to BUILD_LESSONS.json for future reference
2. Continue build (advisory concerns are not blocking)
3. Include in build AAR for pattern analysis