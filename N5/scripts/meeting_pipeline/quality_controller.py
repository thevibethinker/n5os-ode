#!/usr/bin/env python3
"""
Meeting Quality Controller
Manages iteration loop for meeting processing until quality standards met
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from output_validator import OutputValidator, ValidationResult

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

class QualityController:
    """Controls quality iteration for meeting processing"""
    
    def __init__(self, meeting_dir: Path, max_attempts: int = 3):
        self.meeting_dir = meeting_dir
        self.max_attempts = max_attempts
        self.validator = OutputValidator()
        self.attempt_log = []
    
    def check_quality(self) -> ValidationResult:
        """
        Validate current meeting output
        
        Returns:
            ValidationResult
        """
        return self.validator.validate_meeting_complete(self.meeting_dir)
    
    def generate_feedback_prompt(self, validation_result: ValidationResult, attempt: int) -> str:
        """
        Generate feedback for AI to improve output
        
        Args:
            validation_result: Current validation result
            attempt: Current attempt number
            
        Returns:
            Feedback prompt string
        """
        feedback = [
            f"## Quality Feedback - Attempt {attempt}/{self.max_attempts}",
            "",
            f"**Current Score:** {validation_result.score:.2f}",
            f"**Status:** {'✓ Passed' if validation_result.passed else '✗ Failed'}",
            ""
        ]
        
        if validation_result.issues:
            feedback.append("### Issues to Address:")
            for issue in validation_result.issues:
                feedback.append(f"- {issue}")
            feedback.append("")
        
        # Add attempt-specific guidance
        if attempt == 1:
            feedback.extend([
                "### First Attempt Guidance:",
                "- Ensure all mandatory blocks present (B01, B02, B05, B26)",
                "- Meet minimum length requirements",
                "- Include all required sections/fields",
                ""
            ])
        elif attempt == 2:
            feedback.extend([
                "### Second Attempt - Stricter Standards:",
                "- Previous attempt had quality issues",
                "- Focus on substantive content, not just meeting minimums",
                "- Ensure insights are meaningful, not summary repetition",
                "- Verify all commitments have owners and specific actions",
                ""
            ])
        elif attempt >= 3:
            feedback.extend([
                "### Final Attempt:",
                "- This is the last automated retry",
                "- If this fails, meeting will be flagged for human review",
                "- Prioritize correctness over completeness",
                ""
            ])
        
        return "\n".join(feedback)
    
    def log_attempt(self, attempt: int, result: ValidationResult, regenerated: bool = False):
        """Log validation attempt"""
        self.attempt_log.append({
            "attempt": attempt,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "score": result.score,
            "passed": result.passed,
            "issues_count": len(result.issues),
            "issues": result.issues,
            "regenerated": regenerated
        })
    
    def should_retry(self, result: ValidationResult, attempt: int) -> bool:
        """
        Determine if should retry generation
        
        Args:
            result: Current validation result
            attempt: Current attempt number
            
        Returns:
            True if should retry
        """
        if result.passed:
            return False
        
        if attempt >= self.max_attempts:
            return False
        
        # Don't retry if score is very low (fundamental failure)
        if result.score < 0.3:
            logging.warning(f"Score too low ({result.score:.2f}) to retry")
            return False
        
        return True
    
    def save_attempt_log(self):
        """Save attempt log to meeting directory"""
        log_file = self.meeting_dir / "validation_log.json"
        with open(log_file, 'w') as f:
            json.dump({
                "meeting_dir": str(self.meeting_dir),
                "attempts": self.attempt_log,
                "final_status": "passed" if self.attempt_log[-1]["passed"] else "failed",
                "generated_at": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        logging.info(f"Validation log saved: {log_file}")
    
    def get_status_summary(self) -> Dict:
        """Get summary of quality control process"""
        if not self.attempt_log:
            return {"status": "not_started"}
        
        latest = self.attempt_log[-1]
        return {
            "status": "passed" if latest["passed"] else "failed",
            "attempts": len(self.attempt_log),
            "final_score": latest["score"],
            "final_issues_count": latest["issues_count"],
            "needs_human_review": not latest["passed"] and len(self.attempt_log) >= self.max_attempts
        }

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeting quality control")
    parser.add_argument("meeting_dir", type=Path, help="Path to meeting directory")
    parser.add_argument("--check-only", action="store_true", help="Only check, don't generate feedback")
    parser.add_argument("--attempt", type=int, default=1, help="Attempt number")
    
    args = parser.parse_args()
    
    controller = QualityController(args.meeting_dir)
    result = controller.check_quality()
    
    controller.log_attempt(args.attempt, result)
    
    print(f"\n{'='*60}")
    print(f"Quality Check - Attempt {args.attempt}")
    print(f"{'='*60}")
    print(f"Score: {result.score:.2f}")
    print(f"Status: {'✓ PASSED' if result.passed else '✗ FAILED'}")
    
    if result.issues:
        print(f"\nIssues ({len(result.issues)}):")
        for issue in result.issues:
            print(f"  - {issue}")
    
    if not args.check_only and not result.passed:
        feedback = controller.generate_feedback_prompt(result, args.attempt)
        print(f"\n{feedback}")
    
    controller.save_attempt_log()
    
    return 0 if result.passed else 1

if __name__ == '__main__':
    exit(main())
