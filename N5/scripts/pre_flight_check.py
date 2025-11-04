#!/usr/bin/env python3
"""
Pre-Flight Check System: Verify requests before execution.
Catches ambiguity, assesses risk, enforces clarification.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class CheckResult(Enum):
    PROCEED = "proceed"
    CLARIFY = "clarify"
    BLOCK = "block"

@dataclass
class AmbiguityPattern:
    term: str
    variants: List[str]
    clarification: str
    risk_level: str  # low, medium, high

# Ambiguity database
AMBIGUOUS_PATTERNS = [
    AmbiguityPattern(
        term="delete",
        variants=["remove", "drop", "clear", "purge", "erase"],
        clarification="What exactly should be deleted? (files/database records/calendar events/other)",
        risk_level="high"
    ),
    AmbiguityPattern(
        term="fix",
        variants=["repair", "correct", "update", "resolve"],
        clarification="What specific behavior needs fixing? (error/performance/style/logic)",
        risk_level="medium"
    ),
    AmbiguityPattern(
        term="optimize",
        variants=["improve", "enhance", "speed up", "make better"],
        clarification="Optimize for what metric? (speed/memory/readability/maintainability)",
        risk_level="medium"
    ),
    AmbiguityPattern(
        term="everything",
        variants=["all", "entire", "whole", "complete"],
        clarification="Please specify exact scope (which files/directories/components)",
        risk_level="high"
    ),
    AmbiguityPattern(
        term="meetings",
        variants=["events", "appointments", "calendar items"],
        clarification="Which system? (database table/Google Calendar/meeting files/other)",
        risk_level="high"
    ),
    AmbiguityPattern(
        term="update",
        variants=["change", "modify", "edit", "revise"],
        clarification="Update what specifically? (version/content/structure/configuration)",
        risk_level="medium"
    ),
]

DESTRUCTIVE_KEYWORDS = [
    "delete", "remove", "drop", "clear", "purge", "erase",
    "truncate", "destroy", "wipe", "reset", "overwrite"
]

VAGUE_SCOPE_KEYWORDS = [
    "everything", "all", "entire", "whole", "complete",
    "any", "every", "each", "total"
]

class PreFlightChecker:
    def __init__(self, workspace: Path):
        self.workspace = workspace
    
    def check_request(self, request: str, context: dict = None) -> Tuple[CheckResult, Dict]:
        """
        Main pre-flight check.
        Returns: (result, details)
        """
        request_lower = request.lower()
        issues = []
        
        # Check 1: Ambiguity detection
        ambiguity = self.detect_ambiguity(request_lower)
        if ambiguity:
            issues.append({
                'type': 'ambiguity',
                'severity': ambiguity['risk_level'],
                'pattern': ambiguity['term'],
                'clarification': ambiguity['clarification']
            })
        
        # Check 2: Destructive operation detection
        if self.is_destructive(request_lower):
            blast_radius = self.assess_blast_radius(request, context or {})
            if blast_radius['risk'] in ['medium', 'high', 'critical']:
                issues.append({
                    'type': 'destructive',
                    'severity': blast_radius['risk'],
                    'impact': blast_radius['impact'],
                    'affected': blast_radius['affected_count']
                })
        
        # Check 3: Vague scope detection
        if self.has_vague_scope(request_lower):
            issues.append({
                'type': 'vague_scope',
                'severity': 'high',
                'clarification': 'Please specify exact scope and boundaries'
            })
        
        # Determine result
        if not issues:
            return (CheckResult.PROCEED, {})
        
        # Block on critical issues
        critical_issues = [i for i in issues if i['severity'] in ['high', 'critical']]
        if critical_issues:
            return (CheckResult.CLARIFY, {'issues': issues})
        
        # Clarify on medium issues
        return (CheckResult.CLARIFY, {'issues': issues})
    
    def detect_ambiguity(self, request: str) -> Optional[Dict]:
        """
        Check if request contains ambiguous terms.
        """
        for pattern in AMBIGUOUS_PATTERNS:
            # Check main term
            if re.search(r'\b' + pattern.term + r'\b', request):
                return {
                    'term': pattern.term,
                    'clarification': pattern.clarification,
                    'risk_level': pattern.risk_level
                }
            # Check variants
            for variant in pattern.variants:
                if re.search(r'\b' + variant + r'\b', request):
                    return {
                        'term': pattern.term,
                        'clarification': pattern.clarification,
                        'risk_level': pattern.risk_level
                    }
        return None
    
    def is_destructive(self, request: str) -> bool:
        """
        Check if request contains destructive keywords.
        """
        for keyword in DESTRUCTIVE_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', request):
                return True
        return False
    
    def has_vague_scope(self, request: str) -> bool:
        """
        Check if request has vague scope.
        """
        for keyword in VAGUE_SCOPE_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', request):
                return True
        return False
    
    def assess_blast_radius(self, request: str, context: dict) -> Dict:
        """
        Estimate impact of destructive operation.
        """
        # Simple heuristics for now
        affected_count = context.get('affected_count', 0)
        
        if affected_count == 0:
            # Unknown scope
            return {
                'risk': 'high',
                'impact': 'Unknown scope - potential for widespread damage',
                'affected_count': 'unknown'
            }
        elif affected_count > 10:
            return {
                'risk': 'high',
                'impact': f'Affects {affected_count} items',
                'affected_count': affected_count
            }
        elif affected_count > 5:
            return {
                'risk': 'medium',
                'impact': f'Affects {affected_count} items',
                'affected_count': affected_count
            }
        else:
            return {
                'risk': 'low',
                'impact': f'Affects {affected_count} items',
                'affected_count': affected_count
            }

def format_clarification_response(issues: List[Dict]) -> str:
    """
    Format issues as clarification request.
    """
    lines = ["⚠️ PRE-FLIGHT CHECK: Clarification needed\n"]
    
    for i, issue in enumerate(issues, 1):
        lines.append(f"{i}. **{issue['type'].upper()}** (Severity: {issue['severity']})")
        
        if issue['type'] == 'ambiguity':
            lines.append(f"   Ambiguous term: '{issue['pattern']}'")
            lines.append(f"   → {issue['clarification']}")
        
        elif issue['type'] == 'destructive':
            lines.append(f"   Destructive operation detected")
            lines.append(f"   Impact: {issue['impact']}")
            lines.append(f"   → Please confirm scope and provide explicit permission")
        
        elif issue['type'] == 'vague_scope':
            lines.append(f"   Scope is unclear")
            lines.append(f"   → {issue['clarification']}")
        
        lines.append("")
    
    lines.append("Please clarify before I proceed.")
    return "\n".join(lines)

def main():
    """
    CLI interface for testing.
    """
    if len(sys.argv) < 2:
        print("Usage: python3 pre_flight_check.py <request> [--context affected_count=N]")
        return 1
    
    request = sys.argv[1]
    context = {}
    
    # Parse context args
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            try:
                context[key] = int(value)
            except ValueError:
                context[key] = value
    
    checker = PreFlightChecker(Path.cwd())
    result, details = checker.check_request(request, context)
    
    if result == CheckResult.PROCEED:
        print("✓ PRE-FLIGHT CHECK PASSED: Proceed with request")
        return 0
    
    elif result == CheckResult.CLARIFY:
        print(format_clarification_response(details['issues']))
        return 1
    
    elif result == CheckResult.BLOCK:
        print("⛔ PRE-FLIGHT CHECK FAILED: Request blocked")
        for issue in details['issues']:
            print(f"  - {issue['type']}: {issue['severity']}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
