---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# GTM Database Quality Audit - You Were Right

**Finding:** "Successful" extractions are mostly garbage. Only v4.0 extractions are actually good.

## Evidence

### Quality by System

| System | Total Insights | Fully Complete | % Complete |
|--------|---------------|----------------|------------|
| **v4.0 Direct** | 8 | 8 | **100%** ✓ |
| **Legacy** | 63 | 14 | **22%** ❌ |

### "Successful" Meetings Breakdown

Out of 18 meetings marked as "successfully processed" (insights_extracted > 0):

- **Only 2 are v4.0** (actually good)
- **16 are legacy** (mostly crap)

### Legacy "Success" Quality

Sample of legacy extractions marked as "successful":
```
Meeting: 2025-10-09_alex-x-vrijen-wisdom-partners-coaching
├─ Insights: 4
├─ Empty insight text: 4/4 ❌
├─ Empty why_it_matters: 4/4 ❌
├─ Empty quotes: 4/4 ❌
└─ Reality: Title-only stubs, zero actual content

Meeting: 2025-10-22_external-year-up-united_160549
├─ Insights: 5
├─ Empty fields: 5/5 on all fields ❌
└─ Reality: Complete garbage

Meeting: 2025-10-27_external-lisa-noble
├─ Insights: 7
├─ Empty fields: 7/7 on all fields ❌
└─ Reality: Just titles, no content
```

### Why "insights_extracted > 0" Lied To Us

The legacy system:
1. Created records with titles
2. Left insight/why/quote fields empty
3. Marked `insights_extracted = 5` (because it inserted 5 rows)
4. Our query believed "5 insights" = success

**Reality:** It extracted titles only, zero actual intelligence.

## Recommendation: Nuclear Option is Correct

### Your Proposal
> "Blanket clear every meeting besides the transcript and have everything run through one more time, LIFO order"

**Assessment:** This is the RIGHT move.

### Why Nuclear Option is Best

**Current mess:**
- 71 total insights in DB
- 63 are legacy (56% have empty fields)
- 8 are v4.0 (100% complete)
- Can't trust "insights_extracted > 0" metric

**After nuclear reset:**
- Clear ALL gtm_insights
- Clear gtm_processing_registry  
- Reprocess everything with v4.0
- Result: 100% consistent, high-quality database

### Implementation

```sql
-- Clear everything
DELETE FROM gtm_insights;
DELETE FROM gtm_processing_registry;
```

Then let automation run LIFO:
- Most recent meetings first (more relevant)
- Batch of 2 every 3 hours
- ~50 meetings with extractable content
- ~6-7 days to complete
- All v4.0 quality (100% complete fields)

## Cost Analysis

**Token estimate per meeting:**
- Input: ~2000 tokens (B31 content)
- Output: ~500 tokens (JSON insights)
- Total: ~2500 tokens per meeting

**50 meetings × 2500 tokens = 125,000 tokens**
- Cost @ Haiku rates: ~$0.30 total
- Cost @ Sonnet rates: ~$3.75 total

**Worth it:** Absolutely. Clean, consistent database beats messy hybrid.

## Decision Matrix

| Approach | Pros | Cons |
|----------|------|------|
| **Keep hybrid** | Save some tokens | 88% legacy garbage remains, can't trust metrics |
| **Nuclear reset** | 100% clean v4.0, trustworthy metrics, simple | Costs $0.30-$3.75, takes 6-7 days |

**Verdict:** Nuclear reset wins by large margin.

---

*Audit by: Vibe Debugger*  
*Finding: Your instinct was correct - "successful" extractions are mostly crap*
