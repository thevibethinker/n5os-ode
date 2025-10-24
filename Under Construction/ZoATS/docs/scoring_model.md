# Scoring Model (v0.1)

Normalization
- Each criterion scored 1–4 (Emerging, Solid, Strong, Exceptional) using anchors.
- Map 1→0.25, 2→0.50, 3→0.75, 4→1.00.
- Weighted normalized score S = (Σ w_i * n_i) / (Σ w_i). Default equal weights; weights tuned from founder priorities and role-specific critical gaps.
- Pass threshold: 0.72 for Seed/Pre-Seed (draft); verdict bands: ≥0.80 "Strong Yes", 0.72–0.79 "Qualified Yes", 0.60–0.71 "Hold", <0.60 "Reject".

Anchors & Reliability
- Behaviorally Anchored Rating Scales: define concrete indicators per level to reduce rater drift and increase inter-rater reliability [^1][^2][^3].
- Calibration: brief 10–15 min pre-brief using exemplar answers; post-interview debrief requires 1 disconfirming angle per rater.

Decision Policy
- "Qualified Yes" requires (a) no red critical gaps OR (b) credible mitigation plan within 30–60 days.
- Critical gaps derived from role rubric (e.g., FE: Ownership, Systems; FD: Taste, Prototyping; PM: Judgment, Problem Framing).

References

[^1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8480396/
[^2]: https://help.alvalabs.io/en/articles/10541075-how-structured-interviews-are-linked-to-job-performance
[^3]: https://www.metaview.ai/resources/blog/interview-rubrics
