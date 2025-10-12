#!/usr/bin/env python3
"""Script to replace the generate_markdown method in n5_thread_export.py"""

from pathlib import Path

# Read the original file
script_path = Path("/home/workspace/N5/scripts/n5_thread_export.py")
with open(script_path, 'r') as f:
    content = f.read()

# Read the new method (indented version)
new_method_path = Path("/home/.z/workspaces/con_zWtEquyZjXDMpKNa/new_generate_markdown_indented.py")
with open(new_method_path, 'r') as f:
    new_method = f.read()

# Find the old method using markers
start_marker = "    def generate_markdown(self, aar_data: Dict) -> str:"
end_marker = "    def copy_artifacts(self):"

start_idx = content.find(start_marker)
if start_idx == -1:
    print("❌ Could not find start of generate_markdown method")
    exit(1)

# Find the end (start of next method)
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    print("❌ Could not find end of generate_markdown method")
    exit(1)

# Extract the parts
before = content[:start_idx]
after = content[end_idx:]

# Build new content - add blank line before next method
new_content = before + new_method + "\n" + after

# Write back
with open(script_path, 'w') as f:
    f.write(new_content)

print(f"✅ Replaced generate_markdown() method")
print(f"   File size: {len(content)} → {len(new_content)} bytes")
print(f"   New method: {len(new_method)} bytes")
