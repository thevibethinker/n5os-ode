# OUTSTANDING_QUESTIONS

---
**Feedback**: - [ ] Useful
---

## Open Items Requiring Resolution

### 1. Revenue share commercial terms not yet defined

**Question:** What percentage kickback does Ash's platform offer partners, and what triggers payment (placement event vs. 12-month retention vs. billing collection)?

**Owner:** Ash (to provide) + Vrijen/Logan (to evaluate)

**Needed by:** Next co-founder call (target: within 2 weeks)

**Blocker type:** NEEDS_DECISION (commercial terms required before legal/technical work can proceed)

**Unblocking action:** Ash to prepare revenue share proposal showing percentage structure, payment timing/triggers, minimum volume thresholds if any, and comp examples from existing partners

**Impact if delayed:** Cannot move to NDA/legal phase without understanding economics; partnership remains exploratory rather than implementable

---

### 2. Technical integration requirements and data schema alignment unclear

**Question:** What specific data fields does Ash's matching system require (beyond resume), and what API/data transfer format does their platform expect?

**Owner:** Ash's technical team (to specify) + Careerspan head of AI (to implement)

**Needed by:** Technical deep-dive call (after initial co-founder alignment)

**Blocker type:** UNCLEAR_REQUIREMENT (cannot build integration without knowing target schema)

**Unblocking action:** Schedule technical call with Careerspan head of AI and Ash's engineering lead to document data requirements, API specifications, authentication approach, and test integration workflow

**Impact if delayed:** Could discover incompatibility late in process; vague requirements lead to integration rework and launch delays

---

### 3. LinkedIn profile enrichment gap in Careerspan data capture

**Question:** Does Careerspan need to add LinkedIn profile URL capture, or can Nira partnership solve this, or is there alternative enrichment approach?

**Owner:** Vrijen (to evaluate Nira capability) + Ash (to clarify criticality)

**Needed by:** Before first candidate batch handoff (can be parallel to integration work)

**Blocker type:** DEPENDENCY (depends on Nira partnership status and Ash's data requirements flexibility)

**Unblocking action:** 
- Vrijen to confirm with Nira if they can enrich Careerspan candidate profiles with LinkedIn data
- Ash to clarify if LinkedIn is required field or nice-to-have
- Evaluate whether manual enrichment acceptable for pilot phase

**Impact if delayed:** May limit candidate batch quality/usefulness; could force Careerspan to add LinkedIn capture to onboarding flow (product change)

---

### 4. VC-backed startup identification capability needed for candidate filtering

**Question:** Can Careerspan's AI identify and flag which companies on candidate resumes are VC-backed startups vs. other company types?

**Owner:** Careerspan head of AI (to implement) + Ash (to provide filtering criteria)

**Needed by:** Before first candidate batch (required for Ash's 2+ year startup experience filter)

**Blocker type:** WAITING_ON_DATA (need Crunchbase/Tracxn API access and fuzzy matching logic)

**Unblocking action:**
- Research Crunchbase and Tracxn API pricing and capabilities
- Build company enrichment layer that queries APIs during resume parsing
- Define startup classification rules (stage, funding status, employee count thresholds)

**Impact if delayed:** Cannot meet Ash's core candidate filter (2+ years startup experience); would require manual review of candidate work history or passing unqualified candidates

---

### 5. Candidate communication ownership and handoff protocol undefined

**Question:** At what point does candidate communication transfer from Careerspan to Ash's platform, and who owns candidate experience at each stage?

**Owner:** Both teams (collaborative definition needed)

**Needed by:** Before pilot launch (must avoid duplicate outreach or candidate confusion)

**Blocker type:** UNCLEAR_REQUIREMENT (operational workflow not yet mapped)

**Unblocking action:** 
- Document candidate journey map showing all touchpoints
- Define exactly when "pulse check" happens (Careerspan) vs. when "match report" sent (Ash)
- Clarify candidate opt-in/consent mechanism (do they know they're being shared with partner?)
- Establish communication templates and branding (co-branded vs. separate)

**Impact if delayed:** Risk of candidate confusion, duplicate outreach, or negative experience if both platforms contact same candidate without coordination

---

### 6. NDA scope and legal framework for partnership not yet initiated

**Question:** What IP protections, data sharing terms, exclusivity provisions, and liability allocations should the discussion NDA cover?

**Owner:** Legal teams on both sides

**Needed by:** Before sharing detailed technical specs or candidate data (target: 2 weeks)

**Blocker type:** DEPENDENCY (legal review required before deep integration work)

**Unblocking action:**
- Both parties to engage legal counsel
- Draft mutual NDA covering: candidate data privacy, matching algorithm IP, non-solicitation of candidates/employees, term length, dispute resolution
- Review and execute before technical integration begins

**Impact if delayed:** Cannot share sensitive information (candidate PII, algorithm details, financial terms) without legal protection; delays entire partnership timeline
