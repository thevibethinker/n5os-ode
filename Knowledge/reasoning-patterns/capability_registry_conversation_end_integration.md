---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Capability Registry Conversation-End Integration Pattern

## Pattern Summary

When wiring a registry or catalog into an existing multi-phase pipeline, keep the core analyzer/proposal/executor mechanics unchanged and add a **semantic checkpoint** at the orchestration layer:

- Use the orchestrator prompt (Close Conversation) to **decide if the thread is build/orchestrator-class**.
- If yes, run an explicit **capability checkpoint** asking whether a major capability was created or significantly changed.
- Gather a **minimal, structured YAML spec** (name, capability_id, category, change_type, description, entry_points, associated_files) while V is still in-context.
- Route this spec either to a deterministic helper script or to direct file edits that update capability markdown files and `N5/capabilities/index.md`.
- Surface the result in a dedicated **"Capability Registry Updates"** section of the human closure template so the registry state is always explicit (changes vs explicit "none").

## When To Use

- Any time a registry-like system (capabilities, recipes, prompts, agents) needs to stay in sync with build-oriented threads.
- Situations where the safest change is **LLM-side orchestration + structured metadata**, not editing the core filesystem pipeline.

## Key Principles

- **Mechanics vs semantics:** scripts handle file moves and index updates; the LLM decides *whether* and *how* to log a capability.
- **Explicit decisions:** every build/orchestrator closure must either log concrete capability changes or explicitly say "no capability changes logged".
- **Minimal schema:** collect only the fields needed to reconstruct or update a capability file; avoid overloading the checkpoint.
- **Non-invasive wiring:** attach the capability step via prompts and templates, leaving core safety/rollback behavior untouched.

