---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
---

# Socratic Voice System

Build Pangram-resistant content generation through Socratic extraction + voice synthesis

## Objective

Generate V-voice content that passes AI detection (<50% Pangram score) by extracting spoken articulation and arranging (not composing) using voice library patterns

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| W1_socratic_trial | socratic_extraction_trial | pending | - | 1h |
| W2_corpus_analysis | linkedin_corpus_analysis | pending | - | 2h |

## Key Decisions

- Socratic extraction BEFORE any generation
- Paragraph-level chunks (3-5 sentences) preserve human token distribution
- Tightening factor: 'Would V text this to a friend?'
- Voice library sources: LinkedIn corpus (385 posts) + Canon articles

## Relevant Files

- `N5/prefs/communication/socratic-articulation-protocol.md`
- `N5/builds/voice-library-v2/linkedin_corpus.jsonl`
- `Knowledge/voice-library/voice-primitives.md`
- `Knowledge/positions/worldview/talent-optionality-thesis.md`
- `Personal/Knowledge/Canon/VibeThinker/`
- `Knowledge/content-library/social-posts/linkedin/`
