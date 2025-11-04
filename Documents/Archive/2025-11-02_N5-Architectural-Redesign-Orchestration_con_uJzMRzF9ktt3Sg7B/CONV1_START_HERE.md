# CONVERSATION 1: BOOTSTRAP FOUNDATION - START HERE
**N5 Architectural Redesign | Conv 1 of 7**  
**Persona:** Builder  
**Duration:** 2 hours  
**Status:** READY TO BEGIN

---

## 🎯 YOUR MISSION (Builder)

Create the foundation that allows personas to load principles and cognitive prompts.

**What You're Building:**
1. Update 5 personas with loading stub (30 min)
2. Create P36 YAML - Separate Orchestration (30 min)
3. Create P37 YAML - Specification-Driven Regeneration (40 min)
4. Create Code Modification Decision Matrix (20 min)

**Checkpoint:** Test that personas can reference the new files

---

## 📋 DELIVERABLE 1: Update 5 Personas with Loading Stub

**Personas to Update:**
- Vibe Operator (90a7486f-46f9-41c9-a98c-21931fa5c5f6)
- Vibe Builder (567cc602-060b-4251-91e7-40be591b9bc3)
- Vibe Strategist (39309f92-3f9e-448e-81e2-f23eef5c873c)
- Vibe Architect (74e0a70d-398a-4337-bcab-3e5a3a9d805c)
- Vibe Teacher (find ID via list_personas)

**Add This Section to Each Persona (after core_identity):**

```yaml
pre_flight_protocol:
  description: "Load relevant context before substantial work"
  trigger: "System builds, refactors, architectural decisions, complex analysis"
  status: "STUB - Full protocol in Conv 3"
  steps:
    1_can_reference_files:
      action: "You CAN now reference files in Knowledge/architectural/"
      example: "Read file 'Knowledge/architectural/principles/P36_separate_orchestration.yaml'"
    2_full_protocol_coming:
      note: "Full 5-step pre-flight protocol will be added in Conversation 3"
```

**Testing:** After each update, verify persona still loads without errors.

---

## 📋 DELIVERABLE 2: Create P36 YAML

**File:** `Knowledge/architectural/principles/P36_separate_orchestration.yaml`

**Core Structure:**
```yaml
---
id: P36
name: Separate Orchestration Over Code Editing
category: safety
priority: critical
personas: [builder, operator]
version: 1.0
created: 2025-11-02

trigger: "before asking LLM to edit existing production code"

directive: |
  When extending/modifying production code:
  DO: Create separate orchestration points (new scripts/watchers)
  DON'T: Ask LLM to edit existing complex code inline
  
  PATTERN: Producer/Consumer with File Markers

pattern: |
  Extension Pattern:
  1. Keep existing script_v3.py untouched
  2. Create new script_extension.py
  3. Extension consumes v3 output via file markers
  4. Test both independently
  5. If extension fails, v3 still works

examples:
  good:
    - "V wants enrichment → Create separate enricher.py"
  bad:
    - "Edit meeting_processor_v3.py to add feature inline"

anti_patterns:
  inline_editing:
    violation: "Asked to refactor existing script to add feature"
    risk: "63% chance breaking existing functionality"
    instead: "Create separate consumer script"

related_principles: [P37, P5, P20, P28]

rationale: |
  - LLMs 63% higher error rate editing vs generating
  - Separate orchestration = independent failure modes
  - Matches LLM strength (generation) vs weakness (editing)
```

**Full specification in:** file '/home/.z/workspaces/con_uJzMRzF9ktt3Sg7B/FINAL_IMPLEMENTATION_PLAN.md'

---

## 📋 DELIVERABLE 3: Create P37 YAML

**File:** `Knowledge/architectural/principles/P37_specification_driven_regeneration.yaml`

**Core Structure:**
```yaml
---
id: P37
name: Specification-Driven Regeneration
category: safety
priority: critical
personas: [builder, architect]
version: 1.0
created: 2025-11-02

trigger: "before radical refactors (>50% changes, logic overhaul)"

directive: |
  When existing code needs radical refactoring:
  DO: Generate rubric → Regenerate → Compare → Validate
  DON'T: Try to surgically edit complex existing code
  
  PATTERN: 6-Step Specification-Driven Regeneration

pattern: |
  STEP 1: Analyze Current (AI) - Document all functionality
  STEP 2: Generate Rubric (AI → V Review <5min)
  STEP 3: Generate New Version (AI from rubric as v4)
  STEP 4: Behavioral Comparison (AI compares v3 vs v4)
  STEP 5: Validation Testing (V tests v4)
  STEP 6: Version Preservation (Keep v3, deploy v4)

rubric_quality_checklist:
  target_review_time: "<5 minutes"
  completeness:
    - "Lists ALL current functionality?"
    - "Specifies ALL new requirements?"
  testability:
    - "Can I verify each requirement?"
  clarity:
    - "Could another engineer build from this?"
  preservation:
    - "Is preservation explicit?"

related_principles: [P36, P5, P28, P7]

rationale: |
  - Leverages LLM strength: Generation from spec
  - Multiple validation checkpoints
  - Version preservation enables rollback
  - Aligns with Think→Plan→Execute (70%→20%→10%)
```

**Full specification in:** file '/home/.z/workspaces/con_uJzMRzF9ktt3Sg7B/FINAL_IMPLEMENTATION_PLAN.md'

---

## 📋 DELIVERABLE 4: Create Decision Matrix

**File:** `Knowledge/architectural/code_modification_decision_matrix.md`

**Core Content:**

```markdown
# Code Modification Decision Matrix

## Quick Decision Tree

Is code working in production?
├─ NO → Generate normally
└─ YES → How much changes?
   ├─ <10% → Careful editing OK
   ├─ 10-30% → USE P36 (Separate Orchestration)
   ├─ 30-50% → Default to P36 (safer)
   └─ >50% → USE P37 (Specification-Driven Regeneration)

## Scenario Details

**Small Changes (<10%):** Careful editing acceptable
- Fix bug, update variables, add logging
- Use edit_file_llm, test immediately

**Extensions (10-30%):** P36 - Separate Orchestration
- Keep script_v3.py untouched
- Create script_extension.py
- Coordinate via file markers

**Uncertain (30-50%):** Default to P36
- Bias toward preservation
- Can upgrade to P37 later if needed

**Radical Refactor (>50%):** P37 - Specification-Driven Regeneration
- Generate rubric (V reviews <5min)
- Regenerate as v4 from spec
- Behavioral comparison v3 vs v4
- Preserve v3, deploy v4

## Anti-Patterns
❌ "While I'm in here..." (scope creep)
❌ "Just a quick refactor" (underestimating)
❌ "I'll be careful" (trusting LLM editing)
```

**Full specification in:** file '/home/.z/workspaces/con_uJzMRzF9ktt3Sg7B/FINAL_IMPLEMENTATION_PLAN.md'

---

## ✅ CHECKPOINT TESTING

**Test 1: Can Operator Reference P36?**
1. New conversation as Operator
2. Say: "Load and summarize P36"
3. Pass: Operator accesses Knowledge/architectural/principles/P36_separate_orchestration.yaml

**Test 2: Can Builder Use Decision Matrix?**
1. As Builder, say: "I need to extend meeting_processor_v3.py - which pattern?"
2. Pass: Builder references matrix, recommends P36

**Both tests pass → Conv 2 authorized**

---

## 📁 FILES TO CREATE/MODIFY

**Edit (5 files):** Persona prompts (add stub section)  
**Create (3 files):**
- Knowledge/architectural/principles/P36_separate_orchestration.yaml
- Knowledge/architectural/principles/P37_specification_driven_regeneration.yaml
- Knowledge/architectural/code_modification_decision_matrix.md

---

## 🔗 REFERENCE DOCUMENTS

**Complete specifications:** file '/home/.z/workspaces/con_uJzMRzF9ktt3Sg7B/FINAL_IMPLEMENTATION_PLAN.md'  
**Full orchestration plan:** file '/home/.z/workspaces/con_uJzMRzF9ktt3Sg7B/BUILD_ORCHESTRATOR_PLAN.md'  
**Context:** This is conversation con_uJzMRzF9ktt3Sg7B

---

## ⏱️ TIME ESTIMATE

- Persona updates: 30 min
- P36 YAML: 30 min
- P37 YAML: 40 min
- Decision matrix: 20 min
- **Total: 2 hours**

---

**READY TO BEGIN CONVERSATION 1**

Copy this document into new conversation, Builder persona executes, checkpoint test, then Conv 2.
