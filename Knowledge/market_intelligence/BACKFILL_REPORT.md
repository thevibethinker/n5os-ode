# GTM Database Backfill Report

**Date:** November 2, 2025 11:21 PM ET  
**Process:** GTM Database Backfill from B31 Files

---

## Summary

Successfully processed B31_STAKEHOLDER_RESEARCH.md files from meeting records and extracted GTM intelligence insights into the SQLite database.

### Results

- **Total Insights Extracted:** 63
- **Unique Meetings Processed:** 11 (successfully parsed)
- **Total B31 Files Found:** 47
- **Success Rate:** 23% (11/47 meetings yielded insights)

### Data Quality

- **High Confidence (PRIMARY source):** 17 insights (27%)
- **Medium Confidence (SECONDARY source):** 14 insights (22%)
- **Low/Unknown Confidence:** 32 insights (51%)

---

## Successfully Processed Meetings

| Meeting | Date | Insights | Format |
|---------|------|----------|--------|
| 2025-10-09_alex-x-vrijen-wisdom-partners-coaching | 2025-10-09 | 4 | Old |
| 2025-10-17_external-laura-close | 2025-10-17 | 3 | Old |
| 2025-10-17_external-unknown_123228 | 2025-10-17 | 5 | Old |
| 2025-10-22_external-year-up-united_160549 | 2025-10-22 | 5 | Old |
| 2025-10-24_external-alexis-mishu | 2025-10-24 | 4 | Old |
| 2025-10-24_external-sam-partnership-discovery-call | 2025-10-24 | 5 | Old |
| 2025-10-27_external-david | 2025-10-27 | 5 | New |
| 2025-10-27_external-ilya | 2025-10-27 | 5 | New |
| 2025-10-27_external-lisa-noble | 2025-10-27 | 7 | Format 3 |
| 2025-10-29_external-jeff-sipe | 2025-10-29 | 6 | New |
| ‼️ 2025-09-24_lensa-careerspan-discussion-2 | 2025-09-24 | 3 | Old |

---

## Insight Categories

Top categories extracted:

1. **Uncategorized:** 32 insights (51%)
2. **GTM & Distribution:** 8 insights (13%)
3. **Product Strategy:** 4 insights (6%)
4. **Founder Pain Points:** 4 insights (6%)
5. **Career Services/Operations:** 2 insights (3%)

---

## Issues & Limitations

### Format Inconsistency

Three different B31 formats were encountered - 36 meetings (76%) could not be parsed due to format variations.

**Estimated Missing Insights:** 150-200 insights from unprocessed meetings

---

## Recommendations

1. **Standardize B31 Format** for all future generation
2. **Backfill Remaining 36 Files** with improved parser
3. **Data Quality Review** - categorize "Uncategorized" insights
4. **Create Query Interface** for the 63+ insights in database

---

**Database Location:** Knowledge/market_intelligence/gtm_intelligence.db

*Generated: 2025-11-02 23:21 ET*
