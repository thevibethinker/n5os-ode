#!/usr/bin/env python3
"""
Phase Telemetry Validator
Validates worker phase completion through structured telemetry.

Implements quality gates from demonstrator build orchestrator:
- ERROR: Blocks advancement
- WARNING: Allows with concerns noted
- INFO: Context only

Key innovation: Objective validation enables autonomous orchestrator decisions.
"""

import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")


class TelemetryValidator:
    """Validates phase handoff telemetry and enforces quality gates."""
    
    # Severity levels
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    
    # Gate decisions
    BLOCK = "block"
    ALLOW = "allow"
    PASS = "pass"
    
    def __init__(self):
        self.issues = []
        self.recommendations = []
    
    def validate_handoff(self, telemetry_path: Path) -> Dict:
        """
        Validate phase handoff telemetry.
        
        Returns decision dict with:
        - decision: 'block'/'allow'/'pass'
        - severity: highest severity found
        - issues: list of issues
        - recommendations: list of recommendations
        """
        if not telemetry_path.exists():
            return {
                "decision": self.BLOCK,
                "severity": self.CRITICAL,
                "reason": f"Telemetry file not found: {telemetry_path}",
                "issues": [{"type": "missing_telemetry", "severity": self.CRITICAL}],
                "recommendations": ["Worker must generate telemetry before handoff"]
            }
        
        try:
            telemetry = json.loads(telemetry_path.read_text())
        except json.JSONDecodeError as e:
            return {
                "decision": self.BLOCK,
                "severity": self.CRITICAL,
                "reason": f"Invalid JSON in telemetry: {e}",
                "issues": [{"type": "invalid_json", "severity": self.CRITICAL}],
                "recommendations": ["Fix telemetry JSON format"]
            }
        
        # Validate schema
        schema_valid, schema_issues = self._validate_schema(telemetry)
        if not schema_valid:
            return {
                "decision": self.BLOCK,
                "severity": self.CRITICAL,
                "reason": "Telemetry schema validation failed",
                "issues": schema_issues,
                "recommendations": ["Ensure telemetry follows phase_handoff schema"]
            }
        
        # Run quality checks
        self.issues = []
        self.recommendations = []
        
        self._check_outputs(telemetry)
        self._check_quality(telemetry)
        self._check_tests(telemetry)
        self._check_status(telemetry)
        
        # Determine decision based on issues
        decision, severity = self._make_decision()
        
        return {
            "decision": decision,
            "severity": severity,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "telemetry": telemetry
        }
    
    def _validate_schema(self, telemetry: Dict) -> Tuple[bool, List[Dict]]:
        """Validate required fields in telemetry."""
        required_fields = [
            "phase_id",
            "worker_id",
            "timestamp",
            "status",
            "outputs",
            "quality"
        ]
        
        issues = []
        for field in required_fields:
            if field not in telemetry:
                issues.append({
                    "type": "missing_field",
                    "field": field,
                    "severity": self.CRITICAL
                })
        
        return len(issues) == 0, issues
    
    def _check_outputs(self, telemetry: Dict):
        """Check that required outputs were produced."""
        outputs = telemetry.get("outputs", {})
        files = outputs.get("files", [])
        
        # Check if files exist
        missing_files = []
        for file_path in files:
            path = WORKSPACE_ROOT / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if not path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            self.issues.append({
                "type": "missing_outputs",
                "files": missing_files,
                "severity": self.CRITICAL
            })
            self.recommendations.append(f"Generate missing output files: {', '.join(missing_files)}")
    
    def _check_quality(self, telemetry: Dict):
        """Check quality scan results."""
        quality = telemetry.get("quality", {})
        
        # Check for critical issues
        placeholders = quality.get("placeholders", [])
        stubs = quality.get("stubs", [])
        incomplete = quality.get("incomplete", [])
        
        # Critical placeholders (bare except, production stubs)
        critical_patterns = [
            r"bare\s+except",
            r"pass\s*#\s*TODO",
            r"raise\s+NotImplementedError.*production"
        ]
        
        for item in placeholders + incomplete:
            issue_text = item.get("issue", "").lower()
            for pattern in critical_patterns:
                if re.search(pattern, issue_text, re.IGNORECASE):
                    self.issues.append({
                        "type": "critical_placeholder",
                        "detail": item,
                        "severity": self.CRITICAL
                    })
                    self.recommendations.append(f"Fix critical issue in {item.get('file')}: {item.get('issue')}")
        
        # Major issues (stubs, incomplete implementations)
        for stub in stubs:
            if stub.get("severity") == "major":
                self.issues.append({
                    "type": "stub_function",
                    "detail": stub,
                    "severity": self.MAJOR
                })
                self.recommendations.append(f"Implement stub function: {stub.get('function')} in {stub.get('file')}")
        
        # Minor issues (TODOs, minor placeholders)
        for item in placeholders:
            if item.get("severity") == "minor":
                self.issues.append({
                    "type": "minor_placeholder",
                    "detail": item,
                    "severity": self.MINOR
                })
    
    def _check_tests(self, telemetry: Dict):
        """Check test results."""
        tests = telemetry.get("tests", {})
        status = tests.get("status")
        
        if status == "failed":
            self.issues.append({
                "type": "tests_failed",
                "detail": tests,
                "severity": self.CRITICAL
            })
            self.recommendations.append("Fix failing tests before advancing")
        elif status == "partial":
            self.issues.append({
                "type": "tests_partial",
                "detail": tests,
                "severity": self.MAJOR
            })
            self.recommendations.append("Complete test coverage")
        elif status == "not_run":
            self.issues.append({
                "type": "tests_not_run",
                "severity": self.MAJOR
            })
            self.recommendations.append("Run tests to verify functionality")
    
    def _check_status(self, telemetry: Dict):
        """Check reported status."""
        status = telemetry.get("status")
        
        if status == "failed":
            self.issues.append({
                "type": "phase_failed",
                "severity": self.CRITICAL
            })
            self.recommendations.append("Phase reported failure - review logs and retry")
        elif status == "blocked":
            self.issues.append({
                "type": "phase_blocked",
                "severity": self.CRITICAL
            })
            blockers = telemetry.get("blockers", [])
            if blockers:
                self.recommendations.append(f"Resolve blockers: {', '.join(blockers)}")
            else:
                self.recommendations.append("Resolve unspecified blockers")
        elif status == "partial":
            self.issues.append({
                "type": "phase_partial",
                "severity": self.MAJOR
            })
            self.recommendations.append("Complete remaining phase objectives")
    
    def _make_decision(self) -> Tuple[str, str]:
        """
        Make gate decision based on issues.
        
        Returns: (decision, severity)
        - BLOCK: Critical issues present
        - ALLOW: Major/minor issues only
        - PASS: No issues or info only
        """
        if not self.issues:
            return self.PASS, "none"
        
        severities = [issue["severity"] for issue in self.issues]
        
        if self.CRITICAL in severities:
            return self.BLOCK, self.CRITICAL
        elif self.MAJOR in severities:
            return self.ALLOW, self.MAJOR
        else:
            return self.ALLOW, self.MINOR


def validate_telemetry(telemetry_path: Path, output_path: Optional[Path] = None) -> int:
    """
    Validate phase handoff telemetry.
    
    Args:
        telemetry_path: Path to telemetry JSON
        output_path: Optional path to save validation results
    
    Returns:
        0 if PASS, 1 if ALLOW, 2 if BLOCK
    """
    validator = TelemetryValidator()
    result = validator.validate_handoff(telemetry_path)
    
    # Log results
    decision = result["decision"]
    severity = result["severity"]
    issues_count = len(result["issues"])
    
    logger.info(f"=== TELEMETRY VALIDATION ===")
    logger.info(f"File: {telemetry_path}")
    logger.info(f"Decision: {decision.upper()}")
    logger.info(f"Severity: {severity}")
    logger.info(f"Issues: {issues_count}")
    
    if decision == TelemetryValidator.BLOCK:
        logger.error("❌ BLOCKED - Critical issues prevent advancement")
        for issue in result["issues"]:
            if issue["severity"] == TelemetryValidator.CRITICAL:
                logger.error(f"  - {issue['type']}: {issue.get('detail', 'See telemetry')}")
    elif decision == TelemetryValidator.ALLOW:
        logger.warning("⚠️  ALLOW - Issues noted, advancement permitted")
        for issue in result["issues"]:
            logger.warning(f"  - {issue['type']} ({issue['severity']})")
    else:
        logger.info("✅ PASS - No blocking issues")
    
    if result["recommendations"]:
        logger.info("\nRecommendations:")
        for rec in result["recommendations"]:
            logger.info(f"  → {rec}")
    
    # Save results if requested
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        logger.info(f"\n✓ Validation results saved: {output_path}")
    
    # Return exit code based on decision
    if decision == TelemetryValidator.PASS:
        return 0
    elif decision == TelemetryValidator.ALLOW:
        return 1
    else:
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="Validate phase handoff telemetry with quality gates"
    )
    parser.add_argument(
        "telemetry_file",
        help="Path to phase handoff telemetry JSON"
    )
    parser.add_argument(
        "--output",
        help="Path to save validation results JSON"
    )
    
    args = parser.parse_args()
    
    telemetry_path = Path(args.telemetry_file)
    output_path = Path(args.output) if args.output else None
    
    return validate_telemetry(telemetry_path, output_path)


if __name__ == "__main__":
    exit(main())
