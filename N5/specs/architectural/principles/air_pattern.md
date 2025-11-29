# Principle 28: Assess-Intervene-Review Pattern (AIR)

**Category**: Operations  
**Priority**: Critical  
**Related**: P29 (Human-in-Loop), ZT7 (AIR Pattern)

---

## Statement

Every information intake should follow the AIR pattern: Assess (categorize/route), Intervene (transform/act), Review (confirm/correct). Automate Assess and Intervene; keep humans in control of Review.

---

## Rationale

From Zero-Touch Principle 7: Information processing has three natural stages. Humans are terrible at first two (repetitive, pattern-matching) and essential for third (judgment, correction).

**Old way**: Human does all three stages → bottleneck, cognitive load  
**AIR way**: AI does Assess + Intervene, human Reviews → efficiency, quality

---

## The Three Stages

### Assess: What is this and where should it go?

**AI responsibilities**:
- Content analysis (what is this about?)
- Category determination (business/personal/idea/reference)
- Urgency evaluation (needs immediate attention?)
- Relationship detection (connects to existing work?)
- Confidence scoring (how certain am I?)

### Intervene: What needs to happen to this?

**AI responsibilities**:
- Transformation (summarize, extract, format)
- Enrichment (add metadata, tags, timestamps)
- Action extraction (pull out tasks, decisions, questions)
- Routing (move to assessed destination)
- Flagging (mark for review if confidence < threshold)

### Review: Is this correct?

**Human responsibilities**:
- Verify AI decisions (routing correct?)
- Provide corrections (move if wrong)
- Approve actions (tasks extracted accurately?)
- Give feedback (teach system)

---

## Confidence Thresholds

Not everything needs Review. Use confidence to filter:

| Confidence | Action | Expected % |
|------------|--------|------------|
| >90% | Auto-complete, no review | 70-80% |
| 80-90% | Complete, flag for spot-check | 15-20% |
| 70-80% | Complete, flag for review | 5-10% |
| <70% | Hold for mandatory review | <5% |

**Tune thresholds** based on correction rate.

---

## Key Insights

1. **Not all items need Review**: High-confidence operations should auto-complete. Review is for exceptions.

2. **Review is batch, not real-time**: Don't review every item as it comes in. Batch review weekly for efficiency.

3. **Feedback loop is critical**: When you correct AI, system learns. Corrections make future Assessments better.

4. **Confidence calibration**: Start conservative (high threshold), become aggressive as system proves reliable.

---

## Success Criteria

AIR pattern is working when:
- [ ] 80%+ of items auto-complete without human review
- [ ] Correction rate <5% (AI decisions mostly correct)
- [ ] Review time <30min weekly for 50-100 items
- [ ] System learning visible (fewer corrections over time)

---

## Related Principles

- **P29 (Human-in-Loop)**: Review stage defines human role
- **P25 (Automated Organization)**: Assess determines routing
- **P24 (Information Flow)**: AIR implements flow stages
- **ZT7 (AIR Pattern)**: Philosophical foundation

---

*Added: 2025-10-24*  
*Source: Zero-Touch integration (ZT7)*