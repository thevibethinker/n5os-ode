---
created: 2026-01-04
last_edited: 2026-01-04
version: 2.0
type: build_plan
status: complete
provenance: con_zGQhfwqIoAIKek4Q
---

# Plan: Reflection Engine v2

**Objective:** Replace 17 Python scripts with a prompt-driven, ad-hoc reflection processor where the LLM (Zo) is the engine.

**Trigger:** V requested destruction of the legacy automated pipeline and replacement with manual, local processing.

**Key Design Principle:** The LLM IS the engine. Scripts handle file I/O. Prompts define the semantic contract. Same model as Meeting Blocks.

---

## Open Questions

- [x] **Block Namespace:** Keep B50-B99 or create new R-series? → **Decision needed from V**
- [x] **Canonical Home:** Where do processed reflections live? → **Decision needed from V**
- [x] **Input Types:** Text only, or also handle audio transcription? → **Decision needed from V**

---

## Checklist

### Phase 0: Destruction & Archival ✅ COMPLETE
- ☑ Copy legacy scripts to `N5/archive/legacy_reflection_system/scripts/` (17 scripts)
- ☑ Copy legacy prompts to `N5/archive/legacy_reflection_system/prompts/` (7 prompts)
- ☑ Copy registry and configs to `N5/archive/legacy_reflection_system/prefs/`
- ☑ Delete all `reflection_*.py` from `N5/scripts/`
- ☑ Delete legacy prompts from `Prompts/`
- ☑ Clean `Records/reflections/` staging folders
- ☑ Create canonical home: `Personal/Reflections/`

### Phase 1: Block Definition ✅ COMPLETE
- ☑ Create `Prompts/Blocks/Reflection/` directory
- ☑ Create individual block prompts (R01-R06)
- ☑ Define which blocks are "core" vs "optional"
- ☑ Create registry at `N5/prefs/reflection_blocks_v2.md`

### Phase 2: Orchestrator ✅ COMPLETE
- ☑ Create `Prompts/Process Reflection.prompt.md` — The single entry point
- ☑ Orchestrator reads input, selects applicable blocks, generates them
- ☑ Output: Structured markdown with frontmatter, filed to canonical location

---

## Phase 0: Destruction & Archival

### Affected Files
- `N5/scripts/reflection_*.py` (17 files) - ARCHIVE then DELETE
- `Prompts/Reflection Auto Ingest.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Worker.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Pipeline.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Ingest.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Email Orchestrator.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Pull Gdrive.prompt.md` - ARCHIVE then DELETE
- `Prompts/Reflection Synthesizer.prompt.md` - ARCHIVE then DELETE
- `N5/prefs/reflection_block_registry.json` - ARCHIVE (keep reference)
- `N5/capabilities/internal/reflection-pipeline-v1.md` - ARCHIVE then DELETE
- `N5/config/reflection-sources.json` - ARCHIVE then DELETE (if exists)
- `Records/reflections/incoming/` - CLEAR contents
- `Records/reflections/processing_manifest.json` - DELETE

### Changes

**0.1 Archive All Legacy Artifacts:**
Copy everything to `N5/archive/legacy_reflection_system/` before deletion.

**0.2 Delete From Active Locations:**
Remove all reflection_*.py scripts and legacy prompts.

**0.3 Clear Staging Folders:**
Empty `Records/reflections/incoming/` but keep the directory structure.

### Unit Tests
- `ls N5/scripts/reflection*` returns no results
- `ls Prompts/ | grep -i "reflection"` returns only the new `Process Reflection.prompt.md` (after Phase 2)
- Archive folder contains all 17 scripts

---

## Phase 1: Block Definition

### Affected Files
- `Prompts/Blocks/Reflection/` - CREATE directory
- `Prompts/Blocks/Reflection/R01_Personal.prompt.md` - CREATE
- `Prompts/Blocks/Reflection/R02_Learning.prompt.md` - CREATE
- `Prompts/Blocks/Reflection/R03_Strategic.prompt.md` - CREATE
- `Prompts/Blocks/Reflection/R04_Market.prompt.md` - CREATE
- `Prompts/Blocks/Reflection/R05_Product.prompt.md` - CREATE
- `Prompts/Blocks/Reflection/R06_Synthesis.prompt.md` - CREATE
- `N5/prefs/reflection_blocks_v2.md` - CREATE (simple markdown registry)

### Changes

**1.1 New Block Taxonomy (Simplified):**
Reduce from 11 block types to 6 core types:

| Block | Name | What It Captures |
|-------|------|------------------|
| R01 | Personal Insight | Emotional, growth, self-awareness |
| R02 | Learning Note | Insights from reading, conversations, research |
| R03 | Strategic Thought | Vision, positioning, long-term thinking |
| R04 | Market Signal | Competitive intel, trends, opportunities |
| R05 | Product Idea | Features, roadmap, user insights |
| R06 | Synthesis | Cross-reflection patterns, meta-thinking |

**1.2 Block Prompt Structure:**
Each block prompt follows the Meeting Block pattern:
```markdown
---
description: Generate R01 Personal Insight block from reflection
tags: [reflection, block, r01]
tool: true
---
# Generate Block R01: Personal Insight

**Input:** Reflection text provided in conversation context

**Your task:** Generate an R01 Personal Insight block...

## Output Format
[Define structure]

## Quality Standards
[Define standards]
```

**1.3 Registry (Simple Markdown):**
Create `N5/prefs/reflection_blocks_v2.md` — a human-readable registry that the orchestrator references.

### Unit Tests
- All 6 block prompts exist in `Prompts/Blocks/Reflection/`
- Registry file is valid markdown with all blocks listed

---

## Phase 2: Orchestrator

### Affected Files
- `Prompts/Process Reflection.prompt.md` - CREATE (the main entry point)

### Changes

**2.1 The Orchestrator Prompt:**
Single prompt that:
1. Accepts reflection input (text or transcript)
2. Reads the block registry to understand available types
3. Analyzes input to determine which blocks are applicable
4. Generates the relevant blocks inline
5. Assembles final output with YAML frontmatter
6. Files to canonical location

**2.2 Invocation Pattern:**
V types: `@Process Reflection` and pastes/provides the reflection text.
Zo processes and outputs structured blocks.

**2.3 Output Structure:**
```markdown
---
created: YYYY-MM-DD
type: reflection
source: voice_memo | text | journal
blocks_generated: [R01, R03]
provenance: con_xxx
---

# Reflection: [Title derived from content]

## R01: Personal Insight
[Generated content]

## R03: Strategic Thought  
[Generated content]
```

### Unit Tests
- Invoke `@Process Reflection` with sample text
- Output contains valid YAML frontmatter
- At least one block is generated
- File is created in canonical location

---

## Success Criteria

1. **Legacy system fully expunged:** Zero `reflection_*.py` scripts in `N5/scripts/`
2. **New system functional:** `@Process Reflection` successfully processes text into blocks
3. **Architecture matches Meetings:** Block prompts in `Prompts/Blocks/Reflection/`, single orchestrator
4. **No scheduled agents:** System is purely ad-hoc, triggered by V

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Losing useful block definitions | Archive `reflection_block_registry.json` before deletion |
| Style guide orphaning | Keep style guides in place; new system references same files |
| Input variety (audio vs text) | Orchestrator handles both; uses Zo's transcription if needed |

---

## Alternatives Considered (Nemawashi)

### Alternative A: Keep B50-B99 Namespace
**Pros:** Continuity with legacy, no namespace collision
**Cons:** Carries baggage of failed system, 11 types is too many

### Alternative B: New R-Series Namespace (Recommended)
**Pros:** Clean break, simplified taxonomy (6 vs 11), distinct from Meeting blocks (B-series)
**Cons:** Slight learning curve

### Alternative C: Merge Into Meeting System
**Pros:** Single unified block system
**Cons:** Reflections are fundamentally different from meetings; would complect the system

**Recommendation:** Alternative B — R-Series with 6 core blocks

---

## Trap Doors (Irreversible Decisions)

| Decision | Reversibility | Notes |
|----------|---------------|-------|
| Deleting 17 scripts | LOW | Archived, but rebuilding would be painful |
| Block namespace (R vs B) | MEDIUM | Could rename later, but affects all historical data |
| Canonical folder location | MEDIUM | Moving files later is tedious |

---

## Level Upper Review

*(Pending — invoke if V wants divergent thinking before build)*




