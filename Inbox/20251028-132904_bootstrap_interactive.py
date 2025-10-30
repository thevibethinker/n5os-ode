#!/usr/bin/env python3
"""
N5 OS Core - Interactive Onboarding
Personalizes N5 OS during first run

Principles: P1 (Human-Readable), P7 (Dry-Run), P15 (Complete), P19 (Error Handling)
"""

import argparse
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
N5_ROOT = WORKSPACE_ROOT / "N5"
CONFIG_FILE = N5_ROOT / "config" / "user_config.json"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_section(text: str):
    """Print formatted section"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def check_prerequisites() -> bool:
    """Verify all prerequisites are met"""
    print_section("Step 1/5: Checking Prerequisites")
    
    all_good = True
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 8):
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} installed")
    else:
        print_error(f"Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        all_good = False
    
    # Check Git
    if shutil.which("git"):
        print_success("Git installed")
    else:
        print_error("Git not found - install with: apt update && apt install -y git")
        all_good = False
    
    # Check workspace
    if WORKSPACE_ROOT.exists():
        print_success(f"Workspace found: {WORKSPACE_ROOT}")
    else:
        print_error(f"Workspace not found: {WORKSPACE_ROOT}")
        all_good = False
    
    return all_good


def gather_user_info(non_interactive: bool = False) -> Dict[str, str]:
    """Collect user preferences"""
    print("\nLet's personalize N5 OS for you.\n")
    
    if non_interactive:
        return {
            "name": "[YOUR_NAME]",
            "email": "[YOUR_EMAIL]",
            "timezone": "America/New_York",
            "company": "[YOUR_COMPANY]"
        }
    
    name = input(f"{Colors.BOLD}Your name{Colors.END} (e.g., 'Alex'): ").strip()
    email = input(f"{Colors.BOLD}Your email{Colors.END} (e.g., 'alex@example.com'): ").strip()
    timezone = input(f"{Colors.BOLD}Timezone{Colors.END} (e.g., 'America/New_York'): ").strip()
    company = input(f"\n{Colors.BOLD}Company/Organization{Colors.END} (optional, press Enter to skip): ").strip()
    
    return {
        "name": name,
        "email": email,
        "timezone": timezone,
        "company": company
    }


def setup_directories(dry_run: bool = False) -> bool:
    """Create essential directory structure"""
    print_section("Step 3/5: Setting up directories")
    
    dirs = [
        N5_ROOT / "config",
        N5_ROOT / "data",
        N5_ROOT / "templates" / "session_state",
        N5_ROOT / ".state",
        WORKSPACE_ROOT / "Lists",
        WORKSPACE_ROOT / "Knowledge",
        WORKSPACE_ROOT / "Documents",
        WORKSPACE_ROOT / "Records"
    ]
    
    try:
        for dir_path in dirs:
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {dir_path}")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"Created: {dir_path.relative_to(WORKSPACE_ROOT)}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create directories: {e}")
        return False


def initialize_templates(dry_run: bool = False) -> bool:
    """Initialize list templates"""
    print_section("Step 4/5: Initializing templates")
    
    templates = {
        "Lists/ideas.jsonl": {
            "tag": "ideas",
            "title": "",
            "description": "",
            "date_added": ""
        },
        "Lists/must-contact.jsonl": {
            "tag": "must-contact",
            "name": "",
            "email": "",
            "priority": ""
        }
    }
    
    try:
        for filename, template in templates.items():
            filepath = WORKSPACE_ROOT / filename
            if dry_run:
                logger.info(f"[DRY RUN] Would create template: {filepath}")
            else:
                if not filepath.exists():
                    filepath.write_text(json.dumps(template) + "\n")
                    print_success(f"Created template: {filename}")
                else:
                    print_warning(f"Already exists: {filename}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to initialize templates: {e}")
        return False


def save_config(config: Dict[str, str], dry_run: bool = False) -> bool:
    """Save user configuration"""
    print_section("Step 5/5: Saving configuration")
    
    try:
        if dry_run:
            logger.info(f"[DRY RUN] Would save config to: {CONFIG_FILE}")
            logger.info(f"[DRY RUN] Config: {json.dumps(config, indent=2)}")
        else:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")
            print_success(f"Configuration saved to: {CONFIG_FILE.relative_to(WORKSPACE_ROOT)}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        return False


def print_next_steps(config: Dict[str, str]):
    """Print next steps after successful setup"""
    print_header("Setup Complete!")
    
    print(f"\n{Colors.GREEN}Welcome to N5 OS, {config.get('name', 'User')}!{Colors.END}\n")
    
    print("📚 Next steps:\n")
    print(f"  1. {Colors.BOLD}Read the docs{Colors.END}")
    print("     → file 'Documents/N5.md' (system overview)")
    print("     → file 'Documents/System/FIRST_RUN_CHECKLIST.md' (verification)")
    print()
    print(f"  2. {Colors.BOLD}Test a script{Colors.END}")
    print("     → python3 N5/scripts/n5_git_check.py")
    print()
    print(f"  3. {Colors.BOLD}Try a command{Colors.END}")
    print("     → Tell Zo: 'Load Vibe Builder persona'")
    print("     → Tell Zo: 'Show me my N5 system'")
    print()
    print(f"  4. {Colors.BOLD}Customize{Colors.END}")
    print("     → Edit file 'N5/prefs/prefs.md'")
    print("     → Add your own principles to 'Knowledge/architectural/principles/'")
    print()
    
    print(f"{Colors.CYAN}{'─' * 60}{Colors.END}")
    print(f"{Colors.BOLD}Need help?{Colors.END}")
    print("  • file 'Documents/System/ONBOARDING_DESIGN.md'")
    print("  • file 'Knowledge/architectural/planning_prompt.md'")
    print("  • GitHub: https://github.com/vrijenattawar/n5os-core")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.END}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="N5 OS Core Interactive Setup")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--non-interactive", action="store_true", help="Use default placeholder values")
    parser.add_argument("--name", help="Your name (for non-interactive mode)")
    parser.add_argument("--email", help="Your email (for non-interactive mode)")
    parser.add_argument("--timezone", default="America/New_York", help="Your timezone")
    parser.add_argument("--company", help="Your company/organization (optional)")
    args = parser.parse_args()
    
    dry_run = args.dry_run
    non_interactive = args.non_interactive
    
    try:
        # Welcome
        print_header("N5 OS Core - Interactive Setup")
        print(f"\n{Colors.BOLD}Personal operating system for AI-assisted productivity{Colors.END}\n")
        
        if args.dry_run:
            print_warning("DRY RUN MODE - No changes will be made\n")
        
        # Step 1: Prerequisites
        if not check_prerequisites():
            print_error("\nPrerequisites not met. Please resolve issues and try again.")
            return 1
        
        # Step 2: User info
        print_section("Step 2/5: User Configuration")
        
        if non_interactive:
            config = gather_user_info(non_interactive=True)
        else:
            config = gather_user_info(non_interactive=False)
        
        # Step 3: Directories
        if not setup_directories(dry_run=args.dry_run):
            return 1
        
        # Step 4: Templates
        if not initialize_templates(dry_run=args.dry_run):
            return 1
        
        # Step 5: Save config
        if not save_config(config, dry_run=args.dry_run):
            return 1
        
        # Done!
        if not args.dry_run:
            print_next_steps(config)
        else:
            print_warning("\nDRY RUN complete - run without --dry-run to apply changes")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.exception("Setup failed")
        return 1


if __name__ == "__main__":
    exit(main())
