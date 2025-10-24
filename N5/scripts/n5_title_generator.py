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


def get_date_prefix(convo_workspace: Path = None, timestamp: str = None) -> str:
    """Extract date and format as 'MMM DD | ' prefix."""
    from datetime import datetime
    
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif convo_workspace:
        # Try to extract from SESSION_STATE or last message
        session_file = convo_workspace / "SESSION_STATE.md"
        if session_file.exists():
            content = session_file.read_text()
            # Extract date from "Started: YYYY-MM-DD" line
            import re
            match = re.search(r'Started:\*\* (\d{4}-\d{2}-\d{2})', content)
            if match:
                dt = datetime.fromisoformat(match.group(1))
            else:
                dt = datetime.now()
        else:
            dt = datetime.now()
    else:
        dt = datetime.now()
    
    return dt.strftime('%b %d | ')


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
        max_options: int = 3,
        convo_workspace: Path = None,
        timestamp: str = None
    ) -> List[Dict]:
        """
        Generate title options based on thread content with date prefix
        
        Returns list of dicts with:
        - title: Full formatted title with date prefix
        - emoji: Selected emoji
        - base_title: Title without emoji or date
        - reasoning: Why this title/emoji was selected
        - length: Character count
        """
        # Get date prefix
        date_prefix = get_date_prefix(convo_workspace, timestamp)
        
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
        
        # Phase 4: Build options with date prefix
        for base_title in base_titles:
            full_title = f"{date_prefix}{selected_emoji['symbol']} {base_title}"
            
            options.append({
                "title": full_title,
                "emoji": selected_emoji["symbol"],
                "emoji_name": selected_emoji["name"],
                "base_title": base_title,
                "date_prefix": date_prefix,
                "reasoning": {
                    "emoji": emoji_reasoning,
                    "entity": entity,
                    "action": action,
                    "sequence": sequence_num
                },
                "length": len(full_title),
                "valid": len(full_title) <= 45  # Increased for date prefix
            })
        
        # Sort by validity and length (prefer shorter)
        options.sort(key=lambda o: (not o["valid"], o["length"]))
        
        return options[:max_options]
    
    def _extract_primary_entity(self, text: str, aar_data: Dict) -> str:
        """Extract main subject/entity (noun) - BE SPECIFIC, avoid generic terms"""
        text_lower = text.lower()
        
        # Phase 1: Scan artifacts for SPECIFIC system names
        artifacts = aar_data.get('artifacts', [])
        specific_systems = []
        
        # Low-signal filters
        def is_low_signal(name: str) -> bool:
            n = name.lower()
            if n.endswith('.log') or n.endswith('.tmp') or n.endswith('.bak'):
                return True
            bad_terms = ['step', 'flow', 'generate', 'legacy', 'test', 'demo', 'sample']
            return any(bt in n for bt in bad_terms)
        
        # Mapping from filename fragments to canonical system names
        component_map = [
            ('content_library', 'Content Library'),
            ('content-library', 'Content Library'),
            ('email_corrections', 'Email Validation'),
            ('email-corrections', 'Email Validation'),
            ('gmail_monitor', 'Gmail Monitor'),
            ('gmail-monitor', 'Gmail Monitor'),
            ('email_registry', 'Email Registry'),
            ('email-registry', 'Email Registry'),
            ('b_block_parser', 'B-Block Parser'),
            ('b-block-parser', 'B-Block Parser'),
            ('email_composer', 'Email Composer'),
            ('email-composer', 'Email Composer'),
            ('n5_follow_up_email_generator', 'Follow-Up Email Generator'),
            ('follow_up_email_generator', 'Follow-Up Email Generator'),
        ]
        
        # First pass: use component_map matches
        for artifact in artifacts:
            fname = str(artifact.get('filename', '') or artifact.get('relative_path', '')).lower()
            if not fname or is_low_signal(fname):
                continue
            for frag, canon in component_map:
                if frag in fname:
                    if canon not in specific_systems:
                        specific_systems.append(canon)
        
        # Second pass: derive names from filenames (capitalized words), still filtered
        if not specific_systems:
            for artifact in artifacts:
                fname = str(artifact.get('filename', '') or artifact.get('relative_path', '')).lower()
                if not fname or is_low_signal(fname):
                    continue
                base = fname.rsplit('.', 1)[0]
                base = base.replace('_', ' ').replace('-', ' ')
                words = [w.capitalize() for w in base.split() if len(w) > 2]
                if words:
                    candidate = ' '.join(words[:3])
                    if candidate and candidate not in ['Script', 'Module', 'File'] and candidate not in specific_systems:
                        specific_systems.append(candidate)
        
        # If we found multiple specific systems, combine them
        if len(specific_systems) >= 2:
            return f"{specific_systems[0]} + {specific_systems[1]}"
        elif len(specific_systems) == 1:
            return specific_systems[0]
        
        # Phase 2: Specific entity patterns (order matters - most specific first)
        entity_patterns = [
            # SPECIFIC system names (from common N5 components)
            (r'\b(akiflow|aki)', "Akiflow Integration"),
            (r'\b(content library|content-library)', "Content Library"),
            (r'\b(email validation|email validator|email-validator)', "Email Validation"),
            (r'\b(meeting parser|meeting-parser)', "Meeting Parser"),
            (r'\b(b-block|bblock)', "B-Block Parser"),
            (r'\b(email composer|email-composer)', "Email Composer"),
            (r'\b(gmail monitor|gmail-monitor)', "Gmail Monitor"),
            (r'\b(email registry|email-registry)', "Email Registry"),
            (r'\b(follow[-_ ]up email generator)', 'Follow-Up Email Generator'),
            (r'\b(crm consolidation|crm-consolidation)', "CRM Consolidation"),
            (r'\b(meeting intelligence|meeting-intelligence)', "Meeting Intelligence"),
            (r'\b(thread export|thread-export)', "Thread Export"),
            (r'\b(timeline automation|timeline-automation)', "Timeline Automation"),
            (r'\b(personal intelligence|personal-intelligence)', "Personal Intelligence"),
            (r'\b(stakeholder enrichment|stakeholder-enrichment)', "Stakeholder Enrichment"),
            
            # Broader but still specific
            (r'\b(crm system)', "CRM System"),
            (r'\b(email system)', "Email System"),
            (r'\b(meeting system)', "Meeting System"),
            (r'\b(n5 os|n5 system)', "N5 OS"),
            
            # Content types (still specific)
            (r'\b(linkedin post|linkedin content)', "LinkedIn Post"),
            (r'\b(system docs?)', "System Docs"),
            (r'\b(command workflow)', "Command Workflow"),
            (r'\b(automation script)', "Automation Script"),
        ]
        
        for pattern, entity in entity_patterns:
            if re.search(pattern, text_lower):
                return entity
        
        # Phase 3: Extract from objective (look for capitalized multi-word phrases)
        objective = aar_data.get("objective", "")
        capitalized_phrases = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', objective)
        if capitalized_phrases:
            return capitalized_phrases[0]
        
        # Last resort fallback - but flag it as generic
        return "System Work"  # This will trigger a warning that title needs improvement
    
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
