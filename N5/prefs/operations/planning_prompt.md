# N5 Planning Discipline
**Operational Framework for System Design**

**Version:** 2.0  
**Created:** 2025-11-02  
**Based on:** Knowledge/architectural/planning_prompt.md (v1.0)  
**Auto-Load:** System builds, refactors, architectural decisions

---

## Purpose

Tactical planning framework for N5 system work. Translates philosophical DNA into executable workflows.

## Think → Plan → Execute Framework

### Time Allocation (Ben's Velocity Principles)
**70% Think + Plan** - Understand deeply, explore alternatives (Nemawashi), identify trap doors
**20% Review** - Verify criteria, test in production, check error paths
**10% Execute** - Generate code from plan, move fast

### Design Values

1. **Simple Over Easy** - Choose disentangled over convenient
2. **Flow Over Pools** - Every entry has exit conditions, track residence time
3. **Maintenance Over Organization** - Build detection, route exceptions
4. **Code Is Free, Thinking Is Expensive** - Spend 70% in Think+Plan
5. **Nemawashi** - Explore 2-3 alternatives explicitly

## P36: Orchestration Pattern

**When:** Complex work spans multiple domains

### Structure


###Execution Rules
1. Coordinator spawns specialized threads
2. Specialists work independently
3. Coordinator integrates results
4. Handoffs use structured formats
5. Each phase has explicit success criteria

## P37: Refactor Pattern

**When:** Improving existing system without full rebuild

### Rules
1. Read before writing
2. Preserve working parts
3. One concern at a time
4. Test after each change
5. Commit frequently

### Decision Matrix
- Refactor when: Core logic sound, 70%+ preservable
- Rebuild when: Core logic wrong, <50% survives

## Trap Door Identification

**Trap Door** = Irreversible or very-high-cost decision

### Recognition Triggers
- Core technology choice (database, runtime, file format)
- API design all consumers depend on
- Architectural pattern touching entire system

### When You Hit One
1. STOP - Don't proceed without V's input
2. Nemawashi - Explore 2-3 alternatives
3. Document - Write trade-offs, failure modes
4. Consult - Get V's approval
5. Record - Add to trap door registry

## Git Workflow

- Commit early, commit often
- Atomic commits (one logical change)
- Descriptive messages (what and why)
- Most work on main (personal system)
- Use branches for risky experiments

## Fast Feedback Loops

Design for:
- Run locally before deploying
- Test components in isolation
- Dry-run mode for destructive ops
- Immediate verification after writes
- Real-time logs

## Planning Checklist

### Think Phase
- What am I building and why?
- What are alternatives? (2-3)
- What are trap doors?
- What are trade-offs?
- What are failure modes?
- Is this simple or just easy?

### Plan Phase
- Write prose spec
- Define success criteria
- Identify verification steps
- Map information flows
- Specify confidence thresholds
- Document assumptions

### Execute Phase
- Generate code from plan
- Commit before risky changes
- Move fast

### Review Phase
- Verify all criteria met
- Test in production
- Check error paths
- Validate state after writes
- Fresh thread test

## When To Apply

**LOAD FOR:**
- Building new N5 scripts/workflows
- Refactoring systems
- Architectural decisions
- Infrastructure changes
- Multi-persona orchestration (P36)

**DON'T LOAD FOR:**
- Tactical command execution
- Simple file operations
- Research/content creation

## Self-Check Before Complete

- All success criteria met (not 60%, not 80%, ALL)
- Tested in production
- Error paths verified
- Documentation updated
- Fresh thread test passed
- Git committed

**P15 Violation:** Claiming complete when 60% done is most expensive failure

**Format:** "Status: X/Y done (Z%). Remaining: [list]"

---

*v2.0 | 2025-11-02*
