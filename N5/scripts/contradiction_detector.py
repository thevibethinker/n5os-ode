#!/usr/bin/env python3
"""
Contradiction Detector CLI for N5 Learnings

Detects contradictions between new learnings and existing ones using:
1. Semantic similarity (sentence-transformers)
2. Pattern-based contradiction signals
3. LLM verification for ambiguous cases

Usage:
    python3 contradiction_detector.py check "new learning text"
    python3 contradiction_detector.py scan
    python3 contradiction_detector.py scan --build <slug>
    python3 contradiction_detector.py compare "text A" "text B"
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import requests

# Learnings paths
SYSTEM_LEARNINGS_PATH = "/home/workspace/N5/learnings/SYSTEM_LEARNINGS.json"
BUILDS_PATH = "/home/workspace/N5/builds"


class ContradictionDetector:
    """Detects contradictions in learnings using semantic similarity and pattern matching."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize detector with sentence transformer model."""
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        
    def get_embedding(self, text: str) -> List[float]:
        """Get sentence embedding for text."""
        return self.model.encode(text)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        import numpy as np
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
    
    def load_system_learnings(self) -> List[Dict]:
        """Load all system learnings."""
        if not os.path.exists(SYSTEM_LEARNINGS_PATH):
            return []
        
        with open(SYSTEM_LEARNINGS_PATH, 'r') as f:
            data = json.load(f)
            return data.get('learnings', [])
    
    def load_build_learnings(self, build_slug: str) -> List[Dict]:
        """Load learnings from a specific build ledger."""
        ledger_path = os.path.join(BUILDS_PATH, build_slug, "BUILD_LESSONS.json")
        if not os.path.exists(ledger_path):
            return []
        
        with open(ledger_path, 'r') as f:
            data = json.load(f)
            return data.get('learnings', [])
    
    def detect_contradiction_patterns(self, text1: str, text2: str) -> List[str]:
        """Detect pattern-based contradiction signals."""
        signals = []
        t1_lower = text1.lower()
        t2_lower = text2.lower()
        
        # Single-sided negation detection (high similarity + negation in one but not the other)
        negation_words = ["not", "never", "no", "cannot", "can't", "doesn't", "don't", "won't", "isn't", "aren't", "shouldn't", "mustn't"]
        
        has_negation_1 = any(neg in t1_lower for neg in negation_words)
        has_negation_2 = any(neg in t2_lower for neg in negation_words)
        
        # If one has negation and the other doesn't, signal potential contradiction
        if has_negation_1 and not has_negation_2:
            negations = [neg for neg in negation_words if neg in t1_lower]
            signals.append(f"Single-sided negation: '{', '.join(negations)}' in learning A but not B")
        elif has_negation_2 and not has_negation_1:
            negations = [neg for neg in negation_words if neg in t2_lower]
            signals.append(f"Single-sided negation: '{', '.join(negations)}' in learning B but not A")
        
        # Paired negation patterns
        negation_pairs = [
            ("does not", "does"),
            ("doesn't", "does"),
            ("do not", "do"),
            ("don't", "do"),
            ("cannot", "can"),
            ("can't", "can"),
            ("will not", "will"),
            ("won't", "will"),
            ("is not", "is"),
            ("isn't", "is"),
            ("are not", "are"),
            ("aren't", "are"),
            ("should not", "should"),
            ("shouldn't", "should"),
            ("must not", "must"),
            ("never", "always"),
            ("optional", "required"),
            ("disabled", "enabled"),
            ("off", "on"),
            ("false", "true"),
            ("no", "yes"),
            ("require", "allow"),
            ("requires", "allows"),
            ("required", "allowed"),
            ("must", "can"),
            ("mandatory", "optional"),
            ("forbidden", "permitted"),
        ]
        
        for neg, aff in negation_pairs:
            if neg in t1_lower and aff in t2_lower:
                signals.append(f"Negation: '{neg}' in learning A vs '{aff}' in learning B")
            elif neg in t2_lower and aff in t1_lower:
                signals.append(f"Negation: '{neg}' in learning B vs '{aff}' in learning A")
        
        # Opposite directional words
        opposite_pairs = [
            ("increase", "decrease"),
            ("add", "remove"),
            ("include", "exclude"),
            ("before", "after"),
            ("first", "last"),
            ("start", "stop"),
            ("enable", "disable"),
            ("allow", "block"),
            ("permit", "deny"),
        ]
        
        for word1, word2 in opposite_pairs:
            if word1 in t1_lower and word2 in t2_lower:
                signals.append(f"Opposite: '{word1}' in learning A vs '{word2}' in learning B")
            elif word1 in t2_lower and word2 in t1_lower:
                signals.append(f"Opposite: '{word2}' in learning A vs '{word1}' in learning B")
        
        # Number/time contradictions (basic detection)
        import re
        numbers1 = re.findall(r'\d+(?:\.\d+)?(?:\s*(?:min|hour|second|sec|hr|day|week|month|year))?', text1)
        numbers2 = re.findall(r'\d+(?:\.\d+)?(?:\s*(?:min|hour|second|sec|hr|day|week|month|year))?', text2)
        
        if numbers1 and numbers2 and len(numbers1) == len(numbers2) == 1:
            # If both have different numbers, might be contradiction
            try:
                num1 = float(re.search(r'\d+\.?\d*', numbers1[0]).group())
                num2 = float(re.search(r'\d+\.?\d*', numbers2[0]).group())
                if abs(num1 - num2) > (num1 * 0.5):  # More than 50% difference
                    signals.append(f"Number mismatch: '{numbers1[0]}' vs '{numbers2[0]}'")
            except:
                pass
        
        return signals
    
    def llm_verify_contradiction(self, text1: str, text2: str) -> Dict[str, any]:
        """Use LLM to verify if two statements contradict each other."""
        try:
            token = os.environ.get('ZO_CLIENT_IDENTITY_TOKEN')
            if not token:
                return {"verified": False, "reason": "No ZO_CLIENT_IDENTITY_TOKEN"}
            
            prompt = f"""Analyze these two statements and determine if they contradict each other.

Statement A: "{text1}"
Statement B: "{text2}"

Respond with exactly one of these words:
- CONTRADICT: The statements clearly contradict each other
- CONSISTENT: The statements do not contradict (they can both be true or are unrelated)
- AMBIGUOUS: More context is needed to determine if they contradict

Respond with only the word, nothing else."""
            
            response = requests.post(
                "https://api.zo.computer/zo/ask",
                headers={
                    "authorization": token,
                    "content-type": "application/json"
                },
                json={"input": prompt}
            )
            
            result = response.json()
            llm_output = result.get("output", "").strip().upper()
            
            if "CONTRADICT" in llm_output:
                return {"verified": True, "llm_result": "CONTRADICT"}
            elif "CONSISTENT" in llm_output:
                return {"verified": False, "llm_result": "CONSISTENT"}
            else:
                return {"verified": False, "llm_result": "AMBIGUOUS"}
                
        except Exception as e:
            return {"verified": False, "error": str(e)}
    
    def find_contradictions(
        self,
        new_text: str,
        learnings: List[Dict],
        use_llm: bool = True,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find contradictions between new text and existing learnings.
        
        Args:
            new_text: The new learning text to check
            learnings: List of existing learning dicts
            use_llm: Whether to use LLM verification for high-similarity pairs
            similarity_threshold: Minimum similarity to consider learnings related
        
        Returns:
            List of contradiction findings
        """
        contradictions = []
        
        for idx, learning in enumerate(learnings):
            existing_text = learning.get('text', '')
            if not existing_text:
                continue
            
            # Skip if learning is already invalidated
            if learning.get('status') == 'invalidated':
                continue
            
            # Compute semantic similarity
            similarity = self.compute_similarity(new_text, existing_text)
            
            # Only check for contradiction if similarity is above threshold
            if similarity < similarity_threshold:
                continue
            
            # Detect pattern-based signals
            signals = self.detect_contradiction_patterns(new_text, existing_text)
            
            # If no patterns found but high similarity, use LLM verification
            contradiction_confidence = "LOW"
            llm_result = None
            
            if not signals and similarity > 0.85 and use_llm:
                llm_verify = self.llm_verify_contradiction(new_text, existing_text)
                if llm_verify.get("verified"):
                    signals.append(f"LLM verified contradiction")
                    contradiction_confidence = "HIGH"
                    llm_result = llm_verify.get("llm_result")
                elif llm_verify.get("llm_result") == "AMBIGUOUS":
                    contradiction_confidence = "MEDIUM"
            elif signals:
                # Have pattern signals
                if similarity > 0.85:
                    contradiction_confidence = "HIGH"
                elif similarity > 0.75:
                    contradiction_confidence = "MEDIUM"
                else:
                    contradiction_confidence = "LOW"
            
            # If we have contradiction signals or high LLM verification
            if signals or (llm_result == "CONTRADICT"):
                contradictions.append({
                    "index": idx,
                    "learning": existing_text,
                    "similarity": similarity,
                    "contradiction_confidence": contradiction_confidence,
                    "signals": signals,
                    "llm_result": llm_result,
                    "added_at": learning.get('added_at'),
                    "origin_build": learning.get('origin_build'),
                    "status": learning.get('status')
                })
        
        return contradictions
    
    def scan_internal_contradictions(self, learnings: List[Dict], use_llm: bool = False) -> List[Tuple[int, int, Dict]]:
        """
        Scan for internal contradictions within a set of learnings.
        
        Returns:
            List of (index_a, index_b, contradiction_info) tuples
        """
        contradictions = []
        
        for i in range(len(learnings)):
            for j in range(i + 1, len(learnings)):
                text1 = learnings[i].get('text', '')
                text2 = learnings[j].get('text', '')
                
                if not text1 or not text2:
                    continue
                
                # Skip if either is invalidated
                if learnings[i].get('status') == 'invalidated' or learnings[j].get('status') == 'invalidated':
                    continue
                
                similarity = self.compute_similarity(text1, text2)
                
                if similarity < 0.7:
                    continue
                
                signals = self.detect_contradiction_patterns(text1, text2)
                
                if signals or similarity > 0.9:
                    contradiction_confidence = "HIGH" if similarity > 0.85 else "MEDIUM"
                    
                    contradictions.append({
                        "index_a": i,
                        "index_b": j,
                        "text_a": text1,
                        "text_b": text2,
                        "similarity": similarity,
                        "contradiction_confidence": contradiction_confidence,
                        "signals": signals,
                        "added_at_a": learnings[i].get('added_at'),
                        "added_at_b": learnings[j].get('added_at'),
                        "origin_build_a": learnings[i].get('origin_build'),
                        "origin_build_b": learnings[j].get('origin_build')
                    })
        
        return contradictions
    
    def format_contradiction_report(self, new_text: str, contradictions: List[Dict]) -> str:
        """Format contradiction findings as a readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("CONTRADICTION CHECK")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"New Learning: \"{new_text}\"")
        lines.append("")
        
        if not contradictions:
            lines.append("✓ No contradictions found")
            return "\n".join(lines)
        
        lines.append(f"⚠️  FOUND {len(contradictions)} POTENTIAL CONTRADICTION(S)")
        lines.append("")
        
        for c in contradictions:
            lines.append(f"Existing Learning (index {c['index']}, added {c.get('added_at', 'unknown')}):")
            lines.append(f"  \"{c['learning']}\"")
            lines.append("")
            lines.append(f"Similarity: {c['similarity']:.2f}")
            lines.append(f"Contradiction Confidence: {c['contradiction_confidence']}")
            
            if c['origin_build']:
                lines.append(f"Origin Build: {c['origin_build']}")
            
            lines.append("")
            lines.append("Signals:")
            for signal in c['signals']:
                lines.append(f"  - {signal}")
            
            if c['llm_result']:
                lines.append(f"  - LLM Result: {c['llm_result']}")
            
            lines.append("")
            lines.append("Recommendation:")
            lines.append("  1. Verify which learning is correct")
            lines.append("  2. Use `pulse_learnings.py invalidate <index>` on the incorrect one")
            lines.append("  3. Or use `pulse_learnings.py dispute <index>` if context-dependent")
            lines.append("")
            lines.append("-" * 60)
            lines.append("")
        
        return "\n".join(lines)


def check_before_adding(new_text: str, tags: list = None) -> dict:
    """
    Check for contradictions before adding a new learning.
    
    This is the integration function for use by other scripts.
    
    Args:
        new_text: The new learning text to check
        tags: Optional tags for the learning (not used in detection)
    
    Returns:
        {
            "can_add": bool,
            "contradictions": [...],
            "action_required": "none|review|resolve"
        }
    """
    detector = ContradictionDetector()
    learnings = detector.load_system_learnings()
    
    contradictions = detector.find_contradictions(new_text, learnings)
    
    # Filter by confidence threshold
    high_conf_contradictions = [c for c in contradictions if c['contradiction_confidence'] == 'HIGH']
    med_conf_contradictions = [c for c in contradictions if c['contradiction_confidence'] == 'MEDIUM']
    
    if high_conf_contradictions:
        return {
            "can_add": False,
            "contradictions": high_conf_contradictions,
            "action_required": "resolve",
            "reason": "High confidence contradictions found"
        }
    elif med_conf_contradictions:
        return {
            "can_add": False,
            "contradictions": med_conf_contradictions,
            "action_required": "review",
            "reason": "Medium confidence contradictions found"
        }
    else:
        return {
            "can_add": True,
            "contradictions": [],
            "action_required": "none",
            "reason": "No contradictions found"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Detect contradictions in N5 learnings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check if new learning contradicts existing
  python3 contradiction_detector.py check "The API allows unauthenticated access"
  
  # Scan all system learnings for internal contradictions
  python3 contradiction_detector.py scan
  
  # Scan specific build learnings
  python3 contradiction_detector.py scan --build watts-principles
  
  # Compare two specific texts
  python3 contradiction_detector.py compare "API requires auth" "No auth needed"
  
  # Integration function (for scripts):
  from contradiction_detector import check_before_adding
  result = check_before_adding("new learning text")
  if not result["can_add"]:
      print(f"Cannot add: {result['reason']}")
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check new learning against existing')
    check_parser.add_argument('text', help='New learning text to check')
    check_parser.add_argument('--no-llm', action='store_true', help='Skip LLM verification')
    check_parser.add_argument('--threshold', type=float, default=0.7, 
                             help='Similarity threshold (default: 0.7)')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for internal contradictions')
    scan_parser.add_argument('--build', help='Build slug to scan (default: all system learnings)')
    scan_parser.add_argument('--no-llm', action='store_true', help='Skip LLM verification')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two texts directly')
    compare_parser.add_argument('text1', help='First text')
    compare_parser.add_argument('text2', help='Second text')
    compare_parser.add_argument('--no-llm', action='store_true', help='Skip LLM verification')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    detector = ContradictionDetector()
    
    if args.command == 'check':
        # Load system learnings
        learnings = detector.load_system_learnings()
        
        if not learnings:
            print("No existing learnings found")
            return
        
        # Find contradictions
        contradictions = detector.find_contradictions(
            args.text,
            learnings,
            use_llm=not args.no_llm,
            similarity_threshold=args.threshold
        )
        
        # Format and print report
        report = detector.format_contradiction_report(args.text, contradictions)
        print(report)
        
    elif args.command == 'scan':
        if args.build:
            # Load specific build learnings
            learnings = detector.load_build_learnings(args.build)
            print(f"Scanning build '{args.build}' learnings...")
        else:
            # Load system learnings
            learnings = detector.load_system_learnings()
            print("Scanning all system learnings...")
        
        if not learnings:
            print("No learnings found")
            return
        
        print(f"Found {len(learnings)} learnings to check\n")
        
        # Scan for internal contradictions
        contradictions = detector.scan_internal_contradictions(learnings)
        
        if not contradictions:
            print("✓ No internal contradictions found")
            return
        
        print(f"⚠️  Found {len(contradictions)} internal contradiction(s):\n")
        print("=" * 60)
        
        for c in contradictions:
            print(f"\nLearning {c['index_a']} vs Learning {c['index_b']}")
            print(f"Similarity: {c['similarity']:.2f}")
            print(f"Confidence: {c['contradiction_confidence']}")
            print(f"\nText A (from {c.get('origin_build_a', 'unknown')}):")
            print(f"  \"{c['text_a']}\"")
            print(f"\nText B (from {c.get('origin_build_b', 'unknown')}):")
            print(f"  \"{c['text_b']}\"")
            
            if c['signals']:
                print("\nSignals:")
                for signal in c['signals']:
                    print(f"  - {signal}")
            
            print("\n" + "-" * 60)
        
    elif args.command == 'compare':
        # Direct comparison of two texts
        similarity = detector.compute_similarity(args.text1, args.text2)
        signals = detector.detect_contradiction_patterns(args.text1, args.text2)
        
        print("=" * 60)
        print("DIRECT COMPARISON")
        print("=" * 60)
        print(f"\nText A: \"{args.text1}\"")
        print(f"\nText B: \"{args.text2}\"")
        print(f"\nSimilarity: {similarity:.2f}")
        
        if signals:
            print(f"\n⚠️  Contradiction signals found:")
            for signal in signals:
                print(f"  - {signal}")
        else:
            print("\n✓ No contradiction signals found")
        
        if not args.no_llm and similarity > 0.85:
            print("\nVerifying with LLM...")
            llm_result = detector.llm_verify_contradiction(args.text1, args.text2)
            if llm_result.get('verified'):
                print(f"  LLM Result: CONTRADICT confirmed")
            elif llm_result.get('llm_result') == 'CONSISTENT':
                print(f"  LLM Result: No contradiction")
            else:
                print(f"  LLM Result: Ambiguous (more context needed)")
        else:
            print("\n(Use --llm flag to enable LLM verification for high-similarity pairs)")


if __name__ == "__main__":
    main()
