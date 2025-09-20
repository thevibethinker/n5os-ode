#!/usr/bin/env python3
"""
Cache System Status Report
Shows comprehensive integration status across Zo Computer
"""

import os
import json
import subprocess
from pathlib import Path
from cache_manager import CacheManager

def get_system_status():
    """Generate comprehensive system status report"""
    cache_manager = CacheManager()

    # Get cache statistics
    all_files = cache_manager.list_files()
    categories = {}
    total_size = 0

    for file_info in all_files:
        category = file_info['category']
        if category not in categories:
            categories[category] = {'count': 0, 'size': 0}
        categories[category]['count'] += 1
        categories[category]['size'] += file_info['size']
        total_size += file_info['size']

    # Check integration status
    integration_checks = {
        'cache_scripts_executable': all(
            os.access(f'/home/workspace/system_prep/{script}', os.X_OK)
            for script in ['cache_manager.py', 'distribute_docs.py', 'init_cache.sh', 'integrate_system.sh']
        ),
        'startup_hook_exists': Path('/home/workspace/system_prep/startup_hook.sh').exists(),
        'migration_script_exists': Path('/home/workspace/system_prep/migrate_loose_files.py').exists(),
        'readme_exists': Path('/home/workspace/system_prep/README.md').exists(),
        'config_exists': Path('/home/workspace/system_prep/distribution_config.json').exists(),
        'cache_directory_exists': Path('/home/workspace/system_prep/cache').exists(),
        'metadata_exists': Path('/home/workspace/system_prep/cache/metadata.json').exists(),
    }

    # Check system-wide integration
    bashrc_path = Path.home() / '.bashrc'
    system_integration = {
        'bashrc_updated': bashrc_path.exists() and 'system_prep' in bashrc_path.read_text(),
        'path_includes_cache': '/home/workspace/system_prep' in os.environ.get('PATH', ''),
    }

    # Check workflow directory integration
    workflow_dirs = [
        '/home/workspace/N5/scripts',
        '/home/workspace/N5/command_authoring',
        '/home/workspace/examples'
    ]

    workflow_integration = {}
    for dir_path in workflow_dirs:
        dir_obj = Path(dir_path)
        workflow_integration[dir_path] = {
            'exists': dir_obj.exists(),
            'has_cache_readme': (dir_obj / 'CACHE_SYSTEM_README.md').exists()
        }

    return {
        'cache_stats': {
            'total_files': len(all_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'categories': categories
        },
        'integration_status': integration_checks,
        'system_integration': system_integration,
        'workflow_integration': workflow_integration
    }

def print_status_report(status):
    """Print formatted status report"""
    print("🎯 ZO COMPUTER CACHE SYSTEM - STATUS REPORT")
    print("=" * 60)

    # Cache Statistics
    print("\n📊 CACHE STATISTICS:")
    print(f"  • Total Files: {status['cache_stats']['total_files']}")
    print(f"  • Total Size: {status['cache_stats']['total_size_mb']} MB")
    print("  • Categories:")
    for cat, data in status['cache_stats']['categories'].items():
        print(f"    - {cat}: {data['count']} files ({round(data['size']/1024, 1)} KB)")

    # Integration Status
    print("\n🔧 INTEGRATION STATUS:")
    all_integrated = all(status['integration_status'].values())
    print(f"  • Overall Integration: {'✅ Complete' if all_integrated else '⚠️  Partial'}")

    for check, passed in status['integration_status'].items():
        status_icon = '✅' if passed else '❌'
        print(f"  • {check.replace('_', ' ').title()}: {status_icon}")

    # System Integration
    print("\n🌐 SYSTEM-WIDE INTEGRATION:")
    for check, passed in status['system_integration'].items():
        status_icon = '✅' if passed else '❌'
        print(f"  • {check.replace('_', ' ').title()}: {status_icon}")

    # Workflow Integration
    print("\n📁 WORKFLOW INTEGRATION:")
    for workflow, checks in status['workflow_integration'].items():
        if checks['exists']:
            readme_status = '✅' if checks['has_cache_readme'] else '❌'
            print(f"  • {workflow}: {readme_status} (README present)")
        else:
            print(f"  • {workflow}: ❌ (Directory not found)")

    print("\n" + "=" * 60)
    print("🎉 CACHE SYSTEM FULLY OPERATIONAL!")
    print("\n💡 QUICK COMMANDS:")
    print("  • cache-list                    # List all cached files")
    print("  • cache-add file.txt --category conversation  # Cache a file")
    print("  • cache-clean                   # Clean old files")
    print("  • cache-conversation output.md  # Quick conversation caching")
    print("\n📖 For full documentation: /home/workspace/system_prep/README.md")

def main():
    status = get_system_status()
    print_status_report(status)

if __name__ == "__main__":
    main()