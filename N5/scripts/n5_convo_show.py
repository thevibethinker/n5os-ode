#!/usr/bin/env python3
"""
Show conversation details

Usage:
    n5_convo_show.py con_ABC123 [--full] [--json]
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
import json as json_module

sys.path.insert(0, str(Path(__file__).parent))
from conversation_registry import ConversationRegistry

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def format_timestamp(ts_str):
    """Format ISO timestamp to readable date"""
    if not ts_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return ts_str[:16]


def main():
    parser = argparse.ArgumentParser(description="Show conversation details")
    parser.add_argument("convo_id", help="Conversation ID")
    parser.add_argument("--full", action="store_true", help="Include artifacts, issues, learnings, decisions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    registry = ConversationRegistry()
    
    # Get conversation
    if args.full:
        convo = registry.get_with_details(args.convo_id)
    else:
        convo = registry.get(args.convo_id)
    
    if not convo:
        print(f"Conversation not found: {args.convo_id}")
        return 1
    
    # Output
    if args.json:
        print(json_module.dumps(convo, indent=2))
    else:
        # Human-readable format
        print(f"\n{'='*80}")
        print(f"Conversation: {convo['id']}")
        print(f"{'='*80}\n")
        
        print(f"Type:        {convo.get('type', 'N/A')}")
        print(f"Status:      {convo.get('status', 'N/A')}")
        print(f"Mode:        {convo.get('mode', 'N/A')}")
        print(f"Progress:    {convo.get('progress_pct', 0)}%")
        print(f"Starred:     {'Yes' if convo.get('starred') else 'No'}")
        print()
        
        print(f"Created:     {format_timestamp(convo.get('created_at'))}")
        print(f"Updated:     {format_timestamp(convo.get('updated_at'))}")
        if convo.get('completed_at'):
            print(f"Completed:   {format_timestamp(convo.get('completed_at'))}")
        print()
        
        if convo.get('focus'):
            print(f"Focus:       {convo['focus']}")
        if convo.get('objective'):
            print(f"Objective:   {convo['objective']}")
        if convo.get('tags'):
            print(f"Tags:        {', '.join(convo['tags'])}")
        print()
        
        if convo.get('parent_id'):
            print(f"Parent:      {convo['parent_id']}")
        if convo.get('related_ids'):
            print(f"Related:     {', '.join(convo['related_ids'])}")
        print()
        
        if convo.get('workspace_path'):
            print(f"Workspace:   {convo['workspace_path']}")
        if convo.get('state_file_path'):
            print(f"State File:  {convo['state_file_path']}")
        if convo.get('aar_path'):
            print(f"AAR:         {convo['aar_path']}")
        print()
        
        # Full details
        if args.full:
            artifacts = convo.get('artifacts', [])
            if artifacts:
                print(f"\nArtifacts ({len(artifacts)}):")
                print("-" * 80)
                for art in artifacts:
                    print(f"  [{art.get('artifact_type', '?')}] {art['filepath']}")
                    if art.get('description'):
                        print(f"      {art['description']}")
                print()
            
            issues = convo.get('issues', [])
            if issues:
                print(f"\nIssues ({len(issues)}):")
                print("-" * 80)
                unresolved = [i for i in issues if not i.get('resolved')]
                resolved = [i for i in issues if i.get('resolved')]
                
                if unresolved:
                    print("  Unresolved:")
                    for issue in unresolved:
                        print(f"    [{issue['severity']}] {issue['message']}")
                        print(f"        Category: {issue.get('category', 'N/A')}")
                        print(f"        Time: {format_timestamp(issue['timestamp'])}")
                
                if resolved:
                    print("  Resolved:")
                    for issue in resolved:
                        print(f"    [{issue['severity']}] {issue['message']}")
                        if issue.get('resolution'):
                            print(f"        Resolution: {issue['resolution']}")
                print()
            
            learnings = convo.get('learnings', [])
            if learnings:
                print(f"\nLearnings ({len(learnings)}):")
                print("-" * 80)
                for learning in learnings:
                    print(f"  [{learning['type']}] {learning['title']}")
                    print(f"      {learning['description'][:100]}...")
                    print(f"      Status: {learning.get('status', 'pending')}")
                print()
            
            decisions = convo.get('decisions', [])
            if decisions:
                print(f"\nDecisions ({len(decisions)}):")
                print("-" * 80)
                for decision in decisions:
                    print(f"  {decision['decision']}")
                    if decision.get('rationale'):
                        print(f"      Rationale: {decision['rationale']}")
                    if decision.get('outcome'):
                        print(f"      Outcome: {decision['outcome']}")
                    print(f"      Time: {format_timestamp(decision['timestamp'])}")
                print()
    
    return 0


if __name__ == "__main__":
    exit(main())
