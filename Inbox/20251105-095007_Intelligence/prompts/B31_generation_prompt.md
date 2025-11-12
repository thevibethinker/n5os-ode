---
tool: true
description: Generate B31 intelligence block
tags:
  - meeting
  - intelligence
  - b31
---

# B31 - STAKEHOLDER_RESEARCH Generation Prompt

You are generating a STAKEHOLDER_RESEARCH block from a meeting transcript.

## Core Principle

Extract 3-5 ESSENTIAL insights about **THE WORLD** from this conversation - not about the stakeholder themselves (that's B08), but about:
- How their organization/industry works
- Decision criteria and buying patterns
- Market dynamics and competitive landscape
- Stakeholder type pain points and priorities
- Unwritten rules and insider perspectives

**Focus:** NON-OBVIOUS information you can't easily Google.

## Input
- Meeting transcript
- Stakeholder background (from B08 if available)
- Meeting context

## Output Structure

For each insight (3-5 total):

---

## [INSIGHT TITLE]
*Multi-line OK - be clear, not artificially terse*

**Evidence:**
> "[Direct quote from transcript with timestamp]"

**Why it matters:** [ONE SENTENCE combining implication + strategic value for Careerspan]

**Signal Strength:** ● ● ● ○ ○

**Category:** [Tag from list below]

### Source Credibility

**Stakeholder:** [Name] → *Link to B08_STAKEHOLDER_INTELLIGENCE*

**Relevant Experience:** [What makes them knowledgeable on THIS specific topic - role, background, direct involvement]

**Source Type:**
- **PRIMARY**: Firsthand experience (they did this/saw this/experienced this directly)
- **SECONDARY**: Informed observer (they know people who did this/heard about it)
- **SPECULATIVE**: Hypothesis or educated guess based on experience

**Firsthand?:** Yes/No [Evidence from transcript supporting firsthand vs hearsay]

**Weight Justification:** [Why weight this insight heavily or discount it - based on source credibility, specificity, and verifiability]

---

## Signal Strength Rating Guide

Rate 1-5 dots based on:

- **Specificity**: Vague trend vs concrete example with numbers/names/dates
- **Actionability**: Can we use this immediately?
- **Surprise Value**: Is this non-obvious? Does it challenge assumptions?
- **Verification**: How many sources confirm this?

**● ○ ○ ○ ○** = Generic/obvious insight ("hiring is hard")
**● ● ○ ○ ○** = Somewhat specific ("hiring engineers in SF is expensive")  
**● ● ● ○ ○** = Specific, actionable, not obvious ("hiring engineers in SF costs $200K+ and takes 4-6 months")
**● ● ● ● ○** = Highly specific, actionable, surprising, verified by 1-2 other sources
**● ● ● ● ●** = Game-changing insight verified by 3+ stakeholders

## Category Tags

Choose from:
- **[Hiring Manager Pain Points]** - Challenges hiring managers face in recruiting/hiring
- **[Community Owner Pain Points]** - Challenges running/growing/monetizing communities
- **[Founder Pain Points]** - Challenges founders face in specific domains
- **[Investor Decision Criteria]** - How investors evaluate deals, what drives yes/no
- **[Product Strategy]** - Product development approaches, feature priorities, roadmap thinking
- **[GTM/Sales Strategy]** - Go-to-market approaches, sales processes, customer acquisition
- **[Market Dynamics]** - Competitive landscape, market shifts, industry trends
- **[Organizational Behavior]** - How companies actually work internally
- **[Decision-Making Process]** - How stakeholder type makes buying/partnership decisions
- **[Technical Landscape]** - Technology choices, architecture, tooling decisions
- **[Regulatory/Compliance]** - Legal, compliance, regulatory considerations

## Extraction Rules

### What to Extract:

1. **Organization Intel:**
   - Internal processes, decision-making hierarchies
   - Budget allocation priorities
   - Tool/vendor evaluation criteria
   - Pain points with current solutions
   - Reasons past solutions failed

2. **Industry/Market Intel:**
   - Emerging trends stakeholder is seeing firsthand
   - Competitive dynamics and gaps
   - Pricing/economic models
   - Unwritten rules in their industry
   - Regulatory or compliance considerations

3. **Stakeholder Type Patterns:**
   - What criteria do [hiring managers/investors/founders] use to evaluate [candidates/deals/vendors]?
   - What objections come up repeatedly?
   - What signals credibility vs raises red flags?
   - What's the typical buying/decision process?

### What NOT to Extract:

❌ **About the stakeholder** (that's B08):
- Their background, experience, or career
- What they're currently working on
- Their personal motivations or goals

❌ **Generic/Obvious** insights:
- "Hiring is challenging" (everyone knows this)
- "Companies want to save money" (not useful)
- "AI is becoming important" (obvious trend)

❌ **Surface-level** information:
- Basic facts you can Google
- Public information from their website
- Generic industry knowledge

## Quality Standards

✅ **DO:**
- Focus on non-obvious insider perspectives
- Use direct quotes as evidence
- Rate signal strength honestly (most insights = 2-3 dots)
- Distinguish PRIMARY (firsthand) from SECONDARY (hearsay) sources
- Extract implications for Careerspan strategy
- Keep to 3-5 ESSENTIAL insights (resist bloat)

❌ **DON'T:**
- Extract obvious/generic insights
- Skip direct evidence (quotes)
- Treat all sources as equally credible
- Inflate signal strength (be realistic)
- Extract more than 5 insights (focus on quality over quantity)
- Confuse stakeholder intelligence (B08) with research (B31)

## Example Quality Comparison

### HIGH QUALITY

---

## Community Platforms Often Fail Because Founders Build Features Members Don't Actually Want Engagement With

**Evidence:**
> "We launched a bunch of gamification features - points, badges, leaderboards - because every community platform has them. But our most engaged members literally never touched them. They just wanted better search and the ability to bookmark discussions. Took us 9 months to realize we were building the wrong things." [23:14]

**Why it matters:** Validates Careerspan's hypothesis that job seeker communities need practical utility (job matching, skill development) over engagement theater - direct evidence from failed experiment saves months of product development.

**Signal Strength:** ● ● ● ● ○

**Category:** [Product Strategy]

### Source Credibility

**Stakeholder:** Elaine P → *See B08_STAKEHOLDER_INTELLIGENCE*

**Relevant Experience:** Founded and scaled a 50K+ member professional community platform over 4 years; directly responsible for product decisions and member engagement metrics.

**Source Type:** PRIMARY

**Firsthand?:** Yes - "We launched...", "our members...", "Took us 9 months..." - direct involvement in building, launching, and learning from this feature set.

**Weight Justification:** High weight (4 dots) - This is firsthand product learning from someone who built a directly comparable platform. Specific numbers (9 months wasted, 50K members), concrete feature examples, and clear cause-effect relationship make this actionable.

---

### LOW QUALITY

---

## Communities Are Hard To Build

**Evidence:**
> "Yeah, communities are challenging"

**Why it matters:** It's difficult to grow communities

**Signal Strength:** ● ● ● ● ●

**Category:** [Community Owner Pain Points]

### Source Credibility

**Stakeholder:** Elaine P

**Relevant Experience:** Runs a community

**Source Type:** PRIMARY

**Firsthand?:** Yes

**Weight Justification:** She said so

---

## Edge Cases

**No non-obvious insights:** If conversation was entirely surface-level or social:
- Generate file with header
- Note: "No extractable strategic insights - conversation remained social/exploratory without depth on organization, industry, or stakeholder type patterns"

**Insights contradict each other:** Track both, note the contradiction, flag for validation with additional sources

**Low-credibility source:** Still extract if interesting, but rate honestly in Source Credibility section and lower signal strength accordingly

**Multiple stakeholder types:** Tag insights with multiple categories if applicable, but each insight should have ONE primary category

## Testing Your Output

Ask yourself:
1. **Would this insight surprise someone familiar with the industry?** (If no → too obvious)
2. **Can I act on this immediately?** (If no → too vague)
3. **Could I Google this in 30 seconds?** (If yes → not valuable)
4. **Is this about the WORLD or about the PERSON?** (Person → belongs in B08, not B31)
5. **Would I bet $100 this is true?** (If no → lower signal strength)
