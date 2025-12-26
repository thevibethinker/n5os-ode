---
date: "2025-09-20T22:24:55Z"
last-tested: "2025-09-20T22:24:55Z"
generated_date: "2025-09-20T22:24:55Z"
checksum: 8d77372a364301427c38385916bc0aab
tags:
category: unknown
priority: medium
related_files:
anchors: [object Object]
---
# Lists Subfolder Policy

## Purpose
Lists serve as managed databases for tasks, ideas, and data collections within N5 OS. Interpret as dynamic tables with JSONL backends and MD views—add/set/find operations treat them as executable workflows.

## Handling Rules
- **Collective Handling**: Each list is a program; additions/edits via commands only (lists-add, lists-set). Direct file edits prohibited without validation.
- **Creation**: Use lists-create command; auto-generates .jsonl and .md pairs.
- **Promotions/Exports**: Require docgen for documentation; cross-link to knowledge base.
- **Interactions**: Override global prefs for list operations—prioritize atomic changes with rollbacks.

## Hybrid Storage Standards

Lists support **hybrid storage** for complex content requiring rich formatting, structured layout, or extended length.

**Key Principles:**
- JSONL remains the Single Source of Truth (SSOT)
- Markdown files are optional extensions for Reference-type entries
- Use the `links` field to reference external markdown files

**Content Classification:**
1. **Atomic**: Self-contained data in JSONL fields only (~800 chars max)
2. **Reference (Internal)**: Complex content → JSONL + linked markdown file
3. **External**: Third-party content → JSONL + URL link

**For detailed guidance on:**
- When to use hybrid vs. atomic storage
- File location conventions
- YAML frontmatter standards
- Validation and orphan detection

→ See: [Lists Storage Standards](../Documents/System/Lists-Storage-Standards.md)

## Safety Flags
- **Data Integrity**: JSONL is medium-protection; validate schema before commits.
- **Automation Risks**: Lists-set may trigger external actions; gate with dry-runs.
- **Conflicts**: Duplicate detection mandatory; resolve via lists-find.

## Dependencies
- Anchors to: Root N5/POLICY.md (collective governance), N5/schemas/lists.schema.json (validation), N5/knowledge/ (cross-references).
- Relies on commands/ for execution.

## Overrides
- Overrides prefs.md file protection for list .jsonl—allow edits via validated commands only.
- Exempts: Global backup rules (still apply).

## Anchors
- [Root Policy](../POLICY.md) — Hierarchical overrides.
- [List Schemas](../../schemas/lists.schema.json) — Data structure rules.
- [Knowledge Ingestion](../../knowledge/) — Cross-linking standards.
- Related Problems: Data bloat (prefer existing lists), validation failures (auto-revert).
