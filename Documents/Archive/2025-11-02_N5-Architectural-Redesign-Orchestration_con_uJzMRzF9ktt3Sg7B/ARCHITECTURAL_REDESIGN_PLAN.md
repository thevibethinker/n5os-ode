# N5 ARCHITECTURAL REDESIGN - MASTER PLAN
Created: 2025-11-02 (Updated to include P37)
Architect: Vibe Architect
Scope: Dual cognitive bootstrap + principle YAML migration + runtime-active system

## EXECUTIVE SUMMARY

**Problem:** Principles exist but aren't loaded into LLM context → violations happen

**Solution:** Runtime-active cognitive infrastructure
- planning_prompt.md → Code personas (Builder, Operator)  
- thinking_prompt.md → Cognitive personas (Strategist, Architect, Teacher)
- navigator_prompt.md → Operator (system knowledge, orchestration)
- P36 + P37 → Complementary code modification patterns
- 29 principles in YAML → Runtime-loadable by personas

---

## THE THREE COGNITIVE BOOTSTRAP PROMPTS

### 1. planning_prompt.md (Code Personas)

**Purpose:** Cognitive framework for building and executing code/systems
**Target Personas:** Builder, Operator
**Core Content:**
- Think→Plan→Execute framework (Ben Guo)
- Squishy ↔ Deterministic spectrum
- P36 (Separate Orchestration) + P37 (Spec-Driven Regeneration)
- Code modification decision matrix
- Script design principles
- Error handling patterns
- Testing protocols

**Key Addition - Code Modification Decision Matrix:**


**Pattern Documentation - P37 Rubric Template:**


### 2. thinking_prompt.md (Cognitive Personas)

**Purpose:** Cognitive framework for analysis, strategy, learning
**Target Personas:** Strategist, Architect, Teacher
**Core Content:**
- Mental models (46 from research)
- First principles thinking
- Second-order thinking
- Decision frameworks
- Problem decomposition
- Systems thinking
- Cognitive biases & mitigation
- Learning strategies

**Key Frameworks:**
- Ladder thinking (why/how chains)
- Inversion (what guarantees failure)
- 10x thinking (remove constraints)
- Circle of competence
- Probabilistic thinking
- Second-order effects

### 3. navigator_prompt.md (Operator Persona)

**Purpose:** System knowledge for orchestration and file navigation
**Target Persona:** Operator
**Core Content:**
- N5 directory structure & purpose
- File location conventions
- Script inventory & purposes
- Workflow orchestration patterns
- When to invoke which personas
- How to find system components
- Common operational patterns

---

## PRINCIPLE MIGRATION STRATEGY

### Phase 2A: Priority Principles (P36 + P37)

**P36: Separate Orchestration Over Code Editing**


**P37: Specification-Driven Regeneration**


**Relationship Between P36 and P37:**


### Phase 2B: Remaining 27 Principles

[Continues with existing migration plan for P1-P35...]

---

## SIX-PHASE EXECUTION PLAN

### Phase 1: Foundation (Prompts + P36/P37)
**Build Order:**
1. Create  with P36+P37 patterns
2. Create  with cognitive frameworks
3. Create  with system knowledge
4. Migrate P36 to YAML
5. Migrate P37 to YAML
6. Create decision matrix documentation

**Deliverables:**
-  (NEW)
-  (NEW)
-  (NEW)
-  (NEW)
-  (NEW)
-  (NEW)

**Validation:**
- All three prompts loadable (<10k chars each)
- P36 + P37 YAML valid
- Decision matrix clear and actionable

### Phase 2: Principle YAML Migration
**Build Order:**
1. ~~P36, P37 (done in Phase 1)~~
2. P15 (Complete Before Claiming)
3. P25 (Code Is Free)
4. P28 (Plans As Code DNA)
5. P5 (Anti-Overwrite)
6. [Continue with remaining 24 principles...]

**Pattern for each:**


### Phase 3: Persona Integration
**For each persona, embed:**

**Builder:**


**Operator:**


**Strategist:**


**Architect:**


**Teacher:**


### Phase 4: System Testing
**Test Scenarios:**
1. Builder receives code extension task → loads planning_prompt → chooses P36
2. Builder receives refactor task → loads planning_prompt → chooses P37
3. Strategist receives analysis task → loads thinking_prompt → uses mental models
4. Operator receives orchestration task → loads both prompts + navigator
5. Teacher receives explanation request → loads thinking_prompt → uses analogies

### Phase 5: Remaining Principles Migration
[Continue migrating P1-P35 excluding already completed ones]

### Phase 6: Documentation & Rollout
**Deliverables:**
- Updated README explaining new system
- Migration guide for V
- Persona switching guide
- Principle reference index
- Troubleshooting guide

---

## KEY DESIGN DECISIONS

### 1. Why Three Prompts Instead of One?

**Cognitive Load Management:**
- Code work requires different mental frameworks than analytical work
- Loading irrelevant frameworks wastes context window
- Personas load only what they need

**Clear Separation:**
- planning_prompt.md = "How to build/execute"
- thinking_prompt.md = "How to analyze/strategize/learn"
- navigator_prompt.md = "Where things are/how system works"

### 2. Why P36 and P37 Together?

**Complementary Patterns:**
- P36 = Extension without touching working code
- P37 = Refactoring with confidence and validation

**Decision Clarity:**
- Clear matrix: extension vs refactor
- No ambiguity about which to use
- Default to safer option (P36) when uncertain

**Both Respect LLM Limitations:**
- P36: Avoid editing by adding orchestration
- P37: Avoid editing by regenerating from spec

### 3. Why Human Checkpoint in P37?

**Rubric Quality Critical:**
- Bad spec → bad output (garbage in, garbage out)
- V's judgment prevents spec errors early
- Cheaper to fix rubric than fix generated code

**Aligns with Ben's Framework:**
- THINK = Rubric quality (70% of effort)
- PLAN = Approved rubric (20%)
- EXECUTE = Generation (10%)

### 4. Why Version Increments Signal Regeneration?

**Git History Clarity:**
- v3 → v4 immediately signals "major change"
- Developer sees version number, knows to review carefully
- Easy rollback: "just use v3 again"

**Atomic Script Architecture:**
- Can delete v4, keep v3
- Can run both in parallel for A/B testing
- Future: consolidate v3+v4 into leaner v5

---

## SUCCESS METRICS

**Quantitative:**
- Principle citations increase >5x per conversation
- Principle violations decrease <1 per 10 conversations
- Code modification tasks succeed >90% first try
- V reports faster, more confident builds

**Qualitative:**
- V reports improved quality
- V reports fewer gaps in execution
- V reports stronger trust in system
- System feels "smarter" and more reliable

---

## TOTAL EFFORT ESTIMATE

**Phase 1:** 3 hours (3 prompts + P36/P37 + decision matrix)
**Phase 2:** 3 hours (27 principle YAML migration)
**Phase 3:** 2 hours (5 persona integration)
**Phase 4:** 1 hour (testing scenarios)
**Phase 5:** 3 hours (remaining principles)
**Phase 6:** 2 hours (documentation)

**Total: ~14 hours across 6+ conversations**

---

## NEXT STEPS

1. **V reviews updated plan**
2. **V approves or requests modifications**
3. **V authorizes Phase 1 start**
4. **Architect hands to Builder for execution**
5. **Build Orchestrator manages multi-conversation flow**

---

**STATUS: PLAN UPDATED WITH P37 INTEGRATION**
**AWAITING V APPROVAL TO BEGIN PHASE 1**

