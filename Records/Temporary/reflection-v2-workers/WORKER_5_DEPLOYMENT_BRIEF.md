# Worker 5 Deployment Brief

**Date:** 2025-10-26 21:37 ET\
**Status:** Ready to Deploy\
**Prerequisites:** ✅ All Met (Workers 1-4 Complete)

---

## Mission

Build pattern detection system that suggests new block types + repurpose reflection_synthesizer for B90/B91 cross-reflection synthesis.

---

## Context from Worker 4

### ✅ What's Ready

- Block generator produces outputs with metadata
- Output structure: `N5/records/reflections/outputs/YYYY-MM-DD/slug/`
- Metadata tracking: classifications, blocks generated, approval status
- **5 existing reflections** in incoming directory available for analysis
- **1 classification file** exists (can test with this)

### Data Available for Worker 5

```markdown
N5/records/reflections/incoming/
├── 2025-10-20_logan-x-vrijen-morning-powwow.txt.transcript.jsonl
├── 2025-10-20_planning-for-n5-os-demo.m4a.transcript.jsonl
├── 2025-10-20_zo-system-gtm.txt.transcript.jsonl
├── 2025-10-21_reflections-on-n5-os.m4a.transcript.jsonl
├── 2025-10-21_reflections-on-n5-os.m4a.transcript.classification.json ← Can use this
└── 2025-10-23_gestalt-overperformers-tryhard.m4a.transcript.jsonl
```

---

## Deliverables

### 1. Pattern Detection Script

**File:** `file N5/scripts/reflection_block_suggester.py`

**Core Functions:**

```python
def load_recent_reflections(days: int = 30) -> List[Dict]
def identify_low_confidence_classifications(reflections: List) -> List
def extract_recurring_themes(reflections: List) -> List[Dict]
def generate_block_suggestions(themes: List) -> List[Dict]
def save_suggestions(suggestions: List, output_path: Path)
def check_duplicate_suggestions(suggestion: Dict, history: List) -> bool
```

**CLI:**

```bash
python3 reflection_block_suggester.py \
  --days 30 \
  --min-frequency 3 \
  --min-confidence-threshold 0.6 \
  --output N5/records/reflections/suggestions/block_suggestions.jsonl \
  [--dry-run]
```

### 2. Synthesizer Refactor

**File:** `file N5/scripts/reflection_synthesizer.py` (modify existing)

**New Mode:** Generate B90 (Insight Compound) and B91 (Meta-Reflection) from multiple reflections

**New CLI:**

```bash
# Generate B90: Cross-reflection synthesis
python3 reflection_synthesizer.py \
  --block-type B90 \
  --input-pattern "2025-10-*.transcript.jsonl" \
  --output N5/records/reflections/outputs/2025-10-24/compound-insights/ \
  [--dry-run]

# Generate B91: Meta-reflection
python3 reflection_synthesizer.py \
  --block-type B91 \
  --input-pattern "2025-10-*.transcript.jsonl" \
  --output N5/records/reflections/outputs/2025-10-24/meta-reflection/ \
  [--dry-run]

# Legacy mode (maintain compatibility)
python3 reflection_synthesizer.py \
  --legacy \
  --input transcript.jsonl \
  --output outputs/
```

---

## Implementation Plan

### Phase 1: Pattern Detection (30 min)

1. Create `file reflection_block_suggester.py`
2. Implement reflection loading from outputs directory
3. Identify low-confidence classifications (&lt; 0.6 confidence)
4. Extract recurring themes using keyword clustering
5. Generate structured suggestions
6. Save to `file N5/records/reflections/suggestions/block_suggestions.jsonl`

**Test:**

```bash
python3 reflection_block_suggester.py --days 30 --dry-run
```

### Phase 2: Synthesizer Refactor (30 min)

1. Add `--block-type` flag to existing synthesizer
2. Add logic for B90 (cross-reflection synthesis): 
   - Load multiple transcripts
   - Extract common themes
   - Synthesize higher-order insights
   - Apply B90 style guide
3. Add logic for B91 (meta-reflection): 
   - Analyze reflection patterns
   - Track evolution of thinking
   - Generate process insights
   - Apply B91 style guide
4. Maintain `--legacy` mode for backwards compatibility

**Test:**

```bash
python3 reflection_synthesizer.py --block-type B90 \
  --input-pattern "N5/records/reflections/incoming/2025-10-*.transcript.jsonl" \
  --dry-run
```

---

## Key Design Decisions

### Pattern Detection Algorithm

**Simple Approach (Recommended for V1):**

1. Load all reflections from last 30 days
2. Filter to low-confidence classifications (&lt; 0.6)
3. Extract top keywords from each
4. Cluster by keyword similarity
5. Suggest new block for clusters with ≥3 reflections

**Advanced Approach (Future):**

- Use embedding similarity (requires LLM)
- Topic modeling
- More sophisticated theme extraction

**Start simple, evolve later.**

### Suggestion Schema

```json
{
  "suggested_at_iso": "2025-10-26T21:30:00Z",
  "suggested_block_id": "B74",  // Next available ID
  "suggested_block_name": "Customer Discovery",
  "description": "Insights from customer conversations",
  "frequency": 5,
  "example_reflections": ["2025-10-15_...", "2025-10-18_...", "2025-10-22_..."],
  "recommended_domain": "internal",
  "recommended_voice_profile": "N5/prefs/communication/voice.md",
  "confidence": 0.78,
  "status": "pending_review",
  "keywords": ["customer", "user", "feedback", "discovery", "research"]
}
```

### Synthesizer Block Mapping

- **B90 (Insight Compound)**: Load style guide, synthesize cross-reflection themes
- **B91 (Meta-Reflection)**: Load style guide, analyze reflection process evolution
- **Legacy**: Keep old 4-format output (memo/insights/actions/blurb)

---

## Integration Points

### Input Dependencies (Met)

✅ Worker 1: Transcripts available\
✅ Worker 2: Classifications available (1 file, can generate more)\
✅ Worker 3: Style guides for B90/B91 exist\
✅ Worker 4: Output structure defined

### Output Products

- `file block_suggestions.jsonl` → For V's review
- B90/B91 blocks → Add to outputs directory
- Refactored synthesizer → Ready for Worker 6 integration

---

## Testing Strategy

### Test 1: Pattern Detection

```bash
# Run on existing reflections
python3 reflection_block_suggester.py --days 30 --dry-run

# Expected: Detects themes, generates 0-2 suggestions (limited data)
```

### Test 2: Synthesizer B90

```bash
# Generate compound insights from multiple reflections
python3 reflection_synthesizer.py \
  --block-type B90 \
  --input-pattern "N5/records/reflections/incoming/2025-10-2*.transcript.jsonl" \
  --dry-run

# Expected: Loads 4-5 transcripts, generates cross-reflection synthesis
```

### Test 3: Synthesizer B91

```bash
# Generate meta-reflection
python3 reflection_synthesizer.py \
  --block-type B91 \
  --input-pattern "N5/records/reflections/incoming/*.transcript.jsonl" \
  --dry-run

# Expected: Analyzes reflection patterns, generates process insights
```

### Test 4: Legacy Mode

```bash
# Verify old functionality still works
python3 reflection_synthesizer.py \
  --legacy \
  --input N5/records/reflections/incoming/2025-10-21_reflections-on-n5-os.m4a.transcript.jsonl \
  --dry-run

# Expected: Generates old 4-format output
```

---

## Success Criteria

Worker 5 is complete when:

1. ✅ Pattern detection script runs successfully
2. ✅ Suggestions saved to correct location
3. ✅ Deduplication logic prevents duplicates
4. ✅ Synthesizer refactored for B90/B91
5. ✅ Legacy mode maintained
6. ✅ All tests pass with dry-run
7. ✅ Documentation updated

---

## Files to Create/Modify

**Create:**

- `file N5/scripts/reflection_block_suggester.py`
- `file N5/records/reflections/suggestions/block_suggestions.jsonl`
- `file N5/records/reflections/suggestions/.state.json` (track suggestion history)

**Modify:**

- `file N5/scripts/reflection_synthesizer.py` (add block-type mode)

---

## Expected Timeline

**Phase 1:** Pattern Detection - 30 minutes\
**Phase 2:** Synthesizer Refactor - 30 minutes\
**Testing:** 10 minutes

**Total:** \~70 minutes (slightly over estimate, acceptable)

---

## Principles to Follow

- **P0 (Rule-of-Two):** Load registry + 1-2 reflections for analysis
- **P7 (Dry-Run):** Both scripts support dry-run
- **P8 (Minimal Context):** Only load reflections from time window
- **P18 (Verify State):** Check outputs before claiming success
- **P19 (Error Handling):** Handle missing files gracefully
- **Incrementalism:** Design enables continuous system improvement

---

## Notes from Validation

- Worker 4 is production-ready (488 lines, excellent quality)
- Only minor gap: `count_blocks_generated()` is placeholder (doesn't block Worker 5)
- 5 transcripts available for testing pattern detection
- 1 classification file exists (can generate more with Worker 2)
- Ready to proceed immediately

---

## Post-Deployment

After Worker 5 completes:

1. Run pattern detection on existing data
2. Review any suggestions generated
3. Test synthesizer B90/B91 generation
4. Prep for Worker 6 (orchestrator + integration)

---

**Status:** Ready to Deploy\
**Risk:** Low\
**Dependencies:** All Met

**Deploy when ready!**

**2025-10-26 21:37 ET**