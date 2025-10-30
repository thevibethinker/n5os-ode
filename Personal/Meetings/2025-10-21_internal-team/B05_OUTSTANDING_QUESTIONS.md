## OUTSTANDING_QUESTIONS

---
**Feedback**: - [ ] Useful
---

### 1. Can we build a "candidate quality ranker" that bypasses expensive per-user analysis?

**Owner:** Ilse (technical assessment)  
**Needed by:** Tomorrow's strategy meeting  
**Blocker type:** UNCLEAR_REQUIREMENT (unclear if this is technically feasible without AI hallucination/inconsistency)  
**Unblocking action:** Ilse explores options: cached nightly data, proxy signals (title progression, years of experience), AI resume assessment (with accuracy caveats)  
**Impact if delayed:** Can't pursue white-glove recruiting approach without ability to identify "top 50 candidates" efficiently  

**Technical constraints mentioned:**
- "AI is very inconsistent about" value judgments on humans
- Everyone using AI to "puff up their resume" makes quality assessment harder
- Current analysis costs 30-50¢ per vibe check
- Don't currently store vibe check scores (would need one-off analysis or new storage)

---

### 2. Do we pursue Tim as fractional salesperson/recruiter?

**Owner:** V (decision), Logan (input needed)  
**Needed by:** Within next week (Tim presumably available soon)  
**Blocker type:** NEEDS_DECISION (depends on strategic direction choice)  
**Unblocking action:** Tomorrow's strategy meeting must answer: (A) white-glove recruiting model, (B) employer portal focus, or (C) user acquisition focus?  
**Impact if delayed:** Lose potential sales capacity; V willing to personally fund 2-3 months ($10k "gamble") but only makes sense if aligned with strategy

**Context from meeting:**
- Tim has founder relationships
- V confident in candidate quality: "we have some killer candidates"
- Tim's view (per V): "placements are a pain in the balls" but "reliable pipeline of people" is "fish in a barrel"
- Ilse supportive if it means "finding and generating a pipeline" but skeptical of white-glove approach without broader strategy

---

### 3. Should we complete the employer portal build?

**Owner:** Team (collective decision)  
**Needed by:** Tomorrow meeting (impacts Rockel/Dani priorities)  
**Blocker type:** NEEDS_DECISION (strategic direction unclear)  
**Unblocking action:** Clarify whether new strategy is employer-focused (build portal) or candidate-volume-focused (deprioritize portal)  
**Impact if delayed:** Rockel/Dani spinning on wrong priorities; 2-3 months of build time may not align with 6-month runway

**Status:**
- Rockel has Figma sketch
- Estimated 2-3 months build time
- Hardest part: user access management (don't give employers full candidate data access)
- This was the direction while V was traveling, now potentially misaligned

---

### 4. What is our actual go-to-market motion?

**Owner:** V + Logan (GTM), Ilse (technical feasibility validation)  
**Needed by:** Tomorrow meeting (CRITICAL)  
**Blocker type:** NEEDS_DECISION (multiple incompatible options on table)  
**Unblocking action:** Tomorrow's meeting must choose ONE of:
- (A) Magic links to small startups ($100 or free for case studies)
- (B) White-glove recruiting service (Tim + candidate quality ranker)
- (C) VC subscription model (talent-on-tap for active funds)
- (D) Some sequenced combination (what comes first?)

**Impact if delayed:** 6 months runway with scattered execution = failure. Ilse explicitly warned against "doing a lot of things at once hoping one sticks."

---

### 5. How do we resolve the "high quality vs. high volume" tension?

**Owner:** V + Ilse (technical-strategic alignment)  
**Needed by:** Tomorrow meeting (CRITICAL)  
**Blocker type:** NEEDS_DECISION + UNCLEAR_REQUIREMENT  
**Unblocking action:** Explicit acknowledgment of tradeoff, decision on priority (quality or volume), realistic timeline if rebuild needed  
**Impact if delayed:** Continued strategic whiplash, technical foundation misaligned with business needs, team frustration

**Core tension:**
- **Ilse's position:** "I built exactly what you asked for" - high-rigor analysis for employer trust after Rewiring America feedback. Shifting to "cheaper, faster, worse" requires rebuild.
- **V's position:** "There's too much value being generated" - need user volume for acquisition story, can't afford expensive per-user analysis at scale.
- **Unspoken question:** Was the last 6 months of rigor-focused development a mistake, or is the pivot to volume a mistake?

**Possible paths (unresolved):**
1. Accept rebuild timeline, focus on small wins (magic links) while rebuilding for volume
2. Double down on quality, pursue white-glove recruiting where expensive analysis is the product
3. Two-tier approach: cheap pre-screening, expensive full analysis only for shortlisted candidates
4. Accept current product can't serve volume use case, focus on employer portal for smaller TAM

---

### 6. What do we tell the team (Dani, Rockel)?

**Owner:** V + Logan + Ilse (collective)  
**Needed by:** After tomorrow's internal alignment, before investor discussions  
**Blocker type:** DEPENDENCY (blocked on strategic direction decision)  
**Unblocking action:** Finalize strategy, agree on communication approach (transparency vs. gradual rollout)  
**Impact if delayed:** Team operating without context on company direction, potential morale issues, priorities misaligned

**What team needs to know:**
- Runway situation (covered for 3 months, then what?)
- Strategic pivot (if confirmed)
- Their role in next phase
- Vesting acceleration plan if company sells within a year
- Timeline and expectations

---

### 7. What's the actual ARR potential of different approaches?

**Owner:** V (market validation), Logan (brand/distribution validation)  
**Needed by:** Before investor discussions (need credible narrative)  
**Blocker type:** WAITING_ON_DATA (market testing required)  
**Unblocking action:** For each approach, define: (A) unit economics, (B) realistic volume assumptions, (C) implied ARR at 6 months, (D) what VCs would pay for in acquisition  
**Impact if delayed:** Can't build credible acquisition story without revenue/traction narrative

**V's assertions (need validation):**
- Magic links: $100/placement × ??? volume = ???
- VC subscriptions: "infinitely achievable" but what's actual close rate and ACV?
- White-glove recruiting: How many placements can Tim realistically close in 3-6 months?

**Ilse's point:** "There's theoretically no such thing as ARR in recruiting" - it's GMV, not recurring. VC subscription model is only true ARR.

---

### 8. Is the "stay alive for acquisition" strategy realistic?

**Owner:** V (investor relationships), Logan (brand/momentum building)  
**Needed by:** Next 2-4 weeks (validate with more VCs)  
**Blocker type:** WAITING_ON_DATA (need multiple VC confirmations)  
**Unblocking action:** V schedule calls with 3-5 VCs to validate "low power mode → acquisition" narrative; test whether 200 → 2000 users in 6 months at current quality would be acquisition-worthy  
**Impact if delayed:** Could be building toward exit that doesn't exist; VCs may have been polite but not serious about acquisition interest

**VCs' advice (per V):** "Stay alive, accrete users, keep retention strong, work towards acquisition" - but is this real interest or polite brush-off?

---

