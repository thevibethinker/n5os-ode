# B40 - INTERNAL_DECISIONS

**Meeting:** Vrijen x Ilse Strategic Pivot Discussion  
**Date:** 2025-10-21  
**Attendees:** Vrijen, Ilse

---

## Strategic Decisions

| ID | Decision | Type | Rationale | Related Tactical |
|----|----------|------|-----------|------------------|
| D1 | Pivot from VC-backable growth model to acquisition-focused low-power mode | Investment/Strategy | Sales momentum insufficient, investor feedback suggests "stay alive and accumulate value" path more viable than aggressive scaling. Two well-funded competitors validate market but also compress opportunity window. | T1, T2, T3, T4 |
| D2 | Downsize team to skeleton crew: V+Logan full-time, Ilse part-time (through Feb cushion) | Operations/Hiring | Extend runway to 6 months for founders while covering team through 3-month obligation. Reduces burn from ~$50k+/month to sustainable lean operation. | T1, T9 |
| D3 | Target exit/acquisition within 6-12 month window | Investment/Strategy | Market consolidation trend ("most career platforms getting acquired"), need to exit before window closes. Founders emotionally ready for exit over continued grinding. | T10 |
| D4 | Shift primary ICP from enterprises to small companies ($100-200 placements) | GTM/Sales | Remove pressure to generate $50k revenue by EOY. Enables experimentation, case study building, and user accumulation without revenue constraints. Small companies easier to close, provide learning, build proof points. | T5, T6, T8 |
| D5 | Deprioritize sophisticated analysis depth in favor of cheaper, faster matching | Product | Current 30-50¢+ per match analysis with 18-22hr processing time for 50 jobs x 2000 users is economically/operationally unsustainable. Hiring managers need "worth a screen?" signal, not exhaustive analysis. | T5, T11, T12 |

**TENSION:** D5 contradicts 6+ months of product strategy emphasizing rigor, transparency, equity. Ilse built system around "never show bullshit candidates" standard after Rewiring America feedback. V now proposing shift to "good enough" approach.

---

## Tactical Decisions

| ID | Decision | Type | Rationale | Supports Strategic |
|----|----------|------|-----------|-------------------|
| T1 | Cover existing team through 3-month obligation, accelerate vesting if sale within 12 months | Hiring/Operations | Ethical treatment of team, honor commitments. Vesting acceleration incentivizes team support for acquisition. | D2 |
| T2 | Break retirement account (V personal funds) to extend founder runway if needed | Investment | Demonstrates commitment to survival strategy. Removes immediate cash constraint. | D1, D2 |
| T3 | Approach existing investors for bridge/wrap-up funding (not new raise) | Investment | Frame as "cover us at reduced spend, we deliver exit outcome" - clearer ask than growth capital raise. | D1 |
| T4 | Focus brand-building, community embedding, grassroots distribution (Logan's strength) | GTM/Marketing | Plays to founder strengths vs. enterprise sales grinding. Drives user accumulation without sales cycle friction. | D1, D4 |
| T5 | Implement magic link distribution for $100-200 per placement | GTM/Sales | Low-friction monetization, proves concept, builds case studies. Small companies post magic link → filter 10 strong candidates vs. 300 applicants. | D4, D5 |
| T6 | Offer free service to seed-stage startups for case studies and user acquisition | GTM/Marketing | Removes sales friction, builds proof points, drives organic candidate growth through employer distribution. | D4 |
| T7 | Prioritize tech cost reduction and scalability over feature richness | Product | Must support higher user volumes (200→2000/month) at lower unit costs to make lean operation viable. | D5 |
| T8 | Build employer portal for magic link distribution and candidate review | Product | Enables self-service model for small companies. Estimated 2-3 months build time (user access management is hardest part). | D4 |
| T9 | Rochel and Danny: 2 months paid to build "self-sustaining" product, then placement assistance | Hiring | Maximizes team contribution during notice period, uses Careerspan to place own team (validates product), ethical off-ramp. | D2 |
| T10 | Begin acquisition target outreach in parallel with lean operation execution | GTM/Strategy | Test acquisition interest early, understand valuation expectations, create urgency if unexpected traction emerges. | D3 |
| T11 | Explore simpler candidate quality assessment (title + job history 80/20 approach) | Product | V hypothesis: "Higher grade of person drawn to Careerspan" + resume screening may be sufficient for "worth talking to" signal. | D5 |
| T12 | Deprioritize full narrative analysis, vibe check, story verification depth | Product | These features cost 30-50¢+ per analysis and require 18-22hr batch processing. Unsustainable at 2000 users x 50+ jobs/week scale. | D5 |

---

## Holistic Pushes

### Skeleton Crew Acquisition Strategy

**Strategic Rationale:** [D1] [D3] Exit while preserving founder wellbeing and team ethics. Market window closing due to consolidation. VC path exhausting and low-probability. Lean operation extends runway, reduces pressure, enables experimentation toward acquisition.

**Tactical Execution Path:**
1. [T1] [T9] Communicate team transition ethically, honor 3-month commitment, accelerate vesting if sale
2. [T2] [T3] Secure bridge funding (personal + existing investors) for 6-month founder runway
3. [T4] [T6] Shift from enterprise sales to community-driven user acquisition (free for startups, brand-building)
4. [T5] [T8] Build self-service employer portal for magic link distribution at $100-200/placement
5. [T7] [T11] [T12] Reduce product complexity and unit costs to support 10x user growth
6. [T10] Begin acquisition outreach, prepare for 6-12 month exit timeline

**Dependencies:** 
- Three-way V+Logan+Ilse strategic alignment conversation (CRITICAL - scheduled for tomorrow AM)
- Ilse technical feasibility assessment for cost reduction [B41]
- Employer portal build timeline and scope definition [B41]
- Team communication plan and transition logistics [B41]

**Success Criteria:** 
- Runway extended to 6+ months for founders
- User base grows from 200→2000/month
- 7-8 placements/month at $3k = $21-24k revenue (lifestyle business threshold)
- OR acquisition offer at acceptable valuation within 12 months

**MAJOR RISK:** Ilse expressed fundamental concerns about strategic coherence, product-market fit, and technical feasibility. This push requires full co-founder alignment, which does not currently exist.

---

## Resolved Tactical Debates

### Debate: Can we generate "top 50 candidates" list for white-glove recruiting?

**Options Considered:**
- Option A: AI-based quality scoring across all users (role + seniority + sector filtering)
- Option B: Manual screening based on title + job history heuristics
- Option C: Build new assessment system optimized for "worth a screen?" question

**Resolution:** [UNRESOLVED - moved to B47.T1]

**Context:** V wants list of top candidates to enable white-glove placement service (potentially with Tim as hired recruiter). Ilse raised concerns:
1. Current system doesn't store historical vibe check scores
2. AI quality assessment is "wishy washy" and inconsistent
3. Would require significant new build (Option C) for accuracy
4. Resume inflation makes assessment unreliable
5. Conflicts with 2-person maintainability constraint

**Status:** Punted to three-way conversation. V acknowledged validity of concerns but still sees value in exploring simpler heuristics.

---

### Debate: Magic links vs. sophisticated product - which direction?

**Options Considered:**
- Option A: Refocus on employer portal (Ilse + Logan's recent direction)
- Option B: Simplify to magic link distribution with minimal analysis
- Option C: Hybrid - employer portal WITH simplified analysis backend

**Resolution:** [TENTATIVE - Option C with unknowns]

**Rationale:** V and Ilse converged on employer portal being valuable, but disagree on:
- Analysis depth required (V: simpler/cheaper, Ilse: maintain rigor)
- Build timeline (Ilse: 2-3 months, V: needs faster for runway)
- Unit economics at scale (unresolved tension)

**Settled Date:** Not settled - requires Logan input and three-way strategic session

---

## Interrelationships & Tensions

### Core Tension: Product Rigor vs. Economic Viability

**The Problem:** 
- [D5] proposes deprioritizing sophisticated analysis built over 6 months
- Ilse's system designed around "never show bullshit candidates" (post-Rewiring America feedback)
- Current analysis: 30-50¢ per match, 18-22hr processing for 50 jobs x 2000 users
- V's new direction: "good enough" matching to reduce costs and enable scale

**Ilse's Perspective:** 
> "If you had said months ago we want cheaper/faster/worse, we could have built differently. But we've been building for rigor. That's not our product anymore - that's a totally separate product requiring new tech and new UI."

**V's Counter:**
> "Hiring managers just need 'is this person worth a screen?' - lower burden of proof than we've been optimizing for."

**Unresolved:** [B47.Q1] Can current product architecture serve skeleton crew model, or does strategic pivot require product rebuild?

---

### Supporting Tension: Sales-Driven vs. Community-Driven Distribution

**The Problem:**
- V proposing community-driven free distribution to accumulate users
- Simultaneously proposing white-glove recruiting service (Tim-led) to generate immediate revenue
- Ilse questioning: "Which is it? You mentioned 3-4 different approaches in this call."

**Analysis:** V exploring multiple hedges simultaneously:
1. Free magic links for startups → user acquisition
2. $100-200 placement fees → case studies + learning
3. White-glove recruiting service → immediate revenue
4. VC subscription model → potential ARR

This reflects strategic uncertainty, not coherent plan.

**Unresolved:** [B47.Q2] What is the PRIMARY business model for skeleton crew phase?

---

### Founder Emotional State

**V's Position:**
- Emotionally ready for exit: "Logan and I would like an exit. We'd like everyone to walk away with at least something that makes them feel good."
- Willing to self-fund: "I'll fucking cover Tim salary if needed for 2-3 months"
- Exhausted with VC path: Repeated references to "low power mode," "just stay alive," "less pressure"

**Ilse's Position:**
- Frustrated by strategic whiplash: "Why weren't we doing [magic links for small companies] months ago?"
- Protective of product integrity: "Have you read the narrative sections lately? They're fucking amazing dudes."
- Concerned about founder decision quality: "You're trying to brainstorm... you've mentioned 3-4 different possible ways. That's a mistake for startups."

**Implication:** This conversation revealed NOT strategic alignment but strategic misalignment that needs resolution before execution.

---

**Generated:** 2025-10-21T15:54:24Z
