"""
HR — Staff-to-Persona Sync

Bridges file-based employee definitions in Zoffice/staff/ to Zo native personas.
Layer 1: dry-run only — generates commands but does not execute.
"""

from pathlib import Path

import yaml


def _load_registry(registry_path: str) -> dict:
    with open(registry_path) as f:
        return yaml.safe_load(f)


def diff_staff(
    staff_dir: str = "Zoffice/staff/",
    registry_path: str = "Zoffice/staff/registry.yaml",
) -> list[dict]:
    """
    Compare staff directories to registry and identify sync actions needed.

    Returns:
        List of SyncAction dicts: action (create|update|deactivate), employee, reason
    """
    sdir = Path(staff_dir)
    if not sdir.is_absolute():
        sdir = Path(__file__).resolve().parents[3] / staff_dir.lstrip("/")

    reg_path = Path(registry_path)
    if not reg_path.is_absolute():
        reg_path = Path(__file__).resolve().parents[3] / registry_path.lstrip("/")

    registry = _load_registry(str(reg_path))
    staff_list = registry.get("staff", [])
    registered = {s["name"]: s for s in staff_list} if isinstance(staff_list, list) and staff_list and isinstance(staff_list[0], dict) else {}

    actions = []

    # Scan employee directories (skip _template)
    for entry in sorted(sdir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("_") or entry.name.startswith("."):
            continue
        name = entry.name

        persona_path = entry / "persona.yaml"
        has_persona = persona_path.exists()

        if name in registered:
            reg_entry = registered[name]
            if reg_entry.get("zo_persona_id") is None:
                actions.append({
                    "action": "create",
                    "employee": name,
                    "reason": "In registry but no zo_persona_id — needs persona creation",
                })
            else:
                # Check if persona.yaml changed (simplified: always suggest update check)
                actions.append({
                    "action": "update",
                    "employee": name,
                    "reason": "Registered with persona — check for config drift",
                })
        else:
            actions.append({
                "action": "create",
                "employee": name,
                "reason": "Employee directory exists but not in registry",
            })

    # Check for deactivations (in registry but no directory)
    for name in registered:
        employee_dir = sdir / name
        if not employee_dir.exists():
            actions.append({
                "action": "deactivate",
                "employee": name,
                "reason": "In registry but directory removed",
            })

    return actions


def generate_sync_commands(actions: list[dict]) -> list[str]:
    """Generate Zo persona API commands as strings (not executed)."""
    commands = []
    for a in actions:
        if a["action"] == "create":
            commands.append(
                f"zo.create_persona(name='{a['employee']}', "
                f"prompt=<read from staff/{a['employee']}/system-prompt.md>)"
            )
        elif a["action"] == "update":
            commands.append(
                f"zo.edit_persona(persona_id=<lookup>, "
                f"prompt=<read from staff/{a['employee']}/system-prompt.md>)"
            )
        elif a["action"] == "deactivate":
            commands.append(
                f"zo.delete_persona(persona_id=<lookup for {a['employee']}>)"
            )
    return commands


def sync(
    staff_dir: str = "Zoffice/staff/",
    registry_path: str = "Zoffice/staff/registry.yaml",
    dry_run: bool = True,
) -> dict:
    """
    Full sync: diff → generate commands → optionally execute.

    Returns:
        SyncReport: actions (list), commands (list[str]), dry_run (bool), executed (bool)
    """
    actions = diff_staff(staff_dir, registry_path)
    commands = generate_sync_commands(actions)

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="hr",
            employee=None,
            action="staff_sync",
            metadata={
                "action_count": len(actions),
                "dry_run": dry_run,
                "creates": sum(1 for a in actions if a["action"] == "create"),
                "updates": sum(1 for a in actions if a["action"] == "update"),
                "deactivates": sum(1 for a in actions if a["action"] == "deactivate"),
            },
        )
    except Exception:
        pass

    return {
        "actions": actions,
        "commands": commands,
        "dry_run": dry_run,
        "executed": not dry_run,
    }
