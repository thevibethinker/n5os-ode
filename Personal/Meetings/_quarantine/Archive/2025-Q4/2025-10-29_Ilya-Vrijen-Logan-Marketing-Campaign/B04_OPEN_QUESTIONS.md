---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# B04_OPEN_QUESTIONS

## Outstanding Questions with Blocker Identification

### Q1: What is the actual trial structure for employers?
**Owner:** Ilya (with input from Vrijen)  
**Needed by:** Before first customer trial (target: within 1 week for testing)  
**Blocker type:** UNCLEAR_REQUIREMENT  
**Status:** PARTIALLY RESOLVED - Multiple options identified, decision pending

**Details:**
- Three proposed models discussed:
  - **Time-based:** Fixed period (e.g., 14 days)
  - **Volume-based:** First 100 candidates scanned (Vrijen's suggestion)
  - **Hybrid:** Combination of time + milestone triggers
  
**Why it matters:** Trial structure determines:
- Psychological framing for employers (perceived risk, commitment level)
- Pricing positioning (free vs. freemium)
- Marketing messaging (e.g., "unlimited for 14 days" vs. "scan your first 100 candidates free")
- Conversion probability (different structures convert different ICPs)

**Unblocking action:** 
1. Run projected financials for each trial model (cost of supporting one customer for X duration)
2. Design A/B test with first 3-5 customers to measure conversion by trial type
3. Schedule decision call with Vrijen + Logan + Ilya by [DATE TBD]

**Impact if delayed:** 
- Can't finalize marketing copy
- Can't project unit economics for first 10 customers
- Delays customer onboarding clarity

---

### Q2: Can Careerspan support 500+ applicants (from marketing push) applying within 48-72 hours without system degradation?
**Owner:** Ilse Funkhouser (technical), Ilya (usage scenario)  
**Needed by:** Before campaign launch (critical blocker)  
**Blocker type:** NEEDS_DECISION (technical infrastructure + cost decision)  
**Status:** HIGH RISK - Identified but not resolved

**Details:**
- Current constraint: OpenAI API rate limits + story analysis delays (17 min per 5-story candidate)
- Scenario: If one customer is promised results in 48 hours with 50 qualified applicants, and 10 customers come through campaign simultaneously = potential system collapse
- Ilse's concern: "Our app is not well situated to have a viral moment that involves applying to jobs"
- Possible mitigations discussed:
  - Require minimum 1 story before applying (adds friction, selects for high-agency users) - 1 hour build time
  - Get OpenAI priority queue access (requires paid commitment to OpenAI)
  - Pre-load story analysis (background processing)

**Why it matters:** 
- If system crashes under demand, marketing loses credibility with first customers
- Directly impacts whether Ilya can safely promise "results by Friday"
- Affects campaign aggressiveness + customer targeting volume

**Unblocking action:**
1. Get quote from OpenAI for priority queue tier + monthly cost
2. Decision: Should we (a) add story requirement, (b) pay for priority queue, (c) both, or (d) cap campaign volume?
3. Load test current system with realistic campaign scenario (aim for 500 simultaneous candidates over 48 hrs)
4. Document system SLA (e.g., "candidate analysis takes 10-20 min" as baseline promise)

**Impact if delayed:**
- Campaign scope becomes uncertain
- First customer experience could be poor
- Marketing overpromises and operations under-delivers

---

### Q3: What is the systematic process for pulling candidate supply ("turning on the tap") for brand new jobs with zero relevant candidates in the system?
**Owner:** Vrijen + Logan (execution), Ilya (validation)  
**Needed by:** Before campaign (needed to make credible promises)  
**Blocker type:** UNCLEAR_REQUIREMENT + DEPENDENCY  
**Status:** PARTIALLY RESOLVED - Tactics identified, not systematized

**Details:**
- Current ad-hoc levers:
  - LinkedIn posting (Vrijen's account, Logan's account, Careerspan company account)
  - Community outreach (Ben Lang's job list, internal communities where they have credibility)
  - Email lists (past candidates, community newsletters)
  - Network amplification (ask influencers to share)
  
- Insight from Ilya: "You both have really strong networks and people who will go to bat for you"
- Challenge: Currently feels random + inconsistent; needs to be repeatable at scale

- Vrijen acknowledged: "We're very good at speaking candidly...We're very good at like getting visibility in front of really high quality candidates...where we have struggled is to convert that ability...into bringing those folks into the system"

**Why it matters:**
- This is the supply-side lever that enables the entire marketplace
- Determines whether hiring managers see compelling candidate pools quickly (and therefore stay engaged)
- Directly affects trial-to-paid conversion

**Unblocking action:**
1. Document the exact playbook for candidate sourcing (order of outreach channels, message templates, expected response rates)
2. Assign clear owner for each customer (e.g., Vrijen handles LinkedIn + community, Logan handles amplification)
3. Test with first customer: Put out job on Monday, track how many qualified candidates arrive by Wed/Thu
4. Measure: What % of candidates come from each channel? Which channels drive highest engagement quality?

**Impact if delayed:**
- First customer gets weak candidate pool → poor trial experience → no conversion
- Ilya can't reliably promise "50 great applicants" → marketing messaging becomes vague

---

### Q4: What messaging/incentive structure actually drives candidates to tell their stories (not just apply with resume)?
**Owner:** Ilya (messaging), Vrijen (validation from founder feedback)  
**Needed by:** Before campaign onboarding (needed to set candidate expectations)  
**Blocker type:** UNCLEAR_REQUIREMENT + NEEDS_DECISION  
**Status:** UNRESOLVED - Multiple hypotheses, not tested

**Details:**
- Ilya's "carrot and stick" framework:
  - **Carrot (emotional):** "We're finally listening to you. Not your resume. We're listening to you."  
  - **Stick (requirement):** Could be hard requirement (3 stories minimum) or soft nudge (showing that top candidates have stories)
  
- Vrijen's concern: Founders worry about fakery/people making up stories. Hard requirement might signal "we don't trust you" and attract people willing to game the system.

- Alternative: "Unrevealed preferences" messaging—allow employers to silently screen for qualities without making it explicit requirement

- Jeff (Google recruiter, per Vrijen): Stories are a signal. One candidate with 4 stories + 5 vibe checks gets picked over 3-resume candidates. This is the social proof narrative.

- Ilya's proposed video: <30 sec intro showing candidates why they should tell stories (emotional narrative, not requirement)

**Why it matters:**
- If candidates don't tell stories, employer sees minimal differentiation → product value collapses
- Sets tone for user experience (friction vs. flow)
- Affects conversion rate of applicants → job completion

**Unblocking action:**
1. Create 2-3 narrative variations (emotional pitch vs. requirement-based vs. social proof)
2. A/B test with first 100 candidates (track % who tell stories under each condition)
3. Measure: conversion to job application, story completion rate, employer conversion to paid
4. Finalize messaging based on which version drives highest-quality story completion

**Impact if delayed:**
- Candidates bypass storytelling step → employers see weak filtering → low conversion
- Candidate experience feels confusing or gimmicky

---

### Q5: Should we require a minimum 1 story before allowing job application (hard friction gate)?
**Owner:** Ilse (technical), Logan (design philosophy), Ilya (business impact)  
**Needed by:** Before campaign (determines UX + system load)  
**Blocker type:** NEEDS_DECISION  
**Status:** UNRESOLVED - Tradeoffs identified, decision pending

**Details:**
- **Pro (from Logan):** Selects for high-agency people. Signals "we are better at filtering." Natural friction that's also a business moat. Can implement in <1 hour.

- **Con (from Vrijen):** Founders worry this looks like we don't trust them. Attractive people willing to hack the system will just make up stories. Optional requirement more elegant—shows who's serious without being restrictive.

- **Middle ground (Ilse):** Add visible indicator "top candidates have [X stories]" showing social proof without hard requirement. Creates nudge, not barrier.

- **System constraint:** If minimum story required, Ilse can easily handle viral volume. If not required, system may collapse under apply-without-story spam.

**Why it matters:**
- Directly affects story completion rate (constraint on system + quality signal)
- Affects conversion funnel (does minimum story requirement cost us applicants?)
- UX messaging (hard requirement vs. soft nudge feels very different)

**Unblocking action:**
1. Draft both UX flows with messaging (hard gate + soft nudge)
2. Test with first 200 candidates: Show half one flow, half the other, measure story completion + applicant quality
3. Measure employer satisfaction: Do they notice quality difference?
4. Decision: Launch with whichever drives better metrics (completion rate × quality × volume)

**Impact if delayed:**
- UX feels incomplete or contradictory
- System fragility under campaign success becomes liability

---

### Q6: What is the realistic timeline and effort required to get McKinsey portfolio companies (250+ companies, 400 jobs) activated?
**Owner:** Vrijen (relationship), Ilya (execution planning)  
**Needed by:** Within 2 weeks (partnership opportunity window)  
**Blocker type:** DEPENDENCY (contract signature pending)  
**Status:** PARTIALLY RESOLVED - Verbal agreement, contract pending

**Details:**
- Status: Vrijen has informal agreement from McKinsey partner (as of Nov 15). Waiting for formal signature.
- Scope: 250 companies, ~400 open jobs currently on McKinsey board that they "frankly don't even want to maintain"
- Careerspan value prop: Take these jobs off their board and surface them to better candidates
- Potential advantage: Ethical path to "run candidates against these jobs" without permission issues (clients have given McKinsey implicit consent)

**Why it matters:**
- This is the supply-side jackpot: 400 real, current job descriptions to create proof points
- Changes the entire campaign narrative: "We've got you access to Zoc Doc, [other names], etc."
- Solves cold-start problem (employer uploads job, we have pre-existing candidates matching existing McKinsey jobs)

**Unblocking action:**
1. Get contract signed (Vrijen + partner responsibility)
2. Once signed: Build import pipeline (time estimate: TBD, depends on McKinsey data format)
3. Identify 10-20 "marquee" companies to highlight in marketing (Zoc Doc, etc.)
4. Test: Can we surface existing Careerspan candidates against these 400 jobs? (matching quality test)

**Impact if delayed:**
- First campaign lacks compelling job portfolio for employers to see
- Have to build supply from zero (slower, riskier)
- Insta Lily + other early customers feel like one-off sales instead of systematic offering

---

### Q7: What is our specific ICP prioritization for first 10 customers—should we pursue McKinsey portfolio companies (broad, systematic) or Insta Lily / hair-on-fire founders (targeted, high-touch)?
**Owner:** Ilya (strategic direction), Vrijen + Logan (execution)  
**Needed by:** This week (determines campaign targeting + messaging)  
**Blocker type:** NEEDS_DECISION (strategic)  
**Status:** UNRESOLVED - Both appear viable, tradeoffs not quantified

**Details:**
- **Option A: McKinsey Portfolio (Systematic)**
  - Pro: Scalable, built-in supply of 400 jobs, repeatable process, multiple companies
  - Con: May require customization per company, relationship dependent on McKinsey partner
  
- **Option B: Hair-On-Fire Founders (Targeted)**
  - Pro: High pain, high motivation, compel logo potential (Insta Lily raised Series A, Zapier, Shopify)
  - Con: High-touch, one-off customization, niche verticals may not be repeatable
  
- Ilya's guidance: "Embrace the persona that just shows up" + "First of all, any client at this stage is good" but "be mindful...try not to spend too much time on custom needs"

- The tension: Insta Lily is compelling but risky (high-customization rabbit hole). McKinsey portfolio is boring but safe (systematic, scalable).

**Why it matters:**
- Determines initial marketing spend (SMG ads vs. founder networking), sales motions (product-led vs. consultative), product roadmap (custom features vs. core platform)
- First 3 customers set precedent for all future customers
- If we over-customize for Insta Lily, we'll do it for everyone and die

**Unblocking action:**
1. Run financial model: What's the cost of first customer acquisition under each strategy?
2. Draft ICP profiles for both paths (firmographics, pain points, buying process)
3. Ilya's recommendation: Get first customer under Path A (McKinsey) + first customer under Path B (Insta Lily) simultaneously—test both, learn which converts + retains better
4. After 3 customers, decide where to double down

**Impact if delayed:**
- Marketing spend becomes unfocused
- Sales strategy contradictory (broad ads + founder outreach pull in different directions)
- Risk of building product for wrong persona

---

## Summary: Critical Path Items

**Immediate (this week):**
- [ ] Decide trial structure (Q1)
- [ ] Resolve ICP prioritization (Q7)
- [ ] Finalize story-telling messaging framework (Q4)
- [ ] Get McKinsey contract signed (Q6)

**Before campaign launch:**
- [ ] Load test system under 500-applicant scenario (Q2)
- [ ] Document candidate sourcing playbook (Q3)
- [ ] Decide story requirement approach (Q5)
- [ ] Validate first customer scenario end-to-end with test run


