#!/usr/bin/env python3
"""
Principle Violation Detector for Session State System

Detects violations of architectural principles in worker output.
Flags common mistakes before orchestrator review.

Checks for:
- P15: Complete Before Claiming (progress vs claims)
- P16: No Invented Limits (fabricated constraints)
- P19: Error Handling Not Optional (missing try/except)

Usage:
  python3 principle_violation_detector.py --worker-convo con_WORKER_123
  python3 principle_violation_detector.py --worker-convo con_WORKER_123 --dry-run
"""

import argparse
import json
import logging
import re
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
class Violation:
    """Principle violation"""
    principle: str
    severity: str  # high, medium, low
    file_path: str
    line_number: Optional[int]
    description: str
    evidence: str


class PrincipleViolationDetector:
    """Detect principle violations in worker output"""
    
    def __init__(self, worker_convo_id: str, dry_run: bool = False):
        self.worker_convo_id = worker_convo_id
        self.worker_workspace = WORKSPACES_ROOT / worker_convo_id
        self.dry_run = dry_run
        self.violations: List[Violation] = []
        
        if not self.worker_workspace.exists():
            raise ValueError(f"Worker workspace not found: {self.worker_workspace}")
    
    def check_p15_complete_before_claiming(self) -> None:
        """P15: Check if claims match actual completion"""
        # Check SESSION_STATE.md for completion claims
        state_file = self.worker_workspace / "SESSION_STATE.md"
        
        if not state_file.exists():
            return
        
        try:
            content = state_file.read_text()
            
            # Look for completion claims
            completion_patterns = [
                r"✓ Done",
                r"✓ Complete",
                r"Finished",
                r"All complete",
                r"100%"
            ]
            
            has_completion_claim = any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in completion_patterns
            )
            
            if not has_completion_claim:
                return
            
            # Check if there are still open tasks
            open_task_patterns = [
                r"### Next Actions\s*\n\s*1\.",
                r"- \[ \]",  # Unchecked checkbox
                r"TODO",
                r"FIXME",
                r"### Blocked"
            ]
            
            has_open_tasks = any(
                re.search(pattern, content)
                for pattern in open_task_patterns
            )
            
            if has_open_tasks:
                self.violations.append(Violation(
                    principle="P15",
                    severity="high",
                    file_path=str(state_file.relative_to(self.worker_workspace)),
                    line_number=None,
                    description="Claimed complete but has open tasks",
                    evidence="Found completion claim with unchecked items or next actions"
                ))
        
        except Exception as e:
            logger.warning(f"Failed to check P15: {e}")
    
    def check_p16_invented_limits(self) -> None:
        """P16: Check for fabricated API/system limits"""
        # Known false limit patterns
        false_limit_patterns = [
            (r"gmail.*limit.*3", "Gmail 3-message limit (doesn't exist)"),
            (r"api.*limit.*\d+.*per.*day", "Undocumented API daily limit"),
            (r"must.*be.*under.*\d+.*characters", "Arbitrary character limit"),
            (r"maximum.*of.*\d+.*results", "Undocumented result limit"),
        ]
        
        # Check markdown files
        for md_file in self.worker_workspace.rglob("*.md"):
            try:
                content = md_file.read_text()
                
                for pattern, description in false_limit_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        self.violations.append(Violation(
                            principle="P16",
                            severity="medium",
                            file_path=str(md_file.relative_to(self.worker_workspace)),
                            line_number=line_num,
                            description=f"Possible invented limit: {description}",
                            evidence=match.group(0)
                        ))
            
            except Exception as e:
                logger.warning(f"Failed to check {md_file}: {e}")
    
    def check_p19_error_handling(self) -> None:
        """P19: Check for missing error handling in Python scripts"""
        # Check Python files
        for py_file in [self.worker_workspace.rglob("*.py"), USER_WORKSPACE.rglob("*.py")]:
            for script in py_file:
                # Skip if not in worker's work
                if not script.is_relative_to(self.worker_workspace) and not script.is_relative_to(USER_WORKSPACE):
                    continue
                
                try:
                    content = script.read_text()
                    
                    # Check if script has main logic
                    has_main = "def main(" in content or "if __name__ ==" in content
                    
                    if not has_main:
                        continue
                    
                    # Check for error handling
                    has_try_except = "try:" in content and "except" in content
                    has_error_logging = "logger.error" in content or "logging.error" in content
                    
                    if not has_try_except:
                        self.violations.append(Violation(
                            principle="P19",
                            severity="high",
                            file_path=str(script.relative_to(self.worker_workspace) if script.is_relative_to(self.worker_workspace) else script),
                            line_number=None,
                            description="Script missing try/except error handling",
                            evidence="No try/except block found in main logic"
                        ))
                    
                    # Check for file operations without error handling
                    file_ops = re.finditer(r"(open\(|\.write\(|\.read\()", content)
                    for op in file_ops:
                        # Check if this operation is in a try block
                        before_op = content[:op.start()]
                        after_last_try = before_op.rfind("try:")
                        after_last_except = before_op.rfind("except")
                        
                        # If no try block, or except came after try (meaning we're not in a try block)
                        if after_last_try == -1 or after_last_except > after_last_try:
                            line_num = before_op.count('\n') + 1
                            
                            self.violations.append(Violation(
                                principle="P19",
                                severity="medium",
                                file_path=str(script.relative_to(self.worker_workspace) if script.is_relative_to(self.worker_workspace) else script),
                                line_number=line_num,
                                description="File operation without error handling",
                                evidence=op.group(0)
                            ))
                            break  # Only flag once per file
                
                except Exception as e:
                    logger.warning(f"Failed to check {script}: {e}")
    
    def run_checks(self) -> List[Violation]:
        """Run all principle checks"""
        logger.info(f"Checking principles for {self.worker_convo_id}")
        
        if self.dry_run:
            logger.info("[DRY RUN] Would check: P15, P16, P19")
            return []
        
        self.check_p15_complete_before_claiming()
        self.check_p16_invented_limits()
        self.check_p19_error_handling()
        
        return self.violations
    
    def generate_report(self) -> Dict:
        """Generate violation report"""
        violations_by_severity = {
            "high": [v for v in self.violations if v.severity == "high"],
            "medium": [v for v in self.violations if v.severity == "medium"],
            "low": [v for v in self.violations if v.severity == "low"]
        }
        
        report = {
            "worker_convo_id": self.worker_convo_id,
            "timestamp": "2025-10-16T10:12:00Z",
            "total_violations": len(self.violations),
            "by_severity": {
                "high": len(violations_by_severity["high"]),
                "medium": len(violations_by_severity["medium"]),
                "low": len(violations_by_severity["low"])
            },
            "violations": [
                {
                    "principle": v.principle,
                    "severity": v.severity,
                    "file": v.file_path,
                    "line": v.line_number,
                    "description": v.description,
                    "evidence": v.evidence
                }
                for v in self.violations
            ]
        }
        
        return report


def main(worker_convo_id: str, dry_run: bool = False) -> int:
    """Main entry point"""
    try:
        detector = PrincipleViolationDetector(worker_convo_id, dry_run=dry_run)
        
        violations = detector.run_checks()
        
        report = detector.generate_report()
        
        # Save report
        if not dry_run:
            report_path = WORKSPACES_ROOT / worker_convo_id / "PRINCIPLE_VIOLATIONS.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✓ Saved violation report: {report_path}")
        
        # Log summary
        logger.info(f"Found {len(violations)} principle violations")
        logger.info(f"  High severity: {report['by_severity']['high']}")
        logger.info(f"  Medium severity: {report['by_severity']['medium']}")
        logger.info(f"  Low severity: {report['by_severity']['low']}")
        
        # Return non-zero if high severity violations found
        if report['by_severity']['high'] > 0:
            logger.warning("⚠ High severity violations found")
            return 1
        
        logger.info("✓ No high severity violations")
        return 0
    
    except Exception as e:
        logger.error(f"Violation detector error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect principle violations in worker output")
    parser.add_argument("--worker-convo", required=True, help="Worker conversation ID")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    
    args = parser.parse_args()
    
    sys.exit(main(args.worker_convo, args.dry_run))
