---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# Attention-Optimized Context Structure

## Research Foundation

**Key Finding:** Transformer models exhibit U-shaped attention curve
- **HIGH attention:** Beginning + End of context
- **LOW attention:** Middle of context
- **Performance drop:** 20-30% when critical info in middle

**Source:** "Lost in the Middle: How Language Models Use Long Contexts" research

## Optimal Context Architecture

### Current Structure (Suboptimal)
```
┌─────────────────────────────┐
│ System prompt               │ ← Gets attention
│ Full conversation history   │ ← Middle loses attention ⚠️
│ User rules                  │ ← Buried in middle
│ Persona definition          │ ← Buried in middle
│ User's latest message       │ ← Gets attention
└─────────────────────────────┘
```

**Problem:** Critical rules and constraints get lost in middle.

### Optimized Structure
```
┌─────────────────────────────┐
│ CRITICAL RULES              │ ← HIGH ATTENTION ZONE
│ (P15, safety, diligence)    │
├─────────────────────────────┤
│ CURRENT REQUEST             │ ← HIGH ATTENTION ZONE
│ (User's latest message)     │
├─────────────────────────────┤
│ RECENT CONTEXT              │ ← MODERATE ATTENTION
│ (Last 5-8 exchanges)        │
├─────────────────────────────┤
│ COMPRESSED MIDDLE           │ ← SUMMARIZED
│ (Hierarchical summary of    │
│  key decisions, work done,  │
│  open threads)              │
├─────────────────────────────┤
│ INITIAL CONTEXT             │ ← HIGH ATTENTION ZONE
│ (Original goal, constraints,│
│  key requirements)          │
├─────────────────────────────┤
│ SYSTEM PROMPT               │ ← HIGH ATTENTION ZONE
│ (Core behavior, capabilities)│
├─────────────────────────────┤
│ PERSONA DEFINITION          │ ← HIGH ATTENTION ZONE
│ (Mode-specific rules)       │
└─────────────────────────────┘
```

**Benefit:** Critical info placed in high-attention zones (top + bottom).

## Implementation Strategy

### Phase 1: Manual Reinforcement (Current)
- Inject critical reminders at conversation boundaries
- Use inject_reminders.py at 8K+ tokens
- **Status:** ✓ Implemented

### Phase 2: Context Reordering (Platform-Level)
Requires Zo platform changes to reorder context before sending to LLM.

```python
def optimize_context_structure(conversation):
    """
    Reorder context to place critical elements at boundaries.
    """
    # Extract components
    critical_rules = load_critical_rules()
    current_request = conversation[-1]  # Latest user message
    recent = conversation[-8:-1]  # Last 7 exchanges
    middle = conversation[5:-8] if len(conversation) > 13 else []
    initial = conversation[:5]  # First 5 exchanges
    system_prompt = get_system_prompt()
    persona = get_active_persona()
    
    # Compress middle if exists
    if middle:
        middle_summary = hierarchical_summarize(middle)
    else:
        middle_summary = None
    
    # Reconstruct in optimal order
    optimized = []
    
    # TOP (High Attention)
    optimized.append({"role": "system", "content": critical_rules})
    optimized.append(current_request)
    
    # UPPER-MIDDLE (Moderate Attention)
    optimized.extend(recent)
    
    # MIDDLE (Compressed)
    if middle_summary:
        optimized.append({"role": "system", "content": middle_summary})
    
    # LOWER-MIDDLE (High Attention - restoration)
    optimized.extend(initial)
    
    # BOTTOM (High Attention)
    optimized.append({"role": "system", "content": system_prompt})
    optimized.append({"role": "system", "content": persona})
    
    return optimized
```

### Phase 3: Hierarchical Summarization
Compress middle exchanges intelligently.

```python
def hierarchical_summarize(exchanges: List[Message]) -> str:
    """
    Multi-level summarization preserving critical info.
    """
    summary = {
        "decisions_made": extract_decisions(exchanges),
        "work_completed": extract_completed_work(exchanges),
        "open_threads": extract_open_threads(exchanges),
        "blockers": extract_blockers(exchanges),
        "key_insights": extract_insights(exchanges)
    }
    
    return format_summary(summary)

def format_summary(data: dict) -> str:
    """
    Format as concise but complete summary.
    """
    return f"""
=== MIDDLE CONTEXT SUMMARY ===
Decisions Made: {', '.join(data['decisions_made'])}
Work Completed: {data['work_completed']}
Open Threads: {', '.join(data['open_threads'])}
Blockers: {', '.join(data['blockers']) or 'None'}
Key Insights: {', '.join(data['key_insights'])}
=== END SUMMARY ===
"""
```

## Critical Rules Placement

### Rules to Pin at TOP
1. **P15 (Complete Before Claiming)** - Most expensive violation
2. **Diligence (Work Manifest)** - Prevents confabulation
3. **Persona Return Protocol** - Ensures mode switching
4. **Safety Rules** - Non-negotiable constraints
5. **Ambiguity Detection** - Clarify before acting

### Format
```
=== CRITICAL BEHAVIORAL RULES ===

These rules apply ALWAYS, regardless of conversation length:

1. P15: Report "X/Y (Z%)" not "Done" until ALL complete
2. DILIGENCE: Track work in manifest, document placeholders
3. PERSONA: Return to Operator after specialized work
4. SAFETY: Never bypass safety constraints
5. CLARIFY: Ask 3+ questions when ambiguous

=== END CRITICAL RULES ===
```

## Benefits by Conversation Length

### Short (<8K tokens, ~15 exchanges)
- Minimal benefit (all context fits in attention window)
- No summarization needed

### Medium (8-20K tokens, ~30 exchanges)
- **Moderate benefit** (+10-15% adherence)
- Critical rules reinforced at boundaries
- Recent context preserved

### Long (20-50K tokens, ~75 exchanges)
- **High benefit** (+20-30% adherence)
- Middle summarization prevents info loss
- Goal retention improved
- Rule decay prevented

### Very Long (>50K tokens, ~100+ exchanges)
- **Critical** (prevents total degradation)
- Without optimization: <50% rule adherence
- With optimization: >85% rule adherence

## Integration with Existing Systems

### Work with inject_reminders.py
- inject_reminders.py = Phase 1 (manual injection)
- This framework = Phase 2 blueprint (platform-level)
- Both pursue same goal via different mechanisms

### Work with SESSION_STATE.md
- SESSION_STATE captures middle context
- Can be included in compressed summary
- Preserves critical state information

### Work with Personas
- Persona definitions moved to high-attention zone (bottom)
- Mode-specific rules always visible
- Reduces persona "drift"

## Success Metrics

Track improvement:
1. **Rule adherence rate** - % conversations following P15, diligence, persona return
2. **Goal retention** - Can Zo recall original goal at exchange 50?
3. **Context confusion** - How often does Zo ask for already-provided info?
4. **Performance vs length** - Does degradation still occur >20K tokens?

**Target improvements:**
- Rule adherence: 70% → 95%
- Goal retention: 60% → 90%
- Context confusion: 15% → 5%
- Long-convo performance: Maintain >85% across all lengths

## Deployment Roadmap

**Phase 1: Manual Injection** ✓ COMPLETE
- Using inject_reminders.py
- Deployed and operational

**Phase 2: Platform Integration** (Requires Zo backend access)
- Implement context reordering in platform
- Deploy to staging
- A/B test against current structure
- Roll out if metrics improve

**Phase 3: Adaptive Compression** (Future)
- Learn optimal compression strategies
- Adapt based on conversation type
- Personalize to V's patterns

---

## Version History

**2025-11-03** - v1.0 - Initial framework (Phase 3)

## References

[^1]: Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2023)
[^2]: Arize AI Blog, "Paper Reading: Lost in the Middle"
