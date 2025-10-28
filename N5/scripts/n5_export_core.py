#!/usr/bin/env python3
"""
N5 Core Export Script
Exports V's N5 changes to n5os-core GitHub repo for distribution

Usage:
    python3 N5/scripts/n5_export_core.py [--dry-run] [--push]
"""

import argparse
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import yaml
import glob

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

class N5CoreExporter:
    def __init__(self, source_root: str, dest_root: str, dry_run: bool = False):
        self.source_root = Path(source_root)
        self.dest_root = Path(dest_root)
        self.dry_run = dry_run
        self.manifest_path = Path(source_root) / "N5/config/export_core_manifest.yaml"
        self.manifest = self._load_manifest()
        self.destination = Path(self.manifest["destination"])
        self.stats = {"files_copied": 0, "files_modified": 0, "errors": 0}
    
    def _load_manifest(self) -> Dict:
        """Load export manifest configuration"""
        if not self.manifest_path.exists():
            logger.error(f"Manifest not found: {self.manifest_path}")
            raise FileNotFoundError(f"Missing: {self.manifest_path}")
        
        with open(self.manifest_path) as f:
            return yaml.safe_load(f)
    
    def verify_destination(self) -> bool:
        """Verify n5os-core repo is ready"""
        if not self.destination.exists():
            logger.error(f"Destination not found: {self.destination}")
            return False
        
        # Check if git repo
        if not (self.destination / ".git").exists():
            logger.error(f"Not a git repo: {self.destination}")
            return False
        
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.destination,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            logger.warning(f"n5os-core has uncommitted changes:")
            logger.warning(result.stdout)
            if not self.dry_run:
                response = input("Continue? (yes/no): ")
                if response.lower() != "yes":
                    return False
        
        logger.info(f"✓ Destination ready: {self.destination}")
        return True
    
    def generify_content(self, content: str) -> str:
        """Replace V-specific strings with generic placeholders"""
        replacements = self.manifest["replacements"]
        
        # Apply path replacements
        for old, new in replacements.get("paths", {}).items():
            content = content.replace(old, new)
        
        # Apply personal replacements
        for old, new in replacements.get("personal", {}).items():
            content = content.replace(old, new)
        
        return content
    
    def should_exclude(self, file_path: str) -> bool:
        """Check if file matches exclude patterns"""
        exclude_patterns = self.manifest.get("exclude_patterns", [])
        for pattern in exclude_patterns:
            if glob.fnmatch.fnmatch(file_path, pattern):
                return True
        return False
    
    def export_component(self, component_type: str, patterns: List[str]) -> int:
        """Export a component group"""
        logger.info(f"\n→ Exporting {component_type}...")
        files_copied = 0
        
        for pattern in patterns:
            # Expand glob pattern
            pattern_path = self.source_root / pattern
            
            if "*" in pattern:
                # Glob pattern
                files = list(Path(self.source_root).glob(pattern))
            else:
                # Single file
                files = [pattern_path] if pattern_path.exists() else []
            
            for src_file in files:
                # Check exclude
                if self.should_exclude(str(src_file)):
                    logger.info(f"  ⊗ Excluded: {src_file.relative_to(self.source_root)}")
                    continue
                
                # Calculate destination path
                rel_path = src_file.relative_to(self.source_root)
                dest_file = self.destination / rel_path
                
                # Read and generify
                try:
                    if src_file.suffix in [".md", ".py", ".yaml", ".json", ".sh"]:
                        content = src_file.read_text()
                        generified = self.generify_content(content)
                        
                        if self.dry_run:
                            logger.info(f"  [DRY RUN] Would copy: {rel_path}")
                        else:
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            dest_file.write_text(generified)
                            logger.info(f"  ✓ Copied: {rel_path}")
                        
                        files_copied += 1
                    else:
                        # Binary file - copy as-is
                        if self.dry_run:
                            logger.info(f"  [DRY RUN] Would copy: {rel_path}")
                        else:
                            dest_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(src_file, dest_file)
                            logger.info(f"  ✓ Copied: {rel_path}")
                        
                        files_copied += 1
                
                except Exception as e:
                    logger.error(f"  ✗ Error copying {rel_path}: {e}")
                    self.stats["errors"] += 1
        
        return files_copied
    
    def run_export(self) -> bool:
        """Execute full export"""
        logger.info(f"{'='*60}")
        logger.info("N5 Core Export")
        logger.info(f"Workspace: {self.source_root}")
        logger.info(f"Destination: {self.destination}")
        logger.info(f"Dry Run: {self.dry_run}")
        logger.info(f"{'='*60}\n")
        
        # Verify
        if not self.verify_destination():
            logger.error("✗ Destination verification failed")
            return False
        
        # Export each component group
        components = self.manifest.get("components", {})
        for component_type, patterns in components.items():
            count = self.export_component(component_type, patterns)
            self.stats["files_copied"] += count
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Export {'[DRY RUN] ' if self.dry_run else ''}Complete")
        logger.info(f"Files copied: {self.stats['files_copied']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"{'='*60}\n")
        
        return self.stats["errors"] == 0
    
    def git_commit_push(self, auto_push: bool = False) -> bool:
        """Commit and optionally push changes"""
        if self.dry_run:
            logger.info("[DRY RUN] Would commit and push to git")
            return True
        
        try:
            # Add all changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.destination,
                check=True
            )
            
            # Commit
            commit_msg = f"Update core from V's N5 - {datetime.now().strftime('%Y-%m-%d')}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.destination,
                check=True
            )
            logger.info(f"✓ Committed: {commit_msg}")
            
            # Push
            if auto_push:
                subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=self.destination,
                    check=True
                )
                logger.info("✓ Pushed to GitHub")
            else:
                logger.info("⚠ Not pushed. Run 'git push' in n5os-core to publish")
            
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Git operation failed: {e}")
            return False
    
    def update_manifest_timestamp(self):
        """Update last_export timestamp in manifest"""
        if self.dry_run:
            logger.info("[DRY RUN] Would update manifest timestamp")
            return
        
        self.manifest["last_export"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.manifest_path, "w") as f:
            yaml.dump(self.manifest, f, default_flow_style=False)
        logger.info(f"✓ Updated manifest timestamp")

def main():
    parser = argparse.ArgumentParser(description="Export N5 core to n5os-core repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without copying")
    parser.add_argument("--push", action="store_true", help="Auto-push to GitHub after export")
    parser.add_argument("--workspace", default="/home/workspace", help="Workspace path")
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    manifest_path = workspace / "N5/config/export_core_manifest.yaml"
    
    # Load manifest to get destination
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    dest_root = manifest["destination"]
    
    exporter = N5CoreExporter(str(workspace), dest_root, dry_run=args.dry_run)
    
    # Run export
    success = exporter.run_export()
    
    if not success:
        logger.error("✗ Export failed")
        return 1
    
    # Commit and push
    if not args.dry_run:
        if exporter.git_commit_push(auto_push=args.push):
            exporter.update_manifest_timestamp()
        else:
            logger.error("✗ Git operations failed")
            return 1
    
    logger.info(f"\n{'✓'*30} Export successful {'✓'*30}")
    return 0

if __name__ == "__main__":
    exit(main())
