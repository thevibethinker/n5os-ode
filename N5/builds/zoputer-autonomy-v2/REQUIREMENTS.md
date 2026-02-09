---
created: 2026-02-07
last_edited: 2026-02-07
version: 1.0
provenance: con_SWTbq4MHoLlrrcsM
---

# Zoputer Autonomy v2 - Requirements

## Context

Building on the `consulting-zoffice-stack` build (completed 2026-02-06), which established:
- Basic `/zo/ask` communication from va → zoputer
- Skill bundling and manifest generation
- Audit logging on both sides

This build extends that foundation to create a fully autonomous, bidirectional system.

## Core Requirements

### 1. Automatic Git Sync

**GitHub as shared substrate:**
- Create repo (private, under vrijenattawar) for zoputer's deployable content
- va pushes changes automatically (on skill changes or scheduled)
- zoputer pulls automatically (scheduled or on-demand trigger)

**Content distribution (per V's specification):**

| Content Type | Who Can Edit | Where It Lives |
|--------------|--------------|----------------|
| Core skills | va only | `main` branch, protected |
| Learnings/adaptations | zoputer can propose | `zoputer/learnings/` branch → PR to main |
| Client-specific config | Client + zoputer | Fork or client-specific branch |
| Runtime state | zoputer only | Local filesystem (not in Git) |

### 2. Bidirectional /zo/ask Communication

**Current state:** va → zoputer works (ZOPUTER_API_KEY set)

**Needed:**
- zoputer → va (zoputer needs VA_API_KEY)
- Escalation logic: when zoputer hits uncertainty, it calls va for guidance
- Mentor-apprentice relationship, not just puppet-master

### 3. Human Escalation Path (V in the Loop)

**Both va and zoputer can text V when they need a decision:**
- SMS with brief description of the issue
- Context packaged so V can access it from ANY thread (not just the originating one)
- Bridging via conversations.db or similar mechanism

**Flow:**
1. va or zoputer hits a decision point requiring V
2. Packages context into accessible location
3. Texts V: "Hey, I need your input on X. Context: [link/reference]"
4. V responds in whatever thread they're in
5. That thread can access the packaged context and route the decision back

### 4. Medium Autonomy for Zoputer

**Can do independently:**
- Self-edit learnings (commit to `zoputer/learnings/` branch)
- Handle client interactions within established patterns
- Log and adapt based on feedback

**Must ask va:**
- Uncertainty beyond confidence threshold
- Changes to core skills or behaviors
- Novel situations without precedent

**va reviews async:**
- PRs from zoputer's learning branches
- Escalation responses that set precedent

## Success Criteria

- [ ] GitHub repo exists with proper branch protection
- [ ] va can push skill changes → zoputer automatically receives them
- [ ] zoputer can call va via /zo/ask when uncertain
- [ ] Both can text V with packaged context accessible from any thread
- [ ] zoputer can commit learnings to its branch without human intervention
- [ ] Full audit trail of all inter-Zo and human-in-loop communications

## Technical Notes

- zoputer.zo.computer account exists (V confirmed steps 1 & 2 done)
- ZOPUTER_API_KEY is set on va
- Bridge has been tested (ping works)
- Build on existing Skills: `consulting-api`, `audit-system`, `librarian-export`

## V's Key Quotes

> "that zo should be able to itself independently contact you for advice or guidance"
> "when you and zoputer have uncertainty or you need me to make a call, you can selectively text me"
> "packaging up of the context such that I can access it in whatever thread I answer text messages"
> "Zoputer should be medium autonomous"
