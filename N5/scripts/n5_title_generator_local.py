#!/usr/bin/env python3
"""
N5 Thread Title Generator - Local Rule-Based Version

Generates contextual, specific titles based on conversation content without external API calls.
Uses pattern matching and content analysis for reliable, fast title generation.

Usage:
    from n5_title_generator_local import TitleGeneratorLocal
    
    generator = TitleGeneratorLocal()
    title = generator.generate_title(aar_data, artifacts, convo_id)
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Paths
ROOT = Path(__file__).resolve().parents[1]
EMOJI_LEGEND_PATH = ROOT / "config" / "emoji-legend.json"


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


class TitleGeneratorLocal:
    """Generates thread titles using local pattern matching"""
    
    def __init__(self):
        self.emoji_legend = self._load_emoji_legend()
        self._build_emoji_map()
    
    def _load_emoji_legend(self) -> Dict:
        """Load centralized emoji legend"""
        try:
            with open(EMOJI_LEGEND_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Emoji legend not found: {EMOJI_LEGEND_PATH}")
            return {"emojis": [{"symbol": "✅", "name": "completed"}], "usage_contexts": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid emoji legend JSON: {e}")
            return {"emojis": [{"symbol": "✅", "name": "completed"}], "usage_contexts": {}}
    
    def _build_emoji_map(self):
        """Build keyword→emoji mapping"""
        self.keyword_emoji_map = {
            # Build/Implementation
            ('build', 'built', 'implement', 'create', 'develop'): ('🏗️', 'build'),
            ('design', 'spec', 'specification', 'architecture', 'plan'): ('🎯', 'design'),
            ('fix', 'fixed', 'debug', 'repair', 'resolve'): ('🔧', 'fix'),
            ('refactor', 'cleanup', 'reorganize', 'restructure'): ('♻️', 'refactor'),
            
            # Documentation
            ('document', 'docs', 'documentation', 'guide'): ('📝', 'docs'),
            ('research', 'investigate', 'explore', 'study', 'analysis'): ('🔬', 'research'),
            
            # Testing/Verification
            ('test', 'testing', 'verify', 'validation'): ('🧪', 'testing'),
            ('review', 'audit', 'check', 'inspection'): ('👁️', 'review'),
            
            # Configuration
            ('config', 'configure', 'setup', 'install'): ('⚙️', 'config'),
            ('deploy', 'deployment', 'release', 'publish'): ('🚀', 'deploy'),
            
            # Data/Content
            ('data', 'dataset', 'database', 'migration'): ('💾', 'data'),
            ('content', 'article', 'post', 'writing'): ('📰', 'content'),
            
            # System/Infrastructure
            ('system', 'infrastructure', 'server', 'service'): ('🖥️', 'system'),
            ('monitor', 'monitoring', 'observability', 'logging'): ('📊', 'monitoring'),
            
            # Process/Workflow
            ('workflow', 'automation', 'pipeline', 'process'): ('⚡', 'automation'),
            ('onboard', 'onboarding', 'setup', 'initialization'): ('🎯', 'onboarding'),
        }
    
    def _select_emoji(self, text: str) -> tuple:
        """Select appropriate emoji based on content keywords"""
        text_lower = text.lower()
        
        for keywords, (emoji, name) in self.keyword_emoji_map.items():
            if any(kw in text_lower for kw in keywords):
                return emoji, name
        
        # Default
        return '✅', 'completed'
    
    def _extract_entities(self, text: str, artifacts: List[Dict]) -> List[str]:
        """Extract key entities/components from text"""
        entities = []
        
        # Common technical entity patterns
        patterns = [
            r'\b(N5[\w-]*)\b',  # N5-related components
            r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b',  # CamelCase
            r'\b(Phase\s+\d+(?:\.\d+)?)\b',  # Phase numbers
            r'\b([A-Z]{2,})\b',  # Acronyms
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        # Extract from artifact names
        for art in artifacts[:3]:
            fname = art.get('filename', art.get('relative_path', ''))
            if fname:
                # Remove extensions and split on separators
                base = Path(fname).stem
                parts = re.split(r'[_-]', base)
                entities.extend([p for p in parts if len(p) > 3 and p not in ['docs', 'test', 'spec']])
        
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for e in entities:
            if e.lower() not in seen:
                seen.add(e.lower())
                unique.append(e)
        
        return unique[:3]  # Top 3
    
    def _build_title_base(self, objective: str, summary: str, entities: List[str]) -> str:
        """Build base title from components"""
        
        # Priority 1: Extract meaningful phrases from objective/summary
        for source in [objective, summary]:
            if not source or len(source) < 15:
                continue
                
            # Try to extract noun phrases that describe the work
            # Look for patterns like "X analysis", "X fix", "X implementation", etc.
            patterns = [
                r'([\w\s-]+(?:analysis|fix|debug|implementation|refactor|build|system))',
                r'(?:analysis|fix|debug|work)\s+(?:of|on|for)\s+([\w\s-]+)',
                r'([\w\s-]+\s+(?:generation|processing|protocol|workflow))',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, source, re.IGNORECASE)
                if matches:
                    candidate = matches[0].strip()
                    # Clean up
                    candidate = re.sub(r'^(the|a|an)\s+', '', candidate, flags=re.IGNORECASE)
                    candidate = re.sub(r'\s+(for|to|in|on|with|and)\s+.*$', '', candidate, flags=re.IGNORECASE)
                    
                    if 10 <= len(candidate) <= 35:
                        return candidate.title()
        
        # Priority 2: Clean objective directly
        if objective and len(objective) > 10:
            obj_clean = re.sub(r'^(build|create|implement|design|fix|debug|update|add|work on)\s+', '', objective, flags=re.IGNORECASE)
            obj_clean = re.sub(r'\s+(for|to|in|on)\s+.*$', '', obj_clean, flags=re.IGNORECASE)
            obj_clean = obj_clean.strip()
            
            if 10 <= len(obj_clean) <= 35:
                # Check it's not just generic words
                generic_words = {'conversation', 'work', 'system', 'discussion', 'session'}
                words = set(obj_clean.lower().split())
                if not words.issubset(generic_words):
                    return obj_clean.title()
        
        # Priority 3: Use entities ONLY if they're not generic filenames
        if entities:
            # Filter out filename patterns
            filtered = [e for e in entities if not re.match(r'^(SESSION|STATE|FINAL|SUMMARY|INDEX|README|DOC)', e, re.IGNORECASE)]
            if filtered:
                if len(filtered) == 1:
                    return filtered[0]
                elif len(filtered) >= 2:
                    return f"{filtered[0]} {filtered[1]}"
        
        # Priority 4: Extract from summary
        if summary:
            key_phrases = re.findall(r'(?:built|created|fixed|designed|implemented)\s+([^.,;]+)', summary, re.IGNORECASE)
            if key_phrases:
                phrase = key_phrases[0].strip()
                if len(phrase) <= 30:
                    return phrase.title()
        
        # Fallback
        return "Conversation"
    
    def generate_title(
        self,
        aar_data: Dict,
        artifacts: List[Dict],
        convo_workspace: Path = None,
        timestamp: str = None,
        convo_id: str = None
    ) -> Dict:
        """
        Generate title using local pattern matching
        
        Returns dict with:
        - title: Full formatted title
        - base_title: Title without date/emoji
        - emoji: Selected emoji
        - reasoning: Why this title was selected
        """
        date_prefix = get_date_prefix(convo_workspace, timestamp)
        
        # Extract content - PRIORITY ORDER MATTERS
        # 1. Try executive_summary.purpose first (most descriptive)
        purpose = aar_data.get("executive_summary", {}).get("purpose", "")
        # 2. Then try objective field
        objective = aar_data.get("objective", "") or aar_data.get("primary_objective", "")
        # 3. Summary and focus for context
        summary = aar_data.get("summary", "") or aar_data.get("final_state", {}).get("summary", "")
        focus = aar_data.get("focus", "")
        
        # Use purpose as primary source if available
        if purpose and len(purpose) > len(objective):
            objective = purpose
        
        # Combine for analysis
        full_text = f"{objective} {summary}"
        
        # Select emoji
        emoji, emoji_name = self._select_emoji(full_text)
        
        # Extract entities
        entities = self._extract_entities(full_text, artifacts)
        
        # Build base title
        base_title = self._build_title_base(objective, summary, entities)
        
        # Truncate if too long
        if len(base_title) > 30:
            base_title = base_title[:27] + "..."
        
        # Build full title
        full_title = f"{date_prefix}{emoji} {base_title}"
        
        # VALIDATION: Check for duplicate consecutive words
        words = base_title.strip().split()
        for i in range(len(words) - 1):
            if words[i].lower() == words[i+1].lower():
                # Duplicate detected - try to extract better title
                logger.warning(f"Duplicate detected in title: '{words[i]} {words[i+1]}'")
                
                # Try alternative sources
                for source_text in [objective, focus, summary]:
                    if len(source_text) > 15:
                        # Clean and extract
                        clean = re.sub(r'^(build|create|implement|work on|working on|discussing)\s+', '', source_text, flags=re.IGNORECASE)
                        clean = re.sub(r'\s+(for|to|in|on|with)\s+.*$', '', clean, flags=re.IGNORECASE)
                        clean = clean.strip()
                        
                        if 10 <= len(clean) <= 40:
                            # Check this doesn't have duplicates
                            clean_words = clean.split()
                            has_dup = any(clean_words[j].lower() == clean_words[j+1].lower() for j in range(len(clean_words)-1) if j+1 < len(clean_words))
                            
                            if not has_dup and len(clean_words) >= 2:
                                base_title = clean.title()
                                full_title = f"{date_prefix}{emoji} {base_title}"
                                logger.info(f"Fixed duplicate title to: {full_title}")
                                break
                break
        
        return {
            "title": full_title,
            "base_title": base_title,
            "emoji": emoji,
            "emoji_name": emoji_name,
            "date_prefix": date_prefix,
            "reasoning": {
                "method": "Local pattern matching",
                "entities": entities,
                "emoji": f"Selected {emoji_name} based on keywords"
            },
            "length": len(full_title),
            "valid": len(full_title) <= 45
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate N5 thread titles (local)")
    parser.add_argument("--aar", required=True, help="Path to AAR JSON file")
    parser.add_argument("--artifacts", help="Path to artifacts JSON file")
    parser.add_argument("--convo-id", help="Conversation ID")
    
    args = parser.parse_args()
    
    # Load AAR data
    with open(args.aar, 'r') as f:
        aar_data = json.load(f)
    
    # Load artifacts if provided
    artifacts = []
    if args.artifacts:
        with open(args.artifacts, 'r') as f:
            artifacts = json.load(f)
    
    # Generate title
    generator = TitleGeneratorLocal()
    result = generator.generate_title(
        aar_data,
        artifacts,
        convo_id=args.convo_id
    )
    
    print(result['title'])
