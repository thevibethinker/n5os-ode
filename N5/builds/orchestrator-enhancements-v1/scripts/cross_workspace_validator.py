#!/usr/bin/env python3
"""
Cross-Workspace Validator
Reads worker FINAL_REPORT from worker workspace, validates against orchestrator RUBRIC

Usage:
    python3 cross_workspace_validator.py --worker con_WORKER_XXX --rubric /orch/workspace/WORKER_1_RUBRIC.md --output VALIDATION_RESULT.md
"""

import argparse
import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")
logger = logging.getLogger(__name__)

WORKSPACES_ROOT = Path("/home/.z/workspaces")


def find_worker_workspace(worker_id: str) -> Path:
    """Find worker conversation workspace"""
    workspace = WORKSPACES_ROOT / worker_id
    if not workspace.exists():
        raise FileNotFoundError(f"Worker workspace not found: {workspace}")
    return workspace


def parse_rubric(rubric_path: Path) -> Dict:
    """Parse rubric to extract expected deliverables and tests"""
    content = rubric_path.read_text()
    
    rubric = {
        "files": [],
        "behaviors": [],
        "tests": []
    }
    
    # Extract Files section
    files_section = re.search(r'### Files\n(.*?)###', content, re.DOTALL)
    if files_section:
        for line in files_section.group(1).strip().split('\n'):
            if line.startswith('- `'):
                match = re.match(r'- `(.+?)` - (.+)', line)
                if match:
                    rubric["files"].append({"path": match.group(1), "desc": match.group(2)})
    
    # Extract Test Commands
    tests_section = re.search(r'## Test Commands\n```bash\n(.*?)```', content, re.DOTALL)
    if tests_section:
        rubric["tests"] = [cmd.strip() for cmd in tests_section.group(1).strip().split('\n') if cmd.strip() and not cmd.startswith('#')]
    
    return rubric


def find_worker_report(worker_workspace: Path) -> Path:
    """Find FINAL_REPORT or WORKER_REPORT in worker workspace"""
    candidates = [
        worker_workspace / "FINAL_REPORT.md",
        worker_workspace / "WORKER_REPORT.md",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    # Search for any *REPORT*.md files
    report_files = list(worker_workspace.glob("*REPORT*.md"))
    if report_files:
        return report_files[0]
    
    raise FileNotFoundError(f"No report file found in {worker_workspace}")


def validate_files(rubric_files: List[Dict], worker_workspace: Path) -> Tuple[List[str], List[str]]:
    """Validate that expected files exist"""
    results = []
    missing = []
    
    for expected in rubric_files:
        file_path = Path(expected["path"])
        # Check both absolute path and filename in workspace
        if (worker_workspace / file_path.name).exists() or Path(expected["path"]).exists():
            results.append(f"✅ `{expected['path']}` - {expected['desc']}")
        else:
            results.append(f"❌ `{expected['path']}` - MISSING")
            missing.append(expected["path"])
    
    return results, missing


def run_tests(test_commands: List[str], worker_workspace: Path) -> Tuple[List[str], bool]:
    """Execute test commands and capture results"""
    test_results = []
    all_passed = True
    
    if not test_commands:
        return ["No tests specified"], True
    
    for cmd in test_commands:
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=worker_workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                test_results.append(f"✅ `{cmd}` - PASSED")
            else:
                test_results.append(f"❌ `{cmd}` - FAILED (exit {result.returncode})")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            test_results.append(f"❌ `{cmd}` - TIMEOUT (>30s)")
            all_passed = False
        except Exception as e:
            test_results.append(f"❌ `{cmd}` - ERROR: {e}")
            all_passed = False
    
    return test_results, all_passed


def generate_validation_report(
    worker_id: str,
    orchestrator_id: str,
    rubric: Dict,
    worker_report: str,
    file_check_results: List[str],
    missing_files: List[str],
    test_results: List[str],
    tests_passed: bool
) -> str:
    """Generate validation report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overall_pass = len(missing_files) == 0 and tests_passed
    
    report = f"""# Validation Result - Worker

**Orchestrator:** {orchestrator_id}  
**Worker:** {worker_id}  
**Validated:** {timestamp}  
**Result:** {"✅ PASS" if overall_pass else "❌ FAIL"}

## Rubric Compliance

### Deliverables
{chr(10).join(file_check_results)}

### Test Execution
{chr(10).join(test_results)}

## Missing Files
{chr(10).join(f"- {f}" for f in missing_files) if missing_files else "(None)"}

## Decision
{"✅ APPROVED - Ready for integration" if overall_pass else "❌ REJECTED - Address gaps above"}

## Next Steps
{f"Fix missing files: {', '.join(missing_files)}" if missing_files else "Proceed with integration"}

---
**Validation Complete:** {timestamp}
"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="Cross-Workspace Validator")
    parser.add_argument("--worker", required=True, help="Worker conversation ID")
    parser.add_argument("--orchestrator", default="con_ORCH", help="Orchestrator conversation ID")
    parser.add_argument("--rubric", required=True, type=Path, help="Path to RUBRIC file")
    parser.add_argument("--output", required=True, type=Path, help="Output validation report path")
    
    args = parser.parse_args()
    
    try:
        # Find worker workspace
        worker_workspace = find_worker_workspace(args.worker)
        logger.info(f"Worker workspace: {worker_workspace}")
        
        # Parse rubric
        rubric = parse_rubric(args.rubric)
        logger.info(f"Rubric parsed: {len(rubric['files'])} files, {len(rubric['tests'])} tests")
        
        # Find worker report
        worker_report_path = find_worker_report(worker_workspace)
        worker_report = worker_report_path.read_text()
        logger.info(f"Worker report found: {worker_report_path}")
        
        # Validate files
        file_results, missing_files = validate_files(rubric["files"], worker_workspace)
        logger.info(f"File validation: {len(missing_files)} missing")
        
        # Run tests
        test_results, tests_passed = run_tests(rubric["tests"], worker_workspace)
        logger.info(f"Test execution: {'PASSED' if tests_passed else 'FAILED'}")
        
        # Generate report
        validation_report = generate_validation_report(
            worker_id=args.worker,
            orchestrator_id=args.orchestrator,
            rubric=rubric,
            worker_report=worker_report,
            file_check_results=file_results,
            missing_files=missing_files,
            test_results=test_results,
            tests_passed=tests_passed
        )
        
        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(validation_report)
        
        logger.info(f"✓ Validation complete: {args.output}")
        
        return 0 if len(missing_files) == 0 and tests_passed else 1
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
