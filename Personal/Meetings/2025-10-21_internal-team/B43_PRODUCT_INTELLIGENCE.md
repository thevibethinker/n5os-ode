# B43 - PRODUCT_INTELLIGENCE

**Meeting:** Vrijen x Ilse Strategic Pivot Discussion  
**Date:** 2025-10-21

---

## Product Strategy Tensions

### Current Product Architecture

**Designed For:** High-rigor candidate verification and matching
- **Analysis Depth:** Three-tier system (preferences check → vibe check → full analysis)
- **Quality Standard:** "Never show bullshit candidates" (post-Rewiring America feedback)
- **Core Features:** 
  - Story-based verification (narrative summaries, fill-in-the-gaps, accomplishment extraction)
  - Multi-layered preferences matching
  - Comprehensive vibe checks with rationale
  - Full analysis with strategic recommendations
- **Unit Economics:** 30-50¢+ per candidate per job analysis
- **Processing Time:** 18-22 hours for 50 jobs x 2000 users (OpenAI rate limits, high failure rates)

**Ilse's Design Philosophy (6 months of work):**
> "The entire goal for the past six months has been transparency and equity. Making sure we give accurate representation, accurate advice, and the same level of advice to employers. I have brought up multiple times: I could make it cheaper if we make it worse. And the response was always a resounding no. We wanted this level of rigor."

---

### Proposed Strategic Shift

**V's New Direction:** [B40.D5] Deprioritize sophisticated analysis for cheaper, faster matching

**Rationale:**
- Hiring managers need "is this person worth a screen?" not exhaustive analysis
- Current costs unsustainable at target scale (200 → 2000 users/month)
- Lower burden of proof sufficient for initial screening
- Can provide deep analysis AFTER screening, not BEFORE

**V's Framing:**
> "They essentially need to see promising looking candidates. When Careerspan says someone is promising, I subjectively also find them to be promising. That is a much lower burden of proof than getting the job."

---

### The Core Technical Conflict

**Ilse's Response:**
> "That is not our product. That is a totally separate product that would require a totally separate user facing UI and totally new technology. And I can't build an entire new app."

**Three Blocking Issues:**

1. **Architecture Mismatch:** Current system optimized for depth, not speed/cost
   - Can't simply "turn down" analysis quality - would require rebuild
   - UI/UX designed around showing comprehensive matches, not simple screening
   - Data structures don't support historical vibe check queries (scores not stored)

2. **Timeline Constraint:** [B40.T8] Employer portal estimated 2-3 months
   - User access management = hardest technical challenge
   - Can't simultaneously rebuild matching logic AND build new portal
   - Skeleton crew (2 people) can't support new product development + maintenance

3. **Validation Time:** "If we had eight months and a Danny, we would be able to experiment and build cheaper solution from scratch."
   - Current constraints: ~2 months team runway, then V+Logan+part-time Ilse only
   - Not enough time to validate new approach before team transitions off

---

## Roadmap Conflicts

### Ilse + Logan's Recent Direction (Last 2 Weeks)

**Focus:** Employer-side product development
- New marketing page emphasizing employer value prop (completed)
- Employer portal designs (in progress with Rochel)
- Self-service job posting + magic link distribution
- Candidate review interface with user access management

**Strategic Bet:** Focus on monetizing employers directly, not just placement fees

**Progress:** 
- Marketing page live (removed promises about "matches in 15 minutes")
- Figma sketches for employer portal completed
- Had NOT discussed with V until today

---

### V's Direction (This Conversation)

**Primary:** [B40.T4] Community-driven candidate acquisition + low-cost distribution
**Secondary:** [B40.T5] Magic link distribution for $100-200 placements
**Tertiary:** [B47.Q3] White-glove recruiting service with Tim
**Quaternary:** VC subscription model for talent-on-tap

**Ilse's Observation:**
> "On this call, you've mentioned 3-4 different possible ways. Things that we can do to get this company to survive. That's a mistake for startups. You need to pick one."

---

## Technical Constraints on Proposed Directions

### Constraint 1: Cost Reduction Limits

**V's Ask:** Support 2000 users x 50+ jobs/week at lower unit cost

**Ilse's Analysis:**
- Reducing precheck pass rate from 80% → 20% only cuts processing from 22hrs → 11hrs
- Still requires pounding OpenAI API constantly (rate limits, failure rates, cost)
- Cached data approach (using nightly job check data) could help but has limitations:
  - Not all users included (only those with recent activity)
  - Not going far back in time (data retention limits)
  - Less accurate than fresh analysis

**Bottom Line:** "I'm not sure there is any way to make the current app's methodology economically viable or time viable to be supporting thousands of users and hundreds of jobs per week."

---

### Constraint 2: "Top Candidates" Feature Infeasibility

**V's Request:** Generate list of 50 most impressive/marketable candidates for white-glove recruiting

**Technical Blockers:**
1. **No stored scores:** System doesn't save historical vibe check ratings (would require rebuild)
2. **AI inconsistency:** "Wishy washy" value judgments unreliable at scale
3. **Resume inflation:** "If they're smart, everyone is using AI to fluff things up. Everyone is going to look fantastic."
4. **Segmentation complexity:** Need to filter by role + seniority + sector for accurate "top" assessment
5. **Rebuild requirement:** Would need new assessment system purpose-built for "worth talking to" signal

**Ilse's Alternative:** 
> "Honestly, I don't think that we could do much better than just using the resume to assess, hey, is this person probably a good candidate?"

**Implication:** V's white-glove recruiting idea may require starting from resumes, not leveraging Careerspan's analysis advantage.

---

### Constraint 3: User Management = "Hardest Thing"

**For Employer Portal:** [B40.T8]
- Don't want to give employers full access to user profiles (privacy, user experience)
- Need role-based permissions, data redaction, controlled access patterns
- "User access management" is the technical bottleneck (not UI or job posting logic)

**Timeline:** Ilse estimates 2-3 months even with simplified design

**Risk:** If skeleton crew needs this feature operational, 2-3 month timeline overlaps with team transition period (Danny/Rochel off by ~Dec 31)

---

## Open Product Questions

**From Ilse's Perspective:**

1. **What IS the product for skeleton crew?**
   - V wants user accumulation + distribution
   - But current product optimized for employer-pays-for-quality model
   - These require different architectures

2. **Can we preserve ANY analysis advantage?**
   - Ilse's narrative summaries, story verification, vibe checks are "fucking amazing"
   - But too expensive at scale
   - Is there 20% of the value at 20% of the cost?

3. **What does "self-sustaining product" mean?**
   - [B40.T9] Danny and Rochel tasked with building "self-sustaining" features
   - But no concrete definition provided
   - What features? What level of automation? What maintenance burden?

---

## Positive Product Assets (Ilse's Pride Points)

Despite tensions, Ilse highlighted current product strengths:

**Narrative Sections:**
> "Have you read or seen the narrative sections lately? They're fucking amazing dudes. They're so fucking intense."

**Verification Depth:**
> "The fact that this knows so much about someone. The fact that this was all by design, right? This was all to make sure, hey, there's no hallucination, we could prove everything."

**Story Intelligence:**
> "We learn about what tools, responsibilities they did, we learn about their thought process. Maybe we're lucky we get a few additional quantitative or qualitative outcomes and metrics."

**Implication:** Ilse emotionally invested in product quality. Strategic shift toward "good enough" feels like abandoning 6 months of careful work.

---

## Related Decisions

**Strategic:** [B40.D5] Deprioritize analysis depth for cost/speed  
**Tactical:** [B40.T7] Reduce costs + increase scalability  
**Tactical:** [B40.T8] Build employer portal (2-3 month timeline)  
**Tactical:** [B40.T11] Explore simpler 80/20 candidate assessment  
**Tactical:** [B40.T12] Deprioritize narrative analysis, vibe check depth  

**Open Debates:** [B47.Q1] [B47.T1] [B47.T2]

---

**Generated:** 2025-10-21T15:54:24Z
