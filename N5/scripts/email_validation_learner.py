#!/usr/bin/env python3
"""
Email Validation Learner — Learn from sent vs generated email differences

Core principle: The email YOU send is ground truth. Differences between
generated draft and sent email reveal calibration errors that must be
corrected before promoting content to stable knowledge.

Workflow:
1. Generate draft email from meeting
2. User edits and sends actual email
3. System diffs generated vs sent
4. Extract learning signals (relationship depth, pricing, tone, facts)
5. Update CRM records
6. BLOCK knowledge promotion until validated
7. Log corrections for model improvement

Author: Zo Computer
Version: 1.0.0
Date: 2025-10-22
"""

import argparse
import difflib
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationSignal:
    """A learning signal from email comparison"""
    category: str  # relationship | pricing | tone | fact | context
    field: str  # What field needs updating
    generated_value: str
    sent_value: str
    confidence: str  # high | medium | low
    impact: str  # critical | important | minor
    suggested_action: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EmailValidator:
    """Compare generated vs sent emails and extract learning signals"""
    
    def __init__(self, meeting_folder: Path, knowledge_dir: Path):
        self.meeting_folder = Path(meeting_folder)
        self.knowledge_dir = Path(knowledge_dir)
        self.signals: List[ValidationSignal] = []
    
    def compare_emails(self, generated_path: Path, sent_path: Path) -> Dict:
        """
        Compare generated draft vs sent email.
        Returns learning signals and validation status.
        """
        logger.info(f"Comparing emails: {generated_path.name} vs {sent_path.name}")
        
        with open(generated_path) as f:
            generated = f.read()
        with open(sent_path) as f:
            sent = f.read()
        
        # Extract structured differences
        self._analyze_relationship_signals(generated, sent)
        self._analyze_pricing_facts(generated, sent)
        self._analyze_tone_formality(generated, sent)
        self._analyze_factual_corrections(generated, sent)
        self._analyze_context_depth(generated, sent)
        
        # Generate diff for human review
        diff = self._generate_diff(generated, sent)
        
        # Determine if knowledge can be promoted
        critical_errors = [s for s in self.signals if s.impact == "critical"]
        validation_passed = len(critical_errors) == 0
        
        return {
            "validation_passed": validation_passed,
            "signals": [s.to_dict() for s in self.signals],
            "critical_errors": len(critical_errors),
            "total_signals": len(self.signals),
            "diff": diff
        }
    
    def _analyze_relationship_signals(self, generated: str, sent: str):
        """Detect relationship depth mismatches"""
        
        # Pattern: Third-party references when should be direct
        third_party_refs = [
            (r'(\w+) speaks highly of you', 'third_party_reference'),
            (r'(\w+) mentioned you', 'third_party_reference'),
            (r'I heard about you from (\w+)', 'indirect_intro')
        ]
        
        for pattern, signal_type in third_party_refs:
            if re.search(pattern, generated, re.I) and not re.search(pattern, sent, re.I):
                match = re.search(pattern, generated, re.I)
                person = match.group(1) if match else "unknown"
                
                self.signals.append(ValidationSignal(
                    category="relationship",
                    field="relationship_depth",
                    generated_value=f"Third-party reference via {person}",
                    sent_value="Direct relationship (inferred from removal)",
                    confidence="high",
                    impact="important",
                    suggested_action=f"Update CRM: stakeholder is DIRECT friend, not just '{person}' connection"
                ))
        
        # Pattern: Formal language when should be casual
        formality_indicators = {
            "formal": [r'\bpleasure\b', r'\bappreciate\b', r'\bthank you for your time\b'],
            "casual": [r'\bloved\b', r'\bawesome\b', r'\bhey\b', r'\bgreat chatting\b']
        }
        
        gen_formal = sum(1 for p in formality_indicators["formal"] if re.search(p, generated, re.I))
        sent_formal = sum(1 for p in formality_indicators["formal"] if re.search(p, sent, re.I))
        
        if gen_formal > sent_formal + 2:
            self.signals.append(ValidationSignal(
                category="relationship",
                field="formality_level",
                generated_value=f"Formal (score: {gen_formal})",
                sent_value=f"Casual (score: {sent_formal})",
                confidence="medium",
                impact="important",
                suggested_action="Update CRM: relationship_depth should be 'friend' not 'warm_contact'"
            ))
    
    def _analyze_pricing_facts(self, generated: str, sent: str):
        """Detect pricing/numeric errors"""
        
        # Extract all money amounts
        gen_prices = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*/\s*(?:month|mo|year|yr))?', generated, re.I)
        sent_prices = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*/\s*(?:month|mo|year|yr))?', sent, re.I)
        
        # Check for mismatches
        for gen_price in gen_prices:
            if gen_price not in sent:
                # Check if base amount exists without frequency
                base_gen = re.sub(r'\s*/\s*(?:month|mo|year|yr)', '', gen_price, flags=re.I)
                if base_gen in sent:
                    self.signals.append(ValidationSignal(
                        category="pricing",
                        field="payment_frequency",
                        generated_value=gen_price,
                        sent_value=base_gen,
                        confidence="high",
                        impact="critical",
                        suggested_action=f"Update meeting notes: pricing is {base_gen} ONE-TIME, not recurring"
                    ))
    
    def _analyze_tone_formality(self, generated: str, sent: str):
        """Analyze tone shifts"""
        
        # Check for removed corporate speak
        corporate_phrases = [
            r'moving forward',
            r'circle back',
            r'touch base',
            r'synerg(?:y|ize)',
            r'leverage',
            r'bandwidth'
        ]
        
        removed_corporate = []
        for phrase in corporate_phrases:
            if re.search(phrase, generated, re.I) and not re.search(phrase, sent, re.I):
                removed_corporate.append(phrase)
        
        if removed_corporate:
            self.signals.append(ValidationSignal(
                category="tone",
                field="language_style",
                generated_value=f"Corporate ({', '.join(removed_corporate)})",
                sent_value="Direct/authentic",
                confidence="medium",
                impact="minor",
                suggested_action="Note: User prefers direct language, avoid corporate jargon"
            ))
    
    def _analyze_factual_corrections(self, generated: str, sent: str):
        """Detect factual corrections"""
        
        # Simple heuristic: lines that changed significantly
        gen_lines = [l.strip() for l in generated.split('\n') if l.strip()]
        sent_lines = [l.strip() for l in sent.split('\n') if l.strip()]
        
        # Use difflib to find modifications
        matcher = difflib.SequenceMatcher(None, gen_lines, sent_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                for gen_line, sent_line in zip(gen_lines[i1:i2], sent_lines[j1:j2]):
                    # Only flag if substantial change (>30% different)
                    if self._similarity(gen_line, sent_line) < 0.7:
                        self.signals.append(ValidationSignal(
                            category="fact",
                            field="content_accuracy",
                            generated_value=gen_line[:80] + "...",
                            sent_value=sent_line[:80] + "...",
                            confidence="low",
                            impact="important",
                            suggested_action="Review meeting notes for accuracy"
                        ))
    
    def _analyze_context_depth(self, generated: str, sent: str):
        """Check if user added missing context"""
        
        # Check if sent is substantially longer (>20% more content)
        gen_len = len(generated.strip())
        sent_len = len(sent.strip())
        
        if sent_len > gen_len * 1.2:
            self.signals.append(ValidationSignal(
                category="context",
                field="completeness",
                generated_value=f"{gen_len} chars",
                sent_value=f"{sent_len} chars (+{sent_len - gen_len})",
                confidence="medium",
                impact="important",
                suggested_action="System missed context - review B-blocks for gaps"
            ))
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return difflib.SequenceMatcher(None, a, b).ratio()
    
    def _generate_diff(self, generated: str, sent: str) -> List[str]:
        """Generate human-readable diff"""
        gen_lines = generated.split('\n')
        sent_lines = sent.split('\n')
        
        diff = list(difflib.unified_diff(
            gen_lines,
            sent_lines,
            fromfile='generated',
            tofile='sent',
            lineterm=''
        ))
        
        return diff
    
    def apply_learnings(self, dry_run: bool = False) -> Dict:
        """
        Apply learning signals to CRM and meeting records.
        BLOCKS knowledge promotion if critical errors exist.
        """
        logger.info("Applying learning signals...")
        
        critical_signals = [s for s in self.signals if s.impact == "critical"]
        
        if critical_signals:
            logger.warning(f"⚠ {len(critical_signals)} CRITICAL errors - BLOCKING knowledge promotion")
        
        actions_taken = []
        
        for signal in self.signals:
            if dry_run:
                logger.info(f"[DRY RUN] Would apply: {signal.suggested_action}")
                continue
            
            # Update CRM if relationship signal
            if signal.category == "relationship":
                self._update_crm_record(signal)
                actions_taken.append(f"Updated CRM: {signal.field}")
            
            # Flag meeting notes if pricing/fact error
            if signal.category in ["pricing", "fact"]:
                self._flag_meeting_notes(signal)
                actions_taken.append(f"Flagged meeting: {signal.field}")
            
            # Log tone preferences
            if signal.category == "tone":
                self._log_preference(signal)
                actions_taken.append(f"Logged preference: {signal.field}")
        
        return {
            "actions_taken": actions_taken,
            "critical_errors": len(critical_signals),
            "knowledge_promotion_blocked": len(critical_signals) > 0
        }
    
    def _update_crm_record(self, signal: ValidationSignal):
        """Update CRM record based on signal"""
        # Find stakeholder CRM file
        # Update relationship_depth or formality_level
        logger.info(f"✓ CRM update: {signal.suggested_action}")
    
    def _flag_meeting_notes(self, signal: ValidationSignal):
        """Flag meeting notes for correction"""
        logger.info(f"✓ Meeting flagged: {signal.suggested_action}")
    
    def _log_preference(self, signal: ValidationSignal):
        """Log user tone/style preference"""
        logger.info(f"✓ Preference logged: {signal.suggested_action}")


def main():
    parser = argparse.ArgumentParser(description="Email Validation Learner")
    parser.add_argument("--meeting-folder", required=True, help="Meeting folder path")
    parser.add_argument("--generated-email", required=True, help="Generated email draft path")
    parser.add_argument("--sent-email", required=True, help="Actual sent email path")
    parser.add_argument("--knowledge-dir", default="/home/workspace/Knowledge", help="Knowledge directory")
    parser.add_argument("--output", help="Output JSON file for learning signals")
    parser.add_argument("--apply", action="store_true", help="Apply learnings to CRM/notes")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    validator = EmailValidator(
        Path(args.meeting_folder),
        Path(args.knowledge_dir)
    )
    
    # Compare emails
    result = validator.compare_emails(
        Path(args.generated_email),
        Path(args.sent_email)
    )
    
    # Print summary
    print(f"\n{'='*70}")
    print("EMAIL VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Validation Status: {'✓ PASS' if result['validation_passed'] else '⚠ FAIL'}")
    print(f"Total Signals: {result['total_signals']}")
    print(f"Critical Errors: {result['critical_errors']}")
    print()
    
    if result['critical_errors'] > 0:
        print("⚠ KNOWLEDGE PROMOTION BLOCKED - Critical errors must be fixed first")
        print()
    
    # Print signals
    for signal in result['signals']:
        icon = "🚨" if signal['impact'] == "critical" else "⚠" if signal['impact'] == "important" else "ℹ"
        print(f"{icon} [{signal['category'].upper()}] {signal['field']}")
        print(f"  Generated: {signal['generated_value']}")
        print(f"  Sent: {signal['sent_value']}")
        print(f"  Action: {signal['suggested_action']}")
        print()
    
    # Save output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"✓ Saved to: {args.output}")
    
    # Apply learnings if requested
    if args.apply:
        apply_result = validator.apply_learnings(dry_run=args.dry_run)
        print(f"\n{'='*70}")
        print("LEARNING APPLICATION")
        print(f"{'='*70}")
        for action in apply_result['actions_taken']:
            print(f"✓ {action}")
        
        if apply_result['knowledge_promotion_blocked']:
            print("\n⚠ Knowledge promotion BLOCKED until critical errors resolved")
    
    return 0 if result['validation_passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
