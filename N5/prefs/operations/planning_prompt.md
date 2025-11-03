# N5 Planning Discipline
**Operational Framework for System Design**

**Version:** 3.0  
**Created:** 2025-11-02  
**Updated:** 2025-11-02
**Based on:** Knowledge/architectural/planning_prompt.md (v1.0) + Ben's Velocity Principles  
**Auto-Load:** System builds, refactors, architectural decisions

---

## Purpose

Tactical planning framework for N5 system work. Translates philosophical DNA into executable workflows. Load this before any significant system building, refactoring, or architectural work.

## Think → Plan → Execute Framework

### Time Allocation (Ben's Velocity Principles)

**70% Think + Plan** - Understand deeply, explore alternatives (Nemawashi), identify trap doors  
**20% Review** - Verify criteria, test in production, check error paths  
**10% Execute** - Generate code from plan, move fast

**Critical insight:** All code quality comes from planning quality. Execution is mechanical.

### Design Values

1. **Simple Over Easy** - Choose disentangled over convenient (Rich Hickey)
2. **Flow Over Pools** - Every entry has exit conditions, track residence time
3. **Maintenance Over Organization** - Build detection, route exceptions
4. **Code Is Free, Thinking Is Expensive** - AI generates unlimited code; your strategic thinking is the constraint
5. **Nemawashi** - Explore 2-3 alternatives explicitly before deciding

## The Squishy ↔ Deterministic Spectrum

**Core Principle:** Different work requires different approaches. Gravitate toward determinism for stability over time.

### Three Zones

**Zone 1: Squishy LLM + Squishy Format (Markdown)**
- **Use for:** Exploration, brainstorming, initial drafts
- **Characteristics:** High flexibility, low reproducibility
- **Example:** Ideation notes, research synthesis, meeting summaries
- **Risk:** Content drift over time, format inconsistency
- **When appropriate:** Early phases, throwaway work

**Zone 2: Squishy LLM + Structured Format (YAML, CSV)** ⭐ **SWEET SPOT**
- **Use for:** Configuration, structured data, AI-generated content that needs stability
- **Characteristics:** AI-generated but constrained by format
- **Example:** Prompt configs, list maintenance, data extraction
- **Benefits:** Easier for LLMs than JSON, more stable than pure text
- **When appropriate:** Ongoing systems, versioned configs

**Zone 3: Deterministic Script + Structured Format (Python + SQLite)**
- **Use for:** Critical paths, exact transformations, scheduled jobs
- **Characteristics:** Maximum reproducibility, testable, predictable
- **Example:** File operations, database queries, state management
- **Benefits:** No hallucination risk, precise control, easily tested
- **When appropriate:** Production workflows, reliability-critical operations

### Choosing Your Zone

**Ask:**
- How often will this run? (Once → Zone 1, Daily → Zone 3)
- What's the cost of error? (Low → Zone 1, High → Zone 3)
- Do I need exact reproducibility? (No → Zone 1, Yes → Zone 3)
- Is this throwaway or permanent? (Throwaway → Zone 1, Permanent → Zone 3)

**Ben's Authority:** Gravitate toward determinism. Start squishy for exploration, migrate toward deterministic as system stabilizes.

## Ben's Velocity Principles (Integrated)

### Never Lose "Feel" for Code

**The Danger:** Generating without understanding creates dark forests—parts of codebase you fear touching.

**Discipline:**
- Always review generated code before committing
- If generating more code, you should feel MORE TIRED (thinking effort required)
- Develop "spidey sense" for brittle parts, places likely to break
- "Code that's nice will grow by itself with AI; bad code fights you"

**Anti-pattern:** "Just regenerate it" without understanding why it broke

### LLM Prompting Discipline

**Critical Rules:**

❌ **DON'T say:** 
- "use an LLM" 
- "call an AI"
- "query an AI service"
(Triggers external API hallucination—you're prompting me to call something external)

✅ **DO say:** 
- "Transform X to Y format"
- "Use your internal knowledge to analyze..."
- "Extract patterns from this content"
- "Apply [specific technique] to..."

**Why:** You ARE the LLM. Direct instruction > meta-prompting.

### File Format Preferences

**YAML > JSON**  
- Easier for LLMs (less syntax strictness)
- Fewer parsing errors
- More forgiving of human edits

**SQLite for organizing data**  
- Query > browse directories
- Not "folders for organization"
- Single-file database, portable

**CSV for simple tabular data**  
- Universal, simple
- LLM-friendly
- Easy to inspect

### Architecture Patterns from Ben

**Job Queues > File Watchers**
- Use explicit job queues (huey, simple-queue)
- Don't scan directories looking for work
- More deterministic, easier to debug

**Scripts Call Zo API**
- For agentic steps within deterministic workflows
- Script orchestrates (deterministic), Zo provides intelligence (squishy)
- Don't force Zo to manage infrastructure

**Separate Orchestration**
- Don't edit existing complex code
- Create separate orchestration points
- Producer/consumer with file markers

**Pattern Example:**
```
❌ DON'T: Edit process.py to add feature
✅ DO: Create enhance.py that consumes process.py outputs
```

**Why:** LLMs editing existing code → 63% failure rate (refactoring), 37% for edits. New code generation → much safer.

## P36: Orchestration Pattern

**When:** Work spans multiple domains, context limits, or needs distinct cognitive modes

### Structure

```
┌─────────────┐
│ Coordinator │ - Sets objectives, integrates results
└──────┬──────┘
       │
   ┌───┴────┬────────┐
   ▼        ▼        ▼
Specialist Specialist Specialist
(Builder) (Strategist) (Researcher)
```

### Execution Rules
1. Coordinator spawns specialized threads/personas
2. Specialists work independently with clear objectives
3. Coordinator integrates results
4. Handoffs use structured formats (YAML, CSV, not prose)
5. Each phase has explicit success criteria

### Example
```
# Coordinator defines:
- Objective: "Build X feature"
- Specialist A: "Research approaches, produce options.yaml"
- Specialist B: "Given options.yaml, implement choice"
- Integration: "Coordinator reviews, tests end-to-end"
```

## P37: Refactor Pattern

**When:** Improving existing system without full rebuild

### Rules
1. **Read before writing** - Understand what exists
2. **Preserve working parts** - Don't change what works
3. **One concern at a time** - Don't mix refactors
4. **Test after each change** - Commit small, test often
5. **Document why** - Future you needs context

### Decision Matrix: Refactor vs. Rewrite

**Refactor (Wrapper) When:**
- Core logic is sound (70%+ preservable)
- Small surface area to modify
- Can isolate changes
- Tests exist or easy to add
- Time-sensitive (refactor is faster)

**Rewrite When:**
- Core logic is flawed (<50% survives)
- Touching everything anyway
- No tests, hard to verify
- Architectural mismatch
- Would spend more time understanding than rebuilding

**Edge Case (50-70%):** Try wrapper first. If fighting it after 2 hours, switch to rewrite.

## Trap Door Identification

**Trap Door** = Irreversible or very-high-cost-to-reverse decision

### Recognition Triggers
- Core technology choice (database, runtime, file format)
- API design all consumers depend on
- Architectural pattern touching entire system
- Data format 1000+ files depend on
- External dependency (vendor lock-in)

### Trap Door Registry (Common Ones)

**Database Choice** (SQLite vs. PostgreSQL)
- **Cost to reverse:** 8-20 hours (migration + testing)
- **Decision factors:** Single-user? Local? → SQLite | Multi-user? Network? → PostgreSQL
- **N5 default:** SQLite (personal system, portable)

**File Format** (JSONL vs. SQLite vs. YAML)
- **Cost to reverse:** 2-10 hours depending on volume
- **Decision factors:** Append-only logs? → JSONL | Queryable? → SQLite | Config? → YAML
- **When to convert:** >1000 files, frequent queries → migrate to SQLite

**Script Language** (Python vs. Shell vs. Node)
- **Cost to reverse:** 4-12 hours per 500 lines
- **Decision factors:** See P22 (Language Selection)
- **When to switch:** Performance bottleneck, wrong tool for job

### When You Hit One
1. **STOP** - Don't proceed without V's input
2. **Nemawashi** - Explore 2-3 alternatives explicitly
3. **Document** - Write trade-offs, failure modes, cost to reverse
4. **Consult** - Get V's approval if architectural
5. **Record** - Add decision to trap door registry
6. **Review** - Revisit in 3 months—was this the right call?

### Trap Door Decision Template

```markdown
## Decision: [Technology/Pattern Choice]
**Date:** YYYY-MM-DD
**Decider:** V (after Builder Nemawashi)

### Alternatives Considered
1. Option A: [Pros/Cons/Cost to reverse]
2. Option B: [Pros/Cons/Cost to reverse]
3. Option C: [Pros/Cons/Cost to reverse]

### Decision: [Option X]
**Reasoning:** [Why this beats alternatives]
**Cost to Reverse:** [Hours estimate]
**Review Date:** [3-6 months out]

### Assumptions
- [List what must be true for this to work]

### Failure Modes
- [What breaks if assumptions wrong]
```

## Git Workflow

- Commit early, commit often
- Atomic commits (one logical change per commit)
- Descriptive messages (what + why, not just what)
- Most work on main (personal system, not team repo)
- Use branches for risky experiments only

## Fast Feedback Loops

Design for immediate verification:
- Run locally before deploying
- Test components in isolation
- Dry-run mode for destructive operations (P7)
- Immediate state verification after writes (P18)
- Real-time logs with context

## Quality Bars (Production-Grade)

### Code Quality
- `pathlib.Path` not string manipulation
- Type hints for function signatures
- Docstrings for non-obvious functions
- Explicit > implicit
- Descriptive variable names (not `tmp`, `x`, `data`)

### Error Handling
- Specific `except` clauses (not bare `except:`)
- Log with context (what failed, what state, what input)
- Never swallow errors silently
- Return proper exit codes (0 = success, 1+ = failure)

### File Quality
- `.md` for documentation (human-readable first, P1)
- `.py` for scripts (not shell unless 80%+ Unix tools)
- `.jsonl` for append-only logs
- `.yaml` for configs (not JSON)

### Communication Quality
- Concise (every word earns its place)
- Direct (no preamble, no throat-clearing)
- Factual (no speculation without explicitly marking it)
- Specific ("13/23 complete (56%)" not "mostly done")

### Production Testing

**Not Done Until:**
- ✅ Runs in production conditions (not just dev environment)
- ✅ Error paths tested (not just happy path)
- ✅ State verified after writes (don't assume success)
- ✅ Fresh thread test (can someone else understand this?)
- ✅ Dry-run works (for destructive operations)
- ✅ Git committed with clear message

**P15 Enforcement:** Report honest progress.

**Format:** "Status: X/Y complete (Z%). Remaining: [list]"

**Never say "Done" or "✓ Complete" when 60% done.** This is the most expensive failure mode.

## Planning Checklist

### Think Phase (40%)
- What am I building and why?
- What are alternatives? (2-3 via Nemawashi)
- What are trap doors? (irreversible decisions)
- What are trade-offs?
- What are failure modes?
- Is this simple (disentangled) or just easy (familiar)?

### Plan Phase (30%)
- Write prose specification (mini planning prompt)
- Define success criteria explicitly
- Identify verification steps (how will I know it works?)
- Map information flows (entry → transform → destination → exit)
- Specify confidence thresholds for automation
- Document assumptions explicitly (P21)

### Execute Phase (10%)
- Generate code from plan
- Commit before risky changes
- Move fast (quality already locked in from planning)

### Review Phase (20%)
- Verify ALL criteria met (not 13/23, ALL 23/23)
- Test in production conditions
- Check error paths work (not just happy path)
- Validate state after writes (P18)
- Fresh thread test (P12)
- **Actually run the code** (don't just read it)
- Test with real data (not just examples)
- Verify error messages are clear
- Check logs are useful for debugging

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
- Already mid-execution and on-track

## Self-Check Before Complete

- All success criteria met (not 60%, not 80%, **ALL**)
- Tested in production conditions
- Error paths verified
- State verified after writes
- Documentation updated
- Fresh thread test passed (P12)
- Git committed with clear message
- No undocumented placeholders (P21)

**Three-Level Slowdown Recognition:**

1. **Doing wrong thing** (worst) → Go back to Think phase, reconsider problem
2. **Doing it wrong way** (bites later) → Apply Nemawashi, explore alternatives  
3. **Doing it badly** (poor impl) → Review quality bars, increase execution care

**Prevention:** Proper Think→Plan→Execute sequence. Don't skip to execution.

---

## Integration with Other Prompts

**This prompt (planning)** = HOW to build (operational framework)  
**thinking_prompt** = HOW to think (mental models, strategic decisions)  
**navigator_prompt** = WHERE things are (N5 structure, file locations)

**Load order for complex work:**
1. `navigator_prompt` (if unclear where components live)
2. `thinking_prompt` (for strategic decisions, mental models)
3. `planning_prompt` (for execution framework)
4. Apply P36/P37 as patterns emerge

---

*v3.0 | 2025-11-02 | Expanded with Ben's velocity principles, squishy↔deterministic spectrum, trap door registry, quality bars, P36/P37 integration*
