---
created: 2026-01-09
last_edited: 2026-01-12
version: 1.1
title: Pangram
description: Ad-hoc AI detection calibration using Pangram (not an automatic gate)
tags: [integration, voice, writing, ai-detection]
tool: true
---

# Pangram AI Detection (Ad-Hoc)

Use Pangram to **calibrate** outputs when you’re testing or diagnosing “sounds too AI.”  
**Not part of the automatic generation pipeline**.

## Commands

```bash
# Quick check (pass/fail)
python3 /home/workspace/Integrations/Pangram/pangram.py check "TEXT"
python3 /home/workspace/Integrations/Pangram/pangram.py check --file path/to/file.md

# Detailed analysis
python3 /home/workspace/Integrations/Pangram/pangram.py analyze "TEXT" --verbose
```

> Optional: If you want guided interpretation inside Zo, use `@Pangram Check` and paste the draft.

## Interpretation Guidelines

- **Strong pass:** `fraction_ai < 0.3` (30%)
- **Borderline:** `0.3–0.5`
- **High AI signal:** `> 0.5`

## Recommended Workflow (No Auto-Loops)

1. Generate content normally (with Voice Injection Layer active where applicable)
2. If you’re unsure / testing: run a Pangram check (ad-hoc)
3. If score is high: apply targeted edits (voice primitives, specificity, sentence rhythm), then re-check if desired

## Related Files

- Voice system: `file 'N5/prefs/communication/voice-transformation-system.md'`
- Transformation pairs: `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'`
- Hedging patterns: `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'`
- Ad-hoc helper: `file 'Prompts/Pangram Check.prompt.md'`


