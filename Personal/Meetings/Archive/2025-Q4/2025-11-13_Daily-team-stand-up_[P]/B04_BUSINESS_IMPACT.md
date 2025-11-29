---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B04: Business Impact & Risk Assessment

## Opportunity: User Acquisition Spike

**Trigger**: Job board announcement + LinkedIn strategy (weekly roundup of open roles)

**Historical Precedent**: Previous marketing campaign generated hundreds of daily new users

**Projected Impact**:
- User volume: Potential 500+ daily signups during spike
- Feature usage: Heavy application volume (expensive in terms of OpenAI/vibe-check costs)
- Revenue runway: Critical dependency on whether free tier can be economically sustained

**Confidence Level**: MEDIUM-HIGH  
*Rationale: Logan proven user acquisition capability; but platform features have evolved since last spike (story-telling, applications, vibe-checks didn't exist at that scale before)*

---

## Risk: Cost Spiral During Growth

**Severity**: CRITICAL (directly threatens runway)

**Mechanism**:
- If 500 daily users join + use application features, each user generates expensive OpenAI calls
- Feature cost is variable, not fixed; grows with usage
- Ilse flagged $10K/month OpenAI bill as plausible spike scenario

**Current State**: 
- Employer dashboard exists (bare bones)
- Applications feature is functional and in use
- Vibe-check system is operational but expensive

**Historical Comparison**:
- Previous spike month: Before applications existed; much cheaper cost profile
- Current platform: Feature-rich but cost-intensive

**Impact if Unmanaged**:
- Best case: Require premium tier; slow growth temporarily
- Worst case: Runway exhausted; company loses runway for team
- Nuclear options: Stop signups or disable core features (brand damage)

**Confidence in Risk**: HIGH  
*Rationale: Ilse explicitly flagged; team confirmed applications are expensive; Danny unavailable for engineering backup during spike window*

---

## Opportunity: Revenue Model Validation

**Trigger**: Stress-test results + potential free tier guardrail implementation

**Potential Models**:
1. **Direct Apply Forever Free**: Users can apply to Superposition/partner roles at no cost
2. **Premium Tier (N Applications)**: First 1-2 non-direct applications free; additional applications require payment
3. **Messaging Lever**: "Careerspan is free for believers; it costs if you don't believe"

**Market Fit Signal**:
- If users pay voluntarily for applications, validates demand
- If users abandon at paywall, signals premium tier is premature

**Financial Impact**:
- If implemented: Reduces unbounded cost exposure + generates revenue
- If not implemented: Scales risk; requires cost caps on free tier instead

**Alignment with Brand**:
- Mission-driven (help candidates) + sustainable (paid when value is proven)
- Narrative: "Free until you scale usage" is coherent storytelling

**Confidence in Opportunity**: MEDIUM  
*Rationale: Rochel's suggestion (1-2 free applications + then charge) is simple + aligns with B2B revenue model (we're already monetizing employers); but requires engineering to separate direct-apply from premium applications*

---

## Dependency: Engineering Resource

**Current State**:
- Danny: Core engineer, leaving in ~3 weeks (unavailable Nov 13-17)
- Ilse: Engineering + operations; stretched thin
- Rochel: Product/operations; not primary engineer

**Work Queued**:
1. Free tier guardrails (cost control)
2. Direct-apply gating (enable free tier without losing employer benefit)
3. Notification signup form (for "coming soon" roles)
4. Website messaging refresh (less AI-focused)

**Bottleneck**: Danny unavailable; no on-call backup identified yet

**Risk Mitigation**: Identify hourly contractor for on-call coverage + prioritize cost-control features over feature velocity

**Business Impact**: 
- If engineering is available: Can implement guardrails before spike; controlled growth
- If engineering unavailable: Must choose between growth (with cost risk) or caution (miss opportunity)

---

## Bottom Line: Opportunity vs. Risk Trade-off

| Scenario | Likelihood | Upside | Downside |
|----------|-----------|--------|----------|
| **Managed Growth** | 40% | User base scales; revenue model validated; runway extends | Requires tight engineering coordination |
| **Spike Without Guardrails** | 30% | Rapid growth; brand momentum | Cost spiral; runway compression; possible shutdown |
| **No Growth** | 20% | Cost stays predictable | Misses market window; morale hit |
| **Partial Spike** | 10% | Moderate growth; learning opportunity | Suboptimal: misses upside but still carries risk |

**Team Consensus**: Pursue managed growth (stress-test + guardrails) rather than unmanaged spike or no growth.


