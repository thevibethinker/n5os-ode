---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Conversation-End Proposal Schema

Canonical JSON schema used between:
- **Generator:** `N5/scripts/conversation_end_proposal.py`
- **Executor:** `N5/scripts/conversation_end_executor.py`

This document defines the fields that **must** or **may** appear in a proposal JSON file passed to the executor.

## 1. Top-Level Structure

A proposal is a single JSON object with the following fields:

```jsonc
{
  "conversation_id": "nKcbWQptDIBJKPUb",   // REQUIRED – opaque ID string
  "title": "Conversation nKcbWQptDIBJKPUb Closure Proposal", // REQUIRED – human-readable
  "actions": [ /* action objects */ ],       // REQUIRED – may be empty

  "requires_resolution": false,             // OPTIONAL – default false
  "conflicts": [ /* conflict objects */ ],  // OPTIONAL – default []

  "convo_id": "nKcbWQptDIBJKPUb",          // LEGACY – kept for compatibility

  // Auxiliary metadata (not consumed by executor directly)
  "files_to_organize": [ /* metadata only */ ],
  "archive_location": "Documents/Archive/2025-11-29_con_nKcbWQptDIBJKPUb", 
  "aar_required": true,
  "tasks_to_close": [],
  "git_changes": [],
  "thread_title": "Conversation nKcbWQptDIBJKPUb Closure Proposal"
}
```

### Required Fields (Executor-contract)

- `conversation_id` (`str`, required)
  - Opaque identifier for the conversation.
  - Logged by the executor and used for backup/transaction log naming.
- `title` (`str`, required)
  - Human-readable label for logging and inspection.
- `actions` (`list[action]`, required)
  - List of action objects. May be empty, in which case the executor is a no-op.

### Optional Control Fields

- `requires_resolution` (`bool`, optional; default `false`)
  - If `true`, **executor MUST NOT execute** actions.
  - `ConversationEndExecutor.execute_proposal()` checks this flag and aborts early, logging all conflicts.
- `conflicts` (`list[conflict]`, optional; default `[]`)
  - Describes why human resolution is needed before safe execution.

### Legacy and Auxiliary Metadata

- `convo_id` (`str`, legacy)
  - Legacy field kept for higher-level workflows that still read this name.
  - Always mirrors `conversation_id` in current generator.
- `files_to_organize` (`list[object]`, auxiliary)
  - Currently **metadata only**; not consumed by the executor.
  - Shape used today (from generator):
    ```jsonc
    { "source": "/home/workspace/Documents/...", "target": "/home/workspace/Documents/...", "action": "keep" }
    ```
- `archive_location` (`str`, auxiliary)
  - Logical root archive folder for this conversation (human and orchestration hint).
  - Current generator sets this to the same value used in archive actions.
- `aar_required` (`bool`, auxiliary)
- `tasks_to_close` (`list`, auxiliary)
- `git_changes` (`list`, auxiliary)
- `thread_title` (`str`, auxiliary)

These auxiliary fields are safe to extend for higher-level workflows; the executor ignores them.

## 2. Action Objects

Each entry in `actions` is an object consumed by `ConversationEndExecutor`:

```jsonc
{
  "action_type": "archive",         // REQUIRED – one of: move | archive | delete | ignore
  "source": "/abs/source/path",    // REQUIRED – absolute path
  "destination": "/abs/dest/path", // REQUIRED for move/archive; backup location for delete
  "approved": true,                  // REQUIRED for execution (must be true)

  // Optional metadata (not required by executor logic)
  "reason": "Archive conversation artifact from workspace",
  "confidence": "high"
}
```

### Semantics (from executor implementation)

- `action_type` (`str`, required)
  - `"move"` – move file from `source` → `destination`.
  - `"archive"` – semantically identical to `move`, but to archive targets.
  - `"delete"` – delete `source` after backing up to `destination` under `/tmp/conversation_end_backups/<conversation_id>/`.
  - `"ignore"` – no-op; **never executed** (filtered out before execution).

- `source` (`str`, required)
  - Absolute path of the current file.
  - Executor verifies existence in pre-flight checks.

- `destination` (`str`, required for `move`/`archive`/`delete`)
  - For `move`/`archive`:
    - Must be absolute.
    - Must **not** exist at execution time (P5 anti-overwrite rule enforced in preconditions).
  - For `delete`:
    - Used as backup path in transaction log and rollback flow.

- `approved` (`bool`, required for execution)
  - Executor filters actions via:
    ```python
    approved_actions = [
        a for a in proposal["actions"]
        if a.get("approved", False) and a["action_type"] != "ignore"
    ]
    ```
  - If missing or `false`, the action is **never executed**.

- Metadata fields (`reason`, `confidence`, etc.)
  - Optional, used for human inspection only.

## 3. Conflict Objects

Used when `requires_resolution` is `true`:

```jsonc
{
  "type": "archive_path_exists",
  "description": "Archive path already exists: /home/workspace/Documents/Archive/2025-11-29_con_nKcbWQptDIBJKPUb"
}
```

Executor behavior:
- Logs the number of conflicts and each `type`/`description`.
- Returns exit code `1` and **performs no file operations**.

## 4. Current Generator Behavior

Generator: `file 'N5/scripts/conversation_end_proposal.py'`

Given `analysis.json` (from `conversation_end_analyzer.py`), the generator now:

1. Reads `analysis["convo_id"]` and sets:
   - `convo_id` (legacy)
   - `conversation_id` (executor)
2. Derives `title` and `thread_title` as:
   - `analysis["summary"]` if present, else `"Conversation {convo_id} Closure Proposal"`.
3. Computes `archive_location` / archive root as:
   - `/home/workspace/Documents/Archive/YYYY-MM-DD_con_{convo_id}`
4. Builds `actions` by turning each `analysis["artifacts"][i]["path"]` into an `archive` action from:
   - `source = /home/.z/workspaces/con_{convo_id}/{rel_path}`
   - `destination = /home/workspace/Documents/Archive/YYYY-MM-DD_con_{convo_id}/{rel_path}`
   - Each action is marked `approved: true` with a generic `reason` and `confidence`.
5. If the archive root already exists on disk, the generator sets:
   - `requires_resolution = true`
   - Appends a `conflicts` entry of type `"archive_path_exists"`.

## 5. Backward Compatibility Guarantees

- Existing consumers that read `convo_id` continue to function – field is preserved.
- Executor-required fields (`conversation_id`, `title`, `actions`) are now **always present** for generated proposals.
- New fields (`requires_resolution`, `conflicts`) are additive and safe; older proposals without them still execute because the executor uses `.get()` with sensible defaults.
- Auxiliary metadata fields remain top-level and unchanged in name, but are explicitly documented here as **auxiliary**.

## 6. Extension Guidelines

When extending the proposal format:

- **Do not** change the semantics of `conversation_id`, `title`, or `actions`.
- Add new executor-consumed fields only if you also:
  - Update this schema document, and
  - Implement strict validation in the executor.
- Prefer adding nested metadata fields (e.g., `metadata.git`, `metadata.tasks`) over renaming existing top-level keys.
- Treat `requires_resolution=true` + `conflicts` as the primary safety valve for any ambiguous or high-risk situations.

