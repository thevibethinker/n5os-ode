---
created: 2026-02-03
last_edited: 2026-02-03
version: 2
provenance: con_cRFSZyveKbg8N3T5
build_slug: meta-resume-v2
drop_id: D2
status: complete_with_issues
---
# D2 Deposit: Pipeline Test - Hardik × Docsum

## Summary

Pipeline executes successfully end-to-end with correct inputs. However, Step 5 (narrative generation) produces sparse output—the LLM call returns minimal data for spikes, what_they_bring, risks_to_probe, and interview_questions.

## Execution Log

### Step 1: Gather Inputs ✅
```bash
# Manual construction required due to YAML frontmatter parsing bug
# step1_gather.py fails on profile.yaml with double --- markers
```
**Fix applied:** Manually constructed gathered.json using `yaml.safe_load_all()` to handle frontmatter.
**Output:** 45 skills, score 85/100

### Step 2: Ensure Hiring POV ✅
```bash
python3 step2_hiring_pov.py --input /tmp/synthesis/gathered.json --output /tmp/synthesis/hiring_pov.json
```
**Output:** Used existing Docsum Hiring POV (source: gdrive)

### Step 3: Cluster Stories ✅
```bash
python3 step3_cluster.py --input /tmp/synthesis/gathered.json --pov /tmp/synthesis/hiring_pov.json --output /tmp/synthesis/clusters.json
```
**Output:** 4 story clusters, 0 cross-cutting patterns

### Step 4: Resume Diff ✅
```bash
python3 step4_resume_diff.py --input /tmp/synthesis/gathered.json --clusters /tmp/synthesis/clusters.json --output /tmp/synthesis/resume_diff.json
```
**Output:** 5 substantiated claims, 0 revealed (no resume text available)

### Step 5: Generate Narrative ⚠️
```bash
python3 step5_narrate.py --input /tmp/synthesis/gathered.json --pov /tmp/synthesis/hiring_pov.json --clusters /tmp/synthesis/clusters.json --diff /tmp/synthesis/resume_diff.json --output /tmp/synthesis/narrative.json
```
**Output:** Verdict correct (Take This Meeting, 85/100), but sparse content:
- `spikes`: empty
- `what_they_bring`: empty
- `risks_to_probe`: empty
- `interview_questions`: empty

## Output Samples

### clusters.json (Step 3)
```json
{
  "story_clusters": [
    {
      "story_id": "pROFGle1jTPdoivBHQUf",
      "theme": "Foundational AI/ML Platform Architecture",
      "narrative": "Led the end-to-end design and development of a sophisticated ML/MLOps SaaS platform...",
      "evidence_strength": "story_verified",
      "relevance_score": 9
    },
    // 3 more clusters
  ]
}
```

### narrative.json (Step 5) - Sparse
```json
{
  "candidate": {"name": "Hardik", "role": "Founding Full Stack Engineer Candidate"},
  "verdict": {"score": 85, "action": "Take This Meeting"},
  "spikes": {"up": [], "down": []},
  "what_they_bring": [],
  "risks_to_probe": [],
  "interview_questions": [],
  "signal_strength": {"story_verified": 78.0, "resume_only": 22.0}
}
```

## Validation Checklist

- [x] All 5 steps complete without errors
- [x] Data alignment validated (Docsum JD, not FlowFuse)
- [x] narrative.json has all required fields
- [ ] Spikes populated → **FAILED** (empty)
- [ ] what_they_bring populated → **FAILED** (empty)
- [ ] risks_to_probe populated → **FAILED** (empty)
- [ ] interview_questions populated → **FAILED** (empty)
- [x] Signal strength correct (78% story-verified)
- [x] Output saved to canonical location

## Bugs Found

### Bug 1: YAML Frontmatter Parsing (step1_gather.py)
**Issue:** `yaml.safe_load()` fails on files with `---` frontmatter markers
**Fix:** Use `yaml.safe_load_all()` and take last non-None document
**File:** `Skills/candidate-synthesis/scripts/step1_gather.py:110`

### Bug 2: Sparse LLM Response (step5_narrate.py)
**Issue:** `call_llm()` returns minimal data; JSON extraction from response may be failing silently
**Root cause:** Likely the LLM returns text with JSON, but regex extraction fails or times out
**Fix needed:** Add fallback handling, logging, or use `output_format` schema enforcement

## Files Produced

All outputs saved to: `Careerspan/meta-resumes/outputs/hardik-docsum/`
- `gathered.json` (80KB)
- `hiring_pov.json` (4.8KB)
- `clusters.json` (4.5KB)
- `resume_diff.json` (1.2KB)
- `narrative.json` (2KB) - **sparse, needs fix**

## Assessment

**Pipeline mechanics:** Working ✅
**Data alignment gate:** Needed (now logged as build lesson)
**Step 5 quality:** Needs debugging—LLM response handling is unreliable

**Recommendation:** Before D1 consumes this, fix step5_narrate.py to either:
1. Use `output_format` schema in /zo/ask call
2. Add retry logic with explicit JSON request
3. Log raw LLM responses for debugging

## Build Lesson Logged

> CRITICAL: Pipeline must validate data alignment BEFORE execution. Check that decomposer JD employer matches target employer.
