## PRODUCT_INTELLIGENCE

---
**Feedback**: - [ ] Useful
---

### Product Strategy

**Core Strategic Shift: Verification-First Positioning**
- **From:** Job matching platform for communities
- **To:** Verification + filtering solution for hiring managers
- **Rationale:** Leverages unique Careerspan strength (story-based consistency checking) while addressing acute market pain (fake/bullshit candidates)
- **Competitive Moat:** "We would have a very unique edge in [verification], largely with folks that have used Careerspan for a while already"
- **Integration Path:** Stories create verification data set that grows with usage [B40.D2]

**Verification as Filtering Mechanism**
- **Value Prop:** "Selecting for high effort individuals" - spam candidates won't spend time on Careerspan
- **Dual Purpose:** Less fake candidates + less bullshit candidates (time wasters)
- **Market Positioning:** "Filter Plus" not ATS replacement - integrates with existing systems [B40.T5]
- **Strategic Insight:** High-effort barrier (stories) is feature not bug - naturally deters spam applications

**Two-Stage Verification Approach**
- **Stage 1 (Pre-screen):** Magic link → resume upload → two stories → confidence score
  - Pre-filter before hiring manager/recruiter phone screen
  - Can be white-labeled for companies wanting internal branding
  - Ilse's consistency methodology: story-to-story check + role-appropriate language/experience validation [B40.T6]
- **Stage 2 (Post-interview, optional):** Interview transcript verification
  - Compare interview responses against Careerspan stories for consistency
  - Red flag detection, not "catching people out" - ethical positioning
  - Secondary validation layer for high-stakes hires
- **Flexibility:** "Two points at which people could slot this in" - multiple entry points increase adoption paths [B40.T4]

### Technical Approach

**Manual → Automated Transition**
- **Current State:** Ilse doing manual verification similar to job matching process
- **Proof-of-Concept:** "She's like, I can fucking do this manually, similar to how we've been doing it with job matching"
- **Scaling Path:** Build automation on proven manual methodology
- **Advantage:** Can sell to companies NOW with manual process while building automation
- **Timeline:** Allows immediate customer acquisition while engineering catches up

**ATS Integration Architecture** [B40.T5]
- **Initial Research:** API integration and SKUs exploratory research completed
- **Assessment:** "Wouldn't be insurmountable" - feasible integration path exists
- **Value Prop:** "They would just be paying for our data architecture and the workflow of taking, of ingesting this information and then piping it back into their existing system"
- **Integration Model:** Data layer approach - ingest candidate info, return verification score/insights to ATS
- **Strategic Advantage:** If we solve integration, "we will have proven that...we are valuable enough to overcome this very big-ass hurdle"

**Screening Interview Optimization** (Future iteration)
- **Concept:** Design screening interview to "maximally amplify the likelihood of catching someone out"
- **Value Prop:** "Limit the time wasted to the least valuable member of the team" (recruiter/TA, not hiring manager/founder)
- **Workflow:** Share screening interview transcript → Careerspan verification → gate-keep hiring manager time
- **Quantifiable Value:** "Sharing two stories will with an X percent of likelihood ensure that you are not wasting the hiring manager's time"
- **Enhancement:** "If you give us an interview transcript, we increase the likelihood of that candidate being legitimate by Y percent"

**Viral Loop Mechanism** [B40.T10]
- **Current:** "For every story that you tell, you get custom jobs"
- **Proposed:** "For every friend that you bring on to Careerspan, you get higher up in our priority list of jobs"
- **Strategic Goal:** Direct candidate acquisition without community partnership overhead
- **Target:** Elite candidates who don't need external incentives - quality over quantity growth

### Roadmap Updates

**Immediate (Week 1-2):**
- Field test two-story + optional transcript verification with hiring managers
- Validate pain point severity and willingness to adopt
- Continue Ilse's manual verification experiments
- Research ATS API integration requirements [B41]

**Near-term (Month 1):**
- Build 8-10 verification case studies including Soham Parikh prevention analysis [B40.T8]
- Develop screening interview optimization methodology
- Map acquisition targets across verification/ATS/workforce categories

**Checkpoint (Month 2):**
- Assess traction from field tests and case studies
- Evaluate acquisition vs. raise decision based on proof points
- Refine integration approach based on technical research

### Feature Decisions

**Prioritized Features for Acquisition Value:**
1. **Story-to-story consistency verification** (Ilse's manual process) [B40.T6]
   - Most defensible unique capability
   - Already operational, just needs scaling
   
2. **Interview transcript comparison** [B40.T4]
   - Differentiating feature vs. traditional background checks
   - Appeals to companies concerned about AI-assisted interview fraud
   
3. **ATS integration layer** [B40.T5]
   - Critical for adoption at scale
   - Reduces friction vs. standalone platform approach
   
4. **Confidence scoring system**
   - Quantifiable output for hiring managers
   - Creates accountability and measurable value
   
5. **White-label capability**
   - Allows companies to brand as internal tool
   - Reduces adoption friction for companies wanting seamless UX

**Deprioritized Features:**
- Community partnership infrastructure [B40.T9]
- Complex job matching algorithms (basic matching sufficient for top candidate model)
- Standalone ATS replacement features (workflow management, data history)

### Alternative Product Direction (Top Candidate + Signing Bonus Model)

**Concept:** Career agent for elite candidates with redistributed recruiter fees [B40.D4]

**Value Proposition:**
- White glove service for "really outstanding candidates"
- Signing bonus funded by eliminating recruiter fees (15-30% first-year salary)
- Passive recruiting advantage - candidates don't need to actively job search
- Agentic reporting - "We sent you to this many people" transparency

**Target ICP:**
- Careerspan Plus members (already identified ~15 people)
- Top candidates identified by Ilse's scoring system (90+ for target role)
- Elite community members (MIT engineers, alumni networks) accessed unofficially [B40.T10]

**Technical Requirements:**
- Ability to identify top candidates (Ilse can score existing target role pool)
- Lightweight agentic reporting system for candidate transparency
- Entry cohort mechanism (invitation-only, exclusivity positioning)

**Strategic Fit:**
- Populist brand alignment: "It's bullshit that people don't get their own signing bonus"
- Missionary positioning vs. mercenary recruiter model
- "Outstanding and authentic" brand naturally fits top candidate focus
- Lower technical complexity than verification product - faster to market

**Revenue Model:**
- Creator program analogy - pay top candidates to be on platform
- Charge companies for access (still cheaper than recruiters at 15-30% fee)
- Money is incentive for elite candidates who don't have acute job search pain

### User Experience

**Verification Flow (Hiring Manager Perspective):**
1. Send Careerspan magic link to candidate
2. Candidate uploads resume + tells two stories
3. Receive confidence score and consistency report
4. (Optional) Share screening interview transcript for enhanced verification
5. Results integrate back into existing ATS workflow

**Verification Flow (Candidate Perspective):**
1. Receive magic link from company
2. Upload resume
3. Record two career stories (familiar from existing Careerspan experience)
4. Complete verification, proceed to interview stage
5. High-effort barrier filters out spam applicants but rewards genuine candidates

**Positioning Insight:** "We're not trying to catch people out, but we're like, listen, that's a red flag" - ethical framing reduces candidate resistance
