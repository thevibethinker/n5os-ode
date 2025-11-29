# P28: Plans As Code DNA

**Category:** Strategy  
**Priority:** Critical  
**Related:** P2 (SSOT), P21 (Document Assumptions), P31 (Own Planning)

---

## Principle

**Code quality is determined upstream in plans, not downstream in implementation. Plans are the DNA—code is the expression.**

With AI code generation, your plans and specifications directly generate code. If you care about code quality, care about plan quality. The plan is the source of truth; code is a artifact of the plan.

---

## The Problem

**Old mental model (pre-AI):**
```
Idea → Code → Review → Fix → Ship
        ↑
   Quality happens here
```

**Quality was in the coding:**
- Careful variable naming
- Clean abstractions
- Good comments
- Thoughtful structure

**New mental model (with AI):**
```
Idea → Plan → Generate Code → Review Against Plan → Ship
       ↑
   Quality happens here
```

**Quality is in the planning:**
- Clear specifications
- Explicit trade-offs
- Documented assumptions
- Defined success criteria

**The shift:** Code generation is mechanical. Planning is strategic.

---

## Recognition

**Signs of plan-driven quality:**
- Code matches spec precisely
- Edge cases were anticipated in plan
- Error handling was specified upfront
- Tests validate plan requirements
- Code is clean because plan was clear

**Signs of code-driven quality (old way):**
- "Fix it up during implementation"
- Discovering edge cases while coding
- Refactoring to clean up mess
- Comments explain what code should have been

---

## Application

### High-Quality Plan Example

```markdown
## Specification: Command Lookup Function

**Purpose:** Find N5 command by name or tag

**Input:**
- query: string (command name or tag)
- exact: bool (default False)

**Output:**
- List of matching commands (id, name, description, path)
- Empty list if no matches

**Behavior:**
1. Read N5/config/commands.jsonl
2. Parse each line as JSON
3. If exact=True: match name exactly
4. If exact=False: match name or any tag (case-insensitive)
5. Return all matches

**Edge cases:**
- Empty file → return []
- Malformed JSON → log warning, skip line, continue
- No matches → return []
- Multiple matches → return all
- Query is empty string → return []

**Error handling:**
- File not found → raise FileNotFoundError with helpful message
- Permission denied → raise PermissionError
- Invalid JSON → log warning, skip line

**Tests:**
- find_command("build", exact=False) → returns build-related commands
- find_command("nonexistent") → returns []
- find_command("") → returns []
- Malformed JSONL → skips bad lines, returns valid

**Success criteria:**
- All tests pass
- Handles edge cases gracefully
- Error messages are actionable
- Performance <100ms for <100 commands
```

**From this plan, AI generates:**
- Clean, correct implementation
- Proper error handling
- Comprehensive tests
- Good error messages

**Why? Because the plan specified everything.**

---

### Low-Quality Plan Example

```markdown
## Make a command finder

Should search commands by name.

Returns the command if found.
```

**From this plan, AI generates:**
- Unclear interface (what's input format?)
- No edge case handling (what if file missing?)
- No error handling (what if malformed JSON?)
- No tests (what are requirements?)

**Why? Because the plan was vague.**

---

### The Planning Prompt Effect

**Ben's insight:** His entire codebase inherits quality from his planning prompt.

**Planning prompt contains:**
- Design values (Simple Made Easy, Zero-Touch)
- Thinking modes (Nemawashi, Think→Plan→Execute)
- Quality standards (tests, types, error handling)
- Aesthetic preferences (code style, patterns)

**Result:** Every spec written under this planning prompt inherits these values.

**Code quality is a TRANSITIVE property:**
```
Planning Prompt → Plan → Code

If planning prompt is high quality, and
Plan follows planning prompt, then
Code inherits quality automatically.
```

---

## Integration with Think → Plan → Execute

**Think phase (40%):**
- Define what quality means for this component
- Identify edge cases
- Determine error handling strategy
- Establish success criteria

**Plan phase (30%):**
- Write specification with quality requirements
- Document assumptions explicitly
- Define test cases
- Specify error messages

**Execute phase (10%):**
- Generate code from plan (mechanical)
- Code quality is emergent from plan quality

**Review phase (20%):**
- Validate code against plan
- If code is low quality, likely the plan was unclear
- Fix: improve plan, regenerate code

---

## The DNA Metaphor

**Biological DNA:**
- Encodes instructions for organism
- Cells express DNA into proteins
- Organism quality depends on DNA quality
- Fixing DNA fixes all cells that express it

**Planning Prompt as DNA:**
- Encodes values and standards
- Plans express values into specifications
- Code expresses specifications into implementation
- Fixing planning prompt improves all downstream code

**Implication:** Focus upstream. DNA-level changes cascade downstream automatically.

---

## Practical Workflow

### Writing Plans for AI

**Template:**
```markdown
## [Component Name]

**Purpose:** [One-sentence goal]

**Interface:**
- Input: [Types, constraints]
- Output: [Types, format]

**Behavior:**
1. [Step 1]
2. [Step 2]
...

**Edge cases:**
- [Case 1] → [Behavior]
- [Case 2] → [Behavior]

**Error handling:**
- [Error type] → [Response]

**Tests:**
- [Test case 1]
- [Test case 2]

**Success criteria:**
- [Criterion 1]
- [Criterion 2]

**Assumptions:**
- [Assumption 1]
- [Assumption 2]
```

**This template ensures:**
- Clear specification
- Complete edge case handling
- Defined error behavior
- Testable requirements
- Documented assumptions

**From good plan → good code automatically.**

---

## Anti-Patterns

❌ **Fixing quality in code review:** Too late—fix the plan  
❌ **Vague specifications:** "Make it work" generates messy code  
❌ **Undocumented edge cases:** AI doesn't infer—you must specify  
❌ **"Fix it during implementation":** Old mindset, wastes time  

---

## Verification

**Before generating code:**
- [ ] Plan specifies all inputs/outputs
- [ ] Edge cases identified and handled
- [ ] Error handling defined
- [ ] Tests specified
- [ ] Success criteria clear
- [ ] Assumptions documented

**After generating code:**
- [ ] Code matches plan precisely
- [ ] All specified behaviors implemented
- [ ] Edge cases handled as planned
- [ ] Tests validate plan requirements

**If code is low quality, ask:**
- Was the plan unclear?
- Were edge cases unspecified?
- Were assumptions undocumented?
- **Fix plan, regenerate code.**

---

## Strategic Implications

**What this means:**

1. **Spend more time planning:** 70% think+plan vs. 10% execute
2. **Planning skill is primary:** Code writing is secondary
3. **Quality is upstream:** Fix DNA, not cells
4. **Review plans, not code:** (or review code *against* plan)
5. **Planning prompt is sacred:** It's the DNA of your entire system

**What this doesn't mean:**

1. **Code doesn't matter:** It's just that plan matters MORE
2. **Skip code review:** Still verify against plan
3. **AI is perfect:** It needs good plans to generate good code
4. **No implementation skill:** You need to know what good code looks like to plan for it

---

## The Meta-Insight

**Ben's revelation:**

> "All your code is generated from your planning prompt and your plans. If you care about code quality, care about it at the prompt level."

**This is the MOST IMPORTANT principle in velocity coding.**

Code is downstream. Plans are upstream. Quality flows downstream from source.

**Focus on the source.**

---

## Source

From Ben Guo's velocity coding talk: "All code is generated from your planning prompt and your plans. Care about quality at the prompt level, not the code level."

---

**Created:** 2025-10-26  
**Version:** 1.0
