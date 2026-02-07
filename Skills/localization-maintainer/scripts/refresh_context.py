#!/usr/bin/env python3
"""
Localization Maintainer - Context Refresh Script

Scans the client Zo workspace and builds a current awareness snapshot
of exported content (skills, scripts, prompts, schemas).

Runs on CLIENT Zo instances, not va.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def scan_skills(workspace: Path) -> list[dict]:
    """Find all skills with their metadata."""
    skills = []
    skills_dir = workspace / "Skills"
    if not skills_dir.exists():
        return skills
    
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            # Extract name from frontmatter
            content = skill_md.read_text()
            name = skill_dir.name
            if "name:" in content:
                for line in content.split("\n"):
                    if line.strip().startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                        break
            
            # Check for scripts
            scripts_dir = skill_dir / "scripts"
            scripts = []
            if scripts_dir.exists():
                scripts = [f.name for f in scripts_dir.iterdir() if f.is_file()]
            
            skills.append({
                "name": name,
                "path": str(skill_dir.relative_to(workspace)),
                "scripts": scripts
            })
    
    return skills


def scan_scripts(workspace: Path) -> list[str]:
    """Find system scripts in N5/scripts/."""
    scripts = []
    scripts_dir = workspace / "N5" / "scripts"
    if not scripts_dir.exists():
        return scripts
    
    for f in scripts_dir.iterdir():
        if f.is_file() and f.suffix in [".py", ".sh", ".ts"]:
            scripts.append(f.name)
    
    return scripts


def scan_prompts(workspace: Path) -> list[str]:
    """Find prompt files."""
    prompts = []
    for prompt_file in workspace.rglob("*.prompt.md"):
        # Skip node_modules and other noise
        if "node_modules" in str(prompt_file):
            continue
        prompts.append(str(prompt_file.relative_to(workspace)))
    return prompts


def scan_folder_structure(workspace: Path) -> dict:
    """Get top-level folder structure."""
    structure = {}
    for item in sorted(workspace.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            # Get immediate children
            children = []
            try:
                for child in sorted(item.iterdir())[:10]:  # Limit to 10
                    if child.is_dir():
                        children.append(child.name + "/")
                    else:
                        children.append(child.name)
            except PermissionError:
                pass
            structure[item.name + "/"] = children
    return structure


def find_localization_file(workspace: Path) -> tuple[str | None, str | None]:
    """Find the client's LOCALIZATION.md and determine tier."""
    # Check common locations
    candidates = [
        workspace / "Documents" / "consulting" / "LOCALIZATION.md",
        workspace / "LOCALIZATION.md",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            content = candidate.read_text()
            tier = "simple"
            if "tier: complex" in content:
                tier = "complex"
            return str(candidate.relative_to(workspace)), tier
    
    return None, None


def extract_aliases(localization_path: Path | None) -> dict:
    """Extract alias mappings from LOCALIZATION.md."""
    aliases = {}
    if not localization_path or not Path(localization_path).exists():
        return aliases
    
    content = Path(localization_path).read_text()
    # Simple parse - look for table rows with arrows
    in_adaptations = False
    for line in content.split("\n"):
        if "Active Adaptations" in line or "Naming Aliases" in line:
            in_adaptations = True
            continue
        if in_adaptations and line.startswith("|") and "→" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                canonical = parts[1].strip()
                display = parts[2].strip()
                if "→" in display:
                    canonical, display = display.split("→")
                    canonical = canonical.strip()
                    display = display.strip()
                if canonical and display and canonical != "_example_":
                    aliases[canonical] = display
        if in_adaptations and line.startswith("##") and "Adaptations" not in line:
            in_adaptations = False
    
    return aliases


def refresh_context():
    """Main refresh function."""
    workspace = Path("/home/workspace")
    output_dir = workspace / "N5" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "localization_context.json"
    
    # Scan everything
    skills = scan_skills(workspace)
    scripts = scan_scripts(workspace)
    prompts = scan_prompts(workspace)
    structure = scan_folder_structure(workspace)
    loc_file, tier = find_localization_file(workspace)
    
    # Extract aliases if localization file exists
    aliases = {}
    if loc_file:
        aliases = extract_aliases(workspace / loc_file)
    
    context = {
        "last_refresh": datetime.now(timezone.utc).isoformat(),
        "skills": [s["name"] for s in skills],
        "skills_detail": skills,
        "scripts": scripts,
        "prompts": prompts,
        "folder_structure": structure,
        "conventions": {
            "aliases": aliases,
            "naming_pattern": "kebab-case for folders, snake_case for scripts"
        },
        "localization_tier": tier,
        "localization_file": loc_file
    }
    
    output_file.write_text(json.dumps(context, indent=2))
    print(f"✓ Context refreshed: {output_file}")
    print(f"  Skills: {len(skills)}")
    print(f"  Scripts: {len(scripts)}")
    print(f"  Prompts: {len(prompts)}")
    print(f"  Tier: {tier or 'not set'}")


if __name__ == "__main__":
    refresh_context()
