# Reflection Processing System V2 - Implementation Plan

**Project:** Reflection System V2 - Drive-Centric Block-Based Architecture  
**Created:** 2025-10-24  
**Drive Folder ID:** `16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV`  
**Architecture:** Orchestrator-Worker Model

---

## Executive Summary

**What Changed:**
- **✅ Drive-only source** (eliminating email complexity)
- **✅ Block-based outputs** (replacing rigid 4-format synthesizer)
- **✅ Dynamic block selection** based on multi-label classification
- **✅ Voice-appropriate routing** (internal/external, social/professional)
- **✅ Style guide integration** for each block type
- **✅ Incremental compounding** (suggest new block types from reflections)
- **✅ Auto-approval** up to 10 blocks, ask for approval beyond
- **✅ Idempotency** (track processed files to avoid duplication)
- **✅ Polling with offset** (prevent crash-induced skips)

**Key Design Decisions:**
1. Reflection blocks start at **B50** (meetings 1-49, reflections 50-99)
2. Two distinct voice profiles: `social-media-voice.md` (external social) + `voice.md` (professional/internal)
3. Block suggester worker evaluates if new block types should be created
4. Reflection-synthesizer repurposed (determined by Worker 5)
5. Drive folder is SSOT - no email integration

---

## Reflection Block Types (B50-B99)

### Internal Blocks (B50-B59) - Personal/Learning
**Voice:** `N5/prefs/communication/voice.md`

- **B50: PERSONAL_REFLECTION** - Stream of consciousness processing, personal insights
- **B51: LEARNING_INSIGHT** - Lessons learned, mental models, skill development
- **B52: STRATEGIC_MEMO** - Internal strategic thinking, decision frameworks
- **B53: DEBATE_POINTS** - Internal argument mapping, pros/cons analysis

### External Blocks (B60-B79) - Professional Content
**Voice:** `N5/prefs/communication/voice.md` (professional, not social)

- **B60: THOUGHT_LEADERSHIP** - Long-form article foundations, op-ed material
- **B61: MARKET_ANALYSIS** - Market observations, competitive intelligence
- **B62: PRODUCT_ANALYSIS** - Product strategy reflections, feature rationale
- **B63: CURRICULUM_MODULE** - Training/education content building blocks

### Social Blocks (B80-B89) - Public Sharing
**Voice:** `N5/prefs/communication/social-media-voice.md`

- **B80: LINKEDIN_POST** - Ready-to-publish LinkedIn post
- **B81: TWITTER_THREAD** - Thread structure with hooks
- **B82: STORY_SNIPPET** - Narrative moments for storytelling

### Compounding Blocks (B90-B99) - Meta/Evolution
**Voice:** Context-dependent

- **B90: INSIGHT_COMPOUND** - Connections across multiple reflections
- **B91: THEME_EMERGENCE** - Patterns detected over time
- **B92: BLOCK_SUGGESTION** - New block type proposal based on recurring patterns

---

## Classification System

### Multi-Label Categories
Each reflection can have multiple tags:

**Primary Categories:**
- `product_strategy` - Product decisions, feature rationale, roadmap thinking
- `founder_journey` - Entrepreneurship experiences, founder challenges
- `market_intelligence` - Market observations, competitive insights
- `dilemma` - Decision points, trade-offs, tough choices
- `pitch_narrative` - Storytelling for fundraising/sales
- `announcement` - News, launches, milestones
- `hiring` - Recruiting, team building, culture
- `learning` - Personal development, lessons, growth

**Audience Intent:**
- `internal_only` - Private reflection, not for external sharing
- `external_professional` - Can be shared professionally (articles, memos)
- `external_social` - Can be shared on social media

**Content Maturity:**
- `raw` - Stream of consciousness, needs heavy processing
- `structured` - Organized thoughts, ready for light editing
- `polished` - Nearly ready for publishing

### Classification → Block Mapping

```python
CLASSIFICATION_TO_BLOCKS = {
    "product_strategy + internal_only": ["B50", "B52", "B62"],
    "product_strategy + external_professional": ["B60", "B62"],
    "product_strategy + external_social": ["B80", "B62"],
    
    "founder_journey + internal_only": ["B50", "B51"],
    "founder_journey + external_social": ["B80", "B82"],
    
    "market_intelligence + internal_only": ["B52", "B61"],
    "market_intelligence + external_professional": ["B60", "B61"],
    
    "pitch_narrative + external_professional": ["B60", "B63"],
    "pitch_narrative + external_social": ["B80", "B81", "B82"],
    
    # Additional mappings...
}
```

**Block Generation Logic:**
1. Classify reflection → get tags
2. Look up tag combination → get candidate blocks
3. Generate up to 10 blocks automatically
4. If >10 blocks, ask for approval on which to generate

---

## Style Guide Architecture

### Per-Block Style Guides (To Be Created)

Each reflection block type needs a style guide:

**Location:** `N5/prefs/communication/style-guides/reflections/`

**Files to Create:**
- `B50-personal-reflection.md`
- `B51-learning-insight.md`
- `B52-strategic-memo.md`
- `B60-thought-leadership.md`
- `B61-market-analysis.md`
- `B62-product-analysis.md`
- `B63-curriculum-module.md`
- `B80-linkedin-post.md`
- `B81-twitter-thread.md`
- `B82-story-snippet.md`

**Creation Method:**
1. Extract voice from appropriate source (voice.md or social-media-voice.md)
2. Apply transformation strategy from `voice-transformation-system.md`
3. Define block-specific constraints (length, structure, tone)
4. Include examples from `transformation-pairs-library.md`

**Worker Dependency:** Worker 3 creates style guides after Worker 2 defines block structures

---

## File Structure

```
N5/
├── records/reflections/
│   ├── incoming/               # Files pulled from Drive (staging)
│   ├── outputs/                # Generated blocks organized by date
│   │   └── {YYYY-MM-DD}/
│   │       └── {slug}/
│   │           ├── blocks/
│   │           │   ├── B50_PERSONAL_REFLECTION.md
│   │           │   ├── B61_MARKET_ANALYSIS.md
│   │           │   └── ...
│   │           ├── _metadata.json
│   │           └── _transcript.txt (original text)
│   └── registry/
│       └── reflection_registry.jsonl  # Tracking all processed reflections
│
├── prefs/communication/style-guides/reflections/
│   ├── B50-personal-reflection.md
│   ├── B60-thought-leadership.md
│   └── ... (one per block type)
│
├── scripts/
│   ├── reflection_ingest_v2.py        # Drive polling + transcription
│   ├── reflection_classifier.py       # Multi-label classification
│   ├── reflection_block_generator.py  # Block generation with voice routing
│   ├── reflection_block_suggester.py  # Suggests new block types
│   └── reflection_orchestrator_v2.py  # Main coordinator
│
└── .state/
    └── reflection_drive_state.json    # Tracks processed Drive file IDs
```

---

## Worker Breakdown

### Worker 1: Drive Integration & Transcription
**Mission:** Pull files from Drive folder, transcribe audio, stage for processing

**Deliverables:**
- `N5/scripts/reflection_ingest_v2.py`
- `N5/.state/reflection_drive_state.json` (idempotency tracker)
- Drive polling with offset (prevent crash skips)
- Auto-transcription for audio files

**Time:** 45 minutes

---

### Worker 2: Classification & Block Registry
**Mission:** Multi-label classifier + block type registry setup

**Deliverables:**
- `N5/scripts/reflection_classifier.py`
- `N5/prefs/reflection_block_registry.json` (B50-B99 definitions)
- Classification → block mapping logic
- Update main block registry to include reflection blocks

**Time:** 60 minutes

---

### Worker 3: Style Guide Generation
**Mission:** Create style guides for each reflection block type

**Deliverables:**
- 10+ style guide files in `N5/prefs/communication/style-guides/reflections/`
- Voice extraction from source files
- Transformation strategy application
- Examples integration

**Time:** 90 minutes  
**Dependency:** Worker 2 (needs block definitions)

---

### Worker 4: Block Generator with Voice Routing
**Mission:** Generate blocks with correct voice profiles and approval logic

**Deliverables:**
- `N5/scripts/reflection_block_generator.py`
- Voice routing: internal vs external, social vs professional
- Auto-approve up to 10 blocks, ask beyond
- Output to structured directory

**Time:** 60 minutes  
**Dependency:** Workers 2 & 3

---

### Worker 5: Block Suggester & Repurpose Synthesizer
**Mission:** Suggest new block types + determine fate of reflection-synthesizer

**Deliverables:**
- `N5/scripts/reflection_block_suggester.py`
- Analysis of reflection-synthesizer → repurpose plan
- New block type detection algorithm
- Documentation on when to add blocks

**Time:** 45 minutes

---

### Worker 6: Main Orchestrator & Integration
**Mission:** Tie all components together, testing, deployment

**Deliverables:**
- `N5/scripts/reflection_orchestrator_v2.py`
- `N5/commands/reflection-process-v2.md`
- Integration tests
- Documentation updates
- Scheduled task setup

**Time:** 60 minutes  
**Dependency:** All workers

---

## Execution Sequence

### Phase 1: Foundation (Parallel)
- Worker 1: Drive integration
- Worker 2: Classification system

### Phase 2: Content Generation (Sequential after Phase 1)
- Worker 3: Style guides (depends on Worker 2)
- Worker 4: Block generator (depends on Workers 2 & 3)

### Phase 3: Intelligence (Parallel after Phase 2)
- Worker 5: Block suggester

### Phase 4: Integration (After all)
- Worker 6: Orchestrator & deployment

**Total Time:** ~6-7 hours (with parallelization)

---

## Idempotency & Safety

### Tracking Processed Files
**File:** `N5/.state/reflection_drive_state.json`

```json
{
  "last_poll": "2025-10-24T18:00:00Z",
  "processed_files": {
    "1aBC123xyz": {
      "name": "2025-10-24-pricing-strategy.txt",
      "processed_at": "2025-10-24T18:05:00Z",
      "slug": "2025-10-24_pricing-strategy",
      "blocks_generated": ["B50", "B52", "B61"]
    }
  }
}
```

### Dry-Run Support
All scripts support `--dry-run` flag for safety (P7)

### Error Handling
All scripts include comprehensive error handling and recovery paths (P19)

---

## Polling Configuration

### Frequency Options
**V's Decision Needed:**
- Hourly (0 */1 * * *)
- 4x daily (0 */6 * * *)
- Other?

### Offset Strategy
```python
# 7-minute offset to avoid crash windows
POLLING_CRON = "7 */1 * * *"  # Run at :07 past each hour
```

**Rationale:** If system crashes at exactly :00, :07 offset provides recovery buffer

---

## Voice Routing Matrix

| Block Type | Audience | Voice File |
|------------|----------|------------|
| B50-B59 (Internal) | Self | `voice.md` |
| B60-B79 (Professional) | External professional | `voice.md` |
| B80-B89 (Social) | External social | `social-media-voice.md` |
| B90-B99 (Meta) | Context-dependent | Determined per block |

---

## Approval Logic

### Auto-Approve: ≤10 Blocks
Generate all blocks automatically, notify V of completion

### Manual Approve: >10 Blocks
1. Show classification results
2. List all candidate blocks
3. Ask V: "Generate all or select specific blocks?"
4. Proceed based on response

**Implementation:** `reflection_block_generator.py` includes approval prompt

---

## Success Criteria

### System Complete When:
- [ ] Drive folder polls every N hours with offset
- [ ] Audio files auto-transcribe
- [ ] Multi-label classification working
- [ ] All 10+ style guides created
- [ ] Block generation with voice routing functional
- [ ] Auto-approval logic (≤10 blocks) works
- [ ] Manual approval prompt (>10 blocks) works
- [ ] Block suggester detects new patterns
- [ ] Idempotency prevents re-processing
- [ ] Registry tracks all reflections
- [ ] Reflection-synthesizer fate decided
- [ ] Integration tests pass
- [ ] Documentation complete

---

## Next Steps

**V's Decisions Needed:**
1. ✅ Drive folder ID: `16RcIne-UqSteJdbNr0jKIPzsdhcV8_mV` - confirmed?
2. ❓ Polling frequency: Hourly, 4x daily, or other?
3. ✅ Voice routing confirmed: social vs professional distinction
4. ✅ Block approval: ≤10 auto, >10 manual - confirmed
5. ✅ Reflection-synthesizer: repurpose via Worker 5 - confirmed

**Once Approved:**
1. Create worker briefs in `N5/orchestration/reflection-system-v2/`
2. Launch Worker 1 & 2 in parallel
3. Sequential launch of Workers 3-6
4. Integration testing
5. Deployment

---

**Plan Version:** 2.0  
**Status:** Awaiting V's approval on polling frequency  
**Created:** 2025-10-24 18:04 ET
