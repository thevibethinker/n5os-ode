---
date: "2025-10-12T00:00:00Z"
category: workflow
priority: high
tags:
  - architecture
  - design
  - principles
  - system-change
---
# System Design Workflow

**Purpose:** Standard workflow for major system changes (scripts, infrastructure, workflows, refactors)

**When to use:** Before building or modifying any significant system component

**Duration:** 15-30 minutes for design phase + implementation time

---

## Quick Start

```markdown
I need to [build/modify/refactor] [system component].

Before we begin, load the architectural principles and help me 
design this properly.

Reference: command 'N5/commands/system-design-workflow.md'
```

---

## Workflow Steps

### Phase 0: Load Architectural Principles (MANDATORY)

**Before ANY design or implementation:**

```markdown
Load 
```

`file Knowledge/architectural/architectural_principles.md`   (index) Load `file Knowledge/architectural/principles/core.md`   Load `file Knowledge/architectural/principles/safety.md`   Load `file Knowledge/architectural/principles/quality.md` 

**Optional (load if relevant to your task):**

```markdown
Load 
```

`file Knowledge/architectural/principles/design.md`   (for design reviews) Load `file Knowledge/architectural/principles/operations.md`   (for ops/deployment)

**Why:** Ensures compliance with established principles and avoids repeating past mistakes.

**Time:** 2-3 minutes

---

### Phase 1: Requirements & Context (5 min)

**Questions to answer:**

1. **What problem are we solving?**

   - Clear objective statement
   - Success criteria

2. **What are the constraints?**

   - Performance requirements
   - Compatibility needs
   - User preferences

3. **What's the scope?**

   - What's included
   - What's explicitly excluded
   - Clear boundaries

**Deliverable:** Requirements document or summary

---

### Phase 2: Architectural Review (10 min)

**Check against principles:**

- [ ]  **Principle 2:** Single Source of Truth - no redundancy

- [ ]  **Principle 5:** Anti-overwrite - safe file handling

- [ ]  **Principle 7:** Dry-run support - test before committing

- [ ]  **Principle 8:** Minimal context - efficient design

- [ ]  **Principle 11:** Error handling - failure modes documented

- [ ]  **Principle 15:** Complete before claiming complete - clear definition of done

- [ ]  **Principle 16:** Accuracy over sophistication - facts over speculation

- [ ]  **Principle 17:** Test with production config - real environment validation

- [ ]  **Principle 18:** State verification - check writes succeeded

- [ ]  **Principle 19:** Error handling - explicit recovery paths

- [ ]  **Principle 20:** Modular design - selective loading enabled

**Deliverable:** Compliance checklist + design notes

---

### Phase 3: Design Specification (10-15 min)

**Document:**

1. **System architecture**

   - Components and their relationships
   - Data flow
   - Integration points

2. **File structure**

   - What files will be created/modified
   - Where they'll be stored
   - Naming conventions

3. **Error handling**

   - What can go wrong
   - How to recover
   - What gets logged

4. **Testing strategy**

   - How to validate it works
   - Dry-run approach
   - Production validation plan

**Deliverable:** Design spec document

---

### Phase 4: Implementation

**Before coding:**

- [ ]   Review architectural principles one more time

- [ ]   Confirm design spec is complete

- [ ]   Have clear definition of "done"

**During implementation:**

- [ ]   Write code following principles

- [ ]   Add error handling as you go

- [ ]   Add dry-run support if applicable

- [ ]   Document as you build

**Deliverable:** Implemented system

---

### Phase 5: Validation

**Test checklist:**

- [ ]   Dry-run test passes

- [ ]   Production configuration test passes

- [ ]   Error paths tested

- [ ]   State verification works

- [ ]   All success criteria met

- [ ]   Documentation complete

**Deliverable:** Test results + confirmation of completion

---

## Anti-Patterns to Avoid

❌ **Starting implementation without loading principles**

- Always load architectural principles first

❌ **Skipping error handling "for now"**

- Error handling is not optional (Principle 19)

❌ **Testing with wrong configuration**

- Test with production config (Principle 17)

❌ **Claiming complete before full validation**

- Complete means ALL objectives met (Principle 15)

❌ **Adding sophistication over accuracy**

- Facts over speculation (Principle 16)

---

## Integration with Existing Workflows

### For Script Development

1. Load architectural principles
2. Follow this workflow
3. Use 5-phase framework (Analysis → Design → Implementation → Validation → Documentation)

### For System Refactoring

1. Load architectural principles
2. Load existing system documentation
3. Follow this workflow with emphasis on backward compatibility

### For New Infrastructure

1. Load architectural principles
2. Check naming and placement (Principle 13)
3. Follow this workflow with emphasis on integration points

---

## File References

**Core documents:**

- `file Knowledge/architectural/architectural_principles.md`   - **LOAD FIRST**
- `file N5/commands/function-import-system.md`   - 5-phase implementation framework
- `file N5/prefs/prefs.md`   - User preferences

**Related workflows:**

- Thread export system: Example of principle-driven design
- Meeting monitor system: Example of phased implementation

---

## Quick Reference Commands

### Start a system design session

```markdown
Load 
```

`file Knowledge/architectural/architectural_principles.md`   Load `command N5/commands/system-design-workflow.md`    I need to build \[system component\]. Let's design it properly using the architectural principles.

### Review principles mid-project

```markdown
Reload file 'Knowledge/architectural/architectural_principles.md'
Check our current design against principles 5, 7, 11, 15-20.
```

### Validate before claiming complete

```markdown
Review principles 15-19. Are we truly complete?
Have we tested with production config?
Is error handling in place?
```

---

## Enforcement Mechanism

**This workflow should be used when:**

- Building new scripts or workflows
- Refactoring existing systems
- Modifying infrastructure
- Creating automated tasks
- Designing data structures
- Planning major features

**How to ensure it's used:**

- User rules reference this workflow for major changes
- Architectural principles document references this workflow
- Key system documents link to this workflow

---

**Version:** 1.0\
**Last Updated:** 2025-10-12\
**Status:** Active