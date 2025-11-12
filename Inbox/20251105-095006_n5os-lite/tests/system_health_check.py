#!/usr/bin/env python3
"""
N5OS Lite System Health Check

Validates that all components are installed and working correctly.
Run after installation to verify setup.

Usage:
    python3 tests/system_health_check.py
    python3 tests/system_health_check.py --verbose
"""

import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict


class HealthCheck:
    def __init__(self, workspace_root: Path, verbose: bool = False):
        self.workspace = workspace_root
        self.verbose = verbose
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def log(self, msg: str, level: str = "INFO"):
        if self.verbose or level in ["ERROR", "WARN"]:
            prefix = {"INFO": "ℹ️", "PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
            print(f"{prefix.get(level, '•')} {msg}")
    
    def check(self, name: str, condition: bool, error_msg: str = "") -> bool:
        if condition:
            self.passed += 1
            self.log(f"{name}: PASS", "PASS")
            return True
        else:
            self.failed += 1
            self.log(f"{name}: FAIL - {error_msg}", "FAIL")
            return False
    
    def warn(self, name: str, msg: str):
        self.warnings += 1
        self.log(f"{name}: {msg}", "WARN")
    
    def check_directory_structure(self) -> bool:
        """Verify standard directory layout exists"""
        self.log("\n=== Checking Directory Structure ===", "INFO")
        
        required_dirs = [
            "Prompts",
            "Lists",
            "Knowledge",
            "Personal",
            "Inbox",
            "Documents"
        ]
        
        all_exist = True
        for dir_name in required_dirs:
            dir_path = self.workspace / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.check(f"Directory: {dir_name}", exists, f"{dir_path} not found")
            all_exist = all_exist and exists
        
        return all_exist
    
    def check_prompts(self) -> bool:
        """Verify essential prompts are installed"""
        self.log("\n=== Checking Prompts ===", "INFO")
        
        essential_prompts = [
            "planning_prompt.md",
            "thinking_prompt.md",
            "close-conversation.md",
            "add-to-list.md",
            "query-list.md"
        ]
        
        prompts_dir = self.workspace / "Prompts"
        all_exist = True
        
        for prompt in essential_prompts:
            prompt_path = prompts_dir / prompt
            exists = prompt_path.exists()
            self.check(f"Prompt: {prompt}", exists, f"{prompt_path} not found")
            all_exist = all_exist and exists
        
        return all_exist
    
    def check_scripts(self) -> bool:
        """Verify utility scripts are installed"""
        self.log("\n=== Checking Scripts ===", "INFO")
        
        scripts_dir = self.workspace / "scripts"
        if not scripts_dir.exists():
            self.warn("Scripts", "scripts/ directory not found (optional)")
            return True
        
        optional_scripts = [
            "file_guard.py",
            "validate_list.py"
        ]
        
        for script in optional_scripts:
            script_path = scripts_dir / script
            if script_path.exists():
                self.log(f"Script: {script} - installed", "PASS")
                # Check executable
                if not script_path.stat().st_mode & 0o111:
                    self.warn(script, "Not executable - run: chmod +x " + str(script_path))
            else:
                self.warn(script, "Not found (optional)")
        
        return True
    
    def check_lists(self) -> bool:
        """Verify list system is set up"""
        self.log("\n=== Checking List System ===", "INFO")
        
        lists_dir = self.workspace / "Lists"
        if not lists_dir.exists():
            self.check("Lists directory", False, "Lists/ not found")
            return False
        
        # Check for at least one .jsonl file
        jsonl_files = list(lists_dir.glob("*.jsonl"))
        has_lists = len(jsonl_files) > 0
        
        if has_lists:
            self.log(f"Found {len(jsonl_files)} JSONL lists", "PASS")
            
            # Validate JSONL format
            for jsonl_file in jsonl_files:
                try:
                    with open(jsonl_file) as f:
                        for line_num, line in enumerate(f, 1):
                            if line.strip():
                                json.loads(line)
                    self.log(f"  {jsonl_file.name}: Valid JSONL", "PASS")
                except json.JSONDecodeError as e:
                    self.warn(jsonl_file.name, f"Invalid JSON on line {line_num}: {e}")
                except Exception as e:
                    self.warn(jsonl_file.name, f"Error reading: {e}")
        else:
            self.warn("Lists", "No .jsonl files found - create your first list")
        
        return True
    
    def check_protection_system(self) -> bool:
        """Verify file protection system is working"""
        self.log("\n=== Checking Protection System ===", "INFO")
        
        # Check if file_guard.py exists
        file_guard = self.workspace / "scripts" / "file_guard.py"
        if not file_guard.exists():
            self.warn("file_guard.py", "Protection script not found (optional)")
            return True
        
        # Look for .protected files
        protected_files = list(self.workspace.rglob(".protected"))
        if protected_files:
            self.log(f"Found {len(protected_files)} protected directories", "PASS")
            for pf in protected_files[:3]:  # Show first 3
                try:
                    with open(pf) as f:
                        data = json.load(f)
                        reason = data.get('reason', 'No reason specified')
                        self.log(f"  {pf.parent.name}/: {reason}", "INFO")
                except:
                    self.warn(str(pf), "Invalid .protected file format")
        else:
            self.log("No protected directories found (optional)", "INFO")
        
        return True
    
    def check_knowledge_base(self) -> bool:
        """Verify knowledge base setup"""
        self.log("\n=== Checking Knowledge Base ===", "INFO")
        
        knowledge_dir = self.workspace / "Knowledge"
        if not knowledge_dir.exists():
            self.check("Knowledge directory", False, "Knowledge/ not found")
            return False
        
        # Check for organizational subdirectories
        expected_subdirs = ["architectural", "technical", "domain"]
        found_subdirs = [d.name for d in knowledge_dir.iterdir() if d.is_dir()]
        
        if found_subdirs:
            self.log(f"Found subdirectories: {', '.join(found_subdirs)}", "PASS")
        else:
            self.warn("Knowledge", "No subdirectories - create as needed")
        
        return True
    
    def run_all_checks(self) -> bool:
        """Run complete system health check"""
        print("🔍 N5OS Lite System Health Check")
        print("=" * 50)
        
        checks = [
            self.check_directory_structure(),
            self.check_prompts(),
            self.check_scripts(),
            self.check_lists(),
            self.check_protection_system(),
            self.check_knowledge_base()
        ]
        
        print("\n" + "=" * 50)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⚠️  Warnings: {self.warnings}")
        
        if self.failed == 0:
            print("\n🎉 System health check PASSED!")
            print("Your N5OS Lite installation is ready to use.")
            return True
        else:
            print(f"\n❌ System health check FAILED ({self.failed} failures)")
            print("Fix the issues above and re-run this test.")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="N5OS Lite System Health Check")
    parser.add_argument('--workspace', default='/home/workspace',
                       help='Workspace root directory (default: /home/workspace)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        return 1
    
    checker = HealthCheck(workspace, verbose=args.verbose)
    success = checker.run_all_checks()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
