# Session State System - Phase 3 & 4 Implementation

**Objective:** Surgical distributed builds with central monitoring, minimize context overload, maximize quality/resilience

**Updated:** 2025-10-16T06:09 EST

---

## Mission

Build "mission control" for distributed work across Zo conversations:
- Break large builds into focused conversations
- Monitor everything from central orchestrator
- Prevent context window overload
- Maximize quality, minimize bugs
- Surgical precision on each component

---

## Implementation Order

### **1. Integration Test Runner** (Critical - Foundation)
**Why first:** Everything else needs validated implementations
- Orchestrator must verify worker outputs actually work
- Prevents cascading failures
- Foundation for quality gates

**Scope:**
- Execute tests against worker deliverables
- Report results to orchestrator SESSION_STATE
- Support multiple test types (unit, integration, smoke)
- Auto-detect test frameworks (pytest, bun test, etc.)

---

### **2. Auto-Classification** (Critical - Automation)
**Why second:** Reduces manual overhead, enables scale
- Auto-detect conversation type from first message
- Auto-initialize appropriate SESSION_STATE template
- Reduces cognitive load on V and workers

**Scope:**
- Keyword-based classification (build, research, discussion, planning)
- Confidence scoring
- Override mechanism
- Integration with session_state_manager.py init

---

### **3. Dependency Graph Visualization** (Critical - Visibility)
**Why third:** Central monitoring depends on seeing relationships
- Visualize conversation dependencies
- Track data flow between workers
- Identify bottlenecks and risks
- D2 diagram generation

**Scope:**
- Parse SESSION_STATE.md dependencies
- Build directed graph
- Render with D2
- Update on orchestrator dashboard

---

### **4. Principle Violation Detection** (Important - Quality)
**Why fourth:** Quality layer on top of working system
- Auto-detect P15, P16, P19 violations in worker output
- Flag before orchestrator review
- Prevent common mistakes

**Scope:**
- Parse architectural principles
- Build detection rules (regex, AST, heuristics)
- Run on worker SESSION_STATE.md and deliverables
- Report in orchestrator dashboard

---

## Success Criteria

**Phase 3 Complete:**
- [ ] Orchestrator can run tests on worker deliverables
- [ ] Tests pass/fail reported in SESSION_STATE
- [ ] Auto-classification works on init
- [ ] Dependency graph renders correctly

**Phase 4 Complete:**
- [ ] Principle violations auto-detected
- [ ] False positive rate < 20%
- [ ] Integration with orchestrator dashboard

**System Complete:**
- [ ] V can start orchestrator conversation
- [ ] Orchestrator spawns 2+ worker conversations
- [ ] Workers complete tasks independently
- [ ] Orchestrator monitors via SESSION_STATE
- [ ] Integration tests validate outputs
- [ ] Dependency graph shows relationships
- [ ] Principle violations flagged
- [ ] Everything merges successfully

---

## Architecture Notes

**Modular:** Each feature is independent script
**Compatible:** Works with existing build_tracker, orchestrator, message_queue
**Principle-compliant:** P0 (Rule-of-Two), P7 (Dry-run), P19 (Error handling)

---

## Next Action

Implement integration test runner first.
