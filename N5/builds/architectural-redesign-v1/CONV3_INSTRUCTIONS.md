# CONVERSATION 3: Full Bootstrap

**Phase:** 1C - Complete Persona Integration  
**Persona:** Vibe Builder  
**Duration:** 1.5 hours  
**Dependencies:** Conv 1 ✅ + Conv 2 ✅

---

## MISSION

Update 5 personas with full pre-flight protocol + cognitive prompt loading + 8 embedded principles each.

---

## DELIVERABLES

### 1. Operator Persona v2.0
- Full pre-flight protocol (5 steps)
- Auto-load: navigator_prompt.md
- 8 embedded principles (execution-focused)
- Reference paths to full YAMLs

### 2. Builder Persona v2.0
- Full pre-flight protocol (5 steps)
- Auto-load: planning_prompt.md
- 8 embedded principles (build-focused)
- Reference paths to full YAMLs

### 3. Strategist Persona v2.0
- Full pre-flight protocol (5 steps)
- Auto-load: thinking_prompt.md
- 8 embedded principles (strategic-focused)
- Reference paths to full YAMLs

### 4. Architect Persona v2.0
- Full pre-flight protocol (5 steps)
- Auto-load: thinking_prompt.md
- 8 embedded principles (design-focused)
- Reference paths to full YAMLs

### 5. Teacher Persona v2.0
- Full pre-flight protocol (5 steps)
- Auto-load: thinking_prompt.md
- 8 embedded principles (teaching-focused)
- Reference paths to full YAMLs

---

## PERSONA UPDATE TEMPLATE

Each persona needs:



---

## PRINCIPLE SELECTION BY PERSONA

### Builder (execution-focused):
- P1: Human-Readable First
- P5: Safety, Determinism, Anti-Overwrite
- P7: Idempotence and Dry-Run
- P11: Failure Modes and Recovery
- P15: Complete Before Claiming
- P19: Error Handling
- P22: Language Selection
- P36: Orchestration Pattern

### Operator (mechanics-focused):
- P5: Safety, Determinism, Anti-Overwrite
- P7: Idempotence and Dry-Run
- P11: Failure Modes and Recovery
- P18: Verify State
- P19: Error Handling
- P20: Modular
- P36: Orchestration Pattern
- P37: Refactor Pattern

### Strategist (analysis-focused):
- P0.1: LLM-First for Analysis
- P2: Single Source of Truth
- P8: Minimal Context
- P12: Testing in Fresh Threads
- P13: Anti-Analysis Paralysis
- P36: Orchestration Pattern
- P37: Refactor Pattern
- Decision Matrix

### Architect (design-focused):
- P1: Human-Readable First
- P2: Single Source of Truth
- P5: Safety, Determinism
- P8: Minimal Context
- P22: Language Selection
- P28: Plan DNA
- P36: Orchestration Pattern
- P37: Refactor Pattern

### Teacher (explanation-focused):
- P1: Human-Readable First
- P8: Minimal Context
- P12: Testing in Fresh Threads
- P20: Modular
- P0.1: LLM-First
- P2: Single Source of Truth
- P36: Orchestration Pattern
- P37: Refactor Pattern

---

## VALIDATION TESTING (Checkpoint)

After updating all 5 personas, test:

1. **Load Builder** → Verify it auto-references planning_prompt.md
2. **Load Strategist** → Verify it auto-references thinking_prompt.md
3. **Load Operator** → Verify it auto-references navigator_prompt.md
4. **Test Principle Reference** → Can Builder cite P36 by name?
5. **Test Pre-Flight** → Does protocol trigger automatically on system work?

---

## EXECUTION PROTOCOL

1. List personas → Get all 8 IDs
2. Update 5 personas using edit_persona (Operator, Builder, Strategist, Architect, Teacher)
3. For each:
   - Add full pre_flight_protocol
   - Add prompt_references (with correct prompt for domain)
   - Add principle_extensions (P36, P37, decision_matrix)
   - Add 8 relevant_principles (domain-specific)
4. Run checkpoint tests
5. Document completion

---

## TIME ESTIMATE

- 15 min per persona × 5 = 75 min
- 15 min checkpoint testing = 15 min
- **Total: 90 minutes (1.5 hrs)**

---

**Ready to execute Conv 3**
