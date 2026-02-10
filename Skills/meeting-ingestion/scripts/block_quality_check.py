#!/usr/bin/env python3
"""
Block Quality Check for Meeting Intelligence System

Validates generated blocks meet quality standards with configurable thresholds.
Uses sensible defaults approved by V with documented rationale.

Usage:
    python3 block_quality_check.py <meeting_path> [--block B01] [--update-manifest] [--json]
    python3 block_quality_check.py <meeting_path> --check-all
    python3 block_quality_check.py <meeting_path> --status
    
Examples:
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John_x_Careerspan
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John_x_Careerspan --block B01 --update-manifest
    python3 block_quality_check.py Personal/Meetings/Inbox/2026-01-26_John_x_Careerspan --check-all --json
"""

import json
import os
import sys
import logging
import argparse
import re
import yaml
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Quality thresholds - documented rationale below
QUALITY_THRESHOLDS = {
    # Output length validation (words, excluding YAML frontmatter)
    "min_words": {
        # Detailed blocks need substantial content for external sharing
        "B01": 200,  # Detailed recap - comprehensive meeting summary
        "B28": 150,  # Strategic intelligence - requires depth for value
        "B08": 100,  # Stakeholder intelligence - needs detail for actionability
        
        # Standard blocks need moderate content 
        "B02": 50,   # Commitments - need specificity for accountability
        "B03": 50,   # Decisions - need context for understanding
        "B05": 50,   # Action items - need detail for execution
        "B06": 50,   # Business context - need depth for relevance
        "B07": 80,   # Warm intros - need personal touch, can't be generic
        "B10": 60,   # Relationship trajectory - needs nuance
        "B13": 60,   # Plan of action - needs specificity
        "B14": 40,   # Blurbs - concise but substantive
        "B21": 50,   # Key moments - need context to be meaningful
        "B33": 60,   # Decision rationale - needs reasoning depth
        
        # Metadata blocks need basic info
        "B25": 30,   # Deliverable map - structured list with owners
        "B26": 30,   # Meeting metadata - structured info
        
        # Internal blocks need moderate detail
        "B40": 40,   # Internal decisions - context for team
        "B41": 40,   # Team coordination - coordination details
        "B42": 40,   # Internal actions - execution clarity
        "B43": 40,   # Resource allocation - needs specifics
        "B44": 40,   # Process improvements - actionable detail
        "B45": 50,   # Team dynamics - requires sensitivity and depth
        "B46": 40,   # Knowledge transfer - clear info sharing
        "B47": 50,   # Open debates - needs nuance to capture tensions
        "B48": 60,   # Internal synthesis - strategic depth for leadership
        
        # Special blocks
        "B32": 40,   # Thought-provoking ideas - need development but can be concise
        "B00": 20,   # Deferred intents - simple list with context
        "B02_B05": 60,  # Combined block - needs substantial content
        
        # Default for any block not explicitly listed
        "default": 30
    },
    
    # Format compliance checks
    "format": {
        "requires_yaml_frontmatter": True,  # All blocks should have metadata
        "requires_h1_heading": True,        # Clear structure
        "min_sections": 1,                  # At least some organization
        "requires_markdown_structure": True  # Not just plain text
    },
    
    # Hallucination detection
    "hallucination": {
        "max_ai_markers": 0,               # No "As an AI..." or "I cannot access..."
        "max_impossible_details": 0,       # No future dates, non-participants
        "contradiction_threshold": 0.2     # <20% content contradicts other blocks
    },
    
    # Content accuracy (sampling approach)
    "accuracy": {
        "sample_claims_count": 3,          # Check 3 key claims per block
        "min_verifiable_ratio": 0.8,      # 80% of claims should be verifiable in transcript
        "fuzzy_match_threshold": 0.7      # Semantic similarity for claim verification
    },
    
    # Overall quality scoring (weighted average)
    "scoring": {
        "length_weight": 0.3,
        "format_weight": 0.25,
        "hallucination_weight": 0.25,
        "accuracy_weight": 0.2,
        "passing_score": 0.75  # Must score 75% to pass
    }
}

@dataclass
class QualityCheck:
    """Individual quality check result"""
    check_type: str
    passed: bool
    score: float
    details: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)

@dataclass 
class BlockQualityResult:
    """Quality assessment result for a single block"""
    block_code: str
    block_path: str
    overall_passed: bool
    overall_score: float
    checks: List[QualityCheck] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    needs_retry: bool = False
    needs_hitl: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_code": self.block_code,
            "block_path": self.block_path,
            "overall_passed": self.overall_passed,
            "overall_score": round(self.overall_score, 3),
            "checks": [asdict(check) for check in self.checks],
            "issues": self.issues,
            "needs_retry": self.needs_retry,
            "needs_hitl": self.needs_hitl
        }

@dataclass
class QualitySession:
    """Quality check session results"""
    meeting_path: str
    checked_blocks: List[BlockQualityResult] = field(default_factory=list)
    overall_passed: bool = False
    overall_score: float = 0.0
    low_confidence_blocks: List[str] = field(default_factory=list)
    flagged_for_retry: List[str] = field(default_factory=list)
    flagged_for_hitl: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_path": self.meeting_path,
            "overall_passed": self.overall_passed,
            "overall_score": round(self.overall_score, 3),
            "checked_blocks": [block.to_dict() for block in self.checked_blocks],
            "low_confidence_blocks": self.low_confidence_blocks,
            "flagged_for_retry": self.flagged_for_retry,
            "flagged_for_hitl": self.flagged_for_hitl,
            "summary": {
                "total_blocks": len(self.checked_blocks),
                "passed_blocks": sum(1 for b in self.checked_blocks if b.overall_passed),
                "failed_blocks": sum(1 for b in self.checked_blocks if not b.overall_passed),
                "retry_needed": len(self.flagged_for_retry),
                "hitl_needed": len(self.flagged_for_hitl)
            }
        }

class BlockQualityChecker:
    """Main quality checker implementation"""
    
    def __init__(self, meeting_path: str):
        self.meeting_path = Path(meeting_path).resolve()
        if not self.meeting_path.exists():
            raise FileNotFoundError(f"Meeting path not found: {meeting_path}")
            
        # Try new format first: {meeting_name}_[B]/ subdirectory
        self.blocks_dir = self.meeting_path / f"{self.meeting_path.name}_[B]"
        
        # If not found, check legacy format: blocks directly in meeting directory
        if not self.blocks_dir.exists():
            # Check if there are any B*.md files in the meeting directory
            direct_blocks = list(self.meeting_path.glob("B*.md"))
            if direct_blocks:
                self.blocks_dir = self.meeting_path  # Use meeting directory directly
                logger.info(f"Using legacy format: blocks in meeting directory")
            else:
                logger.debug(f"No blocks found in either format")
        else:
            logger.info(f"Using new format: blocks in {self.blocks_dir}")
            
        self.manifest_path = self.meeting_path / "manifest.json"
        
        logger.info(f"Initialized quality checker for: {self.meeting_path}")
        logger.debug(f"Blocks directory: {self.blocks_dir}")
        
    def check_block(self, block_code: str) -> BlockQualityResult:
        """Perform quality checks on a single block"""
        block_files = list(self.blocks_dir.glob(f"{block_code}_*.md"))
        
        if not block_files:
            return BlockQualityResult(
                block_code=block_code,
                block_path="",
                overall_passed=False,
                overall_score=0.0,
                issues=[f"Block file not found: {block_code}"],
                needs_retry=True
            )
            
        block_path = block_files[0]
        logger.debug(f"Checking block: {block_path}")
        
        try:
            with open(block_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return BlockQualityResult(
                block_code=block_code,
                block_path=str(block_path),
                overall_passed=False,
                overall_score=0.0,
                issues=[f"Failed to read block: {e}"],
                needs_hitl=True
            )
        
        checks = []
        
        # 1. Output length validation
        length_check = self._check_output_length(block_code, content)
        checks.append(length_check)
        
        # 2. Format compliance
        format_check = self._check_format_compliance(content)
        checks.append(format_check)
        
        # 3. Hallucination detection  
        hallucination_check = self._check_hallucination_markers(content)
        checks.append(hallucination_check)
        
        # 4. Content accuracy (sampling)
        accuracy_check = self._check_content_accuracy(content)
        checks.append(accuracy_check)
        
        # Calculate overall score
        weights = QUALITY_THRESHOLDS["scoring"]
        overall_score = (
            length_check.score * weights["length_weight"] +
            format_check.score * weights["format_weight"] +
            hallucination_check.score * weights["hallucination_weight"] +
            accuracy_check.score * weights["accuracy_weight"]
        )
        
        overall_passed = overall_score >= weights["passing_score"]
        
        # Determine remediation flags
        needs_retry = (
            not overall_passed and 
            overall_score >= 0.4 and  # In "warning" range
            not any("corruption" in issue.lower() or "encoding" in issue.lower() 
                   for check in checks for issue in check.issues)
        )
        
        needs_hitl = (
            not overall_passed and
            (overall_score < 0.4 or  # Very low confidence
             any("hallucination" in check.check_type and not check.passed for check in checks) or
             any("corruption" in issue.lower() for check in checks for issue in check.issues))
        )
        
        issues = []
        for check in checks:
            issues.extend(check.issues)
            
        return BlockQualityResult(
            block_code=block_code,
            block_path=str(block_path),
            overall_passed=overall_passed,
            overall_score=overall_score,
            checks=checks,
            issues=issues,
            needs_retry=needs_retry,
            needs_hitl=needs_hitl
        )
    
    def _check_output_length(self, block_code: str, content: str) -> QualityCheck:
        """Check if block meets minimum word count requirements"""
        # Remove YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Count words
        words = len(content.split())
        min_words = QUALITY_THRESHOLDS["min_words"].get(
            block_code, 
            QUALITY_THRESHOLDS["min_words"]["default"]
        )
        
        passed = words >= min_words
        score = min(1.0, words / min_words) if min_words > 0 else 1.0
        
        issues = []
        if not passed:
            issues.append(f"Block too short: {words} words < {min_words} minimum")
            
        return QualityCheck(
            check_type="output_length",
            passed=passed,
            score=score,
            details={
                "word_count": words,
                "minimum_required": min_words,
                "ratio": words / min_words if min_words > 0 else 1.0
            },
            issues=issues
        )
    
    def _check_format_compliance(self, content: str) -> QualityCheck:
        """Check if block follows expected markdown structure"""
        issues = []
        score_components = []
        
        # Check for YAML frontmatter
        has_yaml = content.startswith('---') and '\n---\n' in content
        score_components.append(1.0 if has_yaml else 0.0)
        if not has_yaml and QUALITY_THRESHOLDS["format"]["requires_yaml_frontmatter"]:
            issues.append("Missing YAML frontmatter")
            
        # Check for proper markdown headers
        has_h1 = bool(re.search(r'^#\s+', content, re.MULTILINE))
        score_components.append(1.0 if has_h1 else 0.0)
        if not has_h1 and QUALITY_THRESHOLDS["format"]["requires_h1_heading"]:
            issues.append("Missing H1 heading")
            
        # Check for structured content (not just paragraphs)
        has_structure = bool(re.search(r'(^#{2,}|\*\*|^\*|\|.*\||```)', content, re.MULTILINE))
        score_components.append(1.0 if has_structure else 0.0)
        if not has_structure and QUALITY_THRESHOLDS["format"]["requires_markdown_structure"]:
            issues.append("Lacks markdown structure (headers, lists, tables, etc.)")
            
        # Check minimum sections
        section_count = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        min_sections = QUALITY_THRESHOLDS["format"]["min_sections"]
        has_min_sections = section_count >= min_sections
        score_components.append(1.0 if has_min_sections else 0.0)
        if not has_min_sections:
            issues.append(f"Insufficient sections: {section_count} < {min_sections} minimum")
        
        overall_score = sum(score_components) / len(score_components)
        passed = overall_score >= 0.75  # Must pass 3/4 format checks
        
        return QualityCheck(
            check_type="format_compliance",
            passed=passed,
            score=overall_score,
            details={
                "has_yaml_frontmatter": has_yaml,
                "has_h1_heading": has_h1,
                "has_markdown_structure": has_structure,
                "section_count": section_count,
                "format_score_breakdown": score_components
            },
            issues=issues
        )
    
    def _check_hallucination_markers(self, content: str) -> QualityCheck:
        """Detect AI hallucination or fabricated content"""
        issues = []
        
        # Common AI meta-commentary patterns
        ai_markers = [
            r"as an ai",
            r"i cannot access",
            r"i don't have access",
            r"i'm not able to",
            r"i apologize",
            r"let me clarify",
            r"based on the information provided",
            r"according to the transcript",
            r"from what i can see"
        ]
        
        ai_marker_count = 0
        for pattern in ai_markers:
            matches = re.findall(pattern, content, re.IGNORECASE)
            ai_marker_count += len(matches)
            if matches:
                issues.append(f"AI marker detected: '{matches[0]}' ({len(matches)} occurrences)")
        
        # Check for impossible details (future dates beyond reasonable meeting scheduling)
        future_year_pattern = r'\b202[7-9]\b'  # Years beyond 2026 are suspicious
        future_matches = re.findall(future_year_pattern, content)
        if future_matches:
            issues.append(f"Suspicious future dates: {set(future_matches)}")
        
        # Meta-commentary about the AI process itself
        meta_patterns = [
            r"generated? for meeting",
            r"based on my analysis",
            r"here's? the .* block",
            r"analysis of this transcript"
        ]
        
        meta_count = 0
        for pattern in meta_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            meta_count += len(matches)
        
        # Score calculation
        max_ai_markers = QUALITY_THRESHOLDS["hallucination"]["max_ai_markers"]
        penalty = min(1.0, ai_marker_count / max(1, max_ai_markers + 2))  # Gradual penalty
        score = max(0.0, 1.0 - penalty)
        
        passed = (
            ai_marker_count <= max_ai_markers and
            not future_matches and
            meta_count <= 2  # Allow some meta-commentary but not excessive
        )
        
        if not passed and not issues:
            issues.append("High confidence hallucination detected")
        
        return QualityCheck(
            check_type="hallucination_detection",
            passed=passed,
            score=score,
            details={
                "ai_marker_count": ai_marker_count,
                "future_date_count": len(future_matches),
                "meta_commentary_count": meta_count,
                "penalty_applied": penalty
            },
            issues=issues
        )
    
    def _check_content_accuracy(self, content: str) -> QualityCheck:
        """Sample key claims and verify against transcript (simplified)"""
        # For the MVP, we'll do basic heuristics since full transcript verification 
        # requires loading and semantic matching which is expensive
        
        issues = []
        
        # Extract key claims (sentences with specific details)
        claim_patterns = [
            r'[A-Z][^.!?]*(?:decided?|agreed?|committed?|mentioned?)[^.!?]*[.!?]',
            r'[A-Z][^.!?]*(?:will|going to|plan to)[^.!?]*[.!?]',
            r'[A-Z][^.!?]*(?:\$\d+|by \w+day|\d+%)[^.!?]*[.!?]'
        ]
        
        claims = []
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            claims.extend(matches[:2])  # Limit to avoid too many
        
        # Basic plausibility checks
        implausible_count = 0
        
        # Check for overly specific details that seem fabricated
        suspicious_patterns = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # Overly precise timestamps
            r'exactly \d+\.\d{3}',  # Overly precise numbers
            r'\b[A-Z][a-z]+ [A-Z][a-z]+ said ".*" at \d+:\d+ (AM|PM)'  # Overly precise quotes
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content):
                implausible_count += 1
                issues.append(f"Overly specific detail pattern detected")
        
        # Check for internal consistency
        # Look for contradicting statements (simple version)
        contradictions = 0
        if "will not" in content.lower() and "will definitely" in content.lower():
            contradictions += 1
            issues.append("Potential internal contradiction detected")
        
        # Score based on plausibility
        total_issues = implausible_count + contradictions
        score = max(0.0, 1.0 - (total_issues * 0.3))  # Each issue reduces score by 30%
        
        # Pass if score is reasonable and no major red flags
        min_ratio = QUALITY_THRESHOLDS["accuracy"]["min_verifiable_ratio"]
        passed = score >= min_ratio and total_issues <= 2
        
        return QualityCheck(
            check_type="content_accuracy",
            passed=passed,
            score=score,
            details={
                "claims_sampled": len(claims),
                "implausible_patterns": implausible_count,
                "contradictions_detected": contradictions,
                "sample_claims": claims[:3]  # For debugging
            },
            issues=issues
        )
        
    def check_all_blocks(self) -> QualitySession:
        """Check quality for all blocks in the meeting"""
        if not self.blocks_dir.exists():
            logger.warning(f"No blocks directory found: {self.blocks_dir}")
            return QualitySession(
                meeting_path=str(self.meeting_path),
                overall_passed=False,
                overall_score=0.0
            )
            
        # Find all block files
        block_files = list(self.blocks_dir.glob("B*_*.md"))
        block_codes = []
        
        for block_file in block_files:
            # Extract block code from filename (e.g., "B01_DETAILED_RECAP.md" -> "B01")
            match = re.match(r'^(B\d+(?:_B\d+)?)', block_file.stem)
            if match:
                block_codes.append(match.group(1))
                
        logger.info(f"Found {len(block_codes)} blocks to check: {sorted(set(block_codes))}")
        
        session = QualitySession(meeting_path=str(self.meeting_path))
        
        for block_code in sorted(set(block_codes)):
            result = self.check_block(block_code)
            session.checked_blocks.append(result)
            
            # Track flagged blocks
            if result.needs_retry:
                session.flagged_for_retry.append(block_code)
            if result.needs_hitl:
                session.flagged_for_hitl.append(block_code)
            if result.overall_score < 0.6:  # Low confidence threshold
                session.low_confidence_blocks.append(block_code)
        
        # Calculate session-level metrics
        if session.checked_blocks:
            session.overall_score = sum(b.overall_score for b in session.checked_blocks) / len(session.checked_blocks)
            session.overall_passed = all(b.overall_passed for b in session.checked_blocks)
        
        return session
    
    def update_manifest(self, quality_results: QualitySession) -> bool:
        """Update manifest with quality results"""
        if not self.manifest_path.exists():
            logger.warning(f"Manifest not found: {self.manifest_path}")
            return False
            
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read manifest: {e}")
            return False
            
        # Update quality_gate section
        if "quality_gate" not in manifest:
            manifest["quality_gate"] = {}
            
        quality_gate = manifest["quality_gate"]
        
        # Update block-specific quality results
        if "block_quality" not in quality_gate:
            quality_gate["block_quality"] = {}
            
        quality_gate["block_quality"].update({
            "last_check": datetime.now(UTC).isoformat(),
            "overall_score": quality_results.overall_score,
            "overall_passed": quality_results.overall_passed,
            "blocks_checked": len(quality_results.checked_blocks),
            "blocks_passed": sum(1 for b in quality_results.checked_blocks if b.overall_passed),
            "low_confidence": quality_results.low_confidence_blocks,
            "retry_needed": quality_results.flagged_for_retry,
            "hitl_needed": quality_results.flagged_for_hitl,
            "per_block_scores": {
                b.block_code: {
                    "score": b.overall_score,
                    "passed": b.overall_passed,
                    "issues_count": len(b.issues)
                } for b in quality_results.checked_blocks
            }
        })
        
        # Update overall quality gate passed status
        existing_checks = quality_gate.get("checks", {})
        existing_checks["block_quality_passed"] = quality_results.overall_passed
        quality_gate["checks"] = existing_checks
        
        # Update overall score (average with existing checks)
        other_scores = []
        if "score" in quality_gate and quality_gate["score"] > 0:
            other_scores.append(quality_gate["score"])
        
        all_scores = other_scores + [quality_results.overall_score]
        quality_gate["score"] = sum(all_scores) / len(all_scores)
        
        # Update manifest timestamp
        manifest["last_updated_at"] = datetime.now(UTC).isoformat()
        
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logger.info(f"Updated manifest with quality results")
            return True
        except Exception as e:
            logger.error(f"Failed to write manifest: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Block Quality Check for Meeting Intelligence System")
    parser.add_argument("meeting_path", help="Path to meeting directory")
    parser.add_argument("--block", help="Check specific block (e.g., B01)")
    parser.add_argument("--check-all", action="store_true", help="Check all blocks in meeting")
    parser.add_argument("--update-manifest", action="store_true", help="Update manifest with results")
    parser.add_argument("--status", action="store_true", help="Show quality status")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        checker = BlockQualityChecker(args.meeting_path)
        
        if args.status:
            # Show current quality status from manifest
            if checker.manifest_path.exists():
                with open(checker.manifest_path, 'r') as f:
                    manifest = json.load(f)
                    
                quality_gate = manifest.get("quality_gate", {})
                block_quality = quality_gate.get("block_quality", {})
                
                if block_quality:
                    print(f"Quality Status for {checker.meeting_path.name}:")
                    print(f"  Overall Score: {block_quality.get('overall_score', 'N/A'):.3f}")
                    print(f"  Overall Passed: {block_quality.get('overall_passed', 'N/A')}")
                    print(f"  Blocks Checked: {block_quality.get('blocks_checked', 0)}")
                    print(f"  Blocks Passed: {block_quality.get('blocks_passed', 0)}")
                    
                    if block_quality.get('low_confidence'):
                        print(f"  Low Confidence: {', '.join(block_quality['low_confidence'])}")
                    if block_quality.get('retry_needed'):
                        print(f"  Retry Needed: {', '.join(block_quality['retry_needed'])}")
                    if block_quality.get('hitl_needed'):
                        print(f"  HITL Needed: {', '.join(block_quality['hitl_needed'])}")
                        
                    print(f"  Last Check: {block_quality.get('last_check', 'Never')}")
                else:
                    print("No quality check results found in manifest")
            else:
                print("Manifest not found")
            return
        
        # Perform quality checks
        if args.block:
            # Check single block
            result = checker.check_block(args.block)
            if args.json:
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(f"\nQuality Check Results for {args.block}:")
                print(f"  Path: {result.block_path}")
                print(f"  Overall Score: {result.overall_score:.3f}")
                print(f"  Overall Passed: {result.overall_passed}")
                
                for check in result.checks:
                    print(f"  {check.check_type}: {check.score:.3f} ({'PASS' if check.passed else 'FAIL'})")
                    if check.issues:
                        for issue in check.issues:
                            print(f"    - {issue}")
                            
                if result.needs_retry:
                    print("  → FLAGGED FOR RETRY")
                if result.needs_hitl:
                    print("  → FLAGGED FOR HITL")
                    
        else:
            # Check all blocks (default)
            session = checker.check_all_blocks()
            
            if args.update_manifest:
                updated = checker.update_manifest(session)
                if updated:
                    logger.info("Manifest updated with quality results")
                else:
                    logger.warning("Failed to update manifest")
            
            if args.json:
                print(json.dumps(session.to_dict(), indent=2))
            else:
                summary = session.to_dict()["summary"]
                print(f"\nQuality Check Summary for {checker.meeting_path.name}:")
                print(f"  Overall Score: {session.overall_score:.3f}")
                print(f"  Overall Passed: {session.overall_passed}")
                print(f"  Blocks Checked: {summary['total_blocks']}")
                print(f"  Passed: {summary['passed_blocks']}")
                print(f"  Failed: {summary['failed_blocks']}")
                
                if session.low_confidence_blocks:
                    print(f"  Low Confidence: {', '.join(session.low_confidence_blocks)}")
                if session.flagged_for_retry:
                    print(f"  Retry Recommended: {', '.join(session.flagged_for_retry)}")
                if session.flagged_for_hitl:
                    print(f"  HITL Required: {', '.join(session.flagged_for_hitl)}")
                    
                print(f"\nPer-Block Results:")
                for block in session.checked_blocks:
                    status = "PASS" if block.overall_passed else "FAIL"
                    flags = []
                    if block.needs_retry:
                        flags.append("RETRY")
                    if block.needs_hitl:
                        flags.append("HITL")
                    flag_str = f" [{', '.join(flags)}]" if flags else ""
                    
                    print(f"  {block.block_code}: {block.overall_score:.3f} {status}{flag_str}")
                    if block.issues:
                        for issue in block.issues[:2]:  # Show first 2 issues
                            print(f"    - {issue}")
                        if len(block.issues) > 2:
                            print(f"    ... and {len(block.issues) - 2} more issues")
                            
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()