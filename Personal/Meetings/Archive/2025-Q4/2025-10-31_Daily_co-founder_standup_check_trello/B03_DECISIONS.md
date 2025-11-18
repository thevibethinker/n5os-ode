---
created: 2025-10-31
last_edited: 2025-11-16
version: 1.0
---

# B03_DECISIONS

## Major Strategic Decisions

### Product Direction Pivot (CONFIRMED DECISION)
**Decision**: Shift Careerspan product focus from AI-powered career planning to job-seeking orientation

**Rationale**: 
- Core insight: AI-powered career planning is insufficient because end users lack self-knowledge
- Market positioning: Direct job-seeking support addresses more immediate user pain point
- Functional preservation: Self-reflection and conversation engine capabilities maintained as foundation

**Timeline**: Already executed; product has "very much changed"

**Status**: Implemented, ongoing refinement

**Impact**: 
- Redirects product roadmap and go-to-market messaging
- Changes feature prioritization (job application tools over generic career exploration)
- Affects user education and onboarding flows

### Resume Delivery Mechanism (CONFIRMED DESIGN DECISION)
**Decision**: No native word document download feature; instead guide users to external AI tools for formatting

**Rationale**:
- User empowerment: Allows selective content curation before inclusion in resume
- Flexibility: ChatGPT/Google Docs integration provides formatting without vendor lock-in
- Design philosophy: Conscious choice favoring user control over one-click convenience

**Status**: Current design; user accepted with apology for inconvenience

**Risk Assessment**: May reduce user satisfaction short-term; long-term benefit depends on adoption of suggested workflow

**Future Consideration**: Could implement native download if user feedback indicates high friction

### Presentation Strategy (DECISION IN PROGRESS)
**Decision Framework**: Preparation needed for high-stakes presentation with influential stakeholders

**Context**: Vrijen to "demo my stuff" to important decision-makers; currently stressed about execution

**Implied Decisions Pending**:
- Which product features/story will be demoed
- How job-seeking pivot will be positioned to stakeholders
- Timing and resource allocation for preparation

**Status**: Not finalized; requires clarification in follow-up communication

## Decision Dependencies & Follow-ups

| Decision | Status | Dependency | Follow-up Needed |
|----------|--------|-----------|------------------|
| Product pivot to job-seeking | ✓ Confirmed | None | Validate market response |
| Resume workflow design | ✓ Confirmed | Feedback threshold | Monitor user adoption friction |
| Presentation approach | ⏳ In-flight | Stakeholder priorities | Clarify scope & key messages |

## Risk/Assumption Analysis

**Assumption**: Resume manual workflow (copy to ChatGPT) is acceptable to users
- Risk: If adoption is low, may need to implement native download despite design philosophy
- Mitigation: Monitor user feedback and iteration trigger point

**Assumption**: Job-seeking pivot aligns with market demand
- Risk: If early users reject focus, significant product re-architecture required
- Mitigation: Early user validation recommended before major feature development

## Approval Status
All decisions made by Vrijen in solo standup context; no multi-stakeholder approval documented. Co-founder alignment assumed but not explicitly confirmed.

