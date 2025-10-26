# P29: Focus Plus Parallel

**Category:** Operations  
**Priority:** Medium  
**Related:** P26 (Fast Feedback), P20 (Modular Components)

---

## Principle

**Maintain one primary focus while running one auxiliary process in parallel. Strategic parallelism, not chaotic multitasking.**

Human attention works best with singular focus. AI can handle parallel tasks. The optimal workflow: YOU focus on one thing, AI handles one supporting task. Not zero parallelism (too slow), not five things (too chaotic). One + one.

---

## The Problem

**Too little parallelism (serial workflow):**
```
1. Write code
2. Wait (nothing happening)
3. Test code
4. Wait (nothing happening)
5. Deploy code
6. Wait (nothing happening)

Total time: 60 minutes
```

**Too much parallelism (chaos):**
```
1. Write code for feature A
2. Start test run for feature B
3. Check deploy status of feature C
4. Debug error from feature D
5. Review AI output for feature E

Result: Context switching destroys flow
Total time: 90 minutes (slower due to overhead!)
```

**Optimal parallelism (focus + one):**
```
1. Write code for feature A (focused)
2. While testing: have AI research approach for feature B (parallel)
3. Review AI research, make decision
4. While deploying A: have AI generate code for B (parallel)

Result: Maintained focus, utilized wait time
Total time: 30 minutes
```

---

## Recognition

**Good parallelism patterns:**
- **Focus:** Writing specification **Parallel:** AI generating code from previous spec
- **Focus:** Testing locally **Parallel:** AI researching library options
- **Focus:** Code review **Parallel:** AI running test suite
- **Focus:** Debugging issue **Parallel:** AI generating documentation

**Bad parallelism patterns:**
- Five AI conversations open at once
- Switching between unrelated tasks
- Starting new work while previous work unfinished
- Parallel work that requires your attention

**Key distinction:** Parallel work should NOT require focus. It's background work that completes while you focus elsewhere.

---

## Application

### Example: Building New N5 Command

**Serial approach (slow):**
```
1. Write specification (15 min)
2. Generate code manually (30 min)
3. Test code (10 min)
4. Write documentation (15 min)

Total: 70 minutes
```

**Focus + parallel approach (fast):**
```
1. Write specification (15 min)
   PARALLEL: Have AI generate code outline from spec
   
2. Review AI code, refine (10 min)
   PARALLEL: Have AI generate tests from spec
   
3. Run tests, fix bugs (10 min)
   PARALLEL: Have AI generate documentation from spec
   
4. Review documentation, ship (5 min)

Total: 40 minutes
```

**Time saved: 30 minutes (43% faster)**

**Why it works:**
- Your focus never splits
- AI utilizes wait time
- Each parallel task completes before next focus shift

---

### Workflow Template

```markdown
## Focus + Parallel Pattern

**Current focus:** [What I'm actively working on]
**Parallel task:** [What AI is working on in background]

**When focus task completes:**
1. Review parallel task output
2. Make decision based on review
3. Start next focus task
4. Assign new parallel task

**Rules:**
- Only ONE focus task at a time
- Only ONE parallel task at a time
- Parallel task must not require attention
- Switch only when current focus completes
```

---

### Practical Examples

**Example 1: Research + Implementation**
```
FOCUS: Implementing command lookup function
PARALLEL: AI researching best practices for JSONL parsing

When implementation reaches "how to parse JSONL?":
- Review AI research
- Apply learning
- Continue implementation
```

**Example 2: Testing + Documentation**
```
FOCUS: Running test suite and fixing bugs
PARALLEL: AI generating user documentation from code

When tests pass:
- Review generated docs
- Refine and approve
- Ship code + docs together
```

**Example 3: Deploy + Next Feature**
```
FOCUS: Deploying current feature to production
PARALLEL: AI generating specification for next feature

When deploy completes:
- Review next feature spec
- Approve or refine
- Begin implementation
```

---

## Integration with Other Principles

**With P26 (Fast Feedback):**
- Parallel work fills wait time in feedback loops
- Maintains flow during slow operations
- Example: While deploy runs (slow), AI prepares next task

**With P20 (Modular Components):**
- Modularity enables safe parallelism
- Independent components can be worked on in parallel
- Example: While testing module A, AI generates module B

**With P31 (Own Planning):**
- YOU plan (cannot be parallelized)
- AI executes plan (can be parallelized)
- Strategic separation of focus vs. background

---

## Anti-Patterns

❌ **Five parallel AI conversations:** Too much chaos  
❌ **Parallel work requires attention:** Defeats the purpose  
❌ **Starting new work before finishing current:** Fragmentation  
❌ **Zero parallelism:** Missing efficiency opportunities  

---

## Tool Support

**AI parallel work:**
- Long-running AI tasks (research, code generation)
- Background processing (test runs, deployments)
- Supporting work (documentation, analysis)

**Your focus work:**
- Strategic decisions
- Plan writing
- Code review
- Problem-solving

**The split:**
- YOU: High-judgment, focus-required work
- AI: Mechanical, background-compatible work

---

## Context Switching Cost

**Research shows:**
- Context switch cost: 10-20 minutes to regain focus
- Flow state requires 15-20 minutes of uninterrupted focus
- Multitasking reduces productivity by 40%

**Focus + parallel avoids this:**
- Maintains singular focus (no switching)
- Utilizes background capacity (parallel work)
- No cognitive overhead (parallel doesn't demand attention)

---

## Verification

**Before starting parallel work:**
- [ ] Is my primary focus clear and singular?
- [ ] Does parallel task truly not require my attention?
- [ ] Will parallel task complete before I need its output?
- [ ] Am I only running ONE parallel task (not five)?

**Quality check:**
- Am I switching contexts frequently? (Bad sign)
- Can I describe my current focus in one sentence? (Good sign)
- Am I waiting with nothing happening? (Missing parallel opportunity)
- Am I overwhelmed by parallel tasks? (Too much parallelism)

---

## The "One Weird Trick"

**Ben's insight:** This is the "whole secret" of velocity coding.

Not about working on five things at once.
Not about serial execution of everything.

**It's about:**
- Singular focus (flow state)
- Strategic parallelism (efficiency)
- Not zero (too slow)
- Not five (too chaotic)
- **One + one = optimal**

---

## Practical Workflow

```bash
# Example: Using Zo for focus + parallel

# Terminal 1 (YOUR FOCUS)
vim N5/scripts/new_command.py
# You are writing code, in flow

# Terminal 2 (PARALLEL WORK)
# Have AI generate tests in background
# When your focus completes, review AI output

# NOT: Terminal 1, 2, 3, 4, 5 all with different tasks
# NOT: Switching between terminals constantly
# YES: One focus + one parallel
```

---

## Source

From Ben Guo's velocity coding talk: "The one weird trick—not working on five things, not serial, but one primary focus with one parallel task. That's the whole secret."

---

**Created:** 2025-10-26  
**Version:** 1.0
