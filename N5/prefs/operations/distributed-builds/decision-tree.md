# Decision Tree: Sequential vs. Distributed Builds

Use this to determine the right approach for your change.

---

## Quick Decision

**Use SEQUENTIAL (single conversation) if:**
- Total scope < 500 LOC
- ≤ 2 files to modify
- Single module/component
- Quick iteration matters more than perfect quality
- Low risk (non-critical system)

**Use DISTRIBUTED (multi-conversation) if:**
- Total scope > 500 LOC
- > 2 files to modify
- Multiple modules with clear boundaries
- Quality is critical
- Complex dependency graph
- You want best possible architecture

---

## Detailed Analysis

### Scope Indicators

| Indicator | Sequential | Distributed |
|-----------|-----------|-------------|
| **Lines of Code** | < 500 | > 500 |
| **Files Modified** | 1-2 | 3+ |
| **Modules Touched** | 1 | 2+ |
| **Estimated Time** | < 2 hours | > 2 hours |
| **Dependencies** | Simple/none | Complex graph |

### Quality Requirements

| Factor | Sequential OK | Distributed Better |
|--------|--------------|-------------------|
| **System Criticality** | Low | High |
| **Test Coverage Needed** | Basic | Comprehensive |
| **Architecture Impact** | Isolated change | Cross-cutting |
| **Future Maintainability** | Not a concern | Critical |
| **Principle Adherence** | Nice to have | Must have |

### Context Complexity

| Scenario | Sequential | Distributed |
|----------|-----------|-------------|
| "Add a helper function" | ✅ | |
| "Refactor a single module" | ✅ | |
| "Add a feature to existing system" | | ✅ |
| "Build a new subsystem" | | ✅ |
| "Integrate multiple systems" | | ✅ |
| "Major architectural change" | | ✅ |

---

## Cost-Benefit Analysis

### Sequential Build

**Time Investment:**
- Setup: 0 minutes (just start coding)
- Execution: 1-2 hours
- **Total: 1-2 hours**

**Benefits:**
- Fast iteration
- Single context = easy to reason about
- No coordination overhead

**Drawbacks:**
- Context contamination at scale (>500 LOC)
- More bugs in complex changes
- Harder to maintain quality standards

**Best for:** Quick wins, small changes, prototypes

---

### Distributed Build

**Time Investment:**
- Setup: 30-60 min (framing + decomposition)
- Worker execution: 1-2 hours per worker (parallel from V's perspective)
- Integration: 15-30 min per worker
- **Total: 2-4 hours** (but higher quality output)

**Benefits:**
- Context isolation = fewer bugs
- Each module gets full attention
- Incremental testing
- Scales to arbitrary complexity
- Better architecture

**Drawbacks:**
- Coordination overhead
- Learning curve (first time)
- Overkill for simple changes

**Best for:** Major features, system upgrades, critical changes

---

## Examples

### Sequential Build Examples ✅

1. **Add logging to existing function**
   - 1 file, 50 LOC, simple change

2. **Fix a bug in single module**
   - 1 file, 20 LOC, isolated

3. **Update documentation**
   - Multiple files, but no code dependencies

4. **Add a utility function**
   - 1 file, 100 LOC, clear scope

### Distributed Build Examples ✅

1. **Build new N5 subsystem**
   - 5 files, 1200 LOC, multiple modules
   - **Workers:** Parser, State Manager, CLI, Integration, Tests

2. **Refactor meeting intelligence system**
   - 8 files, 2000 LOC, complex dependencies
   - **Workers:** Extraction, Transform, Storage, API, Orchestration, Tests

3. **Add multi-format export feature**
   - 6 files, 900 LOC, clear module boundaries
   - **Workers:** PDF export, DOCX export, HTML export, CLI, Tests, Docs

4. **Integrate new external service**
   - 4 files, 700 LOC, authentication + API + caching + error handling
   - **Workers:** Auth layer, API client, Cache layer, Error handling + tests

---

## Edge Cases

### "I'm not sure about LOC estimate"

**Heuristic:** If you can't confidently estimate scope in 5 minutes → it's probably distributed territory.

### "It's 600 LOC but really simple"

**Consider:** Complexity > LOC. If it's truly simple (repetitive, no dependencies), sequential is fine.

### "It's 300 LOC but touches critical systems"

**Consider:** Risk > LOC. If failure impact is high → distributed for quality.

### "I want to learn distributed builds"

**Recommendation:** Pick a medium-sized build (800-1200 LOC, 3-4 workers) as first learning case. Document lessons.

---

## Decision Flowchart

```
Start
  │
  ├─ Is scope > 500 LOC?
  │   ├─ YES → Distributed
  │   └─ NO → Continue
  │
  ├─ Does it touch > 2 files?
  │   ├─ YES → Distributed
  │   └─ NO → Continue
  │
  ├─ Is it critical system?
  │   ├─ YES → Distributed
  │   └─ NO → Continue
  │
  ├─ Complex dependencies?
  │   ├─ YES → Distributed
  │   └─ NO → Sequential
```

---

## When in Doubt

**Ask yourself:**
1. "Would I be stressed reviewing all this code in one go?"
2. "Are there natural module boundaries?"
3. "Is quality more important than speed right now?"

If 2+ answers are YES → Distributed

---

## Next Steps

**If Sequential:**
- Just start building in single conversation
- Follow `file 'Knowledge/architectural/architectural_principles.md'`

**If Distributed:**
1. Operator activates Vibe Builder persona
2. Load `file 'protocol.md'`
3. Begin framing stage
