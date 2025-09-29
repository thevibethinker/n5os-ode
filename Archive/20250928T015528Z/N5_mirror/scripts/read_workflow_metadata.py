#!/usr/bin/env python3
"""
Read and parse front matter from markdown files for workflow management.
"""

import yaml
import json
from pathlib import Path
import sys
from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def read_frontmatter(markdown_file):
    """Extract YAML front matter from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for front matter
    if not content.startswith("---"):
        return None
    
    # Find the closing delimiter
    end_delim = content.find("---", 3)
    if end_delim == -1:
        return None
    
    # Extract YAML
    yaml_content = content[3:end_delim].strip()
    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {markdown_file}: {e}")
        return None

def find_workflows_by_tag(root_dir, target_tag):
    """Find all markdown files with specific tags."""
    workflows = []
    for md_file in Path(root_dir).rglob("*.md"):
        frontmatter = read_frontmatter(md_file)
        if frontmatter and "tags" in frontmatter:
            if target_tag in frontmatter["tags"]:
                workflows.append({
                    "file": str(md_file),
                    "title": frontmatter.get("title", "No title"),
                    "tags": frontmatter["tags"],
                    "status": frontmatter.get("status", "unknown")
                })
    return workflows

def find_production_ready(root_dir):
    """Find all production-ready workflows."""
    workflows = []
    for md_file in Path(root_dir).rglob("*.md"):
        frontmatter = read_frontmatter(md_file)
        if frontmatter:
            if frontmatter.get("status") == "production-ready":
                workflows.append({
                    "file": str(md_file),
                    "title": frontmatter.get("title", "No title"),
                    "version": frontmatter.get("version", "unknown"),
                    "last_tested": frontmatter.get("last-tested", "unknown")
                })
    return workflows

if __name__ == "__main__":
    # Example usage
    workflow_file = sys.argv[1] if len(sys.argv) > 1 else "README_email_workflow.md"
    
    # Read current workflow metadata
    if Path(workflow_file).exists():
        metadata = read_frontmatter(workflow_file)
        print(f"📋 Front matter for {workflow_file}:")
        print(json.dumps(metadata, indent=2, default=json_serial))
    
    # Search for email workflows
    print(f"\n🔍 Searching for email workflows...")
    email_workflows = find_workflows_by_tag(".", "email")
    for workflow in email_workflows:
        print(f"  - {workflow['title']} ({workflow['status']})")
    
    # Find production-ready workflows
    print(f"\n🚀 Production-ready workflows...")
    prod_workflows = find_production_ready(".")
    for workflow in prod_workflows:
        print(f"  - {workflow['title']} v{workflow['version']} (last tested: {workflow['last_tested']})")