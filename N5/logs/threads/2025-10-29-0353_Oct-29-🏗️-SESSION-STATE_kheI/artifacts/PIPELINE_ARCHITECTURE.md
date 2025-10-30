# Conversation End + Thread Export Pipeline Architecture
**Analysis Date:** 2025-10-28

## System Components

### 1. Thread Export (`n5_thread_export.py`)
**Purpose:** Generate AAR and archive thread artifacts
**Entry Points:**
- Direct invocation: `python3 n5_thread_export.py [thread_id] --title "Title"`
- Auto mode: `python3 n5_thread_export.py --auto`

**Core Flow:**
1. `detect_thread_id()` - Auto-detect conversation
2. `validate_thread()` - Check workspace exists
3. `inventory_artifacts()` - Scan conversation workspace
4. `generate_aar_data()` - Create AAR structure
5. **Title Generation** (via TitleGenerator)
6. `save_checkpoint()` - Save AAR JSON
7. `copy_artifacts()` - Move to archive
8. `generate_markdown()` - Create AAR.md
9. Timeline update (if available)

### 2. Conversation End (`n5_conversation_end.py`)
**Purpose:** Formal conversation close with file organization
**Entry Points:**
- Recipe: "Close Conversation"
- Direct: `python3 n5_conversation_end.py --convo-id [id]`

**Core Flow:**
- **Phase 0**: Generate AAR with title (calls thread export OR inline generation)
- **Phase 1**: Analyze workspace (conversation_end_analyzer.py)
- **Phase 2**: Propose organization (conversation_end_proposal.py)
- **Phase 3**: Execute organization (conversation_end_executor.py)
- **Phase 4**: Checks (git, placeholders, output review, build archive)
- **Phase 5**: Registry closure (update conversations.db)
- **Phase 6**: Archive promotion (copy to Documents/Archive if significant)

### 3. Title Generation (`n5_title_generator.py`)
**Purpose:** Generate descriptive thread titles
**Entry Points:**
- From thread export
- From conversation end (fallback)
- Direct: `python3 n5_title_generator.py --aar [path]`

**Core Logic:**
1. Load AAR JSON + artifacts
2. Analyze conversation content
3. Generate 3-5 title options
4. Select best (or present for selection)
5. Save to PROPOSED_TITLE.md

**Title Format:** `MMM DD | [emoji] [Entity] [Action] [#N]`

### 4. Supporting Components
- `n5_title_generator_local.py` - Fallback generator
- `conversation_end_analyzer.py` - Workspace analysis
- `conversation_end_proposal.py` - Organization proposals
- `conversation_end_executor.py` - File operations
- `n5_archive_threads.py` - Thread archive compression
- `timeline_automation.py` - Timeline updates

## Critical Dependencies

### Title Generation Dependencies:
1. AAR JSON exists with valid structure
2. Artifacts array populated
3. Emoji legend loaded (`N5/config/emoji-legend.json`)
4. Conversation ID available
5. Session state readable (fallback path)

### Conversation End Dependencies:
1. Thread export successful OR inline AAR generation works
2. Title generated and saved
3. Database accessible (`N5/data/conversations.db`)
4. Registry update successful

## Known Failure Points

### Title Generation Issues:
1. **Empty/invalid AAR data** → Generates garbage titles
2. **Missing artifacts** → Can't infer conversation type
3. **Session state fallback fails** → No title generated
4. **Emoji legend missing** → Uses default emoji
5. **Title format validation missing** → Allows "System Work Work"

### Conversation End Issues:
1. **Thread export failure** → Falls back to inline, may skip title
2. **PROPOSED_TITLE.md not created** → No title in registry
3. **Registry update fails** → Title not persisted
4. **Phase ordering** → Title generation happens too early (before all context)

## Testing Strategy

### Unit Tests Needed:
1. Title generator with various AAR structures
2. Title generator with empty/minimal data
3. Title format validation
4. AAR generation (inline vs thread export)
5. Session state extraction
6. Registry update operations
7. File organization proposals
8. Archive promotion logic

### Integration Tests Needed:
1. Full thread export → title generation → save
2. Full conversation end → all phases → registry
3. Thread export → conversation end (sequential)
4. Fallback paths (thread export fails → inline works)
5. Edge cases (empty workspace, no artifacts, minimal session state)

### End-to-End Tests:
1. Realistic conversation simulation
2. Multiple conversation types (build, research, discussion)
3. Large workspace (100+ files)
4. Minimal workspace (SESSION_STATE.md only)

## Root Cause Hypothesis

**Primary Issue:** Title generation receives incomplete/malformed AAR data

**Evidence:**
- PROPOSED_TITLE.md shows "System Work Work" (repeated noun)
- Reasoning shows "Default (no specific indicators detected)"
- Title generation happens in Phase 0, before full context available

**Likely Causes:**
1. AAR generated before workspace fully analyzed
2. Artifacts not populated when title generator runs
3. Session state extraction incomplete
4. Title generator doesn't validate output quality
5. No retry mechanism when title is garbage

**Fix Strategy:**
1. Move title generation to AFTER workspace analysis
2. Validate title quality (detect duplicates, minimum content)
3. Add retry with more context if first attempt fails
4. Ensure AAR + artifacts fully populated before title generation
5. Add explicit title validation step
