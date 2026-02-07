---
drop_id: D2
build_slug: meta-resume-skill-v1
spawn_mode: auto
created: 2026-01-29
---

# D2: Creative Quantitative Data Strategy

## Objective

Design how to leverage Careerspan's quantitative assessment data to create compelling, differentiated visual/analytical elements in the Meta Resume.

## Context

**Business objective:** Careerspan is a recruiting company proving candidates are worth paying attention to through unique, meaningful analysis that competitors (standard recruiters, LinkedIn, self-screening) can't provide.

**The data we have:**
- 45+ skills assessed per candidate
- Each skill has: rating, required_level, required_score, importance, evidence_type, evidence_rating
- "Our Take" assessments (qualitative but structured)
- Alignment data: JD requirements → candidate mapping with verdicts
- Overall scores and match quality

**Current underutilization:**
The existing Meta Resume uses this data for prose synthesis but doesn't visualize or aggregate it in ways that create immediate "aha" moments.

## Creative Brief

Think like a data journalist or a sports analytics designer. What visual/quantitative elements would make a founder say "holy shit, no recruiter has ever given me this"?

Consider:
1. **Signature metrics** — Is there a single number or ratio that captures fit better than "89% match"?
2. **Gap distribution** — How to visualize where gaps cluster (hard skills vs soft skills vs cultural)?
3. **Evidence quality indicators** — Story+Profile vs Inferred vs Transferable — does evidence quality matter for trust?
4. **Comparison anchors** — Can we show "typical candidate in this role" baselines?
5. **Risk visualization** — Heat maps, confidence intervals, something that shows uncertainty honestly?
6. **Threshold clarity** — "This candidate clears the bar on 7/10 requirements. Here's where they don't."

## Deliverables

1. **Data inventory** — What quantitative fields exist in the decomposed data?
2. **5-7 creative concepts** — Each with:
   - Name
   - What it shows
   - Data sources required
   - Visual format (table, chart, icon system, etc.)
   - Why it's differentiated vs standard recruiting
3. **Recommended 2-3 for MVP** — Which to implement first, with rationale

## Reference Files

- Scores data: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/scores_complete.json'`
- Flat CSV: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/scores_complete.csv'`
- Alignment data: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/alignment.yaml'`
- Overview: `file 'Careerspan/meta-resumes/inbox/hardik-flowfuse/overview.yaml'`

## Quality Gates

- [ ] Every concept is grounded in actual available data
- [ ] Concepts serve employer decision-making (not just "cool")
- [ ] At least 2 concepts are implementable in markdown/Gamma (no custom charting required)
- [ ] Differentiation from standard recruiting is explicit
