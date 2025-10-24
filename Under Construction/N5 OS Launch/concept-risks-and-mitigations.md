# N5 OS — Portability Layer (Concept Spec)

## Goals

- Make exit safe and simple; preserve cognition, not just files
- Be tool-agnostic: Obsidian/Notion-ready without migration pain
- Maintain traceability and link integrity

## Artifacts

- Markdown-first content (UTF-8, Git-friendly)
- JSONL transcripts for audio/video with {text, timestamps, source_file}
- Cross-ref index (YAML or JSON) mapping themes → artifacts (paths, anchors)
- Provenance appendices per synthesis output

## File Conventions

- Names: `YYYY-MM-DD_slug.ext`
- Paths: `Knowledge/`, `Lists/`, `Records/` remain stable
- Provenance: `file artifact.md`  → `file artifact.provenance.md`  (or embedded section)

## Minimal Export Contract

- All markdown + JSONL under root dir
- Relative links only
- No proprietary formats required

## Example Index (YAML)

```yaml
version: 1
updated: 2025-10-21
themes:
  founder_psychology:
    - path: Knowledge/notes/2025-10-21_founder-psychology.md
      anchors: ["pattern_recognition", "identity_shift"]
  n5_os:
    - path: In Processing/N5 OS Launch/2025-10-21_reflections-on-n5-os_summary.md
      anchors: ["weighted_jacket", "guardrails", "averaging_effect"]
```

## Trust & Lineage

- Each synthesis doc includes: 
  - Sources list (file paths + timestamps)
  - Pull-quotes (2–5 lines) for each source
  - Confidence & known gaps

## Degradation Modes

- If OS is paused: scheduled synth jobs stop; capture remains manual; export command produces flat bundle for any editor
---
## Risk Addendum: Slippage & Provenance (2025-10-21)

- Risk: Over‑capture with under‑use → more artifacts, same decisions.
  - Mitigation: Guardrail entry points; decision‑first briefs; provenance shown on demand.
- Risk: Lost language → weaker persuasion in follow‑ups.
  - Mitigation: Durable “talking point capture” during/after calls; reuse in briefs.
- Risk: Linkages not surfaced → creativity plateau.
  - Mitigation: Cross‑ref index + synthesis passes that propose link hypotheses for review.
