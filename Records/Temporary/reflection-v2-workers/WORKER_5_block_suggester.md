# Worker 5: Block Suggestion System

**Mission:** Pattern detection → suggest new block types based on usage  
**Time Estimate:** 60 minutes  
**Dependencies:** Worker 2 (needs registry structure)  
**Parallelizable:** Yes (with Worker 4)

---

## Objectives

1. ✅ Build suggestion system: `N5/scripts/reflection_block_suggester.py`
2. ✅ Detect patterns in reflections that don't map to existing blocks
3. ✅ Generate suggestions for new block types
4. ✅ Save suggestions to review file
5. ✅ Implement incremental compounding (every use improves system)

---

## Conceptual Foundation

**Principle:** Incrementalism that compounds with every use.

Every reflection processed should:
1. Classify into existing blocks (Worker 2)
2. Detect unmatched patterns (Worker 5)
3. Suggest new block types when patterns recur
4. Enable V to approve new blocks → expand system

---

## Deliverables

### Script: `N5/scripts/reflection_block_suggester.py`

**Requirements:**
- Analyze reflections that have low-confidence classifications
- Detect recurring themes not captured by existing blocks
- Generate structured suggestions for new block types
- Track suggestion history to avoid duplicates
- Save to review file for V's approval

---

## Pattern Detection Logic

```python
def detect_unmatched_patterns(reflection_history: list) -> list:
    """
    Analyze reflections to find recurring themes not well-served by existing blocks.
    
    Returns list of pattern suggestions.
    """
    
    # Load all reflections from last 30 days
    reflections = load_recent_reflections(days=30)
    
    # Identify low-confidence classifications
    low_confidence = [
        r for r in reflections 
        if max(r["classifications"], key=lambda x: x["confidence"])["confidence"] < 0.6
    ]
    
    if len(low_confidence) < 3:
        return []  # Need at least 3 instances to suggest
    
    # Extract common themes
    themes = extract_themes(low_confidence)
    
    # Generate suggestions
    suggestions = []
    for theme in themes:
        if theme["frequency"] >= 3 and theme not in existing_blocks():
            suggestions.append({
                "suggested_block_name": theme["name"],
                "description": theme["description"],
                "frequency": theme["frequency"],
                "example_reflections": theme["examples"][:3],
                "recommended_domain": infer_domain(theme),
                "confidence": theme["coherence_score"]
            })
    
    return suggestions
```

---

## Suggestion Output

**File:** `N5/records/reflections/suggestions/block_suggestions.jsonl`

**Format:** One JSON object per line
```json
{
  "suggested_at_iso": "2025-10-24T20:45:00Z",
  "suggested_block_id": "B74",
  "suggested_block_name": "Customer Discovery",
  "description": "Insights and learnings from customer conversations and research",
  "frequency": 5,
  "example_reflections": [
    "2025-10-15_customer-call-insights",
    "2025-10-18_user-research-synthesis",
    "2025-10-22_customer-feedback-analysis"
  ],
  "recommended_domain": "internal",
  "recommended_voice_profile": "N5/prefs/communication/voice.md",
  "confidence": 0.78,
  "status": "pending_review"
}
```

---

## Incremental Compounding

**System Evolution:**

1. **Phase 1:** Start with 11 core block types (B50-B91)
2. **Phase 2:** Detect patterns → suggest new blocks
3. **Phase 3:** V approves suggestions → add to registry
4. **Phase 4:** New blocks available for classification
5. **Repeat:** System continuously learns and expands

**Example Evolution:**
```
Week 1: 11 blocks, 15 reflections processed
Week 2: 11 blocks, 32 reflections, 2 suggestions (Customer Discovery, Team Dynamics)
Week 3: V approves Customer Discovery → 12 blocks
Week 4: 12 blocks, 48 reflections, Customer Discovery used 7 times
Week 8: 15 blocks (added Team Dynamics, Hiring Philosophy, Fundraising Strategy)
```

---

## Integration with Reflection-Synthesizer

**Worker 5 Additional Task:** Repurpose existing `reflection_synthesizer.py`

**Options:**

### Option 1: Legacy Compatibility Mode
- Keep synthesizer as fallback for V1 format
- Add flag: `--legacy` to use old 4-format output
- Maintain for backwards compatibility

### Option 2: Convert to Block Adapter
- Refactor synthesizer to generate blocks instead of rigid formats
- Map old formats → new blocks:
  - Decision Memo → B82 (Executive Memo)
  - Key Insights → B60 (Learning & Synthesis) or B90 (Insight Compounding)
  - Action Items → (extract to task system, not reflection block)
  - Executive Blurb → B82 (Executive Memo, condensed)

### Option 3: Special-Purpose Block Generator
- Repurpose as generator for B90 (Insight Compounding) and B91 (Meta-Reflection)
- These blocks require cross-reflection synthesis
- Synthesizer already does this kind of work

**Recommendation:** Option 3
- Leverages existing synthesis capabilities
- Focused on high-value, complex blocks
- Doesn't duplicate block generator functionality

---

## Refactored Synthesizer Usage

```bash
# Generate compound insights block (B90)
python3 /home/workspace/N5/scripts/reflection_synthesizer.py \
  --block-type B90 \
  --input-reflections 2025-10-*.transcript.jsonl \
  --output /home/workspace/N5/records/reflections/outputs/2025-10-24/compound-insights/

# Generate meta-reflection block (B91)
python3 /home/workspace/N5/scripts/reflection_synthesizer.py \
  --block-type B91 \
  --input-reflections 2025-10-*.transcript.jsonl \
  --output /home/workspace/N5/records/reflections/outputs/2025-10-24/meta-reflection/
```

---

## Usage

```bash
# Run pattern detection and generate suggestions
python3 /home/workspace/N5/scripts/reflection_block_suggester.py \
  --days 30 \
  --min-frequency 3 \
  --output /home/workspace/N5/records/reflections/suggestions/block_suggestions.jsonl

# Review suggestions
cat /home/workspace/N5/records/reflections/suggestions/block_suggestions.jsonl | jq
```

---

## Testing

1. Process 10 reflections with diverse themes
2. Run suggester, verify patterns detected
3. Manually add suggested block to registry
4. Re-run classification, verify new block used
5. Verify synthesizer refactor works for B90/B91

---

## Principles Applied

- **P2 (SSOT):** Suggestions stored in single JSONL file
- **P8 (Minimal Context):** Only load recent reflections needed
- **P18 (Verify State):** Check suggestion doesn't already exist
- **P20 (Modular):** Suggester operates independently
- **Incrementalism:** Every reflection improves the system

---

## Success Criteria

Worker 5 is complete when:
1. ✅ Pattern detection works
2. ✅ Suggestions generated correctly
3. ✅ Deduplication prevents duplicate suggestions
4. ✅ Synthesizer repurposed for B90/B91
5. ✅ Integration path clear for new blocks
6. ✅ All tests pass

---

**Status:** Can start in parallel with Worker 4  
**Created:** 2025-10-24
