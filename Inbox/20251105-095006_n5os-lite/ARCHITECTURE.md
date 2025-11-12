# N5OS Lite Architecture

## Design Philosophy

N5OS Lite is an architectural framework for AI-assisted system building. It's not software you run—it's a set of patterns, principles, and procedures that shape how you work with AI.

### Core Insight

**The constraint in AI-assisted development isn't code generation—it's strategic thinking.**

AI can generate unlimited code. What's scarce is:
- Clear problem definition
- Good architectural decisions  
- Thoughtful trade-off analysis
- Systematic planning

N5OS Lite optimizes for these scarce resources.

## Design Values

### 1. Simple Over Easy

**Simple** = Disentangled, composable, understandable  
**Easy** = Convenient, familiar, quick to start

We choose simple. Easy leads to complexity debt.

**Example:**
- ❌ Easy: One mega-script that does everything
- ✅ Simple: Separate scripts with clean interfaces

### 2. Flow Over Pools

Everything has exit conditions. Nothing pools indefinitely.

**Inbox/** has exit conditions (file to Project, Knowledge, or Archive)  
**In-progress work** has completion criteria  
**Temporary files** have cleanup schedules

Stagnation is technical debt.

### 3. Maintenance Over Organization

Don't just organize things—build systems that detect problems and route exceptions.

**Example:**
- ❌ "Organize files into folders"
- ✅ "Build detection for misplaced files + routing rules"

### 4. Code Is Free, Thinking Is Expensive

AI generates code easily. Your strategic thinking is the bottleneck.

**Implication:** Spend 70% of time on Think+Plan, 10% on Execute.

### 5. Human-Readable First

Generate prose and markdown first. Derive structured formats from it.

**Why:** Humans need to understand and maintain systems. Structure follows understanding.

## Architecture Patterns

### Think → Plan → Execute

Time allocation framework for any significant work:

```
┌──────────────┐
│   Think 40%  │  What/Why/Alternatives/Trap doors
└──────┬───────┘
       │
┌──────▼───────┐
│   Plan 30%   │  Prose spec/Success criteria/Assumptions
└──────┬───────┘
       │
┌──────▼───────┐
│  Execute 10% │  Generate from plan/Move fast
└──────┬───────┘
       │
┌──────▼───────┐
│  Review 20%  │  Test everything/Verify all criteria
└──────────────┘
```

**Critical Insight:** All code quality comes from planning quality. Execution is mechanical.

### Squishy ↔ Deterministic Spectrum

Different work requires different approaches:

**Zone 1: Squishy (Markdown)**
- Exploration, brainstorming
- High flexibility, low reproducibility
- Use for: Early phases, throwaway work

**Zone 2: Structured (YAML/CSV)** ⭐
- AI-generated, format-constrained
- Balance of flexibility and stability  
- Use for: Configs, ongoing systems

**Zone 3: Deterministic (Python + SQLite)**
- Maximum reproducibility
- No hallucination risk
- Use for: Critical paths, production workflows

**Guidance:** Start squishy, migrate toward deterministic as system stabilizes.

### Orchestration Pattern (P36)

For complex multi-domain work:

```
┌─────────────┐
│ Coordinator │ ← Sets objectives, integrates results
└──────┬──────┘
       │
   ┌───┴────┬────────┐
   ▼        ▼        ▼
Specialist Specialist Specialist
(Builder)  (Strategist)(Researcher)
```

**Execution:**
1. Coordinator spawns specialists with clear objectives
2. Specialists work independently
3. Coordinator integrates results
4. Handoffs use structured formats (YAML, not prose)
5. Each phase has explicit success criteria

**Example:** Research (Researcher) → Design (Architect) → Build (Builder) → Document (Writer)

### Refactor Pattern (P37)

Decision matrix for improving existing systems:

**Refactor When:**
- Core logic sound (70%+ preservable)
- Small surface area to modify
- Can isolate changes
- Tests exist

**Rewrite When:**
- Core logic flawed (<50% survives)
- Touching everything anyway
- No tests, hard to verify
- Architectural mismatch

**Edge Case (50-70%):** Try refactor first. If fighting it after 2 hours, switch to rewrite.

## Key Concepts

### Trap Doors

Irreversible or high-cost-to-reverse decisions.

**Common Trap Doors:**
- Database choice (8-20 hour reversal cost)
- File format (2-10 hour reversal cost)
- Script language (4-12 hour reversal cost)
- API design (many consumers depend on it)

**When You Hit One:**
1. STOP - Don't proceed without careful analysis
2. Nemawashi - Explore 2-3 alternatives explicitly
3. Document - Trade-offs, failure modes, cost to reverse
4. Record - Add to trap door registry
5. Review - Revisit in 3 months

### Nemawashi

Japanese concept: Laying groundwork for decision by exploring alternatives.

**In Practice:** Before deciding, explicitly consider 2-3 alternatives:
- Option A: Pros/Cons/Cost to reverse
- Option B: Pros/Cons/Cost to reverse  
- Option C: Pros/Cons/Cost to reverse

**Benefit:** Prevents premature convergence. Documents trade-offs. Reveals hidden options.

### Single Source of Truth (P2)

Each fact lives in exactly one canonical location.

**Anti-pattern:** Same information copied across multiple files
**Correct:** One canonical source, others link to it

**Benefit:** No sync problems. Clear authority. Easy updates.

## Component Architecture

### Personas: Specialized AI Modes

Four personas for different cognitive modes:

**Operator** - Default mode
- Execution coordination
- Risk assessment
- Task routing
- State tracking

**Builder** - Implementation mode
- Scripts and workflows
- Infrastructure building
- Quality reviews
- Executor, not designer

**Strategist** - Analysis mode
- Pattern extraction
- Option generation
- Framework building
- Analysis and synthesis

**Writer** - Communication mode
- Documentation
- Meeting notes
- Clear, concise content
- Direct voice

**Architecture:** Each persona is a YAML specification that shapes AI behavior. Personas can be switched mid-conversation based on work type.

### Principles: Architectural Guidelines

Principles are design patterns codified as YAML specifications.

**Structure:**
```yaml
id: P15
name: Complete Before Claiming
category: quality
priority: critical
purpose: |
  Report accurate progress, never claim completion prematurely.
when_to_apply:
  - Multi-phase projects
  - Any task with multiple deliverables
pattern:
  core_behavior: |
    Track progress with quantitative metrics.
    Test all criteria before marking complete.
examples: [...]
anti_patterns: [...]
```

**Usage:** Reference by ID in conversations ("Apply P15", "Follow P7")

### Prompts: Reusable Workflows

Prompts are markdown files with YAML frontmatter containing executable procedures.

**Structure:**
```markdown
---
title: Planning Prompt
tags: [planning, architecture, system-design]
description: Framework for systematic system building
---

# Planning Framework
[Content...]
```

**Usage:** "Load and apply prompts/planning_prompt.md"

## Data Architecture

### File Format Preferences

**YAML > JSON**
- Easier for AI (less syntax strictness)
- Fewer parsing errors
- More forgiving of human edits

**SQLite for Data**
- Query > browse directories
- Single-file database
- Portable, no server needed

**Markdown for Documentation**
- Human-readable first
- Easy to edit and review
- Version control friendly

**JSONL for Logs**
- Append-only
- One record per line
- Streamable

### Directory Structure

```
workspace/
├── Prompts/          # Reusable procedures
├── Knowledge/        # Long-term reference
│   ├── architectural/
│   ├── technical/
│   └── domain/
├── Personal/         # Personal content
│   ├── Journal/
│   ├── Planning/
│   └── Meetings/
├── Projects/         # Active work
├── Inbox/            # Temporary staging
└── Archive/          # Completed/obsolete
```

**Design Principle:** Flat over deep. Clear over clever.

## Safety Architecture

### Protection System

Critical directories marked with `.protected` file:

```yaml
reason: Contains critical system configurations
created: 2025-11-03
```

**Behavior:**
- Requires explicit confirmation before move/delete
- Shows protection reason
- Applies to directory and subdirectories

### Dry-Run by Default (P7)

All destructive operations support `--dry-run`:
```bash
script.py --delete /path --dry-run  # Shows what would happen
script.py --delete /path            # Actually executes
```

**Architecture:** Build verification before commitment into every workflow.

### Anti-Overwrite (P5)

Never overwrite without confirmation. Auto-version on conflict:

```
document.md
document_v2.md  # Auto-generated if document.md exists
document_v3.md  # Pattern continues
```

**Benefit:** No data loss. Easy rollback. Clear history.

## Quality Architecture

### P15: Complete Before Claiming

Most expensive failure mode: Claiming "done" at 60%.

**Enforcement:**
- Report quantitative progress: "13/23 complete (56%)"
- List remaining work explicitly
- Never say "done" unless ALL criteria met
- Format: "Completed: [list]. Remaining: [list]. Status: X/Y (Z%)."

### Fresh Thread Test (P12)

True test of reproducibility: Can someone else run this in a fresh context?

**Method:**
1. Document all dependencies explicitly
2. Test in new conversation/thread
3. Verify only declared files are needed
4. Fix any hidden dependencies

**Benefit:** Ensures true self-contained-ness.

### State Verification (P18)

After writes, verify state changed as expected:

```python
# Write file
path.write_text(content)

# Verify
assert path.exists(), "File should exist"
assert path.read_text() == content, "Content should match"
```

**Principle:** Don't assume success. Verify.

## Extension Architecture

N5OS Lite is designed to be extended:

### Adding Principles

```yaml
---
id: P50
name: Your Custom Principle
category: your_category
priority: medium
purpose: |
  What problem does this solve?
when_to_apply: [...]
pattern: [...]
examples: [...]
```

Add to `principles/` and reference in workflows.

### Creating Personas

```yaml
---
name: Your Custom Persona
domain: Your specialized domain
purpose: What this persona excels at
core_identity: [...]
capabilities: [...]
when_to_invoke: [...]
```

Add to `personas/` and invoke by name.

### Building Prompts

```markdown
---
title: Your Workflow
tags: [relevant, tags]
description: Brief description
---

# Your Workflow
[Executable procedure...]
```

Add to `Prompts/` and load by path.

## Performance Characteristics

### Time Allocation

**Typical Project:**
- Think: 40% of time
- Plan: 30% of time
- Execute: 10% of time
- Review: 20% of time

**Why:** Quality comes from planning. Execution is mechanical.

### Context Management

**P8: Minimal Context, Maximal Clarity**

Don't load everything. Load only what's needed for precision.

**Trade-off:** More context = slower, more expensive. Minimal context = faster, cheaper.

**Optimization:** Keep prompts/personas self-contained. Reduce dependencies.

## Evolution & Maintenance

### Version Control

All components versioned:
```yaml
version: 1.0.0
created: 2025-11-03
updated: 2025-11-03
```

Track changes in changelog:
```yaml
changelog:
  - date: 2025-11-03
    version: 1.0.0
    changes: Initial release
```

### Regular Review

**Monthly:**
- Review protection markers (remove obsolete)
- Clean up Inbox (enforce flow)
- Archive completed projects

**Quarterly:**
- Review trap door decisions (were they right?)
- Assess principle effectiveness
- Refine personas based on usage

### Continuous Improvement

N5OS Lite is a living system:
- Add principles as patterns emerge
- Create personas for new domains
- Build prompts for recurring workflows
- Document lessons learned

## Anti-Patterns

### Over-Engineering

**Symptom:** More structure than needed  
**Fix:** Start minimal. Add only when pain is clear.

### Rigid Adherence

**Symptom:** Following system even when it doesn't fit  
**Fix:** System should serve you, not constrain you.

### Process Over Outcome

**Symptom:** Focus on following process perfectly  
**Fix:** Process is means, not end. Focus on outcomes.

### Premature Optimization

**Symptom:** Optimizing before understanding problem  
**Fix:** Think→Plan→Execute. Understand before optimizing.

## Success Metrics

How do you know N5OS Lite is working?

1. **Fewer Bugs:** Better planning = fewer implementation bugs
2. **Faster Iteration:** Clear processes = less thrashing
3. **Better Decisions:** Explicit trade-offs = informed choices
4. **Less Rework:** Proper verification = right first time
5. **Clearer Communication:** Shared vocabulary = better alignment

## Future Evolution

N5OS Lite is v1.0. Potential evolutions:

- **More Personas:** For specialized domains
- **Enhanced Principles:** As patterns emerge
- **Better Tooling:** Scripts to support workflows
- **Community Patterns:** Shared principles and personas
- **Integration Guides:** For specific tools/platforms

---

*Architecture is the art of making the right trade-offs explicit.*
