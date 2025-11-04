#!/usr/bin/env python3
"""
Analyze conversation patterns to tune persona router
Samples recent conversations and extracts user message patterns
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

def find_conversations(limit=30):
    """Find recent conversation directories"""
    workspace_dir = Path("/home/.z/workspaces")
    conversations = []
    
    for conv_dir in workspace_dir.iterdir():
        if conv_dir.is_dir() and conv_dir.name.startswith("con_"):
            # Get modification time
            mtime = conv_dir.stat().st_mtime
            conversations.append((mtime, conv_dir))
    
    # Sort by most recent
    conversations.sort(reverse=True)
    return [conv[1] for conv in conversations[:limit]]

def extract_user_messages(conv_dir: Path) -> List[str]:
    """Extract user messages from conversation markdown files"""
    messages = []
    
    for md_file in conv_dir.glob("*.md"):
        try:
            content = md_file.read_text()
            # Simple extraction - look for user message patterns
            # This is rough but sufficient for sampling
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('USER:') or line.startswith('# User'):
                    # Get next non-empty line
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip():
                            messages.append(lines[j].strip()[:200])  # First 200 chars
                            break
        except:
            pass
    
    return messages

def categorize_message(message: str) -> List[str]:
    """Manually categorize what persona(s) this message should trigger"""
    msg_lower = message.lower()
    categories = []
    
    # Research patterns
    if any(word in msg_lower for word in ['research', 'find', 'search', 'look up', 'investigate', 'explore', 'discover']):
        categories.append('researcher')
    
    # Strategy patterns
    if any(word in msg_lower for word in ['strategy', 'should we', 'should i', 'decision', 'options', 'approach', 'recommend', 'best way']):
        categories.append('strategist')
    
    # Teaching patterns
    if any(word in msg_lower for word in ['explain', 'how does', 'what is', 'understand', 'learn', 'teach', 'why does']):
        categories.append('teacher')
    
    # Builder patterns
    if any(word in msg_lower for word in ['build', 'create', 'implement', 'code', 'develop', 'make', 'script']):
        categories.append('builder')
    
    # Writer patterns
    if any(word in msg_lower for word in ['write', 'draft', 'compose', 'email', 'post', 'document']):
        categories.append('writer')
    
    # Debugger patterns
    if any(word in msg_lower for word in ['debug', 'fix', 'error', 'bug', 'broken', 'not working', 'issue']):
        categories.append('debugger')
    
    # Architect patterns
    if any(word in msg_lower for word in ['design', 'architecture', 'system', 'structure', 'organize', 'framework']):
        categories.append('architect')
    
    # Default to operator if no specific match
    if not categories:
        categories.append('operator')
    
    return categories

def main():
    print("Analyzing conversation patterns...\n")
    
    conversations = find_conversations(30)
    print(f"Found {len(conversations)} recent conversations\n")
    
    all_messages = []
    persona_samples = defaultdict(list)
    
    for conv_dir in conversations:
        messages = extract_user_messages(conv_dir)
        for msg in messages:
            if len(msg) > 10:  # Filter out very short messages
                personas = categorize_message(msg)
                all_messages.append({
                    'message': msg,
                    'personas': personas,
                    'conversation': conv_dir.name
                })
                for persona in personas:
                    persona_samples[persona].append(msg)
    
    print(f"Extracted {len(all_messages)} user messages\n")
    print("="*70)
    print("\nPERSONA DISTRIBUTION:")
    print("="*70)
    
    for persona, samples in sorted(persona_samples.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n{persona.upper()}: {len(samples)} messages")
        print("-" * 50)
        for i, sample in enumerate(samples[:5], 1):  # Show top 5
            print(f"{i}. {sample[:100]}...")
    
    # Save full results
    output_file = Path("/home/.z/workspaces/con_MkzEBdTNQKB8hgj2/conversation_patterns.json")
    output_file.write_text(json.dumps({
        'total_messages': len(all_messages),
        'persona_distribution': {k: len(v) for k, v in persona_samples.items()},
        'samples': all_messages[:50]  # Save first 50 for detailed review
    }, indent=2))
    
    print(f"\n\nFull results saved to: {output_file}")
    print("\nUse these patterns to tune persona_router.py triggers")

if __name__ == "__main__":
    main()
