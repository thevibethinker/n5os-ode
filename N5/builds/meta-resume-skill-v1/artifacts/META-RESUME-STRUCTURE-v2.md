---
created: 2026-01-30
last_edited: 2026-01-30
version: 2.0
provenance: con_jMehIeVWhVi3ZQd8
---

# Meta Resume Structure Specification v2

## Overview

The Meta Resume is a 3-page employer-facing document that complements the traditional resume by revealing what resumes cannot: gaps, unknowns, thinking patterns, and quantified evidence quality.

**Reader:** Technical founder or technical hiring manager  
**Decision time:** 30 seconds on Page 1, 2-3 minutes total  
**Competing with:** Standard recruiter pitch + resume + LinkedIn

---

## Page 1: The 30-Second Decision

### 1.1 Header

| Attribute | Spec |
|-----------|------|
| **Purpose** | Immediate identification + recommendation signal |
| **Format** | Single line with visual indicator |
| **Content** | `[Logo] [Candidate Name] | [Role] @ [Company] | [Emoji] [Score]% — [Threshold Note]` |
| **Example** | `Careerspan × CorridorX  ·  Hardik | AI Engineer @ FlowFuse | 👍 89% — Above 75% threshold` |
| **Data sources** | `overview.yaml`: candidate.name, position_applied, company, careerspan_score.overall |

**Visual Indicators:**
- 👍 (75%+): Take the meeting
- 🤷 (60-74%): Situational — depends on priorities  
- 👎 (<60%): Pass unless desperate

**Anti-patterns:**
- ❌ Long titles or subtitles
- ❌ Marketing language ("exceptional candidate")
- ❌ Hiding the score

---

### 1.2 What Hiring [Name] Boils Down To

| Attribute | Spec |
|-----------|------|
| **Purpose** | 2-3 sentence synthesis — the 80/20 |
| **Format** | Prose, max 50 words |
| **Question answered** | "In one breath, who is this person and what's the trade-off?" |
| **Data sources** | `overview.yaml`: recommendation.summary; `alignment.yaml`: critical_gaps |

**Template:**
> [Name] is a [archetype] with [key strength]. The trade-off: [primary gap]. The meeting will reveal [open question].

**Example:**
> Hardik is a founding-level AI platform builder with proven production ROI ($50k/mo savings, 5x budget increase). The trade-off: No Node.js experience (FlowFuse's primary stack). The meeting will reveal whether his learning velocity can close that gap fast enough.

**Anti-patterns:**
- ❌ More than 3 sentences
- ❌ No trade-off mentioned
- ❌ Generic praise ("great communicator")

---

### 1.3 What's Clear / What's Not Clear

| Attribute | Spec |
|-----------|------|
| **Purpose** | Binary signal index — instant pattern recognition |
| **Format** | Two-column table, 4-6 items per column |
| **Question answered** | "What can I trust vs. what needs verification?" |
| **Data sources** | `alignment.yaml`: requirements (met=true → Clear, met=partial/unknown → Not Clear) |

**Format:**

| What's Clear ✓ | What's Not Clear ? |
|----------------|-------------------|
| 0→1 AI platform experience | LLM guardrails depth |
| Full-stack ownership | Async-first operating style |
| Business impact metrics | Compliance ownership |
| Elite learning velocity | Node.js/TypeScript |

**Rules:**
- Clear = binary yes, proven with evidence
- Not Clear = unknown, partial, or needs probing
- No evidence in this section (that's Page 2)
- Max 6 items per column

**Anti-patterns:**
- ❌ Evidence or explanation (this is the INDEX, not the body)
- ❌ Overlapping with "What You're Getting" (that section has evidence)
- ❌ More than 12 total items

---

### 1.4 Decision Matrix

| Attribute | Spec |
|-----------|------|
| **Purpose** | Self-selection filter — let readers opt out fast |
| **Format** | Table with 6-8 rows |
| **Question answered** | "Given my priorities, should I keep reading?" |
| **Data sources** | `alignment.yaml`: requirements, gaps; `scores_complete.json`: importance rankings |

**Format:**

| If you need... | [Candidate] is... |
|----------------|-------------------|
| Day-one Node-RED shipping | ❌ Not your candidate |
| Someone to define AI from zero | ✅ Strong signal |
| Proven compliance architect | ❓ Unclear — probe |
| High autonomy, low oversight | ✅ Strong signal |
| Long-term IC commitment | ❓ Probe — trajectory shows mgmt interest |

**Verdicts:**
- ✅ Strong signal (evidence supports)
- ❓ Unclear (needs probing)
- ❌ Not your candidate (gap is real)

**Rules:**
- Include at least 2 "❌ Not your candidate" scenarios
- Include at least 2 "❓ Unclear" scenarios
- Tie to actual JD requirements

**Anti-patterns:**
- ❌ All positive scenarios
- ❌ Generic trade-offs not specific to this candidate
- ❌ More than 8 rows

---

## Page 2: Depth

### 2.1 What You're Getting

| Attribute | Spec |
|-----------|------|
| **Purpose** | Evidence-backed positive signals — the body for "What's Clear" |
| **Format** | Table with 4-6 rows |
| **Question answered** | "What specifically can this person do, and how do I know?" |
| **Data sources** | `scores_complete.json`: skills with rating=Excellent/Good; `alignment.yaml`: requirements with met=true |

**Format:**

| Asset | Evidence | [Company] Relevance |
|-------|----------|---------------------|
| **Founding AI Platform Builder** | Keysight: ML SaaS from scratch, Apple/Samsung/VW clients, team 0→20 | Can define what AI looks like, not just execute |
| **Proven Production ROI** | AmEx: $50k/month savings, 150+ services, zero downtime | Converts technical work into business outcomes |
| **Full-Stack Depth** | React + Spring Boot + FastAPI + K8s + Airflow | Won't throw problems over the wall |

**Rules:**
- Every row has specific evidence (company, metric, scope)
- Relevance column ties to THIS company's needs
- Only items already marked "Clear" on Page 1
- Max 6 assets

**Anti-patterns:**
- ❌ Generic claims ("good communicator")
- ❌ Evidence without specifics
- ❌ Items that weren't in "What's Clear" (that's overlap)

---

### 2.2 What You're NOT Getting (Gaps)

| Attribute | Spec |
|-----------|------|
| **Purpose** | Explicit gaps with severity — the negative space |
| **Format** | Table with 3-5 rows |
| **Question answered** | "What's missing, and how bad is it?" |
| **Data sources** | `alignment.yaml`: critical_gaps; `scores_complete.json`: skills with rating=Fair or required_level gap |

**Format:**

| Gap | Severity | What It Means |
|-----|----------|---------------|
| **Node.js/Node-RED** | MEDIUM-HIGH | Stack is Python/Java. Ramp time before production Node-RED. Fixable with pairing. |
| **LLM Safety & Observability** | MEDIUM | Shipped LLM/RAG but no explicit fallback strategies documented. Probe in meeting. |
| **Compliance Ownership** | MEDIUM | Operated within compliant infra, but no evidence of designing SOC 2 controls. |

**Severity levels:**
- **HIGH:** Likely dealbreaker unless addressed
- **MEDIUM-HIGH:** Significant, requires mitigation
- **MEDIUM:** Notable, manageable with awareness
- **LOW:** Minor, unlikely to affect success

**Rules:**
- Every gap has actionable implication
- At least one HIGH or MEDIUM-HIGH
- Include "Probe in meeting" where appropriate

**Anti-patterns:**
- ❌ Vague gaps ("may struggle")
- ❌ Gaps without severity
- ❌ No actionable implications

---

### 2.3 How They Think

| Attribute | Spec |
|-----------|------|
| **Purpose** | Problem-solving style extracted from story data |
| **Format** | 3-4 bullet points with evidence |
| **Question answered** | "How does this person approach ambiguous problems?" |
| **Data sources** | `scores_complete.json`: our_take fields; story transcripts |

**Format:**

**Problem-Solving Patterns:**
- **Pragmatic over perfect:** Chose Python backend over Nest.js for architectural consistency, not technical novelty. Prioritized reproducibility and user adoption over sophistication.
- **Systems thinker:** Built resource orchestrator to balance performance vs. cost. Sees connections across infrastructure, product, and business outcomes.
- **User-feedback driven:** Managed large volumes of feedback post-rollout, personally triaged and prioritized. Iterative cycles visible in product evolution.

**Data extraction:**
- Pull from `our_take` fields in `scores_complete.json`
- Look for patterns across multiple assessments
- Cite specific examples where possible

**Anti-patterns:**
- ❌ Generic traits ("hardworking")
- ❌ No evidence for patterns
- ❌ More than 4 bullets

---

### 2.4 Gaps to Probe (Interview Questions)

| Attribute | Spec |
|-----------|------|
| **Purpose** | Exact questions to surface disqualifiers fast |
| **Format** | 4-5 numbered questions with rationale |
| **Question answered** | "What should I ask in the first 30 minutes?" |
| **Data sources** | `alignment.yaml`: interview_priority; gap analysis |

**Format:**

### Interview Priorities

1. **Motivation** — He's building for Fortune 500 clients. Why FlowFuse?
   > "You're architecting for Apple and Samsung. What specifically draws you to Node-RED and low-code AI?"

2. **Compliance Ownership** — AmEx gave him a compliant environment. FlowFuse may need him to build one.
   > "Have you ever designed audit logging, access controls, or security policies from scratch? Walk me through what you owned versus inherited."

3. **LLM Safety Depth** — Resume shows capability. Need to probe guardrails.
   > "Tell me about a time an ML/AI system you built failed in production. What broke, and what did you change?"

**Rules:**
- Include exact question phrasing in blockquote
- Brief rationale (1 sentence) before each question
- Tie questions to gaps from 2.2
- Max 5 questions

**Anti-patterns:**
- ❌ Generic interview questions ("Tell me about yourself")
- ❌ Questions answerable from resume
- ❌ No rationale for why this question matters

---

### 2.5 Candidate's Context

| Attribute | Spec |
|-----------|------|
| **Purpose** | Space for candidate's own gap explanations |
| **Format** | 3-4 lines of prose, or blank with placeholder |
| **Question answered** | "What does the candidate want me to know about their gaps?" |
| **Data sources** | Candidate rebuttal input (if provided) |

**Format (if provided):**

> **From the candidate:** "I haven't used Node.js professionally, but I've built personal projects with it and contribute to an open-source Node-RED palette. I'm confident I can ramp within 4-6 weeks given my JavaScript foundation and past stack transitions (Java → Python)."

**Format (if not provided):**

> **Candidate context not provided.** This candidate has not submitted additional context for their gaps. Consider asking directly in the interview.

**Rules:**
- Preserve candidate's voice verbatim
- Max 4 lines
- If no rebuttal provided, use placeholder text

**Anti-patterns:**
- ❌ Editorializing the candidate's statement
- ❌ Hiding that no context was provided

---

## Page 3: [Candidate] By The Numbers

### 3.1 Quality-Weighted Fit Score (QFS)

| Attribute | Spec |
|-----------|------|
| **Purpose** | Single anchor metric with transparent methodology |
| **Format** | Large number + formula footnote |
| **Data sources** | `scores_complete.json`: rating, importance, evidence_rating |

**Format:**

## 87.3 QFS

*Quality-Weighted Fit Score = Σ(rating × importance × evidence_weight) / Σ(importance)*  
*Evidence weights: Direct=1.0, Transferable=0.8, Profile=0.7*

**Why this matters:** Unlike raw match percentages, QFS weights skills by business importance and evidence quality.

---

### 3.2 Evidence Trust Matrix

| Attribute | Spec |
|-----------|------|
| **Purpose** | Visualize where evidence is proven vs. inferred |
| **Format** | 3×3 table with counts |
| **Data sources** | `scores_complete.json`: category × evidence_type counts |

**Format:**

| | Story+Profile 🟢 | Profile Only 🟡 | Transferable 🟠 |
|---|:---:|:---:|:---:|
| **Responsibility** | 12 | 0 | 0 |
| **Hard Skill** | 4 | 5 | 2 |
| **Soft Skill** | 3 | 2 | 1 |

**Interpretation:** 12 responsibilities backed by concrete stories. 7 hard skills inferred from profile only — probe these areas.

---

### 3.3 GitHub Snapshot

| Attribute | Spec |
|-----------|------|
| **Purpose** | Objective code activity evidence |
| **Format** | Stats block + contribution calendar (if available) |
| **Data sources** | GitHub API: contributions, languages, repos |

**Format:**

### GitHub: [@username](https://github.com/username)

| Metric | Value |
|--------|-------|
| **Public Repos** | 23 |
| **Total Contributions (12mo)** | 847 |
| **Top Languages** | Python (45%), TypeScript (30%), Java (15%) |
| **Longest Streak** | 34 days |
| **Last Active** | 3 days ago |

[Contribution calendar visualization if available]

**If GitHub not provided:**

> ⚠️ **GitHub not provided.** No public code profile available. Probe coding practices in interview.

---

### 3.4 Links & Sources

| Attribute | Spec |
|-----------|------|
| **Purpose** | Quick access to primary sources |
| **Format** | Bulleted list |
| **Data sources** | Input data, decomposed files |

**Format:**

**Primary Sources:**
- [LinkedIn](https://linkedin.com/in/username)
- [GitHub](https://github.com/username)
- [Resume](link-if-available)

**Careerspan Analysis:**
- Stories analyzed: 2
- Skills assessed: 45
- Analysis date: 2026-01-29

---

### 3.5 Critical Risks (Flagged)

| Attribute | Spec |
|-----------|------|
| **Purpose** | Top 3 risks with mitigation questions |
| **Format** | Table with severity flags |
| **Data sources** | `alignment.yaml`: critical_gaps × importance |

**Format:**

| 🚨 Risk | Severity | Mitigation Question |
|---------|:--------:|---------------------|
| No AI failure mode handling documented | HIGH | "Tell me about a time an LLM feature failed in production." |
| SOC 2 compliance experience inferred only | MEDIUM | "Which SOC 2 controls have you implemented?" |
| Node.js experience missing | MEDIUM | "How quickly could you ramp on Node.js?" |

---

## Tone Guide

1. **Cold objectivity.** No advocacy. We're advisors, not salespeople. Trade-offs build credibility.

2. **Truffle pig aesthetic.** We're rooting out signal. Employers pay us to find what others miss.

3. **Founder-facing language.** No HR-speak. Direct, specific, actionable. "Stack mismatch is real" not "opportunity for growth."

4. **Specificity over generality.** Every claim has evidence. Every gap has severity. No "may struggle with."

5. **Negative space emphasis.** Resumes handle positive space. We reveal what's missing, unknown, or risky.

6. **Transparency builds trust.** Show methodology. Display formulas. Cite sources. If we don't know, say "Unknown."

7. **Decision support, not decisions.** We say "hire IF you prioritize X." The employer decides.

---

## Data Source Mapping

| Section | Primary Data Source |
|---------|---------------------|
| Header | `overview.yaml` |
| Bottom Line | `overview.yaml`, `alignment.yaml` |
| What's Clear/Not Clear | `alignment.yaml`: requirements |
| Decision Matrix | `alignment.yaml`, `scores_complete.json` |
| What You're Getting | `scores_complete.json` (rating=Excellent/Good) |
| Gaps | `alignment.yaml`: critical_gaps, `scores_complete.json` |
| How They Think | `scores_complete.json`: our_take fields |
| Interview Questions | `alignment.yaml`: interview_priority |
| Candidate Context | External input (candidate rebuttal) |
| QFS | `scores_complete.json` (calculated) |
| Evidence Matrix | `scores_complete.json` (aggregated) |
| GitHub | GitHub API (external fetch) |
| Links | Input data |
| Critical Risks | `alignment.yaml` × `scores_complete.json` |

---

## Quality Checklist

Before generating any Meta Resume:

- [ ] Page 1 answers "should I keep reading?" in 30 seconds
- [ ] Every "What's Clear" item has evidence in "What You're Getting"
- [ ] Every gap has severity and actionable implication
- [ ] Decision Matrix includes at least 2 "Not your candidate" scenarios
- [ ] Interview questions are specific and tie to documented gaps
- [ ] QFS formula is visible and explained
- [ ] GitHub section present (or explicit "not provided" warning)
- [ ] No overlap between sections
- [ ] Tone is objective, not promotional
