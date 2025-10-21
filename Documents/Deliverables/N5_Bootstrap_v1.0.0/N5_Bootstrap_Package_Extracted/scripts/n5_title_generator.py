#!/usr/bin/env python3
"""
N5 Thread Title Generator

Auto-generates thread titles based on centralized emoji legend and content analysis.
Follows noun-first principle and UI constraints (18-30 chars target, 35 max).

Usage:
    from n5_title_generator import TitleGenerator
    
    generator = TitleGenerator()
    title_options = generator.generate_titles(aar_data, artifacts)
    selected = generator.interactive_select(title_options)
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).resolve().parents[1]
EMOJI_LEGEND_PATH = ROOT / "config" / "emoji-legend.json"


class TitleGenerator:
    """Generates thread titles using emoji legend and content analysis"""
    
    def __init__(self):
        self.emoji_legend = self._load_emoji_legend()
        self.emojis_by_priority = sorted(
            self.emoji_legend["emojis"],
            key=lambda e: e.get("priority", 0),
            reverse=True
        )
    
    def _load_emoji_legend(self) -> Dict:
        """Load centralized emoji legend"""
        try:
            with open(EMOJI_LEGEND_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Emoji legend not found: {EMOJI_LEGEND_PATH}")
            return {"emojis": [], "usage_contexts": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid emoji legend JSON: {e}")
            return {"emojis": [], "usage_contexts": {}}
    
    def generate_titles(
        self, 
        aar_data: Dict, 
        artifacts: List[Dict],
        max_options: int = 3
    ) -> List[Dict]:
        """
        Generate title options based on thread content
        
        Returns list of dicts with:
        - title: Full formatted title
        - emoji: Selected emoji
        - base_title: Title without emoji
        - reasoning: Why this title/emoji was selected
        - length: Character count
        """
        options = []
        
        # Extract content for analysis
        objective = aar_data.get("objective", "")
        summary = aar_data.get("summary", "")
        decisions = aar_data.get("key_events", [])
        
        # Combine all text for keyword analysis
        all_text = f"{objective} {summary} " + " ".join([
            d.get("description", "") for d in decisions
        ])
        all_text_lower = all_text.lower()
        
        # Phase 1: Extract entities and actions
        entity = self._extract_primary_entity(all_text, aar_data)
        action = self._extract_primary_action(all_text, aar_data)
        sequence_num = self._detect_sequence_number(all_text, artifacts)
        
        # Phase 2: Select emoji based on priority
        selected_emoji, emoji_reasoning = self._select_emoji(all_text_lower, aar_data)
        
        # Phase 3: Format title (noun-first)
        base_titles = self._format_title_variations(
            entity, action, sequence_num, max_variations=max_options
        )
        
        # Phase 4: Build options
        for base_title in base_titles:
            full_title = f"{selected_emoji['symbol']} {base_title}"
            
            options.append({
                "title": full_title,
                "emoji": selected_emoji["symbol"],
                "emoji_name": selected_emoji["name"],
                "base_title": base_title,
                "reasoning": {
                    "emoji": emoji_reasoning,
                    "entity": entity,
                    "action": action,
                    "sequence": sequence_num
                },
                "length": len(full_title),
                "valid": len(full_title) <= 35
            })
        
        # Sort by validity and length (prefer shorter)
        options.sort(key=lambda o: (not o["valid"], o["length"]))
        
        return options[:max_options]
    
    def _extract_primary_entity(self, text: str, aar_data: Dict) -> str:
        """Extract main subject/entity (noun)"""
        text_lower = text.lower()
        
        # Common entities (order matters - most specific first)
        entity_patterns = [
            # System components
            (r'\b(crm|customer relationship)', "CRM"),
            (r'\b(gtm|go[- ]to[- ]market)', "GTM"),
            (r'\b(n5|n5 os|n5 system)', "N5"),
            (r'\b(email system|mail system)', "Email System"),
            (r'\b(meeting system|meeting prep)', "Meeting System"),
            (r'\b(thread|conversation)', "Thread"),
            
            # Content types
            (r'\b(article|blog post)', "Article"),
            (r'\b(persona|profile)', "Persona"),
            (r'\b(command|workflow)', "Command"),
            (r'\b(script|automation)', "Script"),
            (r'\b(dashboard|report)', "Dashboard"),
            (r'\b(linkedin|social media)', "LinkedIn"),
            
            # Business
            (r'\b(stakeholder|contact)', "Stakeholder"),
            (r'\b(opportunity|deal)', "Opportunity"),
            (r'\b(timeline|schedule)', "Timeline"),
            (r'\b(deliverable|output)', "Deliverable"),
        ]
        
        for pattern, entity in entity_patterns:
            if re.search(pattern, text_lower):
                return entity
        
        # Fallback: Extract first capitalized phrase from objective
        objective = aar_data.get("objective", "")
        words = objective.split()
        if words:
            # Find first noun-looking word (capitalized or important)
            for word in words[:5]:  # Check first 5 words
                if len(word) > 3 and (word[0].isupper() or word.lower() in [
                    "system", "process", "workflow", "document", "feature"
                ]):
                    return word.capitalize()
        
        return "System"
    
    def _extract_primary_action(self, text: str, aar_data: Dict) -> str:
        """Extract main action/descriptor"""
        text_lower = text.lower()
        
        # Action patterns (prefer nouns over verbs for brevity)
        action_patterns = [
            # Status/type (noun form)
            (r'\b(refactor|refactoring)', "Refactor"),
            (r'\b(implement|implementation)', "Implementation"),
            (r'\b(setup|set up|setting up)', "Setup"),
            (r'\b(discussion|discussed|discussing)', "Discussion"),
            (r'\b(fix|fixing|bugfix|bug fix)', "Fix"),
            (r'\b(build|building)', "Build"),
            (r'\b(design|designing)', "Design"),
            (r'\b(integration|integrating)', "Integration"),
            (r'\b(migration|migrating)', "Migration"),
            (r'\b(upgrade|upgrading)', "Upgrade"),
            (r'\b(cleanup|cleaning)', "Cleanup"),
            (r'\b(review|reviewing)', "Review"),
            (r'\b(analysis|analyzing)', "Analysis"),
            (r'\b(testing|test)', "Testing"),
            (r'\b(deployment|deploying)', "Deployment"),
            (r'\b(documentation|documenting)', "Docs"),
            (r'\b(planning|plan)', "Planning"),
            (r'\b(research|researching)', "Research"),
            (r'\b(consolidat|consolidation)', "Consolidation"),
            (r'\b(enhancement|enhancing)', "Enhancement"),
        ]
        
        for pattern, action in action_patterns:
            if re.search(pattern, text_lower):
                return action
        
        # Fallback based on artifacts
        if any('script' in a.get('type', '') for a in aar_data.get('artifacts', [])):
            return "Script"
        if any('doc' in a.get('type', '') for a in aar_data.get('artifacts', [])):
            return "Documentation"
        
        return "Work"
    
    def _detect_sequence_number(self, text: str, artifacts: List[Dict]) -> Optional[int]:
        """Detect if this is part of a numbered sequence"""
        text_lower = text.lower()
        
        # Look for explicit numbering
        patterns = [
            r'#(\d+)',
            r'\bpart (\d+)',
            r'\bphase (\d+)',
            r'\bstep (\d+)',
            r'\bv(\d+)',
            r'\bversion (\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        return None
    
    def _select_emoji(self, text_lower: str, aar_data: Dict) -> Tuple[Dict, str]:
        """Select emoji based on priority and detection rules"""
        
        # Check each emoji by priority
        for emoji in self.emojis_by_priority:
            detection_rules = emoji.get("detection_rules", {})
            positive_keywords = detection_rules.get("positive", [])
            negative_keywords = detection_rules.get("negative", [])
            
            # Check negative keywords first (exclusions)
            if any(neg.lower() in text_lower for neg in negative_keywords):
                continue
            
            # Check positive keywords
            if any(pos.lower() in text_lower for pos in positive_keywords):
                reasoning = f"Detected '{emoji['name']}' via keywords: {positive_keywords[:3]}"
                return emoji, reasoning
        
        # Default to completed
        default_emoji = next(
            (e for e in self.emoji_legend["emojis"] if e["name"] == "completed"),
            self.emoji_legend["emojis"][0] if self.emoji_legend["emojis"] else {
                "symbol": "✅", "name": "completed", "priority": 10
            }
        )
        return default_emoji, "Default (no specific indicators detected)"
    
    def _format_title_variations(
        self, 
        entity: str, 
        action: str, 
        sequence_num: Optional[int],
        max_variations: int = 3
    ) -> List[str]:
        """Generate title variations with different formats"""
        variations = []
        
        # Variation 1: Entity + Action + #N
        if sequence_num:
            title = f"{entity} {action} #{sequence_num}"
        else:
            title = f"{entity} {action}"
        variations.append(title)
        
        # Variation 2: Just Entity + #N (if action is generic)
        if action in ["Work", "Discussion", "Implementation"] and sequence_num:
            variations.append(f"{entity} #{sequence_num}")
        
        # Variation 3: Action + Entity (reversed, less preferred)
        if len(variations) < max_variations:
            if sequence_num:
                variations.append(f"{action} {entity} #{sequence_num}")
            else:
                variations.append(f"{action} {entity}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique_variations.append(v)
        
        return unique_variations[:max_variations]
    
    def interactive_select(self, options: List[Dict]) -> Optional[str]:
        """Interactive title selection with preview"""
        if not options:
            return None
        
        print("\n" + "="*70)
        print("📝 THREAD TITLE OPTIONS")
        print("="*70)
        
        for idx, option in enumerate(options, 1):
            print(f"\n{idx}. {option['title']} ({option['length']} chars)")
            print(f"   {option['reasoning']['emoji']}")
            print(f"   Entity: {option['reasoning']['entity']}, Action: {option['reasoning']['action']}")
        
        print(f"\n{len(options) + 1}. Enter custom title")
        print("="*70)
        
        while True:
            choice = input(f"\nSelect title (1-{len(options) + 1}): ").strip()
            
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]['title']
                elif choice_idx == len(options):
                    custom = input("Enter custom title: ").strip()
                    return custom if custom else None
            
            print(f"❌ Invalid choice. Enter 1-{len(options) + 1}")
    
    def generate_next_thread_title(self, current_title: str) -> Optional[str]:
        """Generate title for next thread based on current title
        
        Rules:
        - No number → treat as #1, next is #2
        - Has #N → increment to #(N+1)
        - Keep same emoji if it's 🔗, otherwise use 🔗 for continuation
        - Keep same entity + action
        
        Args:
            current_title: Current thread title (with or without emoji)
            
        Returns:
            Next thread title with proper sequencing
        """
        if not current_title:
            return None
        
        # Extract emoji if present
        emoji_match = re.match(r'^(\S+)\s+(.+)$', current_title)
        if emoji_match:
            current_emoji = emoji_match.group(1)
            title_without_emoji = emoji_match.group(2)
        else:
            current_emoji = None
            title_without_emoji = current_title
        
        # Extract sequence number
        sequence_patterns = [
            (r'#(\d+)$', lambda m: int(m.group(1))),
            (r'\bpart\s+(\d+)$', lambda m: int(m.group(1))),
            (r'\bphase\s+(\d+)$', lambda m: int(m.group(1))),
        ]
        
        current_num = None
        base_title = title_without_emoji
        
        for pattern, extractor in sequence_patterns:
            match = re.search(pattern, title_without_emoji, re.IGNORECASE)
            if match:
                current_num = extractor(match)
                base_title = re.sub(pattern, '', title_without_emoji, flags=re.IGNORECASE).strip()
                break
        
        # Determine next number
        if current_num is None:
            # No number = treat as #1, next is #2
            next_num = 2
        else:
            next_num = current_num + 1
        
        # Determine emoji for next thread
        # Keep 🔗 if current has it, otherwise use 🔗 for continuation
        if current_emoji == '🔗':
            next_emoji = '🔗'
        else:
            # Use chain emoji for linked threads
            next_emoji = '🔗'
        
        # Build next title
        next_title = f"{next_emoji} {base_title} #{next_num}"
        
        return next_title
    
    def generate_auto_title(
        self, 
        aar_data: Dict, 
        artifacts: List[Dict]
    ) -> str:
        """
        Generate title automatically (no user interaction)
        
        Returns best title option
        """
        options = self.generate_titles(aar_data, artifacts, max_options=1)
        if options:
            return options[0]['title']
        
        # Fallback
        return f"✅ Conversation {aar_data.get('archived_date', 'Unknown')}"


def main():
    """Test title generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test thread title generation")
    parser.add_argument("--test", action="store_true", help="Run with test data")
    args = parser.parse_args()
    
    generator = TitleGenerator()
    
    if args.test:
        # Test data
        test_aar = {
            "thread_id": "con_test123",
            "objective": "Refactor CRM system to improve data consistency",
            "summary": "Successfully refactored CRM database schema and migrated data. Fixed several bugs in the profile matching logic.",
            "key_events": [
                {"description": "Decided to use SQLite instead of JSON files"},
                {"description": "Implemented new schema with proper foreign keys"}
            ],
            "artifacts": [
                {"type": "script", "filename": "migrate_crm.py"},
                {"type": "document", "filename": "schema.md"}
            ],
            "archived_date": "2025-10-16"
        }
        
        print("Generating titles for test AAR...")
        options = generator.generate_titles(test_aar, test_aar["artifacts"])
        
        for idx, option in enumerate(options, 1):
            print(f"\nOption {idx}:")
            print(f"  Title: {option['title']}")
            print(f"  Length: {option['length']} chars")
            print(f"  Valid: {option['valid']}")
            print(f"  Reasoning: {option['reasoning']}")
    else:
        print("Use --test to run with test data")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
