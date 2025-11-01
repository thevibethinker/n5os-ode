# Distributed Build System - Overview

**Version:** 1.0  
**Created:** 2025-10-17  
**Status:** Ready for use

---

## What Is This?

A multi-conversation orchestration system for implementing major changes to Zo. Splits large builds across independent worker conversations, coordinated by a central orchestrator.

**Key Innovation:** Context isolation = quality multiplication

---

## Quick Start

**5-Minute Primer:**

1. **When?** Changes > 500 LOC, multiple modules → Use distributed
2. **How?** Orchestrator decomposes → Workers build → Orchestrator integrates
3. **Why?** Each worker gets full attention on bounded problem = fewer bugs
4. **Who?** V (you) ferries messages between orchestrator and workers
5. **Where?** Active builds in `N5/logs/builds/`, completed in `N5/logs/threads/`

**Start here:** `file 'README.md'` → `file 'decision-tree.md'` → `file 'protocol.md'`

---

## Documentation Structure

### Entry Points
- **`README.md`** - Start here, navigation hub
- **`decision-tree.md`** - When to use distributed vs. sequential
- **`protocol.md`** - High-level workflow (stages, roles, timing)

### Operational Guides
- **`error-tracking-guide.md`** - Error codes, logging, recovery procedures
- **`troubleshooting.md`** - Common issues and solutions

### Templates
- **`templates/WORKER_ASSIGNMENT.md`** - Standard worker assignment
- **`templates/BUILD_STATE_SESSION.md`** - Build state tracking
- **`templates/INTEGRATION_CHECKLIST.md`** - Step-by-step integration
- **`templates/WORKER_ERROR_REPORT.md`** - Error documentation (generated as needed)

---

## System Components

### File Locations

**Active Builds:**
```
/home/workspace/N5/logs/builds/[build-name]/
├── BUILD_STATE_SESSION.md          # Central coordination file
├── assignments/
│   ├── WORKER_1_ASSIGNMENT.md      # V opens in new conversation
│   ├── WORKER_2_ASSIGNMENT.md
│   └── WORKER_N_ASSIGNMENT.md
├── workers/
│   ├── W1_SUMMARY.md               # Worker writes completion summary
│   ├── W1_ERROR_LOG.md             # If errors occur
│   └── W2_SUMMARY.md
└── integration/
    └── INTEGRATION_LOG.md           # Orchestrator tracks integration
```

**Completed Builds:**
```
/home/workspace/N5/logs/threads/[date]_[build-name]_[id]/
[Entire build folder moves here after completion]
```

**Implementation Code:**
```
/home/workspace/[wherever-it-belongs]/
[Workers write actual code to its final destination]
```

---

## Workflow Summary

### Stage 1: Framing (20-40 min, Orchestrator)
- V describes desired change
- Orchestrator asks clarifying questions
- Document shared understanding

### Stage 2: Decomposition (30-60 min, Orchestrator)
- Analyze codebase
- Identify module boundaries
- Create worker assignments (1 per module)
- Map dependencies
- Generate assignment files

### Stage 3: Worker Execution (Variable, per Worker)
- V opens new chat with WORKER_N_ASSIGNMENT.md
- Worker reads assignment
- Worker implements code
- Worker tests work
- Worker generates summary

### Stage 4: Integration (15-45 min per worker, Orchestrator)
- V returns to orchestrator: "Worker N done"
- Orchestrator reads summary
- Orchestrator reviews code
- Orchestrator tests integration
- Decision: ACCEPT / REVISE / REJECT
- Update state, lessons learned

### Stage 5: Validation (30-60 min, Orchestrator)
- After all workers integrated
- System-level testing
- Principle validation
- Documentation updates
- After-action report

### Stage 6: Archival (5 min, Orchestrator)
- Move build folder to N5/logs/threads/
- Preserve for posterity

---

## Roles

### Orchestrator (First Conversation)
- **Persona:** Vibe Builder
- **Does:** Framing, decomposition, integration, validation
- **Doesn't do:** Write implementation code

### Workers (Conversations 2-N)
- **Persona:** Vibe Builder (or other as appropriate)
- **Does:** Read assignment, implement code, test, summarize
- **Doesn't do:** Coordinate with other workers

### V (You)
- **Does:** Initiate, open worker chats, ferry messages, final decisions
- **Doesn't do:** Implementation (that's for AI)

---

## Key Principles

1. **Context isolation** - Each worker focuses on one bounded problem
2. **Explicit interfaces** - Define contracts between workers exactly
3. **Incremental integration** - One worker at a time, in dependency order
4. **Quality gates** - Test at each stage
5. **Continuous learning** - Update lessons after each integration

---

## Decision Framework

### Use Sequential (Single Conversation) When:
- < 500 LOC
- ≤ 2 files
- Single module
- Speed > quality
- Low risk

### Use Distributed (Multi-Conversation) When:
- \> 500 LOC
- \> 2 files
- Multiple modules
- Quality critical
- Complex dependencies

See `file 'decision-tree.md'` for detailed analysis.

---

## Error System

**Error Codes:**
- **E0xx:** Assignment/Setup
- **E1xx:** Dependencies/Interfaces
- **E2xx:** Implementation Quality
- **E3xx:** Integration
- **E4xx:** Testing
- **E5xx:** Principles/Architecture
- **W0xx-W5xx:** Warnings (non-blocking)

See `file 'error-tracking-guide.md'` for complete reference.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Rework cycles per worker | < 1 |
| Integration time per worker | < 30 min |
| Principle violations | 0 |
| Build completion rate | 100% |

---

## Common Pitfalls

1. **Vague assignments** → Constant questions/rework
   - **Fix:** Be extremely explicit, use examples

2. **Workers too large** → Context contamination returns
   - **Fix:** Keep workers 100-300 LOC

3. **Implicit interfaces** → Integration hell
   - **Fix:** Write out exact function signatures

4. **Skipping lessons learned** → Repeat mistakes
   - **Fix:** Update after EVERY integration

5. **Rushing integration** → Bugs slip through
   - **Fix:** Follow checklist, don't skip steps

See `file 'troubleshooting.md'` for complete guide.

---

## Evolution Path

**V1.0 (Current):**
- Basic distributed build workflow
- Error tracking
- Templates

**Future Enhancements:**
- Model selection per worker (use cheaper models for simple tasks)
- Automated testing gates
- Build visualization dashboard
- Success pattern library
- Integration automation

**After Each Build:**
1. Generate after-action report
2. Identify improvements
3. Update templates
4. Version bump

---

## Learning Path

**First Time:**
1. Read all docs (1-2 hours)
2. Pick pilot build (800-1200 LOC, 3-4 workers)
3. Follow protocol exactly (don't improvise)
4. Document everything
5. Review lessons

**Second Build:**
1. Apply lessons from first build
2. Refine assignments based on experience
3. Start developing intuition

**Third+ Builds:**
1. Process becomes natural
2. Focus on optimization
3. Contribute improvements to system

---

## Philosophy

**Why this approach?**

Traditional single-conversation builds suffer from **context contamination** at scale:
- 1000+ LOC in one conversation = LLM loses track
- Multiple modules = cognitive overload
- Complex dependencies = more bugs

**Distributed builds solve this:**
- Each worker = 100-300 LOC = manageable context
- Bounded scope = full attention
- Clear interfaces = fewer integration bugs
- Incremental testing = catch issues early

**Trade-off:**
- Time: Coordination overhead (30-60 min)
- Benefit: Quality multiplication (fewer bugs, better architecture)

**When it's worth it:** Any critical change > 500 LOC

---

## Integration with N5 System

This distributed build system is part of the N5 operating system:

- **Prefs:** `/home/workspace/N5/prefs/operations/distributed-builds/`
- **Logs:** `/home/workspace/N5/logs/builds/` (active), `N5/logs/threads/` (archived)
- **Scripts:** (Future: automation scripts for build orchestration)
- **Knowledge:** Architectural principles inform quality gates

---

## Commands (Future)

Potential registered commands:

- `/build-start` - Initialize new distributed build
- `/build-status` - Check current build state
- `/worker-create` - Generate new worker assignment
- `/worker-integrate` - Integrate completed worker

**V1.0:** Manual workflow (follow protocol.md)  
**V2.0:** Command automation

---

## Support

**If stuck:**
1. Check `file 'troubleshooting.md'`
2. Review `file 'error-tracking-guide.md'`
3. Re-read `file 'protocol.md'`
4. Document the issue for future inclusion in troubleshooting

**If system needs improvement:**
1. Note in after-action report
2. Update relevant template
3. Version bump system

---

## Quick Reference Card

```
WHEN: Change > 500 LOC, multiple modules
HOW:  Orchestrator decomposes → Workers build → Orchestrator integrates
WHO:  V ferries messages between conversations
TIME: Setup 1h + Workers (parallel) + Integration 30m/worker

ORCHESTRATOR TASKS:
1. Frame problem (with V)
2. Decompose into workers
3. Generate assignments
4. Monitor progress
5. Integrate outputs
6. Validate system
7. Archive build

WORKER TASKS:
1. Read assignment
2. Update state → IN_PROGRESS
3. Implement code
4. Test thoroughly
5. Generate summary
6. Update state → REVIEW

V TASKS:
1. Initiate build
2. Open worker conversations
3. Ferry status updates
4. Make final decisions on blockers
5. Approve integrations

LOCATIONS:
Active:     /home/workspace/N5/logs/builds/[build-name]/
Completed:  /home/workspace/N5/logs/threads/[date]_[build-name]/
Code:       /home/workspace/[wherever-it-belongs]/
```

---

## Status: READY TO USE

All documentation complete. All templates created. System ready for first distributed build.

**Recommended First Build:**
- 800-1200 LOC
- 3-4 clear modules
- New N5 subsystem (greenfield > refactor for first build)

**Start:** `file 'README.md'` → `file 'decision-tree.md'` → `file 'protocol.md'`

---

**Last Updated:** 2025-10-17 02:47 ET  
**Version:** 1.0  
**Maintainer:** V
