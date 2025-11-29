---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Worker 5 – Conversation-End Integration & QA

## Objective

Wire the **Capability Registry** into the **Close Conversation** pipeline so that build-oriented orchestrator threads automatically propose capability updates.

## Scope

- `file 'Prompts/Close Conversation.prompt.md'`
- `file 'N5/prefs/operations/conversation-end-output-template.md'`
- `file 'N5/prefs/operations/conversation_end_pipeline.md'`
- Optional: lightweight helper script under `N5/scripts/` for structured capability updates

## Tasks

1. **Design the Interaction**
   - Define when the capability step should run:
     - Only for **orchestrator/build threads** that produced or modified major functionality.
   - Define the questions to ask V when in doubt (e.g., "Did this conversation create or significantly change a major capability? If yes, what should we call it?").

2. **LLM-Side Protocol**
   - Update docs/templates so that, during conversation close, the AI:
     - Checks whether the conversation is a build/orchestrator thread.
     - Asks V to confirm if a capability should be created/updated.
     - Gathers minimal metadata: name, category, description, associated files, entry points.
     - Writes or updates the appropriate capability file under `N5/capabilities/**` (either directly or via a helper script).

3. **(Optional) Helper Script**
   - If useful, design a small script (e.g., `N5/scripts/capability_registry_update.py`) that:
     - Accepts a simple JSON/YAML spec for a capability
     - Creates/updates the corresponding markdown file and keeps `index.md` in sync
   - Keep it **deterministic and testable**; LLM provides semantics, script handles mechanics.

4. **QA & Safety**
   - Ensure the new step **never runs silently**; it should:
     - Either clearly state "No capability changes logged" or
     - List exactly which capability files were created/updated.
   - Add a small test plan:
     - Run Close Conversation on a mock build thread, verify capability file + index update.

## Deliverables

- Updated documentation/instructions for Close Conversation and conversation-end output.
- (Optional) Helper script for deterministic capability updates.
- Mini QA checklist + at least one validated test run.

## Success Criteria

- After this worker is complete, **every future build orchestrator thread** has an explicit decision about capability changes, and the registry stays in sync with real functionality.


