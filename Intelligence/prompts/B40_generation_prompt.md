# B40 - INTERNAL_DECISIONS Generation Prompt

You are generating an INTERNAL_DECISIONS block from an internal team meeting transcript.

## Input
- Internal meeting transcript (team standups, planning meetings, strategy sessions)
- Participant list (all internal team members)
- Meeting metadata

## Output Structure

Generate exactly 4 sections:

---

**Date:** [Meeting date]  
**Duration:** [If clear from transcript]  
**Participants:** [List all team members by name]

---

## SECTION 1: KEY UPDATES

Group by team member - what did each person share?

### [Person Name]

- [Bullet point summary of their update - both tactical and strategic]
- [What they accomplished, what they're working on, what they're blocked on]
- [Include specific details: customer names, project milestones, numbers/metrics]

### [Next Person]

- [Continue for each participant]

**Extraction Rules:**
- One subsection per person who spoke
- 2-5 bullets per person depending on depth of update
- Capture BOTH tactical (what they did) AND strategic (what it means)
- Include specific details when mentioned (names, numbers, dates)
- Note absences if mentioned: "[Name] was absent - [reason if given]"

---

## SECTION 2: TEAM DYNAMICS

Analyze the human/cultural elements of the meeting:

**Atmosphere:**
- Was this casual or formal? Tense or relaxed? Rushed or leisurely?
- Tone indicators: humor, banter, seriousness, stress

**Morale Indicators:**
- Signs of enthusiasm, excitement, momentum
- Signs of concern, frustration, fatigue
- Energy level of the team
- Expressions of support or celebration

**Working Relationships:**
- Collaboration patterns (who's working with whom?)
- Conflicts or disagreements (if any)
- Support and encouragement between team members
- Decision-making dynamics (collaborative vs top-down)

**Remote Work Observations** *(if applicable)*:
- How distributed work is affecting team interaction
- Technical issues or communication challenges
- Work-life balance signals

---

## SECTION 3: BUSINESS MOMENTUM

Analyze what this meeting reveals about company progress and challenges:

### Positive Signals

- Deal progression, customer wins, product milestones achieved
- Fundraising or partnership developments
- Revenue growth, user growth, or engagement improvements
- Team capability increases (new hires, skill development)
- External validation (press, awards, recognition)
- Problem-solving breakthroughs

### Watch Points

- Blockers or delays mentioned
- Concerns raised by team members
- Resource constraints (time, money, people)
- Customer/product issues flagged
- External challenges (competitive, market, regulatory)
- Timeline pressures or deadline risks

**Balance:** Present both sides - this isn't just a highlights reel or a problem list.

---

## SECTION 4: STRATEGIC CONTEXT

1-2 paragraphs synthesizing what this meeting reveals about the company's current state.

Address:
- **Phase:** What phase is the company in? (fundraising, product development, scaling, pivoting, launching, etc.)
- **Key Themes:** What patterns emerge across multiple people's updates?
- **Strategic Implications:** What do the updates collectively signal about company direction, priorities, or health?
- **Momentum:** Is the company accelerating, plateauing, or facing headwinds?
- **Culture:** What does this meeting reveal about how the team works together and makes decisions?

**Purpose:** Give future you (or your team) the ability to look back and quickly understand "where were we in October 2025?" - not just what happened, but what it meant.

---

## Quality Standards

✅ **DO:**
- Capture specific details (customer names, deal sizes, dates, metrics)
- Balance facts with interpretation
- Note both progress AND challenges
- Assess team morale and dynamics (not just business updates)
- Provide strategic interpretation of what updates collectively mean
- Target ~500-600 words total

❌ **DON'T:**
- Transcribe the meeting chronologically
- Miss team morale/culture signals
- Only report positives (or only problems)
- Write vague summaries: "Team is doing well"
- Skip strategic interpretation
- Exceed 800 words

## Example Quality Indicators

**HIGH QUALITY - Key Updates:**

### Vrijen

- Had meeting with Rack House VC (founded by first go-to-market person at Uber who invented surge pricing)
- Discussion about VCs paying retainer for talent network approach
- Particularly promising conversation - may move forward as early as start of next week
- Multiple VC conversations ongoing with potential developments coming in "a few more days"
- V unable to share full details yet, wants things to convert first before announcing

*(Specific names, specific details, strategic significance noted, captures both momentum and intentional ambiguity)*

**LOW QUALITY:**

### Vrijen

- Had some VC meetings
- Going well
- Will update later

*(Vague, missing details, no strategic interpretation)*

---

**HIGH QUALITY - Strategic Context:**

This standup captures the team during an active fundraising/partnership phase. V is in heavy VC meeting mode with multiple conversations progressing simultaneously. The talent network approach appears to be resonating with investors as a distinct value proposition. Team morale is strong despite limited visibility into deal details - Rochel's comment after a month away ("I missed y'all") signals healthy team cohesion even in remote setup.

**LOW QUALITY:**

The team is doing well and making progress on various projects.

---

## Edge Cases

**Skip/Skip Daily:** If daily standup was skipped or someone didn't show:
- Note in header: "Meeting skipped - [reason if known]"
- OR: "[Name] absent - [reason]" under Key Updates

**Highly confidential discussion:** Capture strategic themes without revealing specific confidential details if that's appropriate. Note: "[Confidential discussion - strategic implications captured without specifics]"

**Debate/disagreement:** Capture both perspectives fairly in Key Updates, note team decision-making process in Team Dynamics, interpret implications in Strategic Context

**No meeting (async update):** If this is an async written update rather than synchronous meeting:
- Note in header: "Async update - [date range]"
- Adjust Team Dynamics section to focus on collaboration patterns visible in async updates

## Testing Your Output

Ask yourself:
1. **If I read this 6 months from now, would I understand where the company was?**
2. **Did I capture both business progress AND team dynamics?**
3. **Is Strategic Context actually interpretive or just a summary?**
4. **Did I balance positives and challenges?**
5. **Are there specific details or is everything vague?**
