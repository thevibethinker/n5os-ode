#!/usr/bin/env python3
"""
Meeting Output Validator
Validates meeting blocks and folder structure against quality standards
"""

import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

@dataclass
class ValidationResult:
    """Result of validation check"""
    passed: bool
    issues: List[str]
    score: float  # 0.0-1.0

class OutputValidator:
    """Validates meeting output quality"""
    
    def __init__(self, standards_path: Path = None):
        if standards_path is None:
            standards_path = Path("/home/workspace/N5/prefs/meeting_block_standards.yaml")
        
        with open(standards_path) as f:
            self.standards = yaml.safe_load(f)
    
    def validate_block_quality(self, block_path: Path) -> ValidationResult:
        """
        Validate quality of individual block file
        
        Args:
            block_path: Path to block markdown file
            
        Returns:
            ValidationResult with pass/fail and issues
        """
        issues = []
        
        if not block_path.exists():
            return ValidationResult(passed=False, issues=["Block file not found"], score=0.0)
        
        # Extract block type from filename
        match = re.match(r'B(\d{2})_([a-z_]+)\.md', block_path.name)
        if not match:
            issues.append(f"Invalid block filename: {block_path.name}")
            return ValidationResult(passed=False, issues=issues, score=0.0)
        
        block_num, block_slug = match.groups()
        block_key = f"B{block_num}_{block_slug}"
        
        # Get standards for this block type
        standards = self.standards.get('quality_standards', {}).get(block_key)
        if not standards:
            # No specific standards, basic validation only
            content = block_path.read_text()
            if len(content) < 100:
                issues.append("Block content too short (<100 chars)")
            return ValidationResult(
                passed=len(issues) == 0,
                issues=issues,
                score=1.0 if len(issues) == 0 else 0.5
            )
        
        content = block_path.read_text()
        score = 1.0
        
        # Check minimum length
        if 'min_length' in standards:
            if len(content) < standards['min_length']:
                issues.append(f"Content too short: {len(content)} < {standards['min_length']}")
                score -= 0.3
        
        # Check required sections
        if 'required_sections' in standards:
            for section in standards['required_sections']:
                if section.lower() not in content.lower():
                    issues.append(f"Missing required section: {section}")
                    score -= 0.2
        
        # Check required fields (for metadata)
        if 'required_fields' in standards:
            for field in standards['required_fields']:
                if field.lower() not in content.lower():
                    issues.append(f"Missing required field: {field}")
                    score -= 0.15
        
        # Check minimum items (for list-based blocks)
        if 'min_items' in standards:
            # Count list items (lines starting with -, *, or numbers)
            list_items = len(re.findall(r'^\s*[-*\d]+\.?\s+', content, re.MULTILINE))
            
            # Check for explicit "No X" statement
            accepts_none = standards.get('accepts_none', False)
            has_none_statement = bool(re.search(r'no\s+(commitments|questions|deliverables)', content, re.IGNORECASE))
            
            if list_items < standards['min_items'] and not (accepts_none and has_none_statement):
                issues.append(f"Insufficient items: {list_items} < {standards['min_items']}")
                score -= 0.3
        
        score = max(0.0, score)
        passed = len(issues) == 0 and score >= 0.7
        
        return ValidationResult(passed=passed, issues=issues, score=score)
    
    def validate_folder_structure(self, meeting_dir: Path) -> ValidationResult:
        """
        Validate meeting folder contains required blocks
        
        Args:
            meeting_dir: Path to meeting folder
            
        Returns:
            ValidationResult
        """
        issues = []
        score = 1.0
        
        if not meeting_dir.exists() or not meeting_dir.is_dir():
            return ValidationResult(passed=False, issues=["Meeting directory not found"], score=0.0)
        
        # Check mandatory blocks present
        mandatory_blocks = self.standards.get('core_blocks', {}).get('mandatory', [])
        block_files = list(meeting_dir.glob("B*.md"))
        
        present_blocks = {f.stem[:3] for f in block_files}
        
        for required in mandatory_blocks:
            if required not in present_blocks:
                issues.append(f"Missing mandatory block: {required}")
                score -= 0.25
        
        # Check for forbidden filenames (old format)
        forbidden = self.standards.get('block_naming', {}).get('forbidden', [])
        for forbidden_name in forbidden:
            if (meeting_dir / forbidden_name).exists():
                issues.append(f"Found forbidden filename: {forbidden_name}")
                score -= 0.1
        
        score = max(0.0, score)
        passed = len(issues) == 0 and score >= 0.8
        
        return ValidationResult(passed=passed, issues=issues, score=score)
    
    def validate_folder_name(self, folder_name: str) -> Tuple[bool, str]:
        """
        Validate folder name meets standards
        
        Args:
            folder_name: Name of meeting folder
            
        Returns:
            (is_valid, suggested_name_if_invalid)
        """
        standards = self.standards.get('folder_naming', {})
        
        # Check for forbidden patterns (Fireflies codes)
        for pattern in standards.get('forbidden_patterns', []):
            if re.search(pattern, folder_name):
                return (False, "Contains forbidden pattern (Fireflies code)")
        
        # Check length
        max_length = standards.get('max_length', 100)
        if len(folder_name) > max_length:
            return (False, f"Too long (>{max_length} chars)")
        
        # Check allowed characters
        allowed = standards.get('allowed_chars', 'a-zA-Z0-9_-')
        pattern = f'^[{allowed}]+$'
        if not re.match(pattern, folder_name):
            return (False, "Contains invalid characters")
        
        return (True, "")
    
    def validate_meeting_complete(self, meeting_dir: Path) -> ValidationResult:
        """
        Complete validation of meeting output
        
        Args:
            meeting_dir: Path to meeting folder
            
        Returns:
            Aggregated ValidationResult
        """
        all_issues = []
        scores = []
        
        # Validate folder name
        is_valid_name, name_issue = self.validate_folder_name(meeting_dir.name)
        if not is_valid_name:
            all_issues.append(f"Folder name issue: {name_issue}")
            scores.append(0.7)
        
        # Validate folder structure
        structure_result = self.validate_folder_structure(meeting_dir)
        all_issues.extend(structure_result.issues)
        scores.append(structure_result.score)
        
        # Validate individual blocks
        block_files = list(meeting_dir.glob("B*.md"))
        for block_file in block_files:
            block_result = self.validate_block_quality(block_file)
            if not block_result.passed:
                all_issues.extend([f"{block_file.name}: {issue}" for issue in block_result.issues])
            scores.append(block_result.score)
        
        # Calculate aggregate
        avg_score = sum(scores) / len(scores) if scores else 0.0
        overall_threshold = self.standards.get('validation_thresholds', {}).get('overall_pass_rate', 0.75)
        
        passed = avg_score >= overall_threshold and len(all_issues) == 0
        
        return ValidationResult(passed=passed, issues=all_issues, score=avg_score)

    def _check_b26(self, content: str, standards: Dict) -> List[str]:
        """Check B26 metadata block"""
        issues = []
        
        # Check for required sections
        required_sections = standards.get("required_sections", [])
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing required section: {section}")
        
        # Check for required fields in Basic Information section
        required_fields = standards.get("required_fields_in_basic", [])
        for field in required_fields:
            # Look for field patterns like "**Meeting ID:**" or "**Date:**"
            pattern = f"**{field}:**"
            if pattern not in content and f"{field}:" not in content:
                issues.append(f"Missing required field: {field}")
        
        return issues

def main():
    """CLI interface for validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate meeting output quality")
    parser.add_argument("meeting_dir", type=Path, help="Path to meeting directory")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    
    args = parser.parse_args()
    
    validator = OutputValidator()
    result = validator.validate_meeting_complete(args.meeting_dir)
    
    print(f"\nValidation Result: {'✓ PASSED' if result.passed else '✗ FAILED'}")
    print(f"Score: {result.score:.2f}")
    
    if result.issues:
        print(f"\nIssues ({len(result.issues)}):")
        for issue in result.issues:
            print(f"  - {issue}")
    
    return 0 if result.passed else 1

if __name__ == '__main__':
    exit(main())
