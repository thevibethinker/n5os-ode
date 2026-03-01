"""
Zo2Zo — Skill Receiver

Validates and (dry-run) installs skill bundles received from parent instances.
"""

from pathlib import Path


REQUIRED_FIELDS = {"name", "files", "version"}


def validate_bundle(bundle: dict) -> dict:
    """
    Validate a skill bundle has required fields.

    Returns:
        ValidationResult: valid (bool), issues (list[str])
    """
    issues = []
    for field in REQUIRED_FIELDS:
        if field not in bundle:
            issues.append(f"Missing required field: {field}")

    if "files" in bundle:
        if not isinstance(bundle["files"], dict):
            issues.append("'files' must be a dict of relative_path → content")
        elif len(bundle["files"]) == 0:
            issues.append("'files' dict is empty — no files to install")

    if "name" in bundle:
        name = bundle["name"]
        if not isinstance(name, str) or not name.strip():
            issues.append("'name' must be a non-empty string")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }


def install_bundle(
    bundle: dict,
    skills_dir: str = "Skills/",
    dry_run: bool = True,
) -> dict:
    """
    Install a skill bundle to the skills directory.

    Args:
        bundle: Validated skill bundle.
        skills_dir: Target directory for skills.
        dry_run: If True (default), only report what would happen.

    Returns:
        InstallResult: installed (bool), path (str), dry_run (bool), issues (list)
    """
    validation = validate_bundle(bundle)
    if not validation["valid"]:
        return {
            "installed": False,
            "path": "",
            "dry_run": dry_run,
            "issues": validation["issues"],
        }

    name = bundle["name"]
    target = Path(skills_dir) / name
    files = bundle.get("files", {})

    if dry_run:
        # Audit log
        try:
            from Zoffice.capabilities.security.audit.writer import log_audit
            log_audit(
                capability="zo2zo",
                employee=None,
                action="skill_install_dry_run",
                metadata={"skill": name, "file_count": len(files)},
            )
        except Exception:
            pass

        return {
            "installed": False,
            "path": str(target),
            "dry_run": True,
            "issues": [],
            "would_create": list(files.keys()),
        }

    # Actual install (not used in Layer 1)
    target.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        file_path = target / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    return {
        "installed": True,
        "path": str(target),
        "dry_run": False,
        "issues": [],
    }
