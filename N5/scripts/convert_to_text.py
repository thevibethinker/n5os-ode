#!/usr/bin/env python3
"""
Document to Text Converter
Converts various document formats (docx, pdf, etc.) to plain text using pandoc.
"""

import subprocess
import sys
from pathlib import Path


def convert_to_text(input_file: str, output_file: str = None) -> str:
    """
    Convert a document to plain text using pandoc.
    
    Args:
        input_file: Path to input document (docx, pdf, etc.)
        output_file: Optional output path. If not provided, will use same name with .txt extension
        
    Returns:
        Path to the output text file
    """
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Determine output path
    if output_file:
        output_path = Path(output_file).resolve()
    else:
        output_path = input_path.with_suffix('.txt')
    
    # Run pandoc conversion
    try:
        subprocess.run(
            ['pandoc', str(input_path), '-t', 'plain', '-o', str(output_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Converted: {input_path.name} → {output_path.name}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Pandoc conversion failed: {e.stderr}")


def main():
    if len(sys.argv) < 2:
        print("Usage: convert_to_text.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        output_path = convert_to_text(input_file, output_file)
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
