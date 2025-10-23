#!/usr/bin/env python3
"""
Howie Signature Generator

Generates V-OS tags for email signatures that provide coded instructions to Howie
(Vrijen's scheduling assistant bot) about how to handle meeting scheduling.

Usage:
    python3 howie_signature_generator.py --context "investor meeting" --urgency high
    python3 howie_signature_generator.py --recipient-type investor --priority external --follow-up-days 5
"""

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class HowieTagSet:
    """A set of Howie V-OS tags with their reasoning"""
    lead_type: Optional[str] = None  # LD-INV, LD-HIR, LD-COM, LD-NET, LD-GEN
    scheduling: list[str] = field(default_factory=list)  # LOG, ILS, D3+, D1-, etc.
    priority: Optional[str] = None  # GPT-I, GPT-E, GPT-F
    accommodation: Optional[str] = None  # A-0, A-1, A-2
    follow_up: list[str] = field(default_factory=list)  # F-X
    special: list[str] = field(default_factory=list)  # WEX, WEP, TERM, INC, FLX
    activated: bool = True  # Whether to add * (activation symbol)
    
    def to_signature_line(self) -> str:
        """Generate the Howie tags signature line"""
        tags = []
        
        # Lead type first
        if self.lead_type:
            tags.append(f"[{self.lead_type}]")
        
        # Priority
        if self.priority:
            tags.append(f"[{self.priority}]")
        
        # Accommodation level
        if self.accommodation:
            tags.append(f"[{self.accommodation}]")
        
        # Scheduling constraints
        tags.extend([f"[{t}]" for t in self.scheduling])
        
        # Follow-up rules
        tags.extend([f"[{t}]" for t in self.follow_up])
        
        # Special modifiers
        tags.extend([f"[{t}]" for t in self.special])
        
        # Add activation marker if needed
        signature = " ".join(tags)
        if self.activated and tags:
            signature += " *"
        
        return signature
    
    def get_explanation(self) -> dict:
        """Get human-readable explanation of each tag"""
        explanations = {}
        
        if self.lead_type:
            lead_meanings = {
                "LD-FND": "Founder (strategic)",
                "LD-INV": "Investor",
                "LD-HIR": "Hiring / candidate",
                "LD-COM": "Community organization",
                "LD-NET": "Networking contact",
                "LD-GEN": "General lead"
            }
            explanations[self.lead_type] = lead_meanings.get(self.lead_type, "Unknown lead type")
        
        if self.priority:
            priority_meanings = {
                "GPT-I": "Prioritize internal constraints",
                "GPT-E": "Prioritize external constraints",
                "GPT-F": "Prioritize founders' (Vrijen + Logan) constraints"
            }
            explanations[self.priority] = priority_meanings[self.priority]
        
        if self.accommodation:
            acc_meanings = {
                "A-0": "Only on our terms",
                "A-1": "Baseline accommodation",
                "A-2": "Fully accommodating"
            }
            explanations[self.accommodation] = acc_meanings[self.accommodation]
        
        # Scheduling: LOG/ILS + generic DX, DX+, DX-
        for tag in self.scheduling:
            if tag in {"LOG", "ILS"}:
                sched_meanings = {
                    "LOG": "Align with Logan's availability",
                    "ILS": "Align with Ilse's availability",
                }
                explanations[tag] = sched_meanings[tag]
            elif tag.startswith("D"):
                # Parse DX/ DX+ / DX-
                core = tag[1:]
                suffix = None
                if core.endswith("+") or core.endswith("-"):
                    suffix = core[-1]
                    core = core[:-1]
                try:
                    days = int(core)
                except ValueError:
                    explanations[tag] = f"Scheduling window: {tag}"
                else:
                    if suffix == "+":
                        explanations[tag] = f"Schedule {days}+ business days out (≥ {days} days)"
                    elif suffix == "-":
                        explanations[tag] = f"Schedule by {days} business days at latest (≤ {days} days)"
                    else:
                        explanations[tag] = f"Schedule in exactly {days} business days"
            else:
                explanations[tag] = f"Scheduling: {tag}"
        
        # Follow-ups
        for tag in self.follow_up:
            if tag.startswith("F-"):
                days = tag.split("-")[1]
                explanations[tag] = f"If no reply, nudge after {days} days as Vrijen's assistant"
        
        # Special modifiers
        for tag in self.special:
            special_meanings = {
                "FLX": "Event can shift within same day",
                "WEX": "Allow weekend extension if needed",
                "WEP": "Prefer weekend scheduling",
                "TERM": "Terminate Howie's involvement for this thread",
                "INC": "Ignore email entirely"
            }
            explanations[tag] = special_meanings.get(tag, f"Special: {tag}")
        
        if self.activated:
            explanations["*"] = "ACTIVATED - Howie will process these tags"
        
        return explanations


class HowieSignatureGenerator:
    """Generate intelligent Howie signature tags based on context"""
    
    # Enhanced recipient type detection with priority order
    # More specific patterns checked first
    RECIPIENT_PATTERNS = {
        # Founder-related (check before generic "community")
        "founder": "LD-FND",
        "strategic founder": "LD-FND",
        "founder partnership": "LD-FND",
        "co-founder": "LD-FND",
        "cofounder": "LD-FND",
        
        # Investor-related
        "investor": "LD-INV",
        "vc": "LD-INV",
        "angel": "LD-INV",
        "funding": "LD-INV",
        "raise": "LD-INV",
        "pitch": "LD-INV",
        
        # Hiring-related
        "hire": "LD-HIR",
        "hiring": "LD-HIR",
        "candidate": "LD-HIR",
        "interview": "LD-HIR",
        "recruit": "LD-HIR",
        
        # Community-related (check after founder patterns)
        "community org": "LD-COM",
        "community group": "LD-COM",
        "community partner": "LD-COM",
        "alumni": "LD-COM",
        "association": "LD-COM",
        "consortium": "LD-COM",
        
        # Networking
        "networking": "LD-NET",
        "network": "LD-NET",
        "coffee chat": "LD-NET",
        "intro": "LD-NET",
        
        # Partnership (ambiguous, default to community unless "founder" also present)
        "partnership": "LD-COM",
        "partner": "LD-COM",
        
        # General fallback
        "general": "LD-GEN",
        "misc": "LD-GEN"
    }
    
    # Legacy simple mapping for direct recipient_type parameter
    RECIPIENT_TYPES = {
        "founder": "LD-FND",
        "investor": "LD-INV",
        "hire": "LD-HIR",
        "hiring": "LD-HIR",
        "candidate": "LD-HIR",
        "community": "LD-COM",
        "networking": "LD-NET",
        "network": "LD-NET",
        "general": "LD-GEN",
        "other": "LD-GEN"
    }
    
    # Urgency now maps to DX system (no '!!')
    URGENCY_MAPPING = {
        # by 1 business day latest
        "urgent": "D1-",
        # by 3 business days latest
        "high": "D3-",
        # that day or later
        "normal": "D3+",
        # next week or later
        "low": "D7+",
    }
    
    PRIORITY_MAPPING = {
        "internal": "GPT-I",
        "external": "GPT-E",
        "founders": "GPT-F",
        "founder": "GPT-F"
    }
    
    def __init__(self):
        self.workspace = Path("/home/workspace")
    
    def generate(
        self,
        recipient_type: Optional[str] = None,
        urgency: Optional[str] = None,
        priority: Optional[str] = None,
        accommodation: Optional[int] = None,
        align_with_logan: bool = False,
        align_with_ilse: bool = False,
        follow_up_days: Optional[int] = None,
        weekend_ok: bool = False,
        weekend_prefer: bool = False,
        flexible: bool = False,
        context: Optional[str] = None,
        dry_run: bool = False
    ) -> HowieTagSet:
        """
        Generate Howie tags based on meeting context
        """
        tags = HowieTagSet()
        
        # Infer from context if provided
        if context:
            context_lower = context.lower()
            
            # Infer recipient type using pattern matching
            # Check longer patterns first (e.g., "founder partnership" before "partnership")
            if not recipient_type:
                sorted_patterns = sorted(
                    self.RECIPIENT_PATTERNS.items(),
                    key=lambda x: len(x[0]),
                    reverse=True  # Longest patterns first
                )
                for pattern, lead_tag in sorted_patterns:
                    if pattern in context_lower:
                        # Map lead tag back to recipient_type for consistent handling
                        recipient_type_map = {
                            "LD-FND": "founder",
                            "LD-INV": "investor",
                            "LD-HIR": "hire",
                            "LD-COM": "community",
                            "LD-NET": "networking",
                            "LD-GEN": "general"
                        }
                        recipient_type = recipient_type_map.get(lead_tag, "general")
                        logger.info(f"Inferred recipient_type={recipient_type} from pattern '{pattern}'")
                        break
            
            # Infer urgency
            if not urgency:
                if any(word in context_lower for word in ["urgent", "asap", "immediately", "emergency"]):
                    urgency = "urgent"
                    logger.info("Inferred urgency=urgent from context")
                elif any(word in context_lower for word in ["soon", "quickly", "this week", "early next week"]):
                    urgency = "high"
                    logger.info("Inferred urgency=high from context")
            
            # Infer priority
            if not priority:
                if any(word in context_lower for word in ["internal", "team", "logan", "ilse"]):
                    priority = "internal"
                    logger.info("Inferred priority=internal from context")
                elif any(word in context_lower for word in ["external", "outside", "client", "customer"]):
                    priority = "external"
                    logger.info("Inferred priority=external from context")
            
            # Infer alignment
            if "logan" in context_lower and not align_with_logan:
                align_with_logan = True
                logger.info("Inferred align_with_logan=True from context")
            if "ilse" in context_lower and not align_with_ilse:
                align_with_ilse = True
                logger.info("Inferred align_with_ilse=True from context")
        
        # Build tag set
        if recipient_type:
            tags.lead_type = self.RECIPIENT_TYPES.get(recipient_type.lower())
        
        # Timeline / urgency
        if urgency:
            urgency_tag = self.URGENCY_MAPPING.get(urgency.lower())
            if urgency_tag:
                tags.scheduling.append(urgency_tag)
        
        if priority:
            tags.priority = self.PRIORITY_MAPPING.get(priority.lower())
        
        if accommodation is not None:
            tags.accommodation = f"A-{accommodation}"
        
        if align_with_logan:
            tags.scheduling.append("LOG")
        
        if align_with_ilse:
            tags.scheduling.append("ILS")
        
        if follow_up_days:
            tags.follow_up.append(f"F-{follow_up_days}")
        
        if flexible:
            tags.special.append("FLX")
        
        if weekend_prefer:
            tags.special.append("WEP")
        elif weekend_ok:
            tags.special.append("WEX")
        
        # Default timeline if none set → D3+
        if not any(t.startswith("D") for t in tags.scheduling):
            tags.scheduling.append("D3+")
        
        if dry_run:
            logger.info(f"[DRY RUN] Generated tags: {tags.to_signature_line()}")
        
        return tags
    
    def create_full_signature(
        self,
        tags: HowieTagSet,
        include_contact_info: bool = True,
        include_social_links: bool = True
    ) -> str:
        """Create a complete email signature with Howie tags"""
        lines = []
        
        # Closing
        lines.append("Best,")
        
        if include_contact_info:
            lines.append("Vrijen S Attawar")
            lines.append("CEO @ Careerspan")
            lines.append("---")
        
        if include_social_links:
            lines.append("👉 Try Careerspan! and Follow us on LinkedIn!")
            lines.append("🤝 Let's connect on Twitter or LinkedIn")
        
        # Howie tags
        tag_line = tags.to_signature_line()
        if tag_line:
            lines.append("")
            lines.append(f"Howie Tags: {tag_line}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Howie V-OS signature tags for emails"
    )
    
    # Core parameters
    parser.add_argument(
        "--recipient-type",
        choices=["investor", "hire", "hiring", "candidate", "community", "partner", "networking", "network", "general", "other"],
        help="Type of recipient for lead categorization"
    )
    parser.add_argument(
        "--urgency",
        choices=["urgent", "high", "normal", "low"],
        help="Urgency level for scheduling (maps to D1-/D3-/D3+/D7+)"
    )
    parser.add_argument(
        "--priority",
        choices=["internal", "external", "founders", "founder"],
        help="Priority level (whose preferences to prioritize)"
    )
    parser.add_argument(
        "--accommodation",
        type=int,
        choices=[0, 1, 2],
        help="Accommodation level (0=our terms, 1=baseline, 2=fully accommodating)"
    )
    
    # Alignment
    parser.add_argument("--align-logan", action="store_true", help="Align with Logan's schedule")
    parser.add_argument("--align-ilse", action="store_true", help="Align with Ilse's schedule")
    
    # Follow-up
    parser.add_argument(
        "--follow-up-days",
        type=int,
        help="Days before Howie sends follow-up reminder"
    )
    
    # Special cases
    parser.add_argument("--weekend-ok", action="store_true", help="Allow weekend extension (WEX)")
    parser.add_argument("--weekend-prefer", action="store_true", help="Prefer weekend scheduling (WEP)")
    parser.add_argument("--flexible", action="store_true", help="Meeting can be shifted within same day (FLX)")
    
    # Context
    parser.add_argument(
        "--context",
        help="Free-form context for intelligent tag inference (e.g., 'urgent investor meeting with Logan')"
    )
    
    # Output
    parser.add_argument("--full-signature", action="store_true", help="Generate full email signature")
    parser.add_argument("--explain", action="store_true", help="Show explanation of each tag")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview without side effects")
    
    args = parser.parse_args()
    
    generator = HowieSignatureGenerator()
    
    tags = generator.generate(
        recipient_type=args.recipient_type,
        urgency=args.urgency,
        priority=args.priority,
        accommodation=args.accommodation,
        align_with_logan=args.align_logan,
        align_with_ilse=args.align_ilse,
        follow_up_days=args.follow_up_days,
        weekend_ok=args.weekend_ok,
        weekend_prefer=args.weekend_prefer,
        flexible=args.flexible,
        context=args.context,
        dry_run=args.dry_run
    )
    
    if args.json:
        output = {
            "tags": tags.to_signature_line(),
            "explanation": tags.get_explanation() if args.explain else None
        }
        print(json.dumps(output, indent=2))
    else:
        if args.full_signature:
            print(generator.create_full_signature(tags))
        else:
            print(tags.to_signature_line())
        
        if args.explain:
            print("\n--- Tag Explanations ---")
            for tag, explanation in tags.get_explanation().items():
                print(f"{tag}: {explanation}")
    
    return 0


if __name__ == "__main__":
    exit(main())
