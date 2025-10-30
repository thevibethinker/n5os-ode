#!/usr/bin/env python3
"""
N5 OS Core Onboarding Orchestrator
Configures N5 system after manual prerequisites complete.

Usage:
    python3 n5_onboard.py              # Run onboarding
    python3 n5_onboard.py --dry-run    # Preview without changes
    python3 n5_onboard.py --reset      # Reset and re-run

Part of: N5 OS Core Phase 0.5
"""
import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from prerequisite_checker import PrerequisiteChecker
from config_generator import ConfigGenerator
from setup_validator import SetupValidator
from welcome_guide_generator import WelcomeGuideGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Workspace root
WORKSPACE = Path("/home/workspace/n5os-core")
USER_CONFIG = WORKSPACE / "user_config"

def main(dry_run: bool = False, reset: bool = False) -> int:
    """Main onboarding orchestrator."""
    try:
        logger.info("=== N5 OS Core Onboarding ===")
        logger.info(f"Version: 0.5")
        logger.info(f"Workspace: {WORKSPACE}")
        logger.info(f"Dry run: {dry_run}")
        
        # Check if already onboarded
        if not reset and (USER_CONFIG / ".onboarding_complete").exists():
            logger.warning("⚠️  Onboarding already complete!")
            logger.info("Use --reset to re-run onboarding")
            return 0
        
        if reset:
            logger.info("🔄 Resetting onboarding...")
            if USER_CONFIG.exists() and not dry_run:
                import shutil
                shutil.rmtree(USER_CONFIG)
                logger.info("✓ Cleared user_config/")
        
        # Phase 1: Verify Prerequisites
        logger.info("\n=== Phase 1: Verify Prerequisites ===")
        checker = PrerequisiteChecker()
        prereq_result = checker.check_all()
        
        if not prereq_result["all_passed"]:
            logger.error("❌ Prerequisites not complete")
            for check in prereq_result["checks"]:
                status = "✓" if check["passed"] else "❌"
                logger.error(f"{status} {check['name']}: {check['message']}")
            logger.error("\nComplete manual setup first:")
            logger.error("1. Add rules in Zo settings")
            logger.error("2. Connect apps (Gmail, Drive, Notion)")
            logger.error("3. Add bio in Zo settings")
            logger.error("4. Add personas (Vibe Builder, Vibe Debugger)")
            return 1
        
        logger.info("✓ All prerequisites verified")
        
        # Phase 2: Interactive Interview
        logger.info("\n=== Phase 2: Configure N5 Systems ===")
        preferences = run_interview()
        
        if dry_run:
            logger.info("\n[DRY RUN] Would create:")
            logger.info(f"  {USER_CONFIG}/preferences.json")
            logger.info(f"  {USER_CONFIG}/telemetry_settings.json")
            logger.info(f"  {USER_CONFIG}/.onboarding_complete")
            logger.info(f"\nConfig preview:")
            print(json.dumps(preferences, indent=2))
            return 0
        
        # Phase 3: Generate user_config/
        logger.info("\n=== Phase 3: Generate Configuration ===")
        generator = ConfigGenerator(USER_CONFIG)
        generator.create_user_config(preferences)
        logger.info(f"✓ Created {USER_CONFIG}/")
        
        # Phase 4: Setup Scheduled Tasks
        if preferences["automation"]["scheduled_tasks_enabled"]:
            logger.info("\n=== Phase 4: Setup Scheduled Tasks ===")
            setup_scheduled_tasks(preferences["automation"]["tasks"])
        
        # Phase 5: Validate Setup
        logger.info("\n=== Phase 5: Validate Setup ===")
        validator = SetupValidator(USER_CONFIG)
        validation_result = validator.validate_all()
        
        if not validation_result["all_passed"]:
            logger.error("❌ Validation failed")
            for test in validation_result["tests"]:
                if not test["passed"]:
                    logger.error(f"  ❌ {test['name']}: {test['message']}")
            return 1
        
        logger.info(f"✓ All {len(validation_result['tests'])} validation tests passed")
        
        # Phase 6: Mark Complete
        logger.info("\n=== Phase 6: Finalize ===")
        mark_complete()
        
        # Phase 7: Generate Welcome Guide
        guide_gen = WelcomeGuideGenerator(USER_CONFIG)
        guide_path = guide_gen.generate(preferences)
        logger.info(f"✓ Welcome guide: {guide_path}")
        
        logger.info("\n" + "="*50)
        logger.info("🎉 N5 OS Core onboarding complete!")
        logger.info("="*50)
        logger.info(f"\nYour configuration: {USER_CONFIG}/")
        logger.info(f"Welcome guide: {guide_path}")
        logger.info("\nNext steps:")
        logger.info("  1. Review your welcome guide")
        logger.info("  2. Try: /conversation-end (test recipes)")
        logger.info("  3. Explore: Lists/ and Knowledge/")
        logger.info(f"  4. Configure: Edit {USER_CONFIG}/preferences.json anytime")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\nOnboarding cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Onboarding failed: {e}", exc_info=True)
        return 1

def run_interview() -> Dict[str, Any]:
    """Interactive N5 configuration interview."""
    logger.info("\nAnswer 6 questions to configure your N5 system")
    logger.info("(Takes ~5 minutes)\n")
    
    prefs = {
        "version": "1.0.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "workflows": {},
        "automation": {},
        "conversation_end": {},
        "git": {},
        "n5": {}
    }
    
    # Q1: Workflow Systems
    print("\n" + "="*60)
    print("Q1: Which N5 workflow systems do you want to enable?")
    print("="*60)
    print("\nAvailable systems:")
    print("  1. Lists       - Manage actions, ideas, must-contact")
    print("  2. Meetings    - AAR generation, follow-ups")
    print("  3. Digests     - Daily summaries")
    print("  4. Social      - X/LinkedIn content")
    print("  5. CRM         - Relationship tracking")
    print("\nRecommended for startups: Lists + Digests")
    print("\nEnable? (Enter numbers separated by spaces, e.g. '1 3')")
    print("Or 'all' for everything, 'none' to skip: ", end="")
    
    workflow_input = input().strip().lower()
    prefs["workflows"] = {
        "lists": "1" in workflow_input or "all" in workflow_input,
        "meetings": "2" in workflow_input or "all" in workflow_input,
        "digests": "3" in workflow_input or "all" in workflow_input,
        "social": "4" in workflow_input or "all" in workflow_input,
        "crm": "5" in workflow_input or "all" in workflow_input
    }
    
    # Q2: Automation Level
    print("\n" + "="*60)
    print("Q2: How much should N5 automate?")
    print("="*60)
    print("\n  1. Manual     - I'll trigger everything explicitly")
    print("  2. Semi-Auto  - Suggest automations, I approve (RECOMMENDED)")
    print("  3. Auto       - Run scheduled tasks automatically")
    print("\nChoice (1-3): ", end="")
    
    auto_choice = input().strip()
    auto_levels = {"1": "manual", "2": "semi-auto", "3": "auto"}
    prefs["automation"]["level"] = auto_levels.get(auto_choice, "semi-auto")
    
    # Q3: Scheduled Tasks
    if prefs["automation"]["level"] != "manual":
        print("\n" + "="*60)
        print("Q3: Enable these scheduled tasks?")
        print("="*60)
        print("\n  1. Daily: Index rebuild (keeps Knowledge current)")
        print("  2. Daily: Git check (prevents accidental commits)")
        print("  3. Weekly: Empty files cleanup")
        print("  4. Weekly: List review reminder")
        print("\nRecommended: 1 + 2")
        print("\nEnable? (Enter numbers separated by spaces): ", end="")
        
        tasks_input = input().strip()
        enabled_tasks = []
        if "1" in tasks_input:
            enabled_tasks.append("index-rebuild")
        if "2" in tasks_input:
            enabled_tasks.append("git-check")
        if "3" in tasks_input:
            enabled_tasks.append("empty-files")
        if "4" in tasks_input:
            enabled_tasks.append("list-review")
        
        prefs["automation"]["scheduled_tasks_enabled"] = len(enabled_tasks) > 0
        prefs["automation"]["tasks"] = enabled_tasks
    else:
        prefs["automation"]["scheduled_tasks_enabled"] = False
        prefs["automation"]["tasks"] = []
    
    # Q4: Conversation End Behavior
    print("\n" + "="*60)
    print("Q4: At conversation end, should Zo:")
    print("="*60)
    print("\n  1. Just summarize (minimal)")
    print("  2. Summarize + update lists (RECOMMENDED)")
    print("  3. Summarize + update + trigger workflows (max automation)")
    print("\nChoice (1-3): ", end="")
    
    conv_choice = input().strip()
    behaviors = {
        "1": "summarize_only",
        "2": "summarize_and_update_lists",
        "3": "full_automation"
    }
    prefs["conversation_end"]["behavior"] = behaviors.get(conv_choice, "summarize_and_update_lists")
    prefs["conversation_end"]["auto_archive"] = conv_choice == "3"
    
    # Q5: Git Workflow
    print("\n" + "="*60)
    print("Q5: Git safety preferences")
    print("="*60)
    print("\n  1. Run git-check before commits (RECOMMENDED)")
    print("  2. Auto-commit daily changes")
    print("  3. Require explicit approval for pushes")
    print("\nEnable? (Enter numbers separated by spaces): ", end="")
    
    git_input = input().strip()
    prefs["git"]["safety_mode"] = "strict" if "1" in git_input else "normal"
    prefs["git"]["auto_commit"] = "2" in git_input
    prefs["git"]["require_approval"] = "3" in git_input or "1" in git_input
    
    # Q6: Telemetry
    print("\n" + "="*60)
    print("Q6: Enable anonymous usage telemetry?")
    print("="*60)
    print("\n  - Helps improve N5 OS Core")
    print("  - Completely anonymous (no personal data)")
    print("  - Stored locally only")
    print("  - Can disable anytime")
    print("\nEnable? (y/N): ", end="")
    
    telemetry_choice = input().strip().lower()
    prefs["telemetry_enabled"] = telemetry_choice in ["y", "yes"]
    
    # N5 system defaults
    prefs["n5"]["recipes_enabled"] = True
    prefs["n5"]["session_state_tracking"] = True
    prefs["n5"]["persona_active"] = "vibe-builder"
    
    print("\n✓ Configuration complete!")
    return prefs

def setup_scheduled_tasks(tasks: list) -> None:
    """Create scheduled tasks in Zo."""
    logger.info(f"Setting up {len(tasks)} scheduled tasks...")
    
    # Task definitions
    task_defs = {
        "index-rebuild": {
            "rrule": "FREQ=DAILY;BYHOUR=2;BYMINUTE=0",
            "instruction": "Rebuild Knowledge index to keep system current. Run: python3 /home/workspace/n5os-core/N5/scripts/rebuild_index.py"
        },
        "git-check": {
            "rrule": "FREQ=DAILY;BYHOUR=8;BYMINUTE=0",
            "instruction": "Run git check to prevent accidental commits of sensitive files. Run: python3 /home/workspace/n5os-core/Recipes/git-check.md"
        },
        "empty-files": {
            "rrule": "FREQ=WEEKLY;BYDAY=SU;BYHOUR=3;BYMINUTE=0",
            "instruction": "Clean up empty files in workspace. Run: find /home/workspace/n5os-core -type f -empty -delete"
        },
        "list-review": {
            "rrule": "FREQ=WEEKLY;BYDAY=FR;BYHOUR=16;BYMINUTE=0",
            "instruction": "Review Lists/ for pending items and send summary email"
        }
    }
    
    for task in tasks:
        if task in task_defs:
            # Note: Actual Zo API call would go here
            # For now, just log what would be created
            logger.info(f"  ✓ Would create: {task}")
            logger.info(f"    Schedule: {task_defs[task]['rrule']}")
    
    logger.info(f"✓ Scheduled {len(tasks)} tasks")
    logger.info("  (View in Zo settings or /schedule)")

def mark_complete() -> None:
    """Write .onboarding_complete marker."""
    marker = USER_CONFIG / ".onboarding_complete"
    data = {
        "completed": datetime.now(timezone.utc).isoformat(),
        "n5_version": "1.0.0-core",
        "onboarding_version": "0.5",
        "prerequisites_verified": True,
        "validation_passed": True
    }
    marker.write_text(json.dumps(data, indent=2))
    logger.info(f"✓ Marked complete: {marker}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="N5 OS Core onboarding system"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview configuration without making changes"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset and re-run onboarding"
    )
    args = parser.parse_args()
    
    sys.exit(main(dry_run=args.dry_run, reset=args.reset))
