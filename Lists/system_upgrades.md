---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# N5 System Upgrades Backlog

## Purpose
Tracking future improvements to Zo's agentic reliability and operational capabilities.

---

## Tier 1: High-Impact, Lower Effort (Priority)

### ✓ COMPLETED
- [x] Confidence Calibration - Explicit uncertainty reporting
- [x] Attention-Optimized Context Structure - Blueprint for platform integration
- [x] Pre-Flight Check System - Automatic request verification

### REMAINING

#### 1. Automatic Reminder Injection (System-Level)
**Status:** Planned  
**Effort:** 3-5 days  
**Priority:** High  
**Depends on:** Platform access for middleware hooks

**Description:**  
Move from manual reminder injection (Operator discipline) to automatic system-level injection at conversation boundaries.

**Implementation:**
- Platform middleware hook
- Auto-inject critical reminders every 5-8 exchanges when >8K tokens
- No reliance on Operator memory

**Files:**
- Platform-level ConversationMiddleware
- Integration with existing inject_reminders.py

---

#### 2. Intent Verification Protocol
**Status:** Planned  
**Effort:** 1 week  
**Priority:** High  

**Description:**  
Mandatory intent check for ambiguous/multi-step work. Forces explicit confirmation of interpretation before acting.

**Example:**
```
User: "Delete meetings"
Zo: ⚠️ INTENT VERIFICATION
    I interpret: Delete database records in meetings table
    OR did you mean:
    - Delete Google Calendar events?
    - Archive meeting files?
    Please confirm.
```

**Integration:** Part of pre_flight_check.py enhancement

---

#### 3. Ambiguity Detection Database Enhancement
**Status:** Planned  
**Effort:** 3 days  
**Priority:** High  

**Description:**  
Expand ambiguous patterns database from 6 terms to 20-30 common patterns.

**Categories to add:**
- Data operations (import, export, sync, migrate)
- Code operations (refactor, restructure, rewrite)
- Status changes (enable, disable, toggle, activate)
- Quantity specifiers (some, many, few, several)

**Files:**
- Enhance N5/scripts/pre_flight_check.py AMBIGUOUS_PATTERNS

---

## Tier 2: High-Impact, Higher Effort

#### 4. Rule Violation Tracking & Learning
**Status:** Planned  
**Effort:** 1 week  
**Priority:** Medium  

**Description:**  
Track which rules Zo violates most, learn patterns, adapt reinforcement.

**Capabilities:**
- Log violations with context
- Generate violation stats
- Adjust reminder frequency based on violation rate
- Identify V-specific patterns

**Files:**
- N5/scripts/rule_violation_tracker.py
- N5/data/violations.db

**Benefits:**
- Learn Zo's failure modes
- Adapt system to address most common issues
- Measure improvement over time

---

#### 5. Hierarchical Context Compression
**Status:** Planned  
**Effort:** 2 weeks  
**Priority:** Medium  
**Depends on:** Platform integration capabilities

**Description:**  
Intelligent summarization of middle conversation context to maintain critical info while reducing tokens.

**Strategy:**
- Keep beginning (first 5 exchanges) verbatim
- Compress middle hierarchically (decisions, work done, threads)
- Keep recent (last 8 exchanges) verbatim
- Maintains U-shaped attention optimization

**Benefits:**
- Supports very long conversations (>50K tokens)
- Preserves goal retention
- Reduces context confusion

---

#### 6. Technical Decision Framework
**Status:** Planned  
**Effort:** 1 week  
**Priority:** Medium  

**Description:**  
Structured protocol for evaluating and pushing back on technical decisions.

**Process:**
1. Understand goal & constraints
2. Evaluate proposed approach
3. Identify alternatives
4. Assess trade-offs
5. Communicate (proceed/push back/options)

**Triggers:**
- Architecture decisions
- Technology choices
- Optimization strategies
- Refactoring approaches

**Files:**
- N5/prefs/system/technical_decision_framework.yaml

---

## Tier 3: Architectural Enhancements

#### 7. Pre-Response Validation Layer
**Status:** Planned  
**Effort:** 2-3 weeks  
**Priority:** Low  
**Depends on:** Platform access

**Description:**  
Validate responses BEFORE sending to user. Physically prevent rule violations.

**Checks:**
- P15 compliance (progress metrics required)
- Placeholder documentation
- Confidence calibration
- Completion criteria validation

**Integration:** Platform-level middleware (response interceptor)

**Impact:** Zero rule violations (enforced, not voluntary)

---

#### 8. Cross-Conversation Learning
**Status:** Planned  
**Effort:** 2-3 weeks  
**Priority:** Low  

**Description:**  
Track patterns across conversations, build V-specific heuristics.

**Capabilities:**
- Pattern tracking ("When V says X, he means Y")
- Outcome learning ("Approach A worked better than B for task X")
- Personalization ("V prefers simple over complex")

**Files:**
- N5/scripts/pattern_learner.py
- N5/data/patterns.db

---

#### 9. Metrics Dashboard
**Status:** Planned  
**Effort:** 1-2 weeks  
**Priority:** Low  

**Description:**  
Automated tracking and visualization of agentic reliability metrics.

**Metrics tracked:**
- P15 compliance rate
- Confabulation rate
- Thread documentation completeness
- Placeholder tracking accuracy
- Persona return compliance
- Rule violation breakdown
- Confidence calibration accuracy

**Output:** Weekly/monthly summary reports

**Files:**
- N5/scripts/metrics_dashboard.py

---

#### 10. Refusal Brevity Training
**Status:** Planned  
**Effort:** 1 day  
**Priority:** Low  

**Description:**  
Train brief, non-apologetic refusal patterns.

**Current:**
```
"I appreciate your request, however I must respectfully 
decline as this would violate..."
(~50 words)
```

**Target:**
```
"I can't provide that information."
(5 words)
```

**Implementation:** Add to critical_reminders.txt

---

## Implementation Phases

### Phase 3 ✓ COMPLETE
- Confidence calibration
- Attention-optimized context structure
- Pre-flight check system

### Phase 4 (Next: 2-3 weeks)
- Automatic reminder injection
- Intent verification protocol
- Ambiguity database enhancement

### Phase 5 (Future: 1-2 months)
- Rule violation tracking
- Hierarchical context compression
- Technical decision framework

### Phase 6 (Future: 2-3 months)
- Pre-response validation
- Cross-conversation learning
- Metrics dashboard

---

## Priority Matrix

| Item | Impact | Effort | Priority | Phase |
|------|--------|--------|----------|-------|
| Confidence calibration | High | Low | P0 | 3 ✓ |
| Context optimization | High | Low | P0 | 3 ✓ |
| Pre-flight checks | High | Low | P0 | 3 ✓ |
| Auto reminder injection | High | Medium | P1 | 4 |
| Intent verification | High | Medium | P1 | 4 |
| Ambiguity DB expansion | High | Low | P1 | 4 |
| Violation tracking | Medium | Medium | P2 | 5 |
| Context compression | Medium | High | P2 | 5 |
| Tech decision framework | Medium | Medium | P2 | 5 |
| Response validation | High | High | P3 | 6 |
| Cross-convo learning | Low | High | P3 | 6 |
| Metrics dashboard | Low | Medium | P3 | 6 |
| Refusal brevity | Low | Low | P4 | Any |

---

## Success Metrics

Track improvements over time:

**Baseline (Current):**
- P15 compliance: ~70%
- Confabulation rate: ~15%
- Thread completeness: ~60%
- Rule adherence >8K tokens: ~50%

**Target (After Phase 6):**
- P15 compliance: >95%
- Confabulation rate: <2%
- Thread completeness: >90%
- Rule adherence >8K tokens: >85%

---

## Version History

**2025-11-03** - v1.0 - Initial backlog (10 items from roadmap)

## References

- file 'agentic_reliability_roadmap.md' (full analysis)
- file 'PHASE_2_COMPLETE.md' (current state)
