---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Decisions Made

## Product & UX Decisions

### 1. Candidate Feedback Display (Deferred to Future)
**Decision**: Hold on displaying "How I Want to Be Represented" feedback to employers at this time.
- **Rationale**: Employer portal launched before employer feedback loop was established; risk of unhappy candidates if assessment misses nuances, but better to iterate based on real usage
- **Owner**: Ilse to determine workflow timing
- **Timeline**: Post-launch monitoring for pain signals

### 2. Elevator Pitch Wording Update
**Decision**: Potentially rename "Elevator Pitch" to "Who Are You Getting?" or "Why You Should Say Yes/No" 
- **Rationale**: Current third-person framing doesn't reflect actual candidate voice; better option is actionable summary showing recruiter intel rather than false authenticity
- **Contingency**: Only implement if change takes <1 hour; otherwise deprioritize
- **Approval Process**: V and Ilse to align on final label

### 3. Information Architecture - Above-the-Fold Design
**Decision**: Confirmed that everything needed to make a hire/pass decision appears without scrolling.
- **Components Above Fold**: Deal breakers, overall score, radar graph, elevator pitch, bottom line, stories told count
- **Rationale**: Time-to-hire is critical; recruiters won't scroll through pages
- **Validation**: V approved current layout hierarchy

### 4. Deal Breakers Display Format
**Decision**: Keep current phrasing (red items) but may shift to bullet points instead of paragraphs.
- **Consideration**: Maximize readability for rapid scanning
- **Status**: To be revisited if feedback indicates readability issues

### 5. Uniqueness Axis Documentation
**Decision**: Hold detailed reasoning paragraphs on uniqueness scoring for on-request delivery.
- **Rationale**: Uniqueness can be misinterpreted; need credible explanation for each candidate before rolling out to all employers
- **Implementation**: Part of trial period deep-dive package
- **Risk**: Employers will challenge "what does uniqueness mean?" - must be prepared with concrete examples

## Career Coaching Integration Decision (Conceptual)

**Decision**: Three-way marketplace feature requires study before implementation.
- **Opportunity**: Career coaches viewing candidate applications + identified weaknesses creates mutual reinforcement loop
- **Current Gap**: Career coaching app cannot see job applications or performance assessment from employer side
- **Next Step**: Discuss feasibility and business model with Ilya and Logan
- **Status**: Noted as strategic opportunity but not committed to roadmap

## Demo/Trial Onboarding Decisions

### 1. Dummy Account Setup for Employer Demos
**Decision**: Use fake employer accounts pre-populated with candidates for trial periods.
- **Manual Process**: Change names/emails of sample candidates to anonymize before showing
- **Timeline**: Couple days for full anonymization (not required for V's tomorrow demo)
- **For Tomorrow**: V will create fake accounts programmatically with fake stories for demo

### 2. Test Role Specification
**Decision**: V to create illustrative test role (fake company name, real-world relevant position).
- **Criteria**: Remote position; high-signal qualitative + hard skills; relevant to Careerspan user base
- **Population**: Ilse will run against 100-200 candidate pool (~$200 cost) to generate sample applications
- **Reusability**: Once anonymized, will copy/paste into future employer demo accounts

### 3. Demo Recording Timeline
**Decision**: Record demo this evening or tomorrow morning after groundwork complete.
- **Executor**: V with Ilse's async support
- **Input Needed from V**: Job description + employer account credentials
- **Input Needed from Ilse**: Population of candidates into demo account while V sleeps

### 4. Employer Account for Demo
**Decision**: Create fresh employer account distinct from the initial walkthrough account.
- **Vs. Alternative**: Not reusing the account from this call
- **Communication**: V to send Ilse account details + JD

## Validation Decision: Ordinal Ranking vs. Trade-Offs

**Decision**: Confirmed spider graphs + baseball card format can enable trade-offs-based hiring.
- **Feedback Source**: Positive market response; folks want to move beyond "best candidate" framing
- **Capability**: Data infrastructure already supports multi-dimensional comparison
- **Current Blocker**: Engineering resource constraints + prioritization of time-to-hire
- **Go-to-Market Strategy**: Frame comparative analysis as premium feature for trials; build on-demand when requested
- **Benefit**: Unique differentiator vs. ATS vendors

## Cost-Related Acceptance

**Decision**: Accept current $3/candidate cost as acceptable for market entry.
- **Rationale**: Optimization levers exist but unclear which matter; better to ship and learn
- **Optimization Path**: Use cheaper models, selective prompting, batch processing
- **No Action**: V approved moving forward without optimization before launch

## Messaging & Positioning Decisions

### 1. "Bangers Only" Positioning
**Decision**: Be honest that candidates aren't pre-filtered to superhuman quality.
- **Current Claim**: Careerspan only surfaces good candidates (implied high bar)
- **Reality**: System surfaces everyone; employers benefit from detailed assessment, not filtering
- **Correction Needed**: Update positioning from "only bangers" to "see everyone with deep context"
- **Benefit**: Avoids false promises; sets correct expectations

### 2. Recruiting Market Context: Signal Quality Decline
**Decision**: Lean into observed market trend in positioning.
- **Trend**: Screening volume up, signal quality down across industry
- **Positioning**: Careerspan reverses this by surfacing actionable intel (why say yes/no)
- **Validation**: V confirmed talking to multiple recruiters who confirmed trend

## Offboarding & Staffing Decisions

**Decision**: Continue offboarding with existing operator (Danny) while onboarding new $80/hour operator.
- **Priority**: Stability via existing relationship > aggressive new headcount onboarding
- **Owner**: Ilse coordinating transitions
- **Timeline**: Parallel process, not sequential

## Payments & Monetization (Flagged for Future)

**Decision**: Explicitly flagged as major unanswered question to discuss with Ilya and Logan.
- **Open Questions**: Who pays? How much? Free trial depth? Feature gating?
- **Status**: Not decided in this call

