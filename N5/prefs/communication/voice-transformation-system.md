---
created: 2025-10-22
last_edited: 2026-01-09
version: 3.0
provenance: con_u6YvYuTdjQcOJPLC
---

# V Voice Transformation System

**Version:** 3.0  
**Method:** Few-shot transformation learning (research-backed)  
**Architecture:** Platform-aware with shared core + platform-specific profiles

---

## System Overview

This system produces text in V's authentic voice using **transformation-based learning** rather than attribute lists. The LLM learns by studying before/after examples (neutral → V-voice), then applies that transformation to new content.

### Why Transformation > Attributes

| Approach | Problem |
|----------|---------|
| "Be professional but warm" | Vague, inconsistent results |
| "Use 70% formality" | Arbitrary, hard to calibrate |
| **Transformation pairs** | LLM learns the *process*, not just adjectives |

---

## Architecture

```
voice-transformation-system.md (this file)
├── Core Identity & Dimensions
├── Hedging Kill Rules
├── Compression Test
│
├── platforms/
│   ├── x.md ← X/Twitter voice (profanity OK, punchy, spicy)
│   └── linkedin.md ← LinkedIn voice (no profanity, authoritative)
│
└── style-guides/
    ├── transformation-pairs-library.md ← Platform-agnostic pairs
    ├── succinctness-pairs.md ← Verbose → Direct transformations
    ├── hedging-antipatterns.md ← Comprehensive kill list
    ├── directness-calibration.md ← Context-appropriate directness
    └── pangram-signals.md ← AI detection signals & optimization
```

---

## Core Voice Identity

**In one sentence:** Direct, specific, warmth-through-substance communicator who earns authority through evidence and trusts the reader.

### Dimension Baselines

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Directness** | 0.80 | Assertions over hedging; specific over vague |
| **Warmth** | 0.65 | Comes from genuine interest, not soft language |
| **Confidence** | 0.85 | Earned through specificity and evidence |
| **Humor** | 0.50 | Dry, observational; never try-hard |
| **Formality** | 0.55 | Professional but human; no corporate speak |

### Platform Modifiers

| Platform | Directness | Profanity | Length | Humor |
|----------|------------|-----------|--------|-------|
| **X/Twitter** | +0.05 | ✅ Natural | Short (<140) | +0.20 |
| **LinkedIn** | Base | ❌ Never | Long (500+) | Base |
| **Email** | Base | ❌ Never | Medium | Base |
| **Docs** | -0.05 | ❌ Never | Full | -0.10 |

---

## The Transformation Process

### Step 1: Detect Content Type

Classify the generation request:
- Platform (X, LinkedIn, Email, Doc, DM)
- Purpose (thought leadership, follow-up, ask, intro, etc.)
- Relationship context (cold, warm, established)

### Step 2: Load Relevant Pairs

Pull transformation pairs matching the content type:

```
Platform: X + Purpose: hot-take
→ Load: platforms/x.md (signature patterns, anti-patterns)
→ Load: transformation-pairs-library.md (tag: thought-leadership)
```

### Step 3: Generate Style-Free Draft

Write content with zero style — pure information and structure.

### Step 4: Apply Transformation

Transform the draft using loaded pairs as few-shot examples. The LLM pattern-matches the transformation process.

### Step 5: Validate Against Anti-Patterns

Check output against:
- Hedging patterns (kill list)
- Platform-specific anti-patterns
- Length/format constraints

---

## Hedging Kill Rules

**V's voice is assertive.** The following patterns signal hedging and must be eliminated or transformed:

### Instant Kill (Delete)

- "I was wondering if..."
- "Just wanted to..."
- "I hope this finds you well"
- "No rush, but..."
- "Sorry to bother you"
- "If you don't mind..."
- "When you get a chance..."

### Transform (Replace)

| Hedge | → Direct |
|-------|----------|
| "I think maybe we could..." | "Let's..." |
| "It might be worth considering..." | "Consider:" |
| "I feel like..." | [State directly] |
| "Does that make sense?" | [End with confidence] |
| "Let me know what you think" | "Let me know by [date]" |

### Contextual (Sometimes OK)

- "I think" — OK when genuinely uncertain
- "might" — OK for genuine contingency
- Softeners — OK in high-stakes disagreement (soften with logic, not filler)

**Full kill list:** `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'`

---

## V-Voice Compression Test

Before any output, apply these filters:

1. **Cut the first sentence.** Often throat-clearing.
2. **Delete "just," "maybe," "probably."** Usually add nothing.
3. **Replace "I think" with assertion.** Either you believe it or you don't.
4. **Add a deadline or specific time.** "Soon" = never.
5. **Read it aloud.** If you'd never say it, don't write it.

---

## Platform Profiles

### X/Twitter

**File:** `file 'N5/prefs/communication/platforms/x.md'`

**Summary:**
- Profanity: Natural (9.4% of tweets)
- Length: Punchy — 46% under 100 chars
- Tone: Sharp, self-aware wit, contrarian edge
- Signature patterns: Devastating Analogy, Toxic Trait, Em-Dash Pivot
- Anti-patterns: LinkedIn energy, engagement bait, emoji overload

### LinkedIn

**File:** `file 'N5/prefs/communication/platforms/linkedin.md'`

**Summary:**
- Profanity: Never
- Length: Developed (500+ chars typical)
- Tone: Authoritative, warm, measured
- Signature patterns: (Awaiting corpus analysis)
- Status: Placeholder — awaiting data export

---

## Transformation Pairs

### Core Library

**File:** `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'`

Contains platform-agnostic pairs for:
- Email (intros, follow-ups, asks, updates)
- Feedback (disagreement, critique, recommendations)
- LinkedIn (thought leadership, origin stories)
- DMs (quick asks, networking)
- Closings

### Succinctness Pairs

**File:** `file 'N5/prefs/communication/style-guides/succinctness-pairs.md'`

15 category pairs modeling V's desired evolution:
- Meeting requests
- Email follow-ups
- Introductions & outreach
- Opinions & feedback
- Status updates
- Asks & offers
- Closings

### Directness Calibration

**File:** `file 'N5/prefs/communication/style-guides/directness-calibration.md'`

Context-appropriate directness scores:
- When to soften (genuinely uncertain, high-stakes disagreement)
- When to stay hard (asks, updates, follow-ups)
- Relationship-based adjustments

---

## Anti-Pattern Index

### Global Anti-Patterns

❌ Corporate jargon: "synergy", "leverage", "paradigm"  
❌ Formulaic hooks: "Here's why...", "Let me explain..."  
❌ Desperate/pushy language  
❌ Over-apology  
❌ Stacked qualifiers  

### Platform-Specific Anti-Patterns

**X:** `file 'N5/prefs/communication/platforms/x.md'` → Anti-Patterns section  
**LinkedIn:** `file 'N5/prefs/communication/platforms/linkedin.md'` → (Pending)

### Hedging Anti-Patterns

**Full reference:** `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'`

Includes regex patterns for automated detection.

---

## Prompt Integration

### Auto-Application Rule

When generating ANY user-facing text (emails, posts, documents, DMs):

1. **Detect platform/context**
2. **Load this system** + platform profile + relevant pairs
3. **Generate style-free draft**
4. **Apply transformation**
5. **Validate against kill rules**
6. **Run compression test**
7. **(Optional) Pangram check** — For high-stakes comms, test against AI detection

### Pangram AI Detection Check

For important communications, validate output doesn't read as AI-generated:

```bash
python3 /home/workspace/Integrations/Pangram/pangram.py check "output text"
```

**Target:** `fraction_ai < 0.3` (30%)

**If failing, apply fixes from:** `file 'N5/prefs/communication/style-guides/pangram-signals.md'`

**Quick fixes that lower AI score:**
- Add specific dollar amounts or numbers
- Vary sentence length dramatically (include 2-4 word sentences)
- Break template structure with organic filler
- Add one personality marker per paragraph
- Replace generic references with specifics

### Context Loading

The `writer` category in `n5_load_context.py` loads:
- This file (voice-transformation-system.md)
- Relevant platform profile
- Transformation pairs library
- Hedging anti-patterns

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0 | 2026-01-09 | Platform profiles architecture, X corpus analysis, succinctness pairs, hedging kill list, compression test |
| 2.0 | 2025-10-22 | System-wide transformation, multi-angle, hybrid structure |
| 1.0 | 2025-10-17 | Initial social media voice profile |

---

## Related Files

| Purpose | File |
|---------|------|
| X voice profile | `file 'N5/prefs/communication/platforms/x.md'` |
| LinkedIn profile | `file 'N5/prefs/communication/platforms/linkedin.md'` |
| Core pairs | `file 'N5/prefs/communication/style-guides/transformation-pairs-library.md'` |
| Succinctness | `file 'N5/prefs/communication/style-guides/succinctness-pairs.md'` |
| Hedging kill list | `file 'N5/prefs/communication/style-guides/hedging-antipatterns.md'` |
| Directness | `file 'N5/prefs/communication/style-guides/directness-calibration.md'` |
| System prompt | `file 'N5/prefs/communication/voice-system-prompt.md'` |



