#!/usr/bin/env python3
"""
Skill sanitization script for store distribution.
Removes sensitive data and makes skills distribution-ready.
"""

import os
import re
import shutil
import tempfile
import argparse
from pathlib import Path


class SkillSanitizer:
    def __init__(self):
        # Patterns to sanitize (order matters - more specific first)
        self.patterns = [
            # Absolute paths - use word boundary approach
            (r'/home/workspace/', './'),
            (r'/home/workspace([/\s"\')]|$)', r'.\1'),
            (r'/home/\.z/[^/\s]*/([/\s"\')]|$)', r'./\1'),
            
            # N5 internal systems  
            (r"N5/", "scripts/"),
            (r"file 'N5/[^']*'", "file 'scripts/config.md'"),
            
            # API keys and secrets (more specific patterns first)
            (r'sk-[A-Za-z0-9]{48,}', '<YOUR_OPENAI_API_KEY>'),
            (r'FILLOUT_SECRET_[A-Z0-9_]*', '<YOUR_FILLOUT_SECRET>'),
            (r'GOOGLE_[A-Z_]*KEY', '<YOUR_GOOGLE_KEY>'),
            (r'OPENAI_API_KEY\s*=\s*["\']?[A-Za-z0-9_-]+["\']?', 'OPENAI_API_KEY = "<YOUR_OPENAI_API_KEY>"'),
            
            # Personal identifiers (emails)
            (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '<YOUR_EMAIL>'),
            
            # Phone numbers (various formats)
            (r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', '<YOUR_PHONE>'),
            
            # Zo-specific webhooks and URLs
            (r'https://[^/]*\.zo\.computer/[^\s\'\"]*', '<YOUR_WEBHOOK_URL>'),
            (r'https://[^/]*\.zocomputer\.io/[^\s\'\"]*', '<YOUR_WEBHOOK_URL>'),
            (r'va\.zo\.computer', '<YOUR_DOMAIN>'),
            (r'https://api\.zo\.computer/zo/ask', '<YOUR_ZO_ASK_ENDPOINT>'),
        ]
    
    def _looks_like_key(self, text):
        """Check if a string looks like an API key"""
        if len(text) < 20:
            return False
        # Mix of letters and numbers, mostly random-looking
        has_letters = bool(re.search(r'[a-zA-Z]', text))
        has_numbers = bool(re.search(r'[0-9]', text))
        return has_letters and has_numbers
    
    def sanitize_content(self, content):
        """Apply sanitization patterns to text content"""
        for pattern, replacement in self.patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        return content
    
    def should_sanitize_file(self, file_path):
        """Check if file should be sanitized (text files only)"""
        text_extensions = {'.md', '.py', '.js', '.ts', '.json', '.yaml', '.yml', 
                          '.txt', '.sh', '.bash', '.zsh', '.fish'}
        return file_path.suffix.lower() in text_extensions
    
    def sanitize_skill(self, skill_path, output_dir=None):
        """
        Sanitize a skill directory, creating a clean copy.
        
        Args:
            skill_path (str): Path to skill directory
            output_dir (str): Output directory (default: temp dir)
            
        Returns:
            str: Path to sanitized skill directory
        """
        skill_path = Path(skill_path)
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill directory not found: {skill_path}")
        
        if not (skill_path / "SKILL.md").exists():
            raise ValueError(f"Not a valid skill directory (no SKILL.md): {skill_path}")
        
        # Create output directory
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            sanitized_dir = output_dir / f"{skill_path.name}-sanitized"
        else:
            temp_dir = tempfile.mkdtemp(prefix="skill-sanitize-")
            sanitized_dir = Path(temp_dir) / skill_path.name
        
        # Copy skill directory
        if sanitized_dir.exists():
            shutil.rmtree(sanitized_dir)
        shutil.copytree(skill_path, sanitized_dir)
        
        # Sanitize text files
        for root, dirs, files in os.walk(sanitized_dir):
            for file in files:
                file_path = Path(root) / file
                
                if self.should_sanitize_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        sanitized_content = self.sanitize_content(content)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(sanitized_content)
                            
                    except UnicodeDecodeError:
                        # Skip binary files that got through
                        continue
                    except Exception as e:
                        print(f"Warning: Could not sanitize {file_path}: {e}")
        
        return str(sanitized_dir)


def main():
    parser = argparse.ArgumentParser(description='Sanitize skills for store distribution')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--output-dir', help='Output directory for sanitized skill')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    sanitizer = SkillSanitizer()
    
    try:
        sanitized_path = sanitizer.sanitize_skill(args.skill_path, args.output_dir)
        
        if not args.quiet:
            print(f"✓ Sanitized skill: {sanitized_path}")
        else:
            print(sanitized_path)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())