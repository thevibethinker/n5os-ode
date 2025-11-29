---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Meeting Recap: Strategic Pivot Discussion

## Context & Tone
A focused strategic conversation between Vrijen (founder/CEO) and Ilse (tech lead) to align on major directional changes for Careerspan. The meeting was candid about current challenges and outlined a fundamentally different approach: shifting from a venture-scale ambition to an acquisition-focused, lean-burn model.

## The Problem Statement
Despite having strong product fundamentals (excellent retention and reactivation metrics), Careerspan faces a critical sustainability issue:
- Sales execution is extremely difficult; the team has secured recruiting firm partnerships and job roles but lacks qualified candidates to fill them
- The current business model and product strategy are not generating sufficient revenue to sustain the existing burn rate
- Even with well-funded competitors, Careerspan's technical superiority alone doesn't guarantee market success without distribution

## The Strategic Pivot
**Core Thesis:** Instead of pursuing traditional venture scaling, Careerspan should optimize for acquisition by entering "low power mode" — dramatically reducing burn, maintaining product momentum, and positioning for a strategic exit.

**Key Financial Commitments:**
- 3-month runway for team members (with accelerated vesting if company sells within a year)
- 6-month runway for core leadership (Vrijen, Logan, Ilse)
- Minimal spend on token costs for API infrastructure
- No new fundraising; possible discussions with existing investors for sustainability

## Product & Distribution Strategy

### The Decentralized Talent Network
A central strategic insight from Logan and the team: create a simple, low-friction employer portal where:
- Employers submit job descriptions
- Candidates access a single hub to browse jobs and connect
- Magic links enable interested candidates to be contacted by hiring managers
- Minimal backend analysis required per candidate

### Technical Reorientation
Ilse raised a critical concern: the current analysis pipeline (preferences check → vibe check → full analysis) is computationally expensive and time-prohibitive at scale.
- Current cost per vibe check: 30-50 cents
- Processing 50 jobs against 2,000 users: 18-22+ hours of compute time
- API rate limits with OpenAI create hard bottlenecks

**Proposed Solution:** Shift from comprehensive analysis to a simpler "is this person worth screening?" question. Relax analytical rigor for initial candidate matching, reserving detailed analysis for shortlisted candidates. This dramatically reduces costs and compute time while maintaining decision quality for hiring managers.

### Go-to-Market Evolution
- **Logan's focus:** Brand building, social media-driven organic growth, grassroots community embedding
- **Technical side:** Make jobs distribution cheaper and more scalable; reduce cost-per-candidate-check
- **Distribution:** Leverage Vrijen's hiring manager network (described as the "biggest network" we have at peak saturation), position hiring managers as the primary channel

## Competitive Positioning
Two well-funded competitors (Dax, Jack and Jill) have inferior technology but stronger distributions. The insight: market validation exists; execution and staying power matter more than product superiority at this stage.

## Near-Term Actions
1. Separate conversation with Logan + Ilse before speaking to team (Danny and Knockel) about runway and revised strategy
2. Vrijen exploring opportunity at ASU Agentic AI conference to build relationships with educational institutions
3. Evaluate hiring Tim (or similar recruiter) to drive placement pipeline — Vrijen offered to cover salary if needed
4. Explore subscription revenue model with venture capital firms (VCs as ICP) seeking talent on tap for portfolio companies

## Unresolved Tensions
- **Product rigor vs. speed:** Ilse strongly advocated for maintaining analytical rigor; historically resisted pressure to reduce quality. The new strategy may require renegotiating this principle.
- **Distribution model:** Ilse questioned the feasibility of survival without dedicated sales/pipeline generation; expressed skepticism about pure organic/acquisition-focused approach without aggressive business development
- **Technical feasibility:** Scaling the current system to thousands of users and hundreds of jobs per week is economically impossible with existing infrastructure and methodology
