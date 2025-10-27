# Pattern Map — LinkedIn Top Performers (OCR-derived)

Source images: file '/home/.z/workspaces/con_f7Xbld76jdowigLo/linkedIn_ocr_hires'
Metrics table: file '/home/.z/workspaces/con_f7Xbld76jdowigLo/linkedIn_ocr_hires/post_engagement_scored.md'

Caveat: OCR text bodies are partial; this is a best-effort map from visible structure + metrics. Will reconcile with CSV export later.

## Weighting model
- Engagement Score = (likes + 3*comments + 4*reposts) / impressions
- Heuristic: comments and reposts indicate conversation and spread; we bias pattern selection toward these.

## Observed high-performing posts

1) Post 7 — Score 0.0367
- Likely patterns: Contrast Hook, Lived Specific x2, Quiet Resolution, One-Ask CTA
- Structural notes: clear top hook, 2–4 compact paragraphs, specific numbers, one explicit CTA

2) Post 8 — Score 0.0275
- Likely patterns: Lived Specific, Show-Then-Name, One-Ask CTA
- Structural notes: example first, label later; 1 image; ~150–250 words

3) Post 2 — Score 0.0271
- Likely patterns: Contrast Hook, Mini-Framework (3 bullets), One-Ask CTA
- Structural notes: numbered list in body; no emoji; direct CTA

## Pattern recommendations (ranked)
- P1 Contrast Hook
- P2 Lived Specific (numbers, places, time)
- P3 Quiet Resolution (no chest-beat ending; grounded takeaway)
- P4 One-Ask CTA (question or invite; singular)
- P5 Show-Then-Name (example precedes label)
- P6 Mini-Framework (3 bullets max)

## Prompt assembly recipe (transformation-based)
1) Select top K=3 transformation pairs by semantic relevance to topic (email + LI + notes) and by Engagement Score tie-break.
2) Compose: [Contrast Hook] → [Show-Then-Name] → [Lived Specific x2] → [Mini-Framework OR Short story] → [Quiet Resolution] → [One-Ask CTA].
3) Run QA: stop-verb scan, read-aloud, numbers present, exactly one CTA.
