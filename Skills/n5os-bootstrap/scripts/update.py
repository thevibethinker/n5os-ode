#!/usr/bin/env python3
"""
N5OS Bootstrap Update Script

Pulls latest N5OS content from the substrate without breaking local personalization.
Enables ongoing evolution — instances can receive principle updates, new protocols,
and enhanced safety rules from the parent instance.
"""

import argparse
import json
import logging
import os
import shutil
import sys
import urllib.request
import urllib.error
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


# Default substrate URL (can be overridden via --source)
DEFAULT_SUBSTRATE_URL = "https://raw.githubusercontent.com/vrijenattawar/zoputer-substrate/main/Skills/n5os-bootstrap"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Save YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_installed(skill_root: Path) -> Optional[Dict[str, Any]]:
    """Load installed.yaml if it exists."""
    installed_path = skill_root / "config" / "installed.yaml"
    if installed_path.exists():
        return load_yaml(installed_path)
    return None


def save_installed(skill_root: Path, data: Dict[str, Any]) -> None:
    """Save installed.yaml."""
    installed_path = skill_root / "config" / "installed.yaml"
    data['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_yaml(installed_path, data)


def fetch_remote_manifest(source: str, logger: logging.Logger) -> Optional[Dict[str, Any]]:
    """Fetch manifest from remote source or local path."""
    if source.startswith('http'):
        manifest_url = f"{source.rstrip('/')}/config/manifest.yaml"
        logger.debug(f"Fetching remote manifest: {manifest_url}")
        try:
            with urllib.request.urlopen(manifest_url, timeout=30) as response:
                content = response.read().decode('utf-8')
                return yaml.safe_load(content)
        except urllib.error.URLError as e:
            logger.error(f"Failed to fetch remote manifest: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing remote manifest: {e}")
            return None
    else:
        # Local path
        manifest_path = Path(source) / "config" / "manifest.yaml"
        if manifest_path.exists():
            return load_yaml(manifest_path)
        else:
            logger.error(f"Local manifest not found: {manifest_path}")
            return None


def version_compare(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    def parse_version(v):
        return [int(x) for x in v.split('.')]
    
    try:
        p1, p2 = parse_version(v1), parse_version(v2)
        # Pad shorter version with zeros
        max_len = max(len(p1), len(p2))
        p1.extend([0] * (max_len - len(p1)))
        p2.extend([0] * (max_len - len(p2)))
        
        for a, b in zip(p1, p2):
            if a < b:
                return -1
            elif a > b:
                return 1
        return 0
    except (ValueError, AttributeError):
        # If version parsing fails, treat as needing update
        return -1


def fetch_remote_file(source: str, rel_path: str, logger: logging.Logger) -> Optional[str]:
    """Fetch a single file from remote source."""
    if source.startswith('http'):
        file_url = f"{source.rstrip('/')}/{rel_path}"
        logger.debug(f"Fetching: {file_url}")
        try:
            with urllib.request.urlopen(file_url, timeout=30) as response:
                return response.read().decode('utf-8')
        except urllib.error.URLError as e:
            logger.warning(f"Failed to fetch {rel_path}: {e}")
            return None
    else:
        file_path = Path(source) / rel_path
        if file_path.exists():
            return file_path.read_text()
        return None


def list_remote_files(source: str, component: str, logger: logging.Logger) -> List[str]:
    """
    List files available for a component.
    For local sources, scan directory. For remote, use a manifest listing.
    """
    if not source.startswith('http'):
        # Local source - scan directory
        source_dir = Path(source) / "payload" / component
        if source_dir.exists():
            return [str(f.relative_to(source_dir)) for f in source_dir.glob('**/*.md')]
        return []
    
    # For remote sources, we fetch a file listing if available
    # Otherwise, fall back to the installed list
    listing_url = f"{source.rstrip('/')}/payload/{component}/_files.txt"
    try:
        with urllib.request.urlopen(listing_url, timeout=30) as response:
            content = response.read().decode('utf-8')
            return [line.strip() for line in content.split('\n') if line.strip()]
    except urllib.error.URLError:
        # No listing available - return empty (will use manifest info)
        logger.debug(f"No file listing for {component}, using manifest")
        return []


def determine_updates(
    installed: Dict[str, Any],
    remote_manifest: Dict[str, Any],
    component_filter: Optional[str],
    force: bool,
    logger: logging.Logger
) -> List[Dict[str, Any]]:
    """Determine which components need updating."""
    updates = []
    
    installed_components = installed.get('components', {})
    remote_destinations = remote_manifest.get('destinations', {})
    
    for component, config in remote_destinations.items():
        # Filter by component if specified
        if component_filter and component != component_filter:
            continue
        
        local_version = installed_components.get(component, {}).get('version', '0.0.0')
        remote_version = config.get('version', '1.0.0')
        
        needs_update = force or version_compare(remote_version, local_version) > 0
        
        if needs_update:
            updates.append({
                'component': component,
                'from_version': local_version,
                'to_version': remote_version,
                'config': config
            })
            logger.debug(f"Update needed: {component} {local_version} → {remote_version}")
        else:
            logger.debug(f"Up to date: {component} @ {local_version}")
    
    return updates


def apply_update(
    update: Dict[str, Any],
    source: str,
    skill_root: Path,
    workspace_root: Path,
    dry_run: bool,
    logger: logging.Logger
) -> bool:
    """Apply a single component update."""
    component = update['component']
    config = update['config']
    
    source_rel = config.get('source', f'payload/{component}/')
    target_rel = config['target']
    
    logger.info(f"Updating {component}...")
    
    # Determine files to update
    if source.startswith('http'):
        # Fetch from remote
        payload_dir = skill_root / "payload" / component
        
        # Get file listing (try remote listing, fall back to local)
        remote_files = list_remote_files(source, component, logger)
        
        if not remote_files and payload_dir.exists():
            # Use existing local files as reference
            remote_files = [str(f.relative_to(payload_dir)) for f in payload_dir.glob('**/*.md')]
        
        if not remote_files:
            logger.warning(f"No files found for component {component}")
            return False
        
        # Fetch and update each file
        for rel_file in remote_files:
            content = fetch_remote_file(source, f"payload/{component}/{rel_file}", logger)
            if content is None:
                continue
            
            # Update payload
            payload_path = payload_dir / rel_file
            target_path = workspace_root / target_rel / rel_file
            
            if dry_run:
                logger.info(f"  [DRY-RUN] Would update: {rel_file}")
            else:
                payload_path.parent.mkdir(parents=True, exist_ok=True)
                payload_path.write_text(content)
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content)
                logger.debug(f"  Updated: {rel_file}")
    else:
        # Local source - copy files
        source_dir = Path(source) / source_rel
        payload_dir = skill_root / "payload" / component
        target_dir = workspace_root / target_rel
        
        if not source_dir.exists():
            logger.warning(f"Source directory not found: {source_dir}")
            return False
        
        for source_file in source_dir.glob('**/*.md'):
            rel_path = source_file.relative_to(source_dir)
            payload_path = payload_dir / rel_path
            target_path = target_dir / rel_path
            
            if dry_run:
                logger.info(f"  [DRY-RUN] Would update: {rel_path}")
            else:
                payload_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, payload_path)
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_path)
                logger.debug(f"  Updated: {rel_path}")
    
    return True


def run_personalize(skill_root: Path, installed: Dict[str, Any], dry_run: bool, logger: logging.Logger) -> bool:
    """Re-run personalization after update."""
    personalize_script = skill_root / "scripts" / "personalize.py"
    
    if not personalize_script.exists():
        logger.warning("personalize.py not found, skipping")
        return True
    
    config_file = installed.get('personalization')
    if not config_file:
        logger.info("No personalization config specified, skipping")
        return True
    
    config_path = skill_root / "config" / config_file
    if not config_path.exists():
        config_path = Path(config_file)
    
    if not config_path.exists():
        logger.warning(f"Personalization config not found: {config_file}")
        return True
    
    cmd = [sys.executable, str(personalize_script), str(config_path)]
    if dry_run:
        cmd.append('--dry-run')
    
    logger.info(f"Re-running personalization with {config_file}...")
    
    if not dry_run:
        import subprocess
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=skill_root)
            if result.returncode != 0:
                logger.error(f"Personalization failed: {result.stderr}")
                return False
            logger.debug(f"Personalization output: {result.stdout}")
        except Exception as e:
            logger.error(f"Failed to run personalization: {e}")
            return False
    
    return True


def run_verify(skill_root: Path, logger: logging.Logger) -> int:
    """Run verification after update."""
    verify_script = skill_root / "scripts" / "verify.py"
    
    if not verify_script.exists():
        logger.warning("verify.py not found, skipping verification")
        return 0
    
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, str(verify_script)],
            capture_output=True,
            text=True,
            cwd=skill_root
        )
        if result.returncode != 0:
            logger.warning(f"Verification warnings: {result.stdout}")
        return result.returncode
    except Exception as e:
        logger.error(f"Failed to run verification: {e}")
        return 1


def log_update(updates: List[Dict[str, Any]], dry_run: bool, workspace_root: Path) -> None:
    """Log update to N5/logs/n5os-bootstrap.log."""
    log_dir = workspace_root / "N5" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "n5os-bootstrap.log"
    
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'action': 'update',
        'dry_run': dry_run,
        'components': [
            {
                'name': u['component'],
                'from': u['from_version'],
                'to': u['to_version']
            }
            for u in updates
        ]
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N5OS Bootstrap Update - Pull latest content from substrate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 update.py --dry-run                    # Show what would be updated
  python3 update.py --verbose                    # Update with detailed output
  python3 update.py --component principles       # Update only principles
  python3 update.py --source /path/to/local      # Update from local source
        """
    )
    
    parser.add_argument('--source', default=DEFAULT_SUBSTRATE_URL,
                       help='Source URL or path for updates (default: substrate)')
    parser.add_argument('--component',
                       help='Only update specific component (principles, safety, etc.)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be updated without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Update even if versions match')
    parser.add_argument('--skip-personalize', action='store_true',
                       help='Skip re-personalization after update')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed progress')
    
    args = parser.parse_args()
    
    logger = setup_logging(args.verbose)
    
    try:
        # Determine paths
        skill_root = Path(__file__).parent.parent
        workspace_root = Path('/home/workspace')
        
        logger.info("N5OS Bootstrap Update")
        logger.info(f"Source: {args.source}")
        
        # Load installed state
        installed = load_installed(skill_root)
        if not installed:
            logger.error("N5OS Bootstrap not installed. Run install.py first.")
            return 1
        
        logger.info(f"Installed version: {installed.get('version', 'unknown')}")
        
        # Fetch remote manifest
        logger.info("Checking for updates...")
        remote_manifest = fetch_remote_manifest(args.source, logger)
        
        if remote_manifest is None:
            # If remote fetch fails, try using local manifest for version info
            logger.warning("Could not fetch remote manifest, using local")
            remote_manifest = load_yaml(skill_root / "config" / "manifest.yaml")
        
        # Determine what needs updating
        updates = determine_updates(
            installed,
            remote_manifest,
            args.component,
            args.force,
            logger
        )
        
        if not updates:
            logger.info("Already up to date.")
            return 0
        
        # Show what will be updated
        logger.info(f"Updates available: {len(updates)} component(s)")
        for u in updates:
            logger.info(f"  - {u['component']}: {u['from_version']} → {u['to_version']}")
        
        if args.dry_run:
            logger.info("[DRY-RUN] No changes made.")
            return 0
        
        # Apply updates
        success_count = 0
        for update in updates:
            if apply_update(update, args.source, skill_root, workspace_root, args.dry_run, logger):
                # Update installed state
                if 'components' not in installed:
                    installed['components'] = {}
                
                if update['component'] not in installed['components']:
                    installed['components'][update['component']] = {}
                
                installed['components'][update['component']]['version'] = update['to_version']
                installed['components'][update['component']]['updated_at'] = datetime.now(timezone.utc).isoformat()
                success_count += 1
            else:
                logger.warning(f"Failed to update {update['component']}")
        
        # Save updated installation state
        save_installed(skill_root, installed)
        
        # Re-personalize
        if not args.skip_personalize:
            if not run_personalize(skill_root, installed, args.dry_run, logger):
                logger.warning("Personalization failed, but update was applied")
        
        # Verify
        verify_result = run_verify(skill_root, logger)
        if verify_result != 0:
            logger.warning("Verification reported issues after update")
        
        # Log update
        log_update(updates, args.dry_run, workspace_root)
        
        logger.info(f"Updated {success_count}/{len(updates)} component(s)")
        
        if success_count < len(updates):
            return 2  # Partial update
        
        return 0
        
    except Exception as e:
        logger.error(f"Update failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
