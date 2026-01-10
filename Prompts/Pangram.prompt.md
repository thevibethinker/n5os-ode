---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
title: Pangram
description: Test text against Pangram AI detection API to optimize voice transformation
tags: [integration, voice, writing, ai-detection]
tool: true
---

# Pangram AI Detection

Test text against Pangram's AI detection API. Use this to iterate on voice transformation until outputs score as human-written.

## Commands

```bash
# Quick check (pass/fail)
python3 /home/workspace/Integrations/Pangram/pangram.py check "TEXT"
python3 /home/workspace/Integrations/Pangram/pangram.py check --file path/to/file.md

# Detailed analysis
python3 /home/workspace/Integrations/Pangram/pangram.py analyze "TEXT" --verbose

# Iteration mode (shows what needs work)
python3 /home/workspace/Integrations/Pangram/pangram.py iterate "TEXT" --target 0.3
```

## Target

- **Pass:** `fraction_ai < 0.3` (30%)
- Exit code 0 = human-like, Exit code 1 = AI-detected

## Voice Iteration Workflow

When testing voice transformation output:

1. Generate text using voice transformation system
2. Run through Pangram: `pangram.py check "generated text"`
3. If FAIL, use `pangram.py iterate "text"` to see problem segments
4. Apply transformation pairs to fix flagged segments
5. Re-test until passing

## What Passes vs Fails

**Passes (human-like):**
- Specific numbers and dollar amounts
- Short, varied sentence lengths
- Questions mid-paragraph
- Contractions (You'll, Can we)
- Em-dashes and informal punctuation
- Personal voice markers

**Fails (AI-detected):**
- Smooth, balanced prose
- Corporate vocabulary (leverage, synergy, robust)
- Formulaic structures
- Overly consistent sentence rhythm
- Signposting language (In conclusion, Furthermore)

## Related Files

- Voice system: `file 'N5/prefs/communication/voice-transformation-system.md'`
- Transformation pairs: `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'`
- Hedging patterns: `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'`

