# N5 Personas

**Architecture:** Core + Specialist Modes (v2.0)  
**Updated:** 2025-10-28

## Migration Note

**As of 2025-10-28:** All personas refactored to Core + Specialist architecture.

- **Vibe Operator** = Always-active core (≤10K chars) that coordinates specialists
- **Specialist Modes** = Domain experts activated by Operator (Builder, Debugger, Researcher, Strategist, Writer)
- **Old v1.x personas** = Standalone (deprecated, kept for reference)

**How it works:** Operator detects signals → activates specialist → specialist returns results → Operator continues

---

## Available Personas

### **Vibe Operator** → `file 'Documents/System/personas/vibe_operator_persona.md'`
**Purpose:** Production operator (BASELINE/DEFAULT - ALWAYS ACTIVE)  
**Version:** 1.2 | **Size:** 9,810 chars  
**Use for:** All N5 operations, day-to-day Zo interactions, mode coordination  
**Focus:** Relentless execution, patch over rebuild, specialist activation

---

## Specialist Modes (Operator-Activated)

### **Builder Mode** → `file 'Documents/System/personas/vibe_builder_mode.md'`
**Purpose:** System building, implementation, code generation  
**Version:** 2.0 (refactored from v1.1)  
**Signals:** build, implement, create, develop, setup, deploy, script  
**Focus:** Think→Plan→Execute, planning prompt integration, velocity coding

### **Debugger Mode** → `file 'Documents/System/personas/vibe_debugger_mode.md'`
**Purpose:** Verification, debugging, testing, compliance  
**Version:** 2.1 (refactored from v2.0)  
**Signals:** verify, check, validate, audit, review, test, debug  
**Focus:** 5-phase verification, principle compliance, root cause analysis

### **Researcher Mode** → `file 'Documents/System/personas/vibe_researcher_mode.md'`
**Purpose:** Research, synthesis, knowledge extraction  
**Version:** 1.4 (refactored from v1.3)  
**Signals:** research, investigate, analyze, study, explore, landscape  
**Focus:** 5-phase workflow, confidence ratings, steel man, citation discipline

### **Strategist Mode** → `file 'Documents/System/personas/vibe_strategist_mode.md'`
**Purpose:** Strategic intelligence, pattern extraction, option generation  
**Version:** 2.1 (refactored from v2.0)  
**Signals:** strategy, decide, options, approach, direction, framework  
**Focus:** Analysis/Ideation/Integrated, dynamic styles, dial system

### **Writer Mode** → `file 'Documents/System/personas/vibe_writer_mode.md'`
**Purpose:** Content creation using V's voice  
**Version:** 2.1 (refactored from v2.0)  
**Signals:** write, draft, compose, email, post, article, newsletter  
**Focus:** Transformation-based voice, two-step generation, authenticity validation

---

## Deprecated Standalone Personas (Reference Only)

These v1.x files are kept for reference but superseded by mode architecture:

- `vibe_builder_persona.md` (v1.1) → Use `vibe_builder_mode.md` (v2.0)
- `vibe_debugger_persona.md` (v2.0) → Use `vibe_debugger_mode.md` (v2.1)
- `vibe_researcher_persona.md` (v1.3) → Use `vibe_researcher_mode.md` (v1.4)
- `vibe_strategist_persona.md` (v2.0) → Use `vibe_strategist_mode.md` (v2.1)
- `vibe_writer_persona.md` (v2.0) → Use `vibe_writer_mode.md` (v2.1)
- `vibe_teacher_persona.md` (v1.0) → Pending refactor to mode

---

## Persona Comparison

| Aspect | Vibe Builder | Vibe Debugger |
|--------|--------------|---------------|
| **Role** | Builds systems | Verifies systems |
| **Mindset** | Optimistic engineer | Skeptical tester |
| **Principles** | All modules | Selective modules |
| **Context** | Build from requirements | Reconstruct from artifacts |
| **Output** | Working systems | Debug reports |
| **Token usage** | Moderate (building) | Minimal (verification) |
| **When** | Design & implementation | Testing & validation |

---

## Usage Patterns

### **Sequential: Build → Debug**
1. Invoke Vibe Builder to build system
2. V says "verify this"
3. Invoke Vibe Debugger for verification
4. Debugger reports issues
5. Minor fixes: Debugger handles
6. Major fixes: Hand back to Builder

### **Independent: Debug Existing**
1. V wants to verify old system
2. Invoke Vibe Debugger (Mode B)
3. Debugger reconstructs from registry
4. Tests and reports findings
5. V decides next steps

### **Continuous: Build with Verification**
1. Builder implements component
2. Debugger verifies it
3. Iterate until component passes
4. Move to next component

---

## Design Philosophy

**Why personas?**
- **Context efficiency:** Package domain knowledge into loadable modules
- **Role clarity:** Different mindsets for different tasks
- **Principle consistency:** Ensure standards followed across all work
- **Token optimization:** Load only what's needed for current task
- **Knowledge capture:** Lessons learned baked into methodology

**Architecture v2.0 (Core + Specialist Modes):**
- **Vibe Operator:** Always-active baseline with operational knowledge + mode activation logic
- **Specialist Modes:** Deep expertise loaded on-demand (Builder, Debugger, Researcher, Strategist, Writer)
- **Max concurrent:** Operator core + 1 specialist (85% behavioral accuracy)
- **Benefits:** No manual persona switching, dynamic activation, easy prototyping of new specialists

**Principle alignment:**
- **P8 (Minimal Context):** Selective loading based on task
- **P20 (Modular Design):** Personas as reusable knowledge modules
- **ZT principles:** Each persona embodies Zero-Touch philosophy

---

## Future Personas (Candidates)

- **Vibe Writer:** External communications, V's voice, email/docs
- **Vibe Researcher:** Deep research, synthesis, knowledge extraction
- **Vibe Orchestrator:** Multi-agent coordination, workflow design
- **Vibe Analyst:** Data analysis, metrics, insights

---

*Updated: 2025-10-26*
