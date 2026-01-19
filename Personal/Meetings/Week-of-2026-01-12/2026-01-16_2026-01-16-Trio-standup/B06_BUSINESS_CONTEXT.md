---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: 074838b3-3b6f-4e5c-a843-858a7d072141
---

# B06 - Business Context

## Company: Apply AI / Careerspan

**Product:** AI-powered candidate matching and assessment platform

**Business Model Signals:**
- B2B SaaS - employers are the paying customers
- Credit-based pricing (concern about credit allocation)
- Scanning costs money (API/compute costs per scan)
- Feature differentiation for paying vs. free users

## Feature Context: Silent Database Scanning

### What It Does
- Employers scan the candidate database without candidates knowing
- System evaluates candidates against role requirements
- Auto-apply submits qualified candidates automatically
- Threshold system controls what candidates see/get

### Revenue Implication
- Premium feature for paying customers
- Requires careful cost management (250 day cap)
- Could drive employer retention if results are good

### Competitive Positioning
- "Silent scan" = proactive sourcing without candidate friction
- Different from job boards where candidates must apply first
- Automation reduces manual recruiter work

## Technical Infrastructure Notes
- Role publishing is required before scanning works
- Access control checks happen before scans start
- Duplicate scan prevention is in place
- CSV export pipeline exists but is minimal

## Customer Communication Approach
- Casual, transparent email tone ("that's their problem now")
- Clear labeling of silent vs. public scans
- Candidate-friendly even when candidates aren't notified
