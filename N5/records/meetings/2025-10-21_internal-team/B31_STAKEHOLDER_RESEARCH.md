## STAKEHOLDER_RESEARCH

---
**Feedback**: - [ ] Useful
---

**Perspective:** Speaking as Careerspan co-founders (technical lead + non-technical founder) in career tech space

---

### 1. Career tech companies always pivot to hiring/sourcing

**Evidence:** "Basically every single one has made a shift towards hiring unless they were already focused on networking... or they've in some way shape or form moved towards sourcing or sourcing adjacent stuff. Those two seem to be the only directions that folks drive towards. Which is why career tech is such a barren wasteland."

**Why it matters:** This is industry pattern recognition from V's years of conversations in the space. It suggests that consumer-focused career products (helping individuals with career decisions) don't generate sufficient monetization, forcing pivots to B2B (employers paying for hiring/sourcing). Careerspan is now at the same inflection point. However, V's framing ("barren wasteland") implies these pivots often fail - companies become undifferentiated hiring platforms competing with established players. The trap: pivot to hiring (necessary for revenue) but lose differentiation (fatal in crowded market).

**Signal strength:** ● ● ● ○ ○ (observed pattern but outcome unclear)  
**Category:** Market Dynamics & Competition  
**Domain credibility:** ● ● ● ○ ○ (V has extensive career tech conversations but mostly as observer, not operator)

**Source Credibility:**
- **Stakeholder:** Vrijen → Link to B08
- **Relevant experience:** 4 years in career tech space, decade as career coach, extensive founder/VC network
- **Source type:** SECONDARY (observed pattern from others' experiences, not personal operation)
- **Firsthand?** No - pattern recognition from conversations, not from running multiple career tech companies
- **Weight justification:** Should weight moderately - good pattern recognition, but V hasn't personally operated in this space long enough to validate why these pivots fail

---

### 2. High-quality AI analysis is expensive at scale (30-50¢ per match, 18-22 hours for 50 jobs × 2000 users)

**Evidence:** "To run, let's say, 50 jobs against 2,000 users... could easily take at least 22 hours. Probably more because of the high failure rate that we experience with OpenAI lately... And that should give you a sense of the amount of money that that would cost."

**Why it matters:** This is the core economic constraint killing consumer-scale matching products. Quality matching requires deep analysis; deep analysis requires compute; compute doesn't scale economically. This creates fundamental tension: candidates want comprehensive analysis (Ilse's "fucking amazing narratives"), but economics require shallow screening. No amount of optimization solves this if you're using LLMs for deep reasoning. Implications: (1) Can't compete on volume without sacrificing quality, (2) Must find use case where expensive analysis is the product (white-glove recruiting?), (3) Or must rebuild for cheaper heuristics (6-month setback).

**Signal strength:** ● ● ● ● ○ (specific, actionable, explains why AI matching is hard)  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ● (Ilse is PRIMARY source - built this system, knows exact costs)

**Source Credibility:**
- **Stakeholder:** Ilse → Link to B08
- **Relevant experience:** Senior engineer, built Careerspan's matching system from scratch, deep LLM experience
- **Source type:** PRIMARY (firsthand operational experience building and running this system)
- **Firsthand?** Yes - Ilse wrote every line of this code, monitors the costs daily, deals with OpenAI rate limits personally
- **Weight justification:** Should weight very heavily - this is not speculation, this is operational reality from the person who built and maintains the system

---

### 3. Product decisions 6 months ago dictate strategic options today (path dependency is brutal)

**Evidence:** "Months ago, if you had said, oh, no, we do want to start shifting more towards cheaper, faster, but worse... I would have been able to reassess." And: "Multiple times over the past few months, I have brought up the topic of... I could make it cheaper if we can make it worse. And the response was always a resounding no."

**Why it matters:** Startups assume they can pivot quickly, but technical foundations create path dependency. Ilse spent 6 months building for employer trust (rigorous analysis, no hallucinations, provable accuracy) because that was the explicit requirement after Rewiring America feedback. Now strategy requires volume over quality, but can't easily rebuild. This isn't just Careerspan - it's a general principle about technical debt and strategic flexibility. Early decisions (what to optimize for) constrain later options (how fast you can pivot). Implication: When making technical decisions, explicitly consider: "What strategies does this lock us into? What pivots does this make harder?"

**Signal strength:** ● ● ● ● ○ (highly specific, applicable beyond Careerspan)  
**Category:** Product Strategy  
**Domain credibility:** ● ● ● ● ● (Ilse is PRIMARY source on technical path dependency)

**Source Credibility:**
- **Stakeholder:** Ilse → Link to B08
- **Relevant experience:** Experienced engineer who has built multiple products, understands rebuild costs
- **Source type:** PRIMARY (lived this path dependency personally)
- **Firsthand?** Yes - Ilse made the technical decisions, built the rigorous system, and now faces rebuild constraints
- **Weight justification:** Should weight very heavily - this is painful firsthand lesson in path dependency from someone who executed the original decisions correctly based on requirements given

---

### 4. Startup scatter is a failure mode ("doing a lot of things at once hoping one sticks")

**Evidence:** "It is a mistake to try to do a lot of things at once hoping that one sticks, especially when you're not certain that one of them will be successful enough." And: "Even on this call, you are trying to brainstorm and you've mentioned three or four different possible ways."

**Why it matters:** When startups face existential pressure, instinct is to explore multiple paths simultaneously. Feels like hedging risk, but actually guarantees failure - none get enough focus to validate properly, team fragments attention, runway burns faster. Better: pick one, execute fully for 4-6 weeks, decide based on results. Ilse is pattern-matching to startup death spiral and calling it out explicitly. This is engineer pragmatism vs. founder optimism. V wants to "keep options open"; Ilse knows that kills companies. Applicable insight: at 6 months runway, optionality is not your friend - conviction and focus are.

**Signal strength:** ● ● ● ● ○ (widely applicable startup wisdom, directly relevant to current situation)  
**Category:** GTM & Distribution  
**Domain credibility:** ● ● ● ○ ○ (Ilse has startup experience but as engineer, not operator)

**Source Credibility:**
- **Stakeholder:** Ilse → Link to B08
- **Relevant experience:** Has worked at/with multiple startups, seen this pattern before
- **Source type:** SECONDARY (observed pattern, not from running strategy at multiple startups)
- **Firsthand?** Partial - experienced as team member, but hasn't personally been in founder seat making these calls
- **Weight justification:** Should weight moderately-high - this is well-known startup wisdom, and Ilse is correctly applying it to current situation, but it's not based on personal experience leading strategy through this specific failure mode

---

### 5. Building case studies and learning from small customers beats optimizing for revenue too early

**Evidence:** "We can turn those into case studies. We can learn from them. We can learn what's working, what's not. And we can say, hey, we've helped these companies... If even one of them gets funding, if we did a good job, they're going to want to use us again." And: "If we can get any startups using us, we're organically building up 100 users here, 200 users... But we're also learning along the way."

**Why it matters:** Pre-product-market-fit companies should optimize for learning, not revenue. Give product away to qualified users who will give feedback and serve as case studies. Revenue will come later when you've validated the value prop. But founders under runway pressure (like V) optimize for revenue too early, which ironically makes them less attractive to customers (desperate energy) and slows learning (only talking to people who will pay, not best-fit users). Ilse is advocating for classic lean startup approach: get users, learn fast, build credibility, then monetize. This is especially relevant for B2B - case studies and logos matter more than early revenue.

**Signal strength:** ● ● ● ○ ○ (sound advice, though not novel)  
**Category:** GTM & Distribution  
**Domain credibility:** ● ● ● ○ ○ (Ilse understands product development, less experienced in GTM)

**Source Credibility:**
- **Stakeholder:** Ilse → Link to B08
- **Relevant experience:** Has seen successful and unsuccessful product launches as engineer/team member
- **Source type:** SECONDARY (applying startup wisdom from observation, not from personal GTM leadership)
- **Firsthand?** No - Ilse hasn't personally run GTM or made these tradeoffs as decision-maker
- **Weight justification:** Should weight moderately - this is good startup advice (echoes Paul Graham, Eric Ries), and Ilse is correctly applying it, but it's not based on personal experience executing GTM strategy

---

