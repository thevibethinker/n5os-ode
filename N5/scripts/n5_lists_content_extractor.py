#!/usr/bin/env python3
"""
Lists Content Extractor - Hybrid Entry Content Injection

Extracts and formats content from linked markdown files for embedding
in Lists markdown views. Handles frontmatter parsing, content extraction,
and graceful error handling for missing/broken links.

Usage:
    from n5_lists_content_extractor import extract_content_for_item
    
    content = extract_content_for_item(item, workspace_root)
"""
import re
from pathlib import Path
from typing import Optional, Dict, Any, List


# Constants
DEFAULT_MAX_CHARS = 2000  # Truncate long content at this length


def read_linked_markdown(link_path: str, workspace_root: Path) -> Optional[str]:
    """
    Read markdown content from a linked file path.
    
    Args:
        link_path: Path from JSONL links[*].value field (relative or absolute)
        workspace_root: Workspace root path for resolving relative paths
    
    Returns:
        Markdown content as string, or None if file not found/read error
    """
    try:
        # Resolve path: if relative, resolve against workspace root
        path = Path(link_path)
        if not path.is_absolute():
            path = (workspace_root / link_path).resolve()
        
        if not path.exists():
            return None
        
        return path.read_text(encoding="utf-8")
    except Exception as e:
        # Log error but don't break view generation
        print(f"Warning: Failed to read linked file '{link_path}': {e}")
        return None


def parse_frontmatter(markdown: str) -> Dict[str, Any]:
    """
    Extract YAML frontmatter from markdown content.
    
    Args:
        markdown: Full markdown content string
    
    Returns:
        Dict of frontmatter fields (empty dict if no frontmatter)
    """
    frontmatter = {}
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    
    match = re.match(frontmatter_pattern, markdown, re.DOTALL)
    if match:
        fm_text = match.group(1)
        # Simple key-value parsing (handle basic YAML-like structures)
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                frontmatter[key] = value
    
    return frontmatter


def extract_content_sections(markdown: str) -> List[Dict[str, str]]:
    """
    Extract structured sections from markdown content.
    
    Args:
        markdown: Full markdown content string
    
    Returns:
        List of dicts with 'header' and 'content' keys
    """
    sections = []
    lines = markdown.split('\n')
    
    current_header = None
    current_content = []
    
    for line in lines:
        # Check for header (## or ###)
        header_match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_header:
                sections.append({
                    'header': current_header,
                    'content': '\n'.join(current_content).strip()
                })
            
            # Start new section
            current_header = header_match.group(2).strip()
            current_content = []
        else:
            # Skip frontmatter delimiters
            if not line.startswith('---'):
                current_content.append(line)
    
    # Add final section
    if current_header:
        sections.append({
            'header': current_header,
            'content': '\n'.join(current_content).strip()
        })
    
    return sections


def get_truncated_preview(content: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """
    Truncate content to reasonable length for view.
    
    Args:
        content: Content to truncate
        max_chars: Maximum characters (default 2000)
    
    Returns:
        Truncated content with ellipsis if shortened
    """
    if len(content) <= max_chars:
        return content
    
    # Try to truncate at paragraph break
    truncated = content[:max_chars]
    last_para = truncated.rfind('\n\n')
    if last_para > max_chars * 0.5:  # Only use paragraph break if it's reasonably close
        truncated = truncated[:last_para]
    
    return truncated.rstrip() + '\n\n*(... content truncated)*'


def format_content_for_view(sections: List[Dict[str, str]], max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """
    Format extracted sections for embedding in markdown view.
    
    Args:
        sections: List of section dicts from extract_content_sections()
        max_chars: Maximum characters for total content
    
    Returns:
        Formatted markdown string
    """
    if not sections:
        return ""
    
    lines = []
    total_chars = 0
    
    for section in sections[:10]:  # Limit to 10 sections max
        header = section.get('header', '')
        content = section.get('content', '')
        
        # Stop if we've hit character limit
        if total_chars + len(content) > max_chars:
            lines.append(f"### {header}\n")
            remaining = max_chars - total_chars
            lines.append(get_truncated_preview(content, remaining))
            break
        
        lines.append(f"### {header}\n")
        lines.append(f"{content}\n")
        total_chars += len(content)
    
    return '\n'.join(lines)


def extract_content_for_item(item: Dict[str, Any], workspace_root: Path) -> Optional[str]:
    """
    Main entry point: Extract and format content from linked markdown file.
    
    Args:
        item: JSONL item dict with possible 'links' field
        workspace_root: Workspace root path for resolving links
    
    Returns:
        Formatted markdown content string, or None if not hybrid or error
    """
    # Check if item has links
    links = item.get('links', [])
    if not links:
        return None
    
    # Find first file-type link
    file_link = None
    for link in links:
        if link.get('type') == 'file':
            file_link = link.get('value')
            break
    
    if not file_link:
        return None
    
    # Read linked markdown
    markdown = read_linked_markdown(file_link, workspace_root)
    if markdown is None:
        return f"⚠️ **Linked file not found**: `{file_link}`"
    
    # Extract and format content
    sections = extract_content_sections(markdown)
    
    if not sections:
        # No structured sections, return raw content (truncated)
        return get_truncated_preview(markdown)
    
    return format_content_for_view(sections)


if __name__ == "__main__":
    # Simple test harness
    import sys
    import json
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("Usage: python3 n5_lists_content_extractor.py <jsonl-file> <workspace-root>")
        sys.exit(1)
    
    jsonl_file = Path(sys.argv[1])
    workspace_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd().parent
    
    items = []
    with jsonl_file.open('r') as f:
        for line in f:
            items.append(json.loads(line))
    
    for item in items:
        content = extract_content_for_item(item, workspace_root)
        if content:
            print(f"=== {item.get('title')} ===")
            print(content[:500])  # Preview first 500 chars
            print()

