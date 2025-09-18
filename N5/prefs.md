# N5 OS Preferences (Global)

This governs defaults and rules. Workflow sub-preferences may override; project _prefs.md overrides those.

## Command Index (top)

- `digest-runs` — Generate digest reports from run records for analysis and monitoring. (see ./commands/digest-runs.md)
- `docgen` — Generate command catalog and update prefs Command Index from commands.jsonl. (see ./commands/docgen.md)
- `docgen-with-schedule-wrapper` — Docgen command wrapped with scheduling wrapper for retries/lock/timezone/missed-run. (see ./commands/docgen-with-schedule-wrapper.md)
- `flow-run` — Execute a flow by chaining modules in sequence. (see ./commands/flow-run.md)
- `index-rebuild` — Rebuild the N5 index from scratch and regenerate MD view. (see ./commands/index-rebuild.md)
- `index-update` — Update the N5 index incrementally, scanning only changed files. (see ./commands/index-update.md)
- `knowledge-add` — Add a fact to the knowledge base. (see ./commands/knowledge-add.md)
- `knowledge-find` — Search and filter facts in the knowledge base. (see ./commands/knowledge-find.md)
- `lists-add` — Add an item to a list (JSONL canonical), e.g., the ideas list. (see ./commands/lists-add.md)
- `lists-create` — Create a new list registry entry with JSONL and MD files. (see ./commands/lists-create.md)
- `lists-docgen` — Regenerate MD views from JSONL for lists. (see ./commands/lists-docgen.md)
- `lists-export` — Export a list to MD or CSV format. (see ./commands/lists-export.md)
- `lists-find` — Search and filter items in a list. (see ./commands/lists-find.md)
- `lists-pin` — Pin or unpin an item in a list. (see ./commands/lists-pin.md)
- `lists-promote` — Promote a list with explicit approval. (see ./commands/lists-promote.md)
- `lists-set` — Update fields of an item in a list. (see ./commands/lists-set.md)
- `git-audit` — Scan workspace for files that should be tracked by Git but are untracked, and generate commands to add them.

## Review & Safety

- Never schedule anything without explicit consent.
- Always support --dry-run; sticky safety may enforce it.
- Require explicit approval for side-effect actions (email, external API, creating services, deleting files).

## Git Governance

- Track these paths explicitly:
  - N5/prefs.md
  - N5/commands.jsonl
  - N5/lists/*.jsonl
  - N5/knowledge/**/*.md
  - N5/modules/**/*.md
  - N5/flows/**/*.md
  - N5/schemas/**/*.json
  - N5/scripts/**/*.py
  - N5/examples/**/*.md

- Ignore generated and transient files:
  - N5/commands.md
  - N5/commands/*.md
  - N5/lists/*.md
  - N5/index.md
  - N5/index.jsonl
  - N5/runtime/**
  - N5/exports/**

- Use the command `N5: git-audit` regularly after adding new workflows or files to detect untracked important files.
- This will print exact shell commands to add missing files to Git.
- No automatic changes are made; manual approval is required to add files.

## Scheduling
- Enabled: false
- Max Retries: 2
- Backoff Seconds: 60, 300
- Lock Timeout: 3600
- Missed Run Policy: skip
- Timezone: UTC

## Resolution Order

Project _prefs.md > Workflow sub-pref > Global prefs.md. Knowledge informs, does not override.
