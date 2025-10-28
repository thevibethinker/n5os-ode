# How to Use the ZoATS Scorecards in 3 Minutes (v0.1)

Purpose: Fast, reliable interviews using behavior anchors and evidence-first review.

1) Pre-brief (3 min)
- Skim rubric JSON for this role/stage (weights + pass threshold). 
- Open structured questions for the specific criteria you will score.
- Review 1 exemplar answer or anchor text together (calibration).

2) Evidence-first review (async or live)
- Start with portfolio/work samples; capture 1–2 objective observations per criterion.
- If feasible, blind-first artifact skim before looking at names/brands.

3) Ask 1–2 structured questions per criterion
- Use the role’s question sheets (questions/*.md). Ask the same prompts for every candidate at this stage.
- Listen for level-specific behaviors (L1–L4); avoid vibe words.

4) Anchor and note (inline)
- For each criterion, assign 1–4 using the anchors from criteria/*.json. 
- Take notes using templates/anchored_notes_template.md (evidence → anchor → 1 disconfirming angle).

5) Bias/risk guardrails (built-in)
- Require one disconfirming example before a final verdict.
- Time-box review; avoid contrast effects with previous candidates.
- If AI was used to produce artifacts, require citations/validation notes.

6) Compute score and verdict
- Normalization: 1→0.25, 2→0.50, 3→0.75, 4→1.00.
- Weighted score S = (Σ w_i * n_i) / (Σ w_i). Pass threshold (Seed/Pre-Seed): 0.72.
- Verdict bands: ≥0.80 Strong Yes; 0.72–0.79 Qualified Yes; 0.60–0.71 Hold; <0.60 Reject.

7) Output
- Scorecard JSON + short rationale (templates/verdict_rationale_snippet.md) → internal note or email.

See also: docs/scoring_model.md, docs/bias_fairness.md, docs/evidence_policy.md, docs/simulations.md
