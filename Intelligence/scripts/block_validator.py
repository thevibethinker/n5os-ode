#!/usr/bin/env python3
"""
Block Content Validator (Worker 4)

Validates generated block content against rubrics with quality scoring
and actionable feedback for retry loops.

Usage:
    from Intelligence.scripts import block_validator
    
    result = block_validator.validate_block(
        content="# Generated Content...",
        rubric={"required_sections": ["## Summary"]},
        generation_id=123
    )
    
    if not result["valid"]:
        print(result["feedback"])
"""

import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import database layer
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from Intelligence.scripts import block_db


# ============================================================================
# VALIDATION CHECKS
# ============================================================================

def check_required_sections(content: str, sections: List[str]) -> Dict[str, Any]:
    """Check if required markdown sections are present"""
    missing = []
    for section in sections:
        # Support both exact match and regex pattern
        if section.startswith("##"):
            # Exact heading match
            pattern = re.escape(section)
        else:
            # Treat as regex
            pattern = section
        
        if not re.search(pattern, content, re.MULTILINE):
            missing.append(section)
    
    passed = len(missing) == 0
    message = "All required sections present" if passed else f"Missing sections: {', '.join(missing)}"
    
    return {
        "passed": passed,
        "message": message,
        "details": {"missing": missing}
    }


def check_no_placeholders(content: str, forbidden: Optional[List[str]] = None) -> Dict[str, Any]:
    """Check for placeholder text that indicates incomplete content"""
    default_patterns = [
        r'\bTBD\b',
        r'\bTODO\b',
        r'\[Insert\b',
        r'\[Add\b',
        r'\[Fill in\b',
        r'\.\.\.(?!\w)',  # Ellipsis not part of word
        r'\[X+\]',        # [XXX] style markers
        r'<placeholder>',
        r'PLACEHOLDER',
    ]
    
    if forbidden:
        patterns = default_patterns + [re.escape(p) if not p.startswith('r"') else p.strip('r"') for p in forbidden]
    else:
        patterns = default_patterns
    
    found_placeholders = []
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Get context (20 chars before and after)
            start = max(0, match.start() - 20)
            end = min(len(content), match.end() + 20)
            context = content[start:end].replace('\n', ' ')
            found_placeholders.append({
                "pattern": pattern,
                "match": match.group(),
                "context": context
            })
    
    passed = len(found_placeholders) == 0
    message = "No placeholders found" if passed else f"Found {len(found_placeholders)} placeholder(s)"
    
    return {
        "passed": passed,
        "message": message,
        "details": {"placeholders": found_placeholders}
    }


def check_min_length(content: str, min_chars: int) -> Dict[str, Any]:
    """Check if content meets minimum length requirement"""
    # Strip whitespace for accurate count
    stripped = content.strip()
    char_count = len(stripped)
    
    passed = char_count >= min_chars
    message = f"Content length: {char_count} chars" if passed else f"Too short: {char_count}/{min_chars} chars"
    
    return {
        "passed": passed,
        "message": message,
        "details": {"char_count": char_count, "required": min_chars}
    }


def check_structure(content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Check structural requirements"""
    issues = []
    
    # Must start with heading
    if rules.get("must_start_with_heading", False):
        if not re.match(r'^\s*#', content):
            issues.append("Content must start with a markdown heading")
    
    # Require bullet points
    if rules.get("require_bullet_points", False):
        if not re.search(r'^\s*[-*+]\s', content, re.MULTILINE):
            issues.append("Content must include bullet points")
    
    # Require numbered lists
    if rules.get("require_numbered_list", False):
        if not re.search(r'^\s*\d+\.\s', content, re.MULTILINE):
            issues.append("Content must include numbered list")
    
    # No excessive empty lines
    if rules.get("no_excessive_whitespace", True):
        if re.search(r'\n\n\n\n+', content):
            issues.append("Excessive empty lines detected")
    
    # Must have paragraphs
    if rules.get("require_paragraphs", False):
        # Look for text blocks (not headings, not lists)
        paragraphs = re.findall(r'^(?!#|\s*[-*+\d])[A-Z].{30,}$', content, re.MULTILINE)
        if not paragraphs:
            issues.append("Content must include paragraph text")
    
    passed = len(issues) == 0
    message = "Structure valid" if passed else f"{len(issues)} structural issue(s)"
    
    return {
        "passed": passed,
        "message": message,
        "details": {"issues": issues}
    }


def check_completeness(content: str) -> Dict[str, Any]:
    """Check if content appears complete (heuristic)"""
    issues = []
    
    # Check for abrupt endings
    if not re.search(r'[.!?]\s*$', content.strip()):
        issues.append("Content may be incomplete (doesn't end with punctuation)")
    
    # Check for very short sections
    sections = re.split(r'\n## ', content)
    for i, section in enumerate(sections[1:], 1):  # Skip preamble
        if len(section.strip()) < 50:
            heading = section.split('\n')[0]
            issues.append(f"Section '{heading}' is very short")
    
    passed = len(issues) == 0
    message = "Content appears complete" if passed else "Completeness concerns"
    
    return {
        "passed": passed,
        "message": message,
        "details": {"issues": issues}
    }


# ============================================================================
# QUALITY SCORING
# ============================================================================

def calculate_quality_score(checks: Dict[str, Dict]) -> float:
    """Calculate overall quality score (0-100) from check results"""
    if not checks:
        return 0.0
    
    # Weight different check types
    weights = {
        "required_sections": 30.0,
        "no_placeholders": 25.0,
        "min_length": 15.0,
        "structure": 20.0,
        "completeness": 10.0
    }
    
    total_weight = 0.0
    earned_score = 0.0
    
    for check_name, result in checks.items():
        weight = weights.get(check_name, 10.0)
        total_weight += weight
        
        if result["passed"]:
            earned_score += weight
        else:
            # Partial credit for some checks
            if check_name == "min_length":
                details = result.get("details", {})
                actual = details.get("char_count", 0)
                required = details.get("required", 1)
                ratio = min(actual / required, 1.0)
                earned_score += weight * ratio
    
    score = (earned_score / total_weight * 100.0) if total_weight > 0 else 0.0
    return round(score, 2)


# ============================================================================
# FEEDBACK GENERATION
# ============================================================================

def generate_feedback(checks: Dict[str, Dict], rubric: Dict) -> str:
    """Generate actionable feedback for content improvement"""
    feedback_parts = []
    
    # Prioritize critical failures
    critical_failures = []
    minor_issues = []
    
    for check_name, result in checks.items():
        if not result["passed"]:
            if check_name in ["required_sections", "no_placeholders"]:
                critical_failures.append((check_name, result))
            else:
                minor_issues.append((check_name, result))
    
    if critical_failures:
        feedback_parts.append("**Critical Issues:**")
        for check_name, result in critical_failures:
            feedback_parts.append(f"- {result['message']}")
            
            # Add specific guidance
            if check_name == "required_sections":
                missing = result["details"].get("missing", [])
                if missing:
                    feedback_parts.append(f"  → Add these sections: {', '.join(missing)}")
            
            elif check_name == "no_placeholders":
                placeholders = result["details"].get("placeholders", [])
                if placeholders:
                    feedback_parts.append(f"  → Replace placeholder text with actual content")
                    for ph in placeholders[:3]:  # Show first 3
                        feedback_parts.append(f"    • \"{ph['match']}\" in: ...{ph['context']}...")
    
    if minor_issues:
        feedback_parts.append("\n**Improvements Needed:**")
        for check_name, result in minor_issues:
            feedback_parts.append(f"- {result['message']}")
            
            # Add specific guidance
            if check_name == "structure":
                issues = result["details"].get("issues", [])
                for issue in issues:
                    feedback_parts.append(f"  → {issue}")
            
            elif check_name == "completeness":
                issues = result["details"].get("issues", [])
                for issue in issues:
                    feedback_parts.append(f"  → {issue}")
    
    if not feedback_parts:
        return "Content passes all validation checks."
    
    return "\n".join(feedback_parts)


# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================

def validate_block(
    content: str,
    rubric: Dict[str, Any],
    generation_id: Optional[int] = None,
    block_id: Optional[str] = None,
    log_to_db: bool = True
) -> Dict[str, Any]:
    """
    Validate block content against rubric
    
    Args:
        content: Generated markdown content to validate
        rubric: Validation criteria (JSON dict)
        generation_id: Optional DB reference for logging
        block_id: Optional block ID for logging
        log_to_db: Whether to log results to database
    
    Returns:
        {
            "valid": bool,
            "score": float (0-100),
            "feedback": str,
            "checks": dict of check results
        }
    """
    checks = {}
    
    # Run validation checks based on rubric
    if "required_sections" in rubric and rubric["required_sections"]:
        checks["required_sections"] = check_required_sections(
            content, 
            rubric["required_sections"]
        )
    
    if "forbidden_patterns" in rubric:
        checks["no_placeholders"] = check_no_placeholders(
            content,
            rubric.get("forbidden_patterns")
        )
    else:
        # Always check for common placeholders
        checks["no_placeholders"] = check_no_placeholders(content)
    
    if "min_length" in rubric:
        checks["min_length"] = check_min_length(
            content,
            rubric["min_length"]
        )
    
    if "structure_rules" in rubric:
        checks["structure"] = check_structure(
            content,
            rubric["structure_rules"]
        )
    
    # Always check completeness
    checks["completeness"] = check_completeness(content)
    
    # Calculate score
    score = calculate_quality_score(checks)
    
    # Determine if valid (all critical checks pass + score >= 70)
    critical_passed = all(
        checks[name]["passed"] 
        for name in ["required_sections", "no_placeholders"] 
        if name in checks
    )
    valid = critical_passed and score >= 70.0
    
    # Generate feedback
    feedback = generate_feedback(checks, rubric)
    
    result = {
        "valid": valid,
        "score": score,
        "feedback": feedback,
        "checks": checks
    }
    
    # Log to database if requested
    if log_to_db and generation_id and block_id:
        try:
            failures = [
                name for name, check in checks.items() 
                if not check["passed"]
            ]
            
            block_db.log_validation(
                generation_id=generation_id,
                block_id=block_id,
                validation_type="rubric",
                status="pass" if valid else "fail",
                score=score,
                criteria_checked=list(checks.keys()),
                failures=failures,
                warnings=None,
                validator_version="1.0"
            )
        except Exception as e:
            # Don't fail validation if DB logging fails
            print(f"Warning: Failed to log validation to database: {e}")
    
    return result


# ============================================================================
# RUBRIC UTILITIES
# ============================================================================

def load_rubric_from_db(block_id: str) -> Optional[Dict]:
    """Load validation rubric from database"""
    block = block_db.get_block(block_id)
    if not block:
        return None
    
    rubric_json = block.get("validation_rubric")
    if not rubric_json:
        return None
    
    try:
        return json.loads(rubric_json)
    except json.JSONDecodeError:
        return None


def get_default_rubric() -> Dict:
    """Return default rubric for blocks without specific requirements"""
    return {
        "required_sections": [],
        "forbidden_patterns": None,  # Use defaults
        "min_length": 100,
        "structure_rules": {
            "must_start_with_heading": True,
            "no_excessive_whitespace": True
        }
    }


# ============================================================================
# TESTING / CLI
# ============================================================================

if __name__ == "__main__":
    # Test with sample content
    sample_content = """# Test Block

## Summary
This is a test block with some content.

## Details
- Point 1
- Point 2
- Point 3

This has enough content to pass validation.
"""

    sample_rubric = {
        "required_sections": ["## Summary", "## Details"],
        "min_length": 50,
        "structure_rules": {
            "must_start_with_heading": True,
            "require_bullet_points": True
        }
    }
    
    result = validate_block(
        content=sample_content,
        rubric=sample_rubric,
        log_to_db=False
    )
    
    print("Validation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Score: {result['score']}")
    print(f"\nFeedback:")
    print(result['feedback'])
    print(f"\nChecks:")
    for name, check in result['checks'].items():
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {name}: {check['message']}")
