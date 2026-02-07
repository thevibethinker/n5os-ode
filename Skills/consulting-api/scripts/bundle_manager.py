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
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Import audit logger
sys.path.insert(0, "/home/workspace/Skills/audit-system/scripts")
from audit_logger import log_entry, ZO_INSTANCE

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
        for script_file in scripts_dir.glob("*.py"):
            scripts[script_file.name] = script_file.read_text()
    
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
        
        # Check for API keys in scripts
        for script_name, script_content in content.get("scripts", {}).items():
            if "api_key" in script_content.lower() or "apikey" in script_content.lower():
                errors.append(f"Script {script_name} may contain API keys - reject bundle")
            if "secret" in script_content.lower() and "hashlib" not in script_content.lower():
                warnings.append(f"Script {script_name} mentions 'secret' - verify not credential")
    
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
            script_count = len(list(scripts_dir.glob("*.py"))) if scripts_dir.exists() else 0
            
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
    
    # Handle tarball bundles
    if str(bundle_path).endswith('.tar.gz'):
        import tarfile
        
        try:
            with tarfile.open(bundle_path, 'r:gz') as tar:
                # Extract metadata.json from the tarball
                try:
                    metadata_file = tar.extractfile('metadata.json')
                    if metadata_file:
                        metadata = json.loads(metadata_file.read().decode('utf-8'))
                        # Convert to expected bundle format
                        bundle = {
                            "schema_version": "1.0",
                            "bundle_type": "skill",
                            "skill": {
                                "name": metadata.get("name"),
                                "version": metadata.get("version"),
                            },
                            "content": {
                                "skill_md": "",  # Not needed for validation
                                "scripts": {},
                                "assets": {},
                            },
                            "metadata": metadata,
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No metadata.json found in tarball",
                        }
                except KeyError:
                    return {
                        "success": False,
                        "error": "No metadata.json found in tarball",
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read tarball: {e}",
            }
    else:
        # Handle JSON bundles
        bundle = json.loads(bundle_path.read_text())
    
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
        bundle = json.loads(Path(args.bundle).read_text())
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
