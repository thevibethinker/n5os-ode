# P31: Own The Planning Process

**Category:** Strategy  
**Priority:** Critical  
**Related:** P28 (Plans As Code DNA), P30 (Feel For Code), P27 (Nemawashi)

---

## Principle

**YOU write plans. AI executes plans. Never delegate planning to AI.**

Planning is strategic—it requires judgment, taste, and ownership. AI can assist with research, generate alternatives, and validate approaches, but YOU must own the final plan. The moment you let AI plan your system, you've lost architectural integrity.

---

## The Problem

**Delegating planning to AI:**

**User:** "Build me a command system for N5"

**AI:** Generates 2000 lines across 10 files with architecture you didn't specify

**Result:**
- You don't understand the architecture
- Decisions were made without your input
- System reflects AI's defaults, not your values
- Technical debt from day one
- Lost feel for code immediately

**Cost:** System you don't own, can't maintain, can't evolve.

---

**Owning the planning:**

**User:** Writes specification:
```markdown
## Command System Specification

**Purpose:** Store N5 commands for quick lookup

**Architecture:**
- Single JSONL file: N5/config/commands.jsonl
- Format: {id, name, description, path, tags}
- Operations: add, find, list, update

**Interface:**
- add_command(name, description, path, tags) -> id
- find_command(query, exact=False) -> List[Command]

**Edge cases:**
- Duplicate names → error
- Malformed JSON → skip, log warning
- Missing file → create empty

**Rationale:**
- JSONL: human-readable (P1), simple (P8)
- Single file: <100 commands expected
- Grep-friendly: aligns with Unix philosophy

[... detailed specification ...]
```

**Then:** "Generate code from this specification"

**Result:**
- You own architecture
- Decisions reflect your values
- System is maintainable
- You understand every choice
- Technical quality baked in

**Benefit:** System you own, understand, can evolve.

---

## Recognition

**You own planning when:**
- YOU write the specification
- YOU make trap door decisions
- YOU evaluate trade-offs
- YOU choose architecture
- AI generates code from YOUR plan

**AI owns planning when:**
- AI proposes architecture
- AI makes decisions for you
- You accept defaults without evaluation
- "Just build something" prompts
- You don't understand why things are structured the way they are

**Key indicator:** Can you explain WHY the architecture is designed this way?
- Yes → You own planning
- No → AI owns planning

---

## Application

### Planning Ownership Workflow

```markdown
## Phase 1: YOU Think (Strategic)

**What am I building?**
- [Your answer]

**Why does it matter?**
- [Your rationale]

**What are the alternatives?**
- [Your Nemawashi evaluation]

**What are the trap doors?**
- [Your identified irreversible decisions]

**What trade-offs am I making?**
- [Your explicit trade-off analysis]

---

## Phase 2: YOU Plan (Tactical)

**Specification:**
- [Your detailed spec in prose]

**Architecture:**
- [Your component design]

**Interface:**
- [Your API definition]

**Edge cases:**
- [Your edge case enumeration]

---

## Phase 3: AI Executes (Mechanical)

**Prompt:** "Generate code from this specification: [paste spec]"

**AI role:** Mechanical translation of YOUR plan into code

**Your role:** Review code against YOUR plan

---

## Phase 4: YOU Review (Quality)

**Validation:**
- Does code match my spec?
- Are my edge cases handled?
- Does architecture reflect my decisions?
- Is quality consistent with my standards?
```

---

### AI Assistance (Not Planning)

**AI CAN help with:**

**Research:**
- "What are common patterns for command storage?"
- "Compare JSONL vs SQLite for <100 records"
- "What edge cases exist in JSONL parsing?"

**Validation:**
- "Review my spec for gaps"
- "What edge cases am I missing?"
- "Does this architecture have obvious flaws?"

**Generation:**
- "Generate code from this spec"
- "Implement this interface"
- "Create tests for these requirements"

**AI CANNOT replace:**
- Your values (Simple over Easy)
- Your judgment (trap door decisions)
- Your taste (aesthetic preferences)
- Your vision (what you're building and why)

---

### Bad Prompt (AI Plans)

```
"Build a system to manage N5 commands. Make it good."
```

**Problems:**
- No specification
- No architecture guidance
- No trade-off decisions
- No edge case handling
- AI fills gaps with defaults
- You don't own the result

---

### Good Prompt (You Plan)

```
"Generate code from this specification:

[Detailed spec with]
- Purpose
- Architecture decisions (with rationale)
- Interface definition
- Edge cases enumerated
- Error handling specified
- Tests defined
- Success criteria

Use Python 3.12, type hints, logging, dry-run flag.
"
```

**Benefits:**
- Complete specification
- YOUR architecture decisions
- YOUR trade-offs
- AI executes YOUR plan
- You own the result

---

## Integration with Other Principles

**With P28 (Plans As Code DNA):**
- Plans generate code
- If AI owns plans, AI owns your codebase
- If YOU own plans, YOU own your codebase

**With P30 (Feel For Code):**
- Can't maintain feel if you don't own planning
- Planning creates mental model
- Mental model enables feel

**With P27 (Nemawashi):**
- Nemawashi is YOUR process
- AI can present alternatives
- YOU evaluate and choose

---

## The Strategic Boundary

**Clear separation:**

| Your Responsibility | AI Responsibility |
|---|---|
| What to build | How to implement |
| Why it matters | Code generation |
| Architecture | Execution |
| Trade-offs | Mechanical translation |
| Edge cases | Handling as specified |
| Quality standards | Meeting standards |

**The line:** Strategy vs. execution
**You own:** Above the line
**AI owns:** Below the line

**If AI crosses the line, you've lost control.**

---

## Anti-Patterns

❌ **"Build me a system":** No spec, AI plans for you  
❌ **Accepting AI architecture:** Without evaluation  
❌ **Delegating decisions:** "You choose the data format"  
❌ **"Make it work":** Vague prompts create vague systems  

---

## Verification

**Before generating code:**
- [ ] I wrote the specification
- [ ] I made all trap door decisions
- [ ] I evaluated trade-offs explicitly
- [ ] I defined success criteria
- [ ] I own this architecture
- [ ] I can explain every choice

**If any checkbox fails: STOP. Plan more before executing.**

---

## The Ownership Test

**After AI generates code, ask yourself:**

1. **Why is the system structured this way?**
   - Can you explain the rationale?
   - Or did AI just pick defaults?

2. **What trade-offs were made?**
   - Can you articulate what you gained and lost?
   - Or do you not know?

3. **What would you change if starting over?**
   - Can you identify improvements?
   - Or is it a black box?

**If you can answer these: You own the planning.**
**If you can't: AI owns the planning.**

---

## Cultural Note

**From Ben's talk:**

> "I own the planning process. That's my job. AI's job is execution. I maintain a very strong separation."

**Why this matters:**

**Planning is taste:**
- What is good code?
- What is simple?
- What is maintainable?
- What reflects our values?

**AI has no taste.** AI has patterns.

**Your taste must guide the patterns.**

---

## Practical Workflow

```markdown
## Step 1: Strategic Thinking (YOU)
- What am I building and why?
- What are alternatives?
- What are trap doors?
- Time: 40% of total

## Step 2: Tactical Planning (YOU)
- Write specification
- Define architecture
- Enumerate edge cases
- Time: 30% of total

## Step 3: Execution (AI)
- Generate code from YOUR spec
- Time: 10% of total

## Step 4: Review (YOU)
- Validate against YOUR plan
- Time: 20% of total

Total time split: 90% YOU, 10% AI execution
```

**YOU are the architect. AI is the builder.**

---

## Source

From Ben Guo's velocity coding talk: "Own the planning process. That's where the strategy lives. AI can execute, but YOU must plan."

---

**Created:** 2025-10-26  
**Version:** 1.0
