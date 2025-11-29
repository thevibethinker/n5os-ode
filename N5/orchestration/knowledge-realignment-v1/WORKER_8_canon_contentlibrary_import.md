---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 8: Canon & Content Library Imports (Phase 6 Implementation)

**Orchestrator:** con_Nd2RpEkeELRh3SBJ  
**Task ID:** W8-CANON-CONTENTLIB-IMPORT  
**Estimated Time:** 60–120 minutes  
**Dependencies:**
- Workers 4–7 complete.
- `PHASE2_target_architecture.md` (v1.1) and `PHASE3_migration_plan.md` (v1.1) reviewed.

---

## Mission
Implement scripts to normalize company/V canon, personal brand/social content, and relevant articles into `Personal/Knowledge/Canon/**` and `Personal/Knowledge/ContentLibrary/content/`, retiring `Documents/Knowledge/Articles/` as a SSOT.

---

## Context

Today, narrative canon and article-like content is scattered across:
- `Personal/Knowledge/Legacy_Inbox/stable/company/*` and `semi_stable/*`.
- `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**`.
- `Documents/Knowledge/Articles/**`.

The refined architecture calls for:
- Canonical narratives under `Personal/Knowledge/Canon/{Company,V/SocialContent,Products,Stakeholders}/`.
- Important but non-canon references under `Personal/Knowledge/ContentLibrary/content/`.

---

## Dependencies

- Path config covers `personal_knowledge.canon`, `personal_knowledge.content_library`, and `personal_knowledge.personal_brand`.
- Architecture and Frameworks migrations complete so canon is not polluted with system specs or raw frameworks.

---

## Deliverables

1. Canon/content import script, e.g. `N5/scripts/knowledge_import_canon_contentlibrary.py` with `--dry-run` and `--execute`.
2. Normalized Canon structure:
   - `Personal/Knowledge/Canon/Company/**` for company narratives and timelines.
   - `Personal/Knowledge/Canon/V/SocialContent/**` for personal brand + social content canon.
   - Optional `Canon/Company/Snapshots/` for current/archived snapshots.
3. ContentLibrary imports:
   - Selected documents from `Documents/Knowledge/Articles/**` (and possibly elsewhere) moved or copied into `Personal/Knowledge/ContentLibrary/content/` where they are valuable references but not canon.
4. A manifest file, e.g. `Records/Personal/knowledge-system/canon_content_import_manifest.jsonl`, listing each imported file with:
   - `source_path`, `target_path`, `classification` (canon vs content_library), and `grade`/`domain` guess.

---

## Requirements

- **Language:** Python 3.12.
- **Classification rules:**
  - Use simple heuristics and/or minimal LLM prompts to decide whether a document is:
    - Canon (durable narrative), or
    - Library reference (important but not narrative canon).
- **Non-destructive:**
  - Default to copy-then-validate before deleting from `Documents/Knowledge/Articles/`.
  - Leave a README in `Documents/Knowledge/Articles/` explaining its non-SSOT status once migration is complete.

---

## Implementation Guide

1. **Scanning**

- Enumerate:
  - `Personal/Knowledge/Legacy_Inbox/stable/company/*` + `semi_stable/*`.
  - `Personal/Knowledge/Legacy_Inbox/personal-brand/social-content/**`.
  - `Documents/Knowledge/Articles/**`.

2. **Classification Heuristics**

- Company canon candidates:
  - Titles/descriptions mentioning company overview, positioning, vision, narrative.
  - Files already in `stable/company`.
- V canon / personal brand:
  - Files under `personal-brand/social-content`.
  - Articles clearly authored as V’s public essays.
- ContentLibrary candidates:
  - External articles.
  - Deep dives mainly used as reference material.

3. **Promotion Logic**

- For each file, decide target:
  - `Canon/Company/` or `Canon/Company/Snapshots/`.
  - `Canon/V/SocialContent/`.
  - `ContentLibrary/content/`.
  - `Archive/` if deprecated but worth keeping.

4. **Metadata (optional but recommended)**

- Add minimal frontmatter to imported files if missing:

```yaml
---
grade: knowledge
domain: output
stability: time_bound
form: artifact
---
```

- Adjust `grade`, `stability`, and `domain` where obviously appropriate (e.g. core canon may be `stability: durable`).

5. **Manifest Recording**

- For each moved/copied file, append a JSON line to `canon_content_import_manifest.jsonl` with:

```json
{"source": "Documents/Knowledge/Articles/foo.md", "target": "Personal/Knowledge/Canon/V/foo.md", "classification": "canon", "grade": "knowledge"}
```

---

## Testing

1. Run `--dry-run` and inspect a sample of planned mappings.
2. Run `--execute` and verify:
   - Canon and ContentLibrary contain the expected files.
   - `Documents/Knowledge/Articles/` no longer contains unique SSOT content.
3. Spot-check a few imports in the manifest for correctness.

---

## Report Back

When complete, report to the orchestrator with:

1. Path to the import script.
2. Counts of documents classified as Canon vs ContentLibrary vs Archive.
3. Any ambiguous or skipped files that should be reviewed manually.

**Orchestrator Contact:** con_Nd2RpEkeELRh3SBJ  
**Created:** 2025-11-29  

