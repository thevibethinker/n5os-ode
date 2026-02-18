# P27: Nemawashi Mode

**Category:** Design Philosophy  
**Priority:** Medium  
**Related:** P32 (Simple Over Easy), P31 (Own the Planning)

---

## Principle

**Explore 2-3 alternatives before committing. "Nemawashi" (根回し) means laying groundwork—understanding the terrain before building.**

Before choosing a solution, deliberately explore alternatives. Don't pick the first approach that works. The best solution often isn't obvious initially.

---

## Pattern



**Minimum:** Two alternatives (current + one other)
**Ideal:** Three alternatives (shows you've explored the space)

---

## Examples

### Database Choice

**Without Nemawashi:**
- "We need a database" → PostgreSQL → Build

**With Nemawashi:**
1. SQLite (simple, portable, zero config)
2. PostgreSQL (powerful, network, complex setup)
3. JSON files (simplest, no SQL knowledge needed)

**Choose:** SQLite for single-user, PostgreSQL for multi-user, JSON for prototypes

### Architecture

**Without Nemawashi:**
- "We need background jobs" → Celery + Redis → Build

**With Nemawashi:**
1. Cron + shell scripts (simple, built-in)
2. Celery + Redis (powerful, complex)
3. Python APScheduler (middle ground)

**Choose:** Based on actual requirements, not assumptions

---

## Benefits

1. **Avoid local maxima:** First solution often isn't best
2. **Understand trade-offs:** Explicit comparison forces clarity
3. **Build conviction:** "We chose X because Y and Z didn't fit"
4. **Learn landscape:** Exploration teaches you the domain

---

## Application

Before committing to a solution, ask:
- What are 2 other ways to solve this?
- Why would I choose each approach?
- What are the trade-offs?

Spend 15 minutes exploring alternatives. It saves hours of regret.

---

## Common Mistakes

❌ "Analysis paralysis" (exploring forever)
❌ Only considering familiar solutions
❌ Not documenting the alternatives considered

**Fix:** Set a timer (15 minutes). Document alternatives. Choose.

---

## Related Principles

- **P32 (Simple Over Easy):** Nemawashi reveals the simple solution
- **P31 (Own the Planning):** Exploration is part of planning

---

**Pattern:** Explore → Compare → Commit
