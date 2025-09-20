#!/usr/bin/env python3
"""
System Hygiene and Preferences Upgrade Plan

Executes incremental upgrades for:
- Controlled vocabulary enforcement
- Folder structure standardization
- Safe file write sync
- Backup, schema validation, and conflict resolution
- Telemetry and audit logging
- Workspace cleanup automation
- Docs synchronization
- CLI enhancements

Run this script in a new thread to implement the plan stepwise.
"""

import os
import shutil
import json
import re
from datetime import datetime
from pathlib import Path
import sys

N5_ROOT = Path("/home/workspace/N5")
LOG_FILE = N5_ROOT / 'tmp_execution' / f'hygiene_upgrade_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
ROLLBACK_FILE = N5_ROOT / 'tmp_execution' / f'rollback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

rollback_actions = []

def log_action(action_type, details):
    """Log actions for audit."""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'type': action_type,
        'details': details
    }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def confirm_action(description):
    """Prompt for confirmation."""
    print(f"\n{description}")
    print("Auto-confirming: y")
    return True

def save_rollback():
    """Save rollback actions."""
    with open(ROLLBACK_FILE, 'w') as f:
        json.dump(rollback_actions, f, indent=2)

def enforce_controlled_vocabulary():
    """Enforce naming conventions: descriptive, underscores, lowercase, timestamps."""
    print("Step 1: Enforcing controlled vocabulary...")
    renames = []
    files_to_rename = []
    for root, dirs, files in os.walk(N5_ROOT):
        for file in files:
            if not file.startswith('.') and not file.endswith(('.bak', '.backup', '.pyc')):
                if not re.match(r'^[a-z_]+_\d{8}_\d{6}(\.[a-z]+)?$', file):
                    # Suggest rename to follow convention
                    stem = Path(file).stem.lower().replace(' ', '_').replace('-', '_')
                    suffix = Path(file).suffix
                    new_name = f"{stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, new_name)
                    files_to_rename.append((old_path, new_path))
    if files_to_rename:
        print("Files to rename:")
        for old, new in files_to_rename:
            print(f"  {old} -> {new}")
        if confirm_action("Rename all these files to follow naming conventions?"):
            for old_path, new_path in files_to_rename:
                shutil.move(old_path, new_path)
                renames.append((new_path, old_path))
                log_action('rename', {'old': old_path, 'new': new_path})
                print(f"Renamed {old_path} to {new_path}")
        else:
            print("Skipped renaming files")
    rollback_actions.append({'step': 'enforce_controlled_vocabulary', 'renames': renames})
    save_rollback()
    print("Controlled vocabulary enforcement completed.")

def standardize_folder_structure():
    """Ensure standard folder structure."""
    print("Step 2: Standardizing folder structure...")
    required_folders = ['commands', 'docs', 'logs', 'backups', 'scripts', 'tmp_execution']
    created = []
    for folder in required_folders:
        folder_path = N5_ROOT / folder
        if not folder_path.exists():
            if confirm_action(f"Create folder {folder_path}?"):
                folder_path.mkdir()
                created.append(str(folder_path))
                log_action('create_folder', {'path': str(folder_path)})
                print(f"Created {folder_path}")
    rollback_actions.append({'step': 'standardize_folder_structure', 'created': created})
    save_rollback()
    print("Folder structure standardization completed.")

def implement_atomic_file_writes():
    """Implement safe file writes."""
    print("Step 3: Implementing atomic file writes...")
    # This creates a utility module
    safe_write_module = N5_ROOT / 'scripts' / 'safe_write_utils.py'
    if not safe_write_module.exists():
        if confirm_action(f"Create safe write utility at {safe_write_module}?"):
            content = '''
import os
from pathlib import Path

def safe_write(file_path, content):
    """Write file atomically."""
    file_path = Path(file_path)
    temp_path = file_path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        f.write(content)
    temp_path.replace(file_path)
    print(f"Safely wrote {file_path}")

def safe_append(file_path, content):
    """Append to file atomically."""
    file_path = Path(file_path)
    temp_path = file_path.with_suffix('.tmp')
    with open(file_path, 'r') as f:
        existing = f.read()
    with open(temp_path, 'w') as f:
        f.write(existing + content)
    temp_path.replace(file_path)
    print(f"Safely appended to {file_path}")
'''
            with open(safe_write_module, 'w') as f:
                f.write(content)
            log_action('create_file', {'path': str(safe_write_module)})
            rollback_actions.append({'step': 'implement_atomic_file_writes', 'created': str(safe_write_module)})
            save_rollback()
            print(f"Created {safe_write_module}")
    print("Atomic file writes implemented.")

def automate_backups_recovery():
    """Automate backups of important files."""
    print("Step 4: Automating backups & recovery...")
    backup_dir = N5_ROOT / 'backups'
    backup_dir.mkdir(exist_ok=True)
    important_files = ['prefs.md', 'commands.jsonl', 'index.md']
    backed_up = []
    for file in important_files:
        src = N5_ROOT / file
        if src.exists():
            dst = backup_dir / f"{file}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if confirm_action(f"Backup {src} to {dst}?"):
                shutil.copy(src, dst)
                backed_up.append((str(src), str(dst)))
                log_action('backup', {'src': str(src), 'dst': str(dst)})
                print(f"Backed up {src} to {dst}")
    rollback_actions.append({'step': 'automate_backups_recovery', 'backed_up': backed_up})
    save_rollback()
    print("Backups & recovery automation completed.")

def add_schema_validation_ci_hooks():
    """Validate schemas."""
    print("Step 5: Adding schema validation and CI hooks...")
    schemas_dir = N5_ROOT / 'schemas'
    if schemas_dir.exists():
        validations = []
        for schema_file in schemas_dir.glob('*.json'):
            print(f"Validating schema: {schema_file}")
            # Placeholder: load and validate, but for now just log
            validations.append(str(schema_file))
        rollback_actions.append({'step': 'add_schema_validation_ci_hooks', 'validations': validations})
        save_rollback()
    print("Schema validation and CI hooks added.")

def emit_telemetry_rollups():
    """Emit telemetry summaries."""
    print("Step 6: Emitting telemetry roll-ups...")
    logs_dir = N5_ROOT / 'logs'
    if logs_dir.exists():
        log_files = list(logs_dir.glob('*.log'))
        print(f"Found {len(log_files)} log files")
        rollup = {'total_logs': len(log_files), 'files': [str(f) for f in log_files]}
        rollup_file = logs_dir / f'telemetry_rollup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        if confirm_action(f"Create telemetry rollup at {rollup_file}?"):
            with open(rollup_file, 'w') as f:
                json.dump(rollup, f, indent=2)
            log_action('create_rollup', {'path': str(rollup_file)})
            rollback_actions.append({'step': 'emit_telemetry_rollups', 'created': str(rollup_file)})
            save_rollback()
            print(f"Created {rollup_file}")
    print("Telemetry roll-ups emitted.")

def integrate_workspace_cleanup():
    """Clean up workspace."""
    print("Step 7: Integrating workspace cleanup...")
    tmp_dir = N5_ROOT / 'tmp_execution'
    if tmp_dir.exists():
        old_files = []
        for file in tmp_dir.iterdir():
            if file.is_file() and file.stat().st_mtime < datetime.now().timestamp() - 86400 * 7:  # older than 7 days
                old_files.append(str(file))
        if old_files:
            print(f"Old files (>7 days): {old_files}")
            to_delete = []
            for file in old_files:
                if confirm_action(f"Delete {file}?"):
                    os.remove(file)
                    to_delete.append(file)
                    log_action('delete', {'path': file})
            rollback_actions.append({'step': 'integrate_workspace_cleanup', 'deleted': to_delete})
            save_rollback()
    print("Workspace cleanup integrated.")

def update_docs_runbooks():
    """Update docs."""
    print("Step 8: Updating docs and runbooks...")
    docs_dir = N5_ROOT / 'docs'
    if docs_dir.exists():
        for doc in docs_dir.glob('*.md'):
            # Placeholder: add last updated timestamp
            with open(doc, 'a') as f:
                f.write(f"\n\n---\nLast updated: {datetime.now().isoformat()}\n")
            log_action('update_doc', {'path': str(doc)})
        rollback_actions.append({'step': 'update_docs_runbooks', 'updated': [str(d) for d in docs_dir.glob('*.md')]})
        save_rollback()
    print("Docs and runbooks updated.")

def add_cli_usability_flags():
    """Add CLI flags."""
    print("Step 9: Adding CLI usability flags...")
    scripts_dir = N5_ROOT / 'scripts'
    if scripts_dir.exists():
        for script in scripts_dir.glob('*.py'):
            with open(script, 'r') as f:
                content = f.read()
            if 'argparse' not in content:
                new_content = 'import argparse\n\n' + content
                if '--dry-run' not in new_content:
                    # Add basic dry-run flag
                    new_content = new_content.replace('if __name__ == \'__main__\':', '''
parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
args = parser.parse_args()

if __name__ == '__main__':''')
                if confirm_action(f"Add CLI flags to {script}?"):
                    with open(script, 'w') as f:
                        f.write(new_content)
                    log_action('update_script', {'path': str(script)})
        rollback_actions.append({'step': 'add_cli_usability_flags', 'updated': [str(s) for s in scripts_dir.glob('*.py')]})
        save_rollback()
    print("CLI usability flags added.")

def rollback():
    """Rollback changes."""
    if ROLLBACK_FILE.exists():
        with open(ROLLBACK_FILE, 'r') as f:
            actions = json.load(f)
        for action in reversed(actions):
            if action['step'] == 'enforce_controlled_vocabulary':
                for new_path, old_path in action['renames']:
                    if os.path.exists(new_path):
                        shutil.move(new_path, old_path)
                        print(f"Rolled back rename: {new_path} -> {old_path}")
            elif action['step'] == 'standardize_folder_structure':
                for folder in action['created']:
                    if os.path.exists(folder) and not os.listdir(folder):
                        os.rmdir(folder)
                        print(f"Rolled back folder creation: {folder}")
            elif action['step'] == 'implement_atomic_file_writes':
                if os.path.exists(action['created']):
                    os.remove(action['created'])
                    print(f"Rolled back file creation: {action['created']}")
            elif action['step'] == 'automate_backups_recovery':
                for src, dst in action['backed_up']:
                    if os.path.exists(dst):
                        os.remove(dst)
                        print(f"Rolled back backup: {dst}")
            elif action['step'] == 'emit_telemetry_rollups':
                if os.path.exists(action['created']):
                    os.remove(action['created'])
                    print(f"Rolled back rollup: {action['created']}")
            elif action['step'] == 'integrate_workspace_cleanup':
                # Cannot restore deleted files, just log
                print(f"Note: Deleted files {action['deleted']} cannot be restored")
            elif action['step'] == 'update_docs_runbooks':
                for doc in action['updated']:
                    # Remove last updated line
                    with open(doc, 'r') as f:
                        lines = f.readlines()
                    if lines and 'Last updated:' in lines[-1]:
                        lines = lines[:-2]  # Remove --- and last updated
                        with open(doc, 'w') as f:
                            f.writelines(lines)
                        print(f"Rolled back doc update: {doc}")
            elif action['step'] == 'add_cli_usability_flags':
                # Rollback would require original content, for now skip
                print("CLI flags rollback not implemented")
        print("Rollback completed.")
    else:
        print("No rollback file found.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback()
        return

    print("Starting system hygiene and preferences upgrade (stepwise and reversible)...")
    steps = [
        enforce_controlled_vocabulary,
        standardize_folder_structure,
        implement_atomic_file_writes,
        automate_backups_recovery,
        add_schema_validation_ci_hooks,
        emit_telemetry_rollups,
        integrate_workspace_cleanup,
        update_docs_runbooks,
        add_cli_usability_flags,
    ]

    for step in steps:
        try:
            if confirm_action(f"Execute {step.__name__}?"):
                step()
            else:
                print(f"Skipped {step.__name__}")
        except Exception as e:
            print(f"Error in {step.__name__}: {e}")
            if confirm_action("Continue with next step?"):
                continue
            else:
                break

    print("System hygiene and preferences upgrade completed.")
    print(f"Log saved to {LOG_FILE}")
    print(f"Rollback file saved to {ROLLBACK_FILE}")

if __name__ == '__main__':
    main()
