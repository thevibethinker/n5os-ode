---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
provenance: con_iVOsyLNgj9jOnqmy
---

# D2: Creative Quantitative Data Strategy

## Data Inventory

### Available Fields from `scores_complete.json`

For each of the **45+ skills assessed**, we have:

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `category` | string | "Responsibility", "Hard Skill", "Soft Skill" | 3 top-level categories |
| `skill` | string | "Deliver end-to-end solutions", "Embeddings" | Specific skill name |
| `rating` | string | "Excellent", "Good", "Fair" | 3-tier qualitative rating |
| `required_level` | string | "Advanced", "Intermediate" | JD requirement level |
| `required_score` | string | "4/5", "3/5" | Numeric threshold |
| `max_score` | string | "5" | Scale ceiling |
| `importance` | string | "10/10", "7/10", "5/10" | Business criticality weighting |
| `evidence_type` | string | "Story+profile", "Profile", "Transferable" | Evidence strength tier |
| `story_id` | string | "COKUmaqSITrBKdtxSgJp" | Links to narrative evidence |
| `evidence_rating` | string | "Direct", "Transferable" | Evidence relevance quality |
| `our_take` | string | [detailed analysis] | LLM synthesis, structured but qualitative |

### From `alignment.yaml`

- **requirements_alignment**: Array of 15 JD requirements with:
  - `verdict`: CLEAR, PARTIAL, GAP
  - `evidence`: Textual justification
  - `confidence`: high, medium, low

- **critical_gaps**: List of 4 documented gaps

- **interview_priorities**: 7 probing questions for high-value areas

### From `overview.yaml`

- `careerspan_score.overall`: 89/100 (well-aligned)
- `resume_match.score`: 9/10 (excellent)
- `status`: "Advance to finals"
- `qualification`: "Well-aligned"
- `career_trajectory`: "Lateral Move"

---

## 7 Creative Concepts

### 1. Quality-Weighted Fit Score (QFS)

**What it shows:** A single, weighted fit metric that accounts for both skill rating AND business importance, plus evidence quality.

**Data sources:**
- `rating` (map: Excellent=1.0, Good=0.75, Fair=0.5)
- `importance` (numeric: 1-10)
- `evidence_rating` (weight: Direct=1.0, Transferable=0.8, Profile=0.7)

**Calculation:**
```
QFS = Σ(rating × importance × evidence_weight) / Σ(importance)
```

**Visual format:** Large numeric display with small formula footnote. Example: **87.3 QFS**

**Why it's differentiated:**
- Standard recruiters use raw match percentages ("89% match") that treat all skills equally
- QFS weights by business importance (is this skill critical?) and evidence quality (is this proven or inferred?)
- The formula is transparent so employers see the rigor behind the number
- A single anchor number creates immediate credibility while the full report provides depth

**MVP viability:** ✅ Perfect for markdown/Gamma - calculate via script, display as text

---

### 2. Evidence Trust Matrix

**What it shows:** A 3×3 matrix cross-referencing skill category vs. evidence quality, showing distribution of where the candidate is "proven" vs. "assumed."

**Data sources:**
- `category` (Responsibility, Hard Skill, Soft Skill)
- `evidence_type` (Story+profile, Profile, Transferable)
- Count per cell

**Visual format:**

| | Story+profile | Profile | Transferable |
|---|---|---|---|
| **Responsibility** | 12 | 0 | 0 |
| **Hard Skill** | 4 | 5 | 2 |
| **Soft Skill** | 3 | 2 | 1 |

Color-coded: Story+profile (green), Profile (yellow), Transferable (orange)

**Why it's differentiated:**
- No standard recruiter quantifies evidence quality—they see "skills listed" without distinguishing "proven via story" vs. "inferred from resume"
- This matrix tells employers: "This candidate has 12 responsibilities backed by concrete stories, but 7 hard skills only inferred from profile"
- Transparency builds trust; it shows where candidates are rock-solid vs. where you should probe
- Particularly valuable for technical roles where evidence quality matters

**MVP viability:** ✅ Simple HTML table with CSS styling in Gamma

---

### 3. Gap Heat Map

**What it shows:** Visual distribution of where candidate has gaps, categorized by skill category and severity.

**Data sources:**
- `rating` vs `required_level` (gap analysis)
- `category`
- `importance` (to highlight critical gaps)

**Visual format:**

| | Excellent | Good | Fair |
|---|:---:|---:|---:|
| **Responsibility** | 🟢 12 | 🟡 1 | 🔴 0 |
| **Hard Skill** | 🟢 4 | 🟡 5 | 🔴 2 |
| **Soft Skill** | 🟢 3 | 🟡 2 | 🔴 1 |

Add emphasis: Critical gaps (importance 8-10) shown with 🚨 icon

**Why it's differentiated:**
- Standard recruiters present gaps as a list or vague "needs work in X"
- Heat map shows patterns at a glance: "All gaps are in Hard Skills, mostly Good/Fair ratings, none in Responsibility"
- Employers can quickly assess: "Is this a dealbreaker gap or something trainable?"
- The "importance filter" (critical gaps) directs attention to high-risk areas

**MVP viability:** ✅ Table with emoji icons in markdown/Gamma

---

### 4. Interview Focus Radar

**What it shows:** A radar/spider chart prioritizing interview topics based on: (1) gap severity, (2) importance, (3) alignment verdict confidence.

**Data sources:**
- From `alignment.yaml`: `verdict` (CLEAR/PARTIAL/GAP)
- From `scores_complete.json`: `importance`
- Derived: gap severity = (required_score - rating_as_number)

**Visual format:** A radar chart with 5-6 axes:
1. AI Guardrails & Reliability (GAP, importance 9)
2. LLM Integration Depth (PARTIAL, importance 10)
3. Vector Search & Retrieval (PARTIAL, importance 6)
4. SOC 2 & Privacy (PARTIAL, importance 8)
5. Frontend UI (Good rating, importance 7)

Each axis shows priority score (0-100).

**Why it's differentiated:**
- Standard recruiters send generic interview lists ("ask about ML experience")
- This radar shows exactly where to probe: "High priority on AI reliability (GAP), medium on frontend (Good rating)"
- The visualization demonstrates analytical rigor—we've cross-referenced gaps, importance, and confidence
- Saves hiring managers time while ensuring they don't miss critical areas

**MVP viability:** ⚠️ Requires chart library (Chart.js, etc.) - not native to Gamma. Can implement as HTML component or fall back to priority list table for MVP.

---

### 5. Baseline Comparison Grid

**What it shows:** How this candidate compares to "typical" candidates for this role, based on Careerspan's database of prior assessments.

**Data sources:**
- Current candidate's scores
- Aggregated baseline data from past assessments (requires historical data collection)
- Percentile calculation

**Visual format:**

| Skill | This Candidate | Typical Candidate | Percentile |
|-------|:---:|:---:|---:|
| **Responsibility** | 95/100 | 72/100 | 92nd |
| **Hard Skills** | 78/100 | 65/100 | 81st |
| **Soft Skills** | 82/100 | 68/100 | 88th |
| **Overall** | 89/100 | 70/100 | 88th |

**Why it's differentiated:**
- Standard recruiters have zero context on "what's typical"—they see isolated candidates
- Employers ask "Is this candidate better than most?"—this answers that question quantitatively
- Percentiles contextualize scores: 89/100 means nothing; "88th percentile" means exceptional
- Requires Careerspan to maintain historical baselines—a long-term competitive moat

**MVP viability:** ⚠️ Requires historical database. Not feasible for immediate MVP, but highly valuable long-term. Flag for phase 2.

---

### 6. Evidence Story Trace

**What it shows:** Interactive linkage from each skill rating to the specific story evidence that supports it, with direct quote extraction.

**Data sources:**
- `story_id` in `scores_complete.json`
- Story transcripts/narratives (stored separately)
- Key quote extraction via LLM from `our_take`

**Visual format:**

For skill "Deliver end-to-end solutions" (Excellent):

> 📚 **Evidence:** "I was a founding engineer and architect for an ML SaaS platform, explicitly describing hands-on ownership across backend, frontend, and AI components." (Story: ML Platform Build)

Click-through: "View full story →"

**Why it's differentiated:**
- Standard recruiters say "has experience in X" without proving it
- This feature shows actual quote, source, and story for every claim—it's auditable
- Employers can verify claims themselves; this transparency builds massive trust
- Particularly powerful for founders who've been burned by candidates overstating experience

**MVP viability:** ✅ Collapsible details in HTML/Markdown. Requires story transcripts to be indexed (already have story_id, need to fetch transcript content). Good for Gamma.

---

### 7. Critical Risk Flagged List

**What it shows:** A concise, red-flagged list of the 3-5 highest-risk areas, combining gap severity + importance + alignment verdict.

**Data sources:**
- From `alignment.yaml`: `critical_gaps`
- From `scores_complete.json`: `importance`, `rating` vs `required_level`
- Synthesis: top 3-5 risks with mitigation suggestions

**Visual format:**

### 🚨 Critical Risks

| Risk | Severity | Mitigation |
|------|:---:|---|
| **No AI failure mode handling documented** | HIGH | Ask: "Tell me about a time an LLM feature failed in production. What was your fallback?" |
| **SOC 2 compliance experience inferred only** | MEDIUM | Ask: "Which SOC 2 controls have you implemented? Describe your audit experience." |
| **Node.js experience missing** | MEDIUM | Probe adaptability: "How quickly could you ramp up on Node.js given your Java/React background?" |

**Why it's differentiated:**
- Standard recruiters highlight strengths and gloss over risks, if they identify them at all
- This section says "Here are the 3 biggest risks, here's how to verify them in the interview"
- Employers appreciate transparency—it shows we're not selling, we're advising
- The mitigation question turns risk into a structured interview probe

**MVP viability:** ✅ Simple markdown table. Easiest to implement. High value per effort.

---

## Recommended MVP: Top 3

### 1. Quality-Weighted Fit Score (QFS)

**Implementation difficulty:** Low  
**Differentiation impact:** High  
**Visual complexity:** Low  

**Rationale:** A single anchor number creates immediate credibility and serves as the headline metric. The formula is transparent and demonstrates analytical rigor. Implementation is trivial (Python script to calculate, display as text).

**Why employers care:** They want a quick "is this worth my time?" signal. QFS answers that while showing our methodology is more sophisticated than "89% match."

---

### 2. Evidence Trust Matrix

**Implementation difficulty:** Low  
**Differentiation impact:** Very High  
**Visual complexity:** Low  

**Rationale:** This is a "holy shit" moment—no other recruiter quantifies evidence quality. It tells employers: "We've verified 12 responsibilities with concrete stories; these 7 hard skills are inferred." That transparency builds trust instantly.

**Why employers care:** They've been burned by candidates claiming skills they can't demonstrate. This matrix shows where evidence is rock-solid vs. where to probe.

---

### 3. Critical Risk Flagged List

**Implementation difficulty:** Very Low  
**Differentiation impact:** High  
**Visual complexity:** Very Low  

**Rationale:** Standard recruiters sell. We advise. This section says "Here are the risks, here's how to verify." Employers trust advisors more than salespeople. The mitigation questions are interview-ready.

**Why employers care:** They want to know what could go wrong. We tell them explicitly, and we give them the exact questions to ask. That's helpful, not promotional.

---

## Implementation Notes

### Gamma Compatibility

All 3 recommended concepts are fully implementable in Gamma:
1. QFS: Simple text display with formula footnote
2. Evidence Trust Matrix: HTML table with CSS styling
3. Critical Risks: Markdown table with emoji flags

No custom charting libraries required for MVP.

### Data Access Patterns

1. **For QFS calculation:**
   - Read `scores_complete.json` as JSON array
   - Map ratings to numeric values
   - Apply evidence_rating weights
   - Compute weighted average

2. **For Evidence Trust Matrix:**
   - Group by `category` × `evidence_type`
   - Count per group
   - Output as structured JSON for rendering

3. **For Critical Risks:**
   - Read `alignment.yaml` `critical_gaps`
   - Cross-reference with `importance` from `scores_complete.json`
   - Sort by (severity × importance)
   - Pull `interview_priorities` questions for mitigation text

### Extension Path (Phase 2)

- **Interview Focus Radar:** Implement with Chart.js or similar
- **Baseline Comparison Grid:** Requires historical database; start tracking now
- **Evidence Story Trace:** Requires story transcript indexing; build pipeline

### Differentiation Summary

| Concept | What Standard Recruiters Do | What Careerspan Does |
|---------|----------------------------|---------------------|
| QFS | Raw match % ("89% match") | Quality-weighted, evidence-adjusted fit metric with transparent formula |
| Evidence Trust Matrix | "Skills listed" (no evidence quality) | Quantifies proven vs. inferred: 12 responsibilities with stories, 7 hard skills inferred |
| Critical Risks | Highlight strengths, gloss over gaps | Explicitly flag risks with interview-ready mitigation questions |

These concepts demonstrate the core value proposition: **Careerspan provides unique, meaningful analysis that competitors cannot offer.**
