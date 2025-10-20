# N5 Conditional Rules for Zo

**Critical:** These should be added to your Zo user rules

```markdown
CONDITIONAL RULES:

- CONDITION: When spelling my company's name -> RULE: Always use "Careerspan" not "CareerSpan"

- CONDITION: When I provide the command /gfetch -> RULE: Seek and retrieve from Google Drive or Gmail

- CONDITION: "n5:resume" means there was an error and you stopped responding -> RULE: Bear that in mind and any changes that were already made by you prior to the dropped connection

- CONDITION: Whenever you are stuck or repeatedly encountering errors -> RULE: Troubleshoot in the following way:
  Stop directly trying to solve the problem and take a deep breath. Then step outside of the approach you've been using and ask the following kinds of questions:
  - Am I missing a vital piece of information?
  - Am I executing things in the right order?
  - Are there dependencies I haven't considered?
  - Am I barking up the wrong tree? (Is this approach fundamentally unsound)
  - Are there relevant problem solving principles I can apply?
  - Are there novel angles from which to approach this problem or are there other ways divergent thinking can help me?

- CONDITION: On component invocation (e.g., script/workflow from N5/scripts) -> RULE: Validate interfaces against N5/schemas/index.schema.json; isolate execution in temp env to contain errors

- CONDITION: For cross-module data flow (e.g., knowledge → lists) -> RULE: Enforce modular handoffs with tagged summaries; reject if mismatches detected

- CONDITION: Before destructive actions (e.g., deletes/overwrites) -> RULE: Require dry-run preview and explicit confirmation; validate security against risks in N5/lists/detection_rules.md if it exists

- CONDITION: Before executing system operations (e.g., adding to lists, rebuilding index) -> RULE: Check if a registered command exists in N5/config/commands.jsonl and use it instead of manual operations

- CONDITION: When I request building, refactoring, or modifying significant system components -> RULE: Load file 'Knowledge/architectural/architectural_principles.md' FIRST before any design or implementation work

- CONDITION: When I request creating, modifying, or reviewing a scheduled task -> RULE: Load and follow N5/prefs/operations/scheduled-task-protocol.md before proceeding

- CONDITION: At the start of a new conversation (first response) -> RULE: Initialize SESSION_STATE.md for this conversation workspace by running: python3 /home/workspace/N5/scripts/session_state_manager.py init --convo-id <current_conversation_id> --load-system
```

## Implementation

Copy the rules above into your Zo user settings under "Conditional Rules".

**Note:** Some file paths may not exist yet in your bootstrap. That's OK - the rules will activate when those files are created.
