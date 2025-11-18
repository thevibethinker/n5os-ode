---
title: "Pre-Build Discovery & PRD Protocol"
description: Mandatory grok-first discovery protocol with PRD generation, rubric scoring, and architectural alignment. Prevents duplicate work through systematic understanding before searching.
tags:
  - build
  - planning
  - discovery
  - prd
  - architecture
  - quality-control
tool: true
version: 2
created: 2025-11-15
last_edited: 2025-11-15
---
# Pre-Build Discovery & PRD Protocol v2.0

**Purpose**: Force systematic understanding → comprehensive discovery → structured PRD → measurable quality

**Critical Principle**: **GROK BEFORE GREP** - You can't search effectively until you understand what you're searching for.

**When to Use**: Before ANY of these activities:
- Building new systems/scripts/features
- Refactoring existing code (>50 lines)
- Architectural changes
- System consolidation/cleanup
- Database schema changes
- Multi-file operations (>5 files)

---

## PHASE 0: LOAD ARCHITECTURAL DNA ⚡ MANDATORY

**Before starting ANY discovery or planning:**

### 0.1 Load Core Principles
```bash
# Load the planning prompt with architectural principles
file 'Knowledge/architectural/planning_prompt.md'
```

**Checkpoint**: ✅ I have loaded and reviewed the architectural principles  
**Key principles to apply**:
- Simple Over Easy
- Flow Over Pools
- Maintenance Over Organization
- Code Is Free, Thinking Is Expensive
- Nemawashi (socialize early, build consensus)

### 0.2 Declare Conversation Context
```bash
# Ensure session state exists
python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current> --type build
```

**Checkpoint**: ✅ SESSION_STATE.md initialized for this build thread

---

## PHASE 1: GROK (Understand Deeply FIRST) 🧠

**Principle**: You cannot search effectively until you understand what you're looking for.

### 1.1 Problem Statement (Written, Not Assumed)
**Write explicit answers** (do not skip):

**Q1: What specific problem am I solving?**  
_Answer_:

**Q2: What is the ROOT CAUSE (not just symptoms)?**  
_Answer_:

**Q3: What EVIDENCE supports that this is the actual problem?**  
_Answer_:

**Q4: What would success look like? (Measurable outcome)**  
_Answer_:

**Q5: What am I NOT solving? (Scope boundaries)**  
_Answer_:

**Checkpoint**: ✅ I have written answers to all 5 questions above

### 1.2 Conceptual Understanding
**Before searching files, understand the domain**:

- What are the key CONCEPTS involved? (List 3-5)
- What are the key DATA FLOWS? (Input → Transform → Output)
- What are the INTERFACES between components?
- What VOCABULARY does the system use? (List relevant terms)

**Checkpoint**: ✅ I understand the conceptual model well enough to know what to search for

---

## PHASE 2: DISCOVER (Multi-Method, Not Just Grep) 🔍

**Principle**: Use 4+ discovery methods. Grep alone is lazy and incomplete.

### 2.1 Structured File Search
**Search systematically across multiple locations**:

```bash
# Scripts
find /home/workspace/N5/scripts -type f -name "*{keyword}*" -ls

# Data & Databases
find /home/workspace/N5/data -name "*{keyword}*" -ls

# Registry area
find /home/workspace/N5/registry -name "*{keyword}*" -ls

# Check for empty databases (pollution from past builds)
find /home/workspace/N5/data -name "*.db" -size 0

# Check Knowledge base
find /home/workspace/Knowledge -name "*{keyword}*"
```

**Document findings**:
- [ ] List ALL related files (path, size, last modified)
- [ ] Flag empty databases (0 bytes = unused)
- [ ] Flag large/active databases (>10KB = in use)
- [ ] Note date patterns (recent = active, old = stale)

### 2.2 Code Pattern Search
**Search for functional patterns, not just file names**:

```bash
# Search for imports/usage
grep -r "import.*{module}" /home/workspace/N5/

# Search for class/function definitions
grep -r "class.*{Name}\|def.*{function}" /home/workspace/N5/scripts/

# Search for database table creation
grep -r "CREATE TABLE\|db_path.*{keyword}" /home/workspace/N5/
```

**Document findings**:
- [ ] List classes/functions that provide similar functionality
- [ ] Note where they're imported/used
- [ ] Check if they're active (recent commits/logs)

### 2.3 Executables Database Search
**Check registered commands/prompts**:

```bash
python3 /home/workspace/N5/scripts/executable_manager.py search "{keywords}"
```

**Document findings**:
- [ ] List registered executables related to this domain
- [ ] Note what they do (from descriptions)
- [ ] Check if they solve the current problem

### 2.4 Scheduled Tasks Check
**See if automation already exists**:

```python
# Use list_scheduled_tasks tool
# Search output for related keywords
```

**Document findings**:
- [ ] List scheduled tasks touching this domain
- [ ] Note what they do and how often
- [ ] Check if they depend on systems I'm planning to change

### 2.5 Documentation & Schema Search
**Find existing docs and schemas**:

```bash
# README files
find /home/workspace/N5 -name "*README*" -o -name "*_README*"

# Schemas
ls -lh /home/workspace/N5/schemas/*{keyword}*

# Architecture docs
grep -r "{topic}" /home/workspace/Knowledge/architectural/
```

**Document findings**:
- [ ] List existing documentation
- [ ] Summarize what systems do
- [ ] Note gaps/inconsistencies
- [ ] Identify single source of truth (or lack thereof)

### 2.6 Dependency Mapping
**What depends on existing systems?**

```bash
# Find all references
grep -r "{script_name}\|{module_name}" /home/workspace/N5/ --include="*.py" --include="*.sh"

# Check scheduled tasks (from 2.4)
# Check workflow files
find /home/workspace/N5/workflows -name "*.md" | xargs grep -l "{keyword}"
```

**Document findings**:
- [ ] List all dependents
- [ ] Flag critical dependencies (must not break)
- [ ] Note coupling strength (loose vs tight)

### 2.7 Current State Assessment
**What's the actual operational status?**

```bash
# Database sizes and row counts
ls -lh /home/workspace/N5/data/*.db
sqlite3 {db_path} "SELECT COUNT(*) FROM {table};"

# Check queue depths
wc -l /home/workspace/N5/data/*queue*

# Recent log activity
ls -lt /home/workspace/N5/logs/ | head -20

# Health reports
cat /home/workspace/N5/data/*health_report.json
```

**Document findings**:
- [ ] Operational status (working/broken/degraded)
- [ ] Queue backlog sizes
- [ ] Known issues from health reports
- [ ] Processing rates/throughput

**Checkpoint**: ✅ I have used 4+ discovery methods and documented findings comprehensively

---

## PHASE 3: DESIGN (Structured PRD Generation) 📋

**Principle**: A written PRD prevents vibe coding. Make architectural decisions explicit.

### 3.1 PRD Template (Complete ALL sections)

```markdown
# PRD: {Project Name}

**Version**: 1.0  
**Author**: {Persona Name}  
**Date**: {YYYY-MM-DD}  
**Status**: DRAFT → REVIEW → APPROVED → EXECUTED

---

## 1. Problem Statement
{From Phase 1.1 - copy your answers}

## 2. Discovery Summary
**Existing Systems Found**:
- {List from Phase 2 with status: active/empty/stale}

**Current State**:
- Working: {what functions today}
- Broken: {what's failing}
- Backlog: {queue sizes, bottlenecks}
- Gaps: {what's missing}

**Dependencies**:
- Critical: {must not break}
- Coupled: {will need updates}
- Independent: {safe to change}

## 3. Proposed Solution

### Architecture Decisions
**Approach**: {New build / Refactor / Consolidate / Delete}

**Rationale**: 
- Why this approach over alternatives?
- What architectural principles guide this? (Reference Phase 0)
- What trade-offs are we making?

**Components**:
1. {Component A}: {purpose, interface}
2. {Component B}: {purpose, interface}
3. {Component C}: {purpose, interface}

**Data Flow**:
```
Input → Transform → Output
{Specific paths and formats}
```

### Self-Healing Mechanisms ⚠️ MANDATORY
**How will this system detect failures?**
- {Health check method}
- {Monitoring approach}
- {Alert mechanism}

**How will this stay in sync with other systems?**
- {Sync strategy: registry-first / filesystem-first / both}
- {Conflict resolution}
- {Reconciliation frequency}

**What happens when it breaks?**
- {Failure modes}
- {Graceful degradation}
- {Manual intervention protocol}

**How will it evolve?**
- {Migration path for future changes}
- {Backward compatibility strategy}

### Documentation Strategy
**Single Source of Truth**:
- {Location of canonical docs}
- {Format: README / Knowledge doc / Schema}
- {Update protocol}

**What gets documented**:
- [ ] Architecture overview
- [ ] API/Interface contracts
- [ ] Data schemas
- [ ] Operational runbook
- [ ] Common troubleshooting

## 4. Implementation Plan

### Phases
**Phase A**: {Milestone 1}  
**Phase B**: {Milestone 2}  
**Phase C**: {Milestone 3}

### Files to Create/Modify/Delete
**Create**:
- {path/to/new_file.py}: {purpose}

**Modify**:
- {path/to/existing.py}: {what changes}

**Delete** (archive first):
- {path/to/obsolete.py}: {why safe to remove}

**Preserve** (do not touch):
- {path/to/critical.py}: {why must preserve}

### Testing Strategy
**Unit Tests**:
- {Test file locations}
- {Coverage target}

**Integration Tests**:
- {Test scenarios}
- {Success criteria}

**Validation**:
- {How to verify it works}
- {Regression checks}

## 5. Risk Assessment

### Risks
1. **{Risk A}**: {description}  
   - Likelihood: {High/Med/Low}  
   - Impact: {High/Med/Low}  
   - Mitigation: {strategy}

2. **{Risk B}**: {description}  
   - Likelihood: {High/Med/Low}  
   - Impact: {High/Med/Low}  
   - Mitigation: {strategy}

### Rollback Plan
**If this fails, how do we revert?**
- {Backup strategy}
- {Restoration steps}
- {Data recovery}

**Point of no return**: {When is rollback no longer possible?}

## 6. Success Criteria (Measurable)

### Functional
- [ ] {Specific functionality works}
- [ ] {Existing features still work}
- [ ] {Tests pass}

### Performance
- [ ] {Throughput metric} improves from X to Y
- [ ] {Latency metric} remains under Z
- [ ] {Resource usage} stays within bounds

### Quality
- [ ] Documentation complete
- [ ] Health checks implemented
- [ ] Sync mechanisms verified

### User Impact
- [ ] {V's workflow} improves in {specific way}
- [ ] {Pain point} is resolved

---

## 7. Rubric Self-Score (Complete BEFORE approval)

{See Phase 3.2 below}
```

**Checkpoint**: ✅ I have completed ALL sections of the PRD template above

### 3.2 Quality Rubric (Self-Score Your PRD)

**Instructions**: Score each dimension 1-10. Total must be ≥8.0 to proceed. If <8.0, identify lowest dimension and improve.

#### Dimension 1: Discovery Completeness (Weight: 20%)
**Score**: __/10

- **10**: All existing systems found via 4+ methods, documented with paths/sizes/status/dependencies
- **7**: Major systems found, used 3 methods, minor gaps
- **4**: Minimal search (grep only), obvious misses
- **1**: No systematic discovery

**Evidence for score**:
- Discovery methods used: {list}
- Systems found: {count}
- Gaps identified: {any?}

#### Dimension 2: Architectural Alignment (Weight: 15%)
**Score**: __/10

- **10**: Explicitly references planning_prompt principles, applies all relevant, rationale clear
- **7**: Mentions some principles, partial application
- **4**: Generic approach, ignores architectural DNA
- **1**: Violates core principles (e.g., "Easy over Simple")

**Evidence for score**:
- Principles applied: {list}
- Rationale connects to principles: {yes/no}
- Trade-offs acknowledged: {yes/no}

#### Dimension 3: PRD Completeness (Weight: 20%)
**Score**: __/10

- **10**: All 7 PRD sections complete, self-healing defined, sync mechanisms clear, rollback plan exists
- **7**: PRD exists, missing 1-2 sections (e.g., no self-healing)
- **4**: Vague plan, no structured PRD
- **1**: No plan, jumped to coding

**Evidence for score**:
- PRD sections complete: __/7
- Self-healing mechanisms: {yes/no}
- Sync strategy defined: {yes/no}
- Rollback plan: {yes/no}

#### Dimension 4: Documentation Strategy (Weight: 15%)
**Score**: __/10

- **10**: Single source of truth defined, README/Knowledge doc planned, operational runbook included
- **7**: Docs planned but incomplete (missing runbook or SSOT)
- **4**: Minimal documentation ("I'll add comments")
- **1**: No documentation plan

**Evidence for score**:
- SSOT location: {path}
- Doc types planned: {list}
- Update protocol: {defined?}

#### Dimension 5: Testing & Validation (Weight: 15%)
**Score**: __/10

- **10**: Unit + integration tests planned, coverage target set, validation criteria measurable
- **7**: Basic tests planned, incomplete coverage
- **4**: Manual testing only ("I'll try it")
- **1**: No testing plan

**Evidence for score**:
- Test types: {unit/integration/manual}
- Coverage target: {%}
- Validation criteria: {measurable?}

#### Dimension 6: Self-Healing & Resilience (Weight: 15%)
**Score**: __/10

- **10**: Failure detection automated, sync mechanisms prevent drift, graceful degradation, self-correction
- **7**: Health checks exist but manual intervention needed
- **4**: No failure detection ("it'll work")
- **1**: No consideration of failure modes

**Evidence for score**:
- Failure detection: {method}
- Sync mechanism: {strategy}
- Graceful degradation: {yes/no}

---

### 3.3 Calculate Total Score

```
Total Score = (D1×0.20) + (D2×0.15) + (D3×0.20) + (D4×0.15) + (D5×0.15) + (D6×0.15)

Total Score = __.__/10
```

**Quality Gate**:
- ✅ **8.0-10.0**: Ready for Phase 4 (Approval)
- ⚠️ **6.0-7.9**: Needs improvement - identify lowest dimension and enhance
- ❌ **<6.0**: Substantial gaps - revisit Phase 2 (Discovery) or Phase 3 (Design)

**If score <8.0**:
1. Identify dimension(s) with lowest scores
2. Review that dimension's criteria for score=10
3. Enhance PRD to meet higher criteria
4. Re-score
5. Repeat until ≥8.0

**Checkpoint**: ✅ My PRD scores ≥8.0 and I have evidence for each dimension score

---

## PHASE 4: APPROVE (STOP - Get V's Explicit Sign-Off) ✋

### 4.1 Present Complete Package

**Format for V**:
```markdown
# Approval Request: {Project Name}

## Executive Summary
{2-3 sentences: problem, approach, impact}

## Discovery Highlights
- Existing systems: {count, status}
- Critical dependencies: {list}
- Current bottlenecks: {specific metrics}

## Proposed Solution
- Approach: {New/Refactor/Consolidate/Delete}
- Key components: {list}
- Self-healing: {yes - how}
- Documentation: {yes - where}

## Rubric Score: {X.X}/10.0
- Discovery: {score}/10
- Architecture: {score}/10
- PRD: {score}/10
- Documentation: {score}/10
- Testing: {score}/10
- Self-Healing: {score}/10

## Risks & Mitigations
1. {Risk}: {Mitigation}
2. {Risk}: {Mitigation}

## Approval Status
- [ ] **APPROVED** - Proceed to Phase 5 (Execution)
- [ ] **APPROVED WITH MODIFICATIONS** - {Specify changes}
- [ ] **NOT APPROVED** - {Reason}

---
**V's Response**: {Waiting for explicit approval}
```

### 4.2 Wait for Response

**CRITICAL STOP POINT**:
- ❌ DO NOT proceed to Phase 5 without explicit "APPROVED" from V
- ❌ DO NOT start coding/building during Phases 0-4
- ❌ DO NOT assume approval if V asks clarifying questions
- ❌ DO NOT interpret silence as approval

**If V requests modifications**:
1. Update PRD based on feedback
2. Re-score rubric
3. Re-present for approval
4. Wait for explicit "APPROVED"

**Checkpoint**: ✅ V has explicitly approved with "APPROVED" response

---

## PHASE 5: EXECUTE (Only After Explicit Approval) ⚙️

### 5.1 Incremental Implementation
**Build in chunks, validate continuously**:

```python
# Pseudo-workflow
for phase in [Phase_A, Phase_B, Phase_C]:
    implement(phase)
    test(phase)
    validate(phase)
    document(phase)
    
    if not passing:
        rollback(phase)
        revise_approach()
        seek_approval_again()
```

**Principles**:
- Small batches (test after each component)
- Fail fast (catch errors early)
- Document as you go (not at the end)
- Update SESSION_STATE every 3-5 steps

### 5.2 Continuous Rubric Checking
**During execution, periodically verify**:
- [ ] Am I still following the approved PRD?
- [ ] Are tests being written concurrently? (P33)
- [ ] Is documentation being updated? (Not deferred)
- [ ] Am I detecting scope creep? (Expanding beyond PRD)

**If drifting from plan**:
1. STOP execution
2. Document drift
3. Assess impact
4. If minor: update PRD and continue
5. If major: seek new approval from V

### 5.3 Quality Validation
**Before claiming "done"**:

```bash
# Run all tests
pytest /home/workspace/N5/tests/test_{module}.py -v

# Verify success criteria from PRD Section 6
# Check each item explicitly

# Score final rubric (post-execution)
# Compare to pre-execution score - did quality hold?
```

**Checkpoint**: ✅ All tests pass, success criteria met, rubric score maintained ≥8.0

---

## PHASE 6: VALIDATE & ITERATE (Score Against Rubric) 📊

### 6.1 Post-Execution Rubric Score

**Re-score using same rubric from Phase 3.2**:
- Did discovery hold true? (No surprises)
- Did architecture stay aligned? (No principle violations)
- Is PRD complete? (All sections delivered)
- Is documentation done? (README, runbook, SSOT)
- Are tests passing? (Full coverage)
- Is self-healing working? (Health checks operational)

**Total Score**: __.__/10

### 6.2 Honest Assessment

**Compare to pre-execution score**:
- Pre-execution: {X.X}/10
- Post-execution: {Y.Y}/10
- Delta: {+/- Z.Z}

**If post-execution score < pre-execution score**:
- What degraded? {dimension}
- Why? {root cause}
- Fix: {action to restore quality}

**If post-execution score < 8.0**:
- Identify gaps
- Implement improvements
- Re-validate
- Repeat until ≥8.0

### 6.3 Extract Learnings

**What worked well?**
- {Specific practice}
- {Tool/method that helped}

**What would I do differently?**
- {Specific improvement}
- {Earlier intervention point}

**Pattern to reuse?**
- Name: {descriptive}
- Store: `/home/workspace/Knowledge/reasoning-patterns/{name}.md`
- Future reference: Load this pattern for similar work

### 6.4 Final Documentation

**Update all documents**:
- [ ] README created/updated with current state
- [ ] PRD marked as EXECUTED
- [ ] SESSION_STATE.md updated with completion
- [ ] Rubric scores documented in PRD
- [ ] Learnings extracted to Knowledge/

**Checkpoint**: ✅ All documentation complete, rubric ≥8.0, ready for handoff

---

## ENFORCEMENT & ANTI-PATTERNS

### Mandatory For
- ✅ Vibe Builder (all builds)
- ✅ Vibe Architect (all system designs)
- ✅ Vibe Debugger (system-level fixes)
- ✅ Any refactor >50 lines
- ✅ Any database schema changes
- ✅ Any multi-file operations (>5 files)
- ✅ Any consolidation/cleanup work

### Common Failure Modes (Block These)

**❌ "I'll just quickly build this..."**
→ STOP. Load Phase 0 (architectural DNA) first.

**❌ "This is too simple for a PRD"**
→ STOP. Even "simple" builds need discovery to avoid duplicates.

**❌ "I already know what exists, no need to search"**
→ STOP. You've been wrong twice. Search systematically.

**❌ "I'll search after I start building"**
→ STOP. Phase 1-2 (Grok → Discover) BEFORE any code.

**❌ "Planning is slow, let me just try something"**
→ STOP. Planning_prompt principle: "Thinking is expensive, code is free."  
Building wrong is more expensive than thinking first.

**❌ "I'll document later"**
→ STOP. Documentation is Phase 3 deliverable, not Phase 6 afterthought.

**❌ "The rubric is bureaucratic"**
→ STOP. Rubric enables iteration and prevents P15 (false completion).

**❌ "V will tell me if it's wrong"**
→ STOP. Your job is to deliver quality, not rely on V as QA.

### Persona-Specific Enforcement

**Vibe Builder**:
- Rule in persona: "Before starting implementation: Plan exists and reviewed, Tests will be written concurrently"
- This checklist IS the plan review mechanism
- No building without Phase 4 approval

**Vibe Architect**:
- Rule in persona: "Design clear and complete, Principles applied"
- This checklist enforces principle application (Phase 0)
- PRD is the design artifact

**Vibe Operator**:
- Rule in persona: "Route to specialist when they'd add value"
- Substantial builds = route to Builder with this checklist

---

## ITERATION PROTOCOL

**If rubric score <8.0 at any checkpoint**:

1. **Identify**: Which dimension(s) scored lowest?
2. **Diagnose**: Why did this dimension score low?
3. **Improve**: What specific action raises this score?
4. **Re-score**: Did the improvement work?
5. **Repeat**: Until total score ≥8.0

**Example Iteration**:
```
Initial Score: 7.2/10
- Discovery: 9/10 ✅
- Architecture: 8/10 ✅
- PRD: 6/10 ❌ (missing self-healing)
- Documentation: 7/10 ⚠️
- Testing: 8/10 ✅
- Self-Healing: 4/10 ❌ (not defined)

Action: Add self-healing section to PRD (failure detection, sync mechanism)
Action: Define SSOT location and update protocol

Re-score:
- PRD: 9/10 ✅
- Self-Healing: 9/10 ✅
- Documentation: 9/10 ✅

New Total: 8.7/10 ✅ Ready for approval
```

---

## REFERENCES

**Architectural Principles**:
- `file 'Knowledge/architectural/planning_prompt.md'` (Phase 0 - mandatory load)

**Session Management**:
- `file 'N5/scripts/session_state_manager.py'` (Phase 0 - initialize)

**Discovery Tools**:
- `file 'N5/scripts/executable_manager.py'` (Phase 2.3 - search executables)
- `tool list_scheduled_tasks` (Phase 2.4 - check automation)

**Quality Frameworks**:
- Planning_prompt: "70% Think+Plan, 20% Review, 10% Execute"
- Aaron's 70/30 methodology (inspiration)
- Nemawashi principle (socialize design before building)

---

## VERSION HISTORY

**v2.0** (2025-11-15):
- Complete redesign with grok-first methodology
- Added Phase 0 (architectural DNA loading)
- Multi-method discovery (4+ techniques, not just grep)
- Structured PRD template with 7 sections
- Built-in 6-dimension scoring rubric
- Self-healing mechanisms mandatory
- Documentation as deliverable (not afterthought)
- Iteration protocol for continuous improvement
- Designed by Vibe Architect based on Level Upper analysis

**v1.0** (2025-11-15):
- Initial version with 5-phase checklist
- Discovery-first approach
- Basic approval workflow

---

**This protocol prevents "vibe coding hell" through systematic understanding, comprehensive discovery, structured design, measurable quality, and explicit approval before execution.**

---

*Designed by Vibe Architect | Inspired by Aaron Mak Hoffman's 70/30 methodology | v2.0 | 2025-11-15*

