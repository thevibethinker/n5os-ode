#!/usr/bin/env python3
"""
Block Quality Check for Meeting Intelligence System

Validates generated meeting blocks meet quality standards as defined in the 
quality harness specification. Checks output length, format compliance, 
hallucination markers, and content accuracy.

Part of the meeting-system-v3 build - implements quality validation for 
generated blocks with configurable thresholds and manifest integration.

Usage:
    python3 block_quality_check.py <meeting_path> [--check-blocks B01,B02] [--json]
    python3 block_quality_check.py <meeting_path> --retry-failed
    python3 block_quality_check.py <meeting_path> --status

Examples:
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John --check-blocks B01,B08
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John --json
"""

import json
import os
import sys
import logging
import argparse
import re
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Quality check thresholds (V approved defaults with rationale)

# Block Length Thresholds (words)
# Rationale: Based on block complexity and expected information density
# B01 is comprehensive recap, others are targeted extracts
BLOCK_LENGTH_THRESHOLDS = {
    "B00": 30,  # Deferred intents - typically short action items
    "B01": 200, # Detailed recap - comprehensive summary requires depth
    "B02": 50,  # Commitments - specific but may have multiple items
    "B02_B05": 80,  # Combined commitments+actions - more content
    "B03": 50,  # Decisions - specific but context needed
    "B04": 40,  # Open questions - may be brief but should have detail
    "B05": 50,  # Action items - specific with owners/deadlines
    "B06": 60,  # Business context - strategic insights need detail
    "B07": 100, # Warm intros - draft emails need substance
    "B08": 80,  # Stakeholder intelligence - insights about people
    "B10": 60,  # Relationship trajectory - analysis requires depth
    "B13": 70,  # Plan of action - coordinated approach needs detail
    "B14": 60,  # Blurbs - marketing copy needs polish
    "B21": 50,  # Key moments - quotes and context
    "B25": 50,  # Deliverables - specific items with owners
    "B26": 30,  # Metadata - structured info, can be brief
    "B28": 80,  # Strategic intelligence - long-term insights
    "B32": 50,  # Ideas - novel concepts need explanation
    "B33": 70,  # Decision rationale - reasoning needs depth
    # Internal blocks (B40+) - team-focused, can be more concise
    "B40": 40,  # Internal decisions
    "B41": 40,  # Team coordination
    "B42": 40,  # Internal actions
    "B43": 40,  # Resource allocation
    "B44": 40,  # Process improvements
    "B45": 40,  # Team dynamics
    "B46": 40,  # Knowledge transfer
    "B47": 50,  # Open debates - need context for resolution
    "B48": 60,  # Internal synthesis - strategic for leadership
}

# Confidence thresholds for quality scoring
# Rationale: Based on processing risk and V's tolerance for false positives
CONFIDENCE_THRESHOLDS = {
    "pass": 0.8,       # Blocks must score 80% to pass (high bar for quality)
    "warning": 0.6,    # 60-80% triggers warning but passes (flag for review)
    "fail": 0.6,       # Below 60% fails quality check (needs regeneration)
    "hitl_escalate": 0.4  # Below 40% requires human review (systematic issues)
}

# Hallucination markers - phrases that indicate AI meta-commentary or fabrication
# Rationale: These patterns indicate the AI broke role and added non-transcript content
HALLUCINATION_PATTERNS = [
    r"(?i)I cannot access",
    r"(?i)As an AI",
    r"(?i)I don't have access to",
    r"(?i)Based on the transcript provided",
    r"(?i)The transcript shows",
    r"(?i)From what I can see in the transcript",
    r"(?i)Looking at the meeting transcript",
    r"(?i)\[Note: This is generated content\]",
    r"(?i)\[AI GENERATED\]",
    r"(?i)Unfortunately, I cannot",
    r"(?i)I'm unable to",
    r"(?i)Please note that",
    r"(?i)It's important to note that",
    r"(?i)I should mention",
    r"(?i)Let me clarify",
]

@dataclass 
class QualityCheckResult:
    """Result of a quality check on a single block."""
    block_code: str
    block_name: str
    check_type: str
    passed: bool
    score: float
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

@dataclass
class BlockQualityReport:
    """Complete quality assessment for a single block."""
    block_code: str
    block_name: str
    file_path: str
    overall_passed: bool
    overall_score: float
    word_count: int
    checks: List[QualityCheckResult] = field(default_factory=list)
    needs_regeneration: bool = False
    needs_hitl_review: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.needs_hitl_review:
            return "HITL_REQUIRED"
        elif self.needs_regeneration:
            return "REGENERATION_NEEDED"
        elif not self.overall_passed:
            return "FAILED"
        elif self.overall_score < CONFIDENCE_THRESHOLDS["warning"]:
            return "WARNING"
        else:
            return "PASSED"

@dataclass
class QualitySession:
    """Track quality checking session across multiple blocks."""
    meeting_path: str
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    block_reports: List[BlockQualityReport] = field(default_factory=list)
    
    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.block_reports if r.overall_passed)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.block_reports if not r.overall_passed)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.block_reports if r.overall_score < CONFIDENCE_THRESHOLDS["warning"])
    
    @property 
    def hitl_count(self) -> int:
        return sum(1 for r in self.block_reports if r.needs_hitl_review)


def extract_block_code_from_filename(filename: str) -> Optional[str]:
    """Extract block code from filename like B01_DETAILED_RECAP.md -> B01"""
    # Handle both B01.md and B01_DETAILED_RECAP.md formats
    match = re.match(r'(B\d{2}(?:_B\d{2})?)', filename)
    if match:
        return match.group(1)
    return None


def count_words_in_markdown(content: str) -> int:
    """Count words in markdown content, excluding YAML frontmatter and headers."""
    # Remove YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Remove markdown headers (# ## ###)
    content = re.sub(r'^#+\s+.*$', '', content, flags=re.MULTILINE)
    
    # Remove markdown formatting but keep content
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
    content = re.sub(r'`(.*?)`', r'\1', content)        # Code
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links
    
    # Count words
    words = content.strip().split()
    return len([w for w in words if w.strip()])


def check_block_output_length(block_code: str, content: str) -> QualityCheckResult:
    """Check if block contains sufficient content."""
    word_count = count_words_in_markdown(content)
    min_words = BLOCK_LENGTH_THRESHOLDS.get(block_code, 50)  # Default 50 words
    
    if word_count >= min_words:
        score = min(1.0, word_count / (min_words * 1.5))  # Full score at 1.5x minimum
        return QualityCheckResult(
            block_code=block_code,
            block_name=f"{block_code}_CHECK",
            check_type="output_length",
            passed=True,
            score=score,
            message=f"Sufficient length: {word_count} words (min: {min_words})",
            details={"word_count": word_count, "threshold": min_words}
        )
    else:
        score = word_count / min_words  # Proportional score below threshold
        return QualityCheckResult(
            block_code=block_code,
            block_name=f"{block_code}_CHECK",
            check_type="output_length",
            passed=False,
            score=score,
            message=f"Insufficient length: {word_count} words (min: {min_words})",
            details={"word_count": word_count, "threshold": min_words}
        )


def check_block_format_compliance(block_code: str, content: str) -> QualityCheckResult:
    """Check if block follows expected markdown structure."""
    issues = []
    score = 1.0
    
    # Check for YAML frontmatter (optional but preferred)
    has_frontmatter = content.startswith('---') and content.count('---') >= 2
    if not has_frontmatter:
        issues.append("Missing YAML frontmatter")
        score -= 0.2
    
    # Check for proper heading structure
    has_main_heading = bool(re.search(r'^#\s+\w+', content, re.MULTILINE))
    if not has_main_heading:
        issues.append("Missing main heading")
        score -= 0.3
    
    # Check it's not just plain paragraph text (should have some structure)
    has_structure = bool(re.search(r'^##\s+\w+|^\*\s+|-\s+|\d+\.\s+', content, re.MULTILINE))
    if not has_structure and len(content) > 200:
        issues.append("Lacks structured format (no subheadings, bullets, or lists)")
        score -= 0.2
    
    # Check for obvious formatting issues
    if '```markdown' in content:
        issues.append("Contains markdown code blocks (should be direct content)")
        score -= 0.3
        
    score = max(0.0, score)
    passed = score >= 0.6  # 60% threshold for format compliance
    
    message = "Well-formatted block"
    if issues:
        message = f"Format issues: {', '.join(issues)}"
    
    return QualityCheckResult(
        block_code=block_code,
        block_name=f"{block_code}_CHECK",
        check_type="format_compliance",
        passed=passed,
        score=score,
        message=message,
        details={"issues": issues, "has_frontmatter": has_frontmatter}
    )


def check_no_hallucination_markers(block_code: str, content: str) -> QualityCheckResult:
    """Check for AI hallucination or meta-commentary markers."""
    detected_patterns = []
    
    for pattern in HALLUCINATION_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            detected_patterns.extend(matches)
    
    if detected_patterns:
        # Hallucination is a serious issue - low score
        score = 0.2
        return QualityCheckResult(
            block_code=block_code,
            block_name=f"{block_code}_CHECK",
            check_type="no_hallucination_markers",
            passed=False,
            score=score,
            message=f"Detected AI meta-commentary: {detected_patterns[0][:50]}...",
            details={"detected_patterns": detected_patterns}
        )
    else:
        return QualityCheckResult(
            block_code=block_code,
            block_name=f"{block_code}_CHECK",
            check_type="no_hallucination_markers",
            passed=True,
            score=1.0,
            message="No hallucination markers detected",
            details={"detected_patterns": []}
        )


def check_content_structure(block_code: str, content: str) -> QualityCheckResult:
    """Check that content has appropriate structure for the block type."""
    score = 1.0
    issues = []
    
    # Block-specific structure checks
    if block_code in ["B02", "B05", "B02_B05"]:  # Action/commitment blocks
        # Should have actionable items - look for bullets, owners, dates
        has_bullets = bool(re.search(r'^\s*[-*+]\s+', content, re.MULTILINE))
        has_owners = bool(re.search(r'@\w+|owner:|assigned:|responsible:', content, re.IGNORECASE))
        
        if not has_bullets and len(content) > 100:
            issues.append("Expected bullet points or list format for actions")
            score -= 0.2
            
        if not has_owners and len(content) > 100:
            issues.append("Expected owner assignments for actionable items")
            score -= 0.1
    
    elif block_code == "B01":  # Detailed recap
        # Should have chronological or topical organization
        has_sections = bool(re.search(r'^##\s+', content, re.MULTILINE))
        if not has_sections and len(content) > 300:
            issues.append("Expected section organization for detailed recap")
            score -= 0.2
    
    elif block_code in ["B07"]:  # Warm introductions
        # Should look like email drafts
        has_email_structure = bool(re.search(r'Subject:|Dear|Hi \w+|Best regards|Sincerely', content, re.IGNORECASE))
        if not has_email_structure:
            issues.append("Expected email format for warm introduction")
            score -= 0.3
    
    # General structure checks
    if len(content) > 500:  # Only for longer blocks
        # Should not be just one giant paragraph
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        if paragraph_count < 2:
            issues.append("Long content should be broken into paragraphs")
            score -= 0.1
    
    score = max(0.0, score)
    passed = score >= 0.7  # 70% threshold for structure
    
    message = "Well-structured content" if not issues else f"Structure issues: {', '.join(issues)}"
    
    return QualityCheckResult(
        block_code=block_code,
        block_name=f"{block_code}_CHECK", 
        check_type="content_structure",
        passed=passed,
        score=score,
        message=message,
        details={"issues": issues}
    )


def assess_block_quality(block_path: Path, transcript_content: Optional[str] = None) -> BlockQualityReport:
    """Run all quality checks on a single block file."""
    block_code = extract_block_code_from_filename(block_path.name)
    if not block_code:
        # Return failed report for unparseable filename
        return BlockQualityReport(
            block_code="UNKNOWN",
            block_name=block_path.name,
            file_path=str(block_path),
            overall_passed=False,
            overall_score=0.0,
            word_count=0,
            checks=[QualityCheckResult(
                block_code="UNKNOWN",
                block_name=block_path.name,
                check_type="filename_parse",
                passed=False,
                score=0.0,
                message=f"Cannot parse block code from filename: {block_path.name}"
            )],
            needs_regeneration=True
        )
    
    try:
        content = block_path.read_text(encoding='utf-8')
    except Exception as e:
        return BlockQualityReport(
            block_code=block_code,
            block_name=block_path.name,
            file_path=str(block_path),
            overall_passed=False,
            overall_score=0.0,
            word_count=0,
            checks=[QualityCheckResult(
                block_code=block_code,
                block_name=block_path.name,
                check_type="file_read",
                passed=False,
                score=0.0,
                message=f"Cannot read file: {str(e)}"
            )],
            needs_regeneration=True
        )
    
    word_count = count_words_in_markdown(content)
    
    # Run all quality checks
    checks = [
        check_block_output_length(block_code, content),
        check_block_format_compliance(block_code, content),
        check_no_hallucination_markers(block_code, content),
        check_content_structure(block_code, content)
    ]
    
    # Calculate overall score (average of all checks)
    overall_score = sum(check.score for check in checks) / len(checks)
    overall_passed = overall_score >= CONFIDENCE_THRESHOLDS["fail"]
    
    # Determine escalation needs
    needs_regeneration = overall_score < CONFIDENCE_THRESHOLDS["fail"]
    needs_hitl_review = overall_score < CONFIDENCE_THRESHOLDS["hitl_escalate"]
    
    # Special case: hallucination always needs regeneration
    hallucination_check = next((c for c in checks if c.check_type == "no_hallucination_markers"), None)
    if hallucination_check and not hallucination_check.passed:
        needs_regeneration = True
        # Severe hallucination needs HITL
        if hallucination_check.score < 0.3:
            needs_hitl_review = True
    
    return BlockQualityReport(
        block_code=block_code,
        block_name=block_path.name,
        file_path=str(block_path),
        overall_passed=overall_passed,
        overall_score=overall_score,
        word_count=word_count,
        checks=checks,
        needs_regeneration=needs_regeneration,
        needs_hitl_review=needs_hitl_review
    )


def find_generated_blocks(meeting_path: Path, block_codes: Optional[List[str]] = None) -> List[Path]:
    """Find all generated block files in meeting directory."""
    if block_codes:
        # Look for specific blocks
        block_files = []
        for code in block_codes:
            # Try multiple filename patterns
            patterns = [
                f"{code}.md",
                f"{code}_*.md", 
                f"*{code}*.md"
            ]
            for pattern in patterns:
                files = list(meeting_path.glob(pattern))
                block_files.extend(files)
        return block_files
    else:
        # Find all block files (B##*.md pattern)
        return list(meeting_path.glob("B*.md"))


def update_manifest_with_quality_results(manifest_path: Path, quality_session: QualitySession):
    """Update meeting manifest with quality check results."""
    if not manifest_path.exists():
        logger.warning(f"Manifest not found: {manifest_path}")
        return
    
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as e:
        logger.error(f"Cannot read manifest: {e}")
        return
    
    # Initialize quality_check section if not exists
    if "quality_check" not in manifest:
        manifest["quality_check"] = {}
    
    # Update quality check results
    quality_results = {
        "last_checked_at": quality_session.started_at,
        "overall_status": "passed" if quality_session.failed_count == 0 else "failed",
        "blocks_checked": len(quality_session.block_reports),
        "blocks_passed": quality_session.passed_count,
        "blocks_failed": quality_session.failed_count,
        "blocks_warning": quality_session.warning_count,
        "blocks_need_hitl": quality_session.hitl_count,
        "block_results": []
    }
    
    for report in quality_session.block_reports:
        quality_results["block_results"].append({
            "block_code": report.block_code,
            "file_name": Path(report.file_path).name,
            "passed": report.overall_passed,
            "score": round(report.overall_score, 3),
            "status": report.status,
            "word_count": report.word_count,
            "needs_regeneration": report.needs_regeneration,
            "needs_hitl_review": report.needs_hitl_review,
            "check_details": [
                {
                    "check_type": check.check_type,
                    "passed": check.passed,
                    "score": round(check.score, 3),
                    "message": check.message
                }
                for check in report.checks
            ]
        })
    
    manifest["quality_check"] = quality_results
    
    # Update blocks_failed if there are quality failures
    if quality_session.failed_count > 0:
        if "blocks_failed" not in manifest:
            manifest["blocks_failed"] = []
        
        # Add/update failed blocks from quality check
        failed_block_names = {Path(r.file_path).name for r in quality_session.block_reports if not r.overall_passed}
        
        for failed_name in failed_block_names:
            # Check if already in failed list
            existing = False
            for failed_entry in manifest["blocks_failed"]:
                if isinstance(failed_entry, dict) and failed_entry.get("block") == failed_name:
                    # Update existing entry
                    failed_entry["error"] = "Quality check failed"
                    failed_entry["last_attempt"] = quality_session.started_at
                    existing = True
                    break
                elif failed_entry == failed_name:
                    existing = True
                    break
            
            if not existing:
                manifest["blocks_failed"].append({
                    "block": failed_name,
                    "error": "Quality check failed",
                    "last_attempt": quality_session.started_at
                })
    
    # Save updated manifest
    try:
        manifest_path.write_text(json.dumps(manifest, indent=2))
        logger.info(f"Updated manifest with quality results: {quality_session.passed_count}/{len(quality_session.block_reports)} passed")
    except Exception as e:
        logger.error(f"Cannot save manifest: {e}")


def show_quality_status(meeting_path: Path):
    """Show quality status for blocks in meeting."""
    manifest_path = meeting_path / "manifest.json"
    
    print(f"\n=== Block Quality Status: {meeting_path.name} ===\n")
    
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            quality_data = manifest.get("quality_check", {})
            
            if quality_data:
                print(f"Last checked: {quality_data.get('last_checked_at', 'Never')}")
                print(f"Overall status: {quality_data.get('overall_status', 'Unknown')}")
                print(f"Blocks checked: {quality_data.get('blocks_checked', 0)}")
                print(f"Passed: {quality_data.get('blocks_passed', 0)}")
                print(f"Failed: {quality_data.get('blocks_failed', 0)}")
                print(f"Warnings: {quality_data.get('blocks_warning', 0)}")
                print(f"Need HITL: {quality_data.get('blocks_need_hitl', 0)}")
                
                block_results = quality_data.get("block_results", [])
                if block_results:
                    print(f"\nBlock Details:")
                    for result in block_results:
                        status_icon = "✓" if result["passed"] else "✗"
                        print(f"  {status_icon} {result['file_name']}: {result['status']} (score: {result['score']:.2f})")
                        
                        if not result["passed"]:
                            for check in result.get("check_details", []):
                                if not check["passed"]:
                                    print(f"    - {check['check_type']}: {check['message']}")
            else:
                print("No quality checks have been run.")
        except Exception as e:
            print(f"Cannot read manifest: {e}")
    else:
        print("No manifest.json found.")
    
    # Show current block files
    block_files = find_generated_blocks(meeting_path)
    if block_files:
        print(f"\nGenerated block files ({len(block_files)}):")
        for bf in sorted(block_files):
            print(f"  {bf.name}")
    else:
        print("\nNo generated block files found.")


def quality_check_blocks(
    meeting_path: Path,
    block_codes: Optional[List[str]] = None,
    update_manifest: bool = True
) -> QualitySession:
    """Run quality checks on generated blocks."""
    
    session = QualitySession(meeting_path=str(meeting_path))
    
    # Find blocks to check
    block_files = find_generated_blocks(meeting_path, block_codes)
    
    if not block_files:
        if block_codes:
            logger.warning(f"No blocks found for codes: {block_codes}")
        else:
            logger.warning("No generated block files found")
        return session
    
    logger.info(f"Checking quality of {len(block_files)} blocks in {meeting_path.name}")
    
    # Load transcript for context (optional - used by future checks)
    transcript_content = None
    try:
        # Try to find transcript file
        for pattern in ["transcript.md", "*transcript*.md", "*.md"]:
            transcript_files = list(meeting_path.glob(pattern))
            if transcript_files:
                # Prefer files with 'transcript' in name
                transcript_file = next((f for f in transcript_files if 'transcript' in f.name.lower()), transcript_files[0])
                transcript_content = transcript_file.read_text()
                break
    except Exception:
        pass  # Transcript is optional for current checks
    
    # Run quality checks on each block
    for block_file in sorted(block_files):
        logger.info(f"  Checking: {block_file.name}")
        report = assess_block_quality(block_file, transcript_content)
        session.block_reports.append(report)
        
        # Log results
        if report.overall_passed:
            logger.info(f"    ✓ {report.status} (score: {report.overall_score:.2f})")
        else:
            logger.warning(f"    ✗ {report.status} (score: {report.overall_score:.2f})")
            for check in report.checks:
                if not check.passed:
                    logger.warning(f"      - {check.check_type}: {check.message}")
    
    # Update manifest with results
    if update_manifest:
        manifest_path = meeting_path / "manifest.json"
        update_manifest_with_quality_results(manifest_path, session)
    
    logger.info(f"\nQuality check complete: {session.passed_count}/{len(session.block_reports)} blocks passed")
    
    if session.hitl_count > 0:
        logger.warning(f"⚠️  {session.hitl_count} blocks need HITL review")
    
    if session.failed_count > 0:
        logger.warning(f"⚠️  {session.failed_count} blocks failed quality checks")
    
    return session


def main():
    parser = argparse.ArgumentParser(
        description="Block Quality Check - validate generated meeting blocks meet quality standards"
    )
    parser.add_argument("meeting_path", help="Path to meeting folder")
    parser.add_argument("--check-blocks", type=str, help="Comma-separated block codes to check (B01,B08)")
    parser.add_argument("--retry-failed", action="store_true", help="Re-check previously failed blocks")
    parser.add_argument("--status", action="store_true", help="Show quality status and exit")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--no-manifest-update", action="store_true", help="Don't update manifest with results")
    
    args = parser.parse_args()
    
    meeting_path = Path(args.meeting_path)
    if not meeting_path.is_absolute():
        meeting_path = Path("/home/workspace") / meeting_path
    
    if not meeting_path.exists():
        print(f"Error: Path not found: {meeting_path}")
        return 1
    
    if args.status:
        show_quality_status(meeting_path)
        return 0
    
    block_codes = None
    if args.check_blocks:
        block_codes = [b.strip().upper() for b in args.check_blocks.split(",")]
    elif args.retry_failed:
        # Get failed blocks from manifest
        manifest_path = meeting_path / "manifest.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                quality_data = manifest.get("quality_check", {})
                failed_blocks = [
                    r["block_code"] for r in quality_data.get("block_results", [])
                    if not r.get("passed", True)
                ]
                if failed_blocks:
                    block_codes = failed_blocks
                    logger.info(f"Retrying failed blocks: {', '.join(failed_blocks)}")
                else:
                    logger.info("No previously failed blocks to retry")
                    return 0
            except Exception as e:
                logger.error(f"Cannot read manifest for failed blocks: {e}")
                return 1
    
    try:
        session = quality_check_blocks(
            meeting_path=meeting_path,
            block_codes=block_codes,
            update_manifest=not args.no_manifest_update
        )
        
        if args.json:
            output = {
                "meeting_path": str(meeting_path),
                "started_at": session.started_at,
                "blocks_checked": len(session.block_reports),
                "blocks_passed": session.passed_count,
                "blocks_failed": session.failed_count,
                "blocks_warning": session.warning_count,
                "blocks_need_hitl": session.hitl_count,
                "overall_passed": session.failed_count == 0,
                "block_reports": [
                    {
                        "block_code": r.block_code,
                        "file_name": Path(r.file_path).name,
                        "passed": r.overall_passed,
                        "score": round(r.overall_score, 3),
                        "status": r.status,
                        "word_count": r.word_count,
                        "needs_regeneration": r.needs_regeneration,
                        "needs_hitl_review": r.needs_hitl_review
                    }
                    for r in session.block_reports
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nQuality Check Summary:")
            print(f"  Meeting: {meeting_path.name}")
            print(f"  Blocks checked: {len(session.block_reports)}")
            print(f"  Passed: {session.passed_count}")
            print(f"  Failed: {session.failed_count}")
            print(f"  Warnings: {session.warning_count}")
            print(f"  Need HITL: {session.hitl_count}")
            
            if session.failed_count > 0:
                print(f"\nFailed blocks:")
                for r in session.block_reports:
                    if not r.overall_passed:
                        print(f"  ✗ {r.block_name}: {r.status} (score: {r.overall_score:.2f})")
                        
                print(f"\nRecommendation: Run block regeneration for failed blocks")
        
        return 0 if session.failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        if args.json:
            print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())