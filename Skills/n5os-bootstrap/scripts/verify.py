#!/usr/bin/env python3
"""
N5OS Bootstrap Verifier

Health check script that verifies all expected files exist based on manifest,
validates file contents, and checks for placeholder markers that should have been replaced.
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any


class VerificationResult:
    """Track verification results."""
    
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
    
    def add_check(self, description: str, passed: bool, details: str = None):
        """Add a verification check result."""
        self.checks.append({
            'description': description,
            'passed': passed,
            'details': details
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_results(self, verbose: bool = False):
        """Print verification results."""
        print("N5OS Bootstrap Health Check")
        print("=" * 27)
        
        for check in self.checks:
            status = "✓" if check['passed'] else "✗"
            print(f"{status} {check['description']}")
            
            if verbose and check['details']:
                print(f"  → {check['details']}")
            elif not check['passed'] and check['details']:
                print(f"  → {check['details']}")
        
        print()
        print(f"Summary: {self.passed}/{self.passed + self.failed} checks passed")
        
        if self.failed == 0:
            print("Status: HEALTHY")
        else:
            print("Status: UNHEALTHY")
    
    def is_healthy(self) -> bool:
        """Return True if all checks passed."""
        return self.failed == 0


def load_manifest(skill_root: Path) -> Dict[str, Any]:
    """Load the installation manifest."""
    manifest_path = skill_root / "config" / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def check_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Check if a file exists and is readable."""
    if not file_path.exists():
        return False, "File does not exist"
    
    if not file_path.is_file():
        return False, "Path exists but is not a file"
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if len(content.strip()) == 0:
            return False, "File is empty"
        
        return True, f"File exists, {len(content)} characters"
    
    except Exception as e:
        return False, f"Cannot read file: {e}"


def check_for_placeholders(file_path: Path) -> Tuple[bool, str]:
    """Check file for unreplaced placeholder markers."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Common placeholder patterns
        placeholders = [
            '{{',
            '}}',
            '${',
            'WORKSPACE',
            'INSTANCE_NAME',
            'HANDLE',
            'OWNER_NAME'
        ]
        
        found_placeholders = []
        for placeholder in placeholders:
            if placeholder in content:
                found_placeholders.append(placeholder)
        
        if found_placeholders:
            return False, f"Found placeholders: {', '.join(found_placeholders)}"
        
        return True, "No placeholders found"
    
    except Exception as e:
        return False, f"Cannot check placeholders: {e}"


def verify_manifest_destinations(manifest: Dict[str, Any], workspace_root: Path, 
                                skill_root: Path, result: VerificationResult, 
                                verbose: bool = False) -> None:
    """Verify all files specified in manifest destinations exist."""
    
    for dest_name, config in manifest.get('destinations', {}).items():
        source_dir = skill_root / config['source']
        target_dir = workspace_root / config['target']
        
        # Check if source directory exists (sanity check)
        if not source_dir.exists():
            result.add_check(f"{dest_name} source directory exists", False, 
                           f"Missing: {source_dir}")
            continue
        
        # Check target directory exists
        target_exists = target_dir.exists()
        result.add_check(f"{dest_name} target directory exists", target_exists, 
                        str(target_dir) if not target_exists else None)
        
        if not target_exists:
            continue
        
        # Check each expected file
        for source_file in source_dir.glob('**/*.md'):
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            # File existence check
            exists, details = check_file_exists(target_file)
            result.add_check(f"{dest_name}/{rel_path} exists", exists, 
                           details if not exists or verbose else None)
            
            # Placeholder check (only if file exists)
            if exists:
                no_placeholders, placeholder_details = check_for_placeholders(target_file)
                if not no_placeholders:
                    result.add_check(f"{dest_name}/{rel_path} placeholders resolved", 
                                   False, placeholder_details)


def verify_required_directories(manifest: Dict[str, Any], workspace_root: Path, 
                               result: VerificationResult) -> None:
    """Verify all required directories exist."""
    
    for dir_path in manifest.get('required_dirs', []):
        target_dir = workspace_root / dir_path
        exists = target_dir.exists() and target_dir.is_dir()
        
        result.add_check(f"Required directory: {dir_path}", exists, 
                        None if exists else f"Missing: {target_dir}")


def verify_installation_log(workspace_root: Path, result: VerificationResult) -> None:
    """Check if installation was logged."""
    log_file = workspace_root / "N5" / "logs" / "n5os-bootstrap.log"
    
    if not log_file.exists():
        result.add_check("Installation logged", False, f"No log file: {log_file}")
        return
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            result.add_check("Installation logged", False, "Log file is empty")
        else:
            import json
            # Try to parse the last line as JSON
            try:
                last_entry = json.loads(lines[-1].strip())
                action = last_entry.get('action', 'unknown')
                result.add_check("Installation logged", True, 
                               f"Last action: {action}")
            except json.JSONDecodeError:
                result.add_check("Installation logged", True, 
                               f"Log exists with {len(lines)} entries")
    
    except Exception as e:
        result.add_check("Installation logged", False, f"Cannot read log: {e}")


def main() -> int:
    """Main verification function."""
    parser = argparse.ArgumentParser(
        description="N5OS Bootstrap Health Check - Verify installation integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 verify.py                    # Check installation health
  python3 verify.py --verbose          # Show all checks, not just failures
        """
    )
    
    parser.add_argument('--verbose', action='store_true',
                       help='Show all checks, not just failures')
    
    args = parser.parse_args()
    
    try:
        # Determine paths
        skill_root = Path(__file__).parent.parent
        workspace_root = Path.cwd()
        
        # Load manifest
        manifest = load_manifest(skill_root)
        
        # Create verification result tracker
        result = VerificationResult()
        
        # Run verification checks
        verify_required_directories(manifest, workspace_root, result)
        verify_manifest_destinations(manifest, workspace_root, skill_root, result, args.verbose)
        verify_installation_log(workspace_root, result)
        
        # Print results
        result.print_results(args.verbose)
        
        # Return appropriate exit code
        return 0 if result.is_healthy() else 1
        
    except Exception as e:
        print(f"Verification failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())