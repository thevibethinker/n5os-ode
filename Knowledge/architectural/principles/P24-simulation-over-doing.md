# P24: Simulation Over Doing

**Category:** Strategy  
**Priority:** High  
**Related:** P7 (Dry-Run), P23 (Trap Doors), P27 (Nemawashi)

---

## Principle

**Model, prototype, and test ideas in prose or throwaway code before building production systems.**

Simulation is faster and cheaper than doing. Write specifications, sketch architectures, prototype in disposable code, explore alternatives. Commit to implementation only after simulation reveals the right path.

---

## The Problem

**Doing-first mindset:**
- Start coding immediately
- Discover problems 60% through implementation
- Realize architecture is wrong
- Sunk cost fallacy keeps you going
- Ship something you know is flawed

**Cost:** Wasted time, technical debt, poor architecture.

**Simulation-first mindset:**
- Write spec in prose (15 minutes)
- Realize approach has flaw
- Revise spec (5 minutes)
- Now implementation is straightforward
- Ship something clean

**Benefit:** 20 minutes of thinking saves 4 hours of coding.

---

## Recognition

**When to simulate:**
- Building new system component
- Refactoring existing system
- Making trap door decisions
- Uncertain about approach
- Multiple viable alternatives exist

**Simulation techniques:**
1. **Prose specifications** - Write how it works in English
2. **Architecture diagrams** - Sketch component interactions
3. **Throwaway prototypes** - Spike 2-3 approaches, delete all
4. **Mental models** - Walk through scenarios in your head
5. **Toy examples** - Test concept with minimal data

---

## Application

### Think Phase Simulation

**Before writing any production code:**

```markdown
## Specification: Command Registry System

**Goal:** Store N5 commands in JSONL for quick lookup

**How it works:**
1. Commands stored as {id, name, description, path, tags}
2. Single file: N5/config/commands.jsonl
3. Add command: append line to file
4. Find command: grep by name or tag
5. Update: read all → filter → rewrite (rare operation)

**Edge cases:**
- Duplicate names → Check before append
- Corrupt JSONL → Validate on read, fail gracefully
- Empty file → Initialize with []

**Trap doors:**
- JSONL format (could use SQLite, but aligns with P1/P8)
- Single file (could shard, but unnecessary at <100 commands)

**Alternatives considered:**
1. SQLite - More complex, unnecessary for <100 records
2. Directory of files - Overcomplicated, harder to grep
3. JSONL - Simple, human-readable, grep-friendly ✓

**Decision:** JSONL, single file, validation on read
```

**This took 15 minutes. It revealed:**
- Duplicate name handling needed
- Validation strategy required
- Format choice was a trap door
- Alternatives were overengineered

**Now execution is trivial—the thinking is done.**

---

### Prototype Simulation

**When uncertain about implementation:**

```python
# THROWAWAY PROTOTYPE - Testing JSONL vs SQLite performance
# Will delete after 30 minutes

import json
import time

# Simulate 100 commands
commands = [{"id": i, "name": f"cmd_{i}"} for i in range(100)]

# Test JSONL write speed
start = time.time()
with open("/tmp/test.jsonl", "w") as f:
    for cmd in commands:
        f.write(json.dumps(cmd) + "\n")
print(f"JSONL write: {time.time() - start:.4f}s")

# Test grep search speed
start = time.time()
import subprocess
result = subprocess.run(["grep", "cmd_42", "/tmp/test.jsonl"], capture_output=True)
print(f"Grep search: {time.time() - start:.4f}s")

# Conclusion: JSONL is <1ms for both operations at 100 records
# SQLite would be overkill. Ship JSONL.
```

**This prototype took 10 minutes. It answered:**
- Is JSONL fast enough? (Yes, <1ms)
- Do we need a database? (No, unnecessary complexity)
- Can grep handle it? (Yes, instant)

**Now we know: JSONL is the right choice.**

---

## Integration with Think → Plan → Execute

**Think phase (40% of time):**
- Simulate in prose (specifications)
- Simulate in diagrams (architecture sketches)
- Simulate in mental models (scenario walkthroughs)

**Plan phase (30% of time):**
- Refine simulation into actionable spec
- Prototype if uncertain
- Finalize approach

**Execute phase (10% of time):**
- Generate production code from refined plan
- Simulation already solved hard problems

**Review phase (20% of time):**
- Validate against original simulation
- Check if reality matched model

---

## Anti-Patterns

❌ **Skipping simulation:** "I know what to build" (you don't)  
❌ **Prototyping in production:** Throwaway code must be thrown away  
❌ **Over-simulating:** Simulation paralysis (diminishing returns after 30min)  
❌ **Confusing simulation with planning:** Simulation explores; planning commits  

---

## Tools

**Prose simulation:**
- Markdown specifications
- Architecture diagrams (D2, mermaid)
- Scenario walkthroughs

**Code simulation:**
- `/tmp` for throwaway prototypes
- `--dry-run` flags for testing
- Jupyter notebooks for exploration

**Mental simulation:**
- "What if..." questioning
- Edge case enumeration
- Failure mode brainstorming

---

## Verification

**Before executing:**
- [ ] Wrote specification in prose
- [ ] Sketched architecture if multi-component
- [ ] Prototyped if uncertain about approach
- [ ] Explored 2-3 alternatives
- [ ] Validated approach solves the problem

---

## Source

From Ben Guo's velocity coding talk: "Simulation is better than doing. Try things, throw them away. Code is free now."

---

**Created:** 2025-10-26  
**Version:** 1.0
