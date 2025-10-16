# Aggregate B31 Insights Command

**Command ID:** `aggregate-insights`  
**Version:** 1.0  
**Created:** 2025-10-13

---

## Purpose

Incrementally aggregate B31 stakeholder research insights across meetings to detect patterns, validate signals, and identify opportunities.

---

## Usage

```bash
# Process a new meeting's B31 insights
python3 N5/scripts/aggregate_b31_insights.py --meeting-id [meeting-folder-name]

# Dry run (see what would happen)
python3 N5/scripts/aggregate_b31_insights.py --meeting-id [meeting-folder-name] --dry-run

# Full rebuild (rare - only for fresh start)
python3 N5/scripts/aggregate_b31_insights.py --full-rebuild
```

---

## How It Works

### Incremental Aggregation (Recommended)

1. **Extract insights** from new meeting's B31 file
2. **Load existing** aggregated_insights.md
3. **Generate update instruction** for LLM:
   - Cross-reference new insights with existing
   - Identify confirmations, contradictions, new patterns
   - Determine signal strength promotions
   - Compact when 5+ similar insights exist
4. **LLM updates** aggregated doc (small context window)
5. **Save updated** aggregated_insights.md

**Context efficiency:** Only loads existing doc + new B31 (~20k tokens max)

### Signal Strength Levels

- **Strong Signals** (≥3 primary sources): Act now
- **Emerging Signals** (2 primary sources): Validate & act
- **Single-Source** (1 high-quality source): Monitor
- **Contradictions**: Surface disagreements between primary sources

### Compaction Trigger

When 5+ insights say similar things → Compact into one consolidated insight:
- "[X] operators confirm: [Pattern]"
- Lists all sources with credibility ratings
- Preserves unique nuances in sub-bullets

---

## Source Credibility Weighting

**Primary Source (Weight: 1.0)**
- Firsthand operational experience on exact topic
- Example: Hamoon on embedded career tech solutions (he's built them)

**Secondary Source (Weight: 0.5)**
- Informed perspective but not direct experience
- Example: Consultant sharing client patterns

**Speculative (Weight: 0.25)**
- Intelligent hypothesis, no direct evidence
- Example: Future predictions, cross-industry analogies

**Signal promotion requires PRIMARY sources:**
- 1 primary → Single-Source
- 2 primary → Emerging Signal
- 3+ primary → Strong Signal

---

## Output Location

**Aggregated File:** `Knowledge/market_intelligence/aggregated_insights.md`

**Update Instructions:** `Knowledge/market_intelligence/update_instruction_[meeting-id].txt`

---

## Integration with B08 & CRM

After aggregation validates insights:

1. **Update B08** with validation status
2. **Sync to CRM** with track record:
   - Total insights: N
   - Validated: X (percentage%)
   - Strong performers: [List]

```bash
# After aggregation, sync validation results back
python3 N5/scripts/sync_b08_to_crm.py --meeting-id [meeting-id]
```

---

## Typical Workflow

```bash
# 1. Meeting processed → B31 generated
# 2. Aggregate new insights
python3 N5/scripts/aggregate_b31_insights.py --meeting-id 2025-10-13_hamoon-ekhtiari-futurefit

# 3. Review update instruction
cat Knowledge/market_intelligence/update_instruction_2025-10-13_hamoon-ekhtiari-futurefit.txt

# 4. [LLM processes instruction] → Updates aggregated_insights.md

# 5. Sync validation results to CRM
python3 N5/scripts/sync_b08_to_crm.py

# 6. Review aggregated intelligence
cat Knowledge/market_intelligence/aggregated_insights.md
```

---

## Full Rebuild (Rare)

Only use when:
- Starting fresh
- Fixing corruption
- Major restructuring

**Warning:** Requires processing ALL B31 files through LLM at once (large context).

```bash
python3 N5/scripts/aggregate_b31_insights.py --full-rebuild --dry-run
```

---

## Principles

**P2 (SSOT):** `aggregated_insights.md` is source of truth for validated insights  
**P7 (Dry-Run):** Always available via `--dry-run` flag  
**P15 (Complete Before Claiming):** Script generates instruction; LLM must complete update  
**P18 (Verify State):** Check aggregated file after update  

---

## Future Automation

Once validated, can automate:
- Run after every meeting processing
- Automatic LLM call to update doc
- Automatic CRM sync of validation results
- Weekly summary of new strong signals

---

**Maintained by:** Zo (Vibe Builder)  
**Last Updated:** 2025-10-13
