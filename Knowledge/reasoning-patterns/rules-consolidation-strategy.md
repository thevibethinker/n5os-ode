---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
pattern_type: system-design
source: rules consolidation session, Level Upper analysis
provenance: con_6eWaWKe0VWWLg2Be
---

# Pattern: Rules Consolidation Strategy

## Summary

When a rules system grows beyond ~30 rules, consolidate by functional group rather than optimizing individual rules. The key insight is distinguishing between rules that should be always-on vs conditional, and grouping by workflow rather than by topic.

## The Insight

Rules in LLM-based systems are not code — they're behavioral instructions evaluated by attention. Consolidation helps not because of "efficiency" but because:
1. Fewer rules = less competition for attention
2. Always-on rules get stronger enforcement than conditional ones
3. A single routing table is more reliable than 7 separate switch rules
4. Related instructions in one rule are more likely to be applied together

## Key Decisions

- **Critical rules (persona switching) → always-on**: Conditional rules require the model to match the condition first, reducing salience
- **Group by workflow, not topic**: SMS commands together, build protocol together, agent lifecycle together
- **Preserve specificity**: Consolidated rules keep the same level of detail as originals — compression ≠ vagueness
- **Routing table format**: Tables in rules are effective because they're scannable and unambiguous

## When to Apply

- Rules count exceeds ~30 and growing
- Multiple rules address the same workflow from different angles
- Compliance with specific rules is inconsistent
- New rules keep getting added for the same domain

## Trade-offs

**Pros:**
- Fewer rules = less noise in system prompt
- Critical rules elevated to always-on
- Related behaviors co-located

**Cons:**
- Consolidated rules are longer — may be harder to edit incrementally
- Harder to toggle individual behaviors on/off
- Less modular for adding new behaviors

## Related

- enforcement-at-execution.md (enforce at executor, not router)
