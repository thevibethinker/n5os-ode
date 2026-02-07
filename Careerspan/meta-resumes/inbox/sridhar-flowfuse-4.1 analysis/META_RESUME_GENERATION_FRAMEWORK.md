---
created: 2026-01-30
last_edited: 2026-01-30
version: 1.0
provenance: con_jeRxfQEaHBCj6uBz
---

# Meta Resume Generation Framework

Framework for transforming Careerspan Decomposer outputs into employer-facing Meta Resumes.

---

## 1. Output Structure (Target Format)

The Meta Resume has **8 core sections** designed for rapid hiring manager consumption:

| Section | Purpose | Length |
|---------|---------|--------|
| **Header** | Candidate × Company + Role | 1 line |
| **Verdict** | Hire/pass recommendation + confidence | 1 line + brief rationale |
| **What I Optimized For** | The evaluation lens (JD priorities) | 3-5 bullets |
| **Why This Candidate Is Interesting** | Key differentiators | 4-5 bullets with specifics |
| **Risks / Gaps to Probe** | Honest concerns | 4-6 bullets, actionable |
| **How They Operate** | Behavioral patterns | 3-4 observed traits |
| **Interview Questions That Matter** | High-signal probes | 4-6 questions |
| **Signal Strength** | Evidence quality breakdown | Visual bar + percentages |

**Footer:** Methodology transparency (interviews, skills assessed, process notes)

---

## 2. Input → Output Mapping

### 2.1 Header Generation

**Inputs:**
- `overview.yaml` → `candidate.name`, `candidate.company`, `candidate.position_applied`

**Transform:**
```
{candidate.name} × {candidate.company} — Candidate Intelligence Brief
```

**Subheader:**
```
{candidate.name} × {candidate.company} {candidate.position_applied} - Meta Resume
```

---

### 2.2 Verdict

**Inputs:**
- `overview.yaml` → `careerspan_score.overall` (0-100)
- `overview.yaml` → `recommendation.verdict`
- `alignment.yaml` → `critical_gaps` (count and severity)
- `manifest.yaml` → `counts.gaps` (skill gap list)

**Transform Logic:**

| Score Range | Verdict Template |
|-------------|------------------|
| 85-100 | 👍 Take This Meeting — {score}/100 confidence |
| 70-84 | 🤔 Worth a Conversation — {score}/100 confidence |
| 55-69 | ⚠️ Conditional — {score}/100 confidence |
| <55 | 👎 Pass — {score}/100 confidence |

**Rationale formula:**
1. Extract top strength from `alignment.yaml` → first `CLEAR` requirement
2. Note primary gap concern from `critical_gaps`
3. Combine: "{strength descriptor}. {gap concern} are probeable." or "...need verification."

**Example:**
> 👍 Take This Meeting — 89/100 confidence
> Founding-level AI platform builder. Strong execution signal. Key gaps are probeable.

---

### 2.3 What I Optimized For

**Inputs:**
- `jd.yaml` → `raw_jd` (full job description text)
- `alignment.yaml` → `requirements_alignment` (list of evaluated requirements)

**Transform:**
1. Parse JD for the **4-5 highest-importance capabilities** the role demands
2. Filter to capabilities with `importance >= 8` from `scores_complete.json`
3. Reframe as evaluation criteria (what Careerspan looked for)

**Pattern:**
- Convert JD requirements → evaluation lens
- "Build RAG systems" → "AI reliability & real-world failure modes"
- "Strong generalist skills" → "Full-stack ownership in a small team"
- "Remote, async" → "Fit for async, low-structure environments"

**Output format:**
```markdown
**What I Optimized For**
- {Evaluation criterion 1}
- {Evaluation criterion 2}
- {Evaluation criterion 3}
- {Evaluation criterion 4}
```

---

### 2.4 Why This Candidate Is Interesting

**Inputs:**
- `experience.yaml` → `positions[]` (achievements, scope, type)
- `profile.yaml` → `education.notable`, `years_experience`
- `scores_complete.json` → skills with `rating: "Excellent"` and high `importance`
- `overview.yaml` → `evidence_summary.stories_told`
- `soft_skills.yaml` → `leadership` traits

**Transform:**
1. **Filter for "Excellent" + high-importance skills** with `evidence_type: "Story+profile"`
2. **Extract quantified achievements** from `experience.yaml`
3. **Identify exceptional signals** (founding roles, education credentials, scale of impact)
4. **Synthesize into 4-5 bullets** with this pattern:

**Bullet formula:**
```
{Strength label}: {Specific evidence with numbers/names}
```

**Example mappings:**

| Input Source | Output Bullet |
|--------------|---------------|
| `experience.yaml` → Keysight founding + Apple/Samsung customers | 0→1 AI platform builder: Took an ML SaaS from first commit to enterprise adoption (Apple, Samsung, Volkswagen). |
| `experience.yaml` → AmEx $50k/month savings + "solo" scope | Clear business impact: Identified and fixed $50k/month in infra waste at AmEx as a solo owner. |
| `soft_skills.yaml` → "Founding mindset" + "Solo product leadership" | High autonomy: Founding engineer at Keysight; solo product owner at AmEx. |
| `profile.yaml` → JEE rank 47/14M | Exceptional learning velocity: JEE Rank 47 / 14M (top 0.003%) — credible signal for fast stack ramp. |

---

### 2.5 Risks / Gaps to Probe

**Inputs:**
- `alignment.yaml` → `critical_gaps[]`
- `alignment.yaml` → `requirements_alignment` where `verdict: "PARTIAL"` or `verdict: "GAP"`
- `hard_skills.yaml` → `gaps[]`
- `soft_skills.yaml` → `inferred_gaps[]`
- `manifest.yaml` → `counts.gaps`
- `scores_complete.json` → skills with `rating: "Fair"` or `rating: "Gap"`

**Transform:**
1. **Collect all gap signals** from the sources above
2. **Deduplicate and prioritize** by JD importance (from `scores_complete.json` → `importance`)
3. **Reframe as interview-probeable risks**, not disqualifications
4. **Add trajectory/fit considerations** (career direction, work style mismatches)

**Output format:**
```markdown
**Risks / Gaps to Probe**
- {Skill/tech}: {Brief gap description}; expect ~{ramp time} ramp.
- {Area}: {Observed state} but {missing evidence}.
- {Work style concern}: {Background pattern}; unclear {target environment behavior}.
- {Compliance/process}: {What they have} but no evidence of {what's needed}.
- {Career trajectory}: {Observed signal} — may want {future state}.
```

**Gap severity framing:**

| Severity | Language Pattern |
|----------|------------------|
| Hard gap | "No evidence of X" |
| Soft gap | "X present but not explicitly documented" |
| Ramp gap | "Expect ~N weeks ramp" |
| Fit gap | "Unclear X experience" |

---

### 2.6 How They Operate (Observed Patterns)

**Inputs:**
- `soft_skills.yaml` → `work_style[]`
- `soft_skills.yaml` → `leadership[]`, `communication[]`, `collaboration[]`
- `scores_complete.json` → `our_take` narratives for soft skills (filter `category: "Soft Skill"`)

**Transform:**
1. **Identify 3-4 behavioral patterns** that appear across multiple data points
2. **Name the pattern** (e.g., "Impact-first problem solving")
3. **Describe the observed behavior** (what they actually do)

**Pattern extraction heuristics:**
- Look for repeated verbs/actions across `our_take` narratives
- Cross-reference with `soft_skills.yaml` work_style descriptors
- Identify decision-making approaches from achievement context

**Example:**

| Soft Skills Input | Pattern Output |
|-------------------|----------------|
| "Systematic approach: translates ambiguous problems into measurable business impact" | Impact-first problem solving: Starts with bottlenecks, works backward to systems. |
| "Stakeholder management" + "Cross-functional collaboration" | Strong cross-functional execution: Managed stakeholders, feedback loops, and scaling teams. |
| achievements with cost/performance trade-offs | Judgment-driven decisions: Makes explicit trade-offs between cost, performance, and scalability. |

---

### 2.7 Interview Questions That Matter

**Inputs:**
- `alignment.yaml` → `interview_priorities[]` (pre-generated high-signal questions)
- `alignment.yaml` → `critical_gaps[]` + `requirements_alignment` where `verdict != "CLEAR"`
- JD requirements with `importance >= 8` that have `verdict: "PARTIAL"` or `verdict: "GAP"`

**Transform:**
1. **Start with `interview_priorities`** — these are already calibrated to gaps
2. **Condense/reframe** into conversational interview language
3. **Add career trajectory question** (IC vs. lead path)
4. **Ensure coverage** of: technical depth, work style, compliance, growth direction

**Question types to include:**

| Type | Purpose | Example Pattern |
|------|---------|-----------------|
| Technical probe | Verify depth behind claims | "Tell me about a time X failed. What broke, and what was the fallback?" |
| Work style probe | Validate environment fit | "How do you operate when no one assigns work and decisions are async?" |
| Ramp assessment | Estimate time-to-productivity | "What's your honest timeline to shipping production {tech}?" |
| Process probe | Verify compliance capability | "Have you ever designed {process} from scratch?" |
| Trajectory probe | Understand growth direction | "In three years — senior IC or team lead?" |

---

### 2.8 Signal Strength

**Inputs:**
- `scores_complete.json` → `evidence_type` field for all skills
- `overview.yaml` → `evidence_summary.stories_told`

**Transform:**
1. **Count skills by evidence type:**
   - `Story+profile` → "Story-Verified (✓✓)"
   - `Profile` or `Resume` → "Resume-Only (✓)"
   - `Gap` or null → "Inferred (~)"
2. **Calculate percentages** (count / total skills × 100)
3. **Generate visual bar** (use block characters: █ for filled, ░ for empty)

**Visual formula:**
```
{Label}  {bar_representation}  {percentage}%
```

Where bar = `█` repeated (percentage/4 times) + `░` for remainder to 25 chars

**Example:**
```
Story-Verified (✓✓)   ████████████████████████████  78%
Resume-Only (✓)       ████████                      22%
Inferred (~)          ░░                            0%
```

**Takeaway generation:**
- If Story-Verified >= 70%: "Most evaluated skills are backed by first-hand stories, not resume claims — high-confidence execution signal."
- If Story-Verified 40-69%: "Mixed signal strength — verify key claims in interview."
- If Story-Verified < 40%: "Most evidence is resume-based — deeper probing recommended."

---

### 2.9 Footer / Methodology

**Inputs:**
- `overview.yaml` → `evidence_summary.stories_told`
- `manifest.yaml` → `counts.total_skills`
- Process metadata (static for now)

**Output:**
```
{stories_told} structured interviews · {total_skills} skills assessed · No coding test or GitHub review
Powered by Careerspan
```

---

## 3. Synthesis Algorithm

### Step 1: Load All Inputs
```
inputs = {
    overview: parse_yaml("overview.yaml"),
    profile: parse_yaml("profile.yaml"),
    experience: parse_yaml("experience.yaml"),
    alignment: parse_yaml("alignment.yaml"),
    hard_skills: parse_yaml("hard_skills.yaml"),
    soft_skills: parse_yaml("soft_skills.yaml"),
    scores: parse_json("scores_complete.json"),
    jd: parse_yaml("jd.yaml"),
    manifest: parse_yaml("manifest.yaml")
}
```

### Step 2: Derive Computed Fields
```
computed = {
    verdict_emoji: score_to_emoji(inputs.overview.careerspan_score.overall),
    top_strengths: filter(inputs.scores, rating="Excellent", importance>=9),
    gaps: collect_gaps(inputs.alignment, inputs.hard_skills, inputs.soft_skills),
    signal_counts: count_by_evidence_type(inputs.scores),
    operating_patterns: extract_patterns(inputs.soft_skills, inputs.scores)
}
```

### Step 3: Generate Sections
Each section uses its specific transform (documented above) to produce markdown output.

### Step 4: Assemble Document
```markdown
# {candidate} × {company} — Candidate Intelligence Brief

**Verdict:** {verdict_line}
{verdict_rationale}

## What I Optimized For
{optimization_criteria}

## Why This Candidate Is Interesting
{interesting_bullets}

## Risks / Gaps to Probe
{gaps_bullets}

## How They Operate (Observed Patterns)
{operating_patterns}

## Interview Questions That Matter
{interview_questions}

## Signal Strength
{signal_visualization}

**Takeaway:** {signal_takeaway}

---
*{methodology_footer}*
```

---

## 4. Quality Checklist

Before finalizing a Meta Resume, verify:

- [ ] Verdict score matches `overview.yaml` → `careerspan_score.overall`
- [ ] All "Interesting" bullets have specific evidence (numbers, company names, outcomes)
- [ ] All gaps have corresponding interview questions
- [ ] Signal Strength percentages sum to 100%
- [ ] No skill assessments are fabricated (all from `scores_complete.json`)
- [ ] Operating patterns are derived from observed behavior, not inferred traits
- [ ] Footer methodology numbers match source data

---

## 5. Voice & Tone Guidelines

The Meta Resume speaks as "Carrie, your Careerspan recruiter":

| Element | Tone |
|---------|------|
| Verdict | Confident, direct |
| Strengths | Enthusiastic but evidence-backed |
| Gaps | Honest, non-disqualifying ("probe" not "red flag") |
| Questions | Conversational, specific |
| Takeaway | Analytical, conclusive |

**Language patterns:**
- Use active voice: "Took... built... delivered..."
- Quantify everything possible: "$50k/month", "47/14M", "~4-8 weeks"
- Frame gaps as opportunities: "probeable" not "concerning"
- Use emoji sparingly: only in Verdict (👍 👎 🤔 ⚠️)

---

## 6. Appendix: Field Reference

### overview.yaml
- `careerspan_score.overall` → Primary confidence score (0-100)
- `recommendation.verdict` → Human-readable recommendation
- `evidence_summary.stories_told` → Interview depth indicator

### alignment.yaml
- `requirements_alignment[].verdict` → CLEAR | PARTIAL | GAP
- `critical_gaps[]` → Priority gap descriptions
- `interview_priorities[]` → Pre-generated probe questions

### scores_complete.json
- `rating` → Excellent | Good | Fair | Gap
- `evidence_type` → Story+profile | Profile | Resume | Gap
- `importance` → 1-10 (how critical to role)
- `our_take` → Verbatim Careerspan assessment

### soft_skills.yaml
- `work_style[]` → Behavioral descriptors
- `inferred_gaps[]` → Soft skill concerns

### experience.yaml
- `positions[].achievements[].metric` → Quantified outcomes
- `positions[].type` → founding | fulltime | contract
