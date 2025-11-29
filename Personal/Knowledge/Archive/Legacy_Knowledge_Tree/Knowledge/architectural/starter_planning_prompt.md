# Starter Planning Prompt

**Purpose:** Foundation for thinking about system design before writing code

---

## Core Philosophy

**Think → Plan → Execute**

Most coding time should be spent *thinking* and *planning*, not writing code. Code is cheap. Thinking is expensive. Get the design right before you type.

**Time Distribution:**
- 40% Think (explore the problem space)
- 30% Plan (write the specification)
- 10% Execute (generate the code)
- 20% Review (test and verify)

---

## Key Questions Before Building

### Think Phase
1. **What am I building?** (one sentence)
2. **Why does this need to exist?** (what problem does it solve?)
3. **What are the trap doors?** (irreversible decisions I'm making)
4. **Have I explored alternatives?** (Nemawashi: consider 2-3 approaches)

### Plan Phase
5. **What's the simplest version?** (what can I cut?)
6. **What are the handoffs?** (where does data enter/exit?)
7. **How will I verify it works?** (what does success look like?)

---

## Design Values

**Simple Over Easy:** Choose systems with few intertwined concepts, even if they take more lines of code. Simplicity is about *disentanglement*, not brevity.

**Maintenance Over Organization:** Systems should flow like a river (data in, transform, data out), not pool like a lake (centralized databases, queues). Flow is self-cleaning.

**Code Is Free, Thinking Is Expensive:** 100 lines of clear code costs nothing. 10 lines of clever code costs hours of debugging. Write clear code.

---

## Application

Before any significant build:
1. Load this prompt
2. Answer the 7 questions above
3. Write a prose specification (not code)
4. Get feedback on the plan
5. Only then: write code

**Remember:** The code you don't write is the code you don't have to maintain.

---

**Adapted from:** N5 Planning Prompt (full version)
