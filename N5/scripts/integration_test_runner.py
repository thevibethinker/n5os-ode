#!/usr/bin/env python3
"""
Integration Test Runner for Session State System

Executes tests against worker deliverables and reports results to orchestrator.
Supports multiple test frameworks and test types.

Usage:
  python3 integration_test_runner.py --worker-convo con_WORKER_123
  python3 integration_test_runner.py --worker-convo con_WORKER_123 --test-type integration
  python3 integration_test_runner.py --worker-convo con_WORKER_123 --dry-run
"""

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

WORKSPACES_ROOT = Path("/home/.z/workspaces")
USER_WORKSPACE = Path("/home/workspace")


@dataclass
class TestResult:
    """Test execution result"""
    framework: str
    test_type: str
    passed: bool
    total: int
    passed_count: int
    failed_count: int
    skipped_count: int
    duration_seconds: float
    output: str
    error: Optional[str] = None


class IntegrationTestRunner:
    """Run integration tests on worker deliverables"""
    
    def __init__(self, worker_convo_id: str, dry_run: bool = False):
        self.worker_convo_id = worker_convo_id
        self.worker_workspace = WORKSPACES_ROOT / worker_convo_id
        self.dry_run = dry_run
        
        if not self.worker_workspace.exists():
            raise ValueError(f"Worker workspace not found: {self.worker_workspace}")
    
    def detect_test_framework(self, project_path: Path) -> Optional[str]:
        """Auto-detect test framework from project files"""
        if (project_path / "pytest.ini").exists() or (project_path / "setup.py").exists():
            return "pytest"
        
        if (project_path / "package.json").exists():
            try:
                with open(project_path / "package.json") as f:
                    pkg = json.load(f)
                    scripts = pkg.get("scripts", {})
                    if "test" in scripts:
                        if "jest" in scripts["test"]:
                            return "jest"
                        if "bun" in scripts["test"]:
                            return "bun"
                        return "npm"
            except Exception as e:
                logger.warning(f"Failed to parse package.json: {e}")
        
        if (project_path / "go.mod").exists():
            return "go"
        
        if (project_path / "Cargo.toml").exists():
            return "cargo"
        
        return None
    
    def find_test_directories(self, base_path: Path) -> List[Path]:
        """Find directories containing tests"""
        test_dirs = []
        
        test_patterns = ["test", "tests", "__tests__", "spec", "specs"]
        
        for pattern in test_patterns:
            for test_dir in base_path.rglob(pattern):
                if test_dir.is_dir():
                    test_dirs.append(test_dir)
        
        if base_path.name in test_patterns:
            test_dirs.append(base_path)
        
        return list(set(test_dirs))
    
    def run_pytest(self, project_path: Path, test_type: str = "all") -> TestResult:
        """Run pytest tests"""
        import time
        
        start = time.time()
        
        cmd = ["python3", "-m", "pytest", "-v", "--tb=short"]
        
        if test_type == "unit":
            cmd.extend(["-m", "unit"])
        elif test_type == "integration":
            cmd.extend(["-m", "integration"])
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would run: {' '.join(cmd)} in {project_path}")
            return TestResult(
                framework="pytest",
                test_type=test_type,
                passed=True,
                total=0,
                passed_count=0,
                failed_count=0,
                skipped_count=0,
                duration_seconds=0.0,
                output="[DRY RUN]"
            )
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start
            
            output = result.stdout + "\n" + result.stderr
            passed = result.returncode == 0
            
            total, passed_count, failed_count, skipped_count = self._parse_pytest_output(output)
            
            return TestResult(
                framework="pytest",
                test_type=test_type,
                passed=passed,
                total=total,
                passed_count=passed_count,
                failed_count=failed_count,
                skipped_count=skipped_count,
                duration_seconds=duration,
                output=output
            )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                framework="pytest",
                test_type=test_type,
                passed=False,
                total=0,
                passed_count=0,
                failed_count=0,
                skipped_count=0,
                duration_seconds=time.time() - start,
                output="",
                error="Test execution timeout (300s)"
            )
        except Exception as e:
            return TestResult(
                framework="pytest",
                test_type=test_type,
                passed=False,
                total=0,
                passed_count=0,
                failed_count=0,
                skipped_count=0,
                duration_seconds=time.time() - start,
                output="",
                error=str(e)
            )
    
    def run_bun_test(self, project_path: Path, test_type: str = "all") -> TestResult:
        """Run bun test"""
        import time
        
        start = time.time()
        
        cmd = ["bun", "test"]
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would run: {' '.join(cmd)} in {project_path}")
            return TestResult(
                framework="bun",
                test_type=test_type,
                passed=True,
                total=0,
                passed_count=0,
                failed_count=0,
                skipped_count=0,
                duration_seconds=0.0,
                output="[DRY RUN]"
            )
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start
            
            output = result.stdout + "\n" + result.stderr
            passed = result.returncode == 0
            
            total, passed_count, failed_count, skipped_count = self._parse_bun_output(output)
            
            return TestResult(
                framework="bun",
                test_type=test_type,
                passed=passed,
                total=total,
                passed_count=passed_count,
                failed_count=failed_count,
                skipped_count=skipped_count,
                duration_seconds=duration,
                output=output
            )
        
        except Exception as e:
            return TestResult(
                framework="bun",
                test_type=test_type,
                passed=False,
                total=0,
                passed_count=0,
                failed_count=0,
                skipped_count=0,
                duration_seconds=time.time() - start,
                output="",
                error=str(e)
            )
    
    def _parse_pytest_output(self, output: str) -> tuple:
        """Parse pytest output for test counts"""
        import re
        
        match = re.search(r"(\d+) passed", output)
        passed = int(match.group(1)) if match else 0
        
        match = re.search(r"(\d+) failed", output)
        failed = int(match.group(1)) if match else 0
        
        match = re.search(r"(\d+) skipped", output)
        skipped = int(match.group(1)) if match else 0
        
        total = passed + failed + skipped
        
        return total, passed, failed, skipped
    
    def _parse_bun_output(self, output: str) -> tuple:
        """Parse bun test output for test counts"""
        import re
        
        match = re.search(r"(\d+) pass", output)
        passed = int(match.group(1)) if match else 0
        
        match = re.search(r"(\d+) fail", output)
        failed = int(match.group(1)) if match else 0
        
        total = passed + failed
        
        return total, passed, failed, 0
    
    def run_tests(self, test_type: str = "all") -> List[TestResult]:
        """Run all detected tests"""
        results = []
        
        test_dirs = self.find_test_directories(self.worker_workspace)
        
        if not test_dirs:
            logger.warning(f"No test directories found in {self.worker_workspace}")
            
            framework = self.detect_test_framework(USER_WORKSPACE)
            if framework:
                logger.info(f"Checking user workspace for {framework} tests")
                if framework == "pytest":
                    results.append(self.run_pytest(USER_WORKSPACE, test_type))
                elif framework == "bun":
                    results.append(self.run_bun_test(USER_WORKSPACE, test_type))
            
            return results
        
        for test_dir in test_dirs:
            project_path = test_dir.parent if test_dir.name in ["test", "tests", "__tests__"] else test_dir
            
            framework = self.detect_test_framework(project_path)
            
            if not framework:
                logger.warning(f"No test framework detected for {project_path}")
                continue
            
            logger.info(f"Running {framework} tests in {project_path}")
            
            if framework == "pytest":
                results.append(self.run_pytest(project_path, test_type))
            elif framework == "bun":
                results.append(self.run_bun_test(project_path, test_type))
        
        return results
    
    def report_results(self, results: List[TestResult]) -> Dict:
        """Generate test results report"""
        all_passed = all(r.passed for r in results)
        
        total_tests = sum(r.total for r in results)
        total_passed = sum(r.passed_count for r in results)
        total_failed = sum(r.failed_count for r in results)
        total_skipped = sum(r.skipped_count for r in results)
        total_duration = sum(r.duration_seconds for r in results)
        
        report = {
            "worker_convo_id": self.worker_convo_id,
            "timestamp": "2025-10-16T10:10:00Z",
            "all_passed": all_passed,
            "summary": {
                "total": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "skipped": total_skipped,
                "duration_seconds": round(total_duration, 2)
            },
            "results": [
                {
                    "framework": r.framework,
                    "test_type": r.test_type,
                    "passed": r.passed,
                    "total": r.total,
                    "passed_count": r.passed_count,
                    "failed_count": r.failed_count,
                    "skipped_count": r.skipped_count,
                    "duration_seconds": round(r.duration_seconds, 2),
                    "error": r.error
                }
                for r in results
            ]
        }
        
        return report


def main(worker_convo_id: str, test_type: str = "all", dry_run: bool = False) -> int:
    """Main entry point"""
    try:
        runner = IntegrationTestRunner(worker_convo_id, dry_run=dry_run)
        
        logger.info(f"Running {test_type} tests for worker {worker_convo_id}")
        
        results = runner.run_tests(test_type)
        
        if not results:
            logger.warning("No tests found or executed")
            return 1
        
        report = runner.report_results(results)
        
        report_path = WORKSPACES_ROOT / worker_convo_id / "TEST_RESULTS.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✓ Test report saved: {report_path}")
        logger.info(f"Summary: {report['summary']['passed']}/{report['summary']['total']} passed")
        
        if not report["all_passed"]:
            logger.error(f"✗ {report['summary']['failed']} tests failed")
            return 1
        
        logger.info("✓ All tests passed")
        return 0
    
    except Exception as e:
        logger.error(f"Test runner error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run integration tests on worker deliverables")
    parser.add_argument("--worker-convo", required=True, help="Worker conversation ID")
    parser.add_argument("--test-type", default="all", choices=["all", "unit", "integration", "smoke"], help="Type of tests to run")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    
    args = parser.parse_args()
    
    sys.exit(main(args.worker_convo, args.test_type, args.dry_run))
