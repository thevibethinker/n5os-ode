# P25: Code Is Free, Thinking Is Expensive

**Category:** Design Philosophy  
**Priority:** Critical  
**Related:** P32 (Simple Over Easy), P26 (Fast Feedback Loops)

---

## Principle

**Writing code costs nothing. Thinking, debugging, and maintaining costs everything. Optimize for thought, not keystrokes.**

The bottleneck in software isn't typing speed—it's understanding. Prefer 100 lines of clear code over 10 lines of clever code. Your time is spent reading and debugging, not writing.

---

## The Math

**Typical time distribution:**
- 5% Writing new code
- 20% Reading existing code
- 50% Debugging
- 25% Maintenance

**Optimize for the 95%, not the 5%.**

---

## Examples

### Verbosity Over Cleverness

**Clever (expensive):**
```python
# One line! Impressive! Unmaintainable.
result = [x for x in [y for y in data if y['active']] if x['score'] > threshold]
```

**Clear (cheap):**
```python
# More lines, but obvious intent
active_items = [item for item in data if item['active']]
high_scoring = [item for item in active_items if item['score'] > threshold]
result = high_scoring
```

**Cost difference:** 
- Clever: 30 seconds to write, 5 minutes to understand later
- Clear: 60 seconds to write, 10 seconds to understand later

### Explicit Over Implicit

**Implicit (expensive):**
```python
def process(data, mode=1):
    """Process data. Mode: 1=filter, 2=transform, 3=aggregate"""
    return [MODE_HANDLERS[mode](x) for x in data]
```

**Explicit (cheap):**
```python
def filter_data(data):
    return [x for x in data if x['valid']]

def transform_data(data):
    return [{'id': x['id'], 'value': x['val'] * 2} for x in data]

def aggregate_data(data):
    return sum(x['value'] for x in data)
```

**Cost difference:**
- Implicit: "Magic" that requires understanding MODE_HANDLERS
- Explicit: Self-documenting, each function does one thing

### Early Returns Over Nested Logic

**Nested (expensive):**
```python
def validate(record):
    if record:
        if 'id' in record:
            if record['id'] > 0:
                if record['status'] == 'active':
                    return True
    return False
```

**Early returns (cheap):**
```python
def validate(record):
    if not record:
        return False
    if 'id' not in record:
        return False
    if record['id'] <= 0:
        return False
    if record['status'] != 'active':
        return False
    return True
```

**Cost difference:**
- Nested: Must trace through all branches mentally
- Early returns: Linear reading, exit points clear

---

## Application

### When Writing Code

1. **First draft:** Write it clearly
2. **Second pass:** Make it work
3. **Third pass:** Remove duplication
4. **Stop:** Don't optimize further unless profiling proves it's slow

**Don't:** Write "optimized" code first. You'll get it wrong and waste time.

### When Reviewing Code

Ask: "Will I understand this in 6 months?"

If no:
- Add comments explaining *why*, not *what*
- Break into smaller functions
- Use descriptive variable names
- Add type hints

### When Debugging

**Cost of unclear code:**
- 10 lines clever code = 2 hours debugging
- 100 lines clear code = 10 minutes debugging

**ROI:** Clear code pays for itself immediately.

---

## Exceptions

Sometimes brevity aids clarity:

**Good brevity:**
```python
# Clear and concise
items = [x for x in data if x > 0]
```

**Bad brevity:**
```python
# Obscure
items = list(filter(lambda x: x > 0, data))
```

**Rule:** Prefer standard patterns (list comprehensions) over obscure ones (lambda + filter).

---

## Common Mistakes

❌ "This one-liner is elegant" → Elegance for humans, not computers
❌ "Less code = better" → Less *complexity* = better, not less *lines*
❌ "Comments are for weak code" → Comments explain *why*, code explains *what*

---

## Related Principles

- **P32 (Simple Over Easy):** Simple = fewer concepts, even if more lines
- **P26 (Fast Feedback Loops):** Clear code enables faster iteration
- **P30 (Maintain Feel for Code):** Clear code maintains understanding

---

**Remember:** You're not paid to write code. You're paid to solve problems. The less code you write, the fewer bugs you create. The clearer code you write, the faster you solve the next problem.

**Optimize for understanding, not keystrokes.**
