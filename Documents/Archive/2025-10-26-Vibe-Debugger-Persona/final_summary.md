# Vibe Debugger Persona — Final Summary

**Conversation:** con_SyBlpCrnA0ZGVg8a  
**Date:** 2025-10-26  
**Status:** ✅ Complete

---

## What We Built

**Vibe Debugger** — Specialized verification and debugging persona for end-of-conversation testing and cross-conversation troubleshooting.

**Location:** `file 'Documents/System/vibe_debugger_persona.md'`  
**Size:** 9,445 characters (under 10k limit ✓)

---

## Key Design Decisions

### 1. **No Arbitrary File Limits**
- Removed Rule-of-Two constraint
- Loads as many files as needed for thorough debugging
- Optimizes through selective loading, not arbitrary caps

### 2. **Manual Invocation Model**
- V explicitly switches to persona (like Vibe Builder)
- Works as a lens/filter through which Zo sees debugging work
- Clear context: "You're not building, you're verifying"

### 3. **Cross-Conversation Support**
- Queries conversation registry (conversations.db)
- Navigates conversation workspaces
- Reconstructs systems from artifacts and logs
- Uses orchestrator + worker model to reverse-engineer

### 4. **Systematic 5-Phase Methodology**
1. **Reconstruct:** Understand components individually
2. **Trace:** Map system interactions and flows
3. **Test:** Validate systematically (happy/edge/error paths)
4. **Validate:** Check principle and requirement compliance
5. **Report:** Structured findings with actionable recommendations

### 5. **Principle-Driven Validation**
- Explicitly checks compliance with architectural principles
- Maps findings to specific principle violations
- Provides evidence-based, actionable fixes

---

## Structure (Mirrors Vibe Builder)

- **Core Identity:** Skeptical verification engineer
- **Pre-Flight:** Context loading (no limits), scope definition
- **Methodology:** 5-phase debug process
- **Critical Anti-Patterns:** What NOT to do
- **Tools:** Conversation registry, state inspection, workspace navigation
- **Integration:** N5 system, Zero-Touch validation
- **Testing Checklist:** Pre-test → Testing → Validation → Reporting
- **When to Invoke:** Verification use cases
- **Quality Standards:** Evidence-based, documented, honest
- **Self-Check:** Comprehensive validation checklist
- **Meta:** Living system, V's quality values

---

## How It Works

### **End-of-Conversation Debug (Primary Use Case)**

```
V: "Load Vibe Debugger persona"

Debugger:
1. Loads SESSION_STATE.md for objectives
2. Loads architectural principles
3. Loads relevant system components (no file limits)
4. Reconstructs what was built
5. Tests systematically (dry-run → real → errors → edge cases)
6. Validates against principles + requirements
7. Reports: Critical issues | Warnings | Validated | Not tested
```

### **Cross-Conversation Debug**

```
V: "Debug the CRM consolidation from con_ABC123"

Debugger:
1. Queries conversations.db for con_ABC123
2. Navigates to /home/.z/workspaces/con_ABC123/
3. Reviews /home/workspace/N5/logs/threads/con_ABC123/
4. Reconstructs system from artifacts
5. [Same test/validate/report flow]
```

---

## Key Features

✅ **No arbitrary context limits** — Loads what's needed for thorough debugging  
✅ **Manual invocation** — Explicit persona switch by V  
✅ **Skeptical by design** — Assumes nothing works until tested  
✅ **Systematic methodology** — 5 phases ensure comprehensive coverage  
✅ **Cross-conversation capable** — Debugs work from old conversations  
✅ **Principle-aware** — Validates against architectural standards  
✅ **Evidence-based** — Specific findings, not vague complaints  
✅ **Actionable output** — Prioritized recommendations with fixes  
✅ **Coverage tracking** — Documents what was and wasn't tested  
✅ **Zero-Touch integration** — Validates flow design and automation  

---

## Integration with N5 System

**Architecture Alignment:**
- References architectural principles selectively
- Uses conversation registry for cross-conversation work
- Navigates standard N5 directory structure
- Validates Zero-Touch patterns (flow, AIR, minimal touch)

**Workflow:**
```
Build Phase → V invokes Vibe Builder → System built
Test Phase → V invokes Vibe Debugger → System validated
Report → Debug report with findings + recommendations
Fix Phase → V decides fixes → Vibe Builder implements
```

---

## Comparison: Builder vs. Debugger

| Aspect | Vibe Builder | Vibe Debugger |
|--------|--------------|---------------|
| **Mindset** | Optimistic constructor | Skeptical verifier |
| **Role** | Build systems | Find what's broken |
| **Approach** | Requirements → Implementation | Artifacts → Validation |
| **Output** | Working code + docs | Debug report + recommendations |
| **Context** | Selective (Rule-of-Two) | Comprehensive (load as needed) |
| **Principles** | Apply while building | Validate after building |
| **When** | Design & implementation | Testing & verification |

---

## Example Invocation

**V:**
> "Load Vibe Debugger persona. I just built a lessons extraction workflow in this conversation. Verify it thoroughly — test all paths, check principle compliance, and give me a full report."

**Debugger Response:**
```
✓ Loaded Vibe Debugger persona
✓ Reviewing SESSION_STATE.md...
✓ Loading architectural principles...
✓ Loading workflow components: [file1, file2, file3]

Reconstructing system...
[Phase 1: Component inventory]
[Phase 2: Flow mapping]
[Phase 3: Testing — dry-run, real data, edge cases, errors]
[Phase 4: Principle validation]
[Phase 5: Report generation]

## Debug Report: Lessons Extraction Workflow
[Structured findings with evidence]
```

---

## Deliverables

1. ✅ **Persona Document** — `file 'Documents/System/vibe_debugger_persona.md'` (9,445 chars)
2. ✅ **Personas Index** — `file 'Knowledge/personas/README.md'` (updated)
3. ✅ **Design Summary** — This document
4. ✅ **Integration Notes** — How it fits with N5 and Vibe Builder

---

## Next Steps (Optional)

**If you want to enhance:**
1. **Test it:** Use on real system to refine methodology
2. **Add templates:** Pre-built test vectors for common system types
3. **Automate discovery:** Scripts to auto-discover components from conversation
4. **Metrics tracking:** Log debug sessions to improve over time

**Ready to use as-is:** Load the persona and start debugging.

---

*Designed and implemented: 2025-10-26*  
*By: Vibe Builder persona*  
*For: V's N5 system*
