# P30: Maintain Feel For Code

**Category:** Quality  
**Priority:** High  
**Related:** P15 (Complete Before Claiming), P28 (Plans As Code DNA), P31 (Own Planning)

---

## Principle

**Stay connected to the shape, quality, and craft of generated code. Understanding must match output volume.**

AI can generate code faster than you can understand it. This is dangerous. Maintain "feel" by reading generated code, understanding architecture, and validating quality. If you're generating thousands of lines without mental exhaustion, you've lost connection.

---

## The Problem

**The velocity trap:**
```
Day 1: Generate 1,000 lines
[truncated]
- You rely on AI to tell you what's in the codebase
- You can't explain architecture to someone else
- You discover "features" you didn't know existed
- Code review feels like reading a stranger's code

---

## Application

### Reading Generated Code

**Don't just accept—understand:**

```python
# AI generated this function
def process_records(records: List[Dict]) -> List[Dict]:
    return [
        {**r, 'processed': True, 'timestamp': time.time()}
        for r in records
        if r.get('valid', False)
    ]
```

**Your internal dialogue:**
- "It's filtering for valid records" (understand logic)
- "Adding processed flag and timestamp" (understand additions)
- "Using dict unpacking" (recognize pattern)
- "List comprehension for efficiency" (understand choice)

**If you can't explain it, don't ship it.**

---

### Architecture Awareness

**After generating multi-file system:**

```markdown
## Architecture Check (Self-Quiz)

1. What are the main components?
   - [Can you list them?]

2. How do components interact?
   - [Can you draw the flow?]

3. Where is the single source of truth?
   - [Can you point to it?]

4. What are the edge cases?
   - [Can you enumerate them?]

5. What would break if X fails?
   - [Can you predict failure modes?]

If you can't answer these: STOP. Read code until you can.
```

---

### The Fatigue Test

**Ben's insight:** "You should feel tired."

**Why?**
- Understanding code takes mental effort
- If you're not tired, you're not understanding
- AI removes typing effort, not comprehension effort
- Velocity coding is mentally exhausting (as it should be)

**Self-check:**
```
Generated 2,000 lines today
Feeling: [ ] Energized [ ] Neutral [X] Mentally exhausted

If NOT exhausted:
- Am I actually understanding this code?
- Or just accepting AI output blindly?
```

---

### Maintaining Craft

**Code quality indicators you should feel:**

**Good code feels:**
- Clear and obvious
- Minimal and elegant
- Well-structured
- Consistent in style
- Self-explanatory

**Bad code feels:**
- Confusing or clever
- Bloated or repetitive
- Tangled dependencies
- Inconsistent patterns
- Needs explaining

**If you can't FEEL the difference, you've lost connection.**

---

## Integration with Other Principles

**With P28 (Plans As Code DNA):**
- Plans define quality upstream
- Feel validates quality downstream
- Both required: plan well, verify well

**With P31 (Own Planning):**
- You must own planning (strategic)
- You must maintain feel (tactical)
- AI handles middle (execution)

**With P15 (Complete Before Claiming):**
- Can't claim complete without understanding
- Understanding requires feel
- Feel comes from reading code

---

## Techniques for Maintaining Feel

### 1. Always Read Generated Code

**Don't just run it—understand it:**
- Read every generated function
- Trace execution flow mentally
- Identify edge cases
- Spot potential bugs
- Validate against spec

**Time cost:** ~30% of generation time
**Benefit:** Understanding, quality, confidence

---

### 2. Sketch Architecture

**After generating multi-component system:**
```
# Draw on paper or whiteboard
[Component A] --> [Component B]
       ↓              ↓
   [Database]    [API]
```

**Can you draw it from memory?**
- Yes → You have feel
- No → Read more code

---

### 3. Explain to Rubber Duck

**Teach the code to an imaginary audience:**
- "This system has three components..."
- "Data flows from X to Y because..."
- "Edge cases are handled by..."

**If you can teach it, you understand it.**

---

### 4. Review Session Ritual

**At end of coding session:**
```markdown
## Session Review: [Date]

**Generated today:**
- [Component 1] - [What it does]
- [Component 2] - [What it does]

**Architecture changes:**
- [What changed in system design]

**Edge cases added:**
- [New edge cases handled]

**Still don't understand:**
- [Gaps in understanding - MUST resolve tomorrow]

**Tomorrow's focus:**
- [Based on today's learning]
```

---

## The Craft Element

**Why "feel" matters:**

**Software is a craft:**
- There's good and bad
- Quality is tangible
- Aesthetics matter
- Feel develops with practice

**AI can generate, but:**
- YOU determine good vs. bad
- YOU maintain quality standards
- YOU preserve architectural integrity
- YOU are the craftsperson

**Feel is your craft sense.**

---

## Warning Signs

**You've lost feel when:**

1. **Can't explain what code does** without reading it line-by-line
2. **Don't know what files exist** in your codebase
3. **Surprised by behavior** that code "should" have
4. **Can't predict where bug is** from symptom description
5. **Need AI to tell you** what your own code does

**Recovery:**
- Stop generating
- Read existing code
- Sketch architecture
- Refactor for clarity
- Rebuild mental model

---

## Anti-Patterns

❌ **"Just ship it":** Accepting without understanding  
❌ **Generate and forget:** No review process  
❌ **Relying on AI for your code understanding:** AI is assistant, not memory  
❌ **No mental fatigue:** Sign of shallow engagement  

---

## Verification

**After each code generation session:**
- [ ] Read all generated code
- [ ] Can explain what each part does
- [ ] Can draw architecture from memory
- [ ] Understand edge cases
- [ ] Know what would break if X fails
- [ ] Feel mentally engaged (tired from thinking)

**If any checkbox fails: STOP and recover feel before continuing.**

---

## The Balance

**Too much feel:**
- Writing code manually
- Rejecting AI help
- Slow progress

**Too little feel:**
- Blind acceptance
- Lost architecture
- Technical debt accumulation

**Right balance:**
- AI generates (fast execution)
- You understand (maintained feel)
- Quality preserved
- Velocity sustained

---

## Source

From Ben Guo's velocity coding talk: "It's easy to lose feel for your code. Read what you generate. Understand architecture. You should feel tired—if you're not, you're not understanding."

---

**Created:** 2025-10-26  
**Version:** 1.0
