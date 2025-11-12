# Reflection System Upgrade Plan - REVISED
Conversation: con_pfomxzGM45AMHbMu
Date: 2025-11-06

## Key Updates from Feedback

### 1. Syncthing Setup

STATUS: VoiceThoughts folder created locally but not yet in Syncthing config

CURRENT SYNCTHING FOLDERS:
- Personal Meetings
- Knowledge Base
- Lists & Tracking
- Articles
- Records/Reflections
- Documents
- Records/Company

ACTION NEEDED:
1. Add VoiceThoughts folder to your MacBook Syncthing
2. Share with Zo server
3. Test with voice note upload

BENEFIT: No Google Drive API, automatic sync when MacBook connected

### 2. Script Replacement - CONFIRMED

Keep as scripts (mechanics):
- reflection_ingest_v2.py
- reflection_drive_bridge.py  
- reflection_auto_ingest.py

Replace with prompts (semantics):
- reflection_classifier.py → classify-reflection.prompt.md
- reflection_block_generator.py → generate-reflection-block.prompt.md
- reflection_synthesizer_v2.py → synthesize-reflections.prompt.md
- reflection_block_suggester.py → suggest-new-blocks.prompt.md
- reflection_orchestrator.py → Use reflect-process.prompt.md

### 3. Block Quality: Dual Approach

YOUR DIRECTION: Generate synthetic data + transformation guidelines
Alternate between the two approaches

APPROACH A - SYNTHETIC PAIRS:
Generate realistic before/after transformation examples
Start with: B50, B60, B80
10 high-quality pairs each

APPROACH B - TRANSFORMATION GUIDELINES:
Rule-based guidance without specific examples
Start with: B71, B72, B82
Clear transformation rules + anti-patterns

## Implementation Plan

PHASE 1: FOUNDATION (THIS WEEK)

Syncthing:
- [x] Create VoiceThoughts folder locally
- [ ] You add to MacBook Syncthing config
- [ ] Update ingestion to watch VoiceThoughts
- [ ] Test with real voice note

First Prompts:
- [ ] classify-reflection.prompt.md (semantic classification)
- [ ] generate-reflection-block.prompt.md (style transformation)

Synthetic Data Pilot (Approach A):
- [ ] B50 Personal Reflection - 10 synthetic pairs
- [ ] B60 Learning & Synthesis - 10 synthetic pairs
- [ ] B80 LinkedIn Post - 10 synthetic pairs

Transformation Guidelines Pilot (Approach B):
- [ ] B71 Market Analysis - Rule framework
- [ ] B72 Product Analysis - Rule framework
- [ ] B82 Executive Memo - Rule framework

PHASE 2: STYLE GUIDE ENHANCEMENT (WEEK 2)

- [ ] Evaluate A vs B approaches
- [ ] Scale winning approach to remaining 6 blocks
- [ ] Add anti-patterns to all guides
- [ ] Context-specific templates
- [ ] Voice consistency markers

PHASE 3: PIPELINE MODERNIZATION (WEEK 3)

- [ ] Replace orchestration script with prompt workflow
- [ ] Replace classifier with LLM semantic classification
- [ ] Replace generator with style-guided transformation
- [ ] Replace synthesizer with cross-reflection insights
- [ ] End-to-end testing

PHASE 4: ADVANCED FEATURES (WEEK 4+)

- [ ] Quality gates automation
- [ ] Analytics dashboard
- [ ] Evaluate new block types
- [ ] Consider Drive webhooks if Syncthing insufficient

## New Ingestion Flow

VoiceThoughts folder (Syncthing)
  → File watcher detects new files
  → Transcribe if audio
  → Classify with LLM prompt
  → Transform with style guide prompt
  → Review queue
  → Approve → Publish

## Key Decisions

1. Syncthing over Drive - Simpler architecture
2. Dual approach for synthetic data - Test and iterate
3. Prompt-first for semantics - Scripts for mechanics only
4. Quality over quantity - 10 good examples better than 30 mediocre

## Next Immediate Actions

FOR ZO:
1. Generate 10 synthetic pairs for B50 (Personal Reflection)
2. Create classify-reflection.prompt.md
3. Create generate-reflection-block.prompt.md
4. Update ingestion script for VoiceThoughts

FOR YOU:
1. Add VoiceThoughts folder to MacBook Syncthing
2. Test by dropping a voice note
3. Review B50 synthetic examples when ready

## Questions

1. When can you configure Syncthing on MacBook?
2. Which 3 blocks do you use most often?
3. Voice note format preference? (.m4a, .mp3, .wav)
4. Quality bar: 5 excellent examples or 10 good ones per block?

## Expected Timeline

Week 1: Syncthing working + first prompts + B50 examples
Week 2: All 12 blocks enhanced
Week 3: Full pipeline modernized
Week 4: Polish + advanced features

SUCCESS METRICS:
- Voice notes automatically process from Syncthing
- Classification 90%+ accurate (vs 60% keyword)
- Output maintains your authentic voice
- Zero manual script editing needed
