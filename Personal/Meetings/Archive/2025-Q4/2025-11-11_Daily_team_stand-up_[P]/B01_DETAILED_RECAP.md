---
created: 2025-11-11
last_edited: 2025-11-14
version: 1.0
---

# Detailed Recap: Careerspan Daily Team Standup

## Meeting Context
- **Date:** November 11, 2025
- **Participants:** Vrijen Attawar, Logan Currie, Ilse Funkhouser, Danny Williams, Ilya Kucherenko
- **Type:** Internal team standup
- **Duration:** ~69 minutes
- **Key Theme:** Product progress on employer portal + acquisition strategy updates + go-to-market refinement

## Core Updates

### 1. Employer Portal - Danny Williams
**Status:** ~90% complete, ready for testing
**Completed Work:**
- Employer role creation and management
- Application dashboard with radar graph visualization
- Deal breaker visibility (displaying on employer side)
- Skills and responsibilities display
- Resume viewer integration

**Outstanding Items:**
- Role breakdown detail pages for individual skills/responsibilities (deprioritized pending user feedback)
- Deal breaker edge cases (awaiting real user data from Ilse)
- Some visualization refinement on radar graph due to graphing library constraints

**Technical Notes:**
- Using Firebase backend (temporary; acknowledges scaling limitations)
- Manual user creation process via admin app + Firebase password reset
- Email verification domain not yet configured (blocking password reset flow)

**Key Decision:** Do NOT build individual detail pages for skills/responsibilities until confirmed valuable. Focus on core application review flow instead.

### 2. Darwin Box Acquisition Channel - Vrijen & Logan
**Status:** High-quality lead with promising trajectory
**Company Profile:**
- Singapore-headquartered, billion-dollar revenue
- Primary markets: India, Philippines
- HR tech/talent management platform
- Position: Not traditional acquirer, but "moonshot" appeal to them

**Call Outcome:**
- Founder receptive and asking substantive questions
- Careerspan positioned as non-traditional but intentional offering
- Logan identified concrete value slots for Careerspan tech within Darwin Box's platform
- Next conversation scheduled for early next week (Vrijen, Logan, Ilse, possibly Ilya)

**Strategic Decision:** Hold 5-7 days before second conversation to allow team time to refine GTM narrative and market positioning (not appearing desperate, gives team breathing room).

**Broader Acquisition Pipeline:**
- Goal: 15-20 acquisition conversations in pipeline
- Current pace: 5-10 targets per week
- Method: Cross-reference known decision-makers at senior levels
- Status: Darwin Box is one solid win in early pipeline phase

### 3. Emory University Deployment - Ilse & Danny
**Status:** Pre-deployment, technical blockers being resolved
**Requirements:**
- Roll out Careerspan to Emory alumni
- Create special code/access for federal worker alumni cohort
- Meeting scheduled for Nov 12 to finalize rollout approach

**Technical Implementation:**
- Pull request submitted (Ilse sourced solution via ChatGPT)
- Deploy to staging first for testing
- Ilse learning deployment process with Danny's guidance (Danny will be unavailable next month)
- Backend email domain verification still needed for full deployment

### 4. BS Bullshit & AI Detection System - Ilse
**Status:** Advanced implementation phase, cost-optimized
**Technical Achievement:**
- Reduced cost from $1/user to $0.20-0.30 per user (5+ stories)
- Architecture enables trivial voice/writing style analysis
- Can fact-check against resumes, interview transcripts, and user narratives
- Testing on 10+ production users with 6+ stories

**Fraud Detection Capability:**
- Analyzes communication style consistency across stories
- Tracks quantitative changes (promotions, responsibility escalation)
- Identifies role changes (CEO interactions vs. middle manager) and inconsistencies
- Detects red flags in narrative arc

**Timeline:** Full dashboard integration by end of week

### 5. Go-to-Market & Video Production - Ilya
**Status:** In-progress narrative refinement
**Work In Progress:**
- Cleaning up customer-facing language across trial
- Creating tiered versions: Full language → Demo version → Video storyboard
- Seeking "dazzling descriptors" for technical concepts (non-technical audience)
- Example explored: "dissertation" as metaphor for 1-page JD → 90-page extrapolation (rejected, needs refinement)

**Video Production Plan:**
- Shortlisted 2-3 animator candidates from Fiverr
- 3-6 day delivery lead time (longest bottleneck)
- Logan reaching out to finalists for portfolio review
- Storyboard must be locked in before animation starts

### 6. Acquisition Strategy & Positioning - Logan & Ilya
**Status:** Developing internal mobility angle as key differentiator
**Internal Mobility Discovery:**
- Different from original external candidate positioning
- Large enterprises (1M+ employees) need internal lateral move capability
- Retention + talent development = huge priority at enterprise level
- Careerspan employer portal + analytics = "sexy" tool for manager discovery

**Negotiation Philosophy (Ilya):**
- Preparing for debrief-phase analysis once conversations advance
- Key defensive strategy: Reframe "missteps" as battle-tested product value
- Timing & perceived value matter critically (Groupon example: early overvaluation → quick devaluation)
- Watch for subtle negotiation tactics disguised as collaboration

**Pipeline Status:**
- Goal: Understand which acquirer categories fit best
- Testing: Internal mobility angle with early conversations
- Next phase: Weekly briefing on pipeline status (starting Nov 12/13)

---

## Key Decisions Made

1. **Employer Portal:** Defer role detail pages; focus on core reviewer experience
2. **Darwin Box:** 5-7 day pause before follow-up to refine narrative
3. **Emory:** Proceed with deployment after solving email domain issue
4. **Video:** Lock storyboard before animation begins
5. **Acquisition Calls:** Ilya joins in debrief/defense phase once conversations advance past demos

---

## Dependencies & Open Items

| Item | Owner | Status | Deadline |
|------|-------|--------|----------|
| Email domain verification (Firebase) | Danny | Blocked | Before Emory deploy |
| Pull request test on staging | Danny → Ilse | In progress | Today |
| Go-to-market language cleanup | Ilya | In progress | Today |
| Animator selection & briefing | Logan | In progress | Next 2 days |
| Darwin Box presentation prep | Vrijen, Ilse | In progress | Early next week |
| Weekly acquisition briefing setup | Logan | To-do | Tues Nov 12 or later |

---

## Team Energy & Observations

- **Danny:** Energized about employer portal progress, pragmatic about scope trade-offs
- **Ilse:** Deep focus on product quality (BS detection) + team enablement (teaching deployment)
- **Logan:** Strategic founder energy, managing acquisition pipeline + GTM refinement + demo coordination
- **Vrijen:** Excited about Darwin Box conversation, mindful of managing team pacing
- **Ilya:** Experienced operator perspective, cautious about scope/involvement, protective of team interests

**Overall Tone:** Optimistic execution phase with strategic patience (Darwin Box pause, storyboard lock-in before animation). Team is moving fast but intentionally.

