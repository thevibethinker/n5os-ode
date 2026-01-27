#!/usr/bin/env python3
"""
Package sanitized skills into distribution ZIP files.
"""

import os
import shutil
import argparse
from pathlib import Path
import tempfile
import re


class SkillPackager:
    def __init__(self):
        # Claude Code adaptations
        self.claude_adaptations = [
            # Replace Zo-specific tool calls with generic equivalents
            (r'run_bash_command\(', 'subprocess.run('),
            (r'read_file\(', 'open('),
            (r'create_or_rewrite_file\(', 'with open('),
            
            # Update import statements
            (r'from zo_tools import', '# from zo_tools import'),
            (r'import zo_tools', '# import zo_tools'),
            
            # Generic replacements
            (r'Zo Computer', 'your coding environment'),
            (r'zo\.computer', 'your-domain.com'),
        ]
    
    def adapt_for_claude_code(self, content):
        """Adapt content for Claude Code Cursor compatibility"""
        for pattern, replacement in self.claude_adaptations:
            content = re.sub(pattern, replacement, content)
        return content
    
    def should_adapt_file(self, file_path):
        """Check if file should be adapted for Claude Code"""
        adaptable_extensions = {'.md', '.py', '.js', '.ts'}
        return file_path.suffix.lower() in adaptable_extensions
    
    def create_package(self, skill_path, output_dir, package_name, claude_code=False):
        """
        Create a ZIP package from skill directory.
        
        Args:
            skill_path (str): Path to sanitized skill directory
            output_dir (str): Directory for output ZIP
            package_name (str): Name for the ZIP file (without extension)
            claude_code (bool): Apply Claude Code adaptations
            
        Returns:
            str: Path to created ZIP file
        """
        skill_path = Path(skill_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary working directory for Claude Code version
        if claude_code:
            temp_dir = tempfile.mkdtemp(prefix="claude-adapt-")
            work_path = Path(temp_dir) / skill_path.name
            shutil.copytree(skill_path, work_path)
            
            # Apply Claude Code adaptations
            for root, dirs, files in os.walk(work_path):
                for file in files:
                    file_path = Path(root) / file
                    
                    if self.should_adapt_file(file_path):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            adapted_content = self.adapt_for_claude_code(content)
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(adapted_content)
                                
                        except Exception as e:
                            print(f"Warning: Could not adapt {file_path}: {e}")
            
            source_path = work_path
        else:
            source_path = skill_path
        
        # Create ZIP file
        zip_path = output_dir / f"{package_name}.zip"
        
        # Remove existing ZIP
        if zip_path.exists():
            zip_path.unlink()
        
        # Create the ZIP using shutil
        base_name = str(zip_path.with_suffix(''))
        shutil.make_archive(base_name, 'zip', source_path.parent, source_path.name)
        
        # Clean up temp directory
        if claude_code:
            shutil.rmtree(temp_dir)
        
        return str(zip_path)


def main():
    parser = argparse.ArgumentParser(description='Package skills for distribution')
    parser.add_argument('skill_path', help='Path to sanitized skill directory')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current)')
    parser.add_argument('--claude-code', action='store_true', 
                       help='Create Claude Code Cursor compatible version')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    packager = SkillPackager()
    skill_path = Path(args.skill_path)
    skill_name = skill_path.name.replace('-sanitized', '')
    
    try:
        # Create main Zo-optimized package
        zo_package = packager.create_package(
            args.skill_path, 
            args.output_dir, 
            f"{skill_name}-zo"
        )
        
        packages = [zo_package]
        
        if not args.quiet:
            print(f"✓ Created package: {zo_package}")
        
        # Create Claude Code version if requested
        if args.claude_code:
            claude_package = packager.create_package(
                args.skill_path,
                args.output_dir,
                f"{skill_name}-claude-code",
                claude_code=True
            )
            packages.append(claude_package)
            
            if not args.quiet:
                print(f"✓ Created Claude Code package: {claude_package}")
        
        if args.quiet:
            for package in packages:
                print(package)
                
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())