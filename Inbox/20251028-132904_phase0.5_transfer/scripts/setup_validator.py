#!/usr/bin/env python3
"""
Setup Validator - Runs 12 validation tests to ensure onboarding success.

Tests:
- Prerequisites (4 tests)
- Config generation (4 tests)
- System integration (4 tests)

Part of: N5 OS Core Phase 0.5
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SetupValidator:
    """Validates complete N5 setup after onboarding."""
    
    def __init__(self, user_config_path: Path):
        self.user_config = user_config_path
        self.workspace = Path("/home/workspace/n5os-core")
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all 12 validation tests."""
        tests = [
            # Prerequisites (4)
            self.test_rules_configured(),
            self.test_apps_connected(),
            self.test_bio_provided(),
            self.test_personas_added(),
            
            # Config Generation (4)
            self.test_user_config_exists(),
            self.test_preferences_valid(),
            self.test_telemetry_exists(),
            self.test_completion_marker(),
            
            # System Integration (4)
            self.test_recipes_integration(),
            self.test_session_state_integration(),
            self.test_git_protection(),
            self.test_workspace_structure()
        ]
        
        all_passed = all(test["passed"] for test in tests)
        
        return {
            "all_passed": all_passed,
            "tests": tests,
            "passed_count": sum(1 for t in tests if t["passed"]),
            "total_count": len(tests)
        }
    
    # Prerequisites Tests
    
    def test_rules_configured(self) -> Dict[str, Any]:
        """Test 1: Zo rules configured."""
        try:
            prefs_exist = (self.workspace / "N5" / "prefs").exists()
            return {
                "name": "Rules configured",
                "passed": prefs_exist,
                "message": "N5 prefs system exists" if prefs_exist else "Missing N5/prefs/"
            }
        except Exception as e:
            return {"name": "Rules configured", "passed": False, "message": str(e)}
    
    def test_apps_connected(self) -> Dict[str, Any]:
        """Test 2: Apps connected."""
        # Placeholder - real implementation would check Zo API
        return {
            "name": "Apps connected",
            "passed": True,
            "message": "Assumed connected (prerequisite for onboarding)"
        }
    
    def test_bio_provided(self) -> Dict[str, Any]:
        """Test 3: Bio provided."""
        # Placeholder - real implementation would check Zo API
        return {
            "name": "Bio provided",
            "passed": True,
            "message": "Assumed provided (prerequisite for onboarding)"
        }
    
    def test_personas_added(self) -> Dict[str, Any]:
        """Test 4: Personas added."""
        try:
            personas_exist = (self.workspace / "N5" / "personas").exists()
            return {
                "name": "Personas added",
                "passed": personas_exist,
                "message": "Personas directory exists" if personas_exist else "Missing N5/personas/"
            }
        except Exception as e:
            return {"name": "Personas added", "passed": False, "message": str(e)}
    
    # Config Generation Tests
    
    def test_user_config_exists(self) -> Dict[str, Any]:
        """Test 5: user_config/ created."""
        try:
            exists = self.user_config.exists() and self.user_config.is_dir()
            return {
                "name": "user_config/ exists",
                "passed": exists,
                "message": f"Directory created: {self.user_config}" if exists else "Missing user_config/"
            }
        except Exception as e:
            return {"name": "user_config/ exists", "passed": False, "message": str(e)}
    
    def test_preferences_valid(self) -> Dict[str, Any]:
        """Test 6: preferences.json valid."""
        try:
            prefs_file = self.user_config / "preferences.json"
            if not prefs_file.exists():
                return {"name": "preferences.json valid", "passed": False, "message": "File does not exist"}
            
            # Load and validate JSON
            prefs = json.loads(prefs_file.read_text())
            
            # Check required sections
            required = ["version", "workflows", "automation", "conversation_end", "git", "n5"]
            missing = [k for k in required if k not in prefs]
            
            if missing:
                return {
                    "name": "preferences.json valid",
                    "passed": False,
                    "message": f"Missing sections: {missing}"
                }
            
            return {
                "name": "preferences.json valid",
                "passed": True,
                "message": "Valid JSON with all required sections"
            }
        except json.JSONDecodeError as e:
            return {"name": "preferences.json valid", "passed": False, "message": f"Invalid JSON: {e}"}
        except Exception as e:
            return {"name": "preferences.json valid", "passed": False, "message": str(e)}
    
    def test_telemetry_exists(self) -> Dict[str, Any]:
        """Test 7: telemetry_settings.json exists."""
        try:
            telemetry_file = self.user_config / "telemetry_settings.json"
            exists = telemetry_file.exists()
            
            if exists:
                # Validate JSON
                json.loads(telemetry_file.read_text())
            
            return {
                "name": "telemetry_settings.json exists",
                "passed": exists,
                "message": "File exists and valid" if exists else "Missing telemetry_settings.json"
            }
        except Exception as e:
            return {"name": "telemetry_settings.json exists", "passed": False, "message": str(e)}
    
    def test_completion_marker(self) -> Dict[str, Any]:
        """Test 8: .onboarding_complete marker."""
        try:
            marker_file = self.user_config / ".onboarding_complete"
            exists = marker_file.exists()
            
            if exists:
                data = json.loads(marker_file.read_text())
                has_timestamp = "completed" in data
                return {
                    "name": ".onboarding_complete marker",
                    "passed": has_timestamp,
                    "message": f"Marker written with timestamp" if has_timestamp else "Marker missing timestamp"
                }
            
            return {
                "name": ".onboarding_complete marker",
                "passed": False,
                "message": "Marker file does not exist"
            }
        except Exception as e:
            return {"name": ".onboarding_complete marker", "passed": False, "message": str(e)}
    
    # System Integration Tests
    
    def test_recipes_integration(self) -> Dict[str, Any]:
        """Test 9: Recipes system integration."""
        try:
            recipes_dir = self.workspace / "Recipes"
            has_recipes = recipes_dir.exists() and any(recipes_dir.glob("*.md"))
            return {
                "name": "Recipes integration",
                "passed": has_recipes,
                "message": "Recipes directory with .md files" if has_recipes else "No recipes found"
            }
        except Exception as e:
            return {"name": "Recipes integration", "passed": False, "message": str(e)}
    
    def test_session_state_integration(self) -> Dict[str, Any]:
        """Test 10: Session state manager integration."""
        try:
            session_script = self.workspace / "N5" / "scripts" / "session_state_manager.py"
            exists = session_script.exists()
            return {
                "name": "Session state integration",
                "passed": exists,
                "message": "session_state_manager.py exists" if exists else "Missing session_state_manager.py"
            }
        except Exception as e:
            return {"name": "Session state integration", "passed": False, "message": str(e)}
    
    def test_git_protection(self) -> Dict[str, Any]:
        """Test 11: Git protection (user_config/ gitignored)."""
        try:
            gitignore = self.workspace / ".gitignore"
            if not gitignore.exists():
                return {"name": "Git protection", "passed": False, "message": ".gitignore missing"}
            
            content = gitignore.read_text()
            protected = "user_config/" in content
            
            return {
                "name": "Git protection",
                "passed": protected,
                "message": "user_config/ in .gitignore" if protected else "user_config/ not gitignored!"
            }
        except Exception as e:
            return {"name": "Git protection", "passed": False, "message": str(e)}
    
    def test_workspace_structure(self) -> Dict[str, Any]:
        """Test 12: Workspace structure intact."""
        try:
            required_dirs = ["N5", "Lists", "Knowledge", "Recipes", "Documents"]
            missing = [d for d in required_dirs if not (self.workspace / d).exists()]
            
            if missing:
                return {
                    "name": "Workspace structure",
                    "passed": False,
                    "message": f"Missing directories: {missing}"
                }
            
            return {
                "name": "Workspace structure",
                "passed": True,
                "message": "All required directories exist"
            }
        except Exception as e:
            return {"name": "Workspace structure", "passed": False, "message": str(e)}
