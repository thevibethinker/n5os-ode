---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_CEda9Xg9GGknF2gE
---

# Prompt Engineering Principles

## Source
Derived from Jarrod Watts' approach to AI orchestration
(X post: how to beat Anthropic's kernel challenge with zero kernel knowledge)

## Core Principle: 100x Leverage

Every word in a prompt has **100x leverage** when running agentic loops.

"Vibe coding the prompt was not good enough."

In Pulse builds, a single unclear instruction can cascade through dozens of Drops, each multiplying the ambiguity. What seems like a minor imprecision in a prompt becomes systemic error at scale.

## Anti-Patterns (Never Use)

| Pattern | Problem | Instead |
|---------|---------|---------|
| "try to X" | Permits failure | "X" or "X, or escalate" |
| "if possible" | Permits skipping | "X unless [condition]" |
| "maybe/perhaps" | Ambiguous | Be definitive |
| "improve X" | No target | "improve X by Y%" |
| "consider X" | Permits ignoring | "Apply X to Y" |
| "best effort" | No threshold | Define acceptance criteria |
| "reasonable" | No metric | "within N attempts" |
| "good" | Subjective | Specific quality threshold |
| "as appropriate" | Hand-off responsibility | Explicitly state when/where |
| "etc." | Incomplete | List all items |

## Required Sections in Drop Briefs

Every Drop brief must include these sections:

### 1. Objective
Single sentence, what success looks like.

**Example:**
```
## Objective
Create a CLI tool that detects when Drops are stuck making repeated similar attempts without progress.
```

### 2. Context
Why this matters, what came before, dependencies.

**Example:**
```
## Context
Watts' insight: When stuck, solution isn't more attempts — it's changing the tooling. 
"Giving AI the right tools to identify real optimization opportunities from program trace was extremely helpful."

Plateau signals:
- Repeated similar approaches
- Metrics not improving
- Confidence scores declining
- Same errors recurring
```

### 3. Requirements
Numbered, specific, measurable. No open-ended tasks.

**Example:**
```
## Requirements

### 1. Create Detector Script
Location: `N5/scripts/plateau_detector.py`

### 2. Detection Signals
- Multiple deposits from same Drop with similar content (semantic similarity > 0.8)
- Confidence/quality scores declining or flat across attempts
- "Tried X but failed" patterns repeating

### 3. CLI Interface
Commands: check, analyze, watch
```

### 4. Success Criteria
Checklist of verifiable outcomes. Not "feel good" — testable.

**Example:**
```
## Success Criteria
- [ ] Script created at `N5/scripts/plateau_detector.py`
- [ ] Detects similarity-based plateaus
- [ ] Detects error-repetition plateaus
- [ ] `check_drop_plateau()` function for Pulse Sentinel
- [ ] `--help` documents all commands
```

### 5. Constraints
What NOT to do, boundaries.

**Example:**
```
## Constraints
- Use sentence-transformers for similarity (already installed)
- Log files at `/dev/shm/*.log`
- Don't require running Drop context — work from artifacts only
- Return "no plateau" if insufficient data to judge
```

## Contamination Prevention

When learnings accumulate, they can "contaminate" future Drops with outdated or incorrect beliefs. Watts' system prevents this through:

### 1. Impossibility Audit
Before starting a build, scan all learnings for claims that can't possibly be true.

**Example block:**
```
"Use OAuth token from /tmp/token" — but /tmp/ is cleared on reboot
"Always connect to 10.0.0.5" — but this IP changes in cloud
```

### 2. Confidence & Decay
Every system learning has:
- `confidence`: 0.0-1.0 (starts at 0.7)
- `validated_count`: How many times confirmed
- `last_validated`: Timestamp
- `decay_days`: Days until confidence starts fading (default: 30)

Unvalidated learnings expire. Confirmed ones persist only if re-validated.

### 3. Contradiction Detection
Before adding a new learning, check for contradictions with existing learnings.

**Example:**
```
New: "Use /tmp/cache for downloads"
Existing: "Never use /tmp/ for persistent data"

Contradiction flagged — must resolve before adding.
```

### 4. Fresh Context Injection
System learnings are injected into Drop briefs at spawn time, but Drops can bypass outdated beliefs by:
- Asking for current context explicitly
- Using tools that verify assumptions (filesystem checks, API calls)
- Flagging when assumptions appear wrong

## Plateau Response

When stuck, change tooling — not just retry.

Watts' key insight: The AI "was running into the exact same errors repeatedly" until given tools to "identify real optimization opportunities from program trace."

### Plateau Detection
- Multiple deposits with similar content (semantic similarity > 0.8)
- Same errors recurring without variation
- Confidence scores declining
- Running > 15 minutes without deposit

### Response Pattern

**Don't just:**
```python
retry_same_approach()
```

**Do:**
1. Add instrumentation/logging
2. Try different approach (algorithm, library, method)
3. Expand search space
4. Reframe the problem

**Example:**
```
Old approach: Direct HTTP requests → auth errors
New approach: Use official SDK library with built-in auth handling
```

## Prompt Lint Rules

### High Priority (Blocks spawn)

| Pattern | Issue | Fix |
|---------|-------|-----|
| "try to X" | Ambiguous intent | "X" or "X, or escalate" |
| "if possible" | Permits skipping | "X unless [condition]" |
| "maybe/perhaps" | Uncertainty | Be definitive |
| "improve X" | No target metric | "improve X by Y%" |
| "best effort" | No threshold | Define acceptance criteria |

### Medium Priority (Warnings)

| Pattern | Issue | Fix |
|---------|-------|-----|
| "consider X" | Can be ignored | "Apply X" or "Evaluate X against Y" |
| "reasonable" | Subjective | Use quantitative threshold |
| "etc." | Incomplete | List all items explicitly |

### Structural Requirements

Every Drop brief must have:
- `[x]` Objective section (single sentence success definition)
- `[x]` Context section (why this matters, dependencies)
- `[x]` Requirements section (numbered, specific, measurable)
- `[x]` Success Criteria section (checklist format)
- `[x]` Constraints section (what NOT to do)

## Implementation in N5

### Safety Gates

1. **Pre-Build**: `pre_build_safety_checks()` runs impossibility audit on all learnings
2. **Pre-Spawn**: `prompt_lint.lint_before_spawn()` validates brief quality
3. **Pre-Add**: `contradiction_detector.check_before_adding()` flags contradictions
4. **During Build**: `plateau_detector.check_drop_plateau()` monitors for stuck Drops

### Learnings Management

- Build-local: `N5/builds/<slug>/BUILD_LESSONS.json`
- System-wide: `N5/learnings/SYSTEM_LEARNINGS.json`
- CLI: `pulse_learnings.py` (add, list, validate, dispute, expire-stale)

### Integration Points

All detectors are wired into Pulse:
```python
# Skills/pulse/scripts/pulse.py
- start_build() → pre_build_safety_checks()
- tick() → sentinel_plateau_check()

# Skills/pulse/scripts/pulse_learnings.py
- add_learning() → contradiction_detector.check_before_adding()
```

## Testing Checklist

When using these principles in practice:

- [ ] Brief has clear objective (single sentence)
- [ ] Requirements are numbered and specific
- [ ] Success criteria are testable (checklist)
- [ ] No "try to", "if possible", "maybe"
- [ ] All "etc." replaced with explicit lists
- [ ] All "reasonable", "good" replaced with thresholds
- [ ] Context section explains dependencies
- [ ] Constraints section defines boundaries
- [ ] Brief passes prompt lint (score ≥ 8/10)

## References

- Jarrod Watts X post: https://x.com/i/status/2015599956024021211
- Pulse build system: `Skills/pulse/SKILL.md`
- Detector scripts: `N5/scripts/{impossibility_audit,contradiction_detector,prompt_lint,plateau_detector}.py`
