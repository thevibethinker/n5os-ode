# Principle 26: Maintenance-First Design

**Category**: Design  
**Priority**: High  
**Related**: P14 (Change Tracking), ZT4 (Maintenance > Organization)

---

## Statement

Design for continuous maintenance, not one-time organization. Systems should include regular review rhythms, health checks, and self-assessment as first-class components, not afterthoughts.

---

## Rationale

From Zero-Touch Principle 4: You can't organize your way to productivity. Build systems that maintain themselves with you as quality control.

**Organization = Static**: One-time event, creates structure, decays over time  
**Maintenance = Dynamic**: Continuous process, adapts to change, improves over time

Most systems are designed for initial setup, then maintained as afterthought. This is backwards. Maintenance is the actual work—setup is just scaffolding.

---

## Core Concepts

### Review Rhythms

Three cadences, progressively zooming out:

| Cadence | Duration | Focus | Automation |
|---------|----------|-------|------------|
| Daily | 5 min | "What broke today?" | Mostly automated, human spot-checks |
| Weekly | 30 min | "What's pooling? What's stuck?" | Human reviews AI-flagged items |
| Monthly | 2 hrs | "Is the system working? What needs redesign?" | Human evaluates system-wide metrics |

**Key insight**: These aren't optional. They're *the system*.

### Health Checks as Infrastructure

```bash
# Automated daily health check (runs at 2am)
n5 health-check --daily

Checks:
- Files created but empty? → Flag
- Uncommitted changes >24hr? → Warn
- Pool thresholds exceeded? → Alert
- Stale list items >30d? → Surface
- Missing expected outputs? → Log

Output: health_check_2025-10-24.log + notify if warnings
```

### Build Review Muscle

The more you review, the faster it gets:
- **Week 1**: 30min weekly review
- **Month 3**: 15min weekly review (system highlights only issues)
- **Month 6**: 10min weekly review (most issues auto-resolved)

You're not doing *more* work—you're getting *better* at spotting patterns.

---

## Implementation Patterns

### Pattern 1: Scheduled Review Workflows

```python
# weekly_review.py

def weekly_review():
    """Human-in-loop weekly maintenance."""
    
    print("=== N5 Weekly Review ===\n")
    
    # 1. Pool warnings
    pools = check_all_pools()
    if pools:
        print(f"⚠️  {len(pools)} items pooling:")
        for item in pools:
            print(f"  - {item['path']} ({item['age_days']} days old)")
            action = prompt("Keep/Archive/Delete/Defer?")
            handle_pool_item(item, action)
    
    # 2. Flagged items (low-confidence auto-routes)
    flagged = get_review_queue()
    if flagged:
        print(f"\n📋 {len(flagged)} items flagged for review:")
        for item in flagged:
            show_summary(item)
            decision = prompt("Correct routing? (y/n/edit)")
            if decision == 'n':
                new_route = prompt("Correct destination:")
                move_and_learn(item, new_route)
    
    # 3. Stale lists
    stale = find_stale_list_items(days=30)
    if stale:
        print(f"\n⏰ {len(stale)} stale action items:")
        review_stale_items(stale)
    
    # 4. System health summary
    print("\n📊 System Health:")
    print(f"  - Knowledge items: {count_knowledge_items()}")
    print(f"  - Active lists: {count_active_lists()}")
    print(f"  - Avg intake->output time: {avg_flow_time()} days")
    print(f"  - Touch rate this week: {calculate_touch_rate()}%")
    
    print("\n✅ Weekly review complete!")
```

### Pattern 2: Self-Assessment Metrics

System tracks its own health:

```python
# System health score (0-100)
def calculate_health_score():
    score = 100
    
    # Deduct for pools
    pools = count_pools()
    score -= min(pools * 5, 30)  # Max -30 for pools
    
    # Deduct for high touch rate
    touch_rate = get_touch_rate()
    if touch_rate > 0.20:  # >20% manual routing
        score -= (touch_rate - 0.20) * 100  # Penalty for excess
    
    # Deduct for slow flows
    avg_flow_time = get_avg_flow_time_days()
    if avg_flow_time > 10:
        score -= (avg_flow_time - 10) * 2
    
    # Deduct for stale items
    stale_count = count_stale_items()
    score -= min(stale_count * 2, 20)
    
    return max(score, 0)  # Floor at 0
```

Display in daily health check:
```
System Health Score: 87/100
  - Pools: -5 (1 warning)
  - Touch rate: -3 (18% this week)
  - Flow speed: -5 (avg 12 days)
  - Stale items: 0
```

### Pattern 3: Maintenance Commands

Make maintenance easy to trigger:

```bash
# Daily (quick check)
n5 health-check --daily

# Weekly (interactive review)
n5 review --weekly

# Monthly (full audit)
n5 audit --full

# On-demand (specific concern)
n5 check-pools
n5 check-stale
n5 check-git
```

All return actionable output, not just status.

---

## Key Insights

1. **Maintenance is the product**: The system *is* the maintenance loops, not the folder structure.

2. **High frequency, low duration**: 5min daily >> 1hr monthly. Frequent light touch prevents problems.

3. **Automated detection, human judgment**: System flags issues, human decides response.

4. **Metrics drive improvement**: Can't improve what you don't measure. Track touch rate, flow time, pool count.

---

## Anti-Patterns

❌ **No scheduled reviews**: "I'll review when I have time" → never happens  
❌ **Manual health checks**: Remembering to check for issues → misses 90% of problems  
❌ **One-size-fits-all review**: Same process for daily/weekly/monthly → inefficient  
❌ **Maintenance as reaction**: Only fix things when broken → too late

---

## Testing

### Test 1: Skip Review for 1 Month

Deliberately skip reviews for 30 days:
- How many pools form?
- How many issues go undetected?
- How long does it take to recover?

This proves maintenance value.

### Test 2: Time Review Cadences

Track actual time spent:
- Daily: Should be <5min
- Weekly: Should trend downward (30 → 15 → 10min as system improves)
- Monthly: Should be mostly metrics review, not firefighting

### Test 3: Measure System Health Trend

Track health score over 12 weeks:
- Should trend upward as maintenance loops tune system
- Dips indicate new issues to address
- Flat trend might indicate missing maintenance loops

---

## Success Criteria

Maintenance-first design is working when:
- [ ] Review times decrease over time (system learns, less human intervention)
- [ ] Health checks run automatically daily without human trigger
- [ ] Issues are detected before they impact work (proactive, not reactive)
- [ ] System health score trends upward or stays high (>85)
- [ ] New maintenance needs are identified and added to loops
- [ ] Maintenance feels like steering, not firefighting

---

## Migration Path

If you're starting from scratch or have no maintenance:

**Week 1**: Add daily health check (automated)  
**Week 2**: Add weekly review (30min, manual)  
**Week 4**: Track metrics (touch rate, pools, flow time)  
**Week 8**: Optimize review (reduce duration via better filtering)  
**Week 12**: Add monthly audit (system-wide evaluation)

Don't try to build all loops at once. Start with daily health check, add weekly review, refine from there.

---

## Related Principles

- **P14 (Change Tracking)**: Maintenance requires knowing what changed
- **P11 (Failure Modes)**: Maintenance detects failures early
- **P18 (State Verification)**: Maintenance checks state is correct
- **P24 (Information Flow)**: Maintenance ensures flows stay open
- **ZT4 (Maintenance > Organization)**: Philosophical foundation

---

*Added: 2025-10-24*  
*Source: Zero-Touch integration (ZT4)*