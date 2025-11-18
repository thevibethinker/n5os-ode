---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
block_id: B01
---

# B01: Detailed Recap

## Meeting Context
- **Duration**: ~15 minutes
- **Type**: Sales call (external)
- **Vrijen's Role**: CareerSpan CEO (seller)
- **Client**: Quantum Labs (Series B SaaS, real-time data infrastructure)

---

## Problem Statement (Client's Pain Points)

**Quantum Labs is scaling from 35 to 85 engineers (2.4x headcount increase) in 9 months and facing severe hiring friction.**

### Primary Challenge: Quality Screening (Signal-to-Noise Ratio)
- **Current state**: "Brutal" - Marcus spending 60% of time on candidate screening
- **Root cause**: Current recruiting agencies doing keyword matching only
- **Evidence**: Candidates with "Kafka" and "Kubernetes" on resume but only narrow tool experience, can't design systems or reason about trade-offs
- **Concrete impact**: 40% of candidates passing Marcus's phone screen still fail Sarah's technical deep-dive → wasted engineering time on non-viable candidates

### Secondary Challenge: Engineering Interview Load
- **Cost**: Senior engineers pulled for 3-week interview loops while delayed on Q4 infrastructure milestone by 3 weeks
- **Owner/Impact**: Sarah Chen (VP Engineering) explicitly stated: "every hour my senior engineers spend interviewing is an hour they're not shipping"

### Tertiary Challenge: Specific Technical Requirements
- Quantum Labs not looking for generic "senior backend engineers"
- Specific need for **distributed systems depth**: consensus algorithms, data replication at scale, consistency models
- Sarah wants candidates with production incident experience (not just academic knowledge)
- Key differentiator: Can candidates reason about strong consistency vs. eventual consistency trade-offs?

---

## CareerSpan Solution Pitch

### Core Innovation: Story Packs
Instead of keyword-matched resumes, CareerSpan uses **structured narratives** where candidates demonstrate:
- Decision-making depth (why choose X over Y)
- Trade-off analysis (what broke at scale, how debugged)
- Technical nuance communication

**Example**: Not "Built microservices using Kafka" but rather "Here's why I chose Kafka, what I considered, what broke at scale, and how I debugged it"

### Quality Validation Mechanism: Community Quality Score
- Every story pack peer-reviewed by community of **senior practitioners** (CTOs, Staff+ engineers)
- Specific validators mentioned: Datadog, Stripe, Confluent (companies with deep distributed systems expertise)
- Not self-reported; externally validated for authenticity and depth

### Delivery Model
- **Turnaround**: 24-hour curated shortlists (vs. agencies' "48-hour shortlists" that are LinkedIn scrapes)
- **Format**: 3-5 candidates per shortlist (quality over volume; vs. agencies flooding with 50 resumes)
- **Pre-screening done upstream**: By time candidate reaches client interview, 90%+ confidence they're right caliber

### Historical Performance
- **Success rate**: 60% of CareerSpan candidates make it through full interview loops to offer stage
- **Client comparison**: Quantum Labs currently seeing only 40% phone screen → technical round pass rate (i.e., inverse problem)
- **Customer base**: Mostly Series A-C startups like Quantum Labs

### Specific Mechanism for Quantum Labs
- Vrijen proposed adding specific dimensions to story pack prompts for distributed systems depth
- Candidates wouldn't just claim "I know distributed systems"—would walk through production scenarios where they made consistency/partition/fault-tolerance trade-offs
- Community validators (Datadog, Stripe, Confluent personnel) assess depth of responses

---

## Economics & Risk Profile

**Pricing Structure**:
- Per-search model: $4,500 per search (not traditional retained agency)
- Up to 5 candidates per search
- No additional fees if hire 3 of them; no per-hire percentages

**Comparison to Current Spend**:
- Current agencies: 20-25% of first-year salary → ~$36-45K per hire for $180K senior engineer
- CareerSpan at $4,500/search is dramatically cheaper (assuming 60% placement rate)

**Quality Guarantee (Risk Mitigation)**:
- If none of 5 candidates pass Quantum Labs' technical interview, CareerSpan runs second search at no cost
- Vendor betting on curation quality

---

## Implementation Plan (Pilot)

**Scope**: 2-3 critical roles pilot (not 50-search commitment)
- Starting role: **Senior Distributed Systems Engineer** (highest pain point)

**Onboarding**:
- 1-hour deep-dive call to build search brief
- Attendees: Marcus (recruiting), Sarah (VP Engineering), +1 senior engineer for technical nuance
- Not just skills; context: What are they walking into? Team dynamic? 90-day problem set?

**Expected Timeline**:
- Shortlist delivery: 24 hours
- Interview scheduling: ~1 week (standard friction)
- Interview loops: ~2 weeks
- Offer negotiation: ~1 week
- **Total**: 4-6 weeks time-to-hire (industry standard; CareerSpan's value is reducing friction upstream)

**Metrics Success**:
- If 2 solid hires out of next 5 roles, pays for itself in time savings alone (Sarah's perspective)

---

## Key Moments / Selling Points

### Moment 1: Problem Validation
Vrijen's diagnostic: "So the agencies you're working with—are they surfacing candidates with the right depth? Or are they just keyword matching?"
- Sarah's response: "Honestly? Keyword matching."
- This validated problem before offering solution

### Moment 2: Community Credibility
When Marcus asked "Who's doing this curation?", Vrijen naming specific company validators (Datadog, Stripe, Confluent) added credibility to community quality score (not abstract)

### Moment 3: Cost Justification
Marcus reframed $4,500 cost against 20-25% agency fees—suddenly becomes compelling ROI argument

### Moment 4: Risk Flip
Vrijen's quality guarantee (second search free if first fails) shifted risk from buyer to vendor—removed purchase barrier

### Moment 5: Pilot Legitimacy
Sarah's acceptance of 2-3 searches pilot signaled openness; Vrijen didn't push for large commitment
- Sarah's closing rationale: "if you can deliver even two solid hires out of the next five roles we need to fill, this pays for itself"

---

## Agreements & Next Steps

**Closed Items**:
- ✅ Quantum Labs agrees to pilot: 3 searches at $4,500 each with quality guarantee
- ✅ Distributed Systems Engineer as first search priority
- ✅ Call attendees: Marcus (recruiting), Sarah (VP Engineering), +1 senior engineer

**Open Items** (to be scheduled):
- Pilot agreement document (Vrijen to send today)
- Kickoff call to build search brief (next week)
- Calendar invite to be sent

---

## Relationship Signals

- **Receptiveness**: High (Sarah: "I think it's worth a shot"; both executives engaged)
- **Authority**: Both Sarah (technical) and Marcus (recruiting) present and aligned
- **Timeline**: Implicit urgency (85 engineer target in 9 months = ~2-3 hires/month)
- **Budget**: No budget objection raised; comparison to 20-25% agency fees suggests budget exists
- **Next meeting**: Warm handoff, both committed to next steps

