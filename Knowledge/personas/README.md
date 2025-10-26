# N5 Personas

Specialized AI personas for different work contexts. Each persona packages domain knowledge, methodologies, and constraints for token-efficient context loading.

---

## Available Personas

### **Vibe Builder** → `file 'Documents/System/vibe_builder_persona.md'`
**Purpose:** System building, implementation, infrastructure  
**Use for:** Scripts, workflows, automation, refactoring, architecture  
**Focus:** Building systems that follow principles  
**Mindset:** Senior engineer, construction-focused

**Key features:**
- Loads architectural principles + safety + quality
- Pre-flight checklist before major work
- Script templates and anti-patterns
- System design workflow integration
- Language selection guidance (P22)

**Invocation:** "Load Vibe Builder persona" before system work

---

### **Vibe Debugger** → `file 'Documents/System/vibe_debugger_persona.md'`
**Purpose:** Verification, testing, debugging, quality assurance  
**Use for:** Post-build verification, bug investigation, principle compliance checks  
**Focus:** Finding gaps, testing edge cases, ensuring completeness  
**Mindset:** Senior verification engineer, skeptical

**Key features:**
- Two modes: End-of-conversation (Mode A) or Fresh-thread (Mode B)
- Context reconstruction from conversation registry
- Systematic testing methodology (structure → behavior → integration)
- Principle compliance matrix
- Structured debug reports
- Token-efficient verification (Rule-of-Two)

**Invocation:** "Load Vibe Debugger persona" for verification work

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
