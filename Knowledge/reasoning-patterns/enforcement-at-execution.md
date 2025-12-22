---
created: 2025-12-14
last_edited: 2025-12-14
version: 1.0
pattern_type: architectural
source: planning-system-v1 build, Level Upper analysis
---

# Pattern: Enforcement at Execution, Not Routing

## Summary

When you want behavior X to be mandatory, don't enforce at the routing/dispatch layer—enforce at the execution layer where the work actually happens.

## The Insight

Routing rules can be bypassed, forgotten, or misapplied. The executor (the thing that does the work) is the most reliable enforcement point because it's the last checkpoint before action.

## Application

**Problem:** We wanted mandatory planning before major builds.

**Weak approach:** Add routing rules saying "Operator must route to Architect first."
- Routing rules can be forgotten
- Operator might misjudge what's "major"
- No mechanical enforcement

**Strong approach:** Builder refuses to execute major work without a plan file.
- Enforcement at the point of execution
- Mechanical check (file exists or doesn't)
- Can't be bypassed by routing mistakes

## General Form

```
Instead of:
  Dispatcher → "Must route to X before Y"
  
Prefer:
  Executor → "Refuses to proceed without prerequisite"
```

## When to Apply

Use this pattern when:
- A prerequisite is genuinely important
- The routing layer is complex or has many paths
- You want mechanical (not just procedural) enforcement
- The prerequisite can be checked objectively (file exists, test passes, etc.)

## Trade-offs

**Pros:**
- Robust - can't be bypassed by routing mistakes
- Clear error messages at point of failure
- Self-documenting (executor states what it needs)

**Cons:**
- Less flexibility for edge cases
- Requires executor to have prerequisite-checking logic
- May need escape hatches for urgent work (which should be logged)

## Related

- "Fail fast" principle
- Pre-condition assertions in code
- Builder pattern in persona system

