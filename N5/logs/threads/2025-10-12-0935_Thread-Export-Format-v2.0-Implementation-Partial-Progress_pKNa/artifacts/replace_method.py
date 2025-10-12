#!/usr/bin/env python3
"""Script to replace the generate_markdown method in n5_thread_export.py"""

from pathlib import Path

# Read the original file
script_path = Path("/home/workspace/N5/scripts/n5_thread_export.py")
with open(script_path, 'r') as f:
    lines = f.readlines()

# Read the new method
new_method_path = Path("/home/.z/workspaces/con_zWtEquyZjXDMpKNa/new_generate_markdown.py")
with open(new_method_path, 'r') as f:
    new_method_lines = f.readlines()

# Find the start and end of the old method (lines 277-344, but 0-indexed)
start_line = 276  # Line 277 in 1-indexed
end_line = 344    # Line 344 in 1-indexed (exclusive)

# Replace the method
new_lines = lines[:start_line] + new_method_lines + ['\n'] + lines[end_line:]

# Write back
with open(script_path, 'w') as f:
    f.writelines(new_lines)

print(f"✅ Replaced generate_markdown() method")
print(f"   Old method: lines {start_line+1}-{end_line}")
print(f"   New method: {len(new_method_lines)} lines")
print(f"   Total file: {len(new_lines)} lines (was {len(lines)})")
