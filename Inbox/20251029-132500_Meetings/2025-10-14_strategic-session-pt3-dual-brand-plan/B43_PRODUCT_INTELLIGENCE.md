## PRODUCT_INTELLIGENCE

---
**Feedback**: - [ ] Useful
---

### Product Vision & Architecture

#### Core Product Concept (Refined)
**Careerspan = Passive Hiring Network for Planners**
- **What It Is**: Self-updating professional profile platform that connects passive job seekers with hiring managers building future pipelines
- **What It's NOT**: Job board, resume database, recruiter SaaS tool
- **Key Innovation**: Story-based profiles + LLM matching + passive candidate focus
- **Target User**: "People who care...people who give a shit about being better...the planners"

#### Three-Tier Product Strategy

**Tier 1: Free Platform (Careerspan.com)**
- **User-Facing Value Props**:
  1. Job delivery: "10 jobs you're actually a good fit for" (vs. "slaving over LinkedIn")
  2. Career visibility: "Hiring managers are building passive pipelines from Careerspan"
  3. Network effects: "Jobs current and future" ticker showing activity
- **B2C Focused Messaging**: 100% candidate-side messaging, minimal employer visibility
- **Status**: Put on "ice" - maintain and grow, but don't over-invest in new features

**Tier 2: Careerspan Select (Premium Service)**
- **Model**: High-touch placement service for top candidates
- **Product**: V & Logan as personal career agents
- **Selection Criteria**: High story completion + strong target role match scores
- **Service**:
  - Career coaching
  - Active job hunting on candidate's behalf
  - Direct introductions to hiring managers
  - Negotiation support
- **Revenue**: $2k per placement
- **Key Constraint**: Candidate exclusivity (can't go around Careerspan to employer)

**Tier 3: V&L LLC Services (Separate Brand)**
- **Custom AI Implementations**: V builds Zo-based productivity systems for execs ($5k+)
- **Career Coaching at Scale**: Logan's content/courses leveraging Careerspan placement learnings
- **Synergy**: Elite clients hire from Careerspan; Careerspan users buy V&L services

---

### Critical Product Builds (Next 90 Days)

#### Priority 1: Cheaper Job Delivery System
- **Owner**: Ilsa
- **Problem**: Current job delivery too expensive to scale
- **Goal**: 10x or 100x volume reduction in cost per job delivered
- **Approach**: 
  - Remove "Elsa's bullshit filter" (over-optimization)
  - Bulk licensing from cheaper sources
  - Optimize matching algorithm for speed over perfection
- **Success Metric**: Can afford to send 10 jobs/week to 100k users

#### Priority 2: Employer-Side Job Submission (Minimal Viable)
- **Owner**: Ilsa (with V & Logan requirements)
- **Scope**: Dead simple interface
  - Voice memo or text box: "Describe the role"
  - Careerspan processes and anonymizes
  - System sends JD into matching pipeline
- **User Experience**: "Submit your job and Logan/Vrijen will be in touch"
- **Email Cadence**: Weekly digest of matched candidates (also anonymous)
- **Status**: Intentionally minimal - "We don't prioritize reactive job seekers"

#### Priority 3: Matching & Notification System
- **Owner**: Logan + Ilsa
- **Component A: Candidate Scoring**
  - Cross-reference target roles with story content
  - Generate "Careerspan Select" candidate pool
  - Surface to Logan for manual review
- **Component B: Job-to-Candidate Matching**
  - LLM-based semantic matching (not keyword)
  - Notification system: Email + in-app
- **Component C: Candidate-to-Job Matching**
  - V's scalable system: Feed candidate data into Zo
  - Auto-generate personalized outreach to hiring managers
  - "Here's why [Candidate X] is perfect for your role"

---

### Product Principles (Newly Clarified)

#### Principle 1: "Put Career span on Ice"
- **Meaning**: Maintain and grow, but stop over-building
- **Rationale**: "Every mechanism we have to fill the balloon with value also lets air out"
- **Implication**: Focus on user growth and engagement metrics, not feature expansion
- **Key Quote**: "We change the dynamic by you and me just fending for ourselves. The product is built."

#### Principle 2: "Let the Balloon Fill"
- **Meaning**: Set up conditions for organic growth, then get out of the way
- **Tactics**:
  - Make job delivery cheap enough to sustain
  - Build minimal employer-side submission
  - Create viral loops (job sharing, recruiter donations)
  - Drive traffic via content
- **Key Quote**: "We set up the chicken area, set up the egg area, and then we just Yap and let both sides fill themselves"

#### Principle 3: "B2C Messaging Only"
- **Decision**: Website and all public messaging is 100% candidate-focused
- **Rationale**: "Makes everything fucking simpler...we should have just listened to our [gut]"
- **Employer-Side**: Hidden, network-only, word-of-mouth distribution
- **Key Quote**: "I could not bring myself to talk about the benefit for employers...there's no way to thread that needle with the brand we've built"

#### Principle 4: "Data Quality Over Volume"
- **Thesis**: Fresh, story-based profiles > 10x more resume databases
- **Moat**: Incentive system keeps profiles current (gamification + job matching)
- **Comparison**: "Teal has 10x the users but all they have is a shitty, outdated resume"

---

### Product Gaps & Build Priorities

#### Gap 1: No Placement Track Record
- **Impact**: Can't prove matching works
- **Mitigation**: Manual placements (Careerspan Select) prove concept while platform scales
- **Timeline**: Need first 2 placements (Danny, Rockwell) by Nov 2025

#### Gap 2: Viral Job-Sharing Loop Unproven
- **Concept**: Users share jobs with each other, hiring managers post directly
- **Risk**: "Chicken and egg...we haven't tried yet"
- **Mitigation**: V's hiring manager network (20-30 people) seeds supply side

#### Gap 3: Employer-Side UI Doesn't Exist
- **Current State**: No way for hiring managers to submit jobs or view matches
- **Build**: Minimal interface - just submission + weekly email digest
- **Timeline**: Ilsa to build in Month 2 (Nov 2025)

#### Gap 4: Expensive Job Delivery
- **Current Cost**: Too high to support 100k user goal
- **Blocker**: "Elsa's bullshit filter" + premium data sources
- **Fix**: Ilsa's priority task (Month 1)

---

### Product Metrics & Success Criteria

#### North Star Metrics (For Exit to Jack & Jill)
1. **Users**: 100k by Jan 1, 2026 (currently ~10k → need 10x growth)
2. **Usage**: Story completion rate + job interaction rate
3. **Network Value**: Number of hiring managers + jobs submitted
4. **Placement Evidence**: Demonstrated hires facilitated by platform

**Key Insight**: "All we need is that matching is happening on Careerspan...we just need evidence...not necessarily case studies"

#### Operational Metrics (For Sustainability)
1. **Cost per Job Delivered**: Target <$0.10/job (currently much higher)
2. **Candidate Quality**: % of candidates scoring high on target role match
3. **Hiring Manager Engagement**: % who submit jobs, % who review matches
4. **Lenza Revenue**: $ per candidate application (target $20+)

---

### Technical Architecture Insights

#### AI/LLM Infrastructure
- **Current**: Expensive AI inference costs
- **Goal**: Optimize costs while maintaining quality
- **V's Research**: Claude Haiku 4.5 released - "as good as 4.5 in coding, but at 1/3 cost, 2x speed"
- **Opportunity**: Migrate to cheaper models for matching workloads

#### Zo Integration (V's Custom AI Product)
- **Use Case 1**: V's personal productivity system
- **Use Case 2**: Scalable candidate outreach tool
  - Feed Careerspan candidate data
  - Generate personalized cold emails to hiring managers
  - "Here's why [X] is perfect for your role"
- **Use Case 3**: Customer product for executives ($5k implementation)
- **Technical Note**: Can run local LLMs on Zo (512 GB memory)

---

### Product Roadmap (Deliberately Minimal)

**Month 1-2 (Oct-Nov 2025): Foundation**
- [ ] Cheaper job delivery system (Ilsa)
- [ ] Careerspan Select candidate scoring (Ilsa + Logan)
- [ ] Employer job submission UI (Ilsa - minimal scope)
- [ ] V's scalable outreach system (V + Zo)

**Month 3-6 (Dec 2025 - Mar 2026): Scale**
- [ ] Viral job-sharing loop (if user demand emerges)
- [ ] Anonymous candidate matching UI for employers
- [ ] Recruiter "donation" system (if validated)
- [ ] Lenza integration optimization

**Month 7-12 (Apr-Oct 2026): Exit Prep**
- [ ] Data cleanup for acquisition
- [ ] Case study documentation
- [ ] Platform stability/maintenance mode
- [ ] Handoff documentation for acquirer

**Deliberate Non-Priorities:**
- Resume builder (not our model)
- Application tracking (not our focus)
- Recruiter CRM (not our customer)
- Advanced analytics/dashboard (nice-to-have, not need-to-have)

---

### Product Philosophy: "The Awkward Middle"

**Key Thesis**: "We're in the interregnum...the interstitial stuff...the old age has ended but the new age has yet to truly begin"

**Implication for Product**:
- AI isn't good enough for fully automated matching
- Humans still needed for trust-building and quality control
- Hybrid model (platform + services) is correct strategy for next 3-5 years
- "Just letting people find people and see what emerges" is valid approach

**Key Quote**: "The more we try to take gas from the balloon, the more that diminishes. So what I'm saying is just briefly, while we're already just keeping the product on ice, let's just let people find people and see what emerges"

---

### Product Risk Mitigation

**Risk 1: Platform Doesn't Facilitate Matches**
- **Mitigation**: Careerspan Select proves model works manually first

**Risk 2: Too Expensive to Operate at Scale**
- **Mitigation**: Ilsa's cost optimization + Lenza revenue + cheaper AI models

**Risk 3: Hiring Managers Don't Engage**
- **Mitigation**: V's personal network seeds initial supply (20-30 hiring managers)

**Risk 4: Users Don't Keep Profiles Fresh**
- **Mitigation**: Job delivery incentive + gamification + placement success stories

**Risk 5: Can't Prove Value to Acquirer**
- **Mitigation**: User growth + engagement metrics + Danny/Rockwell case studies + hiring manager testimonials
