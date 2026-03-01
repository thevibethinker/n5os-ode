# Orchestration Capability

**Status:** active

YAML-defined dispatcher framework for scheduled routines and a workflow state machine for multi-step processes. The "daily schedule and workflow clipboard."

## Components

- `scheduler/dispatcher.py` — Loads YAML dispatchers, converts to Zo agent configs
- `scheduler/morning.yaml` — Morning routine (3 tasks)
- `scheduler/evening.yaml` — Evening routine (3 tasks)
- `scheduler/healthcheck.yaml` — Health check (2 tasks, every 30min)
- `workflows/base.py` — Workflow state machine
- `config.yaml` — Scheduler and workflow settings

## API Surface

### Dispatcher

```python
from Zoffice.capabilities.orchestration.scheduler.dispatcher import (
    load_dispatcher, list_dispatchers, to_agent_config, validate_dispatcher
)

d = load_dispatcher("morning") -> DispatcherDef dict
names = list_dispatchers() -> list[str]
agent_cfg = to_agent_config(d) -> {"rrule": str, "instruction": str, "delivery_method": str}
issues = validate_dispatcher(d) -> list[str]
```

### Workflow Engine

```python
from Zoffice.capabilities.orchestration.workflows.base import Workflow

w = Workflow.default()  # standard 6-state workflow
next_state = w.advance("intake", "item_received") -> "classify"
info = w.get_state_info("intake") -> {"state", "valid_events", "is_terminal", "next_states"}
```

Default states: intake → classify → route → process → respond → close
