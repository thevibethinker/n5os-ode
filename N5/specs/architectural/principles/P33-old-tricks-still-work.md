# P33: Old Tricks Still Work

**Category:** Quality  
**Priority:** Medium  
**Related:** P19 (Error Handling), P26 (Fast Feedback), P18 (Verify State)

---

## Principle

**Time-tested software engineering practices remain essential with AI coding. Tests, types, linting, refactoring, simplicity—all still critical.**

AI changes *how* we write code (faster generation), not *what* makes code good (tests, clarity, maintainability). Don't skip fundamentals just because AI can generate fast. Quality practices are more important than ever.

---

## The Problem

**The AI trap:**

"AI can generate code so fast! Do I still need tests?"  
"AI writes working code, why refactor?"  
"AI handles complexity, why keep it simple?"

**Answer: YES. More than ever.**

**Why:**
- AI generates code faster → Technical debt accumulates faster
- More code written → More code to maintain
- Less manual typing → Less time to think during writing
- Faster iteration → Easier to skip quality steps

**Paradox:** AI makes quality practices MORE important, not less.

---

## Recognition

**"Old tricks" that still work:**

1. **Tests** - Validate behavior, catch regressions
2. **Types** - Document interfaces, catch errors early
3. **Linting** - Enforce consistency, catch code smells
4. **Refactoring** - Simplify, clarify, reduce complexity
5. **Simplicity** - Prefer simple over clever
6. **Code review** - Human judgment on quality
7. **Documentation** - Explain intent, not just behavior

**These aren't "old-fashioned"—they're foundational.**

---

## Application

### 1. Tests (Still Critical)

**Even with AI:**

```python
# AI generated this function
def calculate_discount(price: float, code: str) -> float:
    if code == "SAVE10":
        return price * 0.9
    elif code == "SAVE20":
        return price * 0.8
    return price

# You still need tests
def test_calculate_discount():
    assert calculate_discount(100, "SAVE10") == 90
    assert calculate_discount(100, "SAVE20") == 80
    assert calculate_discount(100, "INVALID") == 100
    assert calculate_discount(0, "SAVE10") == 0
    # Edge case: negative price?
    assert calculate_discount(-100, "SAVE10") == -90  # Is this right?
```

**Why tests matter with AI:**
- AI might generate logical code with wrong behavior
- Tests validate YOUR specifications
- Regression prevention when regenerating
- Documentation of expected behavior

---

### 2. Types (Still Valuable)

**Even with AI:**

```python
# Without types (error-prone)
def process_record(record):
    return record["data"]

# With types (self-documenting)
def process_record(record: Dict[str, Any]) -> Dict[str, str]:
    return record["data"]
```

**Why types matter with AI:**
- AI understands types better (improves generation)
- Types catch errors before runtime
- Self-documentation of interfaces
- Refactoring safety

**AI actually generates BETTER code when given type hints.**

---

### 3. Linting (Still Useful)

**Even with AI:**

```bash
# Run linters on AI-generated code
python3 -m pylint script.py
python3 -m mypy script.py
python3 -m black script.py --check
```

**Why linting matters with AI:**
- AI generates working code, not always clean code
- Enforces consistency across codebase
- Catches code smells
- Maintains style standards

---

### 4. Refactoring (Still Essential)

**Even with AI:**

**AI generated 300-line function:**
```python
def process_everything(data):
    # ... 300 lines of intertwined logic
    pass
```

**You should refactor:**
```python
def process_everything(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    enriched = enrich_data(transformed)
    return save_data(enriched)

# Four clear functions, each <50 lines
```

**Why refactoring matters with AI:**
- AI doesn't know your desired abstractions
- Generated code often needs restructuring
- Simplicity requires human judgment
- Maintainability comes from refactoring

**With P25 (Code Is Free):** Refactor fearlessly, AI can regenerate.

---

### 5. Simplicity (Still King)

**Even with AI:**

**AI might generate:**
```python
# Complex, clever, "efficient"
return reduce(lambda acc, x: acc + [x] if x not in acc else acc, lst, [])
```

**You should prefer:**
```python
# Simple, clear, maintainable
seen = set()
result = []
for item in lst:
    if item not in seen:
        seen.add(item)
        result.append(item)
return result
```

**Why simplicity matters with AI:**
- AI optimizes for working, not simple
- Simplicity is human judgment (P32)
- Maintainability > cleverness
- Future you (and AI) understands simple better

---

### 6. Code Review (Still Needed)

**Even with AI:**

```markdown
## Code Review Checklist

- [ ] Does code match specification?
- [ ] Are edge cases handled?
- [ ] Is error handling adequate?
- [ ] Are tests comprehensive?
- [ ] Is it simple (not clever)?
- [ ] Is it maintainable?
- [ ] Would I want to debug this?
```

**Why code review matters with AI:**
- AI has no taste (you do)
- Quality judgment is human
- Architecture validation
- Learning from reviewing

---

### 7. Documentation (Still Important)

**Even with AI:**

```python
# AI might generate this
def process(data):
    return [x for x in data if x > 0]

# You should add this
def process(data: List[float]) -> List[float]:
    """Filter positive values from input data.
    
    Args:
        data: List of numeric values
        
    Returns:
        List containing only positive values
        
    Example:
        >>> process([1, -2, 3, -4])
        [1, 3]
    """
    return [x for x in data if x > 0]
```

**Why documentation matters with AI:**
- Code explains *how*, docs explain *why*
- AI doesn't know your intent
- Future context for regeneration
- Human understanding

---

## Integration with Velocity Coding

**How old tricks fit:**

**Think phase:**
- Consider test cases
- Define types upfront
- Plan for simplicity

**Plan phase:**
- Specify test requirements
- Document interfaces with types
- Design for refactorability

**Execute phase:**
- AI generates code
- Apply types, tests, linting
- Refactor for simplicity

**Review phase:**
- Validate against spec
- Run tests
- Check linting
- Assess simplicity

**Old tricks are PART of velocity, not opposed to it.**

---

## Anti-Patterns

❌ **"AI handles quality":** AI generates, doesn't judge  
❌ **"Tests slow me down":** Tests enable fast iteration  
❌ **"Types are optional":** Types improve AI generation  
❌ **"Skip refactoring":** Technical debt compounds fast  
❌ **"Move fast, break things":** Wrong lesson from startup culture  

---

## The Velocity Misconception

**Wrong interpretation:**
- Fast = skip quality practices
- Velocity = no tests, no types, no reviews
- "Move fast" = accumulate tech debt

**Right interpretation:**
- Fast = generate quickly, validate thoroughly
- Velocity = tests enable safe speed
- "Move fast, don't break things" = quality enables velocity

**Ben's phrase: "Move fast, don't break things"**
- Not "move fast and break things"
- Quality practices enable sustainable speed

---

## Tools & Practices

**Testing:**
- `pytest` - Fast, clear, comprehensive
- Test-driven with AI: write tests, have AI implement

**Types:**
- Type hints (Python 3.5+)
- `mypy` for type checking
- Helps AI generate better code

**Linting:**
- `pylint`, `flake8` - Code quality
- `black` - Formatting
- `mypy` - Type checking
- Run automatically on all generated code

**Refactoring:**
- After AI generation
- Before claiming complete
- Continuous simplification

---

## Verification

**Before shipping AI-generated code:**
- [ ] Tests written and passing
- [ ] Types added to interfaces
- [ ] Linters run clean
- [ ] Refactored for simplicity
- [ ] Code reviewed (by you)
- [ ] Documentation added
- [ ] Edge cases handled

**These aren't optional—they're essential.**

---

## The Math of Quality

**Without quality practices:**
```
Day 1: Generate 1000 lines
Day 2: Fix bugs in Day 1 code (200 lines)
Day 3: Generate 500 lines, fix more bugs (300 lines)
Day 4: Refactor because unmaintainable (500 lines)

Total: 2500 lines written, 1000 lines shipped, lots of churn
```

**With quality practices:**
```
Day 1: Generate 1000 lines + tests (1200 lines)
Day 2: Generate 1000 lines + tests (1200 lines)
Day 3: Generate 1000 lines + tests (1200 lines)
Day 4: Add feature to existing code (200 lines)

Total: 3800 lines written, 3200 lines shipped, clean codebase
```

**Quality practices = higher velocity long-term.**

---

## Source

From Ben Guo's velocity coding talk: "Old tricks still work—tests, types, linting, refactoring, simplicity. Don't skip fundamentals just because AI can generate fast."

Slide references:
- Tests
- Types
- Linting
- Refactoring
- Simplicity

---

**Created:** 2025-10-26  
**Version:** 1.0
