---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 73b000f736ebb07772339cb0e07e3606
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/commands.md
---
# N5 Command Catalog
Generated from commands.jsonl. Do not edit by hand.

| Name | Version | Workflow | Summary | Side Effects | Permissions |
| --- | --- | --- | --- | --- | --- |
| [`docgen`](./docgen.md) | 0.1.0 | ops | Generate command catalog and update prefs Command Index from commands.jsonl | writes:file, modifies:file |  |
| [`git-check`](./git-check.md) | 0.1.0 | ops | Quick audit for overwrites or data loss in staged Git changes |  |  |
| [`grep-search-command-creation`](./grep-search-command-creation.md) | 0.1.0 | automation | Automated command_creation workflow using grep_search, create_command_draft, validate_command | executes:command, atomic:operations |  |
| [`index-rebuild`](./index-rebuild.md) | 0.1.0 | ops | Rebuild the N5 system index from source files | writes:file, modifies:file |  |
| [`lists-add`](./lists-add.md) | 0.2.0 | lists | Add an item to a list with intelligent assignment | writes:file, modifies:file |  |
| [`lists-move`](./lists-move.md) | 0.1.0 | lists | Move an item from one list to another atomically | modifies:file, writes:file |  |
| [`system-upgrades-add`](./system-upgrades-add.md) | 1.0.0 | ops | Interactive command for adding items to the N5 system upgrades list with validation and safety features | writes:file, modifies:file, creates:backup |  |
| [`timeline`](./timeline.md) | 0.1.0 | ops | View n5.os development timeline and system history |  |  |
| [`timeline-add`](./timeline-add.md) | 0.1.0 | ops | Add new entry to n5.os development timeline | writes:file |  |
