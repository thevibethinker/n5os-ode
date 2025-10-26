#!/usr/bin/env python3
"""
Email Composer — Generate follow-up emails with smart resource injection
Implements Phase 2 of Content Library integration

Separates:
1. Resources explicitly/implicitly referenced (priority in draft)
2. Suggested resources (separate section, lower priority)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime, UTC

sys.path.insert(0, str(Path(__file__).parent))
from content_library import ContentLibrary
from b_block_parser import ResourceReference, EloquentLine

# Import Howie signature generator
try:
    from howie_signature_generator import HowieSignatureGenerator, HowieTagSet
    HOWIE_AVAILABLE = True
except ImportError:
    HOWIE_AVAILABLE = False
    logger.warning("Howie signature generator not available")

logger = logging.getLogger(__name__)


@dataclass
class EmailSection:
    """A section of the email"""
    heading: str
    content: List[str]
    priority: int = 5  # Lower = higher priority


class EmailComposer:
    """Compose follow-up emails with smart content injection"""
    
    def __init__(self, voice_config: Optional[Dict] = None):
        self.content_library = ContentLibrary()
        self.voice_config = voice_config or {}
        
    def compose_email(
        self,
        recipient_name: str,
        meeting_summary: str,
        resources_explicit: List[ResourceReference],
        resources_suggested: List[ResourceReference],
        eloquent_lines: List[EloquentLine],
        key_decisions: List[str],
        action_items: List[str],
        recipient_type: Optional[str] = None,
        urgency: Optional[str] = None,
        meeting_context: Optional[str] = None,
        generate_howie_tags: bool = True,
        **kwargs
    ) -> str:
        """
        Compose complete follow-up email
        
        Structure:
        1. Greeting + opening hook
        2. Key recap (decisions, resonant moments)
        3. Resources referenced (explicit only in main body)
        4. Action items / next steps
        5. Optional: Additional resources (suggested)
        6. Signature (with optional Howie tags)
        """
        sections = []
        
        # 1. Opening
        opening = self._compose_opening(recipient_name, meeting_summary, eloquent_lines)
        sections.append(EmailSection("Opening", [opening], priority=1))
        
        # 2. Key recap
        if key_decisions or eloquent_lines:
            recap = self._compose_recap(key_decisions, eloquent_lines)
            sections.append(EmailSection("Recap", recap, priority=2))
        
        # 3. Resources referenced (explicit only)
        if resources_explicit:
            resources = self._compose_explicit_resources(resources_explicit)
            sections.append(EmailSection("Resources", resources, priority=3))
        
        # 4. Action items
        if action_items:
            actions = self._compose_action_items(action_items)
            sections.append(EmailSection("Next Steps", actions, priority=4))
        
        # 5. Suggested resources (separate, optional)
        if resources_suggested:
            suggested = self._compose_suggested_resources(resources_suggested)
            sections.append(EmailSection("Additional Resources", suggested, priority=6))
        
        # 6. Signature with optional Howie tags
        howie_tags = None
        if generate_howie_tags and HOWIE_AVAILABLE:
            howie_tags = self._generate_howie_tags(
                context=meeting_context or meeting_summary,  # changed from meeting_context=
                recipient_type=recipient_type,
                urgency=urgency,
                has_action_items=bool(action_items)
            )
        
        signature = self._compose_signature(howie_tags=howie_tags)
        sections.append(EmailSection("Signature", [signature], priority=10))
        
        # Assemble email
        return self._assemble_email(sections)
    
    def _compose_opening(
        self,
        recipient_name: str,
        meeting_summary: str,
        eloquent_lines: List[EloquentLine]
    ) -> str:
        """Compose opening with optional hook from eloquent line"""
        lines = [f"Hey {recipient_name},"]
        
        # Check if we have a particularly good hook from eloquent lines
        if eloquent_lines and eloquent_lines[0].audience_reaction == "positive":
            hook = eloquent_lines[0].cleaned_text
            # Use first sentence as hook if short enough
            first_sentence = hook.split('.')[0] + '.'
            if len(first_sentence) < 150:
                lines.append(f"\n{first_sentence}")
        
        lines.append(f"\n{meeting_summary}")
        
        return "\n".join(lines)
    
    def _compose_recap(
        self,
        key_decisions: List[str],
        eloquent_lines: List[EloquentLine]
    ) -> List[str]:
        """Compose recap section"""
        lines = ["\n**Quick recap from our conversation:**\n"]
        
        # Add key decisions
        for decision in key_decisions[:3]:
            lines.append(f"- {decision}")
        
        return lines
    
    def _compose_explicit_resources(
        self,
        resources: List[ResourceReference]
    ) -> List[str]:
        """
        Compose resources section - EXPLICIT ONLY
        These were mentioned/referenced in conversation
        """
        lines = ["\n**Resources we discussed:**\n"]
        
        # Group by confidence
        explicit = [r for r in resources if r.confidence == "explicit"]
        implicit = [r for r in resources if r.confidence == "implicit"]
        
        # Add explicit resources first
        for res in explicit[:5]:  # Max 5
            if res.title and res.content:
                lines.append(f"- [{res.title}]({res.content})")
            elif res.content.startswith("http"):
                lines.append(f"- {res.content}")
            else:
                lines.append(f"- {res.title or res.content}")
        
        # Add implicit if any
        if implicit:
            lines.append("\n*Also mentioned:*")
            for res in implicit[:3]:
                lines.append(f"- {res.content}")
        
        return lines
    
    def _compose_action_items(self, actions: List[str]) -> List[str]:
        """Compose action items section"""
        lines = ["\n**Next steps:**\n"]
        
        for action in actions[:5]:
            lines.append(f"- {action}")
        
        return lines
    
    def _compose_suggested_resources(
        self,
        resources: List[ResourceReference]
    ) -> List[str]:
        """
        Compose suggested resources section
        These were NOT mentioned but might be helpful
        """
        lines = ["\n**Additional resources that might be helpful:**\n"]
        lines.append("*(These weren't discussed but seem relevant based on our conversation)*\n")
        
        for res in resources[:3]:  # Max 3 suggestions
            if res.title and res.content:
                lines.append(f"- [{res.title}]({res.content})")
                if res.context:
                    lines.append(f"  *{res.context}*")
            elif res.content.startswith("http"):
                lines.append(f"- {res.content}")
            else:
                lines.append(f"- {res.title or res.content}")
        
        return lines
    
    def _compose_signature(self, howie_tags: Optional['HowieTagSet'] = None) -> str:
        """Compose email signature from Content Library with optional Howie tags"""
        # Search for signature snippet
        signatures = self.content_library.search(
            query=None,
            tags={"purpose": ["signature"], "channel": ["email"]}
        )
        
        sig_parts = []
        
        if signatures:
            sig = signatures[0]
            # Update last_used
            sig.metadata["last_used"] = self._now_iso()
            self.content_library.upsert(sig)
            # Fix newline escaping
            content = sig.content.replace("\\n", "\n")
            sig_parts.append(f"\n{content}")
        else:
            # Fallback
            sig_parts.append("\nBest,\nVrijen")
        
        # Add Howie tags if provided
        if howie_tags and HOWIE_AVAILABLE:
            tag_line = howie_tags.to_signature_line()
            if tag_line:
                sig_parts.append(f"\nHowie Tags: {tag_line}")
        
        return "\n".join(sig_parts)
    
    def _generate_howie_tags(
        self,
        context: Optional[str] = None,
        recipient_type: Optional[str] = None,
        urgency: Optional[str] = None,
        priority: Optional[str] = None,
        has_action_items: bool = False,
        **kwargs
    ) -> Optional['HowieTagSet']:
        """
        Generate intelligent Howie V-OS tags based on meeting context
        
        Args:
            context: Free-form context (e.g., "investor meeting with Logan")
            recipient_type: Type (investor, hire, community, networking, general)
            urgency: Urgency level (urgent, high, normal, low)
            priority: Priority (internal, external, founders)
            has_action_items: Whether there are action items (affects follow-up)
            **kwargs: Additional parameters for HowieSignatureGenerator
        
        Returns:
            HowieTagSet or None if generator not available
        """
        if not HOWIE_AVAILABLE:
            logger.warning("Howie signature generator not available")
            return None
        
        generator = HowieSignatureGenerator()
        
        # Infer follow-up days if action items exist
        follow_up_days = 5 if has_action_items else None
        
        tags = generator.generate(
            context=context,  # not meeting_context
            recipient_type=recipient_type,
            urgency=urgency,
            priority=priority,
            follow_up_days=follow_up_days,
            **kwargs
        )
        
        return tags
    
    def _assemble_email(self, sections: List[EmailSection]) -> str:
        """Assemble final email from sections"""
        # Sort by priority
        sections.sort(key=lambda s: s.priority)
        
        email_parts = []
        for section in sections:
            if section.heading == "Opening" or section.heading == "Signature":
                # No heading for opening and signature
                email_parts.extend(section.content)
            else:
                # Add heading
                email_parts.append(f"\n{section.heading}:")
                email_parts.extend(section.content)
        
        return "\n".join(email_parts)
    
    def _now_iso(self) -> str:
        """Current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")


if __name__ == "__main__":
    import argparse
    import json
    from b_block_parser import BBlockParser
    
    parser = argparse.ArgumentParser(description="Compose follow-up email from B-blocks")
    parser.add_argument("blocks_json", help="Path to B-blocks JSON file")
    parser.add_argument("--recipient", required=True, help="Recipient name")
    parser.add_argument("--summary", required=True, help="Meeting summary")
    parser.add_argument("--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Load blocks
    with open(args.blocks_json, 'r') as f:
        blocks = json.load(f)
    
    # Convert back to dataclasses
    resources_explicit = [ResourceReference(**r) for r in blocks["resources_explicit"]]
    resources_suggested = [ResourceReference(**r) for r in blocks["resources_suggested"]]
    eloquent_lines = [EloquentLine(**e) for e in blocks["eloquent_lines"]]
    
    # Compose email
    composer = EmailComposer()
    email = composer.compose_email(
        recipient_name=args.recipient,
        meeting_summary=args.summary,
        resources_explicit=resources_explicit,
        resources_suggested=resources_suggested,
        eloquent_lines=eloquent_lines,
        key_decisions=blocks["key_decisions"],
        action_items=blocks["action_items"]
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(email)
    else:
        print(email)
