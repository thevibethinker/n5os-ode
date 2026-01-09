# Worker Assignment: w14_orchestrator

**Project:** r-block-framework  
**Component:** process_reflection (Master Orchestrator)  
**Dependencies:** ALL other workers (w01-w13)  
**Output:** `Prompts/Process Reflection.prompt.md`

---

## Objective

Rewrite **Process Reflection** as the master orchestrator that ties together all R-blocks and RIX.

## Pre-Requisites

ALL blocks must be complete:
- Base template: `N5/templates/reflection/r_block_base.md`
- Edge infrastructure: `N5/scripts/reflection_edges.py`
- R00-R09: `Prompts/Blocks/Reflection/R*.prompt.md`
- RIX: `Prompts/Blocks/Reflection/RIX_Integration.prompt.md`

## Orchestration Flow

```
Input Resolution
      ↓
Word Count Gate (<100 = lightweight capture only)
      ↓
Transcript Classification (which blocks are relevant?)
      ↓
Parallel R-Block Dispatch (run relevant R01-R09)
      ↓
RIX Integration (always runs)
      ↓
Output Assembly (combine blocks into final output)
      ↓
File to Canonical Location
```

## Input Resolution

### Priority Order:
1. **Direct file mention** in invocation
2. **Inbox/Voice Thoughts/** for recent audio
3. **Google Drive** (configured folder ID)
4. **Ask user** if ambiguous

### Supported Formats:
- `.txt`, `.md` → direct read
- `.m4a`, `.mp3`, `.wav` → transcribe first
- Google Doc → download and convert

## Classification Logic

### Trigger Words by Block:

| Block | Trigger Patterns |
|-------|------------------|
| R01 Personal | "I feel", "frustrated", "excited", "energy", "identity" |
| R02 Learning | "learned", "realized", "now I understand", "gap in" |
| R03 Strategic | "we should", "direction", "bet on", "opportunity cost" |
| R04 Market | "competitors", "market", "customers are", "trend" |
| R05 Product | "feature", "build", "users want", "MVP" |
| R06 Synthesis | "connects to", "pattern", "framework", "like when" |
| R07 Prediction | "will happen", "in 5 years", "I predict" |
| R08 Venture | "someone should build", "business idea", non-Careerspan |
| R09 Content | "blog post", "should write", "people need to hear" |

### Classification Output:
```json
{
  "relevant_blocks": ["R03", "R04", "R05"],
  "confidence": {"R03": 0.9, "R04": 0.8, "R05": 0.6},
  "primary_theme": "strategic product discussion"
}
```

## Parallel Dispatch

For each relevant block:
1. Read the block prompt
2. Apply to transcript
3. Generate block output
4. Collect results

## RIX Integration

ALWAYS runs after R-blocks:
1. Takes transcript + R-block outputs as input
2. Queries memory profiles
3. Creates edges
4. Produces integration narrative

## Output Assembly

### Final Output Structure:
```
Personal/Reflections/YYYY/MM/YYYY-MM-DD_<slug>/
├── transcript.md      # Original input
├── analysis.md        # Combined analysis with all blocks
├── R03_strategic.md   # Individual block output (if generated)
├── R04_market.md      # Individual block output (if generated)
├── RIX_integration.md # Always present
└── manifest.json      # Metadata about processing
```

### manifest.json:
```json
{
  "slug": "recruiter-game-plan",
  "processed_at": "2026-01-09T11:45:00Z",
  "word_count": 847,
  "blocks_generated": ["R03", "R04", "RIX"],
  "edges_created": 5,
  "source": "google_drive",
  "source_id": "1Ze852..."
}
```

## Prompt Structure

The rewritten `Process Reflection.prompt.md` should include:

1. **Frontmatter** with description, tags, tool: true
2. **How to Invoke** section
3. **Input Resolution** section
4. **Word Count Gate** section
5. **Classification Logic** section (with trigger words table)
6. **Block Reference** section (links to all R-blocks)
7. **RIX Reference** section
8. **Output Structure** section
9. **Quality Standards** section
10. **Worked Example** (end-to-end)

## Completion Criteria

- [ ] Complete orchestration flow documented
- [ ] Input resolution handles all sources
- [ ] Classification logic with trigger words
- [ ] Links to all R-block prompts
- [ ] RIX always-run behavior explicit
- [ ] Output structure with manifest.json
- [ ] Quality standards preserved (V's voice, selectivity)
- [ ] Worked example included
- [ ] 300+ lines (this is the master prompt)

---

**When complete:** Run `python3 N5/scripts/build_orchestrator_v2.py complete --project r-block-framework --worker w14_orchestrator`
