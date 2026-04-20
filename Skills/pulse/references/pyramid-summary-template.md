---
created: 2026-02-21
last_edited: 2026-02-21
version: 1.0
provenance: con_mG5yzbSSJUnMnZcK
---

# Pyramid Summary Template

Multi-resolution context files for builds. Drops reference their context file instead of inlining large context blocks. Most useful for builds with 5+ Drops.

## Convention

**Location:** `N5/builds/<slug>/context/`

**Files:**
- `overview.md` — Build-level context (what, why, constraints)
- `D<stream>.<seq>-context.md` — Per-Drop context file

## Template: Build Overview

```markdown
# Build Context: <Build Name>

## 2-Word: <two-word summary>

## 8-Word: <eight-word summary that captures the core intent>

## 32-Word:
<A paragraph of roughly 32 words that gives enough context for any
Drop to understand what the build is about, why it exists, and what
the key constraints are.>

## Full Context:
<Complete context including:
- Why this build exists (problem statement)
- Key architectural decisions already made
- Relevant prior art or existing systems
- Constraints and non-negotiables
- How this build fits into the larger system>
```

## Template: Per-Drop Context

```markdown
# Drop Context: D<stream>.<seq> — <Task Name>

## 2-Word: <two-word summary of this Drop>

## 8-Word: <what this specific Drop accomplishes in the build>

## 32-Word:
<Enough context for the worker to understand its role, what comes
before it, what comes after it, and why its particular piece matters.>

## Full Context:
<Everything the Drop needs:
- Build overview (link to overview.md, or inline the 32-word version)
- What upstream Drops produced (if any)
- What downstream Drops expect from this one
- Specific technical context for this Drop's domain>

## Upstream Deposits:
<!-- Summaries from deposits of prerequisite Drops -->
- D<x>.<y>: <summary from deposit>

## Related Drops:
- D<a>.<b>: <how this Drop relates, what to be consistent with>
```

## Usage

### In Drop Briefs

Instead of inlining large context blocks, reference the context file:

```markdown
## Context

See `N5/builds/<slug>/context/D1.1-context.md` for full context.

**32-word summary:** <inline the 32-word version for quick reference>
```

### Resolution Selection

Workers should read the resolution level appropriate to their task:

| Situation | Read |
|-----------|------|
| Quick orientation | 8-Word |
| Understanding scope | 32-Word |
| Full implementation context | Full Context |
| Cross-Drop coordination | Related Drops section |

### When to Generate

- **Architect creates** overview.md during planning
- **Architect creates** per-Drop context files when writing Drop briefs
- **Orchestrator updates** context files when deposits arrive (upstream summaries)
- **Not needed** for builds with <5 Drops — inline context in briefs is fine

## Why Multi-Resolution

Adapted from StrongDM's pyramid summaries pattern. Benefits:

1. **Token efficiency** — Workers load only the resolution they need
2. **Consistency** — All Drops share the same build overview rather than paraphrased versions
3. **Updatable** — When upstream Drops complete, their deposit summaries flow into downstream context
4. **Debuggable** — When a Drop fails, you can check if it had adequate context
