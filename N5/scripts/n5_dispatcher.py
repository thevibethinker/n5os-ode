#!/usr/bin/env python3
"""
N5 Command Dispatcher
Routes CLI commands to Prompts (first) or Workers (fallback).
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Optional, Tuple

# Paths
WORKSPACE = Path("/home/workspace")
PROMPTS_DIRS = [
    WORKSPACE / "Prompts",
    WORKSPACE / "N5/prompts",
    WORKSPACE / "N5/workflows"
]
LAUNCHER_SCRIPT = WORKSPACE / "N5/scripts/n5_launch_worker.py"

def find_prompt(query: str) -> Optional[Path]:
    """Find a prompt file matching the query (fuzzy)."""
    query_parts = query.lower().split()
    best_match = None
    max_score = 0

    for folder in PROMPTS_DIRS:
        if not folder.exists():
            continue
        
        for file_path in folder.glob("*.prompt.md"):
            score = 0
            name = file_path.stem.lower()
            
            # Scoring logic
            for part in query_parts:
                if part in name:
                    score += 1
            
            # Exact match bonus
            if query.lower() == name:
                score += 5
                
            if score > max_score:
                max_score = score
                best_match = file_path
    
    return best_match

def get_parent_id() -> str:
    """Try to infer parent ID or ask user."""
    # 1. Check Env Var
    if "CONVERSATION_ID" in os.environ:
        return os.environ["CONVERSATION_ID"]
    
    # 2. Check CWD
    cwd = os.getcwd()
    match = re.search(r'(con_[a-zA-Z0-9]+)', cwd)
    if match:
        return match.group(1)
        
    # 3. Ask User
    print("ℹ️  Context required: Which conversation should this task attach to?")
    while True:
        val = input("Parent Conversation ID (e.g., con_XXX): ").strip()
        if val.startswith("con_"):
            return val
        print("❌ Invalid ID. Must start with 'con_'")

def read_prompt_content(path: Path) -> str:
    """Read prompt content, stripping frontmatter."""
    try:
        content = path.read_text()
        # Remove frontmatter if present
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    except Exception as e:
        print(f"⚠️  Error reading prompt: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="N5 Command Dispatcher")
    parser.add_argument("command", nargs="+", help="Command or instruction")
    parser.add_argument("--parent", help="Parent Conversation ID")
    
    # Parse known args to handle flags passed to n5
    args, unknown = parser.parse_known_args()
    
    query = " ".join(args.command)
    
    # 1. Find Prompt
    print(f"🔍 Searching for prompt matching: '{query}'...")
    prompt_file = find_prompt(query)
    
    instruction = ""
    
    if prompt_file:
        print(f"✅ Found Prompt: {prompt_file.name}")
        print(f"   Path: {prompt_file}")
        instruction = read_prompt_content(prompt_file)
    else:
        print(f"⚠️  No specific prompt found. Using input as raw instruction.")
        instruction = query

    # 2. Resolve Parent
    parent = args.parent if args.parent else get_parent_id()
    
    # 3. Launch Worker
    print(f"\n🚀 Dispatching Worker...")
    print(f"   Parent: {parent}")
    print(f"   Task:   {prompt_file.stem if prompt_file else query}")
    
    sys.stdout.flush() # Ensure logs are visible before exec
    
    # Construct command
    cmd = [
        sys.executable,
        str(LAUNCHER_SCRIPT),
        "--parent", parent,
        "--instruction", instruction,
        "--type", "general" # Default to general, maybe infer from tags later
    ]
    
    # Pass through any extra arguments (e.g., --dry-run, --wizard)
    cmd.extend(unknown)
    
    # Execute
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()



