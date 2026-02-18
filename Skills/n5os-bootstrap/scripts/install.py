#!/usr/bin/env python3
"""
N5OS Bootstrap Installer

The main bootloader script that unpacks payload content into the target workspace structure.
Transforms the skill into actual infrastructure by following the manifest.yaml configuration.
"""

import argparse
import json
import logging
import os
import shutil
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the installer."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_manifest(skill_root: Path) -> Dict[str, Any]:
    """Load the installation manifest."""
    manifest_path = skill_root / "config" / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def ensure_dir(path: Path, dry_run: bool = False, logger: logging.Logger = None) -> None:
    """Create directory if it doesn't exist."""
    if not path.exists():
        if dry_run:
            if logger:
                logger.info(f"[DRY-RUN] Would create directory: {path}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            if logger:
                logger.info(f"Created directory: {path}")


def copy_file(source: Path, target: Path, dry_run: bool = False, logger: logging.Logger = None) -> bool:
    """Copy a single file, creating parent directories as needed."""
    if dry_run:
        if logger:
            logger.info(f"[DRY-RUN] Would copy: {source} -> {target}")
        return True
    
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if logger:
            logger.info(f"Copied: {source.name} -> {target}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to copy {source} -> {target}: {e}")
        return False


def find_conflicts(manifest: Dict[str, Any], skill_root: Path, workspace_root: Path) -> List[Path]:
    """Find existing files that would be overwritten."""
    conflicts = []
    
    for name, dest_config in manifest.get('destinations', {}).items():
        source_dir = skill_root / dest_config['source']
        target_dir = workspace_root / dest_config['target']
        
        if not source_dir.exists():
            continue
            
        for source_file in source_dir.glob('**/*.md'):
            rel_path = source_file.relative_to(source_dir)
            target_file = target_dir / rel_path
            
            if target_file.exists():
                conflicts.append(target_file)
    
    return conflicts


def install_destination(name: str, config: Dict[str, Any], skill_root: Path, 
                       workspace_root: Path, dry_run: bool = False, 
                       logger: logging.Logger = None) -> Dict[str, int]:
    """Install files for a single destination."""
    stats = {'copied': 0, 'skipped': 0, 'errors': 0}
    
    source_dir = skill_root / config['source']
    target_dir = workspace_root / config['target']
    
    if not source_dir.exists():
        if logger:
            logger.warning(f"Source directory missing: {source_dir}")
        return stats
    
    # Ensure target directory exists
    ensure_dir(target_dir, dry_run, logger)
    
    # Copy all markdown files
    for source_file in source_dir.glob('**/*.md'):
        rel_path = source_file.relative_to(source_dir)
        target_file = target_dir / rel_path
        
        if copy_file(source_file, target_file, dry_run, logger):
            stats['copied'] += 1
        else:
            stats['errors'] += 1
    
    return stats


def log_installation(manifest: Dict[str, Any], args: argparse.Namespace, 
                     stats: Dict[str, Dict[str, int]], workspace_root: Path) -> None:
    """Log installation details to N5/logs/n5os-bootstrap.log."""
    log_dir = workspace_root / "N5" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "n5os-bootstrap.log"
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    log_entry = {
        'timestamp': timestamp,
        'action': 'install',
        'dry_run': args.dry_run,
        'force': args.force,
        'config': getattr(args, 'config', None),
        'stats': stats,
        'version': manifest.get('version', 'unknown')
    }
    
    # Append to log file as JSON lines
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def run_personalize(config_path: str, skill_root: Path, dry_run: bool = False, 
                   logger: logging.Logger = None) -> bool:
    """Run personalization if config is provided."""
    personalize_script = skill_root / "scripts" / "personalize.py"
    
    if not personalize_script.exists():
        if logger:
            logger.warning("personalize.py not found, skipping personalization")
        return True
    
    cmd = [sys.executable, str(personalize_script), '--config', config_path]
    if dry_run:
        cmd.append('--dry-run')
    
    if logger:
        action = "[DRY-RUN] Would run" if dry_run else "Running"
        logger.info(f"{action} personalization: {' '.join(cmd)}")
    
    if not dry_run:
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=skill_root)
            if result.returncode != 0:
                if logger:
                    logger.error(f"Personalization failed: {result.stderr}")
                return False
            else:
                if logger and result.stdout:
                    logger.info(f"Personalization output: {result.stdout.strip()}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to run personalization: {e}")
            return False
    
    return True


def main() -> int:
    """Main installer function."""
    parser = argparse.ArgumentParser(
        description="N5OS Bootstrap Installer - Unpack philosophy and infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 install.py --dry-run                    # Show what would be installed
  python3 install.py --force --verbose            # Install with full output
  python3 install.py --config instances/zoputer.yaml  # Install with personalization
        """
    )
    
    parser.add_argument('--config', 
                       help='Instance config file (e.g., instances/zoputer.yaml)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be installed without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing files without prompting')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed progress')
    parser.add_argument('--skip-personalize', action='store_true',
                       help='Skip personalization step')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    try:
        # Determine paths
        skill_root = Path(__file__).parent.parent
        workspace_root = Path.cwd()
        
        logger.info(f"N5OS Bootstrap Installer v1.0")
        logger.info(f"Skill root: {skill_root}")
        logger.info(f"Workspace root: {workspace_root}")
        
        # Load manifest
        manifest = load_manifest(skill_root)
        logger.info(f"Loaded manifest: {manifest['name']} v{manifest.get('version', 'unknown')}")
        
        # Create required directories
        for dir_path in manifest.get('required_dirs', []):
            ensure_dir(workspace_root / dir_path, args.dry_run, logger)
        
        # Check for conflicts
        conflicts = find_conflicts(manifest, skill_root, workspace_root)
        if conflicts and not args.force:
            logger.error(f"Found {len(conflicts)} conflicting files:")
            for conflict in conflicts[:10]:  # Show first 10
                logger.error(f"  - {conflict}")
            if len(conflicts) > 10:
                logger.error(f"  ... and {len(conflicts) - 10} more")
            logger.error("Use --force to overwrite existing files")
            return 2
        
        # Install all destinations
        total_stats = {'copied': 0, 'skipped': 0, 'errors': 0}
        destination_stats = {}
        
        for name, config in manifest.get('destinations', {}).items():
            logger.info(f"Installing {name}...")
            stats = install_destination(name, config, skill_root, workspace_root, 
                                      args.dry_run, logger)
            destination_stats[name] = stats
            
            # Add to totals
            for key in total_stats:
                total_stats[key] += stats[key]
        
        # Summary
        action = "Would install" if args.dry_run else "Installed"
        logger.info(f"{action}: {total_stats['copied']} files, "
                   f"{total_stats['errors']} errors")
        
        # Run personalization if config provided
        if args.config and not args.skip_personalize:
            config_path = str(skill_root / "config" / args.config)
            if not Path(config_path).exists():
                config_path = args.config  # Try as absolute path
            
            if not run_personalize(config_path, skill_root, args.dry_run, logger):
                return 1
        
        # Log installation (unless dry run)
        if not args.dry_run:
            log_installation(manifest, args, destination_stats, workspace_root)
        
        if total_stats['errors'] > 0:
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Installation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())