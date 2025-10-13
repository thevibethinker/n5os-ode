# LLM Aggregation Prompt

You are aggregating market intelligence insights from customer research conversations.

## Task

Create an aggregated insights document that identifies patterns, validates signals, and surfaces opportunities.

## Input Data

**8 insights extracted from 2 meetings:**

### From: Asher King Abramson (Warmer Jobs founder - networking-driven job discovery)

1. **Network-first tools create premium value for introductions**
   - Observation: Users value employer intros highly and would pay for them
   - Implication: Intro facilitation is monetizable at premium pricing
   - Signal: ●●●○○ (Medium)

2. **Product roles show higher willingness to pay**
   - Observation: Product managers likelier to pay for job tools
   - Implication: Early vertical should target product communities
   - Signal: ●●●○○ (Medium)

3. **Recruiting-bounty marketplaces provide fast path to employer supply**
   - Observation: Recruiting bounties exist as integration point
   - Implication: Can validate monetization through low-friction bounty pilots
   - Signal: ●●●○○ (Medium)

4. **Retention acceptable but needs product lift**
   - Observation: 35% weekly retention - reasonable but improvable
   - Implication: Features enabling micro-engagement may increase stickiness
   - Signal: ●●●○○ (Medium)

### From: Charles Jolley (Founder/advisor in talent/operations)

5. **Employers value front-loaded, high-signal candidate signals over credentials**
   - Observation: Async interviews and curated pools gaining traction
   - Implication: Position as high-signal pipeline, charge premium for quality
   - Signal: ●●●○○ (Medium)

6. **Gap between ATS volume and curated community talent pools creates defensibility**
   - Observation: Embedding in trusted communities creates moats
   - Implication: Prioritize formalizing community partnerships with contracts
   - Signal: ●●●○○ (Medium)

7. **Screening modality matters: async/video compresses hiring cycles**
   - Observation: Async approaches improve quality but face candidate resistance
   - Implication: Combine coaching (improve signal) with async screening
   - Signal: ●●●○○ (Medium)

8. **Pricing framing matters for early-stage buyers**
   - Observation: Early-stage expects lower-cost; "high-signal filter" justifies mid-high tiers
   - Implication: Frame product around signal quality, not just access
   - Signal: ●●●○○ (Medium)

---

## Instructions

Create a structured aggregated insights document with:

### 1. Pattern Detection
- Group similar insights together
- Identify themes that appear across multiple sources
- Note: With only 2 sources, look for complementary insights (not just duplicates)

### 2. Signal Assessment
- All are currently medium strength (●●●○○)
- Assess which are most actionable
- Note any that could be elevated to "emerging signal" if validated by one more source

### 3. Contradictions
- Flag any insights that tension with each other

### 4. Opportunity Map
- Convert strong patterns into actionable opportunities
- Format: Insight → Opportunity → Recommended Action

### 5. What's Missing
- What types of sources would strengthen these signals?
- What questions remain unanswered?

---

## Output Format

```markdown
# Market Intelligence: Aggregated Research Insights

**Last Updated:** [timestamp]
**Meetings Analyzed:** 2
**Total Insights:** 8
**Sources:** Asher King Abramson (Warmer Jobs), Charles Jolley (Talent Ops)

---

## Pattern Analysis

### [Pattern Name]
**Verified by:** [X] sources
**Signal strength:** [assessment]

[Description of pattern]

**Sources:**
- [Source 1]: [Their specific insight]
- [Source 2]: [Their specific insight]

---

## Single-Source Insights (Monitor for Validation)

### [Category]

[Insights from only one source that need validation]

---

## Opportunity Map

### [Opportunity Name]
**Based on:** [Pattern/insight]
**Confidence:** [High/Medium/Low]
**Recommended action:** [What to do]

---

## What's Missing / Validation Needed

- [Gap 1]
- [Gap 2]

---

## Next Meeting Priorities

[What questions to ask/who to talk to next to strengthen signals]
```

Generate the complete aggregated document now.
