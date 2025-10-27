# Executive Memo Style Guide

**Block ID:** B82  
**Domain:** external_professional  
**Voice Profile:** `file 'N5/prefs/communication/voice.md'`  
**Auto-Approve Threshold:** 0 blocks (always requires review)

---

## Purpose

Formal internal communication for team/stakeholders on decisions, strategy, or important updates. Clear, concise, action-oriented. Used for communicating with team, advisors, or investors when formality and clarity are essential.

---

## Structure

**Standard format:**
- Subject line: Specific and actionable
- TL;DR: One paragraph (2-3 sentences) with bottom line
- Context: What prompted this memo
- Analysis/Details: Key information, organized in sections
- Decision/Recommendation: What we're doing
- Next Steps: Who does what by when
- (Optional) Appendix: Supporting data, links, details

**Length:** 300-1000 words (concise enough to read in 5 minutes)

---

## Tone & Voice

**Core Characteristics:**
- **Clear:** No ambiguity on decisions or next steps
- **Concise:** Respect reader's time
- **Structured:** Easy to skim, find what you need
- **Decisive:** Clear on what we're doing (not endless options)
- **Professional:** Formal but not stiff
- **Action-oriented:** Always clear on next steps

**Avoid:**
- Corporate jargon ("synergize," "leverage," "circle back")
- Hedging on decisions ("maybe we should consider...")
- Burying the lead (put decision up front)
- Lengthy exposition without clear recommendation
- Passive voice when accountability matters

---

## Lexicon

**Memo-Specific:**
- Decision: Clear choice made
- Recommendation: What should be done
- Context: Background information
- Rationale: Why this decision
- Next steps: Actions with owners and dates
- TL;DR: Bottom line up front

**Action Language:**
- "We will..." (not "we might")
- "X owns Y by [date]"
- "Decision: [clear statement]"
- "Recommendation: [specific action]"

---

## Templates

### Template 1: Decision Memo
```
**Subject:** Decision: [Specific topic]

**TL;DR:**
[Decision made in 1-2 sentences. Key implications in 1 sentence.]

---

**Context:**
[What prompted this decision. Keep to 2-3 paragraphs.]

**Options Considered:**
1. Option A: [Brief description] — [Key trade-off]
2. Option B: [Brief description] — [Key trade-off]
3. Option C: [Brief description] — [Key trade-off]

**Decision:**
We will pursue [Option X].

**Rationale:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Implications:**
- [Impact on team/product/timeline]
- [What changes]
- [What stays the same]

**Next Steps:**
- [Person] will [action] by [date]
- [Person] will [action] by [date]
- [Person] will [action] by [date]

**Questions/Concerns:**
[How to raise feedback or concerns]
```

### Template 2: Update Memo
```
**Subject:** Update: [Specific topic]

**TL;DR:**
[Current status. Key update. What it means for readers.]

---

**What's Changed:**
[Specific update with context]

**Why This Matters:**
[Implications for team/company]

**What's Next:**
- [Milestone 1] — [Date]
- [Milestone 2] — [Date]
- [Milestone 3] — [Date]

**What We Need:**
[Specific asks of readers, if any]

**Questions:**
[How to follow up]
```

---

## Transformation Guidance

**Raw → Refined:**
- Stream of consciousness → Structured memo with sections
- "I'm thinking we should..." → "Decision: We will..."
- Background heavy → TL;DR up front, background in middle
- Vague next steps → Owner + action + date
- Multiple decisions buried → One clear decision per memo

**Key Transforms:**
1. **Front-load the decision:** TL;DR with bottom line first
2. **Make ownership explicit:** "V will X by Friday" not "someone should X"
3. **Remove hedging:** "We will" not "we should consider"
4. **Add structure:** Use headers, bullets, clear sections
5. **Timebox:** Include dates for actions and milestones

---

## Examples

### Example 1: Product Decision

**Raw Input:**
```
Been thinking about whether to build the timeline feature or the AI synthesis 
feature first. Both are important. Timeline is more visual and easier to 
understand but synthesis is the unique value prop. Timeline might attract 
more users initially but synthesis is harder to copy. We probably need both 
eventually but have to pick one for Q1. Leaning toward timeline because it's 
more concrete.
```

**Refined Output:**
```
**Subject:** Decision: Q1 Product Roadmap — Timeline Feature First

**TL;DR:**
We will build the Timeline feature in Q1, followed by AI Synthesis in Q2. 
Timeline provides clear user value and visual differentiation while we refine 
the AI models for synthesis. Target launch: February 15.

---

**Context:**

Two features are critical for differentiating Careerspan from resume builders:
1. **Timeline view:** Visual career progression (12 roles over 15 years)
2. **AI Synthesis:** Help users identify narrative patterns and through-lines

Both are essential long-term. We must choose one for Q1 given current team 
capacity (1 engineer, 30 hrs/week).

**Options Considered:**

**Option A: Build Timeline first**
- Pros: Visual impact, easier to explain, clear user value
- Cons: Less differentiated (some competitors have timelines)
- Effort: 6 weeks

**Option B: Build AI Synthesis first**
- Pros: Unique value prop, harder to copy
- Cons: Requires more AI model refinement, less immediately tangible
- Effort: 8-10 weeks (uncertain)

**Option C: Build both in parallel (MVP versions)**
- Pros: Faster to market with both features
- Cons: Neither feature will be excellent; technical debt likely
- Effort: 10+ weeks

**Decision:**

We will build **Timeline first** (Q1), then **AI Synthesis** (Q2).

**Rationale:**

1. **Certainty:** Timeline scope is well-defined (6 weeks). Synthesis has unknowns in AI quality.
2. **Foundation:** Timeline UI provides structure for displaying synthesis insights later.
3. **User value:** Visual timeline has immediate value; users can start using it day 1.
4. **Feedback loop:** Timeline gives us data on how users view their careers, informing synthesis prompts.

We optimize for shipping excellent features sequentially over mediocre features in parallel.

**Implications:**

- Marketing messaging for Q1 focuses on "See your career progression visually"
- AI synthesis language in messaging becomes "Coming Q2"
- Engineering focus: Timeline feature + infrastructure for future AI integration
- User research priority: How do users interact with timeline? What insights do they extract manually?

**Next Steps:**

- **V** will finalize Timeline feature spec by Nov 1
- **[Engineer]** will begin Timeline implementation Nov 4
- **V** will draft AI Synthesis requirements (for Q2) by Nov 15
- **Team** will review progress at weekly standups, target launch Feb 15

**Questions/Feedback:**

Reply to this thread or ping me directly. Decision is final but open to surfacing concerns about execution.

---

**Appendix: Timeline Feature Scope**

MVP includes:
- Visual timeline of roles (title, company, dates)
- Expandable cards with role details
- Color coding by industry
- Export as image

Deferred to v2:
- Skill tagging
- Automatic gap detection
- Comparative timelines (your path vs others)
```

---

## QA Checklist

Before sending:
- [ ] TL;DR captures decision/update in 2-3 sentences
- [ ] Subject line is specific (not "Team Update")
- [ ] Decision or recommendation is crystal clear
- [ ] Context is concise (3 paragraphs or less)
- [ ] Next steps have owners and dates
- [ ] Structure is skimmable (headers, bullets)
- [ ] No hedging on decisions ("we will" not "we should consider")
- [ ] Professional but not stiff
- [ ] Can be read in under 5 minutes
- [ ] Answers: What changed? Why? What's next?

---

**Version:** 1.0  
**Created:** 2025-10-26
