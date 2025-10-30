#!/usr/bin/env python3
"""
N5 OS Core Installation Script

Installs N5 OS Core on a fresh Zo Computer instance.
Handles initial setup, configuration generation, and validation.

Usage:
    python3 n5_install.py [--dry-run] [--force]
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Paths
WORKSPACE = Path("/home/workspace")
N5_ROOT = WORKSPACE / "N5"
DOCUMENTS = WORKSPACE / "Documents"

class N5Installer:
    def __init__(self, dry_run=False, force=False):
        self.dry_run = dry_run
        self.force = force
        self.errors = []
        
    def log(self, message, level="INFO"):
        """Log installation progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "[DRY-RUN] " if self.dry_run else ""
        print(f"{prefix}[{timestamp}] {level}: {message}")
        
    def check_prerequisites(self):
        """Verify system requirements"""
        self.log("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 12):
            self.errors.append("Python 3.12+ required")
            return False
            
        # Check if N5 directory exists
        if N5_ROOT.exists() and not self.force:
            self.errors.append(f"N5 already exists at {N5_ROOT}. Use --force to overwrite.")
            return False
            
        return True
        
    def create_directory_structure(self):
        """Create N5 directory structure"""
        self.log("Creating directory structure...")
        
        directories = [
            N5_ROOT / "config",
            N5_ROOT / "Lists",
            N5_ROOT / "Records", 
            N5_ROOT / "Recipes",
            N5_ROOT / "bulletins",
            DOCUMENTS / "N5_docs"
        ]
        
        for directory in directories:
            if self.dry_run:
                self.log(f"Would create: {directory}")
            else:
                directory.mkdir(parents=True, exist_ok=True)
                self.log(f"Created: {directory}")
                
    def generate_configs_from_templates(self):
        """Generate active configs from templates"""
        self.log("Generating configurations from templates...")
        
        template_dir = N5_ROOT / "templates"
        config_dir = N5_ROOT / "config"
        
        if not template_dir.exists():
            self.errors.append(f"Templates directory not found: {template_dir}")
            return False
            
        # Commands
        commands_template = template_dir / "config" / "commands.template.jsonl"
        commands_config = config_dir / "commands.jsonl"
        
        if commands_template.exists():
            if self.dry_run:
                self.log(f"Would copy: {commands_template} -> {commands_config}")
            else:
                shutil.copy(commands_template, commands_config)
                self.log(f"Generated: {commands_config}")
        
        return True
        
    def create_readme_files(self):
        """Create README files for key directories"""
        self.log("Creating README files...")
        
        readmes = {
            N5_ROOT / "Lists" / "README.md": """# Lists

Curated collections for tracking items that need action or monitoring.

## Purpose

Lists are **mutable** - items can be added, removed, or reordered as needed.

## Files

- `todos.md` - Action items requiring completion
- `reading_list.md` - Content to consume
- `detection_rules.md` - Security patterns to monitor

## Usage

Add items as needed, remove when complete. These are working documents.
""",
            N5_ROOT / "Records" / "README.md": """# Records

Append-only logs for immutable history and audit trails.

## Purpose

Records are **immutable** - entries are appended but never modified or deleted.

## Files

- `decisions.jsonl` - Architecture and design decisions
- `incidents.jsonl` - System events and issues
- `sessions.jsonl` - Session summaries and outcomes

## Format

Use JSONL (one JSON object per line) for machine-readable records:

```json
{"timestamp": "2025-10-28T07:00:00Z", "type": "decision", "description": "..."}
```

## Usage

Append new entries. Never edit or delete existing records.
""",
            N5_ROOT / "Recipes" / "README.md": """# Recipes

Reusable workflows and procedures, invokable via slash commands.

## Purpose

Recipes are **executable** - markdown files that define workflows for Zo to execute.

## Format

```markdown
---
description: Brief description of workflow
tags: [tag1, tag2]
---

# Workflow Name

Steps for Zo to execute...
```

## Usage

Create markdown files in this directory. Reference them in conversations with `/recipe-name`.
"""
        }
        
        for path, content in readmes.items():
            if self.dry_run:
                self.log(f"Would create: {path}")
            else:
                path.write_text(content)
                self.log(f"Created: {path}")
                
    def create_user_guide(self):
        """Create user-facing N5.md in Documents"""
        self.log("Creating user guide...")
        
        n5_md = DOCUMENTS / "N5.md"
        
        content = """# N5 OS Core - Quick Reference

> Personal AI Operating System for your Zo Computer

## What is N5?

N5 OS Core provides session management, safety systems, and workflow automation for your Zo instance.

## Getting Started

N5 automatically initializes for each conversation. You'll see a session ID when you start chatting.

## Key Features

- **Session Management** - Context tracking across conversations
- **Safety Systems** - Protected paths prevent accidental deletion
- **Bulletins** - System-wide announcements
- **Commands** - Custom slash commands
- **Recipes** - Reusable workflows

## Common Commands

```bash
# Check system status
python3 N5/scripts/n5_audit.py

# View bulletins
python3 N5/scripts/bulletins.py list

# List commands
python3 N5/scripts/commands.py list
```

## Documentation

Full documentation: `file 'N5/docs/user_guide.md'`

## Support

- Issues: https://github.com/vrijenattawar/zo-n5os-core/issues
- Email: vademonstrator@zo.computer

---

**Version**: 0.1.0 (Cesc)
"""
        
        if self.dry_run:
            self.log(f"Would create: {n5_md}")
        else:
            n5_md.write_text(content)
            self.log(f"Created: {n5_md}")
            
    def create_initial_bulletins(self):
        """Create welcome bulletin"""
        self.log("Creating initial bulletins...")
        
        bulletin = {
            "id": "welcome-v0.1",
            "title": "Welcome to N5 OS Core v0.1 (Cesc)",
            "message": "N5 has been successfully installed. Check Documents/N5.md for quick reference.",
            "created": datetime.now().isoformat(),
            "priority": "info",
            "active": True
        }
        
        bulletin_file = N5_ROOT / "bulletins" / "welcome.json"
        
        if self.dry_run:
            self.log(f"Would create: {bulletin_file}")
        else:
            bulletin_file.write_text(json.dumps(bulletin, indent=2))
            self.log(f"Created: {bulletin_file}")
            
    def validate_installation(self):
        """Run validation checks"""
        self.log("Validating installation...")
        
        required_paths = [
            N5_ROOT / "scripts",
            N5_ROOT / "schemas",
            N5_ROOT / "prefs",
            N5_ROOT / "config",
            N5_ROOT / "Lists",
            N5_ROOT / "Records",
            N5_ROOT / "Recipes"
        ]
        
        for path in required_paths:
            if not path.exists():
                self.errors.append(f"Missing required path: {path}")
                
        if self.errors:
            return False
            
        self.log("Validation passed")
        return True
        
    def install(self):
        """Run complete installation"""
        self.log("Starting N5 OS Core installation...")
        self.log(f"Target: {N5_ROOT}")
        
        if not self.check_prerequisites():
            self.log("Prerequisites check failed", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
            return False
            
        self.create_directory_structure()
        
        if not self.generate_configs_from_templates():
            self.log("Configuration generation failed", "ERROR")
            return False
            
        self.create_readme_files()
        self.create_user_guide()
        self.create_initial_bulletins()
        
        if not self.dry_run:
            if not self.validate_installation():
                self.log("Installation validation failed", "ERROR")
                for error in self.errors:
                    self.log(f"  - {error}", "ERROR")
                return False
        
        self.log("Installation complete!", "SUCCESS")
        self.log(f"Next steps:")
        self.log(f"  1. Review: {DOCUMENTS / 'N5.md'}")
        self.log(f"  2. Initialize session: python3 {N5_ROOT / 'scripts/session_state_manager.py'} init")
        self.log(f"  3. Check status: python3 {N5_ROOT / 'scripts/n5_audit.py'}")
        
        return True

def main():
    parser = argparse.ArgumentParser(
        description="Install N5 OS Core on Zo Computer"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true", 
        help="Overwrite existing installation"
    )
    
    args = parser.parse_args()
    
    installer = N5Installer(dry_run=args.dry_run, force=args.force)
    success = installer.install()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
