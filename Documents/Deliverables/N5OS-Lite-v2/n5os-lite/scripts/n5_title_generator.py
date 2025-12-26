#!/usr/bin/env python3
"""
N5 Thread Title Generator - Hybrid Version

Uses local pattern matching by default, with optional LLM enhancement.
Reliable and fast with no external dependencies.

Usage:
    from n5_title_generator import TitleGenerator
    
    generator = TitleGenerator()
    title_options = generator.generate_titles(aar_data, artifacts)
"""

import json
import re
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).resolve().parents[1]
EMOJI_LEGEND_PATH = ROOT / "config" / "emoji-legend.json"

# Configuration: Set to True to enable LLM title generation (slower, requires API)
USE_LLM = False


def get_date_prefix(convo_workspace: Path = None, timestamp: str = None) -> str:
    """Extract date and format as 'MMM DD | ' prefix."""
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif convo_workspace:
        session_file = convo_workspace / "SESSION_STATE.md"
        if session_file.exists():
            content = session_file.read_text()
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
    """Generates thread titles using local pattern matching (with optional LLM enhancement)"""
    
    def __init__(self, use_llm: bool = USE_LLM):
        self.emoji_legend = self._load_emoji_legend()
        self.use_llm = use_llm
        
        # Import local generator
        try:
            from n5_title_generator_local import TitleGeneratorLocal
            self.local_generator = TitleGeneratorLocal()
        except ImportError:
            logger.warning("Local title generator not found, LLM will be required")
            self.local_generator = None
    
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
    
    def _call_llm_for_title(
        self, 
        aar_data: Dict, 
        artifacts: List[Dict],
        emoji_options: str
    ) -> Dict:
        """
        Call LLM to generate contextual title based on conversation content.
        
        Returns dict with:
        - title: Generated title (without date/emoji)
        - emoji_name: Selected emoji name from legend
        - reasoning: Why this title was chosen
        """
        # Build context from AAR
        objective = aar_data.get("objective", "") or aar_data.get("executive_summary", {}).get("purpose", "") or aar_data.get("primary_objective", "")
        summary = aar_data.get("summary", "") or aar_data.get("final_state", {}).get("summary", "")
        key_events = aar_data.get("key_events", [])
        
        # Build artifact summary
        artifact_summary = []
        for art in artifacts[:10]:  # Limit to first 10
            fname = art.get('filename', art.get('relative_path', 'unknown'))
            artifact_summary.append(fname)
        
        # Build prompt for LLM
        prompt = f"""Generate a specific, contextual title for this conversation thread.

CONVERSATION CONTEXT:
Objective: {objective}

Summary: {summary}

Key Events: {', '.join([e.get('description', '') for e in key_events[:5]])}

Artifacts Created: {', '.join(artifact_summary) if artifact_summary else 'None'}

EMOJI OPTIONS:
{emoji_options}

REQUIREMENTS:
1. Title should be 15-30 characters (STRICT - shorter is better)
2. Be SPECIFIC - mention actual system/component names, not generic terms
3. Use noun-first structure (e.g., "Gmail Monitor Fix" not "Fix Gmail Monitor")
4. Select appropriate emoji from options above based on conversation type
5. NO generic titles like "System Work Build" or "Discussion Thread"

OUTPUT FORMAT:
- title: Specific Component Name
- emoji_name: selected_emoji_name
- reasoning: Why this title captures the conversation

Generate title now."""
        
        # Define JSON schema for structured output
        output_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "emoji_name": {"type": "string"},
                "reasoning": {"type": "string"}
            },
            "required": ["title", "emoji_name", "reasoning"]
        }
        
        try:
            # Call zo CLI with correct interface
            result = subprocess.run(
                ['zo', prompt, '--output-format', json.dumps(output_schema)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse JSON response from LLM
                response_text = result.stdout.strip()
                return json.loads(response_text)
            else:
                logger.error(f"LLM call failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("LLM call timed out")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"Response was: {result.stdout}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {e}")
            return None
    
    def generate_titles(
        self, 
        aar_data: Dict, 
        artifacts: List[Dict],
        max_options: int = 3,
        convo_workspace: Path = None,
        timestamp: str = None,
        convo_id: str = None
    ) -> List[Dict]:
        """
        Generate title options using local pattern matching (or optional LLM)
        
        Returns list of dicts with:
        - title: Full formatted title with date prefix and emoji
        - emoji: Selected emoji symbol
        - base_title: Title without emoji or date
        - reasoning: Why this title was selected
        - length: Character count
        """
        # Try local generator first (fast, reliable)
        if self.local_generator:
            try:
                result = self.local_generator.generate_title(
                    aar_data,
                    artifacts,
                    convo_workspace=convo_workspace,
                    timestamp=timestamp,
                    convo_id=convo_id
                )
                return [result]
            except Exception as e:
                logger.error(f"Local title generation failed: {e}")
        
        # If USE_LLM is enabled, try LLM generation
        if self.use_llm:
            date_prefix = get_date_prefix(convo_workspace, timestamp)
            
            # Build emoji options string for LLM
            emoji_options = []
            for emoji in self.emoji_legend.get("emojis", []):
                emoji_options.append(
                    f"- {emoji['symbol']} ({emoji['name']}): {emoji.get('description', 'N/A')}"
                )
            emoji_options_str = "\n".join(emoji_options)
            
            # Call LLM for title generation
            llm_result = self._call_llm_for_title(aar_data, artifacts, emoji_options_str)
            
            if llm_result and "title" in llm_result:
                # Find selected emoji
                selected_emoji = next(
                    (e for e in self.emoji_legend["emojis"] if e["name"] == llm_result.get("emoji_name")),
                    self.emoji_legend["emojis"][0] if self.emoji_legend["emojis"] else {"symbol": "✅", "name": "completed"}
                )
                
                base_title = llm_result["title"]
                full_title = f"{date_prefix}{selected_emoji['symbol']} {base_title}"
                
                return [{
                    "title": full_title,
                    "emoji": selected_emoji["symbol"],
                    "emoji_name": selected_emoji["name"],
                    "base_title": base_title,
                    "date_prefix": date_prefix,
                    "reasoning": {
                        "method": "LLM-generated",
                        "explanation": llm_result.get("reasoning", ""),
                        "emoji": f"Selected {selected_emoji['name']}"
                    },
                    "length": len(full_title),
                    "valid": len(full_title) <= 45
                }]
        
        # Final fallback
        logger.warning("All title generation methods failed, using basic fallback")
        date_prefix = get_date_prefix(convo_workspace, timestamp)
        return self._generate_fallback_titles(aar_data, artifacts, date_prefix, convo_id)
    
    def _generate_fallback_titles(
        self,
        aar_data: Dict,
        artifacts: List[Dict],
        date_prefix: str,
        convo_id: str = None
    ) -> List[Dict]:
        """Fallback title generation if LLM call fails"""
        # Extract basic info
        objective = aar_data.get("objective", "") or aar_data.get("executive_summary", {}).get("purpose", "")
        
        # Use first artifact name if available
        entity = "Conversation"
        if artifacts:
            fname = artifacts[0].get('filename', artifacts[0].get('relative_path', ''))
            if fname:
                entity = Path(fname).stem.replace('_', ' ').replace('-', ' ').title()[:20]
        
        # Default emoji
        default_emoji = next(
            (e for e in self.emoji_legend["emojis"] if e["name"] == "completed"),
            {"symbol": "✅", "name": "completed"}
        )
        
        base_title = entity
        full_title = f"{date_prefix}{default_emoji['symbol']} {base_title}"
        
        return [{
            "title": full_title,
            "emoji": default_emoji["symbol"],
            "emoji_name": default_emoji["name"],
            "base_title": base_title,
            "date_prefix": date_prefix,
            "reasoning": {
                "method": "Fallback",
                "explanation": "LLM generation failed",
                "emoji": "Default"
            },
            "length": len(full_title),
            "valid": len(full_title) <= 45
        }]
    
    def interactive_select(self, options: List[Dict]) -> Optional[str]:
        """Interactive title selection with preview"""
        if not options:
            return None
        
        print("\n" + "="*70)
        print("📝 THREAD TITLE OPTIONS")
        print("="*70)
        
        for idx, option in enumerate(options, 1):
            print(f"\n{idx}. {option['title']} ({option['length']} chars)")
            reasoning = option['reasoning']
            print(f"   Method: {reasoning.get('method', 'N/A')}")
            print(f"   {reasoning.get('explanation', 'N/A')}")
        
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
        """Generate title for next thread based on current title"""
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
        next_num = 2 if current_num is None else current_num + 1
        
        # Use continuation emoji if not already using one
        continuation_emoji = "🔗"
        if current_emoji and current_emoji == continuation_emoji:
            next_emoji = current_emoji
        else:
            next_emoji = continuation_emoji
        
        # Build next title
        next_title = f"{next_emoji} {base_title} #{next_num}"
        return next_title


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate N5 thread titles")
    parser.add_argument("--aar", required=True, help="Path to AAR JSON file")
    parser.add_argument("--artifacts", help="Path to artifacts JSON file")
    parser.add_argument("--convo-id", help="Conversation ID")
    parser.add_argument("--interactive", action="store_true", help="Interactive selection")
    
    args = parser.parse_args()
    
    # Load AAR data
    with open(args.aar, 'r') as f:
        aar_data = json.load(f)
    
    # Load artifacts if provided
    artifacts = []
    if args.artifacts:
        with open(args.artifacts, 'r') as f:
            artifacts = json.load(f)
    
    # Generate titles
    generator = TitleGenerator()
    options = generator.generate_titles(
        aar_data, 
        artifacts,
        convo_id=args.convo_id
    )
    
    # Select title
    if args.interactive:
        selected = generator.interactive_select(options)
        if selected:
            print(f"\n✅ Selected: {selected}")
    else:
        if options:
            print(options[0]['title'])
