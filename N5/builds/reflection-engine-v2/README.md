---
created: 2026-01-10
last_edited: 2026-01-10
version: 1.0
provenance: con_6qD38032W4IsQjVH
---

# Reflection Engine v2

Transform raw thoughts (text or audio) into structured intelligence blocks with knowledge graph integration.

## Quick Start

### Option 1: Direct Paste (Simplest)
```
@Process Reflection

[paste your reflection text here]
```

### Option 2: From File
```
@Process Reflection file 'Inbox/Voice Thoughts/my-thoughts.txt'
```

### Option 3: From Audio
Drop an `.m4a` or `.mp3` file in `Inbox/Voice Thoughts/`, then:
```
@Process Reflection file 'Inbox/Voice Thoughts/recording.m4a'
```
Zo will transcribe automatically before processing.

---

## How It Works

```
┌─────────────────────┐
│  Input              │
│  (text, audio, file)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Process Reflection │  ← Main orchestrator prompt
│  (classification)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Block Generation   │  ← R-block prompts (R00-R09)
│  (selective)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RIX Integration    │  ← Always runs last
│  (edges + memory)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Output Assembly    │
│  → Personal/        │
│    Reflections/     │
└─────────────────────┘
```

---

## Block Reference

| Block | Name | When Generated |
|-------|------|----------------|
| R00 | Emergent | Content that doesn't fit R01-R09 |
| R01 | Personal Insight | Emotional awareness, growth, self-reflection |
| R02 | Learning Note | Insights from reading, conversations, research |
| R03 | Strategic Thought | Vision, positioning, long-term thinking |
| R04 | Market Signal | Competitive intel, trends, opportunities |
| R05 | Product Idea | Features, roadmap, user insights |
| R06 | Synthesis | Cross-reflection patterns, meta-thinking |
| R07 | Prediction | Trend forecasts, future scenarios |
| R08 | Venture Idea | Ideas separate from Careerspan |
| R09 | Content Idea | Ideas for posts, articles, content |
| RIX | Integration | Edge creation + memory links (always runs) |

---

## Output Structure

```
Personal/Reflections/
└── 2026/
    └── 01/
        └── 2026-01-09_recruiter-game-plan-queries/
            ├── manifest.json     # Metadata
            ├── transcript.md     # Source text
            └── analysis.md       # Generated blocks
```

### manifest.json
```json
{
  "id": "2026-01-09_recruiter-game-plan-queries",
  "created": "2026-01-09T12:45:00Z",
  "source_type": "voice_memo",
  "blocks_generated": ["R03", "R04", "R05", "RIX"]
}
```

### analysis.md
```markdown
---
created: 2026-01-09
source: transcript.md
blocks_generated: [R03, R04, R05, RIX]
edges_created: 4
---

# Reflection Analysis: [Title]

## R03: Strategic Thought
[Generated content...]

## R04: Market Signal
[Generated content...]
```

---

## Input Sources

| Source | Path | Notes |
|--------|------|-------|
| Local text | `Inbox/Voice Thoughts/*.txt` | Plain text files |
| Local audio | `Inbox/Voice Thoughts/*.m4a` | Auto-transcribed |
| Google Drive | Configured folder | If enabled in config |
| Direct paste | In conversation | Just start typing |

---

## Edge System

Reflections connect to other content via the edge graph:

```bash
# View edge statistics
python3 N5/scripts/reflection_edges.py stats

# Find edges from a reflection
python3 N5/scripts/reflection_edges.py from 2026-01-09_recruiter-game-plan-queries

# Add an edge manually
python3 N5/scripts/reflection_edges.py add \
  --from reflection:2026-01-09_recruiter-game-plan-queries \
  --to position:candidate-ownership-thesis \
  --type EXTENDS \
  --confidence high
```

### Edge Types
- `EXTENDS` — Builds on previous thought
- `SUPPORTS` — Provides evidence for
- `CONTRADICTS` — Challenges or conflicts with
- `REFINES` — Clarifies or narrows
- `ENABLES` — Makes possible

---

## Troubleshooting

### "No blocks generated"
- Input may be too short or vague
- Try adding more context or detail

### "Transcription failed"
- Check audio file format (m4a, mp3, wav supported)
- Ensure file isn't corrupted

### "File not found"
- Use full path or relative to workspace root
- Check for typos in filename

### "Edge creation failed"
- Verify target exists (position, knowledge article)
- Check edge type is valid

---

## Configuration

- **Block registry:** `N5/prefs/reflection_blocks_v2.md`
- **Engine config:** `N5/prefs/reflection_engine_config.md`
- **Edge data:** `N5/data/reflection_edges.jsonl`

---

## Related

- `Prompts/Process Reflection.prompt.md` — Main orchestrator
- `Prompts/Blocks/Reflection/` — Individual block prompts
- `Personal/Reflections/` — Output location

