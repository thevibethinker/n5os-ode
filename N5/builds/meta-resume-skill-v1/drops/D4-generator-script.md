---
drop_id: D4
build_slug: meta-resume-skill-v1
spawn_mode: auto
created: 2026-01-30
depends_on: [D1, D2]
---

# D4: Main Generator Script

## Objective

Build `Skills/meta-resume-generator/scripts/generate.py` — the core script that transforms decomposed Careerspan data into a 3-page Meta Resume markdown document.

## Input

```
Careerspan/meta-resumes/inbox/<candidate>-<company>/
├── scores_complete.json    # All skill assessments with "Our Take"
├── alignment.yaml          # JD ↔ candidate mapping
├── overview.yaml           # Profile summary, scores
├── jd.yaml                 # Job description
├── experience.yaml         # Work history
├── hard_skills.yaml        # Technical competencies
├── soft_skills.yaml        # Working style
└── careerspan_cleaned.md   # Full cleaned doc
```

## Output

```
Careerspan/meta-resumes/processed/<candidate>-<company>/
├── meta-resume.md          # The 3-page document
└── meta-resume-data.json   # Computed metrics (QFS, matrices, etc.)
```

## Structure to Generate

Follow `file 'N5/builds/meta-resume-skill-v1/artifacts/META-RESUME-STRUCTURE-v2.md'` exactly:

### Page 1: The Decision
1. **Header** — Candidate name, role, company, confidence emoji + QFS score
2. **Bottom Line** — 2-3 sentences, clear recommendation
3. **What's Clear / What's Not Clear** — Two-column binary signals
4. **Decision Matrix** — "If you need X, this candidate is Y" table

### Page 2: The Depth
5. **What You're Getting** — Evidence-backed assets table
6. **What You're NOT Getting** — Gaps with severity + implications
7. **How They Think** — Problem-solving patterns from stories
8. **Candidate's Context** — Space for candidate rebuttal (placeholder text)

### Page 3: [Candidate] By The Numbers
9. **Quality-Weighted Fit Score** — Large display + formula breakdown
10. **Evidence Trust Matrix** — Category × Evidence type grid
11. **Critical Risks** — Top 3-5 flagged with interview questions
12. **GitHub Snapshot** — Placeholder for D5 output, or "Not provided" warning
13. **Links** — LinkedIn, GitHub URLs

## Key Computations

### QFS (Quality-Weighted Fit Score)
```python
# From D2 spec:
# rating: Excellent=1.0, Good=0.75, Fair=0.5
# evidence_weight: Direct=1.0, Transferable=0.8, Profile=0.7
# QFS = Σ(rating × importance × evidence_weight) / Σ(importance)
```

### Evidence Trust Matrix
```python
# Group by category (Responsibility, Hard Skill, Soft Skill)
# Cross with evidence_type (Story+profile, Profile, Transferable)
# Count per cell
```

### Critical Risks
```python
# From alignment.yaml critical_gaps
# Cross-reference with importance from scores_complete.json
# Sort by severity × importance
# Include interview probe from interview_priorities
```

## CLI Interface

```bash
python3 Skills/meta-resume-generator/scripts/generate.py \
  --input Careerspan/meta-resumes/inbox/hardik-flowfuse/ \
  --output Careerspan/meta-resumes/processed/hardik-flowfuse/ \
  [--github-data path/to/github.json]  # Optional, from D5
  [--linkedin-url "https://..."]       # Optional override
```

## Reference Files

- Structure spec: `file 'N5/builds/meta-resume-skill-v1/artifacts/META-RESUME-STRUCTURE-v2.md'`
- Quantitative strategy: `file 'N5/builds/meta-resume-skill-v1/deposits/D2-quantitative-data-strategy-output.md'`
- Test data: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/'`
- Example output style: `file 'N5/builds/careerspan-profile-output-v1/output/hardik-profile-v5.md'`

## Quality Gates

- [ ] All 13 sections generated
- [ ] QFS calculated correctly with formula shown
- [ ] Evidence Trust Matrix populated from actual data
- [ ] Critical Risks include interview questions
- [ ] "Not provided" warnings for missing GitHub/LinkedIn
- [ ] Output is valid markdown that renders cleanly
- [ ] No hallucinated data — only use what's in input files

## Anti-Patterns

- Do NOT use LLM calls for generation — this is pure data transformation
- Do NOT hardcode Hardik-specific content — must work for any candidate
- Do NOT include promotional language — objective tone only
