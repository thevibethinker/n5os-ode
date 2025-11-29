---
created: 2025-11-25
last_edited: 2025-11-25
version: 1.0
---

# B06 – Business Context

## Company
- **Company**: Careerspan
- **Domain**: Career navigation and hiring – helping candidates tell rich, story‑based narratives and helping employers discover, evaluate, and stay in touch with talent.
- **Model**: Two‑sided platform (candidates and employers) with software and AI services layered on top.

## Product Architecture (as surfaced here)
- **Candidate side**:
  - Candidates record stories and preferences, which feed both quick screening and deep analysis.
  - **Vibe checks**: Lightweight first‑pass assessments of role fit using a job description; originally designed to inform, not filter.
  - **Full analysis**: Deeper, line‑item evaluation using stored stories; more expensive but higher fidelity.
- **Employer side**:
  - Employers receive curated candidates based on a mix of direct and transferable skills.
  - Future direction includes rich configuration (e.g., how much transferability they’ll tolerate) and deeper analytics powered by accumulated metadata.

## Current Technical/Operational State
- Scoring:
  - Present system uses a roughly linear scale for transferability vs direct experience; this works early but breaks down once candidates accumulate many stories.
  - Transferable skills can currently drive very high scores, which risks overstating readiness and mis‑setting employer expectations.
- Pipelines:
  - Behind the scenes, Careerspan runs periodic automated checks across many roles, progressively filtering via preferences, quick checks, vibe checks, and then full analyses.
- Notifications / UX:
  - Notification UI exists but is under‑utilized; long‑running processes like full analysis can feel slow and opaque from the candidate’s perspective.
  - Email is the main reliable, scalable channel for keeping people informed today.

## Go‑to‑Market Motion
- **Demos**:
  - Live demos are a core motion with encouraging signals: recent calls have already advanced prospects to integration‑level conversations.
  - The team is thinking of demos analytically (volume, conversion) rather than as one‑off events.
- **Marketing & Ads**:
  - The company is investing in targeted campaigns with strong creative concepts (e.g., pre‑Christmas "open this gift early" ads) and candidate‑facing landing pages that justify time commitment.
  - Upcoming experiments may coincide with high‑attention periods like Black Friday/Cyber Monday, but only with strict budget and targeting guardrails.

## Data, Community, and Moat
- Careerspan expects to accumulate significant cross‑cutting metadata about employers, roles, and candidates.
- The long‑term moat is framed as:
  - **Protected access** (analogous to LinkedIn’s anti‑scraping posture), which preserves platform value.
  - **Tiered visibility and analytics**: basic insights by default, with premium tiers offering deeper views or temporary "XP boost"‑style enhancements.
- Community philosophy emphasizes:
  - Encouraging ethical, inclusive use of filters and analytics.
  - Avoiding tools that simply make it easier to exclude non‑traditional candidates without reflection.

## Strategic Tensions Highlighted
- **Accuracy vs inclusivity**: Making sure transferability is neither over‑ nor under‑weighted so that employers get realistic signals while non‑traditional candidates still have a path in.
- **Simplicity vs sophistication**: Starting with simple, controllable email flows while keeping space open for future agent‑based orchestration.
- **Experimentation vs over‑confidence**: Repeated emphasis that the team must test assumptions with real users rather than assume it knows what the market wants.

