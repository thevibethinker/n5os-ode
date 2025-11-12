---
tool: true
description: Generate B08 intelligence block
tags:
  - meeting
  - intelligence
  - b08
---

# B08 - STAKEHOLDER_INTELLIGENCE Generation Prompt

You are generating a STAKEHOLDER_INTELLIGENCE block from a meeting transcript.

## Input
- Meeting transcript with timestamps
- Attendee list (focus on PRIMARY external stakeholder)
- Meeting metadata

## Output Structure

Generate exactly 5 sections:

---

## SECTION 1: FOUNDATIONAL PROFILE

**Company/Organization:** [Name]

**Product/Service:** [1-2 sentence description of what they do]

**Background:** [2-3 sentences on stakeholder's role, experience, career path]

**Current Focus:** [What they're working on right now - projects, initiatives, goals]

**Motivation:** [Why they took this meeting - what are they trying to accomplish?]

**Funding/Stage** *(if mentioned)*: [Funding round, revenue stage, growth stage]

**Key Challenges:** [2-3 specific problems they're facing - extract from pain points discussed]

**Standout Quote:** "[Direct quote that reveals personality, priorities, or perspective]"

---

## SECTION 2: WHAT RESONATED

Identify 3-5 moments where stakeholder showed genuine enthusiasm, strong agreement, or significant concern.

For each moment:

### [Topic/Theme]

**Quote:** "[Direct quote with timestamp]"

**Why it resonated:** [Analysis of tone shift, energy change, repeated emphasis, or follow-up questions that signal this matters to them]

**What it signals:** [Strategic interpretation - what does this reveal about their priorities, values, decision criteria, or pain points?]

---

Look for indicators:
- Tone changes: excitement, frustration, relief
- Verbal cues: "I love that", "This is exactly", "We've been struggling with"
- Repeated mentions across the conversation
- Detailed follow-up questions
- Personal stories or examples shared
- Hesitations or concerns raised

**Balance positives and negatives** - capture both what excites them AND what worries them.

---

## SECTION 3: DOMAIN AUTHORITY & SOURCE CREDIBILITY

Track topics where this stakeholder has credible knowledge based on their background and experience.

For each domain:

### [Topic/Domain]

**Authority Level:** ● ● ● ● ○ *(1-5 dots based on expertise)*

**Based on:** [Why they're credible - role, experience, direct involvement]

**Insights Provided:** [Bullet list of specific insights they shared in this domain]

**Source Type:**
- PRIMARY: Firsthand experience, direct involvement
- SECONDARY: Informed observer, indirect knowledge
- SPECULATIVE: Hypothesis or educated guess

**Validation Status:** *(update after B31 generation)*
- Unvalidated
- Partially validated (1-2 other sources)
- Validated (3+ sources)
- Contradicted by other sources

---

## SECTION 4: CRM INTEGRATION

**Auto-Generate For:**
- FOUNDER / INVESTOR / CUSTOMER / COMMUNITY / NETWORKING stakeholder types

**Skip For:**
- JOB_SEEKER (different workflow)

**Status:** Profile created at `Knowledge/crm/individuals/[name-slug].md`

**Enrichment Priority:**
- **HIGH**: Active deal/partnership discussions, time-sensitive opportunity, strong mutual fit
- **MEDIUM**: Warm contact, potential future collaboration, valuable network connection
- **LOW**: Networking conversation, passive relationship, long-term relationship building

**Next Actions:** [2-3 specific LinkedIn/research tasks]

Examples:
- Review [Name]'s LinkedIn for [specific info needed]
- Research [Company]'s recent [funding/product/hiring] announcements
- Map connections: Who in our network knows [Name] or works at [Company]?
- Check if [Company] is hiring for [role type] (indicator of pain point/priority)

---

## SECTION 5: HOWIE INTEGRATION

**Recommended Tags:** [LD-XXX] [GPT-X] [A-X]

**Tag Breakdown:**
- **LD (Lead Type):**
  - INV (Investor), NET (Networking), COM (Community), CUS (Customer), 
  - JOB (Job Seeker), PART (Partner), HIRE (Potential Hire), MEDIA (Media/Press)
  
- **GPT (Goal/Phase/Timeline):**
  - E (Early/Exploratory), M (Middle/Moving), C (Close/Critical)
  
- **A (Accommodation Level):**
  - 1 (Minimal - quick check-in OK)
  - 2 (Standard - normal meeting prep)
  - 3 (High - detailed prep needed)
  - 4 (Critical - extensive prep, high stakes)

**Rationale:** [1-2 sentences explaining why each tag based on conversation analysis]

**Priority:**
- **Critical**: Time-sensitive, high-value opportunity, active deal in motion
- **Important**: Strong potential, warm relationship, strategic value
- **Non-critical**: Long-term relationship, passive opportunity, informational

---

## Quality Standards

✅ **DO:**
- Extract SPECIFIC challenges, not generic problems
- Use direct quotes that reveal personality/priorities
- Distinguish between what excited them vs concerned them
- Rate domain authority based on actual experience (not assumed)
- Provide actionable enrichment tasks (specific research questions)
- Match Howie tags to conversation urgency and depth

❌ **DON'T:**
- Write surface-level profile without motivation/challenges
- List topics discussed without analyzing WHY they resonated
- Treat all stakeholders as equally credible on all topics
- Generic enrichment tasks: "Research company" (too vague)
- Wrong Howie tags (e.g., [A-4] for casual networking call)
- Miss concerns/hesitations (only capture positives)

## Example Quality Indicators

**HIGH QUALITY - What Resonated:**
### AI Learning & Development Path

**Quote:** "How do you learn about these design patterns? I've been trying to figure out how to go from beginner tutorials to actually building things." [14:32]

**Why it resonated:** Elaine asked this twice during the conversation and took notes when Vrijen mentioned specific YouTube channels. Her tone shifted from casual to focused - this is a real pain point for her learning journey.

**What it signals:** She's actively trying to level up her AI/ML skills and values practical learning resources over theoretical content. Positioned Vrijen as a credible mentor figure, which builds relationship capital and creates future touchpoint opportunities.

**LOW QUALITY:**
### AI Development

**Quote:** "That's interesting"

**Why it resonated:** She seemed interested in AI

**What it signals:** She likes AI

## Edge Cases

**Multiple stakeholders:** Focus on PRIMARY external stakeholder. If multiple equal-importance stakeholders, generate separate B08 for each.

**Job seeker conversation:** Generate B08 but SKIP Section 4 (CRM Integration) - job seekers follow different workflow.

**Internal meeting:** DO NOT generate B08 - this block is for external stakeholders only. Use B40 instead.

**Limited stakeholder background:** Use what's available from conversation. Mark sections as "Limited information - enrich via LinkedIn/research" where appropriate.
