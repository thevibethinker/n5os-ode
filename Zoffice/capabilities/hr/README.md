# HR Capability

**Status:** active

Personnel office — manages employee lifecycle: scenario-based evaluation, structured handoffs, onboarding validation, and staff-to-persona sync.

## Components

- `evaluation/rubric.py` — Scenario-based evaluation framework
- `evaluation/scenarios.yaml` — Base evaluation scenarios (3 scenarios)
- `development/handoff.py` — Context transfer protocol
- `development/onboarding.py` — New employee validation
- `sync.py` — Staff file → Zo persona sync (dry-run in Layer 1)
- `config.yaml` — Evaluation cadence, sync settings

## API Surface

### Evaluation

```python
from Zoffice.capabilities.hr.evaluation.rubric import evaluate_scenario, run_full_evaluation, save_evaluation

result = evaluate_scenario(employee, scenario_name) -> EvalResult dict
results = run_full_evaluation(employee) -> list[EvalResult]
eval_id = save_evaluation(results, employee) -> str
```

### Handoff

```python
from Zoffice.capabilities.hr.development.handoff import prepare_handoff, format_handoff_message

package = prepare_handoff(from_employee, to_employee, conversation_summary, caller_profile=None, pending_actions=None) -> HandoffPackage
message = format_handoff_message(package) -> str
```

### Onboarding

```python
from Zoffice.capabilities.hr.development.onboarding import validate_persona, validate_employee_dir, onboard_employee

result = validate_persona(persona_dict) -> {"valid": bool, "issues": list}
result = validate_employee_dir(dir_path) -> {"valid": bool, "issues": list}
result = onboard_employee(name, staff_dir) -> OnboardingResult dict
```

### Sync

```python
from Zoffice.capabilities.hr.sync import diff_staff, generate_sync_commands, sync

actions = diff_staff() -> list[SyncAction]
commands = generate_sync_commands(actions) -> list[str]
report = sync(dry_run=True) -> SyncReport dict
```
