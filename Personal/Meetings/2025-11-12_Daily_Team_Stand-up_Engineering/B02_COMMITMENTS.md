---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B02: COMMITMENTS & ACTION ITEMS

## Explicit Commitments (Direct Quotes / Clear Intent)

### Danny Williams (Engineering)

| Commitment | Owner | Deadline | Status | Notes |
|-----------|-------|----------|--------|-------|
| Send staging/localhost link to Vrijen for employer portal testing | Danny | Immediate (same call) | **LIKELY COMPLETE** | Offered to send "local host link" then staging link with "staging" prefix |
| Investigate role detail breakdown implementation (skills/responsibilities deep dive pages) | Danny | TBD (deferred) | PENDING | Deferred in favor of current focus; marked as "sexy but unproven" |
| Review applicant deal breaker submission functionality | Danny | Before next Emory call | **CRITICAL** | Needs test user data to validate real-world input scenarios |
| Teach Vrijen backend deployment process on staging | Danny | Post-call session | **IMMEDIATE** | Knowledge transfer - given Danny leaves in ~1 month |

### Vrijen Attawar (CEO)

| Commitment | Owner | Deadline | Status | Notes |
|-----------|-------|----------|--------|-------|
| Send direct apply link to Danny for job testing | Vrijen | Immediate (same call) | **LIKELY COMPLETE** | Committed: "Give me a job link, give me a direct apply link and I'll just... My user" |
| Create test user with deal breakers on staging | Vrijen | Before Emory meeting (~24 hrs) | **CRITICAL** | Will populate system with realistic deal breaker data for Danny to validate |
| Learn backend deployment from Danny | Vrijen | Same day after call | **PRIORITY** | Knowledge transfer session to occur post-call; needed for Emory federal code rollout |
| Deploy code fix to staging | Vrijen | Before Emory meeting | **CRITICAL** | Deploy the ChatGPT-provided pull request to test Emory federal code fix |
| Schedule call with Darwin Box | Vrijen | Early next week | **IN PROGRESS** | First substantive conversation with billion-dollar acquisition target |

### Ilse Funkhouser (Operations)

| Commitment | Owner | Deadline | Status | Notes |
|-----------|-------|----------|--------|-------|
| Create dummy employer account for testing | Ilse | "Will do" (immediate) | **PENDING** | Will create account and explore employer portal; report findings |
| Share acquirer target database with team | Ilse | Recurring (already done for V) | ONGOING | Database of 15-20 potential acquirers being actively tracked |
| Coordinate Darwin Box call logistics | Ilse | Early next week | **IN PROGRESS** | Organize participant list, timing, preparation |

### Ilya Kucherenko (Engineering/Strategy)

| Commitment | Owner | Deadline | Status | Notes |
|-----------|-------|----------|--------|-------|
| Prepare for more detailed sync with Vrijen | Ilya | Later in day | **PENDING** | Deferred from stand-up; will sync later with more time allocation (9 minutes insufficient) |
| Provide input on Darwin Box call (optional participation) | Ilya | Early next week | CONDITIONAL | May join call depending on head-count dynamics |

---

## Implicit/Conditional Commitments

- **Deal breaker review implementation**: Danny indicated willingness to implement but also expressed desire to defer until test data available
- **Role detail pages**: Deferred but acknowledged as eventual feature; awaiting priority clarification
- **Emory federal code deployment**: Assumed to be deployed during Vrijen/Danny sync (though not explicitly re-stated)

---

## Dependency Chain

```
Emory Meeting Tomorrow
├── Vrijen creates test user with deal breakers (triggers)
├── Danny/Vrijen deployment training (needed)
├── Deploy federal code fix to staging (required)
└── Test deal breaker flow end-to-end (validation)

Darwin Box Call (Early Next Week)
├── Ilse confirms participant list (logistics)
├── Team refines go-to-market narrative (preparation)
└── Ensure employer portal demo-ready (readiness)

Team Knowledge Transfer (Immediate)
└── Vrijen learns backend deployment from Danny
    └── Prerequisite for Emory work & future independence
```

---

## Risk Flags

1. **⚠️ Single Point of Failure - Danny**: Only engineer with deployment knowledge; leaving in ~1 month
2. **⚠️ Time Pressure - Emory**: Meeting tomorrow; multiple blockers (code deploy + test data + knowledge transfer) must complete same-day
3. **⚠️ Unvalidated Features**: Deal breaker submission form untested with real data shapes
4. **⚠️ Bandwidth Split**: CEO dividing attention between engineering support + acquisition conversations

