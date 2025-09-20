# Lists Subfolder Policy

## Purpose
Lists serve as managed databases for tasks, ideas, and data collections within N5 OS. Interpret as dynamic tables with JSONL backends and MD views—add/set/find operations treat them as executable workflows.

## Handling Rules
- **Collective Handling**: Each list is a program; additions/edits via commands only (lists-add, lists-set). Direct file edits prohibited without validation.
- **Creation**: Use lists-create command; auto-generates .jsonl and .md pairs.
- **Promotions/Exports**: Require docgen for documentation; cross-link to knowledge base.
- **Interactions**: Override global prefs for list operations—prioritize atomic changes with rollbacks.

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
- Related Problems: Data bloat (prefer existing lists), validation failures (auto-revert).</content>
</xai:function_call name="create_or_rewrite_file">
<parameter name="target_file">/home/workspace/N5/knowledge/POLICY.md