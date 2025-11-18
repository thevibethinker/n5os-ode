---
created: 2025-11-16
last_edited: 2025-11-16
version: 1.0
---

# B08_FOLLOW_UP_CONVERSATIONS

## Scheduled Follow-Ups

### Ilya + Vrijen + Logan — Tomorrow (Day 3)

**Purpose**: Flesh out trial paths and marketing campaign structure

**Agenda** (from Ilya's closing remarks):
1. Walk through identified user trial path in detail (the "robust trial" with 24-48 hour candidate sourcing)
2. Flesh out second trial path (scaled-down version for hesitant employers)
3. Firm up true value propositions (what Careerspan can definitely do today, what's coming soon)
4. (Time permitting) McKinsey/Insta Lily strategy

**Deliverables Ilya Will Prepare**:
- Marketing campaign framework (how campaigns will be structured and executed)
- Key value propositions document (2-3 value props that are provable today)
- Multiple trial path options (basic, gamified, enterprise)
- Tactical options document (referral programs, third-party validation campaigns beyond paid ads)

**Deliverables V/Logan Will Prepare**:
- Notion document walkthrough (how to navigate Careerspan's customer/candidate data and workflow)
- Messaging catalog update (V to extend analysis from current meetings to 20+ past founder conversations)
- Documentation that Ilya requested (specifics TBD, but likely product capabilities, customer pain points, competitor landscape)

**Duration**: Ilya noted he's in "sponge week" (day 2-3), so he'll be absorbing and drafting, not yet executing. Next week is when he'll move to "execution phase" with calendar management and campaign drafting.

---

### Vrijen — McKinsey Partner + Board Member

**Purpose**: Formalize McKinsey portfolio company agreement

**Urgency**: ASAP (within 1-2 days)

**Action**: 
- Text board member to confirm they're ready to sign/finalize
- Get formal agreement signed (currently "unofficial sanction")
- Confirm: Can Careerspan post jobs on behalf of these 250+ portfolio companies?
- Confirm: Can Careerspan contact those companies with offer to use Careerspan?

**Outcome Needed**:
- Signed agreement (or email confirmation if signing not immediate)
- List of 250+ portfolio companies
- Contact point(s) for reaching into that network
- Any contractual restrictions on Careerspan's use of job data

**Strategic Dependency**: This agreement unblocks the go-to-market plan. Without it, Careerspan reverts to one-off customer recruiting, which is slow.

---

### Vrijen — McKinsey Investor

**Purpose**: Share Careerspan opportunity and potentially loop them into support for partner/portfolio outreach

**Timing**: Same window as partner conversation (1-2 days)

**Action**:
- Email blurb to investor (per V's note: "I need a blurb for the investor to send to the HR company")
- Explain: What Careerspan does, why it matters for their portfolio, how investor can help amplify
- Soft ask: Can they mention Careerspan to portfolio company HR leads?

**Outcome Needed**:
- Investor awareness and buy-in
- Potential champion role (mentions Careerspan to portfolio companies)
- Feedback on positioning/messaging

---

### Vrijen — Insta Lily Co-Founder

**Purpose**: Explore trial opportunity while managing expectations

**Urgency**: Within 1 week (not urgent, but should move soon)

**Context**: V has already met with board member + investor. Both validated Insta Lily's pain (Series A, many open roles, hard to screen).

**Action** (per Ilya's guidance):
- "Under-promise, over-deliver" approach
- Honest framing: "We're early, building this with founder feedback, here's what we can do today and where we're going"
- Soft ask: Would you be willing to try Careerspan with 2-3 roles as a case study?
- Don't over-commit: if they demand heavy customization, defer to post-launch

**Outcome Needed**:
- Agreement to trial Careerspan (ideally with 2-3 job descriptions)
- Feedback loop on product/positioning
- Case study (if it goes well)

**Note**: Ilya flagged risk—don't let Insta Lily consume excessive time if they're demanding. Focus on companies with fewer custom needs and clearer payoff.

---

### Vrijen/Logan — Zapier Contact ("Bonnie")

**Purpose**: Explore "friend-of-family" trial opportunity

**Urgency**: Within 1-2 weeks (after McKinsey is formalized)

**Context**: Zapier is high-growth, AI-forward, likely has hiring pain. V noted "we got Bonnie" (existing relationship).

**Action** (adapting Ilya's playbook):
- Reach out via warm intro (or directly to Bonnie if close enough)
- Honest pitch: "We're building a hiring tool with founder community feedback. You're hiring fast and we think we can help. Want to try?"
- If interest: send small blurb (what Careerspan does, why it matters, timeline expectations)
- Invite to be early case study
- Manage expectations: "We're building, we're learning, your feedback matters"

**Outcome Needed**:
- Agreement to trial with 2-5 roles
- Feedback loop on product and messaging
- Potential champion/referral relationship
- Quota of 50+ qualified candidates sourced within 72 hours (Ilya's test scenario)

**Why This Works**: Zapier has senior leadership, multiple open roles, visibility to founders, and an executive who can say "try this" to their team. Plus existing relationship means less cold outreach friction.

---

### Ilya + Careerspan Team — Technical Architecture Review

**Purpose**: Understand system constraints and optimization path

**Urgency**: Within 2-3 days

**Participants**: Ilya, Ilse (technical), possibly Danny

**Agenda**:
1. OpenAI integration: Current latency profile, bottlenecks, retry logic
2. Rate limiting: What's the safe concurrency? What triggers degradation?
3. Story-minimum requirement: Timeline and impact on conversion (Danny building it)
4. Scaling roadmap: What would it take to handle 100+ simultaneous applicants?
5. Priority queue: Should Careerspan pay for OpenAI priority queue? Cost/benefit?

**Outcome Needed**:
- Clear capacity ceiling (safe to onboard X companies at once)
- Degradation profile (what happens at 2x, 5x, 10x current load?)
- Mitigation tactics (story minimum, staged onboarding, load monitoring)
- Timeline for system optimization (pre- or post-campaign launch?)

**Strategic Implication**: This review determines the campaign's go-live date and scale. If system isn't ready for 5-company cohorts, Ilya can't launch marketing.

---

### Logan — User Onboarding & Communication Sequence Review

**Purpose**: Audit candidate and employer communication flows before customer influx

**Urgency**: Before marketing campaign (within 1-2 weeks)

**Context**: Logan flagged that current onboarding emails are "bare bones" ("Get job matches" — but candidates don't get matches and confusion results). System readiness for higher volume requires communication clarity.

**Agenda**:
1. Map out current email sequence (employer and candidate side)
2. Identify gaps (what should be said but isn't)
3. Set expectations clearly (what candidates and employers get, what they don't, what's coming)
4. Draft new sequence for trial-to-paid path
5. Test with pilot customers

**Deliverables**:
- Revised onboarding email sequence (employer)
- Revised onboarding email sequence (candidate)
- FAQ or help doc (common questions from users)
- Expectation-setting: "First 48 hours you'll see X, by day 5 you'll see Y"

**Why This Matters**: Ilse mentioned she gets users saying "I'm not getting job matches" — this is a communication problem, not a product problem. Fixing it pre-scale prevents churn and improves trial-to-paid conversion.

---

## One-Off Clarifications Needed

### From Logan: User Communication Platform Capabilities

**Question**: What communication tools/templates can Careerspan send to candidates and employers? Can they be customized per employer?

**Why It Matters**: Ilya wants to tailor messaging to different ICPs; Logan wants to set clearer expectations.

**Timeline**: Before drafting campaigns

---

### From Ilse: System Load Testing Baseline

**Question**: What's the current peak load Careerspan has handled? What was the user base size? How did performance degrade?

**Why It Matters**: Ilya needs to know how big to make first cohort without breaking system.

**Timeline**: Within 2-3 days (before trial planning)

---

### From Ilya: Competitor Landscape Summary

**Question**: What are top 3-5 competitors? How are they positioned? What are they claiming?

**Why It Matters**: Messaging and positioning need to differentiate vs. incumbents and new entrants.

**Timeline**: Can be async; Ilya can research this week

---

## No Follow-Ups Needed

**Ilse**: Left call early (spacey, needs rest). Already covered all her input on system constraints and load testing concerns. Can pick her up on technical review call.


