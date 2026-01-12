---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_TBnwuolXxSkp5t1D
tool: true
description: Ad-hoc AI detection check using Pangram. Use for calibration, not during iteration.
tags:
  - voice
  - validation
  - pangram
  - ai-detection
---

# Pangram Check

Manual AI detection validation using the Pangram API. **Not part of automatic pipeline.**

---

## When to Use

✅ **Use for:**
- Before publishing high-stakes content (investor decks, major posts)
- Periodic voice calibration (weekly/monthly check on sample outputs)
- Testing if voice improvements are working (A/B compare before/after)
- Debugging when outputs feel "AI-ish"

❌ **Don't use for:**
- Every single piece of content (overkill, slows iteration)
- During drafting/iteration (breaks flow, adds friction)
- Internal notes or low-stakes content
- As a quality gate before sending emails (voice layer should handle this)

---

## Philosophy

The Voice Injection Layer makes Pangram checks mostly unnecessary. The layer automatically injects V's distinctive linguistic patterns, which naturally reduces AI detection scores.

Pangram is for **calibration**, not **validation**:
- If scores are consistently < 0.5, voice system is working
- If scores are consistently > 0.5, review primitive quality or add more to library
- Use periodically to verify, not on every output

---

## Usage

### Quick Check (Text)
```bash
python3 /home/workspace/Integrations/Pangram/pangram.py --text "Your content here"
```

### Check a File
```bash
python3 /home/workspace/Integrations/Pangram/pangram.py --file path/to/content.md
```

### Interactive (via Zo)
Just say: "@Pangram Check" and paste the content you want to analyze.

---

## Interpreting Results

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| < 0.3 | Very human-like | ✅ No action needed |
| 0.3 - 0.5 | Acceptable | ✅ Fine for most content |
| 0.5 - 0.7 | AI-ish | ⚠️ Consider revision for high-stakes content |
| > 0.7 | Strongly AI | 🔴 Apply novelty injection strategies |

**Target threshold:** < 0.5 for published content

---

## If Score is High

1. **Check primitive usage** — Were voice primitives injected? Run `python3 N5/scripts/retrieve_primitives.py --stats` to verify library health.

2. **Apply novelty injection** — Load strategies from `file 'N5/prefs/communication/style-guides/novelty-injection-prompts.md'`:
   - Strategy 1: Forced primitive injection (high-distinctiveness)
   - Strategy 2: Constraint prompting (domain lens shift)
   - Strategy 3: Multi-angle generation
   - Strategy 4: Socratic iteration
   - Strategy 5: Inversion prompt

3. **Review the content manually** — Sometimes AI detection flags verbose/generic phrasing. Simple edits (removing qualifiers, adding specifics) often help more than regeneration.

4. **Update voice library** — If scores are consistently high, extract new primitives from recent V content (meetings, emails) to refresh the library.

---

## Calibration Schedule

**Suggested cadence:**
- Weekly: Spot check 2-3 recent outputs
- Monthly: Full audit of 10+ outputs across content types
- Quarterly: Review primitive library health + extraction pipeline

**Track results in:** `N5/data/pangram_calibration.jsonl` (manual log)

---

## Related Tools

- **Voice Injection Layer:** `file 'N5/scripts/voice_layer.py'` — auto-injects primitives
- **Voice Post-Check:** `file 'N5/scripts/voice_postcheck.py'` — Pangram + injection suggestions
- **Novelty Injection:** `file 'N5/prefs/communication/style-guides/novelty-injection-prompts.md'`
- **Primitive Stats:** `python3 N5/scripts/retrieve_primitives.py --stats`

---

## Execution

When invoked, ask for the content to check, then run the Pangram analysis and return results with interpretation.

