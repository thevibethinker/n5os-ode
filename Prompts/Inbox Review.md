---
description: Generate human-readable review document for Inbox files. Shows what's
tool: true
  pending, what needs attention, and provides routing suggestions.
tags: []
---
# inbox-review

**Category:** Reporting  
**Version:** 1.0.0  
**Created:** 2025-10-27

---

## Purpose

Generate human-readable review document for Inbox files. Shows what's pending, what needs attention, and provides routing suggestions.

---

## Prerequisites

- Analysis log exists: `N5/logs/.inbox_analysis.jsonl`
- Config exists: `file 'N5/config/routing_config.json'`

---

## Execution

```bash
python3 /home/workspace/N5/scripts/inbox_review_generator.py
```

**Dry-run mode:**
```bash
python3 /home/workspace/N5/scripts/inbox_review_generator.py --dry-run
```

---

## What It Does

1. Reads all unrouted analyses from log
2. Groups files by confidence level:
   - Auto-route ready (≥85%)
   - Suggested routing (60-84%)
   - Manual review needed (<60%)
3. Checks for TTL violations (>14 days in Inbox)
4. Generates `Inbox/REVIEW.md` with:
   - Summary statistics
   - TTL warnings
   - File listings by confidence
   - Usage instructions

---

## Success Criteria

- REVIEW.md generated successfully
- All unrouted files included
- Confidence levels accurate
- TTL warnings present if applicable
- Instructions clear and actionable

---

## Error Handling

- **Analysis log missing:** Creates empty review with warning
- **File missing:** Warns but continues
- **Write fails:** Logs error, returns non-zero exit code

---

## Output

**File:** `Inbox/REVIEW.md`

**Structure:**
```markdown
# Inbox Review
**Generated:** 2025-10-27 20:00 ET
**Total Items:** 12

## Summary
- Auto-route ready: 4 (≥85% confidence)
- Suggested routing: 5 (60-84% confidence)
- Manual review needed: 3 (<60% confidence)

## ⚠️ TTL Exceeded
[Files older than 14 days]

## ✅ Auto-Route Ready (High Confidence)
[High-confidence files that will auto-route]

## 💡 Suggested Routing (Medium Confidence)
[Medium-confidence files needing review]

## ❓ Manual Review Required (Low Confidence)
[Low-confidence files needing classification]

---
## How to Use This Review
[Instructions for processing]
```

---

## Integration

**Part of clearinghouse workflow:**
1. **cleanup-root** → Moves to Inbox/
2. **inbox-process** → Analyzes, routes, generates review
3. **inbox-review** (this command) → Regenerates review on-demand

**Scheduled:** As part of weekly inbox-process

**Manual:** Run anytime to see current Inbox status

---

## Use Cases

- **Weekly review:** See what needs attention
- **After manual routing:** Regenerate to see updated state
- **Health check:** Quick view of Inbox status
- **Before vacation:** Ensure nothing pending

---

## Related

- `file 'N5/commands/inbox-process.md'` - Full workflow
- `file 'N5/scripts/inbox_review_generator.py'` - Implementation
- `file 'N5/config/routing_config.json'` - Configuration
