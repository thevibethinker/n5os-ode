---
created: 2025-12-16
last_edited: 2025-12-16
version: 1.0
provenance: con_XKiLRFt7ycFixjsH
---

# System Documentation Process (N5 OS)

## Purpose
Make system documentation (how N5 works, how to operate it, and why it’s designed the way it is) **easy to produce, consistently stored, and reliably retrievable via semantic memory**.

---

## Canonical storage locations (SSOT)

### System docs (how-to, runbooks, system behavior)
- `Documents/System/**`

### Architecture + principles (guardrails, invariants, standards)
- `Personal/Knowledge/Architecture/**`

### Knowledge pipeline layers
- Content Library (legacy + compatibility): `Knowledge/content-library/**`
- Canonical knowledge paths (target state): `Personal/Knowledge/**` (see `N5/prefs/paths/knowledge_paths.yaml`)

---

## Guardrails already in place (and how they work)

### 1) Sandbox-first creation (prevents scattered files)
- Protocol: `N5/prefs/operations/artifact-placement.md`
- Enforcement workflow: `N5/prefs/operations/file-creation-protocol.md`

**Rule:** drafts/scratch go in the conversation workspace; permanent docs must be intentional and placed in canonical locations.

### 2) Conversation closure promotes important knowledge into the system
- Operational workflow: `N5/prefs/operations/conversation-end.md`

**Rule:** at thread close, promote operational docs into the correct canonical folders (not buried in archives), and keep the archive as historical context.

### 3) Folder governance is explicit
- Multiple prefs + contracts reference `Documents/System/**` and `Personal/Knowledge/Architecture/**` as canonical homes.

---

## Documentation “Definition of Done” (DoD)

A system doc is considered complete when it has:
1. **Clear purpose** (“what question does this answer?”)
2. **Where it lives** (canonical path)
3. **How it’s used** (when/why invoked)
4. **Interfaces** (what scripts/files it touches)
5. **Update cadence** (what changes require updating the doc)

---

## Indexing contract (is documentation indexed?)

### Yes — and the scope is explicit
The canonical re-indexer `N5/scripts/run_full_reindex.py` indexes `*.md` under:
- `N5/capabilities`, `N5/prefs`, `N5/docs`, `N5/schemas`, `N5/workflows`
- `Knowledge`
- `Personal/Knowledge`
- `Prompts`

It excludes obvious noise (`Archive/`, `Trash/`, transcripts, etc.).

### Practical rule
If you want something to be retrievable via semantic memory, store it as a `.md` in one of the indexed roots above (especially `Documents/System/**` or `Personal/Knowledge/Architecture/**`).

---

## Standard operating process (SOP)

### A) When we implement or change a system
1. Create/update the system doc in `Documents/System/**`
2. If it’s an invariant/guardrail, also update/add an Architecture doc in `Personal/Knowledge/Architecture/**`
3. Ensure the doc has the DoD items above
4. Index it (either by nightly/periodic reindex, or immediate `N5MemoryClient.index_file()`)

### B) When closing an important thread
Follow `N5/prefs/operations/conversation-end.md`:
- archive context
- promote operational docs to canonical locations
- add timeline entry when appropriate

---

## Known gaps / improvement hooks

1. **One canonical “map” doc** for the knowledge pipeline exists now:
   - `Documents/System/knowledge-pipeline-and-semantic-memory.md`

2. **Content library path mismatch (legacy vs target state)**
   - `knowledge_paths.yaml` points to `Personal/Knowledge/ContentLibrary` as target canonical.
   - The legacy library currently lives in `Knowledge/content-library/` and is still indexed.

---

## References
- Conversation-end workflow: `N5/prefs/operations/conversation-end.md`
- Sandbox-first artifact rules: `N5/prefs/operations/artifact-placement.md`
- File creation enforcement: `N5/prefs/operations/file-creation-protocol.md`
- Knowledge paths: `N5/prefs/paths/knowledge_paths.yaml`
- Full reindex: `N5/scripts/run_full_reindex.py`

