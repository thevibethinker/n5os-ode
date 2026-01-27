#!/usr/bin/env python3
"""
Main orchestrator for skill export pipeline.
Sanitizes, generates listings, and packages skills for store distribution.
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path
import subprocess
import shutil


class SkillExporter:
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.script_dir = Path(__file__).parent
    
    def log(self, message):
        """Log message if verbose mode enabled"""
        if self.verbose:
            print(message, file=sys.stderr)
    
    def run_script(self, script_name, args, capture_output=False):
        """Run a pipeline script with given arguments"""
        script_path = self.script_dir / script_name
        cmd = [sys.executable, str(script_path)] + args
        
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Script {script_name} failed: {result.stderr}")
            return result.stdout.strip()
        else:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                raise RuntimeError(f"Script {script_name} failed")
    
    def export_skill(self, skill_slug, output_dir=None, claude_code=False):
        """
        Export a skill through the complete pipeline.
        
        Args:
            skill_slug (str): Name of skill to export
            output_dir (str): Output directory for packages
            claude_code (bool): Also create Claude Code version
            
        Returns:
            dict: Export results with paths and listing data
        """
        # Resolve skill directory
        skill_dir = Path("/home/workspace/Skills") / skill_slug
        if not skill_dir.exists():
            raise FileNotFoundError(f"Skill not found: {skill_dir}")
        
        # Set default output directory
        if not output_dir:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"Exporting skill: {skill_slug}")
        self.log(f"Source: {skill_dir}")
        self.log(f"Output: {output_dir}")
        
        # Step 1: Sanitize the skill
        self.log("Step 1: Sanitizing skill...")
        temp_dir = tempfile.mkdtemp(prefix="skill-export-")
        
        try:
            sanitized_path = self.run_script(
                "sanitize.py", 
                [str(skill_dir), "--output-dir", temp_dir, "--quiet"],
                capture_output=True
            )
            
            self.log(f"✓ Sanitized: {sanitized_path}")
            
            # Step 2: Generate listing
            self.log("Step 2: Generating store listing...")
            listing_json = self.run_script(
                "generate_listing.py",
                [sanitized_path],
                capture_output=True
            )
            
            listing_data = json.loads(listing_json)
            self.log(f"✓ Generated listing for: {listing_data['name']}")
            
            # Step 3: Package the skill
            self.log("Step 3: Creating packages...")
            package_args = [
                sanitized_path,
                "--output-dir", str(output_dir),
                "--quiet"
            ]
            
            if claude_code:
                package_args.append("--claude-code")
            
            package_paths = self.run_script(
                "package.py",
                package_args,
                capture_output=True
            ).split('\n')
            
            packages = [path.strip() for path in package_paths if path.strip()]
            
            for package in packages:
                self.log(f"✓ Created: {Path(package).name}")
            
            return {
                "skill": skill_slug,
                "listing": listing_data,
                "packages": packages,
                "sanitized_path": sanitized_path
            }
            
        finally:
            # Clean up temp directory
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)


def main():
    parser = argparse.ArgumentParser(
        description='Export Zo skills for store distribution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 export.py pulse
  python3 export.py meeting-ingestion --output-dir ./packages
  python3 export.py thread-close --claude-code
        """
    )
    
    parser.add_argument('skill_slug', help='Name of skill to export (e.g., "pulse")')
    parser.add_argument('--output-dir', help='Output directory for packages (default: current)')
    parser.add_argument('--claude-code', action='store_true', 
                       help='Also create Claude Code Cursor compatible version')
    parser.add_argument('--quiet', action='store_true', help='Only output listing JSON')
    
    args = parser.parse_args()
    
    exporter = SkillExporter(verbose=not args.quiet)
    
    try:
        result = exporter.export_skill(
            args.skill_slug,
            args.output_dir,
            args.claude_code
        )
        
        # Output listing JSON to stdout for D1.2 to consume
        print(json.dumps(result["listing"], indent=2 if not args.quiet else None))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())