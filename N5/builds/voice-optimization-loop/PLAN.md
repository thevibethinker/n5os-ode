---
created: 2026-01-18
last_edited: 2026-01-18
version: 1.0
provenance: con_K8CGjHBpHa9kAFAY
status: ready
---

# Plan: Voice Optimization Loop — Learning from V's Edits

**Slug:** `voice-optimization-loop`  
**Owner:** Vibe Architect  
**Status:** Ready for Build  
**Created:** 2026-01-18  

---

## Problem Statement

When V improves a draft I generated, the improvements disappear into the conversation. There's no systematic way to:
1. Capture the before/after pair
2. Analyze what changed and why
3. Extract lessons (preferences, patterns, anti-patterns)
4. Update voice library with new primitives from V's edits
5. Store lessons in semantic memory for future retrieval

This is the **feedback loop** that makes voice learning *continuous* rather than batch.

---

## Decisions (Locked)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Trigger mechanism | **Implicit detection** — when V provides their version in response to my generation, assume it's for learning | Natural, zero friction |
| Storage permanence | **Yes, store all pairs** in a database | Cheap storage, future analysis value |
| Lesson scope | **Scoped by content type** with promotion path to global | Different content types have different preferences |
| Voice library in semantic memory | **Yes** (Phase 5) | Enables contextual retrieval across conversations |

---

## Alternatives Considered (Nemawashi)

### Alternative A: Manual Primitive Entry
V manually identifies good phrases from their edits and adds them to voice library.

**Rejected:** Too much friction. V won't do this consistently.

### Alternative B: Scheduled Batch Analysis
Agent periodically reviews conversation history for before/after pairs.

**Rejected:** Loses context. Hard to identify which pairs are "V improved this" vs. "different drafts."

### Alternative C: Interactive Feedback Capture (SELECTED)
When V provides an improved version in conversation, Zo:
1. Detects it as a revision (implicit trigger)
2. Runs diff analysis immediately
3. Extracts lessons
4. Stores to semantic memory + voice library
5. Confirms what was learned

**Selected because:** Low friction, high context, immediate feedback.

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Mitigation |
|----------|---------------|------------|
| Semantic memory schema for lessons | Medium | Design schema carefully; additive only |
| Before/after pair storage format | Low | Use SQLite table (append-only, queryable) |
| Lesson extraction prompt | High | Can iterate on prompt freely |

---

## Success Criteria

1. V can paste an improved version and Zo learns from it (< 30 seconds)
2. Lessons appear in semantic memory and are retrievable in future conversations
3. New primitives from V's edits are proposed for voice library review
4. Writer persona demonstrably uses learned preferences in subsequent drafts
5. V can review accumulated lessons in a structured file
6. Voice library primitives retrievable via semantic memory (Phase 5)

---

## Phase 1: Capture Infrastructure

### Objective
Build the mechanism to detect and store before/after pairs.

### Affected Files
- `N5/scripts/voice_feedback_capture.py` (NEW)
- `N5/data/voice_library.db` (UPDATE — add `feedback_pairs` table)
- `N5/prefs/communication/voice-lessons.md` (NEW)

### Changes
1. Create `voice_feedback_capture.py`:
   - Input: original_text, improved_text, content_type, context
   - Store pair to `feedback_pairs` table in voice_library.db
   - Return confirmation

2. Add `feedback_pairs` table to voice_library.db:
   - id, original_text, improved_text, content_type, context, created_at, analyzed (bool)

3. Create `voice-lessons.md`:
   - Human-readable log of accumulated lessons
   - YAML frontmatter with version tracking

### Unit Tests
- [ ] Script accepts and stores a before/after pair
- [ ] Database insert works correctly
- [ ] Duplicate detection works (same pair not stored twice)

---

## Phase 2: Diff Analysis + Lesson Extraction

### Objective
Analyze what changed between original and improved, extract actionable lessons.

### Affected Files
- `N5/scripts/voice_diff_analyzer.py` (NEW)
- `N5/scripts/voice_lesson_extractor.py` (NEW)

### Changes
1. Create `voice_diff_analyzer.py`:
   - Semantic diff (not just text diff)
   - Categories: word choice, sentence structure, tone, length, directness, specificity
   - Output: structured diff report (JSON)

2. Create `voice_lesson_extractor.py`:
   - Takes diff report + content_type
   - Uses LLM to generate actionable lessons
   - Format: "When writing [content_type], V prefers [specific preference] over [what I did]"
   - Flags lessons for potential global promotion
   - Also extracts candidate primitives (new phrases V used)

### Unit Tests
- [ ] Diff analyzer correctly categorizes changes
- [ ] Lesson extractor produces structured lessons with content_type scope
- [ ] Candidate primitives are extracted with proper metadata

---

## Phase 3: Storage + Semantic Memory Integration

### Objective
Store lessons in semantic memory for retrieval; update voice library with new primitives.

### Affected Files
- `N5/cognition/n5_memory_client.py` (UPDATE — add voice lesson storage)
- `N5/data/voice_library.db` (UPDATE — primitives from edits, source = 'v_edit')
- `N5/scripts/voice_feedback_capture.py` (UPDATE — add semantic memory call)
- `N5/prefs/communication/voice-lessons.md` (UPDATE — append new lessons)

### Changes
1. Add semantic memory integration:
   - Store lessons as memories with type = "voice_preference"
   - Include content_type tag for retrieval scoping
   - Add global_promotion flag for cross-type lessons

2. Update voice library:
   - Add primitives extracted from V's edits
   - Source = "v_edit" (distinct from "transcript" or "linkedin")

3. Update voice-lessons.md:
   - Append human-readable lesson log
   - Organize by content_type

### Unit Tests
- [ ] Lessons stored to semantic memory with content_type
- [ ] Lessons retrievable by content type
- [ ] Primitives added to voice library with source = 'v_edit'

---

## Phase 4: Writer Integration + Retrieval

### Objective
Make Writer persona actually use the learned preferences.

### Affected Files
- `Prompts/Generate With Voice.prompt.md` (UPDATE — add lesson retrieval step)
- `N5/scripts/retrieve_voice_lessons.py` (NEW)

### Changes
1. Create `retrieve_voice_lessons.py`:
   - Query semantic memory for relevant lessons
   - Filter by content_type (with global fallback)
   - Return top N lessons for context injection

2. Update Writer prompt:
   - Add step: "Before drafting, retrieve V's voice lessons for this content type"
   - Include lessons in generation context

### Unit Tests
- [ ] Retrieval script returns relevant lessons for content_type
- [ ] Global lessons included when appropriate
- [ ] Writer prompt includes lessons in generation

---

## Phase 5: Voice Library Semantic Memory Integration

### Objective
Make existing voice library primitives retrievable via semantic memory (beyond current script-based retrieval).

### Affected Files
- `N5/scripts/sync_primitives_to_memory.py` (NEW)
- `N5/cognition/n5_memory_client.py` (UPDATE — add primitive retrieval)

### Changes
1. Create `sync_primitives_to_memory.py`:
   - Reads all primitives from voice_library.db
   - Stores to semantic memory with type = "voice_primitive"
   - Includes tags, function, usage conditions

2. Update memory client:
   - Add method for primitive retrieval
   - Support filtering by tags/domain

3. One-time sync of existing 419 primitives

### Unit Tests
- [ ] All primitives synced to semantic memory
- [ ] Primitives retrievable by domain/tag
- [ ] New primitives auto-sync on add

---

## Dependencies

- Semantic memory: `N5/cognition/n5_memory_client.py`
- Voice library: `N5/data/voice_library.db`
- Writer persona: `Prompts/Generate With Voice.prompt.md`

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-18 | Decisions locked per V's input. Added Phase 5. Ready for build. |
| 0.1 | 2026-01-18 | Initial draft with open questions |
