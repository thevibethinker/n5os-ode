---
created: 2025-11-29
last_edited: 2025-11-29
version: 1
---
# Worker 1 – Capability Schema & Scaffolding

## Objective

Define and lock the **capability schema and file layout** for `N5/capabilities/**` so that all future workers and conversation-end flows can use it reliably.

## Scope

- Operate primarily on:
  - `file 'N5/capabilities/index.md'`
  - `file 'N5/capabilities/CAPABILITY_TEMPLATE.md'`
  - `file 'N5/prefs/system/navigator_prompt.md'` (for discoverability, if needed)
- No destructive changes; additive and refactor-only.

## Tasks

1. **Schema Finalization**
   - Review existing template in `CAPABILITY_TEMPLATE.md`.
   - Propose any additional fields needed (e.g., `confidence`, `last_verified`, `tags`).
   - Keep schema in **Zone 2** (YAML in frontmatter or fenced block) to balance structure and flexibility.

2. **Category & Directory Conventions**
   - Confirm initial categories:
     - `integration`, `internal`, `workflow`, `orchestrator`, `agent`, `site`.
   - Recommend which categories map to which subdirectories:
     - `integrations/`, `internal/`, `workflows/`.
   - Document these rules inside `index.md`.

3. **Template Refinement**
   - Ensure template is copy-paste friendly and minimal.
   - Add 1–2 **worked examples** as comments or below the template (optional but helpful).
   - Clarify how to reference prompts vs. scripts vs. services.

4. **Navigator Integration (optional)**
   - If useful, add a short section or reference in `navigator_prompt.md` so that N5 can quickly surface capabilities when asked "what can you do?".

## Deliverables

- Updated `N5/capabilities/CAPABILITY_TEMPLATE.md` reflecting final schema.
- Updated `N5/capabilities/index.md` with clarified structure and category mapping.
- (Optional) Small note/update in `N5/prefs/system/navigator_prompt.md` pointing to the capability registry.

## Success Criteria

- Schema is stable enough for other workers to start populating capability files.
- Template is clear enough that future you (or other personas) can create a new capability doc in under 2 minutes.
- No ambiguity about where a given capability "belongs" in the directory tree.


