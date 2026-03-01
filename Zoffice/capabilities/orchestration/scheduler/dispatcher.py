"""
Orchestration — Dispatcher Framework

Loads YAML-defined scheduled routines and converts them to Zo agent configurations.
Actual agent creation is handled by rice-integration.
"""

from pathlib import Path

import yaml


def _scheduler_dir() -> Path:
    return Path(__file__).resolve().parent


def load_dispatcher(name: str, scheduler_dir: str | None = None) -> dict:
    """
    Load a dispatcher definition from YAML.

    Args:
        name: Dispatcher name (without .yaml extension).
        scheduler_dir: Override path to scheduler directory.

    Returns:
        DispatcherDef dict with: name, schedule, timezone, employee, tasks.
    """
    sdir = Path(scheduler_dir) if scheduler_dir else _scheduler_dir()
    path = sdir / f"{name}.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def list_dispatchers(scheduler_dir: str | None = None) -> list[str]:
    """List available dispatcher names."""
    sdir = Path(scheduler_dir) if scheduler_dir else _scheduler_dir()
    return [
        p.stem for p in sdir.glob("*.yaml")
        if p.stem != "__init__"
    ]


def to_agent_config(dispatcher_def: dict) -> dict:
    """
    Convert a dispatcher definition to Zo scheduled agent format.

    Returns:
        dict with: rrule, instruction, delivery_method
    """
    schedule = dispatcher_def.get("schedule", "0 8 * * *")
    tz = dispatcher_def.get("timezone", "America/New_York")
    employee = dispatcher_def.get("employee", "chief-of-staff")
    tasks = dispatcher_def.get("tasks", [])
    name = dispatcher_def.get("name", "unnamed-dispatcher")

    # Convert cron to RRULE (simplified: daily at the hour)
    parts = schedule.split()
    minute = parts[0] if len(parts) > 0 else "0"
    hour = parts[1] if len(parts) > 1 else "8"

    # Build instruction from tasks
    task_lines = "\n".join(
        f"  {i+1}. {t['name']}: {t.get('description', '')}"
        for i, t in enumerate(tasks)
    )
    instruction = (
        f"Execute the {name} routine as {employee}.\n\n"
        f"Tasks:\n{task_lines}\n\n"
        f"Complete each task in order and report results."
    )

    return {
        "rrule": f"FREQ=DAILY;BYHOUR={hour};BYMINUTE={minute}",
        "instruction": instruction,
        "delivery_method": "none",
        "name": name,
        "timezone": tz,
    }


def validate_dispatcher(dispatcher_def: dict) -> list[str]:
    """
    Validate a dispatcher definition.

    Returns:
        List of issues (empty = valid).
    """
    issues = []
    if not dispatcher_def.get("name"):
        issues.append("Missing 'name' field")
    if not dispatcher_def.get("schedule"):
        issues.append("Missing 'schedule' field")
    if not dispatcher_def.get("tasks"):
        issues.append("No tasks defined")
    else:
        for i, task in enumerate(dispatcher_def["tasks"]):
            if not task.get("name"):
                issues.append(f"Task {i} missing 'name'")
    return issues
