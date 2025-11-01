#!/usr/bin/env python3
"""
Register all N5 scripts in executables.db
Handles conflicts, extracts metadata, skips deprecated
"""
import sqlite3
import argparse
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/executables.db")
SCRIPTS_DIR = Path("/home/workspace/N5/scripts")

def extract_docstring(script_path):
    """Extract first docstring from Python file"""
    try:
        content = script_path.read_text()
        # Match """ or ''' docstrings
        match = re.search(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'', content, re.DOTALL)
        if match:
            doc = (match.group(1) or match.group(2)).strip()
            # Return first line only
            return doc.split('\n')[0]
        return None
    except Exception as e:
        logging.warning(f"Could not extract docstring from {script_path.name}: {e}")
        return None

def generate_id(script_name, existing_ids):
    """Generate unique ID, handle conflicts"""
    base_id = script_name.replace('_', '-').replace('.py', '')
    
    # Check if exists
    if base_id not in existing_ids:
        return base_id
    
    # Conflict - prefix with 'script-'
    prefixed_id = f"script-{base_id}"
    if prefixed_id not in existing_ids:
        return prefixed_id
    
    # Still conflict - add number
    counter = 2
    while f"{prefixed_id}-{counter}" in existing_ids:
        counter += 1
    return f"{prefixed_id}-{counter}"

def register_scripts(dry_run=False):
    """Scan N5/scripts and register in DB"""
    conn = sqlite3.connect(DB_PATH)
    
    # Get existing IDs
    existing_ids = {row[0] for row in conn.execute('SELECT id FROM executables')}
    
    # Find all Python scripts
    scripts = []
    for script in SCRIPTS_DIR.rglob("*.py"):
        # Skip deprecated, tests, __init__
        if any(skip in str(script) for skip in ['_DEPRECATED', '/tests/', '__init__.py', '__pycache__']):
            continue
        scripts.append(script)
    
    logging.info(f"Found {len(scripts)} scripts to register")
    
    added = 0
    skipped = 0
    conflicts = []
    
    for script in scripts:
        script_id = generate_id(script.name, existing_ids)
        script_name = script.stem.replace('_', ' ').title()
        description = extract_docstring(script) or f"N5 script: {script.name}"
        
        # Check if already registered by path
        existing = conn.execute('SELECT id FROM executables WHERE file_path = ?', (str(script),)).fetchone()
        if existing:
            skipped += 1
            continue
        
        if script_id != script.stem.replace('_', '-').replace('.py', ''):
            conflicts.append((script.name, script_id))
        
        if dry_run:
            logging.info(f"[DRY-RUN] Would register: {script_id} → {script.relative_to('/home/workspace')}")
        else:
            try:
                conn.execute('''
                    INSERT INTO executables (id, name, type, file_path, description, category, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (script_id, script_name, 'script', str(script), description, 'n5-scripts', 'active'))
                added += 1
                existing_ids.add(script_id)
            except sqlite3.IntegrityError as e:
                logging.error(f"Failed to register {script.name}: {e}")
    
    if not dry_run:
        conn.commit()
    conn.close()
    
    return added, skipped, conflicts

def main():
    parser = argparse.ArgumentParser(description="Register N5 scripts in executables.db")
    parser.add_argument('--dry-run', action='store_true', help="Preview without writing")
    args = parser.parse_args()
    
    logging.info("=== Registering N5 Scripts ===")
    added, skipped, conflicts = register_scripts(dry_run=args.dry_run)
    
    logging.info(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Results:")
    logging.info(f"  Added: {added}")
    logging.info(f"  Skipped (already registered): {skipped}")
    if conflicts:
        logging.info(f"  ID conflicts resolved: {len(conflicts)}")
        for orig, resolved in conflicts[:5]:
            logging.info(f"    {orig} → {resolved}")
    
    if args.dry_run:
        logging.info("\nRun without --dry-run to execute")
        return 0
    
    logging.info(f"\n✓ Registered {added} scripts")
    return 0

if __name__ == "__main__":
    exit(main())
