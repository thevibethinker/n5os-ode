## PRODUCT_INTELLIGENCE

---
**Feedback**: - [ ] Useful
---

### Superposition Product Intelligence

**Core Product**: AI-powered recruiting platform using voice agent for job intake

**Product Flow** (as described):
1. Company onboards through Superposition voice agent
2. Agent conducts conversational job description extraction (replaces traditional JD forms)
3. Superposition generates rich, contextual job description from conversation
4. [Current state]: Superposition sources candidates "from the Internet" (unclear if this is automated or manual)
5. [Proposed future state]: Careerspan provides candidate supply layer via API/integration

**Product Philosophy**:
- **Voice-first UX**: Edmund's requirement that companies "onboard in our product" suggests voice agent is core IP/moat
- **Context maximization**: Voice conversation extracts nuance that forms can't capture (role context, team dynamics, hidden requirements)
- **Engineer-focused (currently)**: Only does engineering roles today, considering expansion to PMs, designers, forward-deployed roles
- **Anti-marketplace**: Currently NOT doing candidate marketplace (Edmund: "We're not really touching the kind of candidate side")

**Competitive Positioning**:
- **Replaces**: Traditional contingency recruiting (human-led job intake + manual sourcing)
- **Competes with**: Gem, Lever (recruiting automation), potentially Hired/Vettery (marketplace models)
- **Differentiation**: Voice agent UX for intake (reduces form friction), focus on context extraction over keyword matching

**Product Gaps** (inferred from conversation):
- **Candidate supply**: Currently sourcing "from the Internet" but Edmund interested in Careerspan partnership suggests this isn't working optimally
- **Non-engineer roles**: Considering expansion but hasn't built this yet
- **Latent signal discovery**: Recognize value but don't have mechanism to extract beyond what voice agent JD reveals

**Integration Points for Careerspan**:
1. **Output from voice agent** → Careerspan receives rich JD, converts to magic link format
2. **Careerspan candidate pool** → Flows back into Superposition for client presentation
3. **Attribution/tracking**: Need system to track which candidates came from Careerspan for revenue share

---

### Careerspan Product Intelligence (from Edmund's perspective)

**What Edmund Understands About Careerspan**:
- **Coaching infrastructure**: 1500+ hours of candidate coaching interactions
- **Magic link evaluation**: Semantic evaluation system (specific enough to reference by name)
- **Hiring portal**: Complete product with semantic evaluation capabilities
- **Latent signal capture**: Coaching reveals non-obvious candidate capabilities

**What Edmund Values**:
- **Signal differentiation**: "Something hidden that you're not going to get by brute forcing" - sees Careerspan's coaching data as unique
- **Role-specific applicability**: Specifically excited about roles where "ability to hold a conversation is indicative of job fit" (GTM engineer, forward-deployed)
- **Complementary to voice agent**: Doesn't compete with Superposition's intake process, enhances candidate supply

**What Edmund Doesn't Seem to Understand (or didn't ask about)**:
- How Careerspan coaching converts to candidate matching (mechanics of "this coaching session reveals forward-deployed capability")
- Scale of candidate pool (how many active job seekers in Careerspan database?)
- Geographic coverage (US-only? International?)
- Candidate exclusivity (are Careerspan candidates also on LinkedIn, talking to other recruiters?)

**Product Validation Signals**:
- ✓ Edmund didn't question whether coaching signal is real (accepts premise)
- ✓ Immediately identified applicable use cases (forward-deployed, GTM)
- ~ Unclear if he understands magic link evaluation mechanics (referenced but didn't explore)
- ~ Didn't ask about scale/volume (suggests either not concerned or assuming it's adequate)

---

### Product Integration Architecture

**Proposed Flow**:
```
Company → Superposition voice agent → Rich JD generated
       ↓
Careerspan receives JD → Converts to magic link format
       ↓
Careerspan candidate pool → Semantic matching to JD
       ↓
Matched candidates → Magic link evaluation sent to candidates
       ↓
Qualified candidates → Flow back to Superposition
       ↓
Superposition → Presents to client company
       ↓
Hire → Revenue split between Superposition & Careerspan
```

**Technical Requirements** (to be validated):
- API connection between Superposition and Careerspan (or manual handoff for pilot?)
- Standard format for JD transfer (JSON, structured fields vs free text?)
- Candidate tracking system for attribution
- Feedback loop (did candidate get hired? How did they perform in interviews?)

**Integration Friction Points**:
- **Format mismatch**: Superposition's voice agent output may not map cleanly to magic link format
- **Timing**: How long does Careerspan take to source and evaluate candidates? (Edmund's clients likely expect fast turnaround)
- **Volume expectations**: If Superposition client wants 50 candidates screened, can Careerspan deliver at that scale?
- **Communication channel**: How does Superposition present Careerspan candidates to clients (co-branded? White-labeled? "Powered by Careerspan"?)

---

### Product Development Implications

**For Careerspan**:

1. **Build API Integration Layer**:
   - Receive job descriptions programmatically (don't rely on email handoffs)
   - Return candidate profiles in format Superposition can ingest
   - Track attribution automatically for revenue share calculation

2. **Optimize for Speed**:
   - Edmund's clients likely expect 1-2 week turnaround on candidate pipeline
   - Need to accelerate coaching → matching → evaluation flow
   - Consider async evaluation methods to increase throughput

3. **Role-Specific Signal Extraction**:
   - Document which coaching signals map to forward-deployed capability
   - Build playbooks for GTM engineer, solutions architect, other non-standard roles
   - Create "latent signal report" for each candidate (evidence for hiring managers)

4. **Scale Candidate Pool**:
   - Current pool may be insufficient for partnership demand
   - Need acquisition strategy for candidates interested in non-standard roles
   - Consider: Where do forward-deployed engineers and GTM engineers currently look for jobs?

**For Partnership Success**:

1. **Start with Manual Handoffs** (pilot):
   - Don't build full API integration before proving value
   - Email-based job description sharing fine for 1-2 pilot roles
   - Manual candidate presentation to validate format/quality expectations

2. **Build Feedback Loop**:
   - Track which latent signals actually predicted interview success
   - Iterate on evaluation criteria based on real hiring outcomes
   - Share learnings with Edmund to improve joint offering

3. **Co-branded Materials**:
   - Create "Superposition x Careerspan" pitch deck for Marvin companies
   - Explain how voice agent + latent signals work together
   - Case study format (once pilot generates successful hire)

---

### Product Roadmap Alignment

**Superposition's Likely Roadmap** (inferred):
- **Near-term**: Expand beyond engineers to PM/designer/technical adjacent roles
- **Medium-term**: Geographic expansion (currently US, potentially international)
- **Long-term**: Full-stack recruiting platform (intake + sourcing + evaluation + ATS integration?)

**Careerspan's Roadmap** (inferred from meeting):
- **Near-term**: Prove latent signal value through Superposition partnership
- **Medium-term**: Scale partnerships (more platforms, more communities)
- **Long-term**: Acquisition by larger recruiting/HR tech platform

**Alignment Opportunities**:
- Superposition's role expansion = Careerspan can help validate PM/designer latent signals
- Both companies optimizing for acquisition (Superposition likely venture-backed, looking for strategic exit)
- Shared philosophy on evaluation (traffic light not thermometer)

**Misalignment Risks**:
- If Superposition scales to hundreds of clients, Careerspan's coaching model may not scale with demand
- Superposition may eventually build own candidate sourcing (reducing dependency on Careerspan)
- Geographic expansion could fragment partnership (Careerspan likely US-focused currently)

---

### Product Metrics to Track During Pilot

**Candidate Quality**:
- What % of Careerspan candidates pass Superposition's initial screen?
- How do they compare to candidates from other sources (LinkedIn, referrals, etc)?
- What % get client interviews? Offers? Hires?

**Latent Signal Validation**:
- Which specific coaching signals correlated with interview success?
- Did "latent signal report" help hiring managers make decisions?
- Were there false positives (signals seemed good but candidate didn't work out)?

**Operational Metrics**:
- Time from job description to candidate delivery (target: <1 week?)
- Number of candidates per role (target: 5-10 qualified candidates?)
- Drop-off points (where do candidates fall out of funnel?)

**Business Metrics**:
- Revenue generated per role (success fee amount)
- Cost to Careerspan per placed candidate (coaching hours, evaluation time)
- Customer satisfaction (would Superposition client hire from Careerspan pool again?)

**Strategic Metrics**:
- Did partnership generate case study / proof point for other partnerships?
- Did Careerspan learn insights applicable to direct sales or other integrations?
- Did partnership attract acquisition interest or investor attention?

