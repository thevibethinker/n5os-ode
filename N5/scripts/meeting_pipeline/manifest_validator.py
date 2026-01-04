#!/usr/bin/env python3
"""
Manifest Validator - Comprehensive validation for meeting state transitions

Purpose: Validate that manifest.json accurately reflects actual meeting artifacts.
This prevents false transitions where manifest claims completion but files are missing.

Usage:
  python3 manifest_validator.py <meeting_folder> [--fix] [--verbose]

Returns:
  Exit code 0 if valid, 1 if invalid, 2 if errors during validation

v1.0 (2026-01-03): Initial implementation with artifact validation
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

# Block ID to filename mapping
BLOCK_FILE_PATTERNS = {
    "B01": "B01_DETAILED_RECAP.md",
    "B02": "B02_COMMITMENTS_CONTEXTUAL.md",
    "B05": "B05_OUTSTANDING_QUESTIONS.md",
    "B06": "B06_PILOT_INTELLIGENCE.md",
    "B07": "B07_WARM_INTRO_BIDIRECTIONAL.md",
    "B08": "B08_STAKEHOLDER_INTELLIGENCE.md",
    "B11": "B11_METRICS_SNAPSHOT.md",
    "B13": "B13_PLAN_OF_ACTION.md",
    "B14": "B14_BLURBS_REQUESTED.jsonl",
    "B15": "B15_STAKEHOLDER_MAP.md",
    "B21": "B21_KEY_MOMENTS.md",
    "B24": "B24_PRODUCT_IDEA_EXTRACTION.md",
    "B25": "B25_DELIVERABLE_CONTENT_MAP.md",
    "B26": "B26_MEETING_METADATA_SUMMARY.md",
    "B27": "B27_WELLNESS_INDICATORS.md",
    "B31": "B31_STAKEHOLDER_RESEARCH.md",
    "B32": "B32_THOUGHT_PROVOKING_IDEAS.md",
}

# Required blocks for transition (minimum set)
REQUIRED_BLOCKS = ["B01", "B02", "B25", "B26"]

# System state to output file mapping
SYSTEM_OUTPUT_FILES = {
    "follow_up_email": ["FOLLOW_UP_EMAIL.md"],
    "warm_intro": ["B07_WARM_INTRO_BIDIRECTIONAL.md"],
    "blurbs": [],  # Dynamic based on B14 content
}


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    check_name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    fix_action: Optional[str] = None


@dataclass
class ManifestValidationReport:
    """Complete validation report for a meeting"""
    meeting_folder: str
    timestamp: str
    manifest_exists: bool = False
    manifest_valid_json: bool = False
    checks: list = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if all error-level checks passed"""
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def can_transition(self) -> bool:
        """True if meeting can safely transition to [P]"""
        return self.manifest_exists and self.manifest_valid_json and self.is_valid

    @property
    def error_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed and c.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed and c.severity == "warning")

    def add_check(self, check: ValidationResult):
        self.checks.append(check)

    def to_dict(self) -> dict:
        return {
            "meeting_folder": self.meeting_folder,
            "timestamp": self.timestamp,
            "is_valid": self.is_valid,
            "can_transition": self.can_transition,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "checks": [
                {
                    "name": c.check_name,
                    "passed": c.passed,
                    "message": c.message,
                    "severity": c.severity,
                }
                for c in self.checks
            ]
        }


def validate_manifest_schema(manifest: dict, report: ManifestValidationReport):
    """Validate manifest has required fields"""

    # Check status field
    status = manifest.get("status")
    if not status:
        report.add_check(ValidationResult(
            check_name="status_field",
            passed=False,
            message="Missing 'status' field in manifest",
            fix_action="Add 'status' field with appropriate value"
        ))
    else:
        valid_statuses = {"manifest_generated", "intelligence_generated", "mg2_completed", "processed"}
        if status not in valid_statuses:
            report.add_check(ValidationResult(
                check_name="status_field",
                passed=False,
                message=f"Invalid status '{status}'. Valid: {valid_statuses}",
            ))
        else:
            report.add_check(ValidationResult(
                check_name="status_field",
                passed=True,
                message=f"Status field valid: '{status}'"
            ))

    # Check blocks_generated section
    blocks = manifest.get("blocks_generated", {})
    if not blocks:
        report.add_check(ValidationResult(
            check_name="blocks_generated_section",
            passed=False,
            message="Missing 'blocks_generated' section",
            severity="warning",
            fix_action="Add blocks_generated section"
        ))
    else:
        report.add_check(ValidationResult(
            check_name="blocks_generated_section",
            passed=True,
            message=f"blocks_generated has {len(blocks)} entries"
        ))

    # Check system_states section
    states = manifest.get("system_states", {})
    if not states:
        report.add_check(ValidationResult(
            check_name="system_states_section",
            passed=False,
            message="Missing 'system_states' section",
            severity="warning",
            fix_action="Run manifest_state_updater.py to initialize"
        ))
    else:
        report.add_check(ValidationResult(
            check_name="system_states_section",
            passed=True,
            message=f"system_states has {len(states)} entries"
        ))


def validate_block_artifacts(manifest: dict, meeting_folder: Path, report: ManifestValidationReport):
    """Validate that claimed blocks have corresponding files"""

    blocks = manifest.get("blocks_generated", {})

    # Check required blocks exist
    for block_id in REQUIRED_BLOCKS:
        filename = BLOCK_FILE_PATTERNS.get(block_id)
        if not filename:
            continue

        file_path = meeting_folder / filename

        # Check if manifest claims this block exists
        claimed = blocks.get(block_id.lower().replace("b", "")) or blocks.get(block_id.lower())

        if file_path.exists():
            # File exists - check if non-empty
            if file_path.stat().st_size > 0:
                report.add_check(ValidationResult(
                    check_name=f"block_{block_id}_file",
                    passed=True,
                    message=f"{block_id}: File exists ({file_path.stat().st_size} bytes)"
                ))
            else:
                report.add_check(ValidationResult(
                    check_name=f"block_{block_id}_file",
                    passed=False,
                    message=f"{block_id}: File exists but is empty",
                    severity="error"
                ))
        else:
            report.add_check(ValidationResult(
                check_name=f"block_{block_id}_file",
                passed=False,
                message=f"{block_id}: Required file missing: {filename}",
                severity="error",
                fix_action=f"Generate {block_id} block or mark meeting as not ready"
            ))

    # Check for any additional blocks claimed in manifest
    for key, value in blocks.items():
        if value is True:
            # Try to find corresponding file
            block_id = f"B{key.zfill(2)}" if key.isdigit() else key.upper()
            filename = BLOCK_FILE_PATTERNS.get(block_id)

            if filename:
                file_path = meeting_folder / filename
                if not file_path.exists():
                    report.add_check(ValidationResult(
                        check_name=f"block_{block_id}_claimed",
                        passed=False,
                        message=f"{block_id}: Claimed complete but file missing",
                        severity="warning",
                        fix_action=f"Update blocks_generated.{key} to false or create file"
                    ))


def validate_system_states(manifest: dict, meeting_folder: Path, report: ManifestValidationReport):
    """Validate system_states match actual artifacts"""

    states = manifest.get("system_states", {})
    if not states:
        return

    # Validate follow_up_email
    email_state = states.get("follow_up_email", {})
    email_status = email_state.get("status", "not_started")

    if email_status == "complete":
        output_file = email_state.get("output_file", "FOLLOW_UP_EMAIL.md")
        file_path = meeting_folder / output_file

        if file_path.exists() and file_path.stat().st_size > 100:
            report.add_check(ValidationResult(
                check_name="follow_up_email_artifact",
                passed=True,
                message=f"Follow-up email exists ({file_path.stat().st_size} bytes)"
            ))
        elif file_path.exists():
            report.add_check(ValidationResult(
                check_name="follow_up_email_artifact",
                passed=False,
                message="Follow-up email file too small (<100 bytes)",
                severity="warning"
            ))
        else:
            report.add_check(ValidationResult(
                check_name="follow_up_email_artifact",
                passed=False,
                message=f"follow_up_email marked complete but file missing: {output_file}",
                severity="error",
                fix_action="Generate follow-up email or update status to 'not_started'"
            ))

    # Validate warm_intro
    intro_state = states.get("warm_intro", {})
    intro_status = intro_state.get("status", "not_started")

    if intro_status == "complete":
        b07_path = meeting_folder / "B07_WARM_INTRO_BIDIRECTIONAL.md"
        if b07_path.exists():
            report.add_check(ValidationResult(
                check_name="warm_intro_artifact",
                passed=True,
                message="Warm intro file exists"
            ))
        else:
            report.add_check(ValidationResult(
                check_name="warm_intro_artifact",
                passed=False,
                message="warm_intro marked complete but B07 file missing",
                severity="warning",
                fix_action="Update warm_intro status to 'not_applicable' if no intro needed"
            ))

    # Validate blurbs
    blurbs_state = states.get("blurbs", {})
    if blurbs_state.get("b14_exists", False):
        b14_path = meeting_folder / "B14_BLURBS_REQUESTED.jsonl"
        if b14_path.exists():
            report.add_check(ValidationResult(
                check_name="blurbs_b14_exists",
                passed=True,
                message="B14 file exists as claimed"
            ))
        else:
            report.add_check(ValidationResult(
                check_name="blurbs_b14_exists",
                passed=False,
                message="b14_exists=true but file missing",
                severity="error"
            ))


def validate_transition_readiness(manifest: dict, report: ManifestValidationReport):
    """Validate that ready_for_state_transition is consistent"""

    states = manifest.get("system_states", {})
    ready_state = states.get("ready_for_state_transition", {})

    if not ready_state:
        report.add_check(ValidationResult(
            check_name="transition_readiness_calculated",
            passed=False,
            message="ready_for_state_transition not calculated",
            severity="warning",
            fix_action="Run manifest_state_updater.py to evaluate readiness"
        ))
        return

    claimed_ready = ready_state.get("status", False)
    blocking = ready_state.get("blocking_systems", [])

    # Recalculate readiness
    actual_blocking = []

    if states.get("intelligence_blocks", {}).get("status") != "complete":
        actual_blocking.append("intelligence_blocks")

    if states.get("follow_up_email", {}).get("status") != "complete":
        actual_blocking.append("follow_up_email")

    intro_status = states.get("warm_intro", {}).get("status", "not_started")
    if intro_status not in ["complete", "not_applicable"]:
        actual_blocking.append("warm_intro")

    blurbs = states.get("blurbs", {})
    if blurbs.get("b14_exists") and blurbs.get("pending_blurbs", 1) > 0:
        actual_blocking.append("blurbs")

    actual_ready = len(actual_blocking) == 0

    if claimed_ready == actual_ready and set(blocking) == set(actual_blocking):
        report.add_check(ValidationResult(
            check_name="transition_readiness_consistent",
            passed=True,
            message=f"Readiness calculation consistent (ready={actual_ready})"
        ))
    else:
        report.add_check(ValidationResult(
            check_name="transition_readiness_consistent",
            passed=False,
            message=f"Readiness mismatch: claimed={claimed_ready}, actual={actual_ready}",
            severity="warning",
            fix_action="Run manifest_state_updater.py to recalculate"
        ))


def validate_meeting(meeting_folder: Path, verbose: bool = False) -> ManifestValidationReport:
    """Run full validation on a meeting folder"""

    report = ManifestValidationReport(
        meeting_folder=str(meeting_folder),
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    # Check manifest exists
    manifest_path = meeting_folder / "manifest.json"
    if not manifest_path.exists():
        report.manifest_exists = False
        report.add_check(ValidationResult(
            check_name="manifest_exists",
            passed=False,
            message="manifest.json not found",
            fix_action="Create manifest using MG-1"
        ))
        return report

    report.manifest_exists = True

    # Check manifest is valid JSON
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        report.manifest_valid_json = True
    except json.JSONDecodeError as e:
        report.manifest_valid_json = False
        report.add_check(ValidationResult(
            check_name="manifest_valid_json",
            passed=False,
            message=f"Invalid JSON: {e}"
        ))
        return report

    # Run all validation checks
    validate_manifest_schema(manifest, report)
    validate_block_artifacts(manifest, meeting_folder, report)
    validate_system_states(manifest, meeting_folder, report)
    validate_transition_readiness(manifest, report)

    return report


def print_report(report: ManifestValidationReport, verbose: bool = False):
    """Print validation report to console"""

    print(f"\n{'='*60}")
    print(f"MANIFEST VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Meeting: {Path(report.meeting_folder).name}")
    print(f"Timestamp: {report.timestamp}")
    print(f"{'='*60}\n")

    if not report.manifest_exists:
        print("  manifest.json not found")
        return

    if not report.manifest_valid_json:
        print("  manifest.json is not valid JSON")
        return

    # Group checks by status
    passed = [c for c in report.checks if c.passed]
    failed_errors = [c for c in report.checks if not c.passed and c.severity == "error"]
    failed_warnings = [c for c in report.checks if not c.passed and c.severity == "warning"]

    if verbose or failed_errors or failed_warnings:
        print("CHECKS:")
        for check in report.checks:
            if check.passed:
                icon = ""
            elif check.severity == "error":
                icon = ""
            else:
                icon = ""

            if verbose or not check.passed:
                print(f"  {icon} {check.check_name}: {check.message}")
                if check.fix_action and not check.passed:
                    print(f"      Fix: {check.fix_action}")
        print()

    # Summary
    print(f"SUMMARY:")
    print(f"  Passed: {len(passed)}")
    print(f"  Errors: {report.error_count}")
    print(f"  Warnings: {report.warning_count}")
    print()

    if report.can_transition:
        print(f"  READY FOR TRANSITION TO [P]")
    else:
        print(f"  NOT READY FOR TRANSITION")
        if failed_errors:
            print(f"     Blocking errors: {len(failed_errors)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate manifest.json and meeting artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a single meeting
  python3 manifest_validator.py /path/to/meeting

  # Validate with verbose output
  python3 manifest_validator.py /path/to/meeting --verbose

  # Output JSON report
  python3 manifest_validator.py /path/to/meeting --json
        """
    )

    parser.add_argument("meeting_folder", help="Path to meeting folder")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress output, exit code only")

    args = parser.parse_args()

    meeting_folder = Path(args.meeting_folder)
    if not meeting_folder.is_dir():
        print(f"Error: {meeting_folder} is not a directory", file=sys.stderr)
        sys.exit(2)

    report = validate_meeting(meeting_folder, args.verbose)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    elif not args.quiet:
        print_report(report, args.verbose)

    sys.exit(0 if report.can_transition else 1)


if __name__ == "__main__":
    main()
