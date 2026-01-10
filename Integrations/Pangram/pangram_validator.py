#!/usr/bin/env python3
"""
Pangram Validator Module

Provides validation functions for integration with other systems.
Used by X Thought Leader, follow-up email generator, etc.
"""

import os
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class PangramResult:
    """Result from Pangram AI detection."""
    fraction_ai: float
    fraction_human: float
    passed: bool
    threshold: float
    segments: list[dict]
    raw_response: dict
    
    @property
    def ai_percent(self) -> int:
        return int(self.fraction_ai * 100)
    
    @property
    def human_percent(self) -> int:
        return int(self.fraction_human * 100)


class PangramValidator:
    """Validate text against Pangram AI detection API."""
    
    API_URL = "https://text.api.pangram.com/v3"
    DEFAULT_THRESHOLD = 0.3  # 30% AI max to pass
    
    def __init__(self, api_key: Optional[str] = None, threshold: float = DEFAULT_THRESHOLD):
        self.api_key = api_key or os.environ.get("PANGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("PANGRAM_API_KEY not found in environment")
        self.threshold = threshold
    
    def check(self, text: str) -> PangramResult:
        """
        Check text against Pangram API.
        
        Returns PangramResult with pass/fail status.
        """
        response = requests.post(
            self.API_URL,
            headers={"x-api-key": self.api_key},
            json={"text": text},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        fraction_ai = data.get("fraction_ai", 1.0)
        fraction_human = data.get("fraction_human", 0.0)
        
        # Extract segment-level data
        segments = []
        for window in data.get("windows", []):
            segments.append({
                "text": window.get("text", ""),
                "ai_score": window.get("ai_assistance_score", 0),
                "start": window.get("start_index", 0),
                "end": window.get("end_index", 0),
                "confidence": window.get("confidence", "Unknown")
            })
        
        return PangramResult(
            fraction_ai=fraction_ai,
            fraction_human=fraction_human,
            passed=fraction_ai < self.threshold,
            threshold=self.threshold,
            segments=segments,
            raw_response=data
        )
    
    def validate_and_flag(self, text: str) -> tuple[bool, str, Optional[PangramResult]]:
        """
        Validate text and return (passed, message, result).
        
        Use this for simple integrations:
            passed, msg, result = validator.validate_and_flag(text)
            if not passed:
                # Handle failure
        """
        try:
            result = self.check(text)
            if result.passed:
                return True, f"✓ PASS ({result.ai_percent}% AI)", result
            else:
                return False, f"✗ FAIL ({result.ai_percent}% AI, threshold {int(self.threshold*100)}%)", result
        except Exception as e:
            return False, f"✗ ERROR: {e}", None
    
    def get_problem_segments(self, result: PangramResult, min_ai_score: float = 0.5) -> list[dict]:
        """Get segments with high AI scores for targeted fixes."""
        return [s for s in result.segments if s["ai_score"] >= min_ai_score]
    
    def suggest_fixes(self, result: PangramResult) -> list[str]:
        """
        Suggest fixes based on Pangram results.
        
        Based on empirically-validated patterns from pangram-signals.md.
        """
        suggestions = []
        
        if result.ai_percent >= 70:
            suggestions.append("Add specific numbers or dollar amounts")
            suggestions.append("Vary sentence length dramatically (include 2-4 word sentences)")
            suggestions.append("Break template structure with organic filler")
            suggestions.append("Replace generic references with specifics")
        
        if result.ai_percent >= 50:
            suggestions.append("Add one personality marker (profanity, self-deprecation, parenthetical)")
            suggestions.append("Check for formulaic intro patterns")
        
        # Check for specific segment issues
        problem_segments = self.get_problem_segments(result)
        if problem_segments:
            suggestions.append(f"Focus on fixing {len(problem_segments)} high-AI segments")
        
        return suggestions


# Convenience function for one-shot validation
def validate_text(text: str, threshold: float = 0.3) -> tuple[bool, str]:
    """
    Quick validation check.
    
    Returns (passed: bool, message: str)
    
    Usage:
        passed, msg = validate_text("Your text here")
        if not passed:
            print(f"Failed Pangram check: {msg}")
    """
    try:
        validator = PangramValidator(threshold=threshold)
        passed, msg, _ = validator.validate_and_flag(text)
        return passed, msg
    except Exception as e:
        return False, f"Error: {e}"


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        passed, msg = validate_text(text)
        print(msg)
        sys.exit(0 if passed else 1)
    else:
        print("Usage: python pangram_validator.py <text>")
        sys.exit(1)

