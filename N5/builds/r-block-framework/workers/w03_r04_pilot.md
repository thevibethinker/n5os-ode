# Worker Assignment: w03_r04_pilot

**Project:** r-block-framework  
**Component:** R04_Market (PILOT BLOCK)  
**Dependencies:** w01_foundation (must be complete first)  
**Output:** `Prompts/Blocks/Reflection/R04_Market.prompt.md`

---

## Objective

Develop **R04 (Market Signal)** as the **pilot block** — the first fully-developed R-block using the base template. This sets the quality bar for all other blocks.

## Pre-Requisite

First, read the base template:
```bash
cat N5/templates/reflection/r_block_base.md
```

## R04 Domain: Market Signals

R04 extracts **market intelligence** from reflections — competitive dynamics, distribution channels, timing signals, trend validation.

### What R04 Sees
- Competitive landscape observations
- Distribution channel insights
- Market timing indicators
- Customer/user behavior patterns
- Industry trend signals
- Partnership/ecosystem dynamics

### What R04 Ignores (handled by other blocks)
- Product feature ideas → R05
- Business model/venture ideas → R08
- Personal emotional reactions → R01
- Strategic decisions about Careerspan → R03

## Analysis Dimensions for R04

1. **Signal Type:** What kind of market signal is this?
   - Competitive move
   - Channel emergence/shift
   - Demand signal
   - Timing indicator
   - Ecosystem shift

2. **Confidence Level:** How validated is this signal?
   - Direct observation (high)
   - Secondhand report (medium)
   - Speculation/intuition (low)

3. **Actionability:** What could be done with this?
   - Immediate action possible
   - Monitor and wait
   - File for future reference

4. **Time Sensitivity:** How long is this signal valid?
   - Urgent (days/weeks)
   - Medium-term (months)
   - Structural (years)

5. **Careerspan Relevance:** How does this connect to the business?
   - Direct impact
   - Adjacent/analogous
   - General market context

## Worked Example

Use the recruiter-game-plan reflection as the example:

**Input snippet:**
> "AI headhunter companies like Marvin... they need distribution, we need sourcing capacity... feels like a partnership play rather than build-vs-buy"

**R04 Analysis:**
- Signal Type: Ecosystem shift (AI headhunters emerging as category)
- Confidence: Direct observation (V is in active conversations)
- Actionability: Immediate (partnership outreach possible)
- Time Sensitivity: Medium-term (market forming now, 6-12mo window)
- Careerspan Relevance: Direct impact (solves distribution problem)

## Output Schema

```markdown
## R04: Market Signal

**Signal:** [One-line description]
**Type:** [Competitive | Channel | Demand | Timing | Ecosystem]
**Confidence:** [High | Medium | Low]

### Analysis
[2-3 paragraphs unpacking the signal]

### Evidence
> [Direct quote from transcript]

### Actionability
- **Timeframe:** [Urgent | Medium | Structural]
- **Next step:** [Concrete action if any]

### Careerspan Connection
[How this relates to the business]

### Memory Links
- Related positions: [...]
- Related knowledge: [...]
- Prior reflections: [...]
```

## Deliverable

Rewrite `/home/workspace/Prompts/Blocks/Reflection/R04_Market.prompt.md` as a **full analytical framework**, not a skeleton. Should be 150-250 lines including:

1. All 7 sections from base template, fully populated
2. The 5 analysis dimensions above
3. Complete worked example
4. Memory integration code snippet
5. Quality checklist

## Completion Criteria

- [ ] Prompt follows base template structure
- [ ] All 5 analysis dimensions documented
- [ ] Worked example is complete and realistic
- [ ] Memory integration section has working code pattern
- [ ] Output schema is clear and complete
- [ ] Prompt is 150+ lines (not a skeleton)

---

**When complete:** Run `python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker w03_r04_pilot`
