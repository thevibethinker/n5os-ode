---
created: 2026-02-18
last_edited: 2026-02-18
version: 1.0
provenance: n5os-ode
---

# Root Cause Tracing — Backward Tracing Technique

## Overview

Backward tracing is the most reliable technique for finding root causes. Instead of guessing forward ("what could cause this?"), you start at the failure and systematically trace backward through the execution path until you reach the origin of the problem.

## The Technique

### Step 1: Start at the Error

Identify the exact point of failure:
- The specific line where the exception is thrown
- The exact assertion that fails
- The precise moment behavior diverges from expectation

Record the **actual value** at this point — what is it, and what should it be?

### Step 2: Ask Three Questions

At each level of the trace, answer:

1. **What was the input?** — What value, state, or data arrived at this point? Is it what you expected?
2. **Who called this?** — What function, handler, or process invoked this code? Trace the call stack.
3. **Where did the bad value originate?** — If the input is wrong, where was it produced? Go to that location and repeat.

### Step 3: Trace Backward

Move one level up the call chain and repeat Step 2. Keep going until you find the point where:
- A correct value was transformed into an incorrect one, OR
- An incorrect assumption was encoded, OR
- An external input arrived in an unexpected format, OR
- A dependency returned something unexpected

This is your root cause location.

### Step 4: Verify the Origin

Once you think you have found the origin:
- Confirm by checking: if you fix the value at this point, does the downstream error disappear?
- Check if other code paths also consume this origin — they may have latent bugs too.

## Example Trace

```
ERROR: TypeError: Cannot read property 'name' of undefined (line 45, render.js)
  ↑ `user` is undefined at line 45
  ↑ `user` comes from `getUser()` return value at line 38
  ↑ `getUser()` returns `results[0]` from database query at line 22
  ↑ Database query returns empty array (0 results) at line 18
  ↑ Query uses `userId` parameter which is "undefined" (string) at line 15
  ↑ `userId` parsed from URL params — URL has no `id` parameter
  
ROOT CAUSE: Missing URL parameter validation at route level (line 10)
```

## Common Tracing Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Stopping too early | You found *where* it breaks but not *why* | Keep tracing until you find the origin, not just the symptom |
| Assuming the call stack is complete | Async operations, event handlers, and callbacks can hide intermediate steps | Check for async boundaries and trace through them |
| Ignoring side effects | State mutations elsewhere may have corrupted the value before it reached this point | Check if any concurrent or prior operations modify the same state |
| Trusting type annotations | The declared type may not match the runtime value | Log or inspect actual values, do not rely on type declarations alone |

## When to Use Backward Tracing

- **Always** when you have a clear error or stack trace
- **Always** when the failure point is known but the cause is not
- **Especially** when the error message does not directly indicate the root cause (e.g., "undefined is not a function" — the real question is *why* is it undefined?)
