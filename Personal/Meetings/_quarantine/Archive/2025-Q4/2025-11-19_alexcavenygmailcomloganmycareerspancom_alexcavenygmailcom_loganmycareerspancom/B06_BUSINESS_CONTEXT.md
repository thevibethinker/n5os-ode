---
created: 2025-11-19
last_edited: 2025-11-19
version: 1.0
---

# Business Context

## Market Situation

**Current State of Careerspan**
- ~3,000 signups (platform)
- ~500 active users (completed profile/story minimum)
- Strong usage metrics (participants reporting high engagement)
- Recently secured LOI from Marvin Ventures (McKinsey alumni fund)
- Demo pipeline: Sapphire Ventures scheduled for next week

**Competitive Landscape**
- Traditional problem: ATS systems are terrible at signal extraction from applications
- Current "solutions": Workday, LinkedIn, generic job boards (all poor at matching)
- Market pain: VCs managing 700 companies with 12,000+ open roles across their portfolios—total chaos

## Revenue & Unit Economics Challenge

**The Core Problem**:
- Full database search against all 3,000+ candidates = hundreds of dollars per search
- Exhaustive ML analysis on profiles = prohibitively expensive at scale
- Current compute time for full match: ~1 week to check against full database

**Implication**: 
- Cannot compete on volume/sourcing if every search costs $100-500
- Must shift business model from "search as service" to "recurring partnership with VCs"
- Subscription model (VCs pay monthly) only works if unit economics are solved first

## Strategic Positioning

### What Careerspan Actually Is
**A better applicant triage and ranking system** that solves the #1 hiring problem every company already has: drowning in inbound without good signal extraction.

NOT:
- A sourcing tool
- A new hiring category
- A candidate database business

**Why This Positioning Matters**:
- Replaces existing workflows (ATS → Careerspan with ATS)—much easier sell
- Modular technology that works with any hiring platform
- Applicable to M&A (would plug into Workday, LinkedIn, any HRIS)

### Positioning Against Market Needs

**Short-term "Wow Moment"** (1-2 hours):
- Customer posts job to Careerspan
- Gets warm start with 5-10 qualified candidates matched against existing pool
- Shows proof of concept and quality of Careerspan analysis
- Builds confidence to continue using platform

**Delayed Gratification Moment** (~1 week):
- Job post gets 1,000+ applications through Careerspan
- Careerspan digests and ranks all of them
- Hiring manager sees prioritized candidate list instead of 1,000 resumes
- Value prop = time savings + decision confidence

**FOMO Reinforcement**:
- Show "recently hired" candidates (like StubHub showing sold tickets)
- Social proof: "This engineer just got hired to Company X through Careerspan"
- Messaging: "Stay active or you'll miss top talent moving through the system"

## Customer Segments & Go-to-Market

### Tier 1: VC Partners
**Why they're ideal**:
- Multiple portfolio companies = repeatable use cases
- Understand startup pain (hiring at scale, time pressure, talent competition)
- Can bundle as portfolio perk (reduces per-company friction)
- Tend to be FOMO-driven (competitive advantage narrative)

**Business Model**: Subscription (monthly fee) or success-based pricing tied to hires made

**Warm Pipeline**:
- Marvin Ventures (LOI in hand)
- Sapphire Ventures (demo next week)
- Others in Alex's network

### Tier 2: Direct Portfolio Companies
**Why they matter**:
- Prove unit value to VC sponsors
- Generate use case data (which candidate profiles convert to hires?)
- Build social proof ("We helped Company X fill 12 roles in 6 weeks")

**Business Model**: Per-job posting or seat-based pricing

### Tier 3: Non-VC Companies
**Potential but secondary**:
- Have same pain (application overload) but less buying power
- Longer sales cycles
- Less FOMO-driven

**Avoid**: Universities (long sales cycles, low budget, misaligned incentives, poor unit economics)

## Product Decisions Needed Before Scaling

### 1. "One-Pager" Definition
Must decide: What's the minimum useful output from Careerspan analysis?
- Current: 40 pages of detailed analysis per candidate
- Needed: 1 page with 3-5 critical data points that make hiring managers feel "these guys understand what they're doing"

**Goal**: Minimize compute cost while maintaining perceived value

### 2. Subset-Based Launching Strategy
Rather than proving ability to search 3,000+ candidates:
1. Start with SF-only and NYC-only candidate lists (top 200-500)
2. Filter by quality signals (3+ story completions, clear career narrative)
3. Demonstrate fast search + quality matching on smaller pool
4. Expand only when unit economics support it

**Benefit**: Fast iteration, lower compute cost, better customer experience

### 3. Passive vs. Active Seeker Strategy
**Current**: All messaging is "active job seeker"

**Needed**: 
- Onboarding question: "Are you looking right now? In 3 months? Open to great opportunities?"
- Messaging adjustment to attract passive seekers (who are often better talent)
- VC partnerships specifically need passive seeker access (their hiring is always "future-facing")

### 4. Compute Cost Optimization
**Challenge**: ML engineer may optimize for accuracy (0.1% improvement) vs. business objectives (2-hour turnaround + $0.50 cost)

**Required mindset shift**: "We need a really good $0.50 solution, not a perfect $50 solution"

**Potential Approaches**:
- Auto-encode profiles to simpler representations for faster searching
- Implement cheap filters first (location, seniority level)
- Run two-tier analysis: fast pass for 80% filtering, deep analysis only on candidates scoring 70+
- Use persistence metrics to reduce noise (don't count signals lasting <500ms)

## Revenue Assumptions

### VC Subscription Model
- Monthly fee: $2-5K/month per VC partner
- Triggered by: VCs posting on behalf of portfolio companies
- Revenue stability: Multi-company partnerships = predictable MRR

### Per-Job Posting Model
- Individual company usage: $500-1,000 per job post
- Requires: Candidate pool size to justify (500+ qualified candidates minimum)

### Current Bottleneck
- Cannot scale either model until compute economics are solved
- Need real customer use cases to define "good enough" output
- First customer feedback essential to avoid building wrong product at scale

## Key Success Metrics (Near-term)

1. **Demo conversion**: Turn Sapphire Ventures + others into paying pilots
2. **Time-to-hire improvement**: Track actual hiring speed for first customers
3. **Candidate quality**: Measure how many "matches" convert to interviews/hires
4. **Compute efficiency**: Reduce cost-per-search from $100+ to <$2 while maintaining quality
5. **Workflow integration**: Ensure Careerspan sits naturally in customer's existing hiring process
