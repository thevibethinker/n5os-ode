# Orchestrator Thread Framework (Lightweight, Integrated)

## Purpose
Enable an orchestrator conversation (brainstorm + overseer) to spawn a clean execution thread that implements the plan, and return an AAR for objective review (intent vs. outcome). This document defines the minimal template and steps used by `orchestrator_launcher.py`.

## Plan Template (paste into the orchestrator thread)
```
# Plan Summary for [Task Name]
- **Orchestrator Thread Origin**: [short name or link]
- **Sketched Idea**: [1–3 sentences]
- **Intended Outcome**: [crisp, testable]
- **Launch Command**: [prompt/command/script to start]
- **Sub-Tasks**: [optional bullets]
- **Risks/Notes**: [assumptions, bias to avoid]
```

## Workflow
1. Paste the Plan Template above and fill minimally (Outcome + Launch are essential).
2. Run the launcher with the plan (stdin or file):
   - `cat PLAN.md | python3 N5/tmp_execution/orchestrator_launcher.py --mirror-n5`
   - or `python3 N5/tmp_execution/orchestrator_launcher.py --plan-file PLAN.md --mirror-n5`
3. Optionally add `--execute` to attempt execution if an executable hint is present.
4. Review the generated AAR in `N5/tmp_execution/` and compare Intended vs. Actual.

## AAR Structure
- Execution Thread ID
- Original Plan Reference
- Intended vs. Actual
- Step-by-Step Execution
- Outcomes
- Lessons Learned
- Recommendations for Orchestrator

## Integration Points
- Authoring pipeline: `N5/scripts/author-command/author-command`
- Registry sync: `N5/scripts/append_command.py` → `commands.jsonl`
- Catalog update: handled by chunk6 exporter when author-command runs
- Logging: `/home/workspace/command_authoring.log`

## Notes
- Keep plans concise; provide just enough context to be unambiguous.
- Use Risks/Notes to enumerate assumptions and bias to avoid; this helps maintain clean execution context.
- For trivial tasks, you may execute in-thread and skip spawning.
