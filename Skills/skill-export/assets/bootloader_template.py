#!/usr/bin/env python3
"""
__SKILL_NAME_TITLE__ Bootloader v1.0

A respectful installer that surveys the target Zo environment before proposing changes.
Principle: Learn first, propose second, act only with approval.

Usage:
    python3 bootloader.py              # Interactive survey + install
    python3 bootloader.py --survey     # Survey only
    python3 bootloader.py --plan       # Generate plan without executing
    python3 bootloader.py --execute    # Execute with confirmation
    python3 bootloader.py --execute --dry-run  # Preview execution
"""

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# === SKILL CONFIGURATION (populated by export) ===
SKILL_NAME = "__SKILL_SLUG__"
SKILL_DESCRIPTION = """__SKILL_DESCRIPTION__"""

# Paths this skill needs
REQUIRED_PATHS = __REQUIRED_PATHS__

# Secrets this skill needs  
REQUIRED_SECRETS = __REQUIRED_SECRETS__

# Integrations this skill uses
REQUIRED_INTEGRATIONS = __REQUIRED_INTEGRATIONS__
# === END CONFIGURATION ===


@dataclass
class EnvironmentSurvey:
    """Results of surveying the target environment."""
    workspace_root: Path = field(default_factory=lambda: Path("/home/workspace"))
    existing_skills: list = field(default_factory=list)
    existing_folders: dict = field(default_factory=dict)
    existing_agents: list = field(default_factory=list)
    conventions: dict = field(default_factory=dict)
    conflicts: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)


class EnvironmentSurveyor:
    """Surveys the target Zo environment."""
    
    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path("/home/workspace")
        self.survey = EnvironmentSurvey(workspace_root=self.workspace)
    
    def run_survey(self) -> EnvironmentSurvey:
        """Run complete environment survey."""
        self._survey_skills()
        self._survey_folders()
        self._survey_conventions()
        self._detect_conflicts()
        self._generate_recommendations()
        return self.survey
    
    def _survey_skills(self):
        """Find existing skills."""
        skills_dir = self.workspace / "Skills"
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    self.survey.existing_skills.append(item.name)
    
    def _survey_folders(self):
        """Map existing folder structure."""
        key_folders = ["Personal", "Documents", "Projects", "Datasets", "Records", "Knowledge"]
        for folder in key_folders:
            path = self.workspace / folder
            if path.exists():
                self.survey.existing_folders[folder] = True
                # Check for meetings-related folders
                if folder == "Personal":
                    meetings = path / "Meetings"
                    if meetings.exists():
                        self.survey.existing_folders["Personal/Meetings"] = True
    
    def _survey_conventions(self):
        """Detect naming conventions and patterns."""
        self.survey.conventions["date_format"] = "YYYY-MM-DD"
        
        # Check for AGENTS.md
        agents_md = self.workspace / "AGENTS.md"
        self.survey.conventions["has_agents_md"] = agents_md.exists()
        
        # Check for N5 system
        n5_dir = self.workspace / "N5"
        self.survey.conventions["has_n5"] = n5_dir.exists()
    
    def _detect_conflicts(self):
        """Detect potential conflicts with existing systems."""
        if SKILL_NAME in self.survey.existing_skills:
            self.survey.conflicts.append({
                "type": "skill_exists",
                "message": f"Skill '{SKILL_NAME}' already exists",
                "severity": "warning",
                "resolution": "Will backup existing and install new version"
            })
        
        for path_key, path_info in REQUIRED_PATHS.items():
            default_path = path_info.get("default", "")
            if default_path:
                full_path = self.workspace / default_path
                if full_path.exists():
                    self.survey.conflicts.append({
                        "type": "path_exists", 
                        "message": f"Path '{full_path}' already exists",
                        "severity": "info",
                        "resolution": "Will use existing path"
                    })
    
    def _generate_recommendations(self):
        """Generate installation recommendations."""
        for secret in REQUIRED_SECRETS:
            self.survey.recommendations.append({
                "setting": secret,
                "reason": "Required for skill functionality",
                "action": "Add to Zo Settings > Developers"
            })
        
        for integration in REQUIRED_INTEGRATIONS:
            self.survey.recommendations.append({
                "setting": f"{integration} integration",
                "reason": "Used by this skill",
                "action": "Connect in Zo Settings > Integrations"
            })


class InstallationPlanner:
    """Generates installation plan based on survey."""
    
    def __init__(self, survey: EnvironmentSurvey):
        self.survey = survey
        self.plan = {"steps": [], "backup_paths": [], "config_values": {}}
    
    def generate_plan(self) -> dict:
        """Generate installation plan."""
        skill_dir = self.survey.workspace_root / "Skills" / SKILL_NAME
        
        if SKILL_NAME in self.survey.existing_skills:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = skill_dir.parent / f"{SKILL_NAME}.backup.{timestamp}"
            self.plan["steps"].append({
                "action": "backup",
                "source": str(skill_dir),
                "dest": str(backup_path),
                "description": f"Backup existing {SKILL_NAME} skill"
            })
            self.plan["backup_paths"].append(str(backup_path))
        
        self.plan["steps"].append({
            "action": "install",
            "source": str(Path(__file__).parent),
            "dest": str(skill_dir),
            "description": f"Install {SKILL_NAME} to Skills/"
        })
        
        self.plan["steps"].append({
            "action": "create_config",
            "templates": ["config/settings.yaml.example", "config/blocks.yaml.example"],
            "description": "Create configuration files from templates"
        })
        
        if REQUIRED_SECRETS:
            secrets_str = ', '.join(REQUIRED_SECRETS)
            self.plan["steps"].append({
                "action": "manual",
                "description": f"Set secrets in Zo Settings > Developers: {secrets_str}"
            })
        
        return self.plan


class Installer:
    """Executes installation plan."""
    
    def __init__(self, plan: dict, workspace: Path):
        self.plan = plan
        self.workspace = workspace
        self.record = {"installed_at": None, "steps_completed": [], "rollback_info": {}}
    
    def execute(self, dry_run: bool = False):
        """Execute the installation plan."""
        prefix = "[DRY RUN] " if dry_run else ""
        print(f"\n{prefix}EXECUTING INSTALLATION PLAN")
        print("=" * 60)
        
        for i, step in enumerate(self.plan["steps"], 1):
            print(f"\nStep {i}: {step['description']}")
            
            if dry_run:
                print(f"   [DRY RUN] Would execute: {step['action']}")
                continue
            
            try:
                if step["action"] == "backup":
                    shutil.copytree(step["source"], step["dest"])
                    print(f"   ✓ Backed up to {step['dest']}")
                
                elif step["action"] == "install":
                    source = Path(step["source"])
                    dest = Path(step["dest"])
                    
                    if dest.exists():
                        shutil.rmtree(dest)
                    
                    dest.mkdir(parents=True, exist_ok=True)
                    for item in source.iterdir():
                        if item.name in ["bootloader.py", ".git", "__pycache__"]:
                            continue
                        if item.is_dir():
                            shutil.copytree(item, dest / item.name)
                        else:
                            shutil.copy2(item, dest / item.name)
                    
                    print(f"   ✓ Installed to {dest}")
                
                elif step["action"] == "create_config":
                    skill_dir = self.workspace / "Skills" / SKILL_NAME
                    
                    for template in step.get("templates", []):
                        template_path = skill_dir / template
                        if template_path.exists():
                            # settings.yaml.example -> settings.yaml
                            config_name = template_path.name.replace(".example", "")
                            config_path = template_path.parent / config_name
                            if not config_path.exists():
                                shutil.copy2(template_path, config_path)
                                print(f"   ✓ Created {config_path.name}")
                
                elif step["action"] == "manual":
                    print(f"   ⚠ Manual step required: {step['description']}")
                
                self.record["steps_completed"].append(step)
                
            except Exception as e:
                print(f"   ✗ Failed: {e}")
                raise
        
        self.record["installed_at"] = datetime.now().isoformat()
        
        if not dry_run:
            record_path = self.workspace / "Skills" / SKILL_NAME / ".installation_record.json"
            with open(record_path, "w") as f:
                json.dump(self.record, f, indent=2)
        
        print("\n" + "=" * 60)
        msg = "✓ Installation complete!" if not dry_run else "[DRY RUN] Installation preview complete"
        print(msg)


def print_survey(survey: EnvironmentSurvey):
    """Pretty print survey results."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT SURVEY RESULTS")
    print("=" * 60)
    
    print(f"\nWorkspace: {survey.workspace_root}")
    
    print(f"\nExisting Skills ({len(survey.existing_skills)}):")
    for skill in survey.existing_skills[:10]:
        marker = "⚠" if skill == SKILL_NAME else "•"
        print(f"   {marker} {skill}")
    if len(survey.existing_skills) > 10:
        print(f"   ... and {len(survey.existing_skills) - 10} more")
    
    print(f"\nFolder Structure:")
    for folder, exists in survey.existing_folders.items():
        check = "✓" if exists else "✗"
        print(f"   {check} {folder}")
    
    print(f"\nConventions Detected:")
    for key, value in survey.conventions.items():
        print(f"   • {key}: {value}")
    
    if survey.conflicts:
        print(f"\n⚠ Potential Conflicts ({len(survey.conflicts)}):")
        for conflict in survey.conflicts:
            sev = conflict['severity'].upper()
            print(f"   [{sev}] {conflict['message']}")
            print(f"      Resolution: {conflict['resolution']}")
    
    if survey.recommendations:
        print(f"\n📋 Recommendations:")
        for rec in survey.recommendations:
            print(f"   • {rec['setting']}")
            print(f"     Action: {rec['action']}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Install {SKILL_NAME} skill respectfully"
    )
    parser.add_argument("--workspace", default="/home/workspace",
                       help="Target workspace path")
    parser.add_argument("--survey", action="store_true",
                       help="Run survey only, no installation")
    parser.add_argument("--plan", action="store_true", 
                       help="Generate plan without executing")
    parser.add_argument("--execute", action="store_true",
                       help="Execute installation")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview what would happen")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")
    
    args = parser.parse_args()
    workspace = Path(args.workspace)
    
    print(f"\n🔍 Surveying environment at {workspace}...")
    surveyor = EnvironmentSurveyor(workspace)
    survey = surveyor.run_survey()
    
    if args.survey:
        if args.json:
            print(json.dumps({
                "existing_skills": survey.existing_skills,
                "existing_folders": survey.existing_folders,
                "conventions": survey.conventions,
                "conflicts": survey.conflicts,
                "recommendations": survey.recommendations
            }, indent=2))
        else:
            print_survey(survey)
        return
    
    print_survey(survey)
    
    planner = InstallationPlanner(survey)
    plan = planner.generate_plan()
    
    if args.plan or not args.execute:
        print("\n" + "=" * 60)
        print("INSTALLATION PLAN")
        print("=" * 60)
        for i, step in enumerate(plan["steps"], 1):
            print(f"\n{i}. {step['description']}")
            print(f"   Action: {step['action']}")
        
        if not args.execute:
            print("\n" + "-" * 60)
            print("Run with --execute to install, or --execute --dry-run to preview")
        return
    
    if survey.conflicts:
        print("\n⚠ CONFLICTS DETECTED:")
        for conflict in survey.conflicts:
            print(f"   {conflict['message']}")
            print(f"   Resolution: {conflict['resolution']}")
        
        if not args.dry_run:
            response = input("\nProceed? (yes/no): ")
            if response.lower() != "yes":
                print("Installation cancelled.")
                return
    
    installer = Installer(plan, workspace)
    installer.execute(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
