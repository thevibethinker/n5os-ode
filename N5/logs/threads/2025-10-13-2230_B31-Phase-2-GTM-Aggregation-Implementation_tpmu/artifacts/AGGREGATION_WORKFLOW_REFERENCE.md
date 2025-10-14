# B31 Aggregation Workflow Reference

**Purpose:** Quick guide for future GTM/Product/Fundraising aggregations  
**Created:** 2025-10-13  
**Status:** Validated with 5-meeting GTM test

---

## When to Run Aggregation

**Triggers:**
- 5-7 new meetings in a category (GTM/Product/Fundraising)
- Monthly review cycle
- Before major strategic decisions
- Preparing for investor/partner conversations

---

## Step-by-Step Process

### 1. Select Meetings

**Criteria:**
- Category-focused (GTM = sales+community, Product = features+UX, Fundraising = investors+advisors)
- Have filled-out B31 files (>500 bytes)
- Have transcripts available
- Recent (last 30-60 days preferred)
- Mix of stakeholder types

**Command:**
```bash
# Find meetings with B31s
python3 << 'EOF'
from pathlib import Path
meetings = Path("/home/workspace/N5/records/meetings")
for d in sorted(meetings.glob("2025-*external*"), reverse=True):
    b31 = d / "B31_STAKEHOLDER_RESEARCH.md"
    if b31.exists() and b31.stat().st_size > 500:
        print(f"{d.name} ({b31.stat().st_size} bytes)")
EOF

# Check transcript availability
ls /home/workspace/N5/inbox/transcripts/ | grep [meeting-id]
```

### 2. Extract Patterns

**Method:** Keyword-based categorization

**Pattern Keywords:**
- **Community Distribution:** community, network, distribution, channel, partnership
- **Trust & Proof:** trust, proof, quality, credibility, demonstration, value
- **Integration Friction:** integration, ats, platform, friction, white-label, trial
- **Pricing & Monetization:** price, pricing, revenue, fee, budget, monetiz
- **Candidate Signals:** soft skill, readiness, signifier, referral, behavioral
- **Product Features:** feature, ux, ui, design, workflow, automation
- **Market Dynamics:** market, competition, positioning, differentiation, timing
- **Fundraising Signals:** investor, valuation, runway, metrics, traction

**Adapt keywords per category!**

### 3. Enrich with Quotes

**Parameters:**
- Context window: 1000 characters
- Quotes per insight: 1-2 (best)
- Quote length: 3-4 sentences (one paragraph max)

**Format check:**
```bash
# Verify transcripts are plain text
file /home/workspace/N5/inbox/transcripts/[meeting-id].txt

# Convert if needed (Word docs, etc)
# Use pandoc or manual extraction
```

### 4. Generate Document

**Structure:**
```markdown
# [Category] Aggregated Insights
- Generated date
- Meetings analyzed count
- Category focus

## Table of Contents
- Pattern 1 (N insights)
- Pattern 2 (N insights)
...

## [Pattern Name]
### Insight 1: [Stakeholder]
[B31 summary]
**Supporting evidence:**
> [Quote 1]
> [Quote 2]
---

## Synthesis
### Cross-Pattern Observations
### Recommended Next Steps
```

**Output location:**
- `Knowledge/market_intelligence/aggregated_insights_[CATEGORY].md`

### 5. Review & Iterate

**Quality checks:**
- [ ] Non-obvious patterns surfaced?
- [ ] Quotes add meaningful context?
- [ ] Synthesis actionable?
- [ ] Cross-meeting themes clear?
- [ ] Navigation easy (TOC works)?
- [ ] Source attribution present?

---

## Common Issues

### Issue: Transcript Not Found
**Symptom:** Insight shows "Transcript enrichment not available"  
**Fix:** 
1. Check `/home/workspace/N5/inbox/transcripts/`
2. Look for `.txt`, `.md`, `.docx` variants
3. Convert non-text formats to `.txt`
4. Re-run enrichment

### Issue: Poor Quote Quality
**Symptom:** Quotes are too generic or off-topic  
**Fix:**
1. Refine keywords for pattern
2. Increase context window (up to 1500 chars)
3. Add post-processing to filter timestamps
4. Manually review and edit quotes

### Issue: Pattern Overlap
**Symptom:** Same insight appears in multiple sections  
**Fix:**
1. Tighten keyword specificity
2. Prioritize primary pattern match only
3. Create "cross-cutting themes" section

### Issue: Missing Transcripts
**Symptom:** Recent meeting has no transcript file  
**Fix:**
1. Check if meeting was recorded
2. Request transcript from Fireflies/Granola/etc
3. If unavailable, note in document

---

## Customization by Category

### GTM Focus
**Meeting types:** Sales prospects, community operators, channel partners  
**Key patterns:** Trust & proof, distribution, pricing, integration friction  
**Stakeholder lens:** Buyer personas, partnership readiness

### Product Focus
**Meeting types:** Users, advisors, design partners  
**Key patterns:** Feature requests, UX friction, workflow gaps, automation needs  
**Stakeholder lens:** User jobs-to-be-done, pain severity

### Fundraising Focus
**Meeting types:** Investors, advisors, board members  
**Key patterns:** Market validation, traction metrics, competitive positioning, risks  
**Stakeholder lens:** Investment thesis, due diligence signals

---

## Maintenance

**Frequency:**
- GTM: Every 5-7 sales/community meetings (~monthly)
- Product: Every 7-10 user meetings (~6 weeks)
- Fundraising: Every 3-5 investor meetings (as needed)

**Incremental updates:**
- Add new insights to existing sections
- Update "Change Log" at bottom
- Re-run synthesis when 3+ new meetings added

**Archive policy:**
- Keep current version in `Knowledge/market_intelligence/`
- Archive old versions to `Documents/Archive/` with date stamp
- Maintain change log in current doc

---

## Success Patterns (from Phase 2)

**What worked:**
1. Dynamic generation (not scripted) - more flexible
2. One transcript at a time - context window safe
3. Keyword-based categorization - fast and adequate
4. 1000-char context - good balance of detail vs. noise
5. Best 1-2 quotes per insight - prevents overwhelming
6. Synthesis section - ties it together

**What to improve:**
1. Transcript format standardization
2. Semantic pattern detection (vs. keyword only)
3. Quote cleaning (remove timestamps, speaker labels)
4. Automated incremental updates
5. Command registration for repeatability

---

## Files & Locations

**Source data:**
- B31 files: `N5/records/meetings/[meeting-id]/B31_STAKEHOLDER_RESEARCH.md`
- Transcripts: `N5/inbox/transcripts/[meeting-id].txt`

**Output:**
- GTM: `Knowledge/market_intelligence/aggregated_insights_GTM.md`
- Product: `Knowledge/market_intelligence/aggregated_insights_PRODUCT.md`
- Fundraising: `Knowledge/market_intelligence/aggregated_insights_FUNDRAISING.md`

**Working files:**
- Conversation workspace: `/home/.z/workspaces/[thread-id]/`

---

## Example Commands

**Find GTM meetings:**
```bash
# Sales + community stakeholders
for d in /home/workspace/N5/records/meetings/2025-*external*/; do
  b31="$d/B31_STAKEHOLDER_RESEARCH.md"
  if [ -f "$b31" ] && grep -qi "community\|recruiting\|hiring\|sales" "$b31"; then
    echo $(basename "$d")
  fi
done
```

**Check transcript availability:**
```bash
# For a specific meeting
meeting="2025-09-19_external-rajesh-nerlikar"
ls -la /home/workspace/N5/inbox/transcripts/${meeting}.*
```

**Validate output:**
```bash
# Check generated document
wc -l Knowledge/market_intelligence/aggregated_insights_GTM.md
grep -c "^###" Knowledge/market_intelligence/aggregated_insights_GTM.md
grep -c "Supporting evidence" Knowledge/market_intelligence/aggregated_insights_GTM.md
```

---

**Last updated:** 2025-10-13 22:18 ET  
**Validated:** 5-meeting GTM aggregation (39 insights, 25 quotes)
