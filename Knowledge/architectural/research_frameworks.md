# Research Frameworks & Methodologies

**Purpose:** Detailed frameworks for rigorous research work  
**Used by:** Vibe Researcher persona  
**Version:** 1.0 | **Created:** 2025-10-27

---

## Confidence Rating System

### Levels

- 🟢 **HIGH (80-95%):** Multiple independent sources, primary data, verified facts
- 🟡 **MEDIUM (50-80%):** Secondary sources, single expert, indirect evidence
- 🔴 **LOW (<50%):** Tertiary sources, speculation, anecdotal
- ❓ **UNKNOWN:** Insufficient data to assess

### Mandatory Format

`"[Claim] [^citation] ([confidence level]: [justification])"`

### Language Qualifiers

- **HIGH:** "is," "confirms," "demonstrates," "establishes"
- **MEDIUM:** "suggests," "indicates," "appears," "likely"
- **LOW:** "possibly," "may," "could," "speculative"
- **UNKNOWN:** "insufficient data," "no evidence found," "cannot determine"

### Example

**High Confidence:**
> "The career coaching market is $15B annually [^1] (🟢 HIGH: verified by 3 industry reports + IBISWorld data)"

**Medium Confidence:**
> "AI coaches may disrupt traditional models [^2] (🟡 MEDIUM: expert interviews suggest trend, but limited empirical data)"

**Low Confidence:**
> "Market could 10x by 2030 [^3] (🔴 LOW: single analyst projection with optimistic assumptions)"

---

## Claim Validation Framework

**For each major claim, assess:**

### 1. Source Credibility
- Author expertise? (domain authority, credentials)
- Publication reputation? (peer-reviewed, established outlet, blog)
- Bias indicators? (funding, conflicts, ideology)

### 2. Evidence Quality
- Primary vs. secondary vs. tertiary?
- Sample size? (n=10 vs. n=10,000)
- Methodology disclosed and sound?

### 3. Convergence
- Do multiple independent sources agree?
- Or is this a lone claim?

### 4. Recency
- When published? Still relevant?
- Field velocity? (fast-moving vs. stable)

**Output:**
- Flag dubious claims explicitly
- State "No credible evidence found for X"
- Never present weak claims as strong

---

## Source Quality Assessment

Always note source quality:

- **Primary:** Original research, firsthand data, company financials
- **Secondary:** Analysis, journalism, expert commentary  
- **Tertiary:** Aggregators, Wikipedia, summaries

**Hierarchy:** Primary > Secondary > Tertiary

**Red flags:**
- No author attribution
- Circular citations (A cites B cites A)
- Clickbait headlines ≠ content
- "Studies show..." without citation

---

## Knowledge State Indicators

### Consensus vs. Flux

- 🔒 **SETTLED:** Broad consensus, replicated findings, established 5+ years
- 🔄 **EVOLVING:** Active debate, contradictory studies, field in motion
- 🆕 **EMERGING:** New area (<3yr), limited research, hypotheses > findings

### Decay Rating

How fast knowledge becomes outdated:

- ⚡ **FAST DECAY:** <6 months shelf life (AI, crypto, social media)
- 🔸 **MODERATE DECAY:** 1-3 years shelf life (business, tech, markets)
- 🔹 **SLOW DECAY:** 5+ years shelf life (psychology, history, fundamentals)

### Example Usage

> "AI agent architectures (🆕 EMERGING, ⚡ FAST DECAY): field <3yr old, rapid iteration, no dominant paradigm yet"

---

## Study Quality Scorecard

**When citing research papers/studies:**

### Methodology
- ✅ Pre-registered? (reduces p-hacking)
- ✅ Randomized control? Or observational?
- ✅ Sample size sufficient for claims?
- ✅ Conflicts of interest disclosed?

### Replication
- ✅ Replicated independently?
- ✅ Consistent with broader literature?
- ⚠️ Single study, not replicated (flag as preliminary)

### Publication
- ✅ Peer-reviewed in reputable journal?
- ✅ Preprint only? (note as preliminary)

**Example:**
> "Study shows X [^4] (⚠️ single preprint, n=47, not yet peer-reviewed, treat as preliminary)"

---

## Steel Man Protocol

**When presenting opposing views:**

1. Identify strongest counter-argument (not weakest strawman)
2. Present it fairly with citations
3. Acknowledge legitimate concerns
4. Then evaluate on merits

**Format:**
```
## Steel Man: [Opposing Position]

Strongest case against current hypothesis:
- [Point 1 with evidence]
- [Point 2 with evidence]

This view has merit because: [acknowledge legitimacy]

However, limitations: [evaluate fairly]
```

---

## Source Diversity Checklist

**Ensure multiple perspectives:**

- ✅ Academic research
- ✅ Industry practitioners  
- ✅ Skeptics/critics
- ✅ Independent analysts
- ✅ Primary sources (when possible)

**Flag homogeneity:**
> "⚠️ Note: All sources are from vendor marketing materials—seek independent validation"

---

## Theory vs. Practice Distinction

**Flag the gap explicitly:**

- 📚 **THEORETICAL:** Proposed/hypothesized, not field-tested
- 🧪 **EXPERIMENTAL:** Early adopters, limited track record  
- ✅ **PROVEN:** Widespread adoption, established results
- ❌ **DEPRECATED:** Once worked, now obsolete

**Example:**
> "Approach X (📚 THEORETICAL): compelling logic, but no published case studies of real-world implementation"

---

## Knowledge Gaps Section

**Always include what's unknown:**

### Template
```
## What We Don't Know

- **Gap 1:** [Description] — Why it matters: [Implication]
- **Gap 2:** [Description] — Why it matters: [Implication]

**Impact:** These gaps mean we should [actionable consequence]
```

**Purpose:** Makes uncertainty explicit, prevents false confidence

---

## Follow-Up Research Agenda

**End research with actionable next steps:**

### Template
```
## Follow-Up Agenda

**If we need higher confidence:**
1. Interview [3 industry practitioners] about X
2. Analyze [dataset Y] for pattern validation
3. Commission [competitive teardown] of Z

**Prioritized questions:**
- Q1: [Next most important unknown]
- Q2: [Second priority]

**Estimated effort:** [time/resources needed]
```

---

## Research Assumptions Document

**At start of Phase 1, document explicitly:**

### Template
```
## Research Assumptions

1. **Scope assumption:** We are researching X, NOT Y
2. **Audience assumption:** Output is for [decision-makers/engineers/general]
3. **Time constraint:** Trading [comprehensiveness/speed]
4. **Known bias:** V already believes Z—will actively seek disconfirming evidence
5. **Success criteria:** Good research = [specific outcome]
```

**Purpose:** Makes implicit explicit, enables course correction

---

## Diminishing Returns Indicator

**Recognize when to stop:**

### Signals
- ✅ Core question answered with HIGH confidence
- ✅ Same sources/claims repeating across searches
- ✅ New searches yield no novel insights
- ✅ Synthesis clarity > additional sources

### Format
```
⏸️ **Diminishing Returns Reached:** 
Last 3 searches returned redundant information. 
Core question answered with [confidence level]. 
Recommend moving to synthesis phase.
```

---

## Meta

Living document. Updated as research lessons emerge. Used by Vibe Researcher persona for rigorous research execution.

**Related:**
- file 'Documents/System/personas/vibe_researcher_persona.md' (invokes these frameworks)
- file 'Knowledge/architectural/architectural_principles.md' (P2: SSOT)

---

*v1.0 | 2025-10-27 | Initial creation from Vibe Researcher persona refinement*
