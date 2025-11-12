#!/usr/bin/env python3
"""
N5OS Lite Onboarding Wizard

Personalizes N5OS Lite installation for new users.
Configures preferences, creates initial structure, validates setup.

Usage:
    python3 scripts/onboarding_wizard.py
    python3 scripts/onboarding_wizard.py --non-interactive --name "John Doe"
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class OnboardingWizard:
    def __init__(self, workspace_root, interactive=True):
        self.workspace = Path(workspace_root)
        self.interactive = interactive
        self.config = {}
    
    def run(self):
        """Execute full onboarding workflow"""
        print("🚀 N5OS Lite Onboarding Wizard")
        print("=" * 50)
        print()
        
        # Step 1: Collect user information
        if not self.collect_user_info():
            return False
        
        # Step 2: Configure preferences
        if not self.configure_preferences():
            return False
        
        # Step 3: Create initial directory structure
        if not self.create_directory_structure():
            return False
        
        # Step 4: Create personalized welcome files
        if not self.create_welcome_files():
            return False
        
        # Step 5: Validate installation
        if not self.validate_setup():
            return False
        
        # Step 6: Show next steps
        self.show_completion()
        
        return True
    
    def collect_user_info(self):
        """Collect basic user information"""
        print("📋 Step 1: User Information")
        print("-" * 50)
        
        if self.interactive:
            self.config['name'] = input("Your name: ").strip()
            self.config['role'] = input("Your role (e.g., developer, designer, manager): ").strip()
            self.config['primary_use'] = input("Primary use case (e.g., project management, code development): ").strip()
        else:
            # Non-interactive defaults
            self.config['name'] = self.config.get('name', 'User')
            self.config['role'] = self.config.get('role', 'Developer')
            self.config['primary_use'] = self.config.get('primary_use', 'General')
        
        print(f"✓ User: {self.config['name']}")
        print()
        return True
    
    def configure_preferences(self):
        """Configure system preferences"""
        print("⚙️  Step 2: Preferences")
        print("-" * 50)
        
        if self.interactive:
            # Persona preference
            print("\nChoose your default working persona:")
            print("1. Operator (General tasks, file management)")
            print("2. Builder (System implementation)")
            print("3. Strategist (Analysis and planning)")
            choice = input("Choice [1]: ").strip() or "1"
            
            persona_map = {"1": "operator", "2": "builder", "3": "strategist"}
            self.config['default_persona'] = persona_map.get(choice, "operator")
            
            # Workflow preferences
            self.config['use_state_management'] = self._ask_yes_no(
                "Enable session state tracking?", default=True
            )
            self.config['auto_timestamps'] = self._ask_yes_no(
                "Add timestamps to responses?", default=True
            )
        else:
            self.config['default_persona'] = "operator"
            self.config['use_state_management'] = True
            self.config['auto_timestamps'] = True
        
        print(f"✓ Default persona: {self.config['default_persona']}")
        print()
        return True
    
    def create_directory_structure(self):
        """Create initial directory structure"""
        print("📁 Step 3: Directory Structure")
        print("-" * 50)
        
        directories = [
            "Prompts",
            "Documents",
            "Lists",
            "Knowledge",
            "Inbox",
            "Archive",
            "Images"
        ]
        
        for dir_name in directories:
            dir_path = self.workspace / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Created: {dir_name}/")
            else:
                print(f"  ⟳ Exists: {dir_name}/")
        
        print()
        return True
    
    def create_welcome_files(self):
        """Create personalized welcome and starter files"""
        print("📝 Step 4: Welcome Files")
        print("-" * 50)
        
        # Create welcome document
        welcome_path = self.workspace / "Documents" / "WELCOME.md"
        welcome_content = f"""# Welcome to N5OS Lite, {self.config['name']}!

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Role:** {self.config['role']}  
**Primary Use:** {self.config['primary_use']}

---

## Quick Start

### 1. Your First Workflow

Try this: Create a new prompt by asking your AI:
```
Load planning_prompt.md and help me plan a project
```

### 2. Explore Personas

Your default persona is **{self.config['default_persona'].title()}**.

Try switching:
```
Switch to Builder persona
```

### 3. Manage Knowledge

Add structured knowledge:
```
Run knowledge-ingest.md with this information: [your content]
```

---

## Your Preferences

- **Default Persona:** {self.config['default_persona']}
- **State Management:** {'Enabled' if self.config['use_state_management'] else 'Disabled'}
- **Auto Timestamps:** {'Enabled' if self.config['auto_timestamps'] else 'Disabled'}

---

## Next Steps

1. ✅ Read: `README.md` - System overview
2. ✅ Review: `QUICKSTART.md` - 15-minute guide
3. ✅ Explore: `principles/` - Architectural principles
4. ✅ Try: Run your first prompt

---

**Need help?** Check `ARCHITECTURE.md` or `system/` directory for detailed documentation.
"""
        
        welcome_path.write_text(welcome_content)
        print(f"  ✓ Created: {welcome_path}")
        
        # Create starter list
        tools_list_path = self.workspace / "Lists" / "tools.jsonl"
        if not tools_list_path.exists():
            starter_tools = [
                {
                    "name": "Planning Prompt",
                    "slug": "planning-prompt",
                    "type": "prompt",
                    "description": "Think→Plan→Execute framework",
                    "tags": ["planning", "architecture"],
                    "location": "Prompts/planning_prompt.md",
                    "created": datetime.now().strftime('%Y-%m-%d')
                }
            ]
            with open(tools_list_path, 'w') as f:
                for tool in starter_tools:
                    f.write(json.dumps(tool) + '\n')
            print(f"  ✓ Created: {tools_list_path}")
        
        print()
        return True
    
    def validate_setup(self):
        """Validate installation completeness"""
        print("✅ Step 5: Validation")
        print("-" * 50)
        
        checks = [
            ("Workspace exists", self.workspace.exists()),
            ("Prompts directory", (self.workspace / "Prompts").exists()),
            ("Lists directory", (self.workspace / "Lists").exists()),
            ("Welcome document", (self.workspace / "Documents" / "WELCOME.md").exists()),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        print()
        return all_passed
    
    def show_completion(self):
        """Show completion message and next steps"""
        print("🎉 Onboarding Complete!")
        print("=" * 50)
        print()
        print(f"Welcome aboard, {self.config['name']}!")
        print()
        print("📚 Your personalized workspace is ready.")
        print()
        print("Next steps:")
        print("  1. Open: Documents/WELCOME.md")
        print("  2. Read: README.md and QUICKSTART.md")
        print("  3. Try your first workflow!")
        print()
        print("🚀 Happy building!")
    
    def _ask_yes_no(self, question, default=True):
        """Ask yes/no question"""
        default_str = "[Y/n]" if default else "[y/N]"
        response = input(f"{question} {default_str}: ").strip().lower()
        
        if not response:
            return default
        return response in ['y', 'yes']


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="N5OS Lite Onboarding Wizard")
    parser.add_argument('--workspace', default='/home/workspace',
                       help='Workspace directory (default: /home/workspace)')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Run without prompts (use defaults)')
    parser.add_argument('--name', help='User name (for non-interactive mode)')
    parser.add_argument('--role', help='User role (for non-interactive mode)')
    
    args = parser.parse_args()
    
    wizard = OnboardingWizard(
        workspace_root=args.workspace,
        interactive=not args.non_interactive
    )
    
    if args.name:
        wizard.config['name'] = args.name
    if args.role:
        wizard.config['role'] = args.role
    
    success = wizard.run()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
