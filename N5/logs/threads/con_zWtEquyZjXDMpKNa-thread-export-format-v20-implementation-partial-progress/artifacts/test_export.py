#!/usr/bin/env python3
"""Test the new generate_markdown method"""

import sys
sys.path.insert(0, '/home/workspace/N5/scripts')

from n5_thread_export import ThreadExporter
from datetime import datetime, timezone

# Create a test exporter
exporter = ThreadExporter("con_test123456789ABC", "Test Thread Title", dry_run=True)

# Generate some test artifacts
exporter.artifacts = [
    {
        'filename': 'test_script.py',
        'path': '/tmp/test_script.py',
        'relative_path': 'test_script.py',
        'size_bytes': 1024,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'modified_at': datetime.now(timezone.utc).isoformat(),
        'type': 'script'
    },
    {
        'filename': 'documentation.md',
        'path': '/tmp/documentation.md',
        'relative_path': 'documentation.md',
        'size_bytes': 2048,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'modified_at': datetime.now(timezone.utc).isoformat(),
        'type': 'document'
    }
]

# Generate smart AAR
aar_data = exporter.generate_smart_aar()

# Generate markdown
markdown = exporter.generate_markdown(aar_data)

# Save to file
output_path = '/home/.z/workspaces/con_zWtEquyZjXDMpKNa/sample_aar_output.md'
with open(output_path, 'w') as f:
    f.write(markdown)

print(f"✅ Generated sample AAR: {output_path}")
print(f"   Length: {len(markdown)} chars")
print(f"   Lines: {len(markdown.splitlines())}")
