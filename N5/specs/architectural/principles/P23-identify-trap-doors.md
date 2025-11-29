# P23: Identify Trap Doors

**Category:** Strategy  
**Priority:** Critical  
**Related:** P24 (Simulation), P7 (Dry-Run), P27 (Nemawashi)

---

## Principle

**Explicitly identify and document irreversible or high-cost decisions before committing to them.**

A "trap door" is a decision point where choosing one path makes it expensive or impossible to reverse later. Recognize these moments, document alternatives considered, and make the choice deliberately—not accidentally.

---

## The Problem

**Invisible trap doors:**
- Choose database format without thinking
- Pick file structure casually
- Commit to API design implicitly
- Select architecture "because it works"

**Cost:** Months later, you discover the choice was wrong, but changing it requires rewriting 50% of the system.

**Explicit trap door recognition:**
- "This is a trap door—I'm choosing JSONL over SQLite"
- Document why
- Consider alternatives
- Accept the constraint

**Benefit:** When you hit the limit, you already know why you chose it and what alternatives exist.

---

## Recognition

**A decision is a trap door if:**
- Changing it later requires extensive refactoring
- It affects how other systems integrate with yours
- It creates technical debt if wrong
- Multiple valid alternatives exist
- The "best" choice depends on future unknowns

**Common trap doors:**
1. **Data format** - JSONL, CSV, SQLite, PostgreSQL
2. **File vs. database** - Flat files, embedded DB, client-server
3. **Sync vs. async** - Blocking calls, async/await, threads
4. **Monolith vs. modular** - Single file, multiple modules, microservices
5. **Schema design** - Flat, nested, relational, normalized
6. **API design** - REST, GraphQL, RPC, function calls
7. **Language choice** - Python, Rust, JavaScript, shell script
8. **Framework choice** - Flask, FastAPI, Next.js, vanilla

---

## Application

### Step 1: Recognize the Trap Door

**During specification (P24 simulation):**

```markdown
## Trap Door: Data Storage Format

**Decision Required:** How to store command registry?

**Options:**
1. JSONL (one JSON object per line)
2. Single JSON array
3. SQLite database
4. Directory of files

**This is a trap door because:**
- Changing format later requires migration scripts
- Affects all code that reads/writes commands
- Impacts grep-ability and human readability
- Choice determines performance characteristics at scale
```

---

### Step 2: Evaluate Alternatives

**For each option, document:**

```markdown
### Option 1: JSONL (one JSON object per line)

**Pros:**
- Append-only writes (fast, simple)
- Grep-friendly (line-based search)
- Human-readable
- Git-diffable
- No dependencies

**Cons:**
- Full file read for queries
- No indexing
- Slow at >10K records
- Manual validation required

**Scale limit:** ~1,000 records before noticeable slowdown

---

### Option 2: SQLite

**Pros:**
- Indexed queries (instant)
- ACID transactions
- Scales to millions of records
- Schema validation built-in

**Cons:**
- Binary format (not grep-able)
- Requires sqlite3 library
- Harder to debug
- Overkill for <100 records

**Scale limit:** Millions of records

---

### Option 3: Directory of files

**Pros:**
- Simple filesystem operations
- Natural partitioning
- Easy backups

**Cons:**
- Slow directory scans
- No atomic updates
- Messy for many items
- Harder to query

**Scale limit:** ~100 files before performance degrades
```

---

### Step 3: Make the Choice Explicitly

**Document the decision:**

```markdown
## Decision: JSONL

**Rationale:**
- Current scale: <100 commands (expected: never exceed 200)
- Performance acceptable: grep search <10ms for 100 records
- Aligns with P1 (simplicity) and P8 (minimal dependencies)
- Human-readable for debugging (P22: explicit)
- Git-friendly for version control

**Trap door acknowledged:**
- If we exceed 1,000 commands, migrate to SQLite
- Migration path: read JSONL → insert into SQLite → update code
- Estimated migration cost: 2-3 hours

**Alternatives considered:** SQLite (overkill), directory (too messy)

**This choice commits us to:**
- Full-file reads for queries
- Manual schema validation
- Performance degradation beyond 1K records

**We accept this trade-off because:** Simplicity wins at current scale.
```

---

### Step 4: Monitor the Trap Door

**Set triggers for reevaluation:**

```markdown
## Trap Door Monitoring

**Reevaluate this decision if:**
- [ ] Command count exceeds 500
- [ ] Query time exceeds 100ms
- [ ] Adding complex filtering requirements
- [ ] Need transaction support
- [ ] Hit JSONL format limitations

**Current status (2025-10-29):**
- Commands: 23 
- Query time: ~5ms
- Status: ✅ Well within acceptable range
```

---

## Integration with Think → Plan → Execute

**Think phase:**
- Identify trap doors during specification
- List alternatives
- Document trade-offs

**Plan phase:**
- Choose explicitly
- Document rationale
- Set monitoring triggers

**Execute phase:**
- Implement chosen path
- Add comments marking trap door decisions

**Review phase:**
- Check if trap door limits were hit
- Validate choice was correct
- Update monitoring if needed

---

## Documentation Template

```markdown
## Trap Door: [Decision Name]

**Options:**
1. [Option A] - [brief description]
2. [Option B] - [brief description]
3. [Option C] - [brief description]

**Choice:** [Option X]

**Rationale:**
- [Why this option fits current needs]
- [Which principles it aligns with]
- [What constraints we accept]

**Costs if wrong:**
- [What breaks if we need to change]
- [Estimated refactoring cost]
- [Migration path]

**Alternatives considered:** [Brief summary]

**Reevaluate if:**
- [ ] [Trigger condition 1]
- [ ] [Trigger condition 2]
```

---

## Anti-Patterns

❌ **Ignoring trap doors:** "I'll cross that bridge when I come to it" (bridge is demolished)  
❌ **Over-planning:** Analyzing 10 options for 2 hours (diminishing returns)  
❌ **Implicit choices:** Picking format without documenting why  
❌ **No monitoring:** Never checking if assumptions held  

---

## Verification

**Before committing to a trap door:**
- [ ] Identified this as a trap door decision
- [ ] Listed 2-3 viable alternatives
- [ ] Documented pros/cons for each
- [ ] Made choice explicitly with rationale
- [ ] Set monitoring triggers for reevaluation
- [ ] Estimated migration cost if wrong

---

## Source

From planning_prompt.md: "Identify trap doors—decisions that are hard to reverse—and make them consciously."

---

**Created:** 2025-10-30  
**Version:** 1.0
