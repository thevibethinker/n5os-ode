#!/usr/bin/env python3
"""
Generate store listing JSON from skill metadata.
"""

import json
import re
import argparse
from pathlib import Path


class ListingGenerator:
    def __init__(self):
        self.feature_patterns = [
            r'^\s*[-*+]\s+(.+)$',  # Bullet points
            r'^##\s+Features?\s*$',  # Features section header
            r'^\s*\d+\.\s+(.+)$',   # Numbered lists
        ]
    
    def parse_frontmatter(self, content):
        """Extract YAML frontmatter from markdown"""
        if not content.startswith('---'):
            return {}
        
        try:
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                return {}
            
            frontmatter_text = content[3:end_marker].strip()
            
            # YAML parsing with support for multiline values (| and >-)
            metadata = {}
            lines = frontmatter_text.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                # Skip comments and empty lines
                if line.strip().startswith('#') or not line.strip():
                    i += 1
                    continue
                
                # Check for key: value pair
                if ':' in line:
                    key_part, value_part = line.split(':', 1)
                    key = key_part.strip()
                    value = value_part.strip()
                    
                    # Check for multiline indicators
                    if value in ('|', '>-', '>', '|-', '>+'):
                        # Multiline block - collect all following indented lines
                        multiline_value = []
                        indent_level = None
                        i += 1
                        
                        while i < len(lines):
                            next_line = lines[i]
                            
                            # Stop at next key (unindented or same-level line with :)
                            if next_line.strip() and ':' in next_line:
                                # Check if it's a new top-level key (not indented)
                                if not next_line.startswith(' ') or (next_line.strip().startswith('-') == False):
                                    # Could be a new key - but allow array items
                                    next_key = next_line.split(':', 1)[0].strip()
                                    if next_key and not next_key.startswith('-') and not next_key[0].isdigit():
                                        break
                            
                            # Stop if we hit the frontmatter end or a new section
                            if next_line.strip().startswith('---'):
                                break
                            
                            # Skip empty lines at start
                            if not multiline_value and not next_line.strip():
                                i += 1
                                continue
                            
                            # Add line to multiline value (strip common indentation)
                            stripped = next_line.lstrip()
                            if stripped:
                                multiline_value.append(stripped)
                            else:
                                multiline_value.append('')
                            
                            i += 1
                        
                        # Join multiline lines
                        metadata[key] = ' '.join(multiline_value).strip()
                    elif value.startswith('-'):
                        # Handle inline arrays (key: - item)
                        array_value = [value[1:].strip()]
                        i += 1
                        while i < len(lines) and lines[i].strip().startswith('-'):
                            array_value.append(lines[i].strip()[1:].strip())
                            i += 1
                        metadata[key] = array_value
                    else:
                        # Simple key: value
                        # Remove quotes if present
                        value = value.strip('"\'')
                        metadata[key] = value
                        i += 1
                else:
                    i += 1
            
            return metadata
        except Exception as e:
            print(f"Warning: Frontmatter parsing error: {e}", file=sys.stderr)
            return {}
    
    def extract_features(self, content):
        """Extract features from markdown content"""
        features = []
        lines = content.split('\n')
        in_features_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check for features section header
            if re.match(r'^##\s+(Features?|Capabilities|Benefits)', line, re.IGNORECASE):
                in_features_section = True
                continue
            
            # Stop at next section
            if in_features_section and line.startswith('##'):
                break
            
            # Extract bullet points and numbered items
            if in_features_section or not features:  # Always look for features
                # Bullet points
                bullet_match = re.match(r'^\s*[-*+]\s*\*\*([^*]+)\*\*:\s*(.*)$', line)
                if bullet_match:
                    title = bullet_match.group(1).strip()
                    desc = bullet_match.group(2).strip()
                    features.append(f"{title}: {desc}" if desc else title)
                    continue
                
                # Simple bullet points
                simple_bullet = re.match(r'^\s*[-*+]\s+(.+)$', line)
                if simple_bullet:
                    feature = simple_bullet.group(1).strip()
                    if len(feature) > 10:  # Avoid short/meaningless bullets
                        features.append(feature)
                    continue
                
                # Numbered lists
                numbered = re.match(r'^\s*\d+\.\s+(.+)$', line)
                if numbered:
                    feature = numbered.group(1).strip()
                    if len(feature) > 10:
                        features.append(feature)
        
        # Limit to most relevant features
        return features[:5]
    
    def detect_badges(self, skill_path, metadata, content):
        """Auto-detect badges for the skill"""
        badges = ["zo-optimized"]  # Always included
        
        skill_path = Path(skill_path)
        
        # Check for Claude Code version indicators
        claude_indicators = [
            'claude code', 'cursor', 'claude-code', 'claude_code',
            'adapted for claude', 'cursor compatible'
        ]
        
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in claude_indicators):
            badges.append("claude-code")
        
        # Check for automation badges
        if any(word in content_lower for word in ['automat', 'pipeline', 'workflow']):
            badges.append("automation")
        
        # Check for API integration
        if any(word in content_lower for word in ['api', 'webhook', 'integration']):
            badges.append("integration")
        
        return badges
    
    def generate_listing(self, skill_path):
        """
        Generate store listing JSON from skill directory.
        
        Args:
            skill_path (str): Path to skill directory
            
        Returns:
            dict: Store listing data
        """
        import sys  # Import for stderr output
        
        skill_path = Path(skill_path)
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")
        
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse frontmatter
        metadata = self.parse_frontmatter(content)
        
        # Extract content after frontmatter
        if content.startswith('---'):
            end_marker = content.find('\n---\n', 3)
            if end_marker != -1:
                content = content[end_marker + 5:]
        
        # Generate listing data
        skill_name = metadata.get('name', skill_path.name)
        description = metadata.get('description', '')
        
        # Extract tagline (first sentence of description or first line after title)
        tagline = description
        if not tagline:
            # Look for first substantial line after main title
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            for line in lines[1:]:  # Skip first line (title)
                if not line.startswith('#') and len(line) > 20:
                    tagline = line
                    break
        
        # Truncate tagline if too long
        if len(tagline) > 100:
            tagline = tagline[:97] + "..."
        
        features = self.extract_features(content)
        badges = self.detect_badges(skill_path, metadata, content)
        
        listing = {
            "id": skill_name,
            "name": skill_name.title().replace('-', ' '),
            "tagline": tagline,
            "description": description,
            "features": features,
            "badges": badges
        }
        
        return listing


def main():
    parser = argparse.ArgumentParser(description='Generate store listing JSON from skill')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    generator = ListingGenerator()
    
    try:
        listing = generator.generate_listing(args.skill_path)
        
        if args.pretty:
            output = json.dumps(listing, indent=2)
        else:
            output = json.dumps(listing)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Listing generated: {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())