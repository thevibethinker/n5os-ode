---
created: 2025-11-14
last_edited: 2025-11-14
version: 1.0
---

# B04: RISKS, DEPENDENCIES & CONSTRAINTS

## Critical Path Dependencies

### Chain 1: Emory Rollout (Tomorrow)
```
Vrijen creates test user + deal breakers
        ↓
Danny/Vrijen deploy training session + code deploy
        ↓
Staging environment tested & validated
        ↓
Emory meeting: demonstrate readiness
        ↓
Production rollout clearance
```

**Timeline**: All steps must complete same day (Nov 12/13)  
**Critical Dependency**: Danny's availability for training  
**Failure Mode**: If code deployment fails or test data insufficient, must either delay Emory meeting or launch without deal breaker feature

---

### Chain 2: Darwin Box Acquisition Conversation (Early Next Week)
```
Team refines go-to-market narrative
        ↓
Employer portal reaches demo-ready state
        ↓
Participants prepared (Vrijen, Logan, Ilse, possibly Ilya)
        ↓
Formal call scheduled + executed
```

**Timeline**: Narrative work + demo polish complete by start of week  
**Critical Dependency**: Product remaining feature-complete; employer portal not regressing  
**Failure Mode**: Poor demo or internal confusion re: talking points undermines billion-dollar negotiation

---

### Chain 3: Knowledge Transfer (Immediate)
```
Danny teaches Vrijen backend deployment
        ↓
Vrijen successfully deploys federal code to staging
        ↓
Emory code ready for production (Vrijen can handle independently)
        ↓
Future deployments don't require Danny after departure (in 1 month)
```

**Timeline**: Must occur today/tomorrow  
**Critical Dependency**: Danny available + focused teaching time  
**Failure Mode**: Vrijen lacks deployment capability after Danny leaves; all deployments become single-threaded bottleneck

---

## Resource Constraints

| Resource | Current State | Implications |
|----------|---------------|--------------|
| **Danny (Engineering)** | Only engineer; leaving in ~1 month | Single point of failure for backend; knowledge transfer urgent |
| **Vrijen (CEO)** | Wearing multiple hats (product, sales, now DevOps) | Bandwidth split across engineering support + Darwin Box BD + Emory partnership |
| **Ilse (Operations)** | Managing acquirer pipeline + day-to-day ops | Limited capacity for hands-on technical work |
| **Ilya (Engineering)** | Appears underutilized in stand-up; sync deferred | Potential capacity available but engagement model unclear |

---

## Identified Risks

### 🔴 CRITICAL RISKS

**Risk 1: Deployment Knowledge Silos**
- **Owner**: Danny (engineering expertise)
- **Impact**: If Danny becomes unavailable (unexpected departure, illness), backend deployments halt
- **Probability**: Medium (known departure in 1 month; short window for transfer)
- **Mitigation**: Pair teaching session today; document deployment steps
- **Current Status**: Knowledge transfer scheduled but not yet executed

**Risk 2: Emory Timeline Compression**
- **Owner**: Multiple (code fix + testing + training + Emory meeting all same day)
- **Impact**: Any individual blocker cascades (test data missing → can't validate → feature untested → reputation risk with Emory)
- **Probability**: Medium (multiple dependencies, tight timeline)
- **Mitigation**: Clear ownership per person; slack for troubleshooting
- **Current Status**: Commitments made; execution not yet underway

**Risk 3: Deal Breaker Feature Untested with Real Data**
- **Owner**: Danny (validation), Vrijen (data generation)
- **Impact**: Production rollout with unvalidated input handling; could surface bugs with real user submissions
- **Probability**: Medium (time pressure; feature assumed working without stress testing)
- **Mitigation**: Vrijen to create realistic multi-scenario test data before Emory meeting
- **Current Status**: Acknowledged explicitly by team; test plan outlined

**Risk 4: Darwin Box Negotiation Positioning**
- **Owner**: Vrijen (primary negotiator)
- **Impact**: Desperate or unprepared positioning weakens negotiating power; billion-dollar deal at stake
- **Probability**: Low (one week buffer for prep; team aware of importance)
- **Mitigation**: Intentional 1-week delay for narrative refinement
- **Current Status**: Risk acknowledged and addressed proactively

---

### 🟡 MODERATE RISKS

**Risk 5: Role Detail Pages Scope Creep**
- **Owner**: Danny (engineering)
- **Impact**: If deferred feature becomes suddenly "must-have" for demo, causes rework
- **Probability**: Low-Medium (marked as "sexy but unproven")
- **Mitigation**: Clear decision that feature is deferred; revisit only on user feedback
- **Current Status**: Decision documented; team alignment achieved

**Risk 6: Deal Breaker Submission Form Implementation Status Unclear**
- **Owner**: Danny (engineering)
- **Impact**: If applicant-side form not actually implemented, no submissions possible (test fails completely)
- **Probability**: Low (Danny indicated willingness; just blocked on test data)
- **Mitigation**: Explicit validation that form exists before test data generation
- **Current Status**: Assumed implemented but not explicitly confirmed

**Risk 7: Federal Worker Code Quality**
- **Owner**: Vrijen (sourced from ChatGPT), Danny (deployment)
- **Impact**: Code fix may not actually work; staged deployment failure creates emergency pressure
- **Probability**: Medium (untested ChatGPT code; no peer review mentioned)
- **Mitigation**: Test thoroughly in staging before Emory meeting
- **Current Status**: Code obtained; deployment process to serve as testing

**Risk 8: Ilya Engagement Unclear**
- **Owner**: Ilya (engineering), Vrijen (prioritization)
- **Impact**: Underutilized capacity may indicate unclear responsibilities or project fit
- **Probability**: Medium (deferred sync suggests potential misalignment)
- **Mitigation**: Later sync to clarify Ilya's role and workload
- **Current Status**: Rescheduled; addressing today

---

### 🟢 LOW RISKS

**Risk 9: Testing Account Creation Overhead**
- **Owner**: Danny (provides guidance)
- **Impact**: Testing environment setup delays validation work
- **Probability**: Low (manual process documented; team familiar)
- **Mitigation**: Process already refined (plus-sign email trick)
- **Current Status**: Documented; team has repeated this multiple times

**Risk 10: Scheduling Conflicts with Rockle**
- **Owner**: Vrijen (calendar management)
- **Impact**: If Vrijen unavailable for critical sync (Danny training), cascades
- **Probability**: Low (Vrijen explicitly noted Rockle call post-stand-up; planning ahead)
- **Mitigation**: Separate scheduling for Danny training after Rockle call
- **Current Status**: Already planned

---

## External Dependencies

| Dependency | Entity | Status | Risk Level |
|-----------|--------|--------|-----------|
| Emory meeting execution | Emory (university partner) | Scheduled; on our calendar | Low (assumption: won't cancel) |
| Darwin Box availability | Darwin Box (acquisition target) | TBD early next week | Medium (depends on their schedule) |
| Federal code correctness | ChatGPT (LLM) / Vrijen judgment | Untested | Medium (code review not mentioned) |
| Staging environment stability | Zo infrastructure | Assumed stable | Low (system running; no issues noted) |

---

## Cross-Functional Impact

### If Deal Breaker Feature Fails
- **Emory**: Partnership may stall; federal worker cohort launch delayed
- **Darwin Box**: Demo credibility undermined if we don't have working features
- **Roadmap**: Likely rework required; impacts other timeline commitments

### If Backend Deployment Not Successfully Transferred to Vrijen
- **Immediate**: Emory code deployment may require Danny anyway (not independent)
- **1 Month**: After Danny leaves, no one can deploy; all changes require external help
- **Organizational**: Creates handoff bottleneck; scales poorly as team grows

### If Darwin Box Call Unprepared
- **Deal**: Potentially loses momentum from exploratory call; acquisition path stalls
- **Team Morale**: Failure to capitalize on lead opportunity impacts momentum
- **Valuation**: Unprepared positioning weakens negotiating leverage on terms

---

## Assumption Validation Needed

| Assumption | Stated By | Confidence | Validation Method |
|-----------|-----------|-----------|------------------|
| Applicant-side deal breaker form is implemented | (Implicit in Danny's approach) | Medium | Explicit confirmation from Danny before test data generation |
| Federal code fix from ChatGPT is functionally correct | Vrijen | Low | Code review + staging test before Emory meeting |
| Emory meeting cannot be rescheduled | Vrijen (implied) | High | (Not challenged; assume fixed) |
| Darwin Box founders interested in Careerspan | Vrijen (from call notes) | High | (Early next week call will confirm) |
| 1-week delay strengthens Darwin Box positioning | Ilse | Medium | (Narrative refinement to be judged subjectively) |
| Ilya has available capacity for tasks | (Implicit) | Low | Later sync will clarify |

