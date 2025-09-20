# System Docs Subfolder Policy

## Purpose
System_docs is the documentation hub for N5 OS, treating docs as executable knowledge—guides and READMEs drive system operations and onboarding.

## Handling Rules
- **Collective Use**: Docs are programs; reference before changes. Use authoring-guide.md for command creation.
- **Updates**: Align with knowledge ingestion standards; cross-reference to root.
- **Interactions**: Override prefs for doc edits—allow direct MD changes but require version logging.

## Safety Flags
- **Accuracy**: High-stakes; fact-check against knowledge base.
- **Outdated Risks**: Periodic audits via timeline.

## Dependencies
- Anchors to: Root N5/POLICY.md, N5/knowledge/ (standards), N5/examples/ (practical refs).

## Overrides
- Overrides prefs.md on doc creation—generate automatically without location prompts if structured.
- Exempts: None.

## Anchors
- [Root Policy](../POLICY.md) — System coherence.
- [Knowledge Standards](../../knowledge/) — Ingestion rules.
- [Examples](../../examples/) — Usage patterns.
- Related Problems: Doc sprawl (consolidate), version drift (link to Git).</content>
</xai:function_call name="run_bash_command">
<parameter name="cmd">find /home/workspace/N5 -name "POLICY.md" | head -10