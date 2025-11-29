---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B01: Detailed Recap

## Key Decisions and Agreements

**1. Job Board and Employer Messaging Strategy LOCKED**
- **Decision**: Announce Careerspan's new employer partnership model on LinkedIn, positioning the platform as an alternative application route
- **Why It Matters**: Direct apply remains free; employer access unlocks more leads and platform visibility
- **Rationale**: Value proposition is clearest when explained as "skip the ATS" + "top-of-stack candidates" rather than theoretical
- **Implementation**: Logan preparing announcement document with messaging to be shared across team LinkedIn profiles
- **Timeline**: Post early next week after streamlined lead process is ready (few days away)

**2. Job Board Composition Strategy CONFIRMED**
- **Decision**: Populate board with mix of (a) actively open roles, (b) "coming soon" placeholder roles, and (c) notification signup for future roles
- **Why It Matters**: Creates perception of active hiring environment; nudges candidates to tell stories preemptively; builds mailing list
- **Key Roles to Feature**: Go-to-market engineer, forward-deploy engineer (Superposition interest)
- **Placeholder Approach**: Mark roles with closure dates to set expectation management
- **Notification Mechanism**: TBD (SendGrid vs. Loops); allows email notification when role opens

**3. Free Tier Guardrail IDENTIFIED**
- **Decision**: Direct apply applications always free; consider limiting free tier to 1-2 additional non-direct applications per user
- **Why It Matters**: Prevents unlimited OpenAI/vibe-check costs from bankrupting runway during user acquisition spike
- **Deferral**: Requires engineering; prioritization depends on financial stress-test results
- **Nuclear Options**: Stop new signups or pull OpenAI API key (both undesirable; need graceful degradation)

**4. Candidate Story Framing REINFORCED**
- **Decision**: Lead messaging with "preemptively tell your stories" rather than apologizing for the ask
- **Why It Matters**: Candidates who understand story value actively participate; framing shapes self-selection
- **Evidence**: Team consensus that candidates hesitant to tell stories "don't get it" anyway; focus on believers
- **Messaging**: "Get started by telling stories; they make your profile stronger"

**5. Cost Contingency Planning INITIATED**
- **Decision**: Vrijen + Logan to run financial stress-test; Ilse to generate rough usage/cost projections
- **Why It Matters**: Massive user acquisition spike is possible but financially risky (applications feature is expensive)
- **Historical Context**: Previous acquisition campaign generated hundreds of users daily; stories + applications didn't exist then
- **Timeline Constraint**: Danny away Nov 13-17 then permanently leaving; need on-call engineering backup identified
- **Worst Case**: If costs spiral, pause growth or implement free tier guardrails immediately

## Strategic Context

Careerspan is preparing for significant user growth via job board marketing announcement. Core tension: Can engineering/costs handle hundreds of daily new users using application features? Ilse flagged this as urgent given Danny's impending departure and historical precedent of rapid user acquisition.

Team consensus on philosophy: Careerspan's real defensibility is community landscape dominance, not proprietary algorithm. Clear messaging reduces friction with employers (pragmatic GTM beats theoretical positioning).


