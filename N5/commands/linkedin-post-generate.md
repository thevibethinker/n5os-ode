# linkedin-post-generate

**Version**: 1.0.0  
**Status**: ✅ Production  
**Category**: Content Generation | Personal Brand  
**Import Date**: 2025-10-09

---

## Purpose

Generate professional, voice-authentic LinkedIn posts that sound unmistakably like Vrijen while delivering substantive insight and driving engagement.

---

## Usage

### Basic

```bash
linkedin-post-generate
```

**Interactive mode**: Prompts for seed content and preferences.

### With Seed Content

```bash
linkedin-post-generate --seed "Your transcript, notes, or idea here"
```

### With Dial Overrides

```bash
linkedin-post-generate --seed "Content" --formality balanced --cta-rigour direct
```

### Full Options

```bash
linkedin-post-generate \
  --seed "Your seed content" \
  --mode thought-leadership \
  --formality casual|balanced|formal \
  --cta-rigour soft|balanced|direct \
  --relationship-depth 0-4 \
  --target-length 300 \
  --output-format markdown|json
```

---

## Parameters

### Required

- `--seed` (string): Transcript, notes, or idea prompt (50-5000 tokens)

### Optional

- `--mode` (string): Generation mode
  - Default: `thought-leadership`
  - Future: `comedic`, `example-driven`

- `--formality` (string): Tone formality level
  - Options: `casual`, `balanced`, `formal`
  - Default: Auto-inferred from seed content
  
- `--cta-rigour` (string): Call-to-action directness
  - Options: `soft`, `balanced`, `direct`
  - Default: Auto-inferred from seed content
  
- `--relationship-depth` (int): Audience familiarity level
  - Range: 0-4 (0=strangers, 4=close colleagues)
  - Default: Auto-inferred from seed content

- `--target-length` (int): Target word count
  - Range: 150-400
  - Default: 300

- `--output-format` (string): Output format
  - Options: `markdown`, `json`
  - Default: `markdown`

---

## Outputs

### Files Created

```
Knowledge/personal-brand/social-content/linkedin/
├── YYYY-MM-DD-HHmm-post-draft.md           # Ready-to-paste post
├── YYYY-MM-DD-HHmm-post-metadata.json      # Voice config, metrics
└── YYYY-MM-DD-HHmm-post-analysis.md        # Quality report
```

### Console Output

```
✅ LinkedIn Post Generated Successfully

📄 Post Draft: Knowledge/personal-brand/social-content/linkedin/2025-10-09-2049-post-draft.md

📊 Metrics:
   - Word Count: 287
   - Readability (FK Grade): 10.2
   - CTAs: 2
   - Stop Verbs Detected: 0

🎛️ Voice Config Used:
   - Formality: balanced (confidence: 0.85)
   - Relationship Depth: 2 (confidence: 0.78)
   - CTA Rigour: balanced (confidence: 0.82)

🔍 Validation: PASSED ✅
```

---

## How It Works

### 10-Step Process

1. **Input Validation**: Verify seed content and parameters
2. **Voice Schema Resolution**: Load `voice.md` (v3.1.0), `content-library.json`, `linkedin-stop-verbs.json`
3. **Seed Content Parsing**: Extract key ideas, stats, anecdotes, linguistic patterns
4. **Auto-Dial Inference**: Detect formality, warmth, CTA rigour (unless overridden)
5. **Structure Selection**: Choose post format (story, stat-lead, contrarian take)
6. **Hook Crafting**: Create compelling first line
7. **Voice Engine Application**: Apply distinctive verbs, signature phrases, em-dashes, readability guards
8. **CTA Crafting**: Generate 1-2 context-appropriate calls-to-action
9. **Self-Review**: Validate readability, stop-verbs, structural quality, voice consistency
10. **Output Assembly**: Generate files and display summary

### Voice Integration

**Primary Source**: `N5/prefs/communication/voice.md` (v3.1.0 - UPDATED)

**Mapping**:
- Formality levels → `voice.md` "Formality Levels" section
- Relationship depth → `voice.md` "Relationship Depth Scale" section
- Distinctive verbs → `voice.md` "Lexicon" section (preferred/avoid verbs)
- **Signature phrases** → `voice.md` "Signature Phrases" section (40+ documented)
- **Em-dash usage** → `voice.md` "Punctuation Style" section
- CTA patterns → `voice.md` "Follow-Up Type Rules" section
- Readability rules → `voice.md` "Readability Optimization" section
- **Structure patterns** → `voice.md` "Email Structure Patterns" section

**Word Count Targets (Aligned with Email System):**
- LinkedIn post: 250-350 words (standard thought leadership)
- Short-form post: 150-200 words (quick takes)
- Long-form post: 350-450 words (deep dives, rare)

**Prohibited Language**: `N5/prefs/communication/linkedin-stop-verbs.json`

**Voice Consistency Rules:**
1. Use signature phrases from voice.md where natural
2. Apply em-dash usage for rhythm (V's signature style)
3. Maintain tone weights (warmth 0.80-0.85, confidence 0.72-0.80, humility 0.55-0.65)
4. Use lexicon preferences (tackle not "go after", resonate not "makes sense")
5. Keep concise—V's natural style is compressed

### Validation Rules

**Must Pass**:
- ✅ Flesch-Kincaid Grade Level ≤ 12
- ✅ Average sentence length ≤ 32 words (prefer 16-22)
- ✅ Word count: 150-450 (target: 250-350 for standard)
- ✅ CTA count: 1-2
- ✅ Stop-verbs: ≤ 2 occurrences
- ✅ Hook present (compelling first line)
- ✅ **Voice consistency**: Signature phrases used naturally
- ✅ **Em-dash usage**: Present (V's signature)

**Warnings** (non-blocking):
- ⚠️ Dial confidence < 0.70 → prompts user confirmation
- ⚠️ Readability close to limits (FK = 11-12)
- ⚠️ CTA placement awkward

---

## Examples

### Example 1: Basic Thought Leadership

**Input**:
```
"I just realized that most career coaches focus on helping people get jobs, 
but rarely help them stay engaged once they're in role. We need to rethink 
retention as part of career development, not just an HR problem."
```

**Output** (excerpt):
```
Most career support stops at the offer letter.

We celebrate when someone lands a new role. We optimize resumes, prep for 
interviews, negotiate offers. Then... silence.

But the hard part isn't getting the job. It's staying engaged six months in 
when the novelty fades and you're wondering if you made the right choice.

Retention isn't an HR metric—it's a career development outcome. If we only 
help people jump ship when they're miserable, we're missing the entire middle 
game of career satisfaction...

[CTA: What's your take? Should career coaches focus more on retention?]
```

### Example 2: With Dial Overrides

**Input**:
```bash
linkedin-post-generate \
  --seed "AI is eating software dev jobs" \
  --formality formal \
  --cta-rigour direct \
  --relationship-depth 1
```

**Output Characteristics**:
- More measured language (formal)
- Direct CTA (e.g., "DM me to discuss")
- Minimal personal anecdotes (low relationship depth)

---

## Integration with N5

### Prefs Dependencies

- ✅ `N5/prefs/communication/voice.md` (v3.0)
- ✅ `N5/prefs/communication/content-library.json` (v1.7)
- ✅ `N5/prefs/communication/linkedin-stop-verbs.json` (v1.0)

### Knowledge Output

All generated posts are cataloged in:
```
Knowledge/personal-brand/social-content/linkedin/
```

This directory represents a **knowledge asset** (catalog of social media work output), not N5 OS infrastructure.

### Command Registry

Registered in: `N5/config/commands.jsonl`

```json
{
  "command": "linkedin-post-generate",
  "file": "N5/commands/linkedin-post-generate.md",
  "description": "Generate voice-authentic LinkedIn posts with auto-dial inference",
  "script": "N5/scripts/n5_linkedin_post_generate.py"
}
```

---

## Implementation

**Orchestrator**: `N5/scripts/n5_linkedin_post_generate.py`

**Approach**: Script-based orchestrator (Python 3.12)

**Key Functions**:
- `load_voice_schema()` → Parse voice.md
- `infer_dials()` → Auto-detect formality, warmth, CTA rigour
- `generate_hook()` → Craft compelling first line
- `apply_voice_engine()` → Transform seed → post draft
- `craft_ctas()` → Generate context-appropriate CTAs
- `validate_output()` → Readability + quality checks

---

## Troubleshooting

### Issue: "Dial confidence < 0.70"

**Cause**: Seed content too short or ambiguous for auto-inference.

**Solution**: Provide explicit dial overrides or add more context to seed.

### Issue: "Readability validation failed"

**Cause**: Generated post exceeds FK grade 12 or sentence length 32.

**Solution**: Script auto-retries up to 3 times with simplified language.

### Issue: "Stop-verbs detected"

**Cause**: Prohibited LinkedIn clichés in output.

**Solution**: Script auto-retries with alternative verbs. Check `linkedin-stop-verbs.json` for list.

---

## Future Enhancements

### Tier 2: Comedic Mode
- `--mode comedic`
- Humor intensity dial (0-5)
- Template library integration
- Sincerity outro option

### Tier 3: Analyzer + Learning
- `linkedin-post-analyze` command
- Blueprint extraction from existing posts
- Style learning from example library
- Template-based generation

---

## Version History

### v1.0.0 (2025-10-09)
- ✅ Initial release
- ✅ Thought-leadership mode
- ✅ Auto-dial inference
- ✅ Voice.md v3.0 integration
- ✅ Readability validation
- ✅ CTA crafting
- ✅ Stop-verbs filtering

---

## Related Commands

- `follow-up-email-generator` → Email follow-ups with voice integration
- `deliverable-generate` → Content generation for client deliverables
- `careerspan-timeline` → Company timeline and milestones

---

## Source

**External Function**: LinkedIn Thought Leadership Post Generator v1.2  
**Import Framework**: Function Import System v1.0  
**Archive**: `N5/knowledge/external-functions/linkedin/`
