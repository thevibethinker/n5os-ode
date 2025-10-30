import json

# Rules from the system
rules = [
    {"id": "87801b51-abfe-40f8-a175-b252a11a0b21", "condition": "When DEBUG_LOG.jsonl exists in conversation workspace", "refs": ["N5/scripts/debug_logger.py", "N5/prefs/operations/debug-logging-auto-behavior.md"]},
    {"id": "75305aba-2c4d-40e5-9bdc-2244b011bb6b", "condition": "On component invocation", "refs": ["N5/schemas/index.schema.json"]},
    {"id": "6b2fd151-72cb-4c75-b5ec-2f348f9e8e48", "condition": "Before destructive actions", "refs": ["N5_mirror/scripts/n5_safety.py", "N5/lists/detection_rules.md"]},
    {"id": "4d5bb772-e580-4250-b29d-2a6f67512f44", "condition": "When I suggest moving or deleting files", "refs": ["N5/scripts/n5_protect.py"]},
    {"id": "50952733-3c96-4030-a525-28aad3f77044", "condition": "When building N5 components", "refs": ["Knowledge/architectural/planning_prompt.md"]},
    {"id": "b02bd1e8-add5-4ed3-a2e0-ee94b5aa24cb", "condition": "When creating/modifying scheduled task", "refs": ["N5/prefs/operations/scheduled-task-protocol.md"]},
    {"id": "5c72e81d-529d-44e7-84bf-9d750208949b", "condition": "SESSION_STATE initialization", "refs": ["N5/scripts/session_state_manager.py"]},
]

for rule in rules:
    print(f"\n{'='*60}")
    print(f"Rule: {rule['condition'][:50]}...")
    print(f"ID: {rule['id']}")
    print(f"Files referenced:")
    for ref in rule['refs']:
        print(f"  - {ref}")
