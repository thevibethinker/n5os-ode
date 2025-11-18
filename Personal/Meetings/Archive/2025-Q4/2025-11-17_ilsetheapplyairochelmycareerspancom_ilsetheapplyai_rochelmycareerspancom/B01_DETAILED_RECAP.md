---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Detailed Recap: Careerspan Employer Portal Demo

## Overview
V and Ilse conducted an extended walkthrough of the Careerspan employer onboarding and candidate evaluation system. The session covered the complete workflow from adding an employer account through publishing a role and reviewing applications from the candidate perspective.

## Core Process Flow

### Employer Account Setup
- Navigate to Employers section and click "Add Employer"
- Use employer email format (e.g., virgin+employer@mycareerspan.com) with company name
- Generate password reset link with special consideration for users who already have Careerspan accounts
  - **Critical UX Note**: Use incognito mode when clicking reset links to avoid account confusion
  - Password reset URL initially appears wrong (app.mycarespan.com vs employer.mycareerspan.com) but auto-corrects after setup

### Role Creation Workflow
1. Employer navigates to add role
2. System generates comprehensive job analysis:
   - Assessment criteria breakdown
   - Hard skills ranked by importance (critical/important/nice-to-have)
   - Soft skills identified and prioritized
   - Role responsibilities extraction
3. Processing time: 4-8 minutes depending on OpenAI availability
4. Pre-publishing review: Employer can edit role description before publishing

### Role Publishing & Candidate Application
1. Publish role from draft mode
2. Share direct apply link with candidates
3. Candidate runs through full application process:
   - Resume upload (optional)
   - Deal breaker questions addressing job requirements
   - 30-second processing to sync candidate data with employer portal

## Candidate Evaluation Portal

### Key Candidate Information Displayed
- **Bottom Line**: Summary recommendation (not recommended/proceed with caution/recommended)
- **Deal Breakers**: Red-flagged items where candidate answered "no"
- **Spider Graph**: Multi-dimensional radar chart showing strengths across 5 key dimensions
- **Overall Score**: Composite fit rating
- **Elevator Pitch/Narrative**: AI-generated candidate summary
- **Experience Section**: Job history organized chronologically (with known sorting issues being fixed)
- **Hard/Soft Skills**: Ranked by importance with expertise level indicators
- **Achievements**: Context-specific list pulled from candidate stories

### Above-the-Fold Critical Information
Ilse intentionally designed the portal so decision-critical information appears without scrolling:
- Stories told count
- Career trajectory signals
- Referral source
- Deal breakers
- Overall score
- Radar graph
- Bottom line
- Narrative summary

### Data Richness
- System has generated substantial detail for every candidate (estimated 100+ pages per person)
- Available on-demand: achievement breakdowns, skill trade-offs, expertise level demonstrations
- Currently waiting for user request triggers before surfacing additional depth

## Key UX Decisions

### "How I Want to Be Represented" Feedback
- Currently NOT displayed to employers
- Gap identified: candidates can indicate assessment disagreement/provide context, but employers never see this
- Risk: Short-term unhappy candidates if assessment misses nuances
- Future: Need workflow to surface candidate feedback to employers

### Naming/Labeling Evolution
- "Elevator Pitch" being reconsidered:
  - Ilse concerned about inauthentic voice if rewritten to first-person
  - Proposed alternative: "Who Are You Getting?" or "Why You Should Say Yes/No"
  - Rationale: Recruiter needs actionable intel, not polished pitch

### Uniqueness Scoring
- Spider graph includes "uniqueness" as an axis
- Ilse has supporting reasoning documentation but hasn't surfaced yet
- Future implementation: Provide context around what uniqueness means for each candidate

## Technology & Performance Notes

### Cost Structure
- ~$3 per candidate for full application processing (5-6 stories)
- No cost optimization yet; prioritized getting product to market
- OpenAI timeout issues add 2-3 minutes unpredictably
- Trade-off: Wait for completion to avoid incomplete charge, or risk charges for timeouts

### Processing Observations
- Longest job description generation: 8 minutes (unusual)
- Typical JD generation: 4-5 minutes
- Employer data sync: ~30 seconds
- System tracks clicks vs applications but doesn't display click data yet

## Multi-Dimensional Comparison Capability

### Current State
- Spider graphs display 5 key dimensions per candidate
- All candidates scored across 30+ dimensions (hard skills, soft skills, responsibilities)
- Expertise levels tracked separately (basic/intermediate/advanced)

### Unrealized Potential
- Could create side-by-side radar graph comparisons
- Could export 30-dimension spreadsheet comparisons
- Baseball card comparison format discussed as compelling differentiator
- **Current Blocker**: Time-to-hire pressure means comprehensive analysis isn't priority yet
- **Strategy**: Hold this as demo feature for trial periods when prospect requests deeper analysis

## Employer Onboarding Approach

### Smooth Path Forward
- Don't require employers to create accounts before role publication
- Use dummy employer accounts for setup
- Pre-populate with demo candidates before employer login
- Two options:
  1. Request job description first, pre-populate with demo applicants
  2. Have employer provide name/email/company/JD, system handles account creation

### Trial/Demo Strategy
- 30-minute trial or 1-week demo periods
- Demo role: Real or realistic role with fake company name
- Pre-populated with 3-5 high-quality candidates
- On-request: Full 96-page detailed analysis of any candidate
- On-request: Comparative spreadsheet analysis if prospect requests
- Goal: Prove depth without forcing complex interface on busy decision-makers

