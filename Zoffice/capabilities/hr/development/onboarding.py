"""
HR — Onboarding Protocol

Validates persona definitions and employee directory structure for new employees.
"""

from pathlib import Path

import yaml


REQUIRED_PERSONA_FIELDS = {"name", "role", "capabilities", "status"}


def validate_persona(persona_dict: dict) -> dict:
    """
    Validate a persona.yaml dict against required schema.

    Returns:
        ValidationResult: valid (bool), issues (list[str])
    """
    issues = []
    for field in REQUIRED_PERSONA_FIELDS:
        if field not in persona_dict:
            issues.append(f"Missing required field: {field}")

    if "capabilities" in persona_dict:
        if not isinstance(persona_dict["capabilities"], list):
            issues.append("'capabilities' must be a list")

    if "status" in persona_dict:
        valid_statuses = {"onboarding", "active", "suspended", "archived"}
        if persona_dict["status"] not in valid_statuses:
            issues.append(f"Invalid status '{persona_dict['status']}'. Must be one of: {valid_statuses}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


def validate_employee_dir(employee_dir: str) -> dict:
    """
    Check that an employee directory has required files.

    Required: persona.yaml, system-prompt.md, tools/manifest.yaml
    """
    d = Path(employee_dir)
    issues = []

    if not d.exists():
        return {"valid": False, "issues": [f"Directory does not exist: {employee_dir}"]}

    required_files = [
        "persona.yaml",
        "system-prompt.md",
    ]
    for f in required_files:
        if not (d / f).exists():
            issues.append(f"Missing required file: {f}")

    tools_manifest = d / "tools" / "manifest.yaml"
    if not tools_manifest.exists():
        issues.append("Missing required file: tools/manifest.yaml")

    # Validate persona.yaml content if it exists
    persona_path = d / "persona.yaml"
    if persona_path.exists():
        with open(persona_path) as f:
            persona = yaml.safe_load(f)
        if persona:
            persona_result = validate_persona(persona)
            issues.extend(persona_result["issues"])

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


def onboard_employee(
    employee_name: str,
    staff_dir: str = "Zoffice/staff/",
) -> dict:
    """
    Validate and register a new employee.

    Returns:
        OnboardingResult: employee, valid, issues, registered, persona_synced
    """
    employee_dir = str(Path(staff_dir) / employee_name)
    validation = validate_employee_dir(employee_dir)

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="hr",
            employee=employee_name,
            action="onboarding_attempt",
            metadata={"valid": validation["valid"], "issues": validation["issues"]},
        )
    except Exception:
        pass

    return {
        "employee": employee_name,
        "valid": validation["valid"],
        "issues": validation["issues"],
        "registered": False,  # Layer 1: registration is manual
        "persona_synced": False,  # Layer 1: sync is dry-run only
    }
