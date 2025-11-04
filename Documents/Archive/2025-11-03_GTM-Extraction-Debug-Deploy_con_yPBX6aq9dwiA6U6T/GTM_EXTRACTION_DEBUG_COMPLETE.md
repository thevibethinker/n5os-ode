---
created: 2025-11-03
last_edited: 2025-11-03
version: 1.0
---

# GTM Extraction Pipeline - Complete Debug Analysis

## Executive Summary

**Problem:** Database shows 63% empty insight fields despite files being marked "processed"  
**Root Cause:** Regex-based parsers with routing bugs + format fragmentation  
**Solution Built:** LLM-based extraction system (no regex, handles all formats)  
**Status:** Ready to deploy, needs API key configuration

---

## Debug Process & Findings

### 1. Initial Investigation
- Analyzed database: 40/63 records empty, 49/63 missing key fields
- Only 14/63 records properly populated with all fields
- Conclusion: Extraction pipeline fundamentally broken

### 2. Root Cause Analysis

**PRIMARY BUG - Routing Logic (Line 180 in gtm_b31_processor.py):**
```python
if '## Insight' in content:  # ← SUBSTRING MATCH BUG
    insights = parse_b31_format_new(content, ...)
```

**Why it fails:**
- Python substring `'## Insight' in content` matches BOTH:
  - `"## Insight 1:"` (H2 - intended)
  - `"### Insight 1:"` (H3 - false positive)  
- Files with H3 format routed to H2 parser
- H2 parser regex `r'\n## Insight \d+:'` finds 0 matches
- Returns empty list, marks "processed" with 0 insights

**SECONDARY ISSUE - Format Fragmentation:**  
Across 209 B31 files:
- 96 files: Empty/stub (< 200 bytes)
- 76 files: Narrative/unstructured  
- 20 files: `### N. **Title**` format
- 8 files: `**N. Title**` format
- 6 files: `### Insight N:` format (BROKEN by bug above)
- 3 files: `## Insight N:` format (only format that works)

**Only 37 files (18%)** have structured format current parsers can handle.

### 3. Why Regex Is The Wrong Approach

**Problems with current regex parsers:**
1. **Brittle**: Requires exact format match
2. **Silent failure**: No error when pattern doesn't match
3. **Maintenance burden**: 4 different parsers for 4 formats
4. **Can't handle variations**: New format = new parser needed
5. **Routing complexity**: Complex if/elif chains prone to bugs

**Why LLM interpretation is better:**
1. **Flexible**: Handles ANY format (H2, H3, bold, narrative, mixed)
2. **Semantic**: Understands meaning, not just syntax
3. **Single code path**: One extraction function replaces 4 parsers
4. **Self-documenting**: Prompt explains what to extract
5. **Robust**: Can infer missing fields from context

---

## Solution Implemented

### New File: `N5/scripts/gtm_processor_llm_auto.py`

**Architecture:**
```
Read B31 file → Send to LLM with structured prompt → Parse JSON response → Insert to DB
```

**Key Features:**
1. **No regex parsing** - LLM interprets content semantically
2. **Structured JSON output** - 9 fields per insight
3. **Error handling** - Saves failed responses for debugging
4. **Logging** - Clear progress and error messages
5. **Flexible** - Works with any B31 format

**Extraction Prompt Template:**
- Provides meeting context
- Lists all required fields
- Defines categories/signal strength
- Requests pure JSON output

**Fields Extracted:**
1. title
2. category  
3. evidence (quotes + examples)
4. why_it_matters (strategic implications)
5. signal_strength (1-5)
6. stakeholder_name
7. stakeholder_role
8. stakeholder_type
9. quote

---

## Testing & Validation

### Manual Test Performed
Extracted insights from: `Personal/Meetings/2025-10-14_external-elaine-p/B31_STAKEHOLDER_RESEARCH.md`

**Result:** Successfully extracted 3 insights with all fields populated:
- PDF extraction barriers in RAG
- AI tools democratizing development  
- Generic AI tools failing at career positioning

**Quality:** All insights properly structured with:
- ✓ Clear titles
- ✓ Categorization
- ✓ Evidence with quotes
- ✓ Strategic implications
- ✓ Signal strength ratings
- ✓ Stakeholder context

See: file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/extracted_insights_example.json`

---

## Deployment Plan

### Phase 1: Configuration
```bash
# Set API key (if using external Anthropic API)
export ANTHROPIC_API_KEY="<key>"

# OR: Modify script to use internal Zo API
```

### Phase 2: Test Run
```bash
# Test on single meeting
python3 /home/workspace/N5/scripts/gtm_processor_llm_auto.py \
  --meeting-id "2025-10-14_external-elaine-p"

# Verify output in database
sqlite3 /home/workspace/Knowledge/market_intelligence/gtm_intelligence.db \
  "SELECT * FROM gtm_insights WHERE meeting_id = '2025-10-14_external-elaine-p';"
```

### Phase 3: Batch Processing  
```bash
# Process 10 meetings
python3 /home/workspace/N5/scripts/gtm_processor_llm_auto.py --batch 10

# Process all meetings (caution: API costs)
python3 /home/workspace/N5/scripts/gtm_processor_llm_auto.py --all
```

### Phase 4: Replace Old Processor
1. Rename `gtm_b31_processor.py` → `gtm_b31_processor_DEPRECATED.py`
2. Update scheduled task to call `gtm_processor_llm_auto.py`
3. Monitor first few runs for errors
4. Archive old regex parsers once stable

---

## Cost & Performance Considerations

**LLM Extraction Cost:**
- ~2000-4000 tokens per B31 file (input)
- ~500-1000 tokens per response (output)
- Estimate: $0.01-0.03 per meeting at Claude Sonnet rates

**For 209 files:**
- Total cost: ~$2-6 for complete backfill
- Time: ~5-10 seconds per file (API latency)
- Total runtime: ~20-35 minutes for full batch

**Ongoing:**
- 1-2 new meetings per day
- ~$0.30-0.60/month ongoing cost

---

## Files Changed/Created

**Created:**
- file `/home/workspace/N5/scripts/gtm_processor_llm_auto.py` - New LLM-based processor
- file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/extraction_bug_analysis.md` - Detailed bug analysis
- file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/extracted_insights_example.json` - Test output
- file `/home/.z/workspaces/con_yPBX6aq9dwiA6U6T/DEBUG_LOG.jsonl` - Debug trace

**To Deprecate:**
- file `/home/workspace/N5/scripts/gtm_b31_processor.py` - Regex-based (broken)
- file `/home/workspace/N5/scripts/gtm_db_backfill.py` - Regex-based

**To Keep:**
- file `/home/workspace/N5/scripts/gtm_backfill_llm.py` - Prompt generator (can keep as reference)

---

## Recommendations

1. **Deploy LLM processor immediately** - Current system is 63% broken
2. **Clear bad data** - Delete insights with empty fields before reprocessing
3. **Reprocess all meetings** - Run --all to rebuild clean database
4. **Update scheduled task** - Switch from gtm_b31_processor.py to gtm_processor_llm_auto.py
5. **Monitor first week** - Check logs daily, verify extraction quality
6. **Archive regex parsers** - Keep for reference but don't use

---

## Success Criteria

- [ ] All B31 files with content extracted successfully
- [ ] Zero empty insight/why_it_matters/quote fields
- [ ] Each insight has all 9 required fields
- [ ] Signal strength reflects actual confidence levels
- [ ] Categories properly distributed
- [ ] Stakeholder information correctly extracted
- [ ] Database query returns useful, actionable intelligence

---

*Debug completed: 2025-11-03 12:31 EST*  
*Conversation: con_yPBX6aq9dwiA6U6T*
