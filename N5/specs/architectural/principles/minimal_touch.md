# Principle 30: Minimal Touch Philosophy

**Category**: Operations  
**Priority**: High  
**Related**: P29 (Human-in-Loop), P25 (Automated Organization), ZT8 (Minimal Touch)

---

## Statement

Optimize for minimal human intervention in routine flows, not zero intervention. The goal is reduction of touch points to strategic decisions and exception handling only.

---

## Rationale

From Zero-Touch Principle 8: Goal isn't zero touch (impossible). Goal is minimal touch—reduce human interaction to approval of what matters most.

**Zero touch**: Fully autonomous (risky, no oversight)  
**Minimal touch**: Strategic checkpoints only (efficient + controlled)

---

## Touch Rate as System Metric

**Touch rate** = % of items requiring human routing decision

```python
touch_rate = items_manually_handled / total_items

Target: <15% (85% flow automatically)
```

**Interpretation**:
- <10%: Excellent automation
- 10-20%: Good automation
- 20-30%: Needs improvement
- >30%: Poor automation, mostly manual

---

## Implementation Pattern

### Pattern 1: Reduce Touch Points

Map current workflow, identify all human touch points:

```markdown
## Article Workflow - Current State

1. Save article → MANUAL (human decides to save)
2. Choose category → MANUAL (human picks folder)
3. Summarize → MANUAL (human reads + summarizes)
4. Decide keep/archive → MANUAL (human evaluates)
5. File in Knowledge → MANUAL (human moves file)

Touch points: 5 (100% manual)
```

Redesign to minimize:

```markdown
## Article Workflow - Minimal Touch

1. Save article → AUTO (one-click save, no decision)
2. Categorize → AUTO (AI determines category, confidence >85%)
3. Summarize → AUTO (AI summarizes overnight)
4. Review → MANUAL (human approves/rejects summary weekly)
5. File → AUTO (routing based on review decision)

Touch points: 1 (20% manual)
Touch rate improvement: 80%
```

### Pattern 2: Batch Touch Points

Don't interrupt for each decision—batch weekly:

```python
# ANTI-PATTERN: Real-time decisions
def process_article(article):
    summary = ai.summarize(article)
    
    # Interrupts user immediately
    keep = prompt("Keep this article? (y/n)")  
    if keep:
        category = prompt("Which category?")
        save(article, category)

# BETTER: Batch review
def process_article(article):
    summary = ai.summarize(article)
    auto_route(article, summary)  # No immediate prompt
    
    if confidence < 0.85:
        flag_for_weekly_review(article, summary)

def weekly_review():
    # Review all flagged items in one session
    flagged = get_review_queue()
    for item in flagged:
        # Quick approve/reject, efficient batch processing
        ...
```

### Pattern 3: Progressive Reduction

Track touch rate over time, set reduction goals:

```python
# Month 1: Establish baseline
baseline_touch_rate = measure_touch_rate()  # e.g., 45%

# Month 2: Automate highest-volume flows
automate_articles()  # Touch rate → 35%

# Month 3: Improve AI confidence
tune_thresholds()  # Touch rate → 25%

# Month 4: Add feedback loops
implement_learning()  # Touch rate → 18%

# Month 5: Optimize review process
batch_review_improvements()  # Touch rate → 12%

Goal: <15% within 6 months
```

---

## Key Insights

1. **Minimal ≠ Zero**: Some human touch is essential (judgment, exceptions). Goal is *minimal*, not *zero*.

2. **Touch points are expensive**: Each human decision costs time + context switch. Minimize ruthlessly.

3. **Batching is powerful**: 50 decisions in one 30min session >> 50 separate interruptions.

4. **Measure to improve**: If you don't track touch rate, you can't reduce it systematically.

---

## Anti-Patterns

❌ **Real-time prompts**: Interrupting work for each decision  
❌ **No touch tracking**: Can't tell if automation is improving  
❌ **Forced zero-touch**: Removing necessary human oversight  
❌ **All-or-nothing**: Either fully manual or fully automated (want: strategic touch)

---

## Success Criteria

Minimal touch is working when:
- [ ] Touch rate <15% (85% items flow automatically)
- [ ] Touch points are batched (weekly review, not real-time)
- [ ] Human time spent on judgment, not routing
- [ ] Touch rate decreasing over time (system learning)
- [ ] Can explain every remaining touch point (all are strategic)

---

## Related Principles

- **P29 (Human-in-Loop)**: Defines where human touch happens
- **P28 (AIR Pattern)**: Review stage is the primary touch point
- **P25 (Automated Organization)**: Automation reduces touch points
- **ZT8 (Minimal Touch)**: Philosophical foundation

---

*Added: 2025-10-24*  
*Source: Zero-Touch integration (ZT8)*