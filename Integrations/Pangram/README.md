---
created: 2026-01-09
last_edited: 2026-01-09
version: 1.0
provenance: con_7RlbUBiDe5JU2Rlf
---

# Pangram AI Detection Integration

Test text against Pangram's AI detection API to optimize voice transformation protocols.

## Purpose

Use Pangram as a feedback loop to iterate on V's voice transformation system until outputs consistently score as human-written (< 30% AI).

## Setup

API key is already configured in Settings > Developers as `PANGRAM_API_KEY`.

## Usage

```bash
# Quick pass/fail check
python3 /home/workspace/Integrations/Pangram/pangram.py check "Your text here"
python3 /home/workspace/Integrations/Pangram/pangram.py check --file draft.md

# Detailed analysis with segment breakdown
python3 /home/workspace/Integrations/Pangram/pangram.py analyze "Text" --verbose

# Iteration-focused analysis (what needs work)
python3 /home/workspace/Integrations/Pangram/pangram.py iterate "Text" --target 0.3

# Custom threshold
python3 /home/workspace/Integrations/Pangram/pangram.py check "Text" --threshold 0.25
```

## Threshold

- **Target:** `fraction_ai < 0.3` (30%)
- **Exit code 0** = Pass (human-like)
- **Exit code 1** = Fail (AI-detected)

## Key Findings

From initial testing:

| Text Type | AI Score | Result |
|-----------|----------|--------|
| Corporate jargon ("leverage", "synergy") | 100% | FAIL |
| Generic follow-up email | 90%+ | FAIL |
| V's LinkedIn post (from transformation pairs) | 0% | PASS |

**What passes:**
- Specific dollar amounts and numbers
- Short, punchy sentences
- Questions mid-paragraph
- Contractions ("You'll", "Can we")
- Cadence variation
- Personal voice markers

**What fails:**
- Smooth, flowing prose
- Formulaic structures
- Corporate vocabulary
- Overly balanced sentence lengths

## Integration with Voice System

The voice transformation system is at:
- `file 'N5/prefs/communication/voice-transformation-system.md'`
- `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'`

Use Pangram to:
1. Test generated outputs before sending
2. Identify which transformation pairs produce human-like text
3. Iterate on pairs that consistently fail
4. Build a library of "Pangram-safe" patterns

## API Reference

Endpoint: `POST https://text.api.pangram.com/v3`

Response fields:
- `fraction_ai` - Overall AI score (0.0 - 1.0)
- `fraction_human` - Overall human score
- `windows[]` - Segment-level breakdown with `ai_assistance_score`

