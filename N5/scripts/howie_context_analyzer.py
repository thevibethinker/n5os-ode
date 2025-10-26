#!/usr/bin/env python3
"""
Howie Context Analyzer

Analyzes conversation transcripts and extracted B-blocks to infer appropriate
Howie scheduling tags. Integrates with howie_signature_generator.py to create
contextually appropriate email signatures.

Usage:
    python3 howie_context_analyzer.py --blocks blocks.json --transcript transcript.txt
    python3 howie_context_analyzer.py --blocks blocks.json --output-format json
"""

import argparse
import json
import logging
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Analyzed context from conversation"""
    recipient_type: str  # investor, hire, community, networking, general
    urgency_level: str  # low, normal, high, urgent
    relationship_stage: str  # new, warm, established, internal
    value_signal: str  # low, medium, high, strategic
    requires_follow_up: bool
    follow_up_days: Optional[int]
    accommodation_level: int  # 0-2
    align_with_logan: bool
    priority: str  # internal, founders, external
    confidence: float  # 0.0-1.0
    reasoning: Dict[str, str]


class HowieContextAnalyzer:
    """Analyzes conversation context to recommend Howie tags"""
    
    # Keyword signals for recipient type
    INVESTOR_SIGNALS = [
        "investor", "funding", "raise", "round", "seed", "series",
        "vc", "venture", "capital", "investment", "valuation"
    ]
    
    HIRE_SIGNALS = [
        "hire", "hiring", "candidate", "interview", "role",
        "position", "job", "application", "resume", "technical co-founder search"
    ]
    
    # Strategic founder partnerships (LD-FND)
    FOUNDER_SIGNALS = [
        "founder partnership", "strategic founder", "co-founder", 
        "founder collaboration", "founder alliance", "startup founder",
        "product partnership", "founder-to-founder"
    ]
    
    # Community organizations (LD-COM)
    COMMUNITY_SIGNALS = [
        "community org", "alumni association", "community group",
        "association", "fellowship", "cohort", "network group",
        "meetup", "future of higher ed", "mckinsey alumni"
    ]
    
    NETWORKING_SIGNALS = [
        "coffee", "chat", "connect", "intro", "introduction",
        "advice", "guidance", "mentorship", "feedback", "pick your brain"
    ]
    
    # Urgency signals (maps to DX system)
    URGENT_SIGNALS = [
        "urgent", "asap", "immediately", "emergency", "critical",
        "right away", "as soon as possible", "time-sensitive", "this week"
    ]
    
    HIGH_URGENCY_SIGNALS = [
        "soon", "quickly", "next few days", "pressing",
        "important", "priority", "by end of week"
    ]
    
    # Value signals
    HIGH_VALUE_SIGNALS = [
        "strategic", "key", "important", "critical", "major",
        "significant", "large", "enterprise", "tier-1"
    ]
    
    STRATEGIC_VALUE_SIGNALS = [
        "partnership", "ecosystem", "platform", "integration",
        "long-term", "growth", "expansion"
    ]
    
    # Follow-up indicators
    FOLLOW_UP_NEEDED = [
        "follow up", "send", "share", "forward", "intro",
        "connect", "action item", "next step", "will send"
    ]
    
    def __init__(self):
        self.context = None
    
    def analyze_blocks(self, blocks_data: Dict[str, Any]) -> ConversationContext:
        """Analyze extracted B-blocks to infer context"""
        
        # Combine all text content for analysis
        all_text = self._extract_all_text(blocks_data)
        
        # Analyze different dimensions
        recipient_type, recip_confidence = self._infer_recipient_type(all_text, blocks_data)
        urgency, urgency_confidence = self._infer_urgency(all_text, blocks_data)
        relationship, rel_confidence = self._infer_relationship_stage(all_text, blocks_data)
        value_signal, value_confidence = self._infer_value_signal(all_text, blocks_data)
        follow_up_needed, follow_up_days = self._check_follow_up(blocks_data)
        accommodation = self._infer_accommodation_level(
            recipient_type, relationship, value_signal
        )
        align_logan = self._should_align_with_logan(all_text, recipient_type)
        priority = self._infer_priority(recipient_type, value_signal, relationship)
        
        # Calculate overall confidence
        confidence = (
            recip_confidence * 0.3 +
            urgency_confidence * 0.2 +
            rel_confidence * 0.2 +
            value_confidence * 0.3
        )
        
        # Build reasoning
        reasoning = {
            "recipient_type": self._explain_recipient_type(all_text, recipient_type),
            "urgency": self._explain_urgency(all_text, urgency),
            "relationship": self._explain_relationship(all_text, relationship),
            "value": self._explain_value(all_text, value_signal),
            "accommodation": self._explain_accommodation(accommodation, recipient_type, value_signal)
        }
        
        context = ConversationContext(
            recipient_type=recipient_type,
            urgency_level=urgency,
            relationship_stage=relationship,
            value_signal=value_signal,
            requires_follow_up=follow_up_needed,
            follow_up_days=follow_up_days,
            accommodation_level=accommodation,
            align_with_logan=align_logan,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning
        )
        
        self.context = context
        return context
    
    def _extract_all_text(self, blocks_data: Dict[str, Any]) -> str:
        """Extract all text from blocks for analysis"""
        text_parts = []
        
        # Action items
        if "action_items" in blocks_data:
            text_parts.extend(blocks_data["action_items"])
        
        # Key decisions
        if "key_decisions" in blocks_data:
            text_parts.extend(blocks_data["key_decisions"])
        
        # Questions
        if "questions" in blocks_data:
            text_parts.extend(blocks_data["questions"])
        
        # Resource contexts
        if "resources_explicit" in blocks_data:
            for res in blocks_data["resources_explicit"]:
                if res.get("context"):
                    text_parts.append(res["context"])
        
        return " ".join(text_parts).lower()
    
    def _infer_recipient_type(
        self, text: str, blocks: Dict[str, Any]
    ) -> tuple[str, float]:
        """Infer recipient type from content"""
        
        # Check in priority order - more specific patterns first
        scores = {
            "investor": self._count_signals(text, self.INVESTOR_SIGNALS),
            "hire": self._count_signals(text, self.HIRE_SIGNALS),
            "founder": self._count_signals(text, self.FOUNDER_SIGNALS),  # Check founder first
            "community": self._count_signals(text, self.COMMUNITY_SIGNALS),
            "networking": self._count_signals(text, self.NETWORKING_SIGNALS),
        }
        
        if max(scores.values()) == 0:
            return "general", 0.3
        
        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 5.0, 1.0)
        
        return best_type, confidence
    
    def _infer_urgency(
        self, text: str, blocks: Dict[str, Any]
    ) -> tuple[str, float]:
        """Infer urgency level"""
        
        urgent_count = self._count_signals(text, self.URGENT_SIGNALS)
        high_count = self._count_signals(text, self.HIGH_URGENCY_SIGNALS)
        
        if urgent_count > 0:
            return "urgent", min(urgent_count / 2.0, 1.0)
        elif high_count > 0:
            return "high", min(high_count / 3.0, 1.0)
        elif len(blocks.get("action_items", [])) > 2:
            return "normal", 0.6
        else:
            return "normal", 0.7
    
    def _infer_relationship_stage(
        self, text: str, blocks: Dict[str, Any]
    ) -> tuple[str, float]:
        """Infer relationship stage"""
        
        # Look for first-time meeting indicators
        first_time_signals = ["nice to meet", "thanks for taking the time", "heard about you"]
        first_time_count = self._count_signals(text, first_time_signals)
        
        # Look for established relationship indicators
        established_signals = ["as we discussed", "last time", "following up"]
        established_count = self._count_signals(text, established_signals)
        
        if first_time_count > 0:
            return "new", 0.8
        elif established_count > 0:
            return "established", 0.8
        else:
            return "warm", 0.5
    
    def _infer_value_signal(
        self, text: str, blocks: Dict[str, Any]
    ) -> tuple[str, float]:
        """Infer strategic value"""
        
        high_value_count = self._count_signals(text, self.HIGH_VALUE_SIGNALS)
        strategic_count = self._count_signals(text, self.STRATEGIC_VALUE_SIGNALS)
        
        if strategic_count > 0:
            return "strategic", min((strategic_count + high_value_count) / 3.0, 1.0)
        elif high_value_count > 0:
            return "high", min(high_value_count / 3.0, 1.0)
        else:
            return "medium", 0.6
    
    def _check_follow_up(self, blocks: Dict[str, Any]) -> tuple[bool, Optional[int]]:
        """Check if follow-up is needed and suggest timeline"""
        
        action_items = blocks.get("action_items", [])
        if not action_items:
            return False, None
        
        # Default to 5 days for community/networking
        return True, 5
    
    def _infer_accommodation_level(
        self, recipient_type: str, relationship: str, value: str
    ) -> int:
        """Infer how accommodating to be (0=our terms, 1=balanced, 2=fully accommodating)"""
        
        # High accommodation for investors and high-value relationships
        if recipient_type == "investor" or value == "strategic":
            return 2
        
        # Balanced for new relationships
        if relationship == "new":
            return 1
        
        # Lower accommodation for established or internal
        if relationship == "established" or recipient_type == "networking":
            return 1
        
        return 1  # Default balanced
    
    def _should_align_with_logan(self, text: str, recipient_type: str) -> bool:
        """Check if meeting should align with Logan"""
        
        # Explicit Logan mention
        if "logan" in text:
            return True
        
        # Check for "both of us" or "we should meet" (implies joint meeting)
        if "both of us" in text or "we should meet" in text:
            return True
        
        # "founders" only if it's about OUR founders, not other companies
        # Negative signals: "zo founders", "their founders", "the founders"
        if " founders" in text:
            # Check if it's referring to external founders
            external_founder_phrases = ["zo founders", "their founders", "the founders", "yc founders"]
            if any(phrase in text for phrase in external_founder_phrases):
                return False
            # If just "founders" without qualifier, could be ours
            return "founders" in text
        
        return False
    
    def _infer_priority(
        self, recipient_type: str, value: str, relationship: str
    ) -> str:
        """Infer priority level (internal, founders, external)"""
        
        if value == "strategic" or recipient_type == "investor":
            return "external"
        elif recipient_type in ["community", "networking"]:
            return "external"
        else:
            return "external"  # Default to external for customer-facing
    
    def _count_signals(self, text: str, signals: List[str]) -> int:
        """Count occurrences of signal keywords"""
        count = 0
        for signal in signals:
            count += len(re.findall(r'\b' + re.escape(signal) + r'\b', text))
        return count
    
    def _explain_recipient_type(self, text: str, recipient_type: str) -> str:
        """Generate explanation for recipient type inference"""
        
        if recipient_type == "investor":
            return "Detected investor-related language"
        elif recipient_type == "hire":
            return "Detected hiring/recruiting context"
        elif recipient_type == "community":
            return "Founder seeking help; community/ecosystem play"
        elif recipient_type == "networking":
            return "Networking/advisory conversation"
        else:
            return "General meeting context"
    
    def _explain_urgency(self, text: str, urgency: str) -> str:
        """Generate explanation for urgency inference"""
        
        if urgency == "urgent":
            return "Explicit urgency signals detected"
        elif urgency == "high":
            return "Time-sensitive language detected"
        else:
            return "Standard follow-up timeline"
    
    def _explain_relationship(self, text: str, relationship: str) -> str:
        """Generate explanation for relationship stage"""
        
        if relationship == "new":
            return "First interaction; building relationship"
        elif relationship == "established":
            return "Established relationship"
        else:
            return "Warming relationship"
    
    def _explain_value(self, text: str, value: str) -> str:
        """Generate explanation for value signal"""
        
        if value == "strategic":
            return "Strategic value - potential ecosystem/platform play (Zo customer)"
        elif value == "high":
            return "High value relationship"
        else:
            return "Standard value"
    
    def _explain_accommodation(
        self, accommodation: int, recipient_type: str, value: str
    ) -> str:
        """Generate explanation for accommodation level"""
        
        if accommodation == 2:
            return f"High accommodation due to {recipient_type} type and {value} value"
        elif accommodation == 1:
            return "Balanced accommodation - mutual convenience"
        else:
            return "Minimal accommodation - our terms"
    
    def generate_howie_tags(self) -> str:
        """Generate Howie tag string from analyzed context"""
        
        if not self.context:
            raise ValueError("Must run analyze_blocks() first")
        
        # Build tag components
        tags = []
        
        # Recipient type tag (LD-*)
        type_map = {
            "investor": "LD-INV",
            "hire": "LD-HIR",
            "founder": "LD-FND",  # Add LD-FND
            "community": "LD-COM",
            "networking": "LD-NET",
            "general": "LD-GEN"
        }
        tags.append(type_map.get(self.context.recipient_type, "LD-GEN"))
        
        # Priority tag (GPT-*)
        priority_map = {
            "external": "GPT-E",
            "founders": "GPT-F",
            "internal": "GPT-I"
        }
        tags.append(priority_map[self.context.priority])
        
        # Accommodation tag (A-*)
        tags.append(f"A-{self.context.accommodation_level}")
        
        # Timeline tag (DX system - no more !!)
        urgency_to_timeline = {
            "urgent": "D1-",   # by 1 business day latest
            "high": "D3-",     # by 3 business days latest
            "normal": "D3+",   # 3+ days out (default)
            "low": "D7+"       # 7+ days out
        }
        timeline_tag = urgency_to_timeline.get(self.context.urgency_level, "D3+")
        tags.append(timeline_tag)
        
        # Follow-up tag
        if self.context.requires_follow_up and self.context.follow_up_days:
            tags.append(f"F-{self.context.follow_up_days}")
        
        # Logan alignment
        if self.context.align_with_logan:
            tags.append("LOG")
        
        # Activation symbol
        tags.append("*")
        
        return " ".join(f"[{tag}]" if tag != "*" else tag for tag in tags)
    
    def generate_full_signature(self) -> str:
        """Generate complete signature with Howie tags"""
        
        howie_tags = self.generate_howie_tags()
        
        signature_lines = [
            "Best,",
            "Vrijen S Attawar",
            "CEO @ Careerspan",
            "---",
            "👉 Try Careerspan! and Follow us on LinkedIn!",
            "🤝 Let's connect on Twitter or LinkedIn",
            "",
            f"Howie Tags: {howie_tags}"
        ]
        
        return "\n".join(signature_lines)
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate detailed analysis report"""
        
        if not self.context:
            raise ValueError("Must run analyze_blocks() first")
        
        return {
            "analysis": asdict(self.context),
            "recommended_tags": self.generate_howie_tags(),
            "full_signature": self.generate_full_signature(),
            "confidence_level": f"{self.context.confidence:.0%}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze conversation context and generate Howie tags"
    )
    parser.add_argument(
        "--blocks",
        required=True,
        help="Path to blocks JSON file"
    )
    parser.add_argument(
        "--transcript",
        help="Path to transcript file (optional, for additional context)"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--full-signature",
        action="store_true",
        help="Output full signature block"
    )
    
    args = parser.parse_args()
    
    # Load blocks
    try:
        with open(args.blocks) as f:
            blocks_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load blocks: {e}")
        return 1
    
    # Analyze
    analyzer = HowieContextAnalyzer()
    context = analyzer.analyze_blocks(blocks_data)
    
    # Output
    if args.output_format == "json":
        report = analyzer.generate_analysis_report()
        print(json.dumps(report, indent=2))
    else:
        if args.full_signature:
            print(analyzer.generate_full_signature())
        else:
            print(analyzer.generate_howie_tags())
        
        print("\n--- Analysis ---")
        print(f"Recipient Type: {context.recipient_type} ({context.reasoning['recipient_type']})")
        print(f"Urgency: {context.urgency_level} ({context.reasoning['urgency']})")
        print(f"Relationship: {context.relationship_stage} ({context.reasoning['relationship']})")
        print(f"Value Signal: {context.value_signal} ({context.reasoning['value']})")
        print(f"Accommodation: Level {context.accommodation_level} ({context.reasoning['accommodation']})")
        print(f"Follow-up: {'Yes' if context.requires_follow_up else 'No'}", end="")
        if context.requires_follow_up:
            print(f" (in {context.follow_up_days} days)")
        else:
            print()
        print(f"Confidence: {context.confidence:.0%}")
    
    return 0


if __name__ == "__main__":
    exit(main())
