---
date: '2025-09-20T22:24:55Z'
last-tested: '2025-09-20T22:24:55Z'
generated_date: '2025-09-20T22:24:55Z'
checksum: 141445889337f1c301ac3383771d7e1c
tags: []
category: unknown
priority: medium
related_files: []
anchors:
  input: null
  output: /home/workspace/N5_mirror/POLICY.md
---
# N5 OS Root Policy

## Purpose
N5 is the core operating system for knowledge management, command execution, and workflow orchestration. This folder serves as the root anchor for all subsystems, treating the entire structure as a cohesive program with dynamic components (e.g., lists as databases, commands as executables).

## Handling Rules
- **Collective Interpretation**: View subfolders as interdependent modules—commands drive lists, knowledge informs flows. Always cross-reference before isolated changes.
- **Additions**: Require policy creation for new subfolders. Use existing structures (e.g., lists for data) before inventing new ones.
- **Edits/Deletions**: Consult subfolder POLICY.md first; escalate to this root policy for conflicts. Prohibit direct edits to .jsonl registries without validation scripts.
- **Interactions**: Prioritize folder policies over global prefs.md. Dry-run all changes; log in timeline for auditability.

## Safety Flags
- **High-Risk Folders**: commands/, knowledge/, lists/—require explicit approval for structural changes.
- **Data Sensitivity**: All .jsonl files are medium-protection; backups mandatory before overwrites.
- **External Dependencies**: Flows/modules may call external APIs; gate with consent checks.
- **Recovery**: Use Git history for restores; log incidents here.

## Dependencies
- Relies on prefs.md for defaults, but this policy overrides unless exempted.
- Anchors to: Root N5/prefs.md (global governance), N5/timeline/ (logging), N5/knowledge/ (epistemic standards).
- Related Issues: System resilience (per zo_setup_rubric.md), knowledge integrity (ingestion standards).

## Overrides
- Overrides prefs.md file protection for root-level decisions (e.g., allow emergency prefs edits with logging).
- Exempts: None currently; all global rules subordinate unless conflict arises.

## Anchors
- [Global Preferences](prefs.md) — Defaults and guardrails.
- [Setup Rubric](zo_setup_rubric.md) — Scoring for resilience.
- [Timeline](timeline/) — Change history and recovery.
- [Knowledge Base](knowledge/) — Epistemic foundation.
- Related Problems: Folder sprawl (avoid new structures without policies), policy gaps (auto-flag missing POLICY.md).</content>
</xai:function_call"><xai:function_call name="create_or_rewrite_file">
<parameter name="target_file">/home/workspace/N5/commands/POLICY.md