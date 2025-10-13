# B31_STAKEHOLDER_RESEARCH

---

**Perspective:** Internal operations & engineering (Careerspan team)

### Insight 1: Responses API migration introduces background-mode tradeoffs
- Evidence: Ilse described background mode and connectivity/timeouts issues (00:04–04:06)
- Why it matters: Background mode mitigates token/timeouts but requires monitoring and may increase operational complexity
- Signal strength: ● ● ● ○ ○

### Insight 2: Persisting lead-distribution state improves user coverage
- Evidence: Ilse's plan to track which users have been checked/sent for a role in Firestore (06:07–07:27)
- Why it matters: Reduces lost impressions for newly signed users; improves product reliability and candidate reach
- Signal strength: ● ● ● ● ○

### Insight 3: Operational changes can produce unit-cost savings
- Evidence: Ilse mentioned "It'll save us like 30 cents per user" (07:27)
- Why it matters: Small per-user savings scale; justifies engineering effort for caching/efficiency
- Signal strength: ● ● ○ ○ ○

### Insight 4: Events are tactical marketing & networking assets
- Evidence: Discussion about Danny's panel and capturing photos (09:43–10:21)
- Why it matters: Events offer reusable assets and networking leads; plan for asset capture should be explicit
- Signal strength: ● ● ○ ○ ○

---

**Action:** Update internal product/ops doc with Firestore lead-tracking design and monitoring checklist

**Feedback**: - [ ] Useful
