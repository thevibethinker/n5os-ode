# Troubleshooting Distributed Builds

Common issues and how to resolve them.

---

## Worker Issues

### "Worker says assignment is unclear"

**Symptoms:**
- Worker asks many clarifying questions
- Worker makes wrong assumptions
- Worker can't start

**Root Cause:** Assignment not explicit enough

**Fix:**
1. Read worker's questions carefully
2. Update assignment with:
   - More explicit scope
   - Concrete examples
   - Exact interface definitions
3. Add clarifications to assignment file
4. Worker reloads assignment
5. **Prevention:** Be more explicit in future assignments (use examples)

---

### "Worker exceeded scope"

**Symptoms:**
- Worker modified files not on whitelist
- Worker added features not requested
- Worker deliverables > assignment

**Root Cause:** Scope creep, unclear boundaries

**Fix:**
1. Error E201
2. Worker reverts unauthorized changes
3. **Prevention:** Make anti-scope section more prominent in assignment

**Decision Tree:**
- Extra work is valuable? → Accept but document as bonus
- Extra work is distraction? → Revert, refocus on assignment

---

### "Worker is blocked"

**Symptoms:**
- Worker status = BLOCKED
- Error report generated
- Progress stopped

**Fix:**
1. Read error report: `W[N]_ERROR_LOG.md`
2. Assess blocker type:

**Blocker Type A: Missing Information**
- **Fix:** Orchestrator provides clarification, updates assignment
- **Time:** 5-15 min

**Blocker Type B: Dependency Not Ready**
- **Fix:** Worker waits or works on something else
- **Time:** Until prerequisite complete

**Blocker Type C: Interface Mismatch**
- **Fix:** Coordinate between workers OR redesign interface
- **Time:** 15-30 min

**Blocker Type D: Fundamental Problem**
- **Fix:** May need to rescope or redesign approach
- **Time:** 1+ hour

---

### "Worker taking too long"

**Symptoms:**
- Worker in IN_PROGRESS > 2 hours
- No updates to state
- Scope seems stuck

**Root Cause:** Scope too large OR worker stuck on problem

**Fix:**
1. Check with user (V): "Worker [N] still in progress. Check status?"
2. Assess situation:
   - Worker making progress? → Wait
   - Worker stuck? → Provide guidance or simplify scope
   - Scope too large? → Split into sub-workers

**Prevention:** Keep workers small (100-300 LOC target)

---

### "Worker tests fail"

**Symptoms:**
- Worker reports test failures
- Code doesn't work as expected

**Root Cause:** Implementation bug OR test is wrong

**Fix:**
1. Worker debugs: Is code wrong or test wrong?
2. Fix accordingly
3. If repeatedly failing → orchestrator reviews approach

---

## Orchestrator Issues

### "Decomposition taking forever"

**Symptoms:**
- Orchestrator spending >1 hour on decomposition
- Can't figure out how to split work
- Too many options considered

**Root Cause:** Analysis paralysis (P13) OR scope too complex

**Fix:**
1. **Time-box decision:** Pick an approach in next 15 minutes
2. **Start simple:** Create 3-4 workers with clear boundaries
3. **Iterate:** Can refine after first worker shows patterns

**Reminder:** Perfect decomposition doesn't exist. Good enough > perfect.

---

### "Integration taking too long"

**Symptoms:**
- Orchestrator spending >1 hour per worker integration
- Deep diving into every line
- Overthinking decisions

**Root Cause:** Over-reviewing OR worker summaries insufficient

**Fix:**
1. **Follow checklist:** `file 'templates/INTEGRATION_CHECKLIST.md'` (don't improvise)
2. **Time-box:** 30 min max per worker
3. **Trust tests:** If tests pass, don't second-guess everything
4. **Improve summaries:** If you're confused, worker summary needs more detail

**Prevention:** Make worker summary requirements more explicit

---

### "Can't decide: ACCEPT vs REJECT"

**Symptoms:**
- Worker code has minor issues
- Unclear if worth sending back
- Stuck on decision

**Decision Matrix:**

| Issue Severity | Time to Fix | Decision |
|----------------|-------------|----------|
| Typo / formatting | < 5 min | REVISE (orchestrator fixes) |
| Missing edge case | < 15 min | REVISE if simple, REJECT if complex |
| Wrong approach | > 30 min | REJECT (worker must redo) |
| Logic bug | Any | REJECT (worker must fix) |
| Principle violation | Depends | REJECT if serious, ACCEPT with note if minor trade-off |
| Missing test | < 15 min | REVISE (orchestrator adds), or REJECT for critical code |

**Guideline:** If you're hesitating > 10 minutes, probably REJECT with clear feedback.

---

### "Orchestrator lost track of state"

**Symptoms:**
- Unsure which workers are done
- Unsure what to integrate next
- State file out of sync

**Fix:**
1. Read `BUILD_STATE_SESSION.md` fully
2. Update any stale status entries
3. Check dependency graph
4. Determine next worker in sequence

**Prevention:** Update BUILD_STATE_SESSION.md after EVERY worker interaction

---

## Dependency Issues

### "Circular dependency discovered"

**Symptoms:**
- W2 needs W3, W3 needs W2
- Can't determine execution order

**Root Cause:** Bad decomposition

**Fix:**
1. **Redesign:** Break circular dependency by:
   - Extracting shared component → new worker
   - Redefining interfaces
   - Changing execution order
2. **Example:**
   ```
   BAD:
   W2 (parser) needs W3 (validator)
   W3 (validator) needs W2 (parser)
   
   GOOD:
   W1 (shared data structures)
     ├→ W2 (parser, uses W1)
     └→ W3 (validator, uses W1)
   ```

---

### "Worker waiting forever for dependency"

**Symptoms:**
- W3 blocked waiting for W1
- W1 taking too long

**Fix:**
1. **Assess W1 progress:**
   - Nearly done? → W3 waits
   - Stuck? → Help W1 unblock
   - Scope too large? → Split W1, let W3 start with partial

2. **Workaround:** Can W3 start with mock/stub of W1's output?

---

### "Interface mismatch between workers"

**Symptoms:**
- W2 delivers output in format A
- W3 expected input in format B
- Integration fails

**Root Cause:** Interface not explicitly defined in assignments

**Fix:**
1. **Assess severity:**
   - Simple conversion? → W3 adds adapter (or orchestrator does)
   - Fundamental mismatch? → One worker must change

2. **Decide who changes:**
   - Fewer dependents? → That one changes
   - Already integrated? → Unintegrated one changes
   - Equal? → W higher in dependency tree changes

3. **Prevent recurrence:** Define interfaces EXACTLY in future assignments (show examples)

---

## Build-Level Issues

### "Build scope growing"

**Symptoms:**
- Started with 3 workers, now have 7
- Keep discovering more work
- Timeline expanding

**Root Cause:** Scope wasn't well-defined OR requirements changing

**Fix:**
1. **Stop and assess:**
   - Is new work truly necessary for THIS build?
   - Or can it be deferred?

2. **Options:**
   - **Defer:** Move new work to backlog, complete original scope
   - **Pivot:** Accept new scope, update timeline
   - **Hybrid:** Complete core workers, defer extras

3. **Update BUILD_STATE_SESSION.md** with scope decision

**Prevention:** Better framing phase (spend more time defining what's in/out)

---

### "Quality issues across multiple workers"

**Symptoms:**
- Multiple workers missing tests
- Multiple workers violating principles
- Pattern of poor quality

**Root Cause:** Assignments not emphasizing quality standards

**Fix:**
1. **Immediate:** Send all deficient workers back for fixes
2. **Systemic:** Update remaining assignments to emphasize:
   - Quality gates
   - Test requirements
   - Principle adherence
3. **Root fix:** Update WORKER_ASSIGNMENT template

---

### "Build taking way longer than estimated"

**Symptoms:**
- Estimated 8 hours, now at 16 hours
- Still not complete

**Root Cause:** Bad estimation OR scope creep OR blockers

**Fix:**
1. **Assess:**
   - Original scope? → Bad estimation (learn for next time)
   - Scope grew? → Scope creep (cut or accept)
   - Many blockers? → Assignments weren't clear enough

2. **Options:**
   - **Push through:** Complete as planned (accept time cost)
   - **Cut scope:** Defer some workers
   - **Halt:** Too expensive, try different approach

3. **Document in after-action:** Why estimation was off

---

### "Build failed completely"

**Symptoms:**
- Can't integrate workers
- Fundamental design flaw discovered
- Need to start over

**Root Cause:** Usually bad decomposition in Stage 2

**Fix:**
1. **Acknowledge:** Not all builds succeed
2. **Don't force it:** If fundamentally broken, stop
3. **Document:**
   - What went wrong
   - Why
   - What would we do differently
4. **Options:**
   - Restart with new decomposition
   - Abandon distributed approach, go sequential
   - Defer build entirely

**Update BUILD_STATE_SESSION.md:**
```markdown
**Status:** FAILED

**Reason:** [Clear explanation]

**Lessons:** [What we learned]

**Next steps:** [What we'll do instead]
```

---

## Communication Issues

### "Lost track of which conversation is which"

**Symptoms:**
- Multiple worker chats open
- Confused about which is orchestrator
- Adding files to wrong conversation

**Fix:**
1. **Label conversations clearly** in Zo UI (if possible)
2. **Check conversation workspace:** Each has unique ID
   - Orchestrator: `/home/.z/workspaces/[orchestrator-id]/`
   - Workers: `/home/.z/workspaces/[worker-id]/`
3. **Look for BUILD_STATE_SESSION.md:**
   - Present? → Orchestrator
   - Absent? → Worker

**Prevention:** Only have orchestrator + 1 active worker open at a time

---

### "Worker updated state but orchestrator doesn't see it"

**Symptoms:**
- Worker says "updated BUILD_STATE_SESSION.md"
- Orchestrator reads it, doesn't see changes

**Root Cause:** Worker wrote to wrong path OR file moved

**Fix:**
1. **Check paths:**
   - Worker should write to: `/home/workspace/N5/logs/builds/[build-name]/BUILD_STATE_SESSION.md`
   - Orchestrator should read from: same location
2. **If paths differ:** Reconcile, ensure both use same file

**Prevention:** Provide absolute paths in assignments

---

## First-Time Issues

### "Don't understand the workflow"

**Fix:**
1. Read `file 'protocol.md'` fully
2. Review `file 'decision-tree.md'` (is this right approach?)
3. Pick a SMALL pilot build (3 workers, 500-800 LOC)
4. Follow protocol step-by-step
5. Don't improvise until you've done it once

---

### "Assignments feel too detailed"

**Response:** That's the point. Explicit > implicit.

Distributed builds succeed because workers have ZERO ambiguity about what to build. Better to over-specify than under-specify.

If workers constantly succeed without needing clarification → assignments are right level of detail.

---

### "Integration checklist feels tedious"

**Response:** Checklists prevent errors.

Each step catches specific failure modes. Skip steps → bugs slip through.

As you gain experience, you'll internalize the checklist, but still reference it for edge cases.

---

## System-Level Troubleshooting

### "Everything is taking longer than expected"

**Possible Causes:**
1. **Learning curve:** First distributed build? Expect 2x time
2. **Scope misjudgment:** Actually larger than estimated
3. **Bad decomposition:** Workers too large or wrong boundaries
4. **Quality issues:** Spending time on rework
5. **Blockers:** Too many dependencies or unclear assignments

**Fix:**
1. Identify which stage is slow:
   - Framing? → Scope wasn't clear enough
   - Decomposition? → P13 or difficult domain
   - Worker execution? → Workers too large
   - Integration? → Summaries insufficient or orchestrator over-reviewing

2. Optimize slowest stage for next build

---

### "Feeling overwhelmed"

**Symptoms:**
- Too many moving pieces
- Lost track of what's happening
- Tempted to give up and do it in one conversation

**Fix:**
1. **Breathe:** It's okay to feel this way initially
2. **Simplify:** Can you reduce workers? (3 workers > 6 for first build)
3. **Focus on one thing:** Just integrate the next worker. Don't think about all of them.
4. **Trust the system:** Follow protocol, don't improvise
5. **Remember why:** Context isolation = higher quality code

**If still overwhelmed:** Consider if distributed is right approach for THIS build. Maybe it's actually better as sequential.

---

## When to Abort

Sometimes distributed build isn't working. Signs to abort:

- [ ] >50% of workers need multiple rework cycles
- [ ] Integration taking > 1 hour per worker consistently
- [ ] Constant blockers and circular dependencies
- [ ] You (V) feeling frustrated and stuck
- [ ] Fundamentally wrong decomposition discovered

**If aborting:**
1. Don't feel bad - learning experience
2. Document what went wrong
3. Try simpler build next time, or go sequential
4. Review framing and decomposition stages (likely where it broke)

---

## Getting Help

**If stuck after trying troubleshooting steps:**

1. **Check documentation:**
   - `file 'protocol.md'`
   - `file 'error-tracking-guide.md'`
   - This file

2. **Review BUILD_STATE_SESSION.md:**
   - Read lessons learned
   - Check error log
   - Look for patterns

3. **Ask V (yourself):**
   - "What's the simplest fix?"
   - "Is this worth the time investment?"
   - "Should I adjust approach?"

4. **Document for future:**
   - Add issue to this troubleshooting guide
   - Update templates to prevent recurrence

---

## Common Patterns

### Success Pattern: "Clear assignments, smooth integration"

**What you see:**
- Workers complete quickly
- Few questions or blockers
- Integration takes < 30 min
- High quality output

**Why it works:**
- Orchestrator spent time on explicit assignments
- Examples provided
- Interfaces defined exactly
- Quality standards clear

**Repeat this.**

---

### Failure Pattern: "Constant rework"

**What you see:**
- Workers repeatedly REJECTED
- Integration finds many issues
- Timeline expanding

**Why it fails:**
- Assignments too vague
- Quality standards not explicit
- Worker testing insufficient

**Fix:** Update assignment template, be more explicit.

---

### Failure Pattern: "Integration bottleneck"

**What you see:**
- Workers complete quickly
- Integration takes forever
- Orchestrator overwhelmed

**Why it fails:**
- Worker summaries insufficient
- Orchestrator over-reviewing
- Too many workers integrating simultaneously

**Fix:** Better summaries, follow checklist, integrate one at a time.

---

## Prevention > Cure

**Best troubleshooting is prevention:**

1. **Invest in framing** - 30% of effort here prevents 70% of later issues
2. **Be explicit in assignments** - Better to over-specify
3. **Define interfaces exactly** - Show examples, don't assume
4. **Keep workers small** - 100-300 LOC target
5. **Update lessons learned** - After EVERY integration
6. **Refine templates** - Based on what you learn

---

## Metrics for Health

Track these to assess if build is healthy:

| Metric | Healthy | Unhealthy |
|--------|---------|-----------|
| Rework cycles per worker | 0-1 | 2+ |
| Integration time | < 30 min | > 1 hour |
| Workers blocked | < 20% | > 50% |
| Questions per worker | 0-2 | 5+ |
| Principle violations | 0 | 2+ |

If multiple metrics are unhealthy → investigate root cause.

---

**Remember:** Troubleshooting is learning. Every issue teaches you how to make the next build smoother.
