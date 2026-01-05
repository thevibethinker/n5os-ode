---
description: Process a reflection into structured blocks (R01-R09) and file to canonical location
tags: [reflection, orchestrator, blocks]
tool: true
---

# Process Reflection

**Purpose:** Transform raw reflection input (text or audio) into structured intelligence blocks.

## How to Invoke

- **Chat:** `@Process Reflection` or `@Process Reflection [filename]`
- **Text/SMS:** "Process reflection" or "Process reflection [filename]"

## Input Resolution

### Step 1: Check for Direct Input
If a filename or path is provided, use that directly.

### Step 2: Check Local Folder (Primary)
Look in `Inbox/Voice Thoughts/` for unprocessed files:
```bash
ls -la /home/workspace/Inbox/Voice\ Thoughts/
```
If audio/text files exist, process the most recent one.

### Step 3: Check Google Drive (Fallback)
If local folder is empty or file not found:
```
Folder ID: 116Myv-EXxf8P8udqIh_zlbMk2uJtnD90
Account: attawar.v@gmail.com
```
Use `google_drive-list-files` to find unprocessed files, then `google_drive-download-file` to fetch.

### Step 4: Ask User
If no files found in either location, ask which reflection to process.

## Processing Flow

### For Audio Files (.m4a, .mp3, .wav)
1. **Transcribe** using `transcribe_audio` tool
2. **Read transcript** to get full text
3. Continue to block generation

### For Text Files (.txt, .md)
1. **Read file** directly
2. Continue to block generation

## Block Generation

### Detection Guide

Scan the reflection for signals:

| Block | Trigger Signals |
|-------|----------------|
| R01 Personal | "I feel", "I realized", "struggling with", "grateful", emotional language |
| R02 Learning | "I learned", "interesting insight", book/article/conversation references |
| R03 Strategic | "Careerspan should", "positioning", "long-term", company direction |
| R04 Market | Competitor names, "the market", "trend", industry observations |
| R05 Product | "We could build", "feature", user feedback, product ideas |
| R06 Synthesis | Cross-domain connections, "this connects to", emergent patterns |
| R07 Prediction | "I predict", "will happen", "in 5 years", future states |
| R08 Venture | "Startup idea", "someone should build", non-Careerspan business ideas |
| R09 Content | "Blog post about", "should write", "people need to hear", content ideas |
| R00 Emergent | Meaningful content that doesn't fit R01-R09 |

### Generation Rules
- Generate **only blocks that have substantive content**
- Use individual block prompts from `Prompts/Blocks/Reflection/`
- If content doesn't fit, use R00 with provisional framework
- Preserve V's voice — don't over-polish

## Output Structure

Create folder at: `Personal/Reflections/YYYY/MM/YYYY-MM-DD_<slug>/`

```
Personal/Reflections/2026/01/2026-01-04_productivity-in-ai-age/
├── source.m4a          # Original audio (moved here)
├── transcript.md       # Full transcript with YAML frontmatter
└── analysis.md         # R-blocks output
```

### Slug Generation
- If file has descriptive name → use it (kebab-case)
- If timestamp-named → use first 5 words of transcript (kebab-case)

### transcript.md Format
```markdown
---
created: YYYY-MM-DD
source: [original filename]
duration: [if available]
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
blocks_generated: [R01, R03, R07]
provenance: [conversation_id]
---

# Reflection Analysis: [Title]

[Date] | [Duration if known]

---

## R01: Personal Insight
[Block content]

---

## R03: Strategic Thought
[Block content]

---

## R07: Prediction
[Block content]

---

## Processing Notes
- Blocks generated: R01, R03, R07
- R00 generated: No
- Source archived: Yes
```

## Post-Processing

1. **Move source file** from input folder to output folder
2. **Confirm completion** with summary:
   - Title/slug
   - Blocks generated
   - Output location
   - Any R00 flags for review

## Quality Standards

- Preserve V's voice — don't over-polish raw thought
- Be selective — only generate blocks with real content
- Title should capture the essence, not be generic
- If R00 is generated, flag it for potential new block type
- If the reflection is thin, say so honestly

## Configuration

See `file 'N5/prefs/reflection_engine_config.md'` for input paths and settings.
See `file 'N5/prefs/reflection_blocks_v2.md'` for block registry.

