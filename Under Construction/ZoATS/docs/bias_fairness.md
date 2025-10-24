# Bias & Fairness Controls (v0.1)

Purpose: implement practical, reliable bias/risk guardrails for early-stage hiring without adding friction.

Core practices we will implement:
- Structured interviews with behaviorally anchored rating scales (BARS) to increase inter-rater reliability and predictive validity [^1][^2][^3].
- Standardized questions by criterion with anchors 1–4; identical prompts for all candidates at the same stage [^2].
- Work-sample/portfolio-first evidence review before live interviews to reduce halo/affinity effects [^4].
- Blind-first artifact review when feasible (hide school/company names until preliminary scoring) [^4].
- Multi-rater calibration + debrief with transparent rationales and disconfirming evidence requirement (one explicit counterpoint per verdict).
- Guardrails and checklists embedded in scorecard UX (e.g., bias prompts, time-boxing, anchor tooltips).

Open-source we can absorb (future ML or analytics phases):
- IBM AI Fairness 360 (AIF360): metrics + mitigation algorithms; can power analytics on score distributions by group [^5][^6][^7].
- Microsoft Fairlearn: fairness dashboards, disparity metrics, mitigation strategies [^8].
- FAT Forensics: transparency and fairness inspection for data/process audits [^9].

Scope note: ZoATS v0.* is process-structured (not model-scored). Toolkits apply when/if we add algorithmic scoring. We will still adopt their metric concepts to monitor human scoring disparities over time.

[^1]: https://www.criteriacorp.com/interview/structured-interviews
[^2]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8480396/
[^3]: https://help.alvalabs.io/en/articles/10541075-how-structured-interviews-are-linked-to-job-performance
[^4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9553626/
[^5]: https://ai-fairness-360.org/
[^6]: https://github.com/Trusted-AI/AIF360
[^7]: https://aif360.readthedocs.io/en/latest/Getting%20Started.html
[^8]: https://fairlearn.org/
[^9]: https://www.turingpost.com/p/ai-fairness-tools
