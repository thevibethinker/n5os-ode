---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B03: Decision Logic & Trade-offs

## Job Board Strategy

**Problem Statement**: Need to announce new employer partnership model to drive both user acquisition and employer awareness, but current job board is either empty or confusing.

**Decision Tree**:
```
Do we populate the board?
├─ YES (chosen)
│  ├─ With real roles only? NO
│  ├─ With mixed real + coming soon? YES
│  ├─ Add notification signup? YES (Rochel exploring)
│  └─ Why? Perception matters; signals active hiring; captures emails for future
│
└─ NO (rejected)
   └─ Why? Misses visibility opportunity; messaging lands better with active board
```

**Trade-off Accepted**: Some "coming soon" roles create friction if candidates click and find placeholder. Mitigation: Clear messaging about when roles open + ability to be notified.

---

## Application Costs & Free Tier

**Problem Statement**: If user acquisition succeeds, OpenAI/vibe-check costs could bankrupt runway. Need guardrail but maintain free-to-user promise.

**Decision Tree**:
```
How to protect costs?
├─ Stop signups? NO (nuclear option; kills growth)
├─ Pull OpenAI key? NO (nuclear option; kills app functionality)
├─ Hard cap on free tier? YES (pending financial review)
│  ├─ Free direct apply only? PARTIAL (still needs engineering)
│  ├─ Free tier: 1-2 applications? YES (Rochel's suggestion)
│  └─ Premium tier: after N applications? YES (aligned with funding narrative)
│
└─ Monitor and respond? YES (parallel track; 1-3 day response latency)
```

**Trade-off Accepted**: Monetization requires engineering work; adds complexity to messaging. Benefit: Protects runway + aligns with "mission-driven but sustainable" brand.

---

## Direct Apply Priority

**Problem Statement**: Different features have different cost profiles. Direct apply (to Superposition, etc.) doesn't use vibe checks; other applications do.

**Decision**: Direct apply stays free forever. Other applications get gated after N free attempts.

**Rationale**: 
- Aligns GTM with "good candidates, we get cut of the hire" model
- Doesn't punish candidates for using employer partnerships
- Cleaner value prop: "Apply directly to our partners for free; use Careerspan's vibe-check analysis for other roles at cost"

**Risk**: Requires engineering to separate application types. If not implemented, either all applications are gated (kills direct apply benefit) or none are (no cost control).

---

## Candidate Self-Selection

**Problem Statement**: Some candidates hesitant to tell stories preemptively; team wants to know if this is a feature or a problem.

**Decision**: Treat hesitation as self-selection signal. Focus messaging on believers; don't apologize for the ask.

**Rationale**:
- Candidates who "get it" (understand story value) become stronger candidates anyway
- Friction for non-believers reduces mediocre submissions
- Messaging shift: "Strong candidates prepare stories" vs. "We want your stories"

**Risk**: Might reduce total candidate volume. Benefit: Higher quality + stronger brand alignment.

---

## Engineering Resource Constraint

**Problem Statement**: Danny leaving in 3 weeks (unavailable Nov 13-17, then permanent). Major features (free tier guardrails, direct-apply gating) need engineering.

**Decision**: Identify on-call backup for Danny coverage; prioritize cost-control engineering over feature work.

**Rationale**:
- If user acquisition succeeds but costs spiral, runway dies
- Better to be conservative (limit growth temporarily) than to bankrupt
- On-call coverage at hourly rate cheaper than emergency engineering later

**Risk**: Delays other features. Benefit: Prevents existential cash flow crisis.


