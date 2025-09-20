import argparse


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
