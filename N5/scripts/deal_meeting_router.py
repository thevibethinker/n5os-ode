#!/usr/bin/env python3
"""
Meeting Deal Router - Routes meetings to Zo/Careerspan deal pipelines

Scans meetings for B36_DEAL_ROUTING.json. If missing, generates routing
via LLM classification (dual-lens: Zo relevance + Careerspan relevance).

After B36 generation, triggers B37 deal intel extraction if meeting
involves a deal-related contact (via meeting_deal_intel.py).

Usage:
  python3 deal_meeting_router.py [--limit N] [--dry-run] [--meeting-id ID]

Called by scheduled agent every 6 hours after external sync.
"""

import argparse
import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess

DB_PATH = '/home/workspace/N5/data/deals.db'
MEETINGS_ROOT = '/home/workspace/Personal/Meetings'

# Thresholds
LINK_THRESHOLD = 0.70      # Score to link meeting to existing deal
CREATE_THRESHOLD = 0.85    # Score to auto-create new deal


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def trigger_deal_intel_extraction(meeting_path: str, dry_run: bool = False) -> bool:
    """
    After B36 is generated, check if meeting involves deal contact and generate B37.
    
    Returns True if B37 was generated, False otherwise.
    """
    try:
        from meeting_deal_intel import process_meeting, DealSignalRouter
        from deal_signal_router import DealSignalRouter
        
        router = DealSignalRouter()
        meeting_folder = Path(meeting_path)
        
        intel = process_meeting(meeting_folder, router, dry_run)
        return intel is not None
    except ImportError as e:
        print(f"  ⚠ Could not load meeting_deal_intel: {e}")
        return False
    except Exception as e:
        print(f"  ⚠ Deal intel extraction failed: {e}")
        return False


def find_meetings_needing_routing(limit: int = 25) -> list:
    """
    Find meeting folders that don't have B36_DEAL_ROUTING.json
    """
    meetings = []
    
    for week_dir in sorted(Path(MEETINGS_ROOT).glob('Week-of-*'), reverse=True):
        if len(meetings) >= limit:
            break
            
        for meeting_dir in week_dir.iterdir():
            if not meeting_dir.is_dir():
                continue
            
            routing_file = meeting_dir / 'B36_DEAL_ROUTING.json'
            transcript_file = meeting_dir / 'transcript.md'
            recap_file = meeting_dir / 'B01_DETAILED_RECAP.md'
            
            # Skip if already routed
            if routing_file.exists():
                continue
            
            # Need at least transcript or recap
            if not transcript_file.exists() and not recap_file.exists():
                continue
            
            meetings.append({
                'path': str(meeting_dir),
                'name': meeting_dir.name,
                'has_transcript': transcript_file.exists(),
                'has_recap': recap_file.exists()
            })
            
            if len(meetings) >= limit:
                break
    
    return meetings


def load_existing_deals() -> dict:
    """Load all deals for matching"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, deal_type, company, category, primary_contact
        FROM deals
    ''')
    
    deals = {}
    for row in c.fetchall():
        company_key = row['company'].lower().strip()
        deals[company_key] = {
            'id': row['id'],
            'deal_type': row['deal_type'],
            'company': row['company'],
            'category': row['category'],
            'contact': row['primary_contact']
        }
        # Also add partial matches
        for word in company_key.split():
            if len(word) > 3:
                if word not in deals:
                    deals[word] = deals[company_key]
    
    conn.close()
    return deals


def generate_routing_prompt(meeting_path: str, existing_deals: dict) -> str:
    """Generate the prompt for LLM routing classification"""
    
    # Load meeting content
    content = ""
    recap_path = Path(meeting_path) / 'B01_DETAILED_RECAP.md'
    transcript_path = Path(meeting_path) / 'transcript.md'
    
    if recap_path.exists():
        with open(recap_path, 'r') as f:
            content = f.read()[:8000]  # Limit size
    elif transcript_path.exists():
        with open(transcript_path, 'r') as f:
            content = f.read()[:8000]
    
    meeting_name = Path(meeting_path).name
    
    # List existing deals for matching
    deal_list = "\n".join([
        f"- {d['company']} ({d['deal_type']})" 
        for d in list(existing_deals.values())[:50]
    ])
    
    prompt = f"""Analyze this meeting and classify its relevance to deal pipelines.

MEETING: {meeting_name}

CONTENT:
{content}

EXISTING DEALS (for matching):
{deal_list}

OUTPUT STRICT JSON with these fields:
{{
  "zo_relevance_score": 0.0-1.0,  // How relevant to Zo partnerships/GTM
  "careerspan_relevance_score": 0.0-1.0,  // How relevant to Careerspan acquisition
  "zo_reasoning": "brief explanation",
  "careerspan_reasoning": "brief explanation",
  "companies_mentioned": [
    {{"name": "Company Name", "match_to_deal_id": "deal-id-or-null", "context": "why mentioned"}}
  ],
  "recommended_deal_links": ["deal-id-1", "deal-id-2"],
  "create_new_deals": [
    {{"company": "Name", "deal_type": "zo_partnership|careerspan_acquirer", "confidence": 0.0-1.0, "rationale": "why"}}
  ],
  "summary": "1-2 sentence summary of meeting's deal relevance"
}}

Be conservative with create_new_deals - only if clearly actionable and confidence >= 0.85.
A meeting can be relevant to BOTH pipelines (overlap allowed).
"""
    return prompt


def route_meeting(meeting: dict, existing_deals: dict, dry_run: bool = False) -> dict:
    """
    Route a single meeting using LLM classification.
    Returns the routing result.
    """
    prompt = generate_routing_prompt(meeting['path'], existing_deals)
    
    # For now, output the prompt - actual LLM call happens via Zo /zo/ask
    # This script generates the work; Zo executes the LLM calls
    
    result = {
        'meeting_path': meeting['path'],
        'meeting_name': meeting['name'],
        'status': 'pending_llm',
        'prompt': prompt,
        'timestamp': datetime.now().isoformat()
    }
    
    return result


def write_routing_output(meeting_path: str, routing_data: dict):
    """Write B36_DEAL_ROUTING.json and .md to meeting folder"""
    
    json_path = Path(meeting_path) / 'B36_DEAL_ROUTING.json'
    md_path = Path(meeting_path) / 'B36_DEAL_ROUTING.md'
    
    # Write JSON
    with open(json_path, 'w') as f:
        json.dump(routing_data, f, indent=2)
    
    # Write markdown summary
    md_content = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: deal_meeting_router
---

# B36 Deal Routing

## Relevance Scores
- **Zo Partnership Relevance:** {routing_data.get('zo_relevance_score', 0):.2f}
- **Careerspan Acquisition Relevance:** {routing_data.get('careerspan_relevance_score', 0):.2f}

## Summary
{routing_data.get('summary', 'No summary available')}

## Companies Mentioned
"""
    
    for company in routing_data.get('companies_mentioned', []):
        md_content += f"- **{company.get('name', 'Unknown')}**: {company.get('context', '')}\n"
        if company.get('match_to_deal_id'):
            md_content += f"  - Matched to deal: `{company['match_to_deal_id']}`\n"
    
    md_content += f"""
## Deal Links
"""
    for deal_id in routing_data.get('recommended_deal_links', []):
        md_content += f"- `{deal_id}`\n"
    
    if routing_data.get('create_new_deals'):
        md_content += f"""
## Auto-Created Deals
"""
        for deal in routing_data['create_new_deals']:
            md_content += f"- **{deal.get('company')}** ({deal.get('deal_type')}) - confidence: {deal.get('confidence', 0):.2f}\n"
    
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    print(f"  ✓ Wrote {json_path.name} and {md_path.name}")


def link_meeting_to_deal(meeting_path: str, deal_id: str, lens_scores: dict):
    """Record meeting-deal link in deal_activities"""
    conn = get_db()
    c = conn.cursor()
    
    meeting_name = Path(meeting_path).name
    activity_id = f"act-{deal_id}-{meeting_name[:20]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    c.execute('''
        INSERT INTO deal_activities (
            id, deal_id, activity_type, description, metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        activity_id,
        deal_id,
        'meeting_linked',
        f"Meeting linked: {meeting_name}",
        json.dumps({
            'meeting_path': meeting_path,
            'zo_score': lens_scores.get('zo_relevance_score'),
            'careerspan_score': lens_scores.get('careerspan_relevance_score'),
            'linked_at': datetime.now().isoformat()
        }),
        datetime.now().isoformat()
    ))
    
    # Update deal's last_touched
    c.execute('UPDATE deals SET last_touched = ? WHERE id = ?',
              (datetime.now().isoformat(), deal_id))
    
    conn.commit()
    conn.close()
    print(f"  ✓ Linked meeting to deal: {deal_id}")


def auto_create_deal(company: str, deal_type: str, meeting_path: str, confidence: float, rationale: str) -> str:
    """Auto-create a new deal from meeting mention"""
    conn = get_db()
    c = conn.cursor()
    
    import re
    company_key = re.sub(r'[^a-z0-9]', '', company.lower())
    deal_id = f"auto-{deal_type[:5]}-{company_key[:15]}-{datetime.now().strftime('%Y%m%d')}"
    
    meeting_name = Path(meeting_path).name
    
    c.execute('''
        INSERT INTO deals (
            id, deal_type, company, stage, owner,
            source_system, source_id, metadata_json,
            first_identified, last_touched
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        deal_id,
        deal_type,
        company,
        'identified',
        'V',
        'auto_meeting',
        f"meeting:{meeting_name}",
        json.dumps({
            'auto_created': True,
            'source_meeting': meeting_path,
            'confidence': confidence,
            'rationale': rationale,
            'created_at': datetime.now().isoformat()
        }),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))
    
    # Log activity
    activity_id = f"act-{deal_id}-created-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    c.execute('''
        INSERT INTO deal_activities (
            id, deal_id, activity_type, description, metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        activity_id,
        deal_id,
        'auto_created_from_meeting',
        f"Auto-created from meeting: {meeting_name}",
        json.dumps({
            'meeting_path': meeting_path,
            'confidence': confidence,
            'rationale': rationale
        }),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    print(f"  ✓ Auto-created deal: {deal_id} ({company})")
    return deal_id


def main():
    parser = argparse.ArgumentParser(description='Route meetings to deal pipelines')
    parser.add_argument('--limit', type=int, default=25, help='Max meetings to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    parser.add_argument('--meeting-id', help='Process specific meeting folder name')
    parser.add_argument('--output-prompts', help='Output prompts to file for batch LLM processing')
    args = parser.parse_args()
    
    # Find meetings needing routing
    if args.meeting_id:
        # Find specific meeting
        meetings = []
        for week_dir in Path(MEETINGS_ROOT).glob('Week-of-*'):
            for meeting_dir in week_dir.iterdir():
                if meeting_dir.name == args.meeting_id:
                    meetings.append({
                        'path': str(meeting_dir),
                        'name': meeting_dir.name,
                        'has_transcript': (meeting_dir / 'transcript.md').exists(),
                        'has_recap': (meeting_dir / 'B01_DETAILED_RECAP.md').exists()
                    })
                    break
    else:
        meetings = find_meetings_needing_routing(args.limit)
    
    if not meetings:
        print("✓ No meetings need routing")
        return {'status': 'complete', 'processed': 0}
    
    print(f"Found {len(meetings)} meetings needing routing")
    
    # Load existing deals for matching
    existing_deals = load_existing_deals()
    print(f"Loaded {len(existing_deals)} existing deals for matching")
    
    # Generate routing tasks
    tasks = []
    for meeting in meetings:
        result = route_meeting(meeting, existing_deals, args.dry_run)
        tasks.append(result)
    
    if args.output_prompts:
        # Output prompts for batch processing
        with open(args.output_prompts, 'w') as f:
            for task in tasks:
                f.write(json.dumps({
                    'meeting_path': task['meeting_path'],
                    'meeting_name': task['meeting_name'],
                    'prompt': task['prompt']
                }) + '\n')
        print(f"\n✓ Wrote {len(tasks)} prompts to {args.output_prompts}")
        print("  Run LLM batch processing, then call with --apply-results")
    else:
        print(f"\n=== Routing Tasks Generated ===")
        print(f"Total: {len(tasks)} meetings")
        print("\nTo process with LLM:")
        print(f"  python3 deal_meeting_router.py --output-prompts /tmp/routing_prompts.jsonl")
        print("  # Then process prompts via /zo/ask API")
    
    return {'status': 'tasks_generated', 'count': len(tasks)}


if __name__ == '__main__':
    main()
