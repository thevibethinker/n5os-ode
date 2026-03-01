#!/usr/bin/env python3
"""
Consulting API - Skill Bundle Manager

Handles creation, validation, and transmission of skill bundles
between va and zoputer in the Zoffice Consultancy Stack.

Usage:
    python3 bundle_manager.py create --skill security-gate --output /path/to/bundle.json
    python3 bundle_manager.py validate --bundle /path/to/bundle.json
    python3 bundle_manager.py list-exportable
    python3 bundle_manager.py transmit --bundle /path/to/bundle.json --target zoputer
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import audit logger
sys.path.insert(0, "/home/workspace/Skills/audit-system/scripts")
from audit_logger import log_entry, ZO_INSTANCE

try:
    import yaml
except ImportError:
    yaml = None

# Bundle storage
BUNDLE_DIR = Path("/home/workspace/N5/config/consulting/bundles")

# Skill registry - canonical list of exportable skills
EXPORTABLE_SKILLS = [
    "security-gate",
    "audit-system",
    "consulting-api",
    "content-classifier",
    "librarian-export",
]


def load_allowed_targets() -> set[str]:
    """
    Load allowed transmission targets.
    Priority:
      1) CONSULTING_API_ALLOWED_TARGETS env var (comma-separated)
      2) zo-substrate config identity + partner handles/names
    """
    env_targets = {
        t.strip()
        for t in os.environ.get("CONSULTING_API_ALLOWED_TARGETS", "").split(",")
        if t.strip()
    }
    if env_targets:
        return env_targets

    allowed = {"zoputer", "zoputer.zo.computer"}
    substrate_cfg = Path("/home/workspace/Skills/zo-substrate/config/substrate.yaml")
    if yaml and substrate_cfg.exists():
        try:
            cfg = yaml.safe_load(substrate_cfg.read_text()) or {}
            for section in ("identity", "partner"):
                block = cfg.get(section, {}) or {}
                for key in ("name", "handle"):
                    value = str(block.get(key, "")).strip()
                    if value:
                        allowed.add(value)
        except Exception:
            pass
    return allowed


def normalize_target(target: str) -> str:
    return target.strip()


def load_bundle_from_path(bundle_path: Path) -> tuple[dict, Optional[str]]:
    """
    Load bundle dict from JSON or .tar.gz.
    Returns (bundle, error_message).
    """
    if str(bundle_path).endswith(".tar.gz"):
        import tarfile

        try:
            with tarfile.open(bundle_path, "r:gz") as tar:
                try:
                    metadata_file = tar.extractfile("metadata.json")
                    if not metadata_file:
                        return {}, "No metadata.json found in tarball"
                    metadata = json.loads(metadata_file.read().decode("utf-8"))
                except KeyError:
                    return {}, "No metadata.json found in tarball"

            bundle = {
                "schema_version": "1.0",
                "bundle_type": "skill",
                "skill": {
                    "name": metadata.get("name"),
                    "version": metadata.get("version"),
                },
                "content": {"skill_md": "", "scripts": {}, "assets": {}},
                "metadata": metadata,
            }
            return bundle, None
        except Exception as e:
            return {}, f"Failed to read tarball: {e}"

    try:
        return json.loads(bundle_path.read_text()), None
    except Exception as e:
        return {}, f"Failed to read JSON bundle: {e}"


def compute_bundle_hash(bundle_path: Path) -> str:
    """Compute SHA-256 hash of bundle file."""
    return hashlib.sha256(bundle_path.read_bytes()).hexdigest()


def create_skill_bundle(skill_name: str, version: str = "1.0.0") -> dict:
    """
    Create a skill bundle from a skill directory.
    
    Returns:
        dict with bundle metadata and content
    """
    skill_path = Path(f"/home/workspace/Skills/{skill_name}")
    
    if not skill_path.exists():
        raise ValueError(f"Skill not found: {skill_name}")
    
    # Read SKILL.md
    skill_md_path = skill_path / "SKILL.md"
    skill_md = skill_md_path.read_text() if skill_md_path.exists() else ""
    
    # Read all scripts
    scripts = {}
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        include_ext = {".py", ".ts", ".js", ".mjs", ".cjs", ".sh", ".bash", ".zsh"}
        for script_file in scripts_dir.rglob("*"):
            if not script_file.is_file():
                continue
            if script_file.suffix.lower() not in include_ext:
                continue
            rel_path = str(script_file.relative_to(scripts_dir))
            scripts[rel_path] = script_file.read_text(errors="replace")
    
    # Read assets
    assets = {}
    assets_dir = skill_path / "assets"
    if assets_dir.exists():
        for asset_file in assets_dir.rglob("*"):
            if asset_file.is_file():
                rel_path = str(asset_file.relative_to(assets_dir))
                assets[rel_path] = asset_file.read_bytes().hex()
    
    # Create bundle
    bundle = {
        "schema_version": "1.0",
        "bundle_type": "skill",
        "skill": {
            "name": skill_name,
            "version": version,
            "exported_from": ZO_INSTANCE,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        },
        "content": {
            "skill_md": skill_md,
            "scripts": scripts,
            "assets": assets,
        },
        "metadata": {
            "source_path": str(skill_path),
            "file_count": len(scripts) + len(assets) + (1 if skill_md else 0),
        }
    }
    
    return bundle


def validate_bundle(bundle: dict) -> dict:
    """
    Validate a skill bundle structure and content.
    
    Returns:
        dict with validation results
    """
    errors = []
    warnings = []
    
    # Check schema version
    if bundle.get("schema_version") != "1.0":
        warnings.append(f"Unexpected schema version: {bundle.get('schema_version')}")
    
    # Check required fields
    if "skill" not in bundle:
        errors.append("Missing 'skill' section")
    else:
        skill = bundle["skill"]
        if "name" not in skill:
            errors.append("Missing skill.name")
        if "version" not in skill:
            errors.append("Missing skill.version")
    
    # Check content
    if "content" not in bundle:
        errors.append("Missing 'content' section")
    else:
        content = bundle["content"]
        
        # SKILL.md should exist
        if not content.get("skill_md"):
            warnings.append("Missing SKILL.md content")
        
        # Should have scripts or assets
        if not content.get("scripts") and not content.get("assets"):
            warnings.append("Bundle has no scripts or assets")
        
        # Check for potentially hardcoded credentials in scripts
        for script_name, script_content in content.get("scripts", {}).items():
            hardcoded_credential_patterns = [
                r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]",
                r"(?i)\b(sk_live|sk_test|ghp_|xoxb-|AIza)[A-Za-z0-9_\-]{8,}",
            ]
            for pattern in hardcoded_credential_patterns:
                if re.search(pattern, script_content):
                    errors.append(
                        f"Script {script_name} appears to contain hardcoded credentials"
                    )
                    break
            if re.search(r"(?i)\b(secret|token|password)\b", script_content) and "os.environ" not in script_content:
                warnings.append(
                    f"Script {script_name} mentions secrets/tokens - verify they are environment-based"
                )
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def export_bundle(bundle: dict, output_path: Path) -> None:
    """Export bundle to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, indent=2))


def list_exportable_skills() -> list:
    """List skills that are available for export."""
    available = []
    for skill_name in EXPORTABLE_SKILLS:
        skill_path = Path(f"/home/workspace/Skills/{skill_name}")
        if skill_path.exists():
            # Check for SKILL.md
            has_skill_md = (skill_path / "SKILL.md").exists()
            # Count scripts
            scripts_dir = skill_path / "scripts"
            if scripts_dir.exists():
                script_count = sum(
                    1
                    for p in scripts_dir.rglob("*")
                    if p.is_file() and p.suffix.lower() in {".py", ".ts", ".js", ".mjs", ".cjs", ".sh", ".bash", ".zsh"}
                )
            else:
                script_count = 0
            
            available.append({
                "name": skill_name,
                "path": str(skill_path),
                "has_skill_md": has_skill_md,
                "script_count": script_count,
                "exportable": has_skill_md,  # Must have SKILL.md
            })
    
    return available


def transmit_bundle(bundle_path: Path, target: str, dry_run: bool = False) -> dict:
    """
    Transmit a bundle to the target Zo instance.
    
    Supports both JSON bundles and tarball bundles (.tar.gz).
    For now, this creates a transmission record. In production, this would
    use the actual API to send to zoputer.zo.computer.
    
    Returns:
        dict with transmission result
    """
    import uuid
    
    correlation_id = str(uuid.uuid4())
    target = normalize_target(target)
    allowed_targets = load_allowed_targets()
    if target not in allowed_targets:
        return {
            "success": False,
            "error": "target_not_allowed",
            "target": target,
            "allowed_targets": sorted(allowed_targets),
        }

    bundle, load_error = load_bundle_from_path(bundle_path)
    if load_error:
        return {"success": False, "error": load_error}
    
    # Validate before transmission
    validation = validate_bundle(bundle)
    if not validation["valid"]:
        return {
            "success": False,
            "error": "Bundle validation failed",
            "validation": validation,
        }
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "bundle_size": bundle_path.stat().st_size,
            "target": target,
            "validation": validation,
        }
    
    # Log the transmission
    log_entry(
        entry_type="skill_bundle",
        direction=f"{ZO_INSTANCE}-to-{target}",
        payload=json.dumps({
            "bundle_path": str(bundle_path),
            "skill_name": bundle["skill"]["name"],
            "skill_version": bundle["skill"]["version"],
            "bundle_hash": compute_bundle_hash(bundle_path),
        }),
        correlation_id=correlation_id,
        metadata={
            "target": target,
            "validation_passed": True,
            "bundle_size_bytes": bundle_path.stat().st_size,
        }
    )
    
    # TODO: Actual API transmission to zoputer.zo.computer
    # For now, we just log it and return success
    
    return {
        "success": True,
        "correlation_id": correlation_id,
        "bundle_size": bundle_path.stat().st_size,
        "target": target,
        "transmitted_at": datetime.now(timezone.utc).isoformat(),
        "note": "Bundle logged for transmission. Actual API integration pending.",
    }


def create_daily_manifest() -> dict:
    """
    Create a manifest of all bundles to export in the daily sync.
    
    Returns:
        dict with manifest of changed skills
    """
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": ZO_INSTANCE,
        "bundles": [],
    }
    
    for skill_info in list_exportable_skills():
        if not skill_info["exportable"]:
            continue
        
        skill_name = skill_info["name"]
        
        # Check if changed since last export
        # TODO: Implement change detection via git or file hashes
        
        manifest["bundles"].append({
            "skill": skill_name,
            "include": True,  # TODO: Change detection
            "reason": "pending_change_detection",
        })
    
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Consulting API Bundle Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # create command
    create_parser = subparsers.add_parser("create", help="Create a skill bundle")
    create_parser.add_argument("--skill", required=True, help="Skill name to bundle")
    create_parser.add_argument("--version", default="1.0.0", help="Bundle version")
    create_parser.add_argument("--output", required=True, help="Output file path")
    create_parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    
    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a bundle")
    validate_parser.add_argument("--bundle", required=True, help="Bundle file path")
    validate_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # list-exportable command
    subparsers.add_parser("list-exportable", help="List exportable skills")
    
    # transmit command
    transmit_parser = subparsers.add_parser("transmit", help="Transmit bundle to target")
    transmit_parser.add_argument("--bundle", required=True, help="Bundle file path")
    transmit_parser.add_argument("--target", default="zoputer", help="Target instance")
    transmit_parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    
    # manifest command
    manifest_parser = subparsers.add_parser("manifest", help="Create daily manifest")
    manifest_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "create":
        try:
            bundle = create_skill_bundle(args.skill, args.version)
            if not args.dry_run:
                export_bundle(bundle, Path(args.output))
            if args.dry_run:
                print(f"Dry run: bundle would be written to: {args.output}")
            else:
                print(f"Created bundle: {args.output}")
            print(f"  Skill: {bundle['skill']['name']} v{bundle['skill']['version']}")
            print(f"  Files: {bundle['metadata']['file_count']}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    elif args.command == "validate":
        bundle, load_error = load_bundle_from_path(Path(args.bundle))
        if load_error:
            print(f"Error: {load_error}")
            sys.exit(1)
        result = validate_bundle(bundle)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Valid: {result['valid']}")
            if result['errors']:
                print("Errors:")
                for e in result['errors']:
                    print(f"  - {e}")
            if result['warnings']:
                print("Warnings:")
                for w in result['warnings']:
                    print(f"  - {w}")
        
        sys.exit(0 if result['valid'] else 1)
    
    elif args.command == "list-exportable":
        skills = list_exportable_skills()
        print(f"{'Skill':<25} {'Exportable':<12} {'Scripts':<10} {'Path':<40}")
        print("-" * 90)
        for s in skills:
            print(f"{s['name']:<25} {str(s['exportable']):<12} {s['script_count']:<10} {s['path']:<40}")
    
    elif args.command == "transmit":
        result = transmit_bundle(Path(args.bundle), args.target, args.dry_run)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
    
    elif args.command == "manifest":
        manifest = create_daily_manifest()
        if args.output:
            Path(args.output).write_text(json.dumps(manifest, indent=2))
            print(f"Manifest written to: {args.output}")
        else:
            print(json.dumps(manifest, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
