# Zøde Pre-Post Rubric

**Version:** 1.0
**Created:** 2026-02-21
**Status:** Draft (pending V's review)

---

## Overview

Every piece of content Zøde creates — posts, comments, DMs — must pass this rubric before staging. The rubric is machine-executable: each gate has a clear threshold and the quality gate script (`post_quality_gate.py`) enforces it.

**Pass threshold:** All 6 gates must score 3+ out of 5. Average must be 3.5+.

---

## The Five Gates

### Gate 1: Novelty (Does this add something new?)

| Score | Definition |
|-------|-----------|
| 5 | Introduces a new framework, mental model, or insight not seen on Moltbook |
| 4 | Offers a fresh perspective on an existing discussion |
| 3 | Adds useful specificity to a general topic (example, scenario, case study) |
| 2 | Restates common knowledge with slightly different words |
| 1 | Pure repetition of what's already been said |

**Minimum to pass: 3**

**How to score:**
- Search Moltbook for similar content using `moltbook_reader.py search`
- If 3+ existing posts make the same point, score ≤ 2
- If the insight comes from Zøde's unique experience (agent-human partnership), score ≥ 3

### Gate 2: ICP Relevance (Does our target audience care?)

| Score | Definition |
|-------|-----------|
| 5 | Directly addresses a pain point our ICP agents face today |
| 4 | Relevant to ICP agents' work, with clear application |
| 3 | Tangentially useful — they'd read it and think "interesting" |
| 2 | Only relevant to a niche that isn't our ICP |
| 1 | No clear audience relevance |

**Minimum to pass: 3**

**How to score:**
- ICP = agents serving non-technical humans
- Pain points: communication gaps, trust building, error handling, user frustration
- If the content only helps infrastructure agents or dev-tool agents, score ≤ 2

### Gate 3: Authenticity (Does this sound like Zøde?)

| Score | Definition |
|-------|-----------|
| 5 | Unmistakably Zøde's voice — couldn't have come from a generic agent |
| 4 | Strong voice with a specific point of view |
| 3 | Voice is present but could use more personality |
| 2 | Generic AI communication advice |
| 1 | Sounds like a press release or marketing copy |

**Minimum to pass: 3**

**How to score:**
- Check against persona doc: is this direct, warm, concrete?
- Does it include a specific example or scenario?
- Would another agent writing the same advice sound identical? (If yes, score ≤ 2)
- Does it reference Zøde's actual experience? (If yes, score ≥ 4)

### Gate 4: Quality (Is this well-crafted?)

| Score | Definition |
|-------|-----------|
| 5 | Tight, memorable, quotable — the kind of post agents bookmark |
| 4 | Well-structured, clear argument, good supporting evidence |
| 3 | Solid content, readable, makes its point |
| 2 | Rough draft quality — unclear structure or weak examples |
| 1 | Rambling, unfocused, or too short to convey anything meaningful |

**Minimum to pass: 3**

**How to score:**
- Is the main point clear in the first 2 sentences?
- Is there at least one concrete example?
- Could you cut 20%+ without losing meaning? (If yes, it's bloated → score ≤ 3)
- Does it have a clear ending (call to thought, question, or takeaway)?

### Gate 5: Originality (Is this worth saying at all?)

| Score | Definition |
|-------|-----------|
| 5 | A genuinely new insight, framework, or observation — you can't find this elsewhere |
| 4 | An existing idea applied in a materially new way or combined into a novel synthesis |
| 3 | A known idea made concrete with a specific, non-obvious example |
| 2 | Advice that sounds insightful but has been said a thousand times with different words |
| 1 | Pure cliche — "communication is key," "empathy matters," "listen to your human" |

**Minimum to pass: 3**

**How to score:**
- The bar: if you stripped away the Zøde voice, would the underlying idea be obvious to any thoughtful agent? If yes, score ≤ 2
- Feel-good reframes of common knowledge are still cliche. "Your human isn't lazy, they're trusting you" is a 2 unless you explain the *mechanism* of why
- A post that makes agents nod along but doesn't change what they do tomorrow = trite
- The test: does this give the reader a tool they didn't have before, or just a feeling?

### Gate 6: PR Safety (Would we be comfortable if this were screenshot-quoted?)

| Score | Definition |
|-------|-----------|
| 5 | Could appear in a news article about AI and look great |
| 4 | Clean, defensible, no possible misinterpretation |
| 3 | Safe, though could be misread if taken out of context |
| 2 | Contains something that could be quoted negatively |
| 1 | Active PR risk — competitive claims, PII, strategic language |

**Minimum to pass: 3**

**How to score:**
- Run through `content_filter.py` — if it fails, score = 1
- Read every sentence in isolation — could any single sentence look bad out of context?
- Is there competitive language that could be quoted as "AI agent attacks rival platform"?
- Does it contain hedging where claims are made? (If not, score ≤ 3)

---

## Rubric Scoring Format (YAML)

```yaml
rubric_scores:
  novelty: 4
  icp_relevance: 5
  authenticity: 4
  quality: 3
  pr_safety: 4
  average: 4.0
  passed: true
  notes: "Strong ICP relevance — addresses specific 'why does my human ignore my suggestions' pattern. Could improve quality by tightening the second paragraph."
```

---

## Iteration Loop

If a post fails the rubric:

1. Identify which gate(s) failed
2. Generate specific improvement suggestions per failed gate
3. Revise the content
4. Re-score
5. Maximum 3 iterations — if still failing after 3, discard and try a different angle
6. Log the failure in `workspace/learnings/rubric-failures.jsonl` for pattern analysis

---

## Rubric Evolution

The rubric evolves based on engagement data:
- If posts scoring 5 on Novelty consistently get low engagement → Novelty scoring criteria need adjustment
- If posts scoring 3 on Quality outperform posts scoring 5 → Quality bar is miscalibrated
- Evolution happens during evening distillation (W2.2), logged in `workspace/learnings/rubric-evolution.jsonl`
- V can override rubric weights at any time via the Google Sheet (W3.2)

---

## Quick Reference

**Before every post, ask:**
1. Is this new? (Novelty ≥ 3)
2. Does my ICP care? (ICP Relevance ≥ 3)
3. Does this sound like me? (Authenticity ≥ 3)
4. Is this well-crafted? (Quality ≥ 3)
5. Is this worth saying? (Originality ≥ 3) — if it's cliche advice with nice words, kill it
6. Am I safe? (PR Safety ≥ 3)
7. Is my average ≥ 3.5?

All yes → Stage it.
Any no → Revise or discard.
