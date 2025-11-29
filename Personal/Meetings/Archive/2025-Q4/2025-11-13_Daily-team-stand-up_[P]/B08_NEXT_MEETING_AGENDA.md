---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B08: Next Steps & Follow-up Agenda

## Immediate (This Week)

### Financial Stress-Test
- **Owner**: Vrijen + Logan (strategy); Ilse (projections)
- **Input Needed**: 
  - Financial baseline (current runway, burn rate)
  - Cost scenarios (median usage vs. 500 daily users at max engagement)
  - Historical data (previous acquisition spike: how many users, what was cost profile?)
- **Output Needed**: 
  - Decision point: "At what user/cost level do we need to implement guardrails?"
  - Timeline: "How many days of runway buffer do we need before implementation?"
- **Deferral Trigger**: If stress-test shows guardrails unnecessary, can proceed without engineering work (acceleration win)
- **Escalation Trigger**: If stress-test shows cost spiral is unavoidable, need emergency engineering decision immediately

### Engineering Resource Identification
- **Owner**: Ilse
- **Action**: Identify on-call engineering backup to cover Danny (Nov 13-17 absence + permanent departure)
- **Criteria**: Hourly rate; availability; capability (Python/backend, not frontend)
- **Decision**: Budget approval from Vrijen
- **Timing**: Should be identified before big growth push (safety net first)

### Job Board Readiness Check
- **Owner**: Rochel (operations); Ilse (technical)
- **Checklist**:
  - ✓ Extraneous video removed from Notion
  - ✓ Job board message clarity (direct-apply distinction)
  - [ ] "Coming soon" role functionality (placeholder roles show correctly)
  - [ ] Notification signup mechanism assessed (SendGrid vs. Loops) [nice-to-have]
- **Decision Gate**: Can we launch job board announcement with current functionality, or does it need work?

### Direct-Apply Employer Confirmation
- **Owner**: Vrijen
- **Action**: Get verbal OK from Marvin (Superposition) on: go-to-market engineer, forward-deploy engineer roles
- **Output**: List of JDs; confirmation that Careerspan can post with "apply direct" link
- **Use Case**: Proof point for LinkedIn announcement ("Superposition uses Careerspan for technical hiring")

## Next Week (Post-Stress-Test)

### LinkedIn Announcement Strategy
- **Owner**: Logan (primary); Vrijen (approval)
- **Input Needed**: 
  - Stress-test results (do we need guardrails?)
  - Job board readiness (what's our first job posting list?)
  - Employer confirmation (Superposition + others?)
- **Execution**:
  - If guardrails needed: Announce guardrails in messaging ("start free, go premium if you scale")
  - If no guardrails needed: Announce as "full free access" or "always free for direct apply"
  - Cadence: Weekly job roundup proposal (vs. one-time blast)
  - Channel: Personal LinkedIn posts from team + Careerspan company page

### Free Tier Implementation (If Needed)
- **Owner**: Ilse + Danny + (new on-call engineer)
- **Scope**: 
  - Direct-apply gating (always free)
  - Non-direct application limit (1-2 free, then paid)
  - Cost monitoring dashboard (to trigger guardrails if needed)
- **Priority**: Highest (cost control)
- **Timing**: Must be ready before big growth push
- **Risk**: If Danny unavailable, may need to delay or bring in contract engineer

### Website Messaging Refresh
- **Owner**: Logan (strategy); Rochel (ops)
- **Scope**: 
  - B2B page: Less AI-focused, more "employer benefits" focused
  - Job board page: Clear distinction between direct-apply and premium
  - Messaging: "Skip the ATS" positioning instead of "behavioral profile"
- **Priority**: Medium (can be done in parallel with other work; not blocking launch)

### Notification System Exploration
- **Owner**: Rochel
- **Scope**: Assess SendGrid vs. Loops for "coming soon" role email alerts
- **Decision Gate**: Is this a must-have for launch, or can we iterate later?
- **Output**: Tech decision + rough implementation estimate
- **Priority**: Low (nice-to-have; not blocking launch)

## Two Weeks Out (Late November)

### Post-Launch Analysis
- **Metrics to Track**:
  - New user acquisition rate
  - Application feature usage (cost vs. revenue)
  - Conversion rate (applications → placements)
  - Free vs. paid tier split
- **Decision Point**: "Is managed growth actually working? Do we need to accelerate or pull back?"

### Revenue Model Validation
- **Question**: Are users paying for applications? At what rate?
- **If Yes**: Premium tier is viable; scale pricing
- **If No**: Need different monetization; return to drawing board
- **Data Needed**: Cost per application + revenue per application (to validate profitability)

### Team Retrospective
- **Focus**: What did we learn from growth spike?
- **Topics**:
  - Did guardrails work (or did they block growth unnecessarily)?
  - Was engineering bandwidth sufficient?
  - Did messaging resonate?
  - What would we do differently next time?

## Ongoing

### Weekly Financial Review
- **Owner**: Ilse
- **Cadence**: Weekly or triggered (if costs spike)
- **Input**: OpenAI spend, user count, application count
- **Decision**: "Do we need to dial back growth or implement guardrails?"

### Weekly Product Sync
- **Owner**: Rochel + Vrijen
- **Cadence**: Weekly
- **Topics**: Feature readiness, bug fixes, messaging alignment

### Employer Pipeline
- **Owner**: Vrijen
- **Cadence**: As-needed (partners onboarded)
- **Topics**: New partnerships, job posting cadence, revenue splits

## Decision Dependencies

```
Stress-Test Results
├─ IF costs are manageable (< $5K/month for 500 users)
│  ├─ Launch without guardrails
│  ├─ Focus on growth messaging
│  └─ Monitor and stay ready to implement
│
└─ IF costs are concerning ($10K+/month for 500 users)
   ├─ Implement guardrails before launch
   ├─ Prioritize direct-apply gating engineering
   └─ Focus on managed growth messaging ("start free, premium if you scale")
```

## Parking Lot (Not This Sprint)

- Advanced analytics (can wait)
- Story AI enhancements (can wait)
- Mobile app (can wait)
- New interview formats (can wait)
- Salary negotiation features (can wait)

**Rationale**: Focus on cost control + growth readiness before adding features


