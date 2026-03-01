# Build Close: build-promote

## Summary

Synthesized 5 deposits across 3 waves. All 5/5 drops complete. Build finalized and self-verified.

**What was built:** A 4-script skill that transforms completed Pulse builds into first-class `Skills/` entries. Established `state/` as a new skill standard for runtime data.

## Decisions (5)

- **Consolidated into Skills/, not Datasets/:** Zode's runtime data (semantic memory, staging queues) is fundamentally different from tabular DuckDB data in Datasets/. `state/` within the skill is the right home.
- **Two-layer classification over LLM classification:** Heuristic (path/extension) + content inspection handles 80%+ of files deterministically. No external API calls needed.
- **Template-based path adaptation over AST parsing:** Simple string replacement ordered by specificity is sufficient — builds don't have complex import graphs.
- **SKILL.md generation as draft:** Auto-generated docs are marked draft for V to review. Better than no docs, but human review ensures quality.
- **Build scaffolding stays in build folder:** meta.json, PLAN.md, STATUS.md, deposits, drops remain as historical record. Only operational files migrate.

## Learnings

- [D1.1] 196 builds cluster into 184 groups — 7 multi-build chains exist (e.g. zo-hotline has 5 versions). Simple prefix matching after stripping version suffixes works well.
- [D1.2] Two-layer classification (heuristic + content) achieves high confidence on 80%+ of files. Ambiguous files get "low" confidence and "review manually" guidance.
- [D2.1] Path adaptation must process most-specific paths first to avoid partial matches. `sys.path.insert` hacks referencing build paths should be removed entirely.
- [D2.2] Self-referential verification is tricky — a tool that checks for `N5/builds/` references will flag its own detection logic. Required nuanced string-literal and docstring filtering.
- [D3.1] E2E on `builds-audit-cleanup` found that SKILL.md provenance metadata ("Build origin: N5/builds/...") should not trigger stale path warnings.

## Concerns

- [D2.2] verify.py's stale path check needed 4 rounds of refinement to handle meta-tool self-reference correctly. If the detection heuristics change, these filters may need updating.
- [General] The lineage analyzer's promotability determination is conservative — it only flags `complete`/`finalized` builds with operational content. Some builds may be promotable but have unusual status values.

## Position Candidates (2)

- "Build folders are historical records; operational systems belong in Skills/" — reinforced by the Zode migration and the build-promote architecture itself.
- "Runtime state (`state/`) is a distinct concern from code, governance, and datasets" — established as a new skill convention.

## Content Library Candidates (1)

- `Skills/build-promote/SKILL.md` — documents the `state/` standard and promotion workflow. Useful reference for future skill creation.

## Artifacts Created

| Path | Description |
|------|-------------|
| `Skills/build-promote/scripts/lineage_analyzer.py` | Scan, cluster, promotable commands |
| `Skills/build-promote/scripts/artifact_classifier.py` | 9-category file classification |
| `Skills/build-promote/scripts/promote.py` | 9-step promotion workflow |
| `Skills/build-promote/scripts/verify.py` | 8-check verification suite |
| `Skills/build-promote/SKILL.md` | Full skill documentation |
| `Skills/build-promote/state/lineage.json` | Cached lineage analysis (196 builds) |
| `Skills/build-promote/state/.n5protected` | Protection marker |
| `Skills/builds-audit-cleanup/` | E2E test promotion result |
