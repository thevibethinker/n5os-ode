---
created: 2026-02-04
last_edited: 2026-02-04
version: 2.0
provenance: con_1kVhshgDe0iYErkj
status: draft
---

# Resume:Decoded Template Sketch v2

Incorporating temporal signals + info layering + zero repetition.

---

## Info Layering System

| Layer | Encoding | Meaning |
|-------|----------|---------|
| **Bold text** | `**skill**` | Story-verified (highest confidence) |
| Regular text | `skill` | Resume/profile-backed |
| *Italic text* | `*skill*` | Inferred (lowest confidence) |
| Years in parens | `(4y)` | Time spent practicing this skill |
| Gradient bar | `████` | Importance × rarity (visual weight) |
| ▲/▼ | Arrow | Strength vs gap |

This replaces the ✓✓/✓ markers — bold IS the verification signal.

---

## Temporal Signals to Extract

From work history + Careerspan data:

| Signal | Source | Where to Show |
|--------|--------|---------------|
| Total years exp | Resume | Candidate header |
| IC vs Mgmt split | Role titles over time | Candidate header: "6y IC · 2.5y Mgmt" |
| Years per skill | Role durations × skill use | Spikes: "**MLOps** (4y)" |
| Trajectory | Title progression | Header: "↑ IC→Lead→Staff" or "→ Lateral" |
| Tenure pattern | Avg time at companies | Risk section if short |
| Recency | When skill last used | Fade/dim if >3y ago |

---

## Page 1: The Decision Page (v2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESUME:DECODED                          [Careerspan logo] × [Partner logo] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                           HARDIK PATEL                                      │
│                      AI Engineer Candidate                                  │
│                                                                             │
│          8.5y exp · 6y IC · 2.5y Tech Lead · ↗ IC→Lead trajectory          │
│          Keysight (4y) → AmEx (3y) → Stealth (1.5y)                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AT A GLANCE  [bold = story-verified]                                       │
│  ───────────────────────────────────────────────────────────────────────    │
│                                                                             │
│   ▲ **MLOps 0→1** (4y)    ▲ **Enterprise scale** (3y)   ▲ RAG/LLM (1.5y)   │
│     ████████████            ██████████                    ████████          │
│                                                                             │
│   ▲ **Cross-fn delivery** (5y)    ▲ Cost optimization (2y)                  │
│     █████████                       ███████                                 │
│                                                                             │
│   ▼ Node.js (0y)          ▼ *Early-stage pace*          ▼ Consumer UX (0y) │
│     ██████ [gap]            █████ [unknown]               ████ [gap]        │
│                                                                             │
│   gradient = importance × scarcity for this role                            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  👍 TAKE THIS MEETING                                         87/100  │  │
│  │  ─────────────────────────────────────────────────────────────────    │  │
│  │  Rare 0→1 builder with 4 years proving it at enterprise scale.        │  │
│  │  30 min reveals: can he ship "good enough" at startup pace?           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├───────────────────────────────────┬─────────────────────────────────────────┤
│                                   │                                         │
│  ⚠ WHAT TO PROBE                  │  ✦ WHY HIM                              │
│  ────────────────                 │  ─────────                              │
│                                   │                                         │
│  Pace & perfectionism             │  Builds platforms, not features         │
│  Enterprise muscle may slow him.  │  **Keysight ML infra went from his     │
│  Ask for "shipped ugly" examples. │  laptop to Apple/Samsung in 18mo.**    │
│                                   │                                         │
│  Stack ramp                       │  Finds problems before they're tickets  │
│  Zero Node.js. Python/Java only.  │  **Both major stories start with "I    │
│  4-8 week ramp realistic.         │  noticed..." not "I was assigned..."** │
│                                   │                                         │
│  Retention risk                   │  Owns outcomes, not tasks               │
│  Ambitious. 2.5y avg tenure.      │  **Drove $2M savings without being     │
│  Needs clear path to Staff+.      │  asked. Self-directed roadmap work.**  │
│                                   │                                         │
│  [no overlap with spikes above]   │  [narrative only — not skill lists]    │
│                                   │                                         │
├───────────────────────────────────┴─────────────────────────────────────────┤
│                                                                             │
│  SIGNAL STRENGTH                                                            │
│  ──────────────────────────────────────────────────────────────────────     │
│  ████████████████████████████████████████░░░░░░░░░░░░░░ 78% story-verified │
│                                                                             │
│  Higher % = assessment based on demonstrated behavior, not claimed skills.  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Resume:Decoded by Careerspan × CorridorX · Docsum · Feb 2026            1 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What changed from v1:**
- Candidate header now has temporal signals (IC/Mgmt split, trajectory, tenure history)
- Years in parentheses on every spike
- Bold = story-verified (no more ✓✓ markers)
- Italic = inferred/unknown
- "Risks" renamed "What to Probe" (action-oriented)
- "Strengths" renamed "Why Him" (direct)
- Strengths column is **narrative only** — no skill overlap with spikes
- Signal strength collapsed to single bar (78% tells the story)

---

## Page 2: The Prep Page (v2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RESUME:DECODED                          [Careerspan logo] × [Partner logo] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔍 BEHAVIORAL EVIDENCE                                                     │
│  ──────────────────────────────────────────────────────────────────────     │
│  What we learned from structured stories — not resume claims.               │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  How he finds work                                                    │  │
│  │  Observes friction → builds solution → sells it internally.           │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │ "I noticed teams were provisioning oversized databases because   │  │  │
│  │  │  the tooling made it easier to over-request than right-size."    │  │  │
│  │  └──────────────────────────────── Keysight, Year 2 ───────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  How he solves problems                                               │  │
│  │  Zooms out before optimizing. Fixes root cause, not symptom.          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │ "Everyone wanted to fine-tune the model. I asked why we were     │  │  │
│  │  │  hitting the API for the same queries repeatedly."               │  │  │
│  │  └──────────────────────────────── AmEx, Year 1 ───────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❓ YOUR 30 MINUTES                                                         │
│  ──────────────────────────────────────────────────────────────────────     │
│  Questions that probe the gaps from Page 1.                                 │
│                                                                             │
│  ┌──────────────────────────────────┬──────────────────────────────────────┐│
│  │                                  │                                      ││
│  │  → Pace & perfectionism          │  → Stack ramp                        ││
│  │  "Tell me about something you    │  "How would you approach our TS      ││
│  │  shipped that you weren't proud  │  codebase in week one? What's your   ││
│  │  of. What trade-off did you      │  learn-by-doing pattern?"            ││
│  │  make and why?"                  │                                      ││
│  │                                  │                                      ││
│  ├──────────────────────────────────┼──────────────────────────────────────┤│
│  │                                  │                                      ││
│  │  → Retention & ambition          │  → Dealbreaker check                 ││
│  │  "Where do you want to be in     │  "We can't offer equity until        ││
│  │  3 years? What would make you    │  Series A. Is that a blocker?"       ││
│  │  stay vs leave?"                 │                                      ││
│  │                                  │                                      ││
│  └──────────────────────────────────┴──────────────────────────────────────┘│
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📊 IF YOU NEED...                                                          │
│  ──────────────────────────────────────────────────────────────────────     │
│                                                                             │
│  A 0→1 platform builder              ✓  4y doing exactly this at Keysight  │
│  Shipping production code by Day 30  ⚠  Maybe. Ramp + pace are unknowns    │
│  Deep Node.js/TS from Day 1          ✗  No. Python/Java background only    │
│  Someone who stays 4+ years          ⚠  Possible if path to Staff is clear │
│  Consumer product instincts          ✗  No signal. All B2B/enterprise      │
│  Self-directed technical leader      ✓  **Strong signal across 3 roles**   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ─────────────────────────────────────────────────────────────────────────  │
│  2 structured interviews · 45 skills · 78% story-verified                   │
│                        Powered by Careerspan                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Resume:Decoded by Careerspan × CorridorX · Docsum · Feb 2026            2 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**What changed from v1:**
- Behavioral signals now have temporal anchors ("Keysight, Year 2")
- Interview questions directly reference Page 1 risks with arrows (→)
- Dealbreakers folded into questions (not separate section)
- Trade-off table uses bold for story-verified confidence
- Years of evidence woven into trade-off verdicts ("4y doing exactly this")
- Methodology footer is minimal (one line)

---

## Repetition Eliminated

| Previously repeated | Now lives in ONE place |
|--------------------|------------------------|
| Skill names | Spikes only (Page 1 top) |
| Verification markers | Bold = verified (everywhere) |
| Signal strength % | Single bar (Page 1) + footer (Page 2) |
| Risk items | "What to Probe" column only |
| Strength items | "Why Him" column only (narrative, not skills) |
| Interview topics | Questions section only (arrows link to risks) |

---

## Layering Examples

**Single spike, maximum info density:**
```
▲ **MLOps 0→1** (4y)
  ████████████
```
- `▲` = strength (not a gap)
- `**bold**` = story-verified
- `(4y)` = 4 years practicing this
- `████████████` = high importance × high rarity for this role

**Single gap, maximum info density:**
```
▼ *Early-stage pace* 
  █████ [unknown]
```
- `▼` = gap/risk
- `*italic*` = inferred (no direct evidence)
- no years = we can't measure time on this
- `[unknown]` label = explicitly flagging uncertainty

**Trade-off row with temporal context:**
```
A 0→1 platform builder    ✓  4y doing exactly this at Keysight
```
- Verdict (✓/⚠/✗) + years of evidence in one line

---

## Temporal Signals Summary

**Header block:**
```
8.5y exp · 6y IC · 2.5y Tech Lead · ↗ IC→Lead trajectory
Keysight (4y) → AmEx (3y) → Stealth (1.5y)
```

**Embedded in spikes:**
```
▲ **MLOps 0→1** (4y)
▲ RAG/LLM (1.5y)  ← less time, shown via years
▼ Node.js (0y)    ← zero experience, explicit
```

**In behavioral quotes:**
```
└──────────────────────────────── Keysight, Year 2 ───────────────┘
```

**In trade-off verdicts:**
```
✓  4y doing exactly this at Keysight
```

---

## Design Principles (Updated)

1. **Every element earns its space** — no decorative content
2. **Info layering over repetition** — bold/italic/years encode, don't repeat
3. **Temporal signals are first-class** — years matter, show them
4. **Narrative vs skill separation** — spikes = skills, columns = stories
5. **Forward references** — Page 2 questions arrow-link to Page 1 risks
6. **Uncertainty is explicit** — italic + [unknown] label, not hidden

---

## Open Questions

1. **Recency fade** — Should skills >3 years old get dimmed? (e.g., "Python (5y, last: 2023)")
2. **Tenure pattern** — 2.5y avg tenure is a signal. Where does it live?
3. **Management scope** — "2.5y Tech Lead" but how many reports? Where to show?
4. **Skill overlap detection** — How to ensure spikes ≠ "Why Him" content automatically?

---

*Ready for V's feedback.*
