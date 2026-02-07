---
created: 2026-02-04
last_edited: 2026-02-04
version: 1
provenance: con_1kVhshgDe0iYErkj
status: active
---
# Candidate Output Realignment Plan

## Context

The `meta-resume-generator` skill was a bastardization of three different output experiments:
1. **Anti-Resume** — Markdown-based "negative space" analysis
2. **Meta Resume** — 2-page branded PDF with signal strength bars
3. **Resume:Decoded** (Candidate:Decoded) — Branded PDF with spikes visualization

After advisor feedback (TBD), we're starting fresh with a new approach.

---

## Learnings from Previous Attempts

### What Worked

| Element | Source | Why It Worked |
|---------|--------|---------------|
| **"Should you take this meeting?" framing** | Anti-Resume | Answers the employer's actual question directly |
| **Negative space emphasis** | Anti-Resume | Differentiates from resume (which only shows positives) |
| **Clear yes/no + reasoning** | Anti-Resume | Forces a decision, not a "maybe" |
| **Trade-off framing** | Anti-Resume | "If you need X, this is your candidate / not your candidate" |
| **Signal strength bars** | Meta Resume | Visual representation of evidence quality (story-verified vs resume-only vs inferred) |
| **Spikes visualization** | Candidate:Decoded | At-a-glance strengths (▲) and gaps (▼) with verification markers |
| **Behavioral signals with quotes** | Candidate:Decoded | "What the resume can't tell you" — direct quotes from interviews |
| **Interview questions that matter** | All three | Actionable — tells employer exactly what to probe |
| **2-page constraint** | Meta Resume / Decoded | Forces ruthless prioritization |

### What Didn't Work

| Element | Problem |
|---------|---------|
| **Multiple input formats** | Decomposer dir vs synthesized JSON vs legacy JSON — too many code paths |
| **Adapter complexity** | 400+ lines mapping decomposer output to template — brittle and hard to debug |
| **LLM synthesis layer** | `synthesize.ts` added latency and inconsistency without clear value |
| **Template proliferation** | `template.html` + `template-decoded.html` — unclear which to use |
| **Spikes not integrated** | `extractSpikes()` existed but wasn't called by `mapToCandidateDecoded()` |
| **Inconsistent terminology** | "Meta Resume" vs "Candidate:Decoded" vs "Anti-Resume" in same codebase |

### Anti-Resume Framework (Preserved)

The Anti-Resume framework (`ANTI-RESUME-FRAMEWORK.md`) contains valuable structure:

1. **Should You Take This Meeting?** — 80/20 panel, clear yes/no
2. **What You're Buying** — Resume signal synthesized (Asset | Evidence | Relevance)
3. **What You're NOT Buying** — Gaps with severity (High/Medium-High/Medium/Low)
4. **Risk Profile** — Ramp Time, Likely Failure Mode, Management Overhead, Flight Risk
5. **What The Meeting Will Reveal** — Unknown unknowns → interview agenda
6. **Decision Framework** — "If you need X, candidate is Y" trade-offs
7. **Bottom Line** — Restate recommendation with reasoning

**Design principles worth keeping:**
- Negative space over positive space
- Specificity over generality
- Trade-offs over verdicts
- Efficiency over completeness
- Honesty over advocacy

---

## Current Pipeline State

```
[Raw Careerspan Doc] 
    ↓ OCR/extraction
[careerspan-decomposer]
    ↓ outputs to Careerspan/meta-resumes/inbox/<candidate>-<company>/
    │   ├── scores_complete.json  ← Main assessment data
    │   ├── overview.yaml
    │   ├── jd.yaml
    │   ├── profile.yaml
    │   └── ... other YAML files
    ↓
[??? NEW SKILL ???]
    ↓
[Branded PDF output]
```

The decomposer output schema is well-defined (`scores_complete.json` canonical schema v2.0):
- `overall_score`, `bottom_line`, `qualification`, `career_trajectory`
- `category_scores` (background, uniqueness, responsibilities, hard_skills, soft_skills)
- `signal_strength` (story_verified_pct, resume_only_pct, inferred_pct)
- `potential_dealbreakers` array
- `skills[]` with `skill_name`, `category`, `rating`, `importance`, `our_take`, `evidence_type`, `support[]`

---

## Open Questions (Awaiting Advisor Input)

**V to provide meeting notes addressing:**

1. **Who is the audience?**
   - Hiring manager? CEO? HR? Recruiter?
   - What's their time budget? (30 sec skim? 2 min read? 10 min deep dive?)

2. **What's the primary use case?**
   - Pre-meeting prep?
   - Go/no-go decision?
   - Interview guide?
   - All three?

3. **What format resonates?**
   - PDF (printable, shareable)?
   - Web page (interactive)?
   - Notion page (collaborative)?
   - Email summary + PDF attachment?

4. **What's the core value proposition?**
   - Speed (fast no)?
   - Depth (rich context)?
   - Differentiation (negative space)?
   - Actionability (interview questions)?

5. **What elements are must-haves vs nice-to-haves?**
   - Signal strength visualization?
   - Spikes at-a-glance?
   - Trade-off framework?
   - Direct quotes from interviews?

---

## Candidate Skills to Leverage

### `branded-pdf` Skill

Located at `Skills/branded-pdf/`. Generates clean, professional PDFs with:
- Dual-logo headers
- Customizable styling
- Well-spaced typography
- Markdown → PDF pipeline

**Potential integration:** Use `branded-pdf` for rendering, with a new skill handling the content transformation from decomposer output.

---

## Next Steps

1. [ ] V provides advisor meeting notes
2. [ ] Clarify audience and use case
3. [ ] Define minimal viable output format
4. [ ] Design new skill with clean interface to decomposer
5. [ ] Build and test with real candidates

---

## Archived Assets

The following were preserved before deletion:

- **Anti-Resume Framework**: `Skills/careerspan-decomposer/references/ANTI-RESUME-FRAMEWORK.md` (moved)
- **Sample outputs**: Hardik PDFs (not preserved — can regenerate)
- **Template HTML**: Lost (recreatable from spec)
- **Adapter logic**: Lost (was overly complex anyway)

---

*This document will be updated once advisor input is received.*
