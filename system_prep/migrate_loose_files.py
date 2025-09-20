#!/usr/bin/env python3
"""
Script to migrate existing loose temporary files into the cache system
"""

import os
import subprocess
import json
from pathlib import Path

def categorize_file(filepath):
    """Determine appropriate category for a file based on its path and name"""
    path_str = str(filepath).lower()

    if 'backup' in path_str or filepath.suffix == '.bak':
        return 'backups'
    elif 'log' in path_str or filepath.suffix == '.log':
        return 'logs'
    elif 'tmp_execution' in path_str or 'temp' in path_str:
        return 'temporary'
    elif 'conversation' in path_str:
        return 'conversation'
    elif 'output' in path_str or 'generated' in path_str:
        return 'generated'
    elif 'script' in path_str and filepath.suffix == '.py':
        return 'scripts'
    elif 'template' in path_str:
        return 'templates'
    elif 'test' in path_str:
        return 'tests'
    else:
        return 'misc'

def find_loose_files():
    """Find all loose temporary files that should be cached"""
    cmd = [
        'find', '/home/workspace', '-type', 'f',
        '(', '-name', '*.tmp', '-o', '-name', '*temp*', '-o', '-name', '*cache*',
             '-o', '-name', '*.log', '-o', '-name', '*backup*', '-o', '-name', '*.bak',
             '-o', '-name', '*conversation*', '-o', '-name', '*generated*', '-o', '-name', '*output*', ')',
        '-not', '-path', '*/__pycache__/*',
        '-not', '-path', '*/.git/*',
        '-not', '-path', '*/system_prep/*'  # Don't include our own cache system files
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return [Path(line.strip()) for line in result.stdout.strip().split('\n') if line.strip()]
    return []

def migrate_files():
    """Migrate all loose files to cache system"""
    files = find_loose_files()
    migrated = []
    errors = []

    print(f"Found {len(files)} loose files to migrate...")

    for filepath in files:
        if not filepath.exists():
            continue

        category = categorize_file(filepath)
        print(f"Migrating {filepath} -> category: {category}")

        try:
            # Use the cache manager to add the file
            cmd = [
                'python3', '/home/workspace/system_prep/cache_manager.py',
                'add', '--file', str(filepath), '--category', category
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                migrated.append({
                    'original': str(filepath),
                    'category': category,
                    'cached_path': result.stdout.strip().split(': ')[1] if ': ' in result.stdout else 'unknown'
                })

                # Remove the original file after successful caching
                filepath.unlink()
                print(f"✓ Migrated and removed: {filepath}")
            else:
                errors.append({
                    'file': str(filepath),
                    'error': result.stderr,
                    'category': category
                })
                print(f"✗ Failed to migrate: {filepath} - {result.stderr}")

        except Exception as e:
            errors.append({
                'file': str(filepath),
                'error': str(e),
                'category': category
            })
            print(f"✗ Error migrating {filepath}: {e}")

    return migrated, errors

def main():
    print("🔄 Starting migration of loose files to cache system...")
    print("=" * 60)

    migrated, errors = migrate_files()

    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully migrated: {len(migrated)} files")
    print(f"❌ Failed to migrate: {len(errors)} files")

    if migrated:
        print("\n📁 MIGRATED FILES:")
        for item in migrated:
            print(f"  • {item['original']} → {item['category']} ({item['cached_path']})")

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  • {error['file']} ({error['category']}): {error['error']}")

    print("\n" + "=" * 60)
    print("🎯 Cache system is now centralized!")

if __name__ == "__main__":
    main()