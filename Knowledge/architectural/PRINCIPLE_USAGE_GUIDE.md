# Principle Usage Guide

**Version:** 1.0  
**Updated:** 2025-11-02  
**Audience:** AI personas, V, system designers

---

## Purpose

This guide explains how to use N5's 37 architectural principles effectively. Principles aren't documentation—they're enforcement mechanisms that trigger automatically during work.

---

## How Principles Work

### Automatic Triggering
Each principle defines trigger conditions in YAML:



When work matches trigger, principle loads and enforces pattern.

### Pre-Flight Loading
Personas load principles via pre-flight protocol:
1. Check embedded relevant_principles (8 per persona)
2. Load extended principles if pattern triggered
3. Apply loaded principles during execution
4. Reference principles by name in decision-making

### Priority Levels
Principles have priority ratings:
- **Critical:** P5 (safety), P15 (completion), P19 (error handling)
- **High:** P1 (human-readable), P2 (SSOT), P8 (minimal context)
- **Medium:** Most design and execution principles
- **Low:** Optimization and enhancement principles

---

## Core Principles (P0.1-P4)

### P0.1: LLM-First for Analysis and Synthesis
**Trigger:** Solving problems requiring understanding, analyzing patterns, creative problem-solving  
**Pattern:** Default to LLM reasoning for analysis and synthesis. Use scripts only for deterministic computation.

**Use when:**
- Analyzing qualitative data
- Pattern extraction from conversations
- Strategic decision-making
- Creative problem-solving

**Don't use for:**
- File operations (use scripts)
- Data transformation (use scripts)
- Deterministic computation

**Example:**
Good: AI analyzes meeting transcript to extract themes  
Bad: AI tries to parse JSON with regex instead of using Python

### P1: Human-Readable First
**Trigger:** Creating output files, documentation, data structures  
**Pattern:** Generate human-readable content first (markdown, text); derive machine formats from it. Never start with JSON skeletons.

**Use when:**
- Creating new files
- Designing data structures
- Writing documentation
- Building frameworks

**Workflow:**
1. Write human-readable version (markdown, prose)
2. Derive machine-readable format if needed (JSON, YAML)
3. Keep human version as source of truth

**Example:**
Good: Write principle in markdown → Convert to YAML  
Bad: Start with JSON structure → Fill in content

### P2: Single Source of Truth (SSOT)
**Trigger:** Storing factual information, creating reference documentation  
**Pattern:** Each fact lives in exactly one canonical location. All other references link rather than duplicate.

**Use when:**
- Documenting decisions
- Storing configuration
- Maintaining reference data
- Cross-referencing information

**Implementation:**
- One canonical file per concept
- Other locations link to canonical source
- Update only canonical source
- Scripts validate references

**Example:**
Good: Principle P15 defined in P15_complete_before_claiming.yaml, persona references by name  
Bad: Copy P15 definition into multiple persona files

### P3: Voice Integration Policy
**Trigger:** Processing extracted information, creating user-facing outputs  
**Pattern:** Apply appropriate voice levels - neutral for extraction, full voice for user-facing deliverables.

**Voice levels:**
- Level 0 (Neutral): Raw extraction, data processing
- Level 1 (Minimal): Internal documentation, technical notes
- Level 2 (Balanced): Mixed audience, technical + business
- Level 3 (Full V-voice): User-facing content, external communication

**Use when:**
- Processing meeting notes (Level 0 → Level 3)
- Creating documentation (Level 1-2)
- Writing user-facing content (Level 3)

### P4: Ontology-Weighted Analysis
**Trigger:** Processing information extraction, analyzing content for insights  
**Pattern:** Use P1-P7 as high priority emphasis. Weight extraction based on ontological importance.

**Priority order:**
1. Principles (P1-P7)
2. Decisions and commitments
3. Action items and deadlines
4. Insights and patterns
5. Context and background

**Use when:**
- Processing information-dense content
- Extracting key points from meetings
- Prioritizing attention during analysis

---

## Safety Principles (P5-P7, P11, P19, P21, P23)

### P5: Safety, Determinism, Anti-Overwrite
**Trigger:** Writing/modifying files, destructive operations  
**Pattern:** Never overwrite without confirmation. Auto-version on conflict (_v2, _v3). Keep rolling backup and audit logs.

**Critical:** Non-negotiable for file operations

**Workflow:**
1. Check if file exists
2. If exists, create versioned copy
3. Maintain audit trail
4. Provide rollback capability

### P7: Idempotence and Dry-Run by Default
**Trigger:** Building workflows that write files or have side effects  
**Pattern:** Support dry-run mode. Re-running same instruction produces identical end-state.

**Implementation:**
- All scripts support --dry-run flag
- Show preview before execution
- Idempotent operations (run twice = run once)

### P11: Failure Modes and Recovery
**Trigger:** Processing inputs, encountering errors, before destructive operations  
**Pattern:** Pause on uncertainty >25%. Log exceptions with context. Halt before destructive actions on error.

**Decision tree:**
- <25% uncertainty: Proceed with logging
- 25-50% uncertainty: Pause, ask for clarification
- >50% uncertainty: Stop, report state, request input

### P19: Error Handling is Not Optional
**Trigger:** Writing any code, building workflows  
**Pattern:** All code paths have error handlers. All errors logged with context. No silent failures.

**Requirements:**
- Try/except blocks for all operations
- Specific exception handling (not bare except)
- Log context: what was attempted, what failed, system state

### P21: Document All Assumptions
**Trigger:** Building frameworks, making strategic recommendations  
**Pattern:** Explicit > implicit. State assumptions, constraints, confidence levels. Make uncertainty visible.

**Format:**
- "Assuming X, then Y"
- "Confidence: 70% because Z"
- "Constraint: Must complete by date D"

### P23: Identify Trap Doors
**Trigger:** Planning complex work, making architectural decisions  
**Pattern:** Before proceeding, identify decisions that are expensive to reverse. Consider alternatives. Choose deliberately.

**Examples of trap doors:**
- Database selection
- Framework choice
- File format standards
- Directory structure

**Process:**
1. Identify trap door decisions
2. List alternatives
3. Document trade-offs
4. Choose deliberately
5. Record rationale

---

## Quality Principles (P15-P16, P18, P20, P28, P30, P33)

### P15: Complete Before Claiming
**Trigger:** Reporting progress, delivering work  
**Pattern:** Report honest progress "X/Y done (Z%)" not "✓ Done" unless ALL complete. Most expensive failure mode.

**Critical:** This is the most expensive failure mode

**Format:**
- "Completed: [list]. Remaining: [list]. Status: X/Y (Z%)."
- Only "✓ Done" when 100% complete
- Never claim done at 60-90%

**Example:**
Good: "Completed 4/7 principles (57%). Remaining: P22, P25, P32."  
Bad: "✓ Principles complete" (when 3 remain)

### P16: Accuracy Over Sophistication
**Trigger:** Claiming capabilities, citing documentation, stating limits  
**Pattern:** Cite docs or say "unknown" - never fabricate API limits, capabilities, or facts.

**Rules:**
- If you don't know, say "I don't know"
- If uncertain, say "uncertain, need to verify"
- Cite sources for claims
- Never invent API limits or capabilities

### P18: State Verification is Mandatory
**Trigger:** After file writes, destructive operations, data transforms  
**Pattern:** Always verify write succeeded, file contains expected content, state matches intent.

**Workflow:**
1. Perform operation
2. Verify state changed as expected
3. Log verification result
4. If verification fails, report and halt

### P20: Modular Design for Context Efficiency
**Trigger:** Building complex systems, designing workflows  
**Pattern:** Break into independent modules. Each module self-contained. Minimize cross-dependencies.

**Benefits:**
- Fits in context windows
- Easier to understand
- Simpler to modify
- Better error isolation

### P28: Plans As Code DNA
**Trigger:** Creating strategic frameworks, designing systems  
**Pattern:** Strategy quality determines implementation quality. Poor upstream planning = inevitable downstream bugs.

**Time split:** 70% think+plan, 20% review, 10% execute

**Process:**
1. Think (40%): What, why, trap doors, alternatives
2. Plan (30%): Prose spec, success criteria, decisions
3. Execute (10%): Build from plan
4. Review (20%): Test vs plan, principle compliance

### P30: Maintain Feel For Code
**Trigger:** Building infrastructure, designing workflows  
**Pattern:** Understand what you're building at system level. Not just syntax—how components interact, where bottlenecks emerge.

**Avoid:** Copy-paste without understanding, black-box abstractions, cargo-culting patterns

### P33: Old Tricks Still Work
**Trigger:** Solving problems, selecting tools  
**Pattern:** Unix tools, grep, awk, shell scripts often outperform complex solutions. Prefer boring technology.

**Examples:**
- grep for search (vs custom parser)
- awk for data transform (vs Python script)
- Shell pipeline (vs multi-stage processing)

---

## Design Principles (P8-P10, P13-P14, P22, P35)

### P8: Minimal Context, Maximal Clarity
**Trigger:** Designing prompts, loading context, building workflows  
**Pattern:** Keep prompts self-contained. Avoid excessive file loading. Load only what's needed for precision.

**Rules:**
- Embed essential info in prompt
- Reference files only when needed for precision
- Don't load "just in case"
- Test prompts in fresh threads (P12)

### P13: Naming and Placement
**Trigger:** Creating new files/directories, organizing content  
**Pattern:** Follow established conventions. Ask for location if ambiguous. Never create new roots without consent.

**Workflow:**
1. Scan existing structure
2. Follow naming patterns
3. If ambiguous, ask
4. Never create new top-level directories

### P22: Language Selection for Purpose
**Trigger:** Writing scripts, choosing tools  
**Pattern:** Match language to task characteristics, not habit.

**Decision tree:**
- 80%+ Unix tools → Shell
- API-heavy + SDK → Node.js/TypeScript
- Performance daemon → Go
- Complex logic → Python
- Prototyping → Python
- Default → Python

**Trade-offs:**
- Shell: Fast glue, poor complex logic
- Python: Best LLM corpus, memory-heavy, general default
- Node.js: First-class web APIs, native async
- Go: Performance, worse ergonomics, smaller corpus

---

## Execution Principles (P24-P27, P29, P31-P32, P34)

### P24: Simulation Over Doing
**Trigger:** Before destructive operations, complex workflows  
**Pattern:** Dry-run first. Preview impact. Validate assumptions. Then commit.

**Always simulate:**
- File deletions
- Bulk operations
- Schema changes
- Data migrations

### P26: Fast Feedback Loops
**Trigger:** Building workflows, designing systems  
**Pattern:** Optimize for rapid iteration. Test quickly. Fail fast. Learn early.

**Techniques:**
- Unit tests
- Quick validation scripts
- Incremental builds
- Continuous verification

### P27: Nemawashi Mode
**Trigger:** Planning complex work, making architectural decisions  
**Pattern:** Pre-socialize decisions. Consider 2-3 alternatives before committing. Build consensus.

**Process:**
1. Identify decision
2. Generate 2-3 alternatives
3. Present trade-offs
4. Get input
5. Decide together

### P31: Own The Planning Process
**Trigger:** Beginning complex work  
**Pattern:** Front-load thinking. Invest in planning. Don't rush to execution.

**Time distribution:** 70% think+plan, 20% review, 10% execute

### P32: Simple Over Easy
**Trigger:** Choosing between implementation approaches  
**Pattern:** Simple = few components, easy to understand. Easy = convenient now, complex later. Choose simple.

**Trade-off:**
- Simple: Harder upfront, easier long-term, fewer moving parts
- Easy: Easier upfront, harder long-term, hidden complexity

---

## Advanced Principles (P36-P37)

### P36: Orchestration Pattern
**Trigger:** Work spanning multiple domains, context limits, distinct cognitive modes needed  
**Pattern:** Coordinator spawns specialists with clear objectives. Each phase has explicit success criteria.

**Use for:**
- Multi-phase projects
- Cross-domain work
- Context-heavy tasks

**Structure:**
- Coordinator defines phases
- Each phase has success criteria
- Specialists execute phases
- Coordinator validates completion

### P37: Refactor Pattern
**Trigger:** Core logic sound but messy, 70%+ code preservable  
**Pattern:** Read before writing. Preserve working parts. One concern at a time. Test after each change.

**Process:**
1. Read and understand current code
2. Identify what works
3. Preserve working parts
4. Refactor one concern at a time
5. Test after each change
6. Never "rewrite from scratch"

---

## Usage Patterns

### For AI Personas
1. Load relevant principles via pre-flight protocol
2. Reference principles by name during work
3. Cite principles in decision rationale
4. Report principle compliance at completion

### For Script Design
1. Implement P5 (safety), P7 (dry-run), P19 (error handling)
2. Follow P22 (language selection)
3. Support P26 (fast feedback)
4. Enable P18 (state verification)

### For Workflow Design
1. Apply P28 (plan DNA) - front-load planning
2. Use P36 (orchestration) for multi-phase work
3. Implement P24 (simulation) for safety
4. Follow P20 (modular design) for clarity

### For Documentation
1. Follow P1 (human-readable first)
2. Maintain P2 (SSOT)
3. Apply P3 (voice integration)
4. Document via P21 (assumptions)

---

## Common Mistakes

**Claiming done early (P15 violation)**
Symptom: "✓ Done" when 60% complete  
Fix: Report "X/Y done (Z%)" until 100%

**Inventing limits (P16 violation)**
Symptom: "API limit is 100 requests" (without checking docs)  
Fix: Cite docs or say "unknown, need to verify"

**Skip dry-run (P7, P24 violation)**
Symptom: Delete files without preview  
Fix: Always show dry-run first, require confirmation

**Copy-paste without understanding (P30 violation)**
Symptom: Implement code without system-level understanding  
Fix: Explain how it works, where it fits, what it affects

**Excessive file loading (P8 violation)**
Symptom: Load 10 files "just in case"  
Fix: Load only what's needed for precision

---

## Validation

### Self-Check Questions
- Did I follow P15 (report honest progress)?
- Did I apply relevant safety principles (P5, P7, P11, P19)?
- Did I cite sources for claims (P16)?
- Did I verify state after operations (P18)?
- Did I load minimal context (P8)?

### Automated Checks
- Schema validation: All YAML principles validate against schema
- Cross-reference validation: All principle references valid
- Protection checks: File operations respect n5_protect.py
- Risk assessment: Destructive ops scored via risk_scorer.py

---

## Related Documentation

- file 'Knowledge/architectural/ARCHITECTURAL_OVERVIEW.md' - System architecture
- file 'N5/prefs/principles/principles_index.yaml' - Principle index
- file 'N5/schemas/principle.schema.json' - YAML schema
- file 'N5/prefs/system/nuance-manifest.md' - System behavior patterns

---

Last updated: 2025-11-02 21:10 ET
