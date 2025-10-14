# Email Follow-Up Generator — Sandbox Test Setup

**Date:** 2025-10-13 18:00 ET  
**Test Subject:** Hamoon Ekhtiari (FutureFit)  
**Status:** ✅ READY FOR SANDBOX TEST

---

## System Loaded

### Core Components
- ✅ `file 'N5/commands/follow-up-email-generator.md'` (v11.0.0)
- ✅ `file 'N5/prefs/communication/voice.md'` (v3.0.0)
- ✅ `file 'N5/prefs/communication/essential-links.json'` (v1.7.0)

### Test Data Available
- ✅ **Stakeholder Profile:** `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/stakeholder_profile.md'`
- ✅ **Meeting Transcript:** `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/transcript.txt'` (21,501 chars)
- ✅ **Detailed Recap:** `file 'N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit/detailed_recap.md'` (2,332 chars)

### Previous Test Outputs
- `follow_up_email_DRAFT.md` (831 bytes)
- `follow_up_email_DRAFT_ORIGINAL.md` (1,009 bytes)
- `follow_up_email_NEW_v11.md` (3,204 bytes)
- `follow_up_email_v11-1_TEST.md` (6,802 bytes)

---

## System Capabilities (v11.0.0)

### Enhancement 4: Enhanced Dial Mapping + Resonant Details ⭐⭐⭐⭐
- WarmthScore (0-10) calculation from personal anecdotes, humor, shared values
- FamiliarityScore (0-10) from prior meetings, shared context, inside jokes
- Maps to voice.md scale (0-4): Stranger/New Contact/Warm Contact/Partner/Inner Circle
- Resonance Pool extraction with confidence scores and emotional tone

### Enhancement 3: Readability Guardrails ⭐⭐⭐
- Flesch-Kincaid Grade Level ≤ 10
- Average Sentence Length: 16-22 words
- Max Sentence Length: 32 words
- Max 4 sentences per paragraph

### Enhancement 2: Confidence-Based Link Insertion ⭐⭐
- Auto-insert links when confidence ≥ 0.75
- Mark uncertain links as [[MISSING: category]]
- Markdown inline format: `[text](URL)`

### Enhancement 1: Transcript Language Echoing ⭐
- Extract Vrijen's distinctive phrases (confidence ≥ 0.75)
- Incorporate max 2 phrases for voice authenticity

---

## Test Execution Steps

The system follows a 13-step workflow with Metaprompter v6 compliance:

1. **Step 0-0B:** Router-aligned file resolution + time capture
2. **Step 1:** Transcript parsing → Harvest Phase (ENHANCED with resonance extraction)
3. **Step 1B:** Transcript Language Echoing
4. **Step 2:** Essential Link Autofill → Link Map (ENHANCED with confidence scoring)
5. **Step 3:** Auto-Dial Inference (ENHANCED with warmth/familiarity scoring)
6. **Step 4:** Socratic Expansion & Content Confirmation
7. **Step 4B:** Iterative Parsing Loop (if needed)
8. **Step 5:** Relationship & Style Calibration
9. **Step 6:** Apply Master Voice Engine (ENHANCED with resonance integration)
10. **Step 6A:** Delay Check
11. **Step 6B:** Match V's Natural Conciseness (200-300 words)
12. **Step 7:** Subject Line Generation
13. **Step 7B:** Draft Email
14. **Step 8:** Self-Review & Risk Sweep
15. **Step 9:** Output Assembly
16. **Step 10:** Map-Archive Hook
17. **Step 11:** Edge-Case Handling

---

## Test Context: Hamoon Ekhtiari

**Company:** FutureFit (futurefit.ai)  
**Meeting Date:** 2025-10-10  
**Days Elapsed:** 3 days (within normal follow-up window)  
**Relationship Stage:** First meeting, exploratory partnership  
**Priority:** Normal  
**Next Step:** Send follow-up within 2 weeks with 1-2 concrete use cases

**Expected Dials:**
- **Relationship Depth:** 1-2 (New Contact → Warm Contact)
- **Formality:** Balanced
- **CTA Rigour:** Balanced
- **WarmthScore:** ~5-6 (first meeting, professional warmth)
- **FamiliarityScore:** ~2-3 (first meeting, some rapport)

---

## Expected Outputs

1. **subjectLine** — Format: "Follow-Up Email – Hamoon x Careerspan [keyword1 • keyword2]"
2. **draftEmail** — 200-300 words, Markdown format with inline links
3. **voiceConfigUsed** — Applied voice settings
4. **dialInferenceReport** — ENHANCED with warmth/familiarity scores
5. **Missing-Content Map** — Uncertainties flagged
6. **Link Map** — ENHANCED with confidence scores
7. **Missing Links Array** — Low-confidence links for review
8. **Resonance Pool** — ENHANCED with emotional tone and usage flags
9. **SpeakerQuoteMap** — Verbatim quotes attributed
10. **phrasePool** — Vrijen's distinctive phrases extracted
11. **DiffCorrectionLog** — Revision tracking
12. **daysElapsed** — Time since meeting

---

## Sandbox Test Plan

### Option A: Full Pipeline Test
Run complete 13-step workflow with all enhancements activated.

### Option B: Component Test
Test individual enhancements (resonance extraction, dial mapping, link confidence).

### Option C: Comparison Test
Generate new email and compare against existing test outputs.

---

## Ready for Execution

**Input Required from V:**
1. Which test mode? (A, B, or C)
2. Use transcript.txt or detailed_recap.md as source?
3. Any dial overrides for testing?
4. Where to save test output?

---

**System Status:** ✅ All dependencies loaded and validated  
**Next:** Await V's test execution command
