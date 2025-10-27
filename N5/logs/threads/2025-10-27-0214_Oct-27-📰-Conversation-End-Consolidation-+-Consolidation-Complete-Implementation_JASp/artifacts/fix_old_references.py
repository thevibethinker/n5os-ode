#!/usr/bin/env python3
"""
Fix Old Path References
Updates N5/commands/ → Recipes/ and commands.jsonl → recipes.jsonl
"""

import re
from pathlib import Path

# Files to update and their replacement patterns
UPDATES = {
    "/home/workspace/N5/scripts/file_protector.py": [
        ('"/N5/commands/*.md"', '"/home/workspace/Documents/Archive/2025-10-27-Commands-to-Recipes-Migration/commands/*.md"'),
        ('N5/commands/', 'Recipes/'),
    ],
    "/home/workspace/N5/scripts/n5_convert_prompt.py": [
        ('N5/commands/', 'Recipes/'),
        ('commands.jsonl', 'recipes.jsonl'),
    ],
    "/home/workspace/N5/scripts/meeting_core_generator.py": [
        ('N5/commands/meeting-process.md', 'Recipes/Meetings/Meeting Process.md'),
    ],
    "/home/workspace/N5/scripts/meeting_intelligence_orchestrator.py": [
        ('N5/commands/meeting-process.md', 'Recipes/Meetings/Meeting Process.md'),
    ],
    "/home/workspace/N5/scripts/fix_meeting_duplication.py": [
        ('"/home/workspace/N5/commands/meeting-process.md"', '"/home/workspace/Recipes/Meetings/Meeting Process.md"'),
    ],
    "/home/workspace/N5/scripts/n5_bootstrap_advisor_server.py": [
        ('ls /home/workspace/N5/commands/*.md', 'ls /home/workspace/Recipes/*/*.md'),
    ],
    "/home/workspace/N5/scripts/n5_follow_up_email_generator.py": [
        ('N5/commands/', 'Recipes/'),
    ],
}

# Files that reference commands.jsonl but should be deprecated/noted
COMMANDS_JSONL_FILES = [
    "/home/workspace/N5/scripts/append_command.py",
    "/home/workspace/N5/scripts/n5_commands_manage.py",
    "/home/workspace/N5/scripts/n5_docgen.py",
    "/home/workspace/N5/scripts/incantum_parser.py",
]

def main():
    print("=== Fixing Path References ===\n")
    
    fixed = 0
    for filepath, replacements in UPDATES.items():
        path = Path(filepath)
        if not path.exists():
            print(f"⚠️  {filepath} - Not found")
            continue
            
        content = path.read_text()
        original = content
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ {path.name}: '{old}' → '{new}'")
                fixed += 1
        
        if content != original:
            path.write_text(content)
    
    print(f"\n=== Fixed {fixed} references ===\n")
    
    print("=== Scripts that reference commands.jsonl (need manual review) ===")
    for filepath in COMMANDS_JSONL_FILES:
        path = Path(filepath)
        if path.exists():
            print(f"  - {path.name}")
    
    print("\n✓ Path fix complete")
    print("\nNote: Scripts referencing commands.jsonl may need deprecation or")
    print("      updating to use recipes.jsonl. Review manually.")

if __name__ == "__main__":
    main()
