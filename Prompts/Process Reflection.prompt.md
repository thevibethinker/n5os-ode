---
description: Master orchestrator for processing reflections into structured R-blocks with memory integration
tags:
  - reflection
  - orchestrator
  - blocks
  - memory
  - edges
tool: true
version: 3
---
# Process Reflection — Master Orchestrator

**Purpose:** Transform raw reflection input (text or audio) into structured intelligence blocks (R01-R09), always run integration analysis (RIX), and file to canonical location with knowledge graph edges.

---

## 1. How to Invoke

### Chat/Claude Code
```
@Process Reflection
@Process Reflection [filename]
@Process Reflection [Google Doc title]
```

### Text/SMS
```
Process reflection
Process reflection [filename]
```

### With Options
```
@Process Reflection --skip-audio   # Skip transcription, text only
@Process Reflection --dry-run      # Preview without writing files
@Process Reflection --blocks R03,R04,R05  # Force specific blocks
```

---

## 2. Orchestration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT RESOLUTION                         │
│  Direct file → Local folder → Google Drive → Ask user       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     WORD COUNT GATE                          │
│  < 100 words = lightweight capture only                      │
│  ≥ 100 words = full processing                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 TRANSCRIPT CLASSIFICATION                    │
│  Scan for trigger patterns → Identify relevant blocks        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               PARALLEL R-BLOCK DISPATCH                      │
│  Load relevant block prompts → Generate each block           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                 RIX INTEGRATION (ALWAYS)                     │
│  Query memory → Create edges → Pattern detection             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT ASSEMBLY                           │
│  Combine blocks → Write files → Create manifest              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Input Resolution

### Priority Order

1. **Direct file mention** in invocation
2. **Local inbox** (`Inbox/Voice Thoughts/`)
3. **Google Drive** (configured folder)
4. **Ask user** if ambiguous or empty

### Step 1: Check for Direct Input
```python
if invocation_includes_path:
    return resolve_path(invocation_path)
```

### Step 2: Check Local Folder (Primary)
```bash
ls -la /home/workspace/Inbox/Voice\ Thoughts/
```
Process the most recent unprocessed file.

### Step 3: Check Google Drive (Fallback)
```
Folder ID: 116Myv-EXxf8P8udqIh_zlbMk2uJtnD90
Account: attawar.v@gmail.com
```
Use `google_drive-list-files` then `google_drive-download-file`.

### Step 4: Ask User
If no files found, prompt: "No reflections found. Which file should I process?"

### Supported Formats

| Format | Action |
|--------|--------|
| `.txt`, `.md` | Direct read |
| `.m4a`, `.mp3`, `.wav` | Transcribe with `transcribe_audio` tool |
| Google Doc | Download and convert to markdown |

---

## 4. Word Count Gate

After obtaining transcript, check word count:

| Word Count | Processing Mode |
|------------|-----------------|
| **< 100** | Lightweight capture — save transcript only, no blocks |
| **100-500** | Standard processing — generate applicable blocks |
| **500+** | Deep processing — full block analysis, comprehensive RIX |

### Lightweight Capture Output
```
Personal/Reflections/YYYY/MM/YYYY-MM-DD_<slug>/
├── transcript.md      # With frontmatter noting "lightweight capture"
└── manifest.json      # word_count, source, lightweight: true
```

---

## 5. Classification Logic

### Trigger Patterns by Block

| Block | ID | Trigger Patterns |
|-------|----|------------------|
| **Personal Insight** | R01 | "I feel", "frustrated", "excited", "energy", "identity", "struggle", "grateful" |
| **Learning Note** | R02 | "learned", "realized", "now I understand", "gap in", "insight", "reading about" |
| **Strategic Thought** | R03 | "we should", "direction", "bet on", "opportunity cost", "positioning", "long-term" |
| **Market Signal** | R04 | "competitors", "market", "customers are", "trend", "industry", pricing signals |
| **Product Idea** | R05 | "feature", "build", "users want", "MVP", "product idea", "should add" |
| **Synthesis** | R06 | "connects to", "pattern", "framework", "like when", "reminds me", "same as" |
| **Prediction** | R07 | "will happen", "in X years", "I predict", "expect", "bet on", future states |
| **Venture Idea** | R08 | "someone should build", "business idea", "startup", non-Careerspan opportunities |
| **Content Idea** | R09 | "blog post", "should write", "people need to hear", "thread", "content" |
| **Emergent** | R00 | Valuable content that doesn't fit R01-R09 |

### Classification Algorithm

```python
def classify_transcript(transcript: str) -> dict:
    triggers = {
        "R01": ["feel", "frustrated", "excited", "energy", "identity"],
        "R02": ["learned", "realized", "understand", "insight"],
        "R03": ["should", "direction", "bet", "opportunity", "strategic"],
        "R04": ["competitor", "market", "customer", "trend", "industry"],
        "R05": ["feature", "build", "users", "MVP", "product"],
        "R06": ["connects", "pattern", "framework", "reminds", "like"],
        "R07": ["will", "predict", "expect", "years", "future"],
        "R08": ["startup", "business idea", "someone should build"],
        "R09": ["blog", "write", "content", "publish", "thread"]
    }

    relevant = []
    confidence = {}

    for block, patterns in triggers.items():
        score = sum(1 for p in patterns if p.lower() in transcript.lower())
        if score >= 2:  # Threshold: 2+ triggers
            relevant.append(block)
            confidence[block] = min(score / len(patterns), 1.0)

    return {
        "relevant_blocks": sorted(relevant),
        "confidence": confidence,
        "primary_theme": identify_primary_theme(transcript)
    }
```

### Classification Output Example
```json
{
  "relevant_blocks": ["R03", "R04", "R05"],
  "confidence": {"R03": 0.9, "R04": 0.8, "R05": 0.6},
  "primary_theme": "strategic product discussion about market positioning"
}
```

---

## 6. Block Reference

Each block has a dedicated prompt with deep analytical framework:

| Block | Prompt File | Purpose |
|-------|-------------|---------|
| R00 | `Prompts/Blocks/Reflection/R00_Emergent.prompt.md` | Catch-all for novel content |
| R01 | `Prompts/Blocks/Reflection/R01_Personal.prompt.md` | Personal insights, emotions, identity |
| R02 | `Prompts/Blocks/Reflection/R02_Learning.prompt.md` | Knowledge acquisition, skill gaps |
| R03 | `Prompts/Blocks/Reflection/R03_Strategic.prompt.md` | Directional decisions, bets |
| R04 | `Prompts/Blocks/Reflection/R04_Market.prompt.md` | Market signals, competitive intel |
| R05 | `Prompts/Blocks/Reflection/R05_Product.prompt.md` | Feature ideas, user problems |
| R06 | `Prompts/Blocks/Reflection/R06_Synthesis.prompt.md` | Cross-domain patterns |
| R07 | `Prompts/Blocks/Reflection/R07_Prediction.prompt.md` | Future state hypotheses |
| R08 | `Prompts/Blocks/Reflection/R08_Venture.prompt.md` | Non-Careerspan business ideas |
| R09 | `Prompts/Blocks/Reflection/R09_Content.prompt.md` | Publishing opportunities |

### Block Dispatch Protocol

For each relevant block:
1. **Load** the block prompt: `file 'Prompts/Blocks/Reflection/R0X_Name.prompt.md'`
2. **Apply** framework to transcript
3. **Generate** block output following schema
4. **Collect** results for assembly

---

## 7. RIX Integration (Always Runs)

**Prompt:** `Prompts/Blocks/Reflection/RIX_Integration.prompt.md`

RIX is special — it **always runs** regardless of classification:

### RIX Responsibilities
1. **Extract key concepts** from transcript
2. **Query memory profiles** (positions, knowledge, meetings)
3. **Assess connections** for genuine relevance
4. **Create edges** in `N5/data/reflection_edges.jsonl`
5. **Detect patterns** (super-connectors, promotion candidates)
6. **Write integration narrative** contextualizing the reflection

### Edge Creation
```bash
python3 N5/scripts/reflection_edges.py add \
  --from "<reflection_slug>" \
  --to "<target_slug>" \
  --edge-type <EXTENDS|CONTRADICTS|SUPPORTS|REFINES|ENABLES> \
  --evidence "<quote>" \
  --confidence <high|medium|low>
```

### RIX Output Location
Always written to: `Personal/Reflections/YYYY/MM/YYYY-MM-DD_<slug>/RIX_integration.md`

---

## 8. Output Structure

### Canonical Location
```
Personal/Reflections/YYYY/MM/YYYY-MM-DD_<slug>/
```

### Full Output Structure
```
Personal/Reflections/2026/01/2026-01-09_recruiter-game-plan/
├── transcript.md           # Original input with frontmatter
├── analysis.md             # Combined R-block analysis
├── R03_strategic.md        # Individual block (if generated)
├── R04_market.md           # Individual block (if generated)
├── RIX_integration.md      # Always present
└── manifest.json           # Processing metadata
```

### Slug Generation Rules
1. If file has descriptive name → use it (kebab-case)
2. If timestamp-named → extract theme from first 5 significant words
3. Maximum 50 characters, lowercase, hyphens only

### transcript.md Format
```markdown
---
created: YYYY-MM-DD
source: [original filename]
source_type: [audio|text|gdoc]
duration: [if available]
word_count: [number]
provenance: [conversation_id]
---

# Transcript: [Title]

[Full transcript text]
```

### analysis.md Format
```markdown
---
created: YYYY-MM-DD
source: transcript.md
blocks_generated: [R03, R04, R05]
edges_created: 5
provenance: [conversation_id]
---

# Reflection Analysis: [Title]

**Date:** [YYYY-MM-DD] | **Duration:** [if known] | **Word Count:** [number]

---

## Classification

**Primary Theme:** [theme]
**Blocks Generated:** R03, R04, R05, RIX
**Confidence:** R03 (0.9), R04 (0.8), R05 (0.6)

---

## R03: Strategic Thought

[Block content following R03 output schema]

---

## R04: Market Signal

[Block content following R04 output schema]

---

## R05: Product Idea

[Block content following R05 output schema]

---

## RIX: Integration Analysis

[Block content following RIX output schema]

---

## Processing Notes

- **Blocks generated:** R03, R04, R05, RIX
- **R00 generated:** No
- **Edges created:** 5
- **Super-connectors flagged:** [list if any]
- **Promotion candidates:** [list if any]
```

### manifest.json Format
```json
{
  "slug": "recruiter-game-plan",
  "title": "Recruiter Game Plan",
  "processed_at": "2026-01-09T11:45:00Z",
  "word_count": 847,
  "source": "google_drive",
  "source_id": "1Ze852...",
  "source_filename": "voice_thought_2026-01-09.m4a",
  "blocks_generated": ["R03", "R04", "R05", "RIX"],
  "edges_created": 5,
  "classification": {
    "relevant_blocks": ["R03", "R04", "R05"],
    "confidence": {"R03": 0.9, "R04": 0.8, "R05": 0.6},
    "primary_theme": "strategic product discussion"
  },
  "flags": {
    "r00_generated": false,
    "super_connectors": [],
    "promotion_candidates": ["recruiter-trust-theme"]
  },
  "provenance": "conversation_abc123"
}
```

---

## 9. Quality Standards

### Voice Preservation
- **Preserve V's voice** — don't over-polish raw thought
- **Capture nuance** — hesitations and uncertainties are data
- **Avoid corporate-speak** — keep it real

### Selectivity
- **Only generate blocks with substantive content**
- **Don't force blocks** — if nothing fits, say so
- **Quality over quantity** — 2 strong blocks beats 5 weak ones

### Evidence Standards
- **Every claim needs a quote** — direct from transcript
- **No invented connections** — RIX edges require evidence
- **Confidence calibration** — be honest about uncertainty

### Thin Reflections
If a reflection is thin:
```markdown
## Processing Notes

This reflection is thin on extractable content. Generated only:
- Transcript (archived)
- RIX integration (minimal — 0 edges created)

Consider: Was this the right format for this thought?
```

---

## 10. Worked Example

### Input
```
File: Inbox/Voice Thoughts/2026-01-09_morning-thoughts.m4a
Duration: 4:32
```

### Step 1: Transcription
```
Thinking about the recruiter game plan again. The market is shifting — I keep seeing
these AI screening tools pop up. But here's what they're missing: the relationship
layer. Recruiters don't just match keywords, they build trust. Maybe we should build
something that helps recruiters demonstrate their value to candidates, not just
employers. Like a recruiter scorecard or trust metric. This connects to what I was
reading about in that trust-building article. I predict these AI tools will hit a wall
in 18 months when candidates start gaming them.
```
Word count: 98 (borderline, proceed with standard processing)

### Step 2: Classification
```json
{
  "relevant_blocks": ["R03", "R04", "R05", "R06", "R07"],
  "confidence": {"R03": 0.6, "R04": 0.9, "R05": 0.8, "R06": 0.5, "R07": 0.7},
  "primary_theme": "market analysis with product ideation"
}
```

### Step 3: Block Generation

**R04 (Market Signal):**
```markdown
## R04: Market Signal

**Signal:** AI screening tools proliferating but missing relationship layer
**Type:** Competitive Intelligence
**Confidence:** High
**Careerspan Relevance:** Direct

### The Signal
AI screening tools are entering the recruiter market but focus on keyword matching...
[continues per R04 schema]
```

**R05 (Product Idea):**
```markdown
## R05: Product Idea

**Idea:** Recruiter scorecard / trust metric for candidate-facing value
**Type:** Feature idea
**Urgency:** Medium

### The Problem
Recruiters lack tools to demonstrate value to candidates...
[continues per R05 schema]
```

**R07 (Prediction):**
```markdown
## R07: Prediction

**Prediction:** AI screening tools will plateau in 18 months
**Confidence:** Medium
**Timeframe:** 18 months

### Falsification Criteria
The prediction is WRONG if: AI tools show sustained adoption growth past mid-2027...
[continues per R07 schema]
```

### Step 4: RIX Integration
```markdown
## RIX: Integration Analysis

**Concepts Extracted:** recruiter, trust, AI screening, relationship, value demonstration
**Memory Hits:** positions: 2, knowledge: 1, meetings: 0
**Edges Created:** 3

### Edges Created
| From | To | Type | Evidence |
|------|----|------|----------|
| 2026-01-09_recruiter-game-plan | recruiter-trust-thesis | EXTENDS | "they build trust" |
| 2026-01-09_recruiter-game-plan | trust-building-article | SUPPORTS | "what I was reading about" |
| 2026-01-09_recruiter-game-plan | ai-tools-prediction-2025 | REFINES | "will hit a wall in 18 months" |

### Pattern Flags
- recruiter-trust-thesis: 6 edges (super-connector)
```

### Step 5: Output Assembly
```
Personal/Reflections/2026/01/2026-01-09_recruiter-game-plan/
├── transcript.md
├── analysis.md
├── R04_market.md
├── R05_product.md
├── R07_prediction.md
├── RIX_integration.md
└── manifest.json
```

### Step 6: Completion Summary
```
Processed: 2026-01-09_recruiter-game-plan
Location: Personal/Reflections/2026/01/2026-01-09_recruiter-game-plan/

Blocks generated:
  - R04: Market Signal (AI screening tools proliferating)
  - R05: Product Idea (Recruiter scorecard/trust metric)
  - R07: Prediction (AI tools plateau in 18 months)
  - RIX: Integration (3 edges created)

Flags:
  - Super-connector: recruiter-trust-thesis (6 edges)
  - Source archived: Yes
```

---

## 11. Configuration

### Input Paths
- Local: `Inbox/Voice Thoughts/`
- Google Drive: Folder ID `116Myv-EXxf8P8udqIh_zlbMk2uJtnD90`

### Edge Storage
- File: `N5/data/reflection_edges.jsonl`
- CLI: `N5/scripts/reflection_edges.py`

### Block Registry
- Location: `Prompts/Blocks/Reflection/`
- Pattern: `R0X_Name.prompt.md` and `RIX_Integration.prompt.md`

### Memory Profiles (for RIX)
- `positions` — V's stated beliefs and stances
- `knowledge` — Facts, articles, learnings
- `meetings` — Prior conversations

---

## 12. Error Handling

### No Files Found
```
No reflections found in local folder or Google Drive.
Options:
1. Specify a file path directly
2. Record a new voice thought
3. Check Google Drive sync
```

### Transcription Failure
```
Audio transcription failed for [filename].
Error: [error message]

Options:
1. Retry transcription
2. Check audio format (supported: m4a, mp3, wav)
3. Provide text version if available
```

### Classification Uncertainty
```
Classification uncertain — no blocks triggered with high confidence.

Transcript themes detected: [list]
Closest blocks: R0X (0.3), R0Y (0.2)

Options:
1. Process with detected blocks (lower confidence)
2. Skip block generation, archive transcript only
3. Force specific blocks with --blocks flag
```

---

*Template Version: 3.0 | R-Block Framework | 2026-01-09*
