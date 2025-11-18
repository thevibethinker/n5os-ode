---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B03: DECISIONS MADE & REASONING

## Decision 1: Defer Role Detail Pages Feature

**Decision**: Implementation of deep-dive detail pages for individual skills/responsibilities will NOT be prioritized in immediate roadmap

**Context**:
- Danny raised concern: "I just don't know how useful it's gonna be to go through like 20 different pages"
- Feature was intended to help non-technical hiring managers understand role requirements
- Could enable technical SME validation of job descriptions

**Arguments For**:
- Vrijen emphasized demo value: "it's gonna be part of the demo"
- Enables validation by domain experts (e.g., "does this Swift engineer job description look right?")
- Supports inexperienced hiring managers in new technical domains

**Arguments Against** (Prevailing):
- Danny's skepticism: Feels like a product misfit for employers (might belong in job seeker prep app instead)
- Unproven demand signal from users
- Engineering effort could be better spent elsewhere
- Summary view sufficient for initial use cases

**Resolution**: Vrijen acknowledged "I would appreciate tossing it in because it's sexy" but agreed to deprioritize in favor of "deal breaker reviewing and... getting the deal breaker stuff visible on the employer portal"

**Status**: Feature moves to backlog; can revisit if user feedback indicates demand

---

## Decision 2: Prioritize Deal Breaker Review Implementation

**Decision**: Deal breaker functionality (employer-side review) moves to priority tier immediately

**Context**:
- Already partially implemented on employer dashboard (visible)
- Missing: applicant-side form for deal breaker question submission
- Blocker: No test data to validate output format/handling

**Rationale**:
- Vrijen indicated this is "more important than" detail pages
- Required for Emory partnership rollout (federal worker cohort needs deal breaker screening)
- Unblocks data validation work

**Implementation Approach**:
1. Vrijen will create test user with deal breaker requirements
2. Vrijen will submit application(s) with deal breaker responses
3. This generates realistic data for Danny to test/validate
4. Allows validation without requiring mock/fake data

**Reasoning**: Real user data removes guesswork about field types, string lengths, edge cases

**Timeline**: Must complete before Emory meeting tomorrow

**Owner**: Danny (testing/validation), Vrijen (test data generation)

---

## Decision 3: Bundle Backend Deployment Training with Emory Work

**Decision**: Conduct knowledge transfer on backend deployment as part of same-day work session

**Context**:
- Vrijen needs to deploy code fix for Emory federal worker code
- Danny leaving in ~1 month, creating succession risk
- Vrijen has never deployed backend before

**Original Alternative**: Danny deploys directly; Vrijen watches or waits

**Chosen Alternative**: Danny teaches Vrijen deployment hands-on while doing actual work

**Rationale**:
- Kills two birds (Emory requirement + knowledge transfer)
- Practical learning > theoretical instruction
- Creates capability redundancy before Danny's departure
- Vrijen will be more independent for future issues

**Approach**: Staging environment deployment as training exercise

**Risk Mitigation**: Real codebase, non-production environment, expert guidance

**Timeline**: Immediate (post-call)

---

## Decision 4: Delay Non-Immediate Darwin Box Call to Next Week

**Decision**: First substantive Darwin Box call scheduled for "early next week" (not same day or tomorrow)

**Context**:
- Darwin Box is high-value acquisition target (billion-dollar company, multiple markets)
- Initial exploratory call with founder already occurred (went well)
- Team wants to appear prepared, not desperate

**Rationale**:
- "Give everyone a little bit of time and space... to iron out some more stuff in the go to market side" (Ilse's input)
- Narrative refinement needed for strong positioning
- Avoid signaling urgency to potential acquirer
- Allow product polish (current tasks) to finish

**Framing**: Delaying to strengthen negotiating position, not due to blockers

**Timeline**: Early next week (likely Monday or Tuesday)

**Preparation Activities**:
- Refine go-to-market messaging
- Ensure employer portal demo-ready
- Brief team on Darwin Box's business model and strategic fit

**Participants**: Vrijen, Logan, Ilse, possibly Ilya (pending participant count dynamics)

**Purpose**: Formal presentation of Careerspan technology and vision

---

## Decision 5: Allocate Ilya Sync to Separate Dedicated Session

**Decision**: Postpone Ilya's substantive update to later in the day with dedicated time allocation

**Context**:
- Vrijen wanted quick Ilya update within 9-minute remaining window
- Ilya pointed out insufficient time: "maybe it's better to carve out more than nine minutes for it"
- Vrijen has Rockle (1:1) call immediately after stand-up

**Rationale**:
- Quality > rushed briefing
- Ilya's update appears to be strategic/material enough to warrant full attention
- Vrijen's schedule has capacity later in day
- Prevents context-switching during Ilya's material

**Alternative Considered**: Include Ilya in stand-up more substantively (not taken)

**Implementation**: Reschedule to midday or afternoon when both have focus time

---

## Decision 6: Emory Rollout Sequencing

**Decision**: Meet with Emory tomorrow to finalize rollout plan; implement federal worker code same day

**Context**:
- Partnership with Emory to reach alumni community
- Special requirement: Access code for federal worker alumni cohort
- Code fix awaiting testing and deployment

**Rationale**:
- Meeting scheduled (can't reschedule)
- Show prepared/capable position to partner
- Demonstrate progress between calls

**Implementation Path**:
1. Emory meeting (tomorrow): Finalize rollout mechanics
2. Vrijen + Danny: Deploy code to staging and test during training session
3. Implication: Staging environment ready for Emory team to validate before production rollout

---

## Trade-offs & Opportunity Costs

| Decision | Opportunity Cost | Justification |
|----------|-----------------|---------------|
| Defer role detail pages | Marginally slower demo completeness | Unproven feature; deal breaker blocking Emory work |
| Bundle training with Emory work | Slightly slower deployment (paired vs. solo) | Long-term risk reduction (Danny departure) |
| Delay Darwin Box call | 1 week slower acquisition timeline | Stronger negotiating position through polish |
| Separate Ilya sync | Scheduling complexity | Quality of strategic conversation |

---

## Open Questions / Unanswered Aspects

1. **What specifically does Darwin Box want to see in a "cool shit we've built" demo?** (Framing remains flexible pending their input)
2. **What deal breaker questions will the Emory federal worker cohort have?** (May inform field design)
3. **Will Rockle's absence affect the Darwin Box call preparation?**
4. **How critical is the federal code fix vs. nice-to-have?** (Assumed critical; no contingency discussed)

