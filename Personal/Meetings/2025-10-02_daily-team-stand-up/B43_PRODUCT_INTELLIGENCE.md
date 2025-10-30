# PRODUCT_INTELLIGENCE

---

## Product Strategy

**Game Plan Migration Philosophy**:
- Remove `target_job` field (single job target from onboarding)
- Align `role_match_score` with `role_preferences` (broader interest profile)
- Users can now express: specific role interests + openness to other good fits
- Migration applied: Add target_role as initial role_interest + "open to more roles that you think are a good fit"

**B2C Complexity vs. B2B Focus Tension**:
- Product has B2C features (salary filtering, location preferences, role interests)
- Business model shifting toward B2B (companies pay for candidate vetting)
- Strategic decision: Don't over-invest in B2C complexity if B2B is the path [B40.D2]

---

## Feature Decisions

**Salary Requirements Handling** [B40.T2]:
- **Approach**: Text input (not structured bands)
- **Why**: Captures role-dependent salary expectations ("$300k for head of product on-site, $200k if remote, $150-180k for project management")
- **Cost consideration**: Semantic parsing is expensive, but current user base is small and B2B model covers costs
- **Filtering logic**: 
  - Hard requirements (location, salary floor) → cut off early in cheap pre-filter
  - Soft requirements → reflected in role_match_score
  - If role_match_score is low enough, skip expensive full analysis
  - User opt-in (magic link) always overrides filters

**AI Confidence & Gender Features** [B40.T3]:
- **Status**: Delayed
- **Reason**: Game plan migration is higher priority

---

## Technical Approach

**Role Matching Evolution**:
- Old: Match against single `target_job` from onboarding
- New: Match against `role_preferences` (flexible multi-role interests)
- Benefit: Users aren't locked into initial onboarding choice
- Cost: More complex matching logic

**Salary Filtering Architecture**:
- Parse salary requirements once per user (not per job)
- Store structured interpretation: role-dependent salary bands
- Cheap filter: "Is salary clearly outside range?" → Yes = skip full analysis
- Expensive filter: Semantic parsing for nuanced matching

---

## User Experience

**Onboarding Updates**:
- User sees: "Role interest, salary requirements, location preferences, other preferences"
- All editable in settings after onboarding
- Text input encourages natural language expression

**Settings Management**:
- Users can directly edit preferences post-onboarding
- PostHog integration planned [T6] to track preference changes
- Loops sync planned [T6] for email communication

---

## Technical Debt / Bugs

**T7 - Resume Transcription Timeout Bug (Staging)** [B41.A4]:
- **Symptom**: Unable to edit job history, "Bad request for update job" error
- **Hypothesis**: First transcription try timed out, second try initialized, first try completed → data mismatch between Firestore and backend
- **Status**: Under investigation (Danny)
- **Environment**: Staging only (so far)

**T6 - PostHog + Loops Integration Cleanup** [B41.A3]:
- **Need**: Backend must send updated user preferences to PostHog
- **Downstream**: Then setup PostHog → Loops sync for email campaigns
- **Status**: Not started (Ilse's backlog)
