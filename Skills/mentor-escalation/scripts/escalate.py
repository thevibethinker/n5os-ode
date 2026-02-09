#!/usr/bin/env python3
"""
Escalation Decision Framework for Zoputer Autonomy

Implements confidence-based decision routing:
- >= 0.7: Auto-decide (zoputer acts autonomously)
- 0.5-0.7: Ask va (mentor guidance)
- < 0.5: Ask V (human escalation)

Usage:
    python3 escalate.py assess "Should I modify this workflow for client X?"
    python3 escalate.py ask-va "How should I handle this request?" --context '{"client": "X"}'
    python3 escalate.py ask-human "Complex legal question requires V's input"
    python3 escalate.py should-escalate --confidence 0.6

Based on the localization protocol threshold decisions.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    import requests
except ImportError:
    print("Error: requests library required. Run: pip install requests")
    sys.exit(1)

from va_client import call_va, log_audit

# Confidence thresholds from localization protocol
CONFIDENCE_THRESHOLDS = {
    "auto_decide": 0.7,      # >= 0.7: zoputer decides alone
    "ask_va": 0.5,           # 0.5-0.7: ask va for guidance
    "ask_v": 0.0             # < 0.5: escalate to human (V)
}

# Decision types that always require human approval regardless of confidence
ALWAYS_HUMAN_TYPES = [
    "security_gate_change",
    "audit_protocol_change", 
    "new_obligations",
    "legal_compliance",
    "privacy_policy_change",
    "tier_boundary_change"
]


def assess_confidence(situation: str, context: Optional[Dict] = None) -> float:
    """
    Use LLM to assess confidence in handling a situation autonomously.
    
    Args:
        situation: Description of the situation requiring a decision
        context: Optional context dictionary
    
    Returns:
        Confidence score between 0.0 and 1.0
    """
    correlation_id = f"assess-{uuid.uuid4().hex[:8]}"
    
    # Build context string
    context_str = ""
    if context:
        context_str = f"\nCONTEXT:\n{json.dumps(context, indent=2)}"
    
    # Assessment prompt based on localization protocol principles
    prompt = f"""You are an AI confidence assessor for zoputer's decision-making framework.

SITUATION TO ASSESS:
{situation}{context_str}

Assess zoputer's confidence in handling this situation autonomously. Consider:

1. **Cosmetic vs Structural**: 
   - Cosmetic changes (labels, display names, ordering) → High confidence
   - Structural changes (workflow steps, data capture, dependencies) → Lower confidence

2. **Risk Level**:
   - Low risk (reversible, no client impact) → Higher confidence  
   - High risk (security, audit, compliance, permanent changes) → Lower confidence

3. **Precedent**:
   - Clear precedent exists → Higher confidence
   - Novel situation → Lower confidence

4. **Authority Level**:
   - Within zoputer's scope → Higher confidence
   - Requires strategic/policy decision → Lower confidence

CONFIDENCE SCALE:
- 0.9-1.0: Routine operation with clear precedent
- 0.7-0.9: Standard adaptation within established patterns  
- 0.5-0.7: Novel situation but within general guidelines
- 0.3-0.5: Complex decision requiring strategic input
- 0.0-0.3: High-stakes decision requiring human judgment

Respond with ONLY a confidence score between 0.0 and 1.0 as a decimal number."""

    try:
        # For confidence assessment, we'll use a simple local LLM call
        # In a real implementation, this might call a lighter model
        result = call_va(prompt, correlation_id)
        
        output = result.get("output", "").strip()
        
        # Extract confidence score from response
        try:
            confidence = float(output)
            # Clamp to valid range
            confidence = max(0.0, min(1.0, confidence))
            return confidence
        except ValueError:
            print(f"Warning: Could not parse confidence score from: {output}")
            # Default to asking va when in doubt
            return 0.6
    
    except Exception as e:
        print(f"Warning: Confidence assessment failed: {e}")
        # Default to asking va when assessment fails
        return 0.6


def should_escalate(confidence: float, decision_type: Optional[str] = None) -> str:
    """
    Determine escalation path based on confidence score and decision type.
    
    Args:
        confidence: Confidence score 0.0-1.0
        decision_type: Optional type of decision
    
    Returns:
        "auto", "va", or "human"
    """
    # Check for decisions that always require human approval
    if decision_type in ALWAYS_HUMAN_TYPES:
        return "human"
    
    # Apply confidence thresholds
    if confidence >= CONFIDENCE_THRESHOLDS["auto_decide"]:
        return "auto"
    elif confidence >= CONFIDENCE_THRESHOLDS["ask_va"]:
        return "va"
    else:
        return "human"


def escalate_to_va(question: str, context: Optional[Dict] = None, confidence: Optional[float] = None) -> str:
    """
    Escalate a question to va for guidance.
    
    Args:
        question: The question to ask
        context: Optional context dictionary
        confidence: Optional confidence score
    
    Returns:
        va's response as a string
    """
    correlation_id = f"va-escalation-{uuid.uuid4().hex[:8]}"
    
    # Build escalation request
    escalation = {
        "type": "mentor_escalation",
        "from": "zoputer",
        "confidence": confidence,
        "situation": question,
        "context": context or {},
        "question": question,
        "correlation_id": correlation_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Format prompt for va
    prompt = f"""You are va, the Master Zo. Zoputer is escalating a decision for your guidance.

ESCALATION REQUEST:
```json
{json.dumps(escalation, indent=2)}
```

As zoputer's mentor, provide guidance that includes:

1. **Recommendation**: Specific action to take
2. **Rationale**: Why this approach is best 
3. **Precedent**: Does this set a pattern for future similar decisions?
4. **Learning**: What principle should zoputer remember?

Format your response clearly for an apprentice AI to understand and apply."""

    try:
        result = call_va(prompt, correlation_id)
        response = result.get("output", "")
        
        # Log the escalation decision
        log_decision({
            "escalation_type": "mentor",
            "question": question,
            "confidence": confidence,
            "context": context,
            "va_response_preview": response[:200],
            "correlation_id": correlation_id
        })
        
        return response
    
    except Exception as e:
        raise Exception(f"Failed to escalate to va: {e}")


def escalate_to_human(question: str, context: Optional[Dict] = None, confidence: Optional[float] = None) -> str:
    """
    Escalate a question to V (human) for decision.
    
    This is a placeholder - actual implementation would integrate with 
    the pending decisions system from D3.x streams.
    
    Args:
        question: The question to escalate
        context: Optional context dictionary  
        confidence: Optional confidence score
    
    Returns:
        Acknowledgment string
    """
    correlation_id = f"human-escalation-{uuid.uuid4().hex[:8]}"
    
    # Log the escalation
    escalation = {
        "type": "human_escalation",
        "from": "zoputer", 
        "confidence": confidence,
        "situation": question,
        "context": context or {},
        "question": question,
        "correlation_id": correlation_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending"
    }
    
    log_decision(escalation)
    
    # In the real implementation, this would:
    # 1. Add to pending decisions queue
    # 2. Send notification to V
    # 3. Return a tracking ID
    
    print(f"Human escalation logged with ID: {correlation_id}")
    print("This decision requires V's input. Implementation pending from D3.x streams.")
    
    return f"Escalated to human with correlation_id: {correlation_id}"


def log_decision(decision: Dict[str, Any]) -> None:
    """Log decision to audit system."""
    correlation_id = decision.get("correlation_id")
    
    log_audit(
        entry_type="escalation_decision",
        direction="internal",
        payload=decision,
        correlation_id=correlation_id
    )


def cmd_assess(args) -> int:
    """Assess confidence for a situation."""
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            context = {"raw_context": args.context}
    
    print("Assessing decision confidence...")
    
    try:
        confidence = assess_confidence(args.situation, context)
        escalation_path = should_escalate(confidence, args.decision_type)
        
        print(f"\nSITUATION: {args.situation}")
        print(f"CONFIDENCE: {confidence:.2f}")
        print(f"ESCALATION PATH: {escalation_path}")
        
        if escalation_path == "auto":
            print("✓ Proceed autonomously")
        elif escalation_path == "va":
            print("→ Ask va for guidance")
        else:
            print("⚠ Escalate to human (V)")
        
        return 0
    
    except Exception as e:
        print(f"✗ Assessment failed: {e}")
        return 1


def cmd_ask_va(args) -> int:
    """Ask va for guidance."""
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            context = {"raw_context": args.context}
    
    print("Escalating to va for guidance...")
    
    try:
        response = escalate_to_va(args.question, context, args.confidence)
        
        print("\n" + "="*60)
        print("VA GUIDANCE:")
        print("="*60)
        print(response)
        print("="*60)
        
        return 0
    
    except Exception as e:
        print(f"✗ va escalation failed: {e}")
        return 1


def cmd_ask_human(args) -> int:
    """Escalate to human (V) for decision."""
    context = None
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            context = {"raw_context": args.context}
    
    print("Escalating to human (V)...")
    
    try:
        result = escalate_to_human(args.question, context, args.confidence)
        print(f"✓ {result}")
        return 0
    
    except Exception as e:
        print(f"✗ Human escalation failed: {e}")
        return 1


def cmd_should_escalate(args) -> int:
    """Check what escalation path to take."""
    escalation_path = should_escalate(args.confidence, args.decision_type)
    
    print(f"CONFIDENCE: {args.confidence}")
    print(f"DECISION TYPE: {args.decision_type or 'general'}")
    print(f"ESCALATION PATH: {escalation_path}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Escalation Decision Framework - confidence-based routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 escalate.py assess "Should I remove review gate for client X?"
  python3 escalate.py ask-va "How to handle workflow modification?" --context '{"client": "startup"}'  
  python3 escalate.py ask-human "Legal compliance question"
  python3 escalate.py should-escalate --confidence 0.6

Confidence Thresholds:
  >= 0.7: Auto-decide (autonomous action)
  0.5-0.7: Ask va (mentor guidance)  
  < 0.5: Ask human (V's decision)
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # assess
    assess_parser = subparsers.add_parser("assess", help="Assess confidence for a situation")
    assess_parser.add_argument("situation", help="Situation to assess")
    assess_parser.add_argument("--context", help="JSON context object")
    assess_parser.add_argument("--decision-type", help="Type of decision", choices=ALWAYS_HUMAN_TYPES + ["general"])
    
    # ask-va
    ask_va_parser = subparsers.add_parser("ask-va", help="Ask va for guidance")
    ask_va_parser.add_argument("question", help="Question for va")
    ask_va_parser.add_argument("--context", help="JSON context object")
    ask_va_parser.add_argument("--confidence", type=float, help="Confidence level if already assessed")
    
    # ask-human
    ask_human_parser = subparsers.add_parser("ask-human", help="Escalate to human (V)")
    ask_human_parser.add_argument("question", help="Question for V")
    ask_human_parser.add_argument("--context", help="JSON context object")
    ask_human_parser.add_argument("--confidence", type=float, help="Confidence level if already assessed")
    
    # should-escalate
    should_parser = subparsers.add_parser("should-escalate", help="Check escalation path for confidence level")
    should_parser.add_argument("--confidence", type=float, required=True, help="Confidence level 0.0-1.0")
    should_parser.add_argument("--decision-type", help="Type of decision", choices=ALWAYS_HUMAN_TYPES + ["general"])
    
    args = parser.parse_args()
    
    if args.command == "assess":
        sys.exit(cmd_assess(args))
    elif args.command == "ask-va":
        sys.exit(cmd_ask_va(args))
    elif args.command == "ask-human":
        sys.exit(cmd_ask_human(args))
    elif args.command == "should-escalate":
        sys.exit(cmd_should_escalate(args))
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()