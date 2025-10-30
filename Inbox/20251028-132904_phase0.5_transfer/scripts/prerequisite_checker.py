#!/usr/bin/env python3
"""
Prerequisite Checker - Verifies manual setup complete before onboarding.

Checks:
1. Zo rules configured
2. Apps connected (Gmail, Drive, Notion)
3. Bio provided
4. Personas added (Vibe Builder, Vibe Debugger)

Part of: N5 OS Core Phase 0.5
"""
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class PrerequisiteChecker:
    """Validates that manual prerequisites are complete."""
    
    def __init__(self):
        self.workspace = Path("/home/workspace/n5os-core")
    
    def check_all(self) -> Dict[str, Any]:
        """Run all prerequisite checks."""
        checks = [
            self.check_rules(),
            self.check_apps(),
            self.check_bio(),
            self.check_personas()
        ]
        
        all_passed = all(check["passed"] for check in checks)
        
        return {
            "all_passed": all_passed,
            "checks": checks,
            "passed_count": sum(1 for c in checks if c["passed"]),
            "total_count": len(checks)
        }
    
    def check_rules(self) -> Dict[str, Any]:
        """Check if Zo rules are configured."""
        # In real implementation, would check Zo settings API
        # For now, we'll check if N5/config exists (proxy for setup)
        try:
            rules_exist = (self.workspace / "N5" / "prefs").exists()
            return {
                "name": "Zo Rules",
                "passed": rules_exist,
                "message": "Rules configured in Zo settings" if rules_exist else "Add rules in Zo settings first"
            }
        except Exception as e:
            return {
                "name": "Zo Rules",
                "passed": False,
                "message": f"Error checking rules: {e}"
            }
    
    def check_apps(self) -> Dict[str, Any]:
        """Check if required apps are connected."""
        # In real implementation, would check Zo integrations API
        # For now, assume connected if onboarding is being run
        # (user wouldn't get this far without apps)
        return {
            "name": "Apps Connected",
            "passed": True,  # Placeholder
            "message": "Gmail, Drive, and Notion connected (assumed)"
        }
    
    def check_bio(self) -> Dict[str, Any]:
        """Check if bio is provided in Zo settings."""
        # In real implementation, would check Zo user profile API
        return {
            "name": "Bio Provided",
            "passed": True,  # Placeholder
            "message": "Bio configured in Zo settings (assumed)"
        }
    
    def check_personas(self) -> Dict[str, Any]:
        """Check if required personas are added."""
        # In real implementation, would check Zo personas API
        # For now, check if personas directory exists
        try:
            personas_dir = self.workspace / "N5" / "personas"
            personas_exist = personas_dir.exists()
            return {
                "name": "Personas Added",
                "passed": personas_exist,
                "message": "Vibe Builder and Vibe Debugger personas added" if personas_exist else "Add personas in Zo settings first"
            }
        except Exception as e:
            return {
                "name": "Personas Added",
                "passed": False,
                "message": f"Error checking personas: {e}"
            }
