#!/usr/bin/env python3
"""
External Deal Sync - One-way sync from external sources to deals.db

Sources:
  1. Zo Data Partnerships (Google Sheet)
  2. Careerspan Acquirer Targets (Notion - via browser scrape)
  3. Careerspan Leadership (Notion - via browser scrape)

Usage:
  python3 deal_sync_external.py [--source zo|acquirers|leadership|all] [--dry-run]

This script is called by the scheduled agent every 6 hours.
For Notion sources, the actual data fetch is done by Zo's browser tools,
and this script processes the cached markdown files.
"""

import argparse
import sqlite3
import json
import re
import os
from datetime import datetime
from pathlib import Path

DB_PATH = '/home/workspace/N5/data/deals.db'
CACHE_DIR = '/home/workspace/N5/cache/deal_sync'

# Ensure cache dir exists
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sync_zo_partnerships(dry_run: bool = False) -> dict:
    """
    Sync Zo Data Partnerships from cached xlsx/markdown.
    The actual fetch is done by Zo tool calls before this runs.
    """
    cache_file = f"{CACHE_DIR}/zo_partnerships.jsonl"
    
    if not os.path.exists(cache_file):
        print(f"⚠ Cache file not found: {cache_file}")
        print("  Run: python3 deal_sync_external.py --fetch-zo first")
        return {'status': 'skipped', 'reason': 'no_cache'}
    
    records = []
    with open(cache_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if dry_run:
        print(f"[DRY RUN] Would sync {len(records)} Zo partnership records")
        return {'status': 'dry_run', 'count': len(records)}
    
    conn = get_db()
    c = conn.cursor()
    
    inserted = updated = 0
    for r in records:
        deal_id = r.get('id') or f"zo-dp-{re.sub(r'[^a-z0-9]', '', r['Company'].lower())[:20]}"
        
        c.execute('SELECT id FROM deals WHERE id = ?', (deal_id,))
        exists = c.fetchone()
        
        metadata = {
            'founder': r.get('Founder'),
            'implementation': r.get('Implementation'),
            'last_synced': datetime.now().isoformat(),
            'source': 'google_sheets'
        }
        
        if exists:
            c.execute('''
                UPDATE deals SET
                    company = ?, website = ?, category = ?, temperature = ?,
                    owner = ?, notes = ?, metadata_json = ?, last_touched = ?
                WHERE id = ?
            ''', (
                r['Company'], r.get('Website'), r.get('category'),
                r.get('Warmth', '').lower() if r.get('Warmth') else None,
                r.get('Liaison'), r.get('Notes'),
                json.dumps(metadata), datetime.now().isoformat(), deal_id
            ))
            updated += 1
        else:
            c.execute('''
                INSERT INTO deals (
                    id, deal_type, company, website, category,
                    temperature, stage, owner, notes,
                    source_system, source_id, metadata_json,
                    first_identified, last_touched
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deal_id, 'zo_partnership', r['Company'], r.get('Website'),
                r.get('category'), r.get('Warmth', '').lower() if r.get('Warmth') else None,
                'identified', r.get('Liaison'), r.get('Notes'),
                'google_sheets', r.get('source_id', f"gsheet:{deal_id}"),
                json.dumps(metadata), datetime.now().isoformat(), datetime.now().isoformat()
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Zo Partnerships synced: {inserted} inserted, {updated} updated")
    return {'status': 'success', 'inserted': inserted, 'updated': updated}


def sync_careerspan_acquirers(dry_run: bool = False) -> dict:
    """
    Sync Careerspan Acquirer Targets from cached Notion scrape.
    """
    cache_file = f"{CACHE_DIR}/careerspan_acquirers.jsonl"
    
    if not os.path.exists(cache_file):
        print(f"⚠ Cache file not found: {cache_file}")
        return {'status': 'skipped', 'reason': 'no_cache'}
    
    records = []
    with open(cache_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if dry_run:
        print(f"[DRY RUN] Would sync {len(records)} Careerspan acquirer records")
        return {'status': 'dry_run', 'count': len(records)}
    
    conn = get_db()
    c = conn.cursor()
    
    # Temperature mapping: normalize Notion values to our schema
    temp_map = {
        'hot': 'hot',
        'warm': 'warm', 
        'temperate': 'warm',  # Temperate -> warm
        'cool': 'cold',       # Cool -> cold
        'cold': 'cold',
    }
    
    inserted = updated = 0
    for r in records:
        # Generate deal ID from company name if not present
        company = r.get('company', '')
        deal_id = r.get('id') or f"cs-acq-{re.sub(r'[^a-z0-9]', '', company.lower())[:20]}"
        
        # Get temperature from "deal temp" field and normalize
        raw_temp = r.get('deal temp', r.get('temperature', '')).lower().strip()
        temperature = temp_map.get(raw_temp, None)
        
        c.execute('SELECT id FROM deals WHERE id = ?', (deal_id,))
        exists = c.fetchone()
        
        if exists:
            c.execute('''
                UPDATE deals SET
                    company = ?, category = ?, proximity = ?, temperature = ?,
                    exit_type = ?, website = ?, notes = ?, metadata_json = ?,
                    last_touched = ?
                WHERE id = ?
            ''', (
                company, r.get('category'), r.get('proximity'),
                temperature, r.get('deal type'), r.get('website'),
                r.get('notes'), json.dumps(r), datetime.now().isoformat(),
                deal_id
            ))
            updated += 1
        else:
            c.execute('''
                INSERT INTO deals (
                    id, deal_type, company, category, proximity, temperature,
                    exit_type, stage, owner, website, notes,
                    source_system, source_id, metadata_json,
                    first_identified, last_touched
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deal_id, 'careerspan_acquirer', company, r.get('category'),
                r.get('proximity'), temperature, r.get('deal type'),
                'identified', 'V', r.get('website'), r.get('notes'),
                'notion', f"notion:{deal_id}", json.dumps(r),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Careerspan Acquirers synced: {inserted} inserted, {updated} updated")
    return {'status': 'success', 'inserted': inserted, 'updated': updated}


def sync_careerspan_leadership(dry_run: bool = False) -> dict:
    """
    Sync Careerspan Leadership from cached Notion scrape.
    Leadership entries are stored as careerspan_acquirer with category='leadership'.
    """
    cache_file = f"{CACHE_DIR}/careerspan_leadership.jsonl"
    
    if not os.path.exists(cache_file):
        print(f"⚠ Cache file not found: {cache_file}")
        return {'status': 'skipped', 'reason': 'no_cache'}
    
    records = []
    with open(cache_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if dry_run:
        print(f"[DRY RUN] Would sync {len(records)} leadership records")
        return {'status': 'dry_run', 'count': len(records)}
    
    conn = get_db()
    c = conn.cursor()
    
    inserted = updated = 0
    for r in records:
        # Generate deal ID from person name or notion_id
        person = r.get('person', '').strip()
        notion_id = r.get('notion_id', '')
        deal_id = r.get('id') or f"cs-lead-{re.sub(r'[^a-z0-9]', '', person.lower())[:20]}" if person else f"cs-lead-{notion_id[:12]}"
        
        # Use person as company placeholder (actual company requires resolving company_relation)
        company_placeholder = f"[Leadership: {person}]" if person else "[Unknown]"
        
        metadata = {
            'notion_id': notion_id,
            'notion_url': r.get('url'),
            'linkedin_url': r.get('linkedin_url'),
            'x_handle': r.get('x_handle'),
            'second_degree_connects': r.get('2nd_degree_connects'),
            'notes_thesis': r.get('notes_thesis'),
            'company_relation_ids': r.get('company_relation', []),
            'roles': r.get('roles', []),
            'last_synced': datetime.now().isoformat(),
        }
        
        c.execute('SELECT id FROM deals WHERE id = ?', (deal_id,))
        exists = c.fetchone()
        
        if exists:
            c.execute('''
                UPDATE deals SET
                    company = ?, primary_contact = ?, category = ?,
                    website = ?, notes = ?,
                    metadata_json = ?, last_touched = ?
                WHERE id = ?
            ''', (
                company_placeholder, person, 'leadership',
                r.get('linkedin_url'), r.get('notes_thesis'),
                json.dumps(metadata), datetime.now().isoformat(), deal_id
            ))
            updated += 1
        else:
            c.execute('''
                INSERT INTO deals (
                    id, deal_type, company, primary_contact, category,
                    stage, owner, website, notes,
                    source_system, source_id, metadata_json,
                    first_identified, last_touched
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deal_id, 'careerspan_acquirer', company_placeholder,
                person, 'leadership',
                'identified', 'V', r.get('linkedin_url'), r.get('notes_thesis'),
                'notion', f"notion:{notion_id}", json.dumps(metadata),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Careerspan Leadership synced: {inserted} inserted, {updated} updated")
    return {'status': 'success', 'inserted': inserted, 'updated': updated}



def sync_deal_brokers(dry_run: bool = False) -> dict:
    """Sync Deal Brokers to deal_contacts table"""
    cache_file = f"{CACHE_DIR}/deal_brokers.jsonl"
    
    if not os.path.exists(cache_file):
        print(f"⚠ Cache file not found: {cache_file}")
        return {'status': 'skipped', 'reason': 'no_cache'}
    
    records = []
    with open(cache_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if dry_run:
        print(f"[DRY RUN] Would sync {len(records)} broker records")
        return {'status': 'dry_run', 'count': len(records)}
    
    conn = get_db()
    c = conn.cursor()
    
    inserted = updated = 0
    for r in records:
        contact_id = r.get('id', f"broker-{re.sub(r'[^a-z0-9]', '', r.get('contact', 'unknown').lower())[:20]}")
        
        c.execute('SELECT id FROM deal_contacts WHERE id = ?', (contact_id,))
        exists = c.fetchone()
        
        if exists:
            c.execute('''
                UPDATE deal_contacts SET
                    full_name = ?, company = ?, angle_strategy = ?,
                    blurb = ?, notion_url = ?, metadata_json = ?, updated_at = ?
                WHERE id = ?
            ''', (
                r.get('contact'), r.get('company'), r.get('angle_strategy'),
                r.get('blurb'), r.get('notion_url'),
                json.dumps(r.get('metadata', {})), datetime.now().isoformat(),
                contact_id
            ))
            updated += 1
        else:
            c.execute('''
                INSERT INTO deal_contacts (
                    id, contact_type, pipeline, full_name,
                    company, angle_strategy, blurb, notion_url,
                    source_system, source_id, metadata_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_id, 'broker', 'careerspan', r.get('contact'),
                r.get('company'), r.get('angle_strategy'), r.get('blurb'),
                r.get('notion_url'), 'notion', r.get('notion_id'),
                json.dumps(r.get('metadata', {})),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Deal Brokers synced: {inserted} inserted, {updated} updated")
    return {'status': 'success', 'inserted': inserted, 'updated': updated}


def sync_leadership_targets(dry_run: bool = False) -> dict:
    """Sync Leadership Targets to deal_contacts table"""
    cache_file = f"{CACHE_DIR}/careerspan_leadership.jsonl"
    
    if not os.path.exists(cache_file):
        print(f"⚠ Cache file not found: {cache_file}")
        return {'status': 'skipped', 'reason': 'no_cache'}
    
    records = []
    with open(cache_file, 'r') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    if dry_run:
        print(f"[DRY RUN] Would sync {len(records)} leadership records")
        return {'status': 'dry_run', 'count': len(records)}
    
    conn = get_db()
    c = conn.cursor()
    
    inserted = updated = 0
    for r in records:
        contact_id = r.get('id', f"lead-{re.sub(r'[^a-z0-9]', '', r.get('person', 'unknown').lower())[:20]}")
        
        # Try to find associated deal
        company = r.get('company')
        associated_deal = None
        if company:
            c.execute("SELECT id FROM deals WHERE deal_type = 'careerspan_acquirer' AND company LIKE ?", 
                     (f'%{company}%',))
            match = c.fetchone()
            if match:
                associated_deal = match['id']
        
        c.execute('SELECT id FROM deal_contacts WHERE id = ?', (contact_id,))
        exists = c.fetchone()
        
        if exists:
            c.execute('''
                UPDATE deal_contacts SET
                    full_name = ?, company = ?, linkedin_url = ?,
                    second_degree_connects = ?, associated_deal_id = ?,
                    notion_url = ?, metadata_json = ?, updated_at = ?
                WHERE id = ?
            ''', (
                r.get('person'), company, r.get('linkedin_url'),
                r.get('second_degree_connects'), associated_deal,
                r.get('notion_url'), json.dumps(r.get('metadata', {})),
                datetime.now().isoformat(), contact_id
            ))
            updated += 1
        else:
            c.execute('''
                INSERT INTO deal_contacts (
                    id, contact_type, pipeline, full_name,
                    company, linkedin_url, second_degree_connects,
                    associated_deal_id, notion_url,
                    source_system, source_id, metadata_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_id, 'leadership', 'careerspan', r.get('person'),
                company, r.get('linkedin_url'), r.get('second_degree_connects'),
                associated_deal, r.get('notion_url'),
                'notion', r.get('notion_id'), json.dumps(r.get('metadata', {})),
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"✓ Leadership Targets synced: {inserted} inserted, {updated} updated")
    return {'status': 'success', 'inserted': inserted, 'updated': updated}


def main():
    parser = argparse.ArgumentParser(description='Sync external deal sources to deals.db')
    parser.add_argument('--source', choices=['zo', 'acquirers', 'leadership', 'all'],
                        default='all', help='Which source to sync')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    args = parser.parse_args()
    
    results = {}
    
    if args.source in ['zo', 'all']:
        results['zo'] = sync_zo_partnerships(args.dry_run)
    
    if args.source in ['acquirers', 'all']:
        results['acquirers'] = sync_careerspan_acquirers(args.dry_run)
    
    if args.source in ['leadership', 'all']:
        results['leadership'] = sync_careerspan_leadership(args.dry_run)
    
    print(f"\n=== Sync Summary ===")
    print(json.dumps(results, indent=2))
    
    return results


if __name__ == '__main__':
    main()

