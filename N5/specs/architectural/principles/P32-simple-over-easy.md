# P32: Simple Over Easy

**Category:** Design Philosophy  
**Priority:** Critical  
**Related:** P8 (Minimal Context), P20 (Modular Components), P27 (Nemawashi)

---

## Principle

**Choose simple (few intertwined concepts) over easy (familiar, convenient). Simple systems are maintainable. Easy systems become complex.**

From Rich Hickey's "Simple Made Easy": Simple means *disentangled* (few braids). Easy means *near at hand* (familiar). Simple is objective—count the braids. Easy is subjective—varies by person. Choose simple, even when easy is more convenient.

---

## The Problem

**Easy (but not simple):**

```python
# "Easy" - one line, looks convenient
df.groupby(['category', 'date']).agg({'value': ['sum', 'mean', 'std']}).reset_index()

# How many concepts are intertwined?
# - DataFrames (structured data)
# - GroupBy (aggregation concept)
# - Multi-level operations (nested structure)
# - Column selection (implicit knowledge)
# - Reset index (state management)
# - Lambda-like aggregation (functional concept)

# Count: 6+ braided concepts
# Hard to reason about, hard to modify, hard to debug
```

**Simple (but less "easy"):**

```python
# "Simple" - more lines, explicit steps
records_by_category = defaultdict(list)
for record in records:
    key = (record['category'], record['date'])
    records_by_category[key].append(record['value'])

results = []
for key, values in records_by_category.items():
    results.append({
        'category': key[0],
        'date': key[1],
        'sum': sum(values),
        'mean': statistics.mean(values),
        'std': statistics.stdev(values)
    })

# How many concepts?
# - Dictionary (single concept)
# - List (single concept)
# - Loop (single concept)
# - Functions (sum, mean, stdev - familiar)

# Count: 3-4 independent concepts
# Easy to reason about, easy to modify, easy to debug
```

**The paradox:** "Simple" takes more lines but has fewer concepts. "Easy" takes fewer lines but has more concepts.

**Which is better?** Simple. Always simple.

---

## Recognition

### What is Simple?

**Simple = Few Intertwined Concepts**

- Minimal dependencies between parts
- Each component does one thing
- Easy to reason about each part independently
- Can change one part without affecting others

**Examples:**
- Plain data structures (lists, dicts)
- Pure functions (no side effects)
- Explicit steps (clear control flow)
- Unix pipes (compose independent tools)

---

### What is Easy?

**Easy = Familiar, Near at Hand, Convenient**

- Frameworks that "do everything"
- One-liner magic
- Implicit behavior
- "Convention over configuration"
- Familiar patterns from previous experience

**Examples:**
- ORM frameworks (implicit SQL)
- Monolithic libraries (batteries included)
- DSLs (domain-specific languages)
- Clever one-liners

---

### The Trap

**Easy today, complex tomorrow:**

```
Day 1: "This framework does everything! So easy!"
Day 30: "How do I customize this behavior?"
Day 60: "Why is this thing breaking?"
Day 90: "I can't modify it without breaking other parts"
Day 180: "I need to rewrite this"
```

**Simple today, simple tomorrow:**

```
Day 1: "More code to write, but straightforward"
Day 30: "Easy to customize—just change this part"
Day 60: "Bug is obvious—it's in this function"
Day 90: "Added feature by adding new function"
Day 180: "Still maintainable, still growing"
```

---

## Application

### Architectural Decision: Data Storage

**Easy option: ORM Framework (SQLAlchemy, Django ORM)**

```python
# Looks easy
class Record(Model):
    name = CharField()
    data = JSONField()
    tags = ArrayField()

# But how many braids?
# - Database connection (implicit)
# - Schema migrations (hidden)
# - Query generation (magic)
# - Type coercion (automatic)
# - Transaction management (implicit)
# - Caching (hidden)
# - Relationships (complex)

# 7+ intertwined concepts
```

**Simple option: Direct SQL + JSON**

```python
# More explicit
import sqlite3
import json

def save_record(db_path, record_dict):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO records (name, data) VALUES (?, ?)",
            (record_dict['name'], json.dumps(record_dict))
        )

def load_records(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT data FROM records").fetchall()
        return [json.loads(row[0]) for row in rows]

# How many braids?
# - Database connection (explicit)
# - SQL (standard, learnable)
# - JSON serialization (standard)

# 3 independent concepts
```

**Which is simpler?** The "more verbose" one—fewer braided concepts.

---

### Choosing Simple in Nemawashi

**When evaluating alternatives:**

```markdown
## Option A: Use Framework X

**Easy?** Yes - one import, "just works"

**Simple?** Let's count braids:
- Framework-specific patterns (1)
- Hidden configuration (2)
- Implicit behaviors (3)
- Magic methods (4)
- Vendor lock-in (5)

**Braid count: 5+**

---

## Option B: Compose Standard Tools

**Easy?** No - more code to write

**Simple?** Let's count braids:
- Standard library (1)
- Explicit functions (2)

**Braid count: 2**

---

## Decision: Choose B (Simple)

**Rationale:** Fewer braids = easier to maintain long-term.
Easy today ≠ simple tomorrow.
```

---

## The Simplicity Test

**Hexagonal complexity test:**

Imagine explaining your system to someone in 6 months (including future you).

**Questions:**
1. How many concepts do they need to understand?
2. Can they understand each concept independently?
3. Can they modify one part without understanding all parts?
4. Is the behavior explicit or implicit?
5. Can they trace execution flow easily?

**More "yes" answers = more simple.**

---

## Integration with N5

**Simple patterns in N5:**

- **JSONL over ORM:** Plain text, grep-friendly, no schema
- **Scripts over frameworks:** Explicit control flow, standard library
- **Files over database:** Direct access, version-controllable
- **grep over query language:** Standard Unix tool, composable
- **Python over DSL:** General-purpose, learnable

**All aligned with P8 (Minimal Context) and P1 (Human-Readable).**

---

## Anti-Patterns

❌ **"This framework does everything":** Easy, not simple (many braids)  
❌ **"Everyone uses this":** Popular ≠ simple  
❌ **"It's just one line":** Line count ≠ simplicity  
❌ **"Convention over configuration":** Implicit > explicit (braids)  

---

## Simple vs Easy in Practice

### Example: Task Queue

**Easy: Celery (Python task queue framework)**
- One import, seems easy
- Hidden: broker, workers, serialization, retry logic, monitoring
- Braid count: 8+

**Simple: Script + Cron + File**
```bash
# tasks.jsonl - list of tasks (one per line)
# process_tasks.py - reads, executes, logs
# cron - runs every minute

# Braid count: 3 (file, script, scheduler)
```

**Which scales better long-term?** Simple. Always simple.

---

## The Rich Hickey Framework

**From "Simple Made Easy" talk:**

| Simple | Complex |
|---|---|
| One role | Multiple roles |
| One task | Multiple tasks |
| One concept | Multiple concepts |
| One dimension | Multiple dimensions |

| Easy | Hard |
|---|---|
| Near at hand | Far from hand |
| Familiar | Unfamiliar |
| In our toolkit | Not in toolkit |

**Simple ≠ Easy**
**Prefer simple, even when hard.**

---

## Verification

**Before choosing "easy" option:**
- [ ] Count the braids (intertwined concepts)
- [ ] Can I explain each part independently?
- [ ] Can I modify one part without touching others?
- [ ] Is behavior explicit or implicit?
- [ ] Will this be maintainable in 6 months?

**If braid count >5: probably too complex, find simpler option.**

---

## Practical Heuristics

**Choose simple:**
- Plain data structures over frameworks
- Composition over inheritance
- Explicit over implicit
- Standard over custom
- Small tools over Swiss Army knife
- Separate concerns over "does everything"

**Suspect "easy":**
- One-liner magic
- "It just works" (hiding complexity)
- Large frameworks
- Implicit behaviors
- Vendor lock-in
- "Convention over configuration"

---

## The Long Game

**Month 1:**
- Easy is faster (familiar, convenient)
- Simple takes more thought

**Month 6:**
- Easy starts showing cracks
- Simple is still straightforward

**Month 12:**
- Easy requires workarounds
- Simple accepts changes gracefully

**Month 24:**
- Easy needs rewrite
- Simple still maintainable

**Choose for Month 24, not Month 1.**

---

## Source

**Rich Hickey's "Simple Made Easy" (2011):**
- Simple = objective (count concepts)
- Easy = subjective (varies by person)
- Choose simple, even when hard

**Referenced in Ben Guo's velocity coding talk as core design value.**

**Required viewing:** https://www.infoq.com/presentations/Simple-Made-Easy/

---

**Created:** 2025-10-26  
**Version:** 1.0
