# GTM Document Structural Fixes

**Date:** 2025-10-13 19:07 ET  
**Status:** Ready to execute

---

## Issues to Fix

### 1. **Structural Chaos**
- **Problem:** Mixing "Insight X: Person Name" headers with "Insight Y — Description" 
- **Example:** "Insight 1: Usha Srinivasan" followed by "Insight 2 — Employers in SME..."
- **Fix:** Use consistent structure:
  - **Stakeholder name as H3** (`### Usha Srinivasan — External`)
  - **Insight description as H4** (`#### Insight 1 — Description`)
  - **Attribution tag** (External vs. Internal/Careerspan)

### 2. **Missing Stakeholder Attribution**
- **Problem:** Can't distinguish external stakeholders from Careerspan internal voices
- **Internal speakers:** Vrijen, Logan, other team members
- **External speakers:** Everyone else
- **Fix:** Add attribution tags to stakeholder headers:
  - `### Usha Srinivasan — External`
  - `### Vrijen Attawar — Careerspan Internal`
  - `### Logan Currie — Careerspan Internal`

### 3. **Weak Synthesis Section**
- **Problem:** Current synthesis is 5 bullet points + 5 recommendations = too shallow
- **Fix:** Expand to include:
  - **Detailed pattern analysis** across all meetings
  - **Contradictions/tensions** between stakeholder views
  - **Segment-specific insights** (communities vs. enterprise)
  - **Timeline/sequencing** recommendations
  - **Risk factors** and failure modes
  - **Quantitative summary** of insight distribution
  - Target: 2-3x current length

### 4. **Undefined Signal Strength**
- **Problem:** ● ● ● ● ○ system used but never explained
- **Fix:** Add definition section at top of document:
  ```markdown
  **Signal strength scale:**
  - ● ● ● ● ● (5/5): Direct, actionable, verified by multiple sources
  - ● ● ● ● ○ (4/5): Strong evidence, single source, high confidence
  - ● ● ● ○ ○ (3/5): Good evidence, requires validation
  - ● ● ○ ○ ○ (2/5): Weak signal, speculative, needs more data
  - ● ○ ○ ○ ○ (1/5): Low confidence, hypothesis only
  ```

### 5. **Quote Quality Issues**
- **Problem:** Many quotes from internal Careerspan discussions (Vrijen explaining product strategy)
- **Not actionable now** but flag for future cleanup

---

## Proposed New Structure

```markdown
# GTM Aggregated Insights

**Version:** 1.2
[metadata...]

**Signal strength scale:**
- ● ● ● ● ● (5/5): Direct, actionable, verified by multiple sources
- ● ● ● ● ○ (4/5): Strong evidence, single source, high confidence
- ● ● ● ○ ○ (3/5): Good evidence, requires validation
- ● ● ○ ○ ○ (2/5): Weak signal, needs more data
- ● ○ ○ ○ ○ (1/5): Low confidence, hypothesis only

---

## Trust & Proof

### Usha Srinivasan — External
**Role:** Community builder / University career services

#### Insight 1 — Employers in SME sectors value soft-skill readiness
- Evidence: [...]
- Why it matters: [...]
- Signal strength: ● ● ● ● ○

**Supporting evidence from transcript:**
> [quote]

#### Insight 2 — White-label partnerships lower friction
- Evidence: [...]
- Why it matters: [...]
- Signal strength: ● ● ● ○ ○

**Supporting evidence from transcript:**
> [quote]

---

### Krista Tan — External
**Role:** Community founder (Women in Product)

#### Insight 1 — Quality-first programming is retention lever
[...]

---

### Vrijen Attawar — Careerspan Internal
**Context:** Internal team discussion / customer conversations

#### Insight 1 — Referrals dominate hiring
[...]

---

[Continue for all stakeholders...]

---

## Synthesis

### Executive Summary
[High-level takeaways, 2-3 paragraphs]

### Pattern Analysis

#### 1. Community Distribution (Dominant Theme)
- **Frequency:** 11 insights across 5 meetings
- **Key stakeholders:** Usha, Krista, David, Rajesh
- **Consensus points:**
  - [...]
- **Tensions/contradictions:**
  - [...]
- **Actionability:** High

#### 2. Trust & Proof Requirements
- **Frequency:** 10 insights across 6 meetings
- **Key insight:** [...]
- **Segment differences:**
  - Communities: [...]
  - Enterprise: [...]

#### 3. [Continue for each pattern...]

### Segmentation Analysis

**Communities (Usha, Krista, David):**
- Value proposition: [...]
- Pricing sensitivity: [...]
- Integration needs: [...]

**Enterprise/Scale-ups (Whitney, Allie, Rajesh):**
- Value proposition: [...]
- Pricing sensitivity: [...]
- Integration needs: [...]

### Contradictions & Tensions

1. **Proactive vs. Urgent hiring modes:**
   - Whitney: "High growth = hard to be relational"
   - Krista: "Organic growth takes time"
   - Resolution: Dual-mode pricing strategy

2. **Quality vs. Volume:**
   - [...]

### Timeline & Sequencing

**Phase 1 (0-3 months):**
- [...]

**Phase 2 (3-6 months):**
- [...]

### Risk Factors

1. **Integration friction** (Usha, Krista): [...]
2. **Proof requirements** (Krista, Whitney): [...]
3. **[...]**

### Quantitative Summary

- **Total insights:** 35
- **External stakeholders:** 5
- **Internal discussions:** 1
- **Signal strength distribution:**
  - 5/5: 0 insights
  - 4/5: 12 insights (34%)
  - 3/5: 23 insights (66%)
  - 2/5: 0 insights
  - 1/5: 0 insights

### Recommended Actions (Prioritized)

1. **Immediate (Week 1-2):**
   - [...]

2. **Near-term (Month 1-2):**
   - [...]

3. **Medium-term (Month 3-6):**
   - [...]
```

---

## Implementation Steps

1. **Add signal strength definition** at top
2. **Restructure sections** with stakeholder-first organization
3. **Add attribution tags** (External vs. Internal)
4. **Expand synthesis section** 3x
5. **Validate all quotes** match stakeholder attribution
6. **Update ToC** to reflect new structure

---

**Estimated time:** 90-120 minutes
