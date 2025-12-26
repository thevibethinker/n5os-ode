# P32: Simple Over Easy

**Category:** Design Philosophy  
**Priority:** Critical  
**Related:** P25 (Code Is Free), P27 (Nemawashi)

---

## Principle

**Choose simple (few intertwined concepts) over easy (familiar, convenient). Simple systems are maintainable. Easy systems become complex.**

From Rich Hickey: Simple means *disentangled* (few braids). Easy means *near at hand* (familiar). Simple is objective—count the braids. Easy is subjective.

---

## The Trade-Off

**Easy:** Familiar, convenient, fast to start → Hard to maintain, debug, modify  
**Simple:** Unfamiliar, more lines, slower start → Easy to maintain, debug, modify

**Choose simple.** Your future self will thank you.

---

## Recognition

### What is Simple?
- Few intertwined concepts
- Minimal dependencies between parts
- Each component does one thing
- Easy to reason about independently

### What is Easy?
- Looks familiar
- Fewer lines of code
- One-line solutions
- Framework magic

**Trap:** Easy feels productive today. Simple is productive forever.

---

## Examples

### Database Choice

**Easy:** PostgreSQL + ORM (familiar, powerful)
- Concepts: network, auth, migrations, connections, ORM, SQL abstraction

**Simple:** SQLite file (unfamiliar to some)
- Concepts: file on disk

**N5 Choice:** SQLite for single-user systems.

### Code Style

**Easy (complex):**
```python
result = df.groupby('cat').agg({'val': 'sum'}).reset_index()
# Concepts: DataFrame, groupby, agg dict, index management
```

**Simple (clear):**
```python
totals = {}
for record in records:
    cat = record['category']
    totals[cat] = totals.get(cat, 0) + record['value']
# Concepts: dict, loop, accumulation
```

**Choose:** Simple (3 concepts) over easy (5+ concepts).

---

## Framework

**Before choosing, evaluate:**

1. **Count the braids** (concepts intertwined)
   - Simple = 1-3 concepts
   - Complex = 5+ concepts

2. **Check familiarity**
   - Easy = familiar pattern
   - Hard = unfamiliar pattern

**Matrix:**
```
         Easy    Hard
Simple   [BEST]  [GOOD]  ← Choose
Complex  [TRAP]  [AVOID] ← Avoid
```

**Priority:** Simple > Easy. Always.

---

## Application

1. **Before adding dependency:** Can I do this with stdlib + 10 more lines?
2. **Before using framework feature:** Do I understand all hidden concepts?
3. **Before clever code:** Can a beginner understand this in 2 minutes?

**Default:** If simple requires 2x lines but 0.5x concepts, choose simple.

---

## Common Mistakes

❌ "One-liners are simpler" → No. Count concepts, not lines.  
❌ "Framework X makes it easy" → Easy ≠ simple. Reduces lines or concepts?  
❌ "Everyone does it this way" → Popularity ≠ simplicity.

---

## Related Principles

- **P25 (Code Is Free):** More lines costs nothing. More concepts costs everything.
- **P27 (Nemawashi):** Explore alternatives to find the simple solution.

---

**Reference:** Rich Hickey, "Simple Made Easy" (2011)
