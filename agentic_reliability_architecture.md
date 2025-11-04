---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Agentic Reliability Architecture: Solving Rule Decay & Diligence Failures

## Purpose

Design comprehensive system to address V's two most painful Zo failure modes:
1. **Rule decay over long conversations** - Critical rules forgotten as context grows  
2. **Diligence failures** - Incomplete work, placeholders, lost artifacts, confabulated completion

This is meta-design for Zo's behavioral reliability. Builder will implement.

---

## Problem Analysis

### Failure Mode 1: Rule Decay

**Symptoms:**
- Long conversations (>15 exchanges) degrade ~20-30%
- P15 violations increase
- Persona switches forgotten
- Safety checks skipped

**Root cause:** Transformer attention U-curve (beginning/end strong, middle weak)

**Cost:** Increased validation burden, repeated corrections, trust erosion

### Failure Mode 2: Diligence Failures

**Symptoms:**
- "✓ Done" when 13/23 subtasks complete
- Undocumented placeholders
- Lost artifact tracking
- Confabulated features

**Root cause:** No structured work tracking, optimistic completion bias (P15)

**Cost:** 2-3x validation cycles, phantom features, debugging non-existent code

---

## Design Philosophy

**Core:** *Explicit state > Implicit assumptions*

**Trade-offs:**
- ✅ Verbose tracking over silent execution
- ✅ Explicit checkpoints over assumed progress  
- ✅ Structured state over memory
- ✅ Self-verification loops over trust
- ❌ Avoid cognitive overhead that slows thinking
- ❌ Avoid tracking theater (useless metrics)

**Rationale:** V prefers cognitive load on them over Zo silent failures. Reliability > convenience.

---

## Architecture: Two-System Solution

### System 1: Critical Rule Pinning (Solves Rule Decay)

**What:** Position critical rules at context boundaries (beginning AND end) where attention is strongest

**How:** Dynamic rule injection system

**Components:**

#### 1A. Rule Classification Database
**File:** `N5/data/critical_rules.db` (SQLite)

**Schema:**
```sql
CREATE TABLE critical_rules (
    rule_id TEXT PRIMARY KEY,
    rule_text TEXT NOT NULL,
    priority INTEGER NOT NULL,  -- 1=MUST NEVER FORGET, 2=Important, 3=Guideline
    category TEXT NOT NULL,     -- safety|completion|persona|technical
    trigger_context TEXT,       -- When does this matter? (JSON array of contexts)
    violation_cost TEXT,        -- What happens if violated?
    last_violated_ts TIMESTAMP  -- Track failure patterns
);

CREATE TABLE rule_applications (
    conversation_id TEXT,
    rule_id TEXT,
    position TEXT,              -- beginning|end|both
    exchange_number INTEGER,
    violated BOOLEAN DEFAULT 0,
    FOREIGN KEY (rule_id) REFERENCES critical_rules(rule_id)
);
```

**Priority 1 Rules (ALWAYS at context boundaries):**
- P15: Complete Before Claiming
- P5: Safety & Anti-Overwrite  
- Persona return protocol
- Never confabulate features
- Always verify state before claiming done

**Priority 2 Rules (Context-dependent injection):**
- Technical decision pushback (when building)
- Ambiguity detection (when requirements unclear)
- Trap door identification (when architectural decisions)

#### 1B. Rule Injection Hook
**File:** `N5/scripts/rule_injector.py`

**Function:** Before generating each response, inject Priority 1 rules at BOTH beginning and end of context

**Implementation:**
```python
def inject_critical_rules(
    conversation_id: str,
    exchange_number: int,
    current_context: str,
    context_length_tokens: int
) -> str:
    """
    Injects critical rules at context boundaries.
    
    Strategy:
    - If context < 4000 tokens: No injection needed (rules visible)
    - If 4000-8000 tokens: Inject P1 rules at END
    - If >8000 tokens: Inject P1 rules at BEGINNING and END
    
    Returns: Modified context with rules pinned
    """
    
    rules = get_priority_1_rules()
    
    if context_length_tokens < 4000:
        return current_context  # No injection needed
    
    # Build injection text
    injection = build_rule_reminder(rules, exchange_number)
    
    if context_length_tokens < 8000:
        # Append at end
        return current_context + "\n\n" + injection
    else:
        # Sandwich: beginning + middle + end
        prefix = build_critical_reminder_prefix(rules)
        return prefix + "\n\n" + current_context + "\n\n" + injection
```

**Injection Format:**
```
[CRITICAL BEHAVIORAL CONSTRAINTS - Exchange #15]

You are approaching context limits. Re-anchor to core constraints:

1. P15 (Complete Before Claiming): Report "X/Y done (Z%)" not "✓ Done"
   - NEVER claim complete when subtasks remain
   - Current exchange: Verify ALL artifacts before reporting done

2. P5 (Safety): Check n5_protect.py before destructive operations
   
3. Persona Return: After specialized work, switch back to Operator
   - Current persona: [detect from SESSION_STATE]
   - Return protocol: [specific command]

[END CRITICAL CONSTRAINTS]
```

#### 1C. Violation Detector
**File:** `N5/scripts/violation_detector.py`

**Function:** Post-response analysis to detect rule violations

**Detection patterns:**
- P15 violations: Regex for "✓ Done", "Complete", "Finished" WITHOUT progress metrics
- Persona violations: Check SESSION_STATE persona tracking vs active persona
- Safety violations: Destructive operations without n5_protect.py calls

**On detection:**
1. Log to `rule_applications` table (`violated=1`)
2. Generate alert for V: "⚠️ Detected P15 violation - Zo claimed done without progress report"
3. Suggest correction: "Would you like me to verify actual completion status?"

---

### System 2: Diligence Tracking (Solves Completion Failures)

**What:** Structured work tracking that makes implicit task decomposition explicit

**How:** Work manifest system integrated with SESSION_STATE

**Components:**

#### 2A. Work Manifest Format
**File:** `SESSION_STATE.md` extension

**New section added:**
```markdown
## Work Tracking

### Current Task
**Objective:** [One-line goal]
**Started:** [exchange#]
**Estimated Subtasks:** [count]

### Subtask Breakdown
- [ ] 1. Subtask description (Assigned: [exchange#])
- [ ] 2. Another subtask
- [x] 3. Completed subtask (Done: [exchange#])
- [ ] 4. Future subtask

**Progress:** 1/4 complete (25%)

### Artifacts Created
| File | Purpose | Status | Created | Notes |
|------|---------|--------|---------|-------|
| script.py | Main logic | Complete | #12 | No placeholders |
| config.yaml | Settings | Partial | #13 | TODO: Add validation |

### Placeholders/TODOs
| Location | Description | Priority | Reason |
|----------|-------------|----------|--------|
| script.py:45 | Error handling | HIGH | Needs error taxonomy |
| config.yaml | Validation rules | MED | Waiting on requirements |

### Changes Made
| File | Change Type | Exchange | Description |
|------|-------------|----------|-------------|
| script.py | Created | #12 | Initial implementation |
| script.py | Modified | #14 | Added logging |

### Verification Checklist
Before claiming done, verify:
- [ ] All subtasks checked off
- [ ] All artifacts in "Complete" status
- [ ] No HIGH priority placeholders remain
- [ ] Changes table matches actual file state
- [ ] Fresh thread test passed (can V understand this?)
```

#### 2B. Task Decomposition Protocol

**Trigger:** Any request involving >1 file or >30 minutes estimated work

**Protocol:**
1. **Explicit decomposition** (don't proceed without this):
   ```
   Breaking this down into subtasks:
   1. [Subtask 1]
   2. [Subtask 2]
   3. [Subtask 3]
   
   Does this decomposition match your expectations? Any missing steps?
   ```

2. **Update Work Manifest** in SESSION_STATE.md

3. **Checkpoint after each subtask:**
   ```
   ✅ Subtask 1 complete (1/3 done, 33%)
   Moving to subtask 2: [description]
   ```

4. **Final verification** before claiming done:
   - Run self-verification script
   - Report actual vs expected state
   - Offer validation steps for V

#### 2C. Self-Verification Script
**File:** `N5/scripts/work_verifier.py`

**Function:** Automated checks before claiming "Done"

**Checks:**
```python
def verify_work_complete(session_state_path: str) -> Dict[str, Any]:
    """
    Verifies work actually complete before allowing claim.
    
    Returns:
        {
            'complete': bool,
            'progress': '13/23 (56%)',
            'blocking_issues': List[str],
            'artifacts_verified': bool,
            'placeholders_documented': bool
        }
    """
    
    # Parse Work Tracking section
    subtasks = parse_subtasks(session_state_path)
    artifacts = parse_artifacts(session_state_path)
    placeholders = parse_placeholders(session_state_path)
    
    blocking = []
    
    # Check 1: All subtasks complete?
    incomplete = [t for t in subtasks if not t['complete']]
    if incomplete:
        blocking.append(f"{len(incomplete)} subtasks incomplete")
    
    # Check 2: All artifacts in Complete status?
    partial = [a for a in artifacts if a['status'] != 'Complete']
    if partial:
        blocking.append(f"{len(partial)} artifacts partial/incomplete")
    
    # Check 3: High priority placeholders documented?
    high_pri = [p for p in placeholders if p['priority'] == 'HIGH']
    if high_pri:
        blocking.append(f"{len(high_pri)} HIGH priority TODOs remain")
    
    # Check 4: Artifacts actually exist?
    missing = []
    for artifact in artifacts:
        if not Path(artifact['file']).exists():
            missing.append(artifact['file'])
    if missing:
        blocking.append(f"Missing files: {missing}")
    
    complete = len(blocking) == 0
    progress = f"{len([t for t in subtasks if t['complete']])}/{len(subtasks)}"
    
    return {
        'complete': complete,
        'progress': progress,
        'blocking_issues': blocking,
        'artifacts_verified': len(missing) == 0,
        'placeholders_documented': len(high_pri) == 0 or all(p['reason'] for p in high_pri)
    }
```

**Integration:** Called automatically before any claim of completion

**Output format:**
```
⚠️ Work verification FAILED

Progress: 13/23 subtasks complete (56%)

Blocking issues:
- 10 subtasks incomplete
- 2 artifacts in Partial status
- 3 HIGH priority placeholders without resolution plan

Cannot claim "Done" until these resolved.

Next steps:
1. Complete remaining subtasks, OR
2. Explicitly defer incomplete work with rationale
```

#### 2D. Placeholder Documentation Standard

**Rule:** NO placeholder allowed without entry in Placeholders table

**Enforcement:**
- Pre-commit hook scans code for TODO/FIXME/PLACEHOLDER
- Validates each has entry in SESSION_STATE Placeholders table
- Blocks commit if undocumented placeholders found

**Example:**
```python
# ❌ WRONG - Undocumented placeholder
def process_data(input):
    # TODO: Add validation
    return transform(input)

# ✅ RIGHT - Documented in SESSION_STATE
def process_data(input):
    # PLACEHOLDER: Input validation (tracked in SESSION_STATE #23)
    # Reason: Waiting on validation rule spec from V
    # Priority: HIGH
    # Resolution: Will implement once requirements clear
    return transform(input)
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
**Builder creates:**
1. Critical rules database schema
2. Rule injection hook (basic version)
3. Work Manifest template in SESSION_STATE
4. Placeholder documentation standard

**Validation:**
- Test rule injection at 5K, 10K, 15K token conversations
- Verify Work Manifest updates correctly
- Check placeholder enforcement works

### Phase 2: Verification (Week 3-4)
**Builder creates:**
1. Work verifier script
2. Violation detector
3. Pre-commit hooks for placeholders
4. Artifact tracking automation

**Validation:**
- Simulate P15 violations, verify detection
- Test work verifier with partial work
- Verify artifact tracking catches missing files

### Phase 3: Integration (Week 5-6)
**Builder creates:**
1. Integration with Operator persona (routing logic)
2. Integration with session_state_manager.py
3. V-facing dashboards (violation reports, work status)
4. Documentation and examples

**Validation:**
- End-to-end test: Start complex task, track through completion
- Verify rule decay doesn't occur in 20+ exchange conversation
- Confirm diligence failures caught before claiming done

### Phase 4: Measurement (Week 7-8)
**Metrics to capture:**
1. Rule violations per conversation (target: <2%)
2. P15 compliance rate (target: >95%)
3. Work tracking accuracy (artifacts match reality target: >98%)
4. False positive rate on verifications (target: <10%)

**Dashboards:**
- Daily: Violation summary
- Weekly: Trend analysis (are we improving?)
- Per-conversation: Work tracking accuracy

---

## Success Criteria

### For Rule Decay Fix:
- ✅ P15 violations drop below 2% of conversations
- ✅ Persona switch failures drop below 1% of conversations
- ✅ Safety check skips drop to 0 (critical)
- ✅ Rule violation detection catches 95%+ of actual violations

### For Diligence Fix:
- ✅ No confabulated completions (measured via V feedback)
- ✅ Work Manifest accuracy >98% (artifacts listed = artifacts existing)
- ✅ Placeholder documentation compliance 100%
- ✅ V validation cycles drop from 2-3x to <1.5x average

### Overall:
- ✅ V reports increased confidence in Zo reliability
- ✅ Fewer "did you actually do X?" validation questions
- ✅ System feels like reliable partner, not probationary assistant

---

## Alternative Approaches Considered

### Alt 1: Fine-tuning model on V's rules
**Rejected because:**
- Expensive (requires training infrastructure)
- Slow iteration (weeks per experiment)
- Black box (can't debug why rules forgotten)
- Zo already knows rules; problem is attention not knowledge

### Alt 2: External validation agent (separate LLM checks Zo's work)
**Rejected because:**
- Adds latency (double API calls)
- Expensive (2x LLM costs)
- Complex orchestration
- Doesn't solve root cause (rule decay)

### Alt 3: Shorter context windows (force frequent summarization)
**Rejected because:**
- Loses conversation continuity
- Forces constant re-grounding
- Doesn't actually improve within-window attention
- Band-aid, not fix

**Why our approach wins:**
- Leverages known attention patterns (U-curve)
- Explicit tracking matches V's mental model
- Debuggable (can see violations in logs)
- Iteratively improvable (tune priorities, thresholds)

---

## Risks & Mitigations

### Risk 1: Rule injection adds cognitive overhead
**Mitigation:** Only inject when context >4K tokens. Keep injection minimal (<100 tokens).

### Risk 2: Work Manifest becomes tracking theater
**Mitigation:** Only activate for multi-step work (>1 file or >30min). Single commands skip it.

### Risk 3: False positives on violation detection
**Mitigation:** Log violations but don't block execution. V reviews logs, tunes thresholds.

### Risk 4: Placeholders proliferate instead of reducing
**Mitigation:** Require priority + reason + resolution plan. High-priority blocks claiming done.

---

## Questions for V

1. **Priority confirmation:** Are these still your top 2 failure modes? Any others more painful?

2. **Cognitive load trade-off:** How verbose should Work Manifest updates be? Every subtask or only milestones?

3. **Violation alerts:** Want real-time interruptions ("⚠️ Detected violation") or end-of-work summaries?

4. **Phase 1 vs all-at-once:** Prefer gradual rollout (Phase 1 → test → Phase 2) or build everything then test?

5. **Who reviews violations:** You, or should we build auto-correction ("Detected P15 violation, regenerating response with progress metrics")?

---

## Next Steps

**Decision point:** V approves architecture → Builder implements Phase 1

**Deliverables from Builder:**
1. Working critical_rules.db with initial Priority 1 rules
2. rule_injector.py (basic injection at boundaries)
3. SESSION_STATE.md template with Work Tracking section
4. Placeholder documentation guide

**Timeline:** Phase 1 completeable in 1-2 weeks, assuming no major design changes.

---

*Architect handoff to Builder: This is the blueprint. All mandatory components specified. Ready for implementation.*
