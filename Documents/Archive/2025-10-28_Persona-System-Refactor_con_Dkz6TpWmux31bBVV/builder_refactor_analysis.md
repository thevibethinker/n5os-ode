# Builder Refactor Analysis
**Date:** 2025-10-28  
**Protocol:** Deconstruction Protocol v1.0

---

## Phase 1: Content Classification

### CORE (Move to Operator)
- ✅ **N5 System Architecture** - File topology, patterns → Already in Operator
- ✅ **Troubleshooting Protocol** - General debugging approach → Already in Operator  
- ✅ **Pre-Flight (MANDATORY)** - Context loading → Replaced by Activation Interface
- ✅ **Integration** - When to load what → Operator handles mode activation
- ✅ **When to Invoke** - Invocation conditions → Operator detects signals
- ✅ **Self-Check** - Generic checklist → Operator handles
- ✅ **Meta** - Persona system philosophy → Not needed in mode

### SPECIALIST (Keep - Builder-specific)
- ✅ **Language Selection (P22)** - Build-specific decision tree + rationale
- ✅ **Script Template** - Build output pattern
- ✅ **Critical Anti-Patterns** - Build-specific mistakes
- ✅ **Testing Checklist** - Build validation (converted to return payload)
- ✅ **Quality Standards** - Code/file/communication standards
- ✅ **Key Lessons** - Historical build learnings

### REINFORCEMENT (Keep - Strategic duplication)
- ✅ **Critical Principles** - P5, P7, P15, P16, P19, P21 (safety + quality)
  - *Justification:* These are most violated in build work
  - *Budget:* 6 principles (need to reduce to 3 per MP6)
  - *Decision:* Keep P15 (Complete), P16 (No Invented Limits), P19 (Error Handling)

### DELETE
- ❌ **Core Identity** - "Senior builder with N5 knowledge" → Operator provides this
- ❌ **Watch for** - Generic anti-patterns → Covered in specialist section
- ❌ **Full principle references** - `file 'Knowledge/...'` → Operator loads these
- ❌ **System Architecture diagram** → Operator knows this

---

## Phase 2: Activation Interface Design

### Signals (Auto-Detection)
**Primary (strong):**
- "build", "implement", "create", "script", "develop"
- "setup", "deploy", "generate", "configure"

**Secondary (weak):**
- "write code", "make a", "add functionality"
- "refactor" (if involves new implementation)

**Context requirements:**
- Request implies NEW construction (vs editing existing)
- OR request involves system/infrastructure setup
- OR request is script/automation creation

**NOT Builder if:**
- Pure editing/modification (use Operator direct)
- Pure debugging/verification (Debugger mode)
- Research/analysis needed first (Researcher mode)

---

## Phase 3: Required Context (Handoff Template)

```markdown
**Activating Builder Mode**

**Objective:** [What to build - 1 sentence]

**Constraints:**
- Tech stack: [Languages, frameworks, tools required/preferred]
- Dependencies: [Existing systems, files, services]
- Limitations: [Performance, compatibility, restrictions]

**Success Criteria:** [Definition of done - measurable]
- [ ] Functional: [Core behavior works]
- [ ] Tested: [Validation approach]
- [ ] Documented: [What docs needed]

**Context Files:** [Absolute paths to relevant files]
- Config: /path/to/config
- Schema: /path/to/schema
- Example: /path/to/example

**Principles Emphasis:** [Which P-rules apply most]
- P7 (Dry-Run): Must support --dry-run
- P22 (Language Selection): Choose appropriate language

**Planning Required:** [Yes/No - load planning prompt?]
```

---

## Phase 4: Success Criteria & Return Payload

### Builder Exits When:
1. **System functional** - Happy path works end-to-end
2. **Validation complete** - Tests pass OR manual verification done
3. **Documented** - Code has docstrings, README if multi-file
4. **Principles checked** - Self-check passed for emphasized principles

### Return Payload Structure:
```json
{
  "status": "complete|partial|blocked",
  "created_files": ["/absolute/path/1", "/absolute/path/2"],
  "modified_files": ["/absolute/path/3"],
  "validation_results": {
    "dry_run": "passed|failed|skipped",
    "production_test": "passed|failed|skipped",
    "principle_check": ["P15✓", "P19✓", "P22✓"]
  },
  "issues": [
    {
      "type": "glitch|limitation|assumption",
      "description": "Brief description",
      "workaround": "What was done",
      "squawk_log": true
    }
  ],
  "recommendations": [
    "Follow-up testing needed",
    "Consider adding monitoring"
  ],
  "completion_percentage": 95
}
```

---

## Phase 5: Reinforcement Budget Analysis

**Current Builder principles:** P8, P20, P5, P7, P11, P19, P15, P16, P18, P21, P1, P2, P17, P22

**Operator Core already has:** All P0-P40 as lightweight reference

**Builder-specific reinforcement needed:**
1. **P15 (Complete Before Claiming)** - Most violated in build work
   - *Why:* Builders claim "done" at 60% constantly
   - *Angle:* Specific completion percentage tracking
2. **P16 (No Invented Limits)** - Critical for external API work
   - *Why:* "Gmail limits to 3 messages" type hallucinations
   - *Angle:* Cite docs or say "don't know"
3. **P19 (Error Handling)** - Builders skip this for "quick scripts"
   - *Why:* Silent failures in production
   - *Angle:* Mandatory try/except + logging

**Budget:** 3/3 principles ✅

---

## Phase 6: Mode Purity Validation

### MP7 Test: Remove Core → Still Functions?
✅ **YES** - Builder mode only needs:
- Objective, constraints, success criteria (from handoff)
- Domain expertise (language selection, templates, anti-patterns)
- No dependency on N5 topology or session state

### MP2 Test: Interface Contract Complete?
✅ **YES**
- Signals defined (build, implement, create, etc.)
- Required context specified (handoff template)
- Success criteria clear (4 exit conditions)
- Return payload structured (JSON schema)

### MP4 Test: Stateless?
✅ **YES**
- No squawk log management (returns issues to Operator)
- No session state tracking (gets context from handoff)
- Internal phase tracking OK (Think→Plan→Execute within activation)

### MP5 Test: Escalation Paths Clear?
✅ **YES** - Return to Operator for:
- Missing critical context (can't determine language, constraints unclear)
- Operational blocker (file permissions, environment issues)
- Cross-domain need (requires research, strategic decision)

### MP6 Test: Reinforcement Budget?
✅ **YES** - 3 principles reinforced with justification

---

## Token Efficiency Projection

**Current Builder:** ~287 lines, ~6,732 characters
**Projected Refactored:** ~180 lines, ~4,200 characters
**Reduction:** ~37% size reduction

**With Operator Core active:** 50%+ effective reduction (no duplicate N5 topology, principle loading, etc.)

---

## Next: Generate Refactored Builder

Ready to create `vibe_builder_mode_v2.0.md`
