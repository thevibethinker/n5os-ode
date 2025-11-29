#!/usr/bin/env python3
"""
CRM V3 Command Line Interface

Provides direct control over CRM data with simple, powerful commands:
- Manual profile creation
- Intelligent search
- AI-powered intelligence synthesis
- Enrichment queue management
- Statistics and listing

Usage:
    crm create --email john@example.com --name "John Doe" [options]
    crm search --email john@example.com
    crm intel --email john@example.com
    crm enrich --email john@example.com
    crm list [--category INVESTOR] [--limit 20]
    crm stats
"""

import argparse
import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Import helper functions
sys.path.insert(0, '/home/workspace/N5/scripts')
from crm_calendar_helpers import (
    get_or_create_profile,
    schedule_enrichment_job,
    get_db_connection
)

DB_PATH = '/home/workspace/N5/data/crm_v3.db'
PROFILES_DIR = Path('/home/workspace/N5/crm_v3/profiles')


def create_profile(email: str, name: str, category: str = 'NETWORKING', notes: str = None):
    """
    Manually create profile.
    
    Args:
        email: Contact email
        name: Full name
        category: NETWORKING | INVESTOR | ADVISOR | COMMUNITY
        notes: Optional notes
    """
    try:
        # Check if profile already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, yaml_path FROM profiles WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠ Profile already exists: {existing[1]} (ID: {existing[0]})")
            print(f"  Path: {existing[2]}")
            conn.close()
            return
        
        # Create profile using helper (doesn't accept category)
        profile_id = get_or_create_profile(
            email=email,
            name=name,
            source='manual_cli'
        )
        
        # Update category in database
        cursor.execute("UPDATE profiles SET category = ? WHERE id = ?", (category, profile_id))
        conn.commit()
        
        # Get yaml_path from database
        cursor.execute("SELECT yaml_path FROM profiles WHERE id = ?", (profile_id,))
        yaml_path = cursor.fetchone()[0]
        yaml_file = Path(yaml_path)
        
        # Append notes to YAML if provided
        if notes:
            if yaml_file.exists():
                with open(yaml_file, 'a') as f:
                    f.write(f"\n# Manual Notes (CLI)\n{notes}\n")
        
        # Schedule immediate enrichment
        schedule_enrichment_job(
            profile_id=profile_id,
            scheduled_for=datetime.now().isoformat(),
            checkpoint='checkpoint_2',
            priority=100,
            trigger_source='manual'
        )
        
        conn.close()
        
        # Success message
        print(f"✓ Profile created: {yaml_file.stem} (ID: {profile_id})")
        print(f"  Email: {email}")
        print(f"  Category: {category}")
        print(f"  Path: {yaml_path}")
        print(f"  Enrichment: Queued (priority 100, immediate)")
        
    except Exception as e:
        print(f"✗ Error creating profile: {e}", file=sys.stderr)
        sys.exit(1)


def search_profiles(email: str = None, name: str = None, company: str = None):
    """
    Search profiles by email, name, or company.
    
    Args:
        email: Exact email match
        name: Fuzzy name search
        company: Company domain search
    """
    if not any([email, name, company]):
        print("⚠ Please provide at least one search parameter (--email, --name, or --company)")
        sys.exit(1)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query
        conditions = []
        params = []
        
        if email:
            conditions.append("email = ?")
            params.append(email)
        
        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")
        
        if company:
            conditions.append("email LIKE ?")
            params.append(f"%@{company}%")
        
        query = f"""
            SELECT id, email, name, category, last_contact_at, meeting_count, 
                   profile_quality, yaml_path
            FROM profiles
            WHERE {' OR '.join(conditions)}
            ORDER BY last_contact_at DESC NULLS LAST
        """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No profiles found.")
            return
        
        print(f"Found {len(results)} profile(s):\n")
        
        for i, row in enumerate(results, 1):
            profile_id, email, name, category, last_contact, meeting_count, quality, yaml_path = row
            
            last_contact_str = last_contact if last_contact else "Never"
            category_str = category if category else "Uncategorized"
            
            print(f"[{i}] {name} ({email})")
            print(f"    Category: {category_str} | Quality: {quality} | Last Contact: {last_contact_str}")
            print(f"    Meetings: {meeting_count} | Path: {yaml_path}\n")
    
    except Exception as e:
        print(f"✗ Error searching profiles: {e}", file=sys.stderr)
        sys.exit(1)


def get_intelligence_synthesis(email: str = None, profile_id: int = None):
    """
    AI-powered intelligence synthesis across all sources.
    
    Args:
        email: Profile email
        profile_id: Profile database ID
    """
    if not email and not profile_id:
        print("⚠ Please provide either --email or --id")
        sys.exit(1)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Fetch profile
        if profile_id:
            cursor.execute("""
                SELECT id, email, name, yaml_path, category, last_contact_at, 
                       meeting_count, profile_quality, relationship_strength
                FROM profiles WHERE id = ?
            """, (profile_id,))
        else:
            cursor.execute("""
                SELECT id, email, name, yaml_path, category, last_contact_at, 
                       meeting_count, profile_quality, relationship_strength
                FROM profiles WHERE email = ?
            """, (email,))
        
        profile = cursor.fetchone()
        
        if not profile:
            print(f"✗ Profile not found")
            conn.close()
            sys.exit(1)
        
        profile_id, email, name, yaml_path, category, last_contact, meeting_count, quality, strength = profile
        
        # Read YAML file
        yaml_file = Path(yaml_path)
        yaml_content = ""
        if yaml_file.exists():
            with open(yaml_file, 'r') as f:
                yaml_content = f.read()
        
        # Query intelligence sources
        cursor.execute("""
            SELECT source_type, source_path, summary, 
                   source_date, created_at
            FROM intelligence_sources
            WHERE profile_id = ?
            ORDER BY source_date DESC
        """, (profile_id,))
        sources = cursor.fetchall()
        conn.close()
        
        # Display synthesis header
        print(f"\n{'='*70}")
        print(f"Intelligence Synthesis: {name} ({email})")
        print(f"{'='*70}\n")
        
        # Overview section
        print("Overview:")
        print(f"- Profile ID: {profile_id}")
        print(f"- Category: {category or 'Uncategorized'}")
        print(f"- Quality: {quality}")
        if strength:
            print(f"- Relationship Strength: {strength}")
        print()
        
        # Relationship context
        print("Relationship:")
        print(f"- Meetings: {meeting_count}")
        print(f"- Last Contact: {last_contact or 'Never'}")
        
        # Calculate days since last contact
        if last_contact:
            try:
                last_dt = datetime.fromisoformat(last_contact.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_dt.replace(tzinfo=None)).days
                print(f"- Days Since Contact: {days_ago}")
            except:
                pass
        print()
        
        # Intelligence sources summary
        print(f"Intelligence Sources ({len(sources)} total):")
        if sources:
            source_types = {}
            for source in sources:
                source_type = source[0]
                source_types[source_type] = source_types.get(source_type, 0) + 1
            
            for source_type, count in source_types.items():
                print(f"- {source_type}: {count}")
            print()
            
            # Show recent sources
            print("Recent Sources:")
            for source in sources[:5]:
                source_type, path, summary, source_date, created_at = source
                summary_short = summary[:80] + "..." if summary and len(summary) > 80 else summary
                print(f"- [{source_type}] {source_date}")
                if path:
                    print(f"  Path: {path}")
                if summary_short:
                    print(f"  {summary_short}")
        else:
            print("- No intelligence sources yet")
            print()
        
        # Profile data preview
        print("Profile Data Preview:")
        yaml_lines = yaml_content.split('\n')
        preview_lines = yaml_lines[:15]
        for line in preview_lines:
            print(f"  {line}")
        if len(yaml_lines) > 15:
            print(f"  ... ({len(yaml_lines) - 15} more lines)")
        print()
        
        print(f"{'='*70}")
        print(f"Full profile: {yaml_path}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"✗ Error generating intelligence: {e}", file=sys.stderr)
        sys.exit(1)


def queue_enrichment(email: str, priority: int = 100):
    """
    Manually queue enrichment for profile.
    
    Args:
        email: Profile email
        priority: Enrichment priority (100=immediate, 75=3-day, 25=gmail)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find profile
        cursor.execute("SELECT id, name FROM profiles WHERE email = ?", (email,))
        profile = cursor.fetchone()
        
        if not profile:
            print(f"✗ Profile not found: {email}")
            conn.close()
            sys.exit(1)
        
        profile_id, name = profile
        
        # Determine checkpoint based on priority
        checkpoint = 'checkpoint_2' if priority >= 75 else 'checkpoint_1'
        
        # Schedule enrichment
        schedule_enrichment_job(
            profile_id=profile_id,
            scheduled_for=datetime.now().isoformat(),
            checkpoint=checkpoint,
            priority=priority,
            trigger_source='manual'
        )
        
        conn.close()
        
        print(f"✓ Enrichment queued for: {name} ({email})")
        print(f"  Profile ID: {profile_id}")
        print(f"  Priority: {priority}")
        print(f"  Scheduled: Immediate")
        
    except Exception as e:
        print(f"✗ Error queueing enrichment: {e}", file=sys.stderr)
        sys.exit(1)


def list_profiles(category: str = None, limit: int = 20):
    """
    List profiles with filters.
    
    Args:
        category: Filter by category (NETWORKING, INVESTOR, ADVISOR, COMMUNITY)
        limit: Max number of profiles to show
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            query = """
                SELECT id, name, email, category, profile_quality, last_contact_at
                FROM profiles
                WHERE category = ?
                ORDER BY last_contact_at DESC NULLS LAST
                LIMIT ?
            """
            cursor.execute(query, (category, limit))
        else:
            query = """
                SELECT id, name, email, category, profile_quality, last_contact_at
                FROM profiles
                ORDER BY last_contact_at DESC NULLS LAST
                LIMIT ?
            """
            cursor.execute(query, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("No profiles found.")
            return
        
        filter_str = f" (Category: {category})" if category else ""
        print(f"Profiles{filter_str} (showing {len(results)}):\n")
        
        for row in results:
            profile_id, name, email, cat, quality, last_contact = row
            last_contact_str = last_contact if last_contact else "Never"
            cat_str = cat if cat else "Uncategorized"
            
            print(f"[{profile_id:3d}] {name:30s} | {cat_str:12s} | {quality:10s} | {last_contact_str}")
        
        print()
        
    except Exception as e:
        print(f"✗ Error listing profiles: {e}", file=sys.stderr)
        sys.exit(1)


def show_stats():
    """
    Display CRM statistics.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total profiles
        cursor.execute("SELECT COUNT(*) FROM profiles")
        total_profiles = cursor.fetchone()[0]
        
        # Profiles by category
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM profiles 
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        by_category = cursor.fetchall()
        
        # Profiles by quality
        cursor.execute("""
            SELECT profile_quality, COUNT(*) 
            FROM profiles 
            GROUP BY profile_quality
        """)
        by_quality = cursor.fetchall()
        
        # Enrichment queue
        cursor.execute("""
            SELECT COUNT(*) 
            FROM enrichment_queue 
            WHERE status = 'pending'
        """)
        pending_jobs = cursor.fetchone()[0]
        
        # Enrichment queue by priority
        cursor.execute("""
            SELECT priority, COUNT(*) 
            FROM enrichment_queue 
            WHERE status = 'pending'
            GROUP BY priority
            ORDER BY priority DESC
        """)
        by_priority = cursor.fetchall()
        
        # Recent activity
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM profiles 
            WHERE created_at >= ?
        """, (seven_days_ago,))
        recent_profiles = cursor.fetchone()[0]
        
        conn.close()
        
        # Display
        print("\n" + "="*50)
        print("CRM V3 Statistics")
        print("="*50 + "\n")
        
        print(f"Profiles: {total_profiles} total")
        for cat, count in by_category:
            cat_name = cat if cat else "Uncategorized"
            print(f"  ├─ {cat_name}: {count}")
        print()
        
        print("Quality:")
        total_quality = sum(q[1] for q in by_quality)
        for quality, count in by_quality:
            pct = (count / total_quality * 100) if total_quality > 0 else 0
            print(f"  ├─ {quality}: {count} ({pct:.0f}%)")
        print()
        
        print(f"Enrichment Queue: {pending_jobs} pending jobs")
        if by_priority:
            for priority, count in by_priority:
                priority_label = {
                    100: "morning-of",
                    75: "3-day",
                    25: "gmail"
                }.get(priority, f"priority-{priority}")
                print(f"  ├─ Priority {priority} ({priority_label}): {count}")
        print()
        
        print("Recent Activity:")
        print(f"  └─ {recent_profiles} profiles added in last 7 days")
        print()
        
    except Exception as e:
        print(f"✗ Error generating stats: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CRM V3 Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crm create --email john@example.com --name "John Doe"
  crm search --name "John"
  crm intel --email john@example.com
  crm list --category INVESTOR --limit 10
  crm stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to execute')
    
    # crm create
    create_parser = subparsers.add_parser('create', help='Create profile manually')
    create_parser.add_argument('--email', required=True, help='Contact email')
    create_parser.add_argument('--name', required=True, help='Full name')
    create_parser.add_argument('--category', default='NETWORKING', 
                               choices=['NETWORKING', 'INVESTOR', 'ADVISOR', 'COMMUNITY'],
                               help='Profile category')
    create_parser.add_argument('--notes', help='Optional notes')
    
    # crm search
    search_parser = subparsers.add_parser('search', help='Search profiles')
    search_parser.add_argument('--email', help='Search by email (exact match)')
    search_parser.add_argument('--name', help='Search by name (fuzzy match)')
    search_parser.add_argument('--company', help='Search by company domain')
    
    # crm intel
    intel_parser = subparsers.add_parser('intel', help='Get intelligence synthesis')
    intel_parser.add_argument('--email', help='Profile email')
    intel_parser.add_argument('--id', type=int, help='Profile ID')
    
    # crm enrich
    enrich_parser = subparsers.add_parser('enrich', help='Queue enrichment manually')
    enrich_parser.add_argument('--email', required=True, help='Profile email')
    enrich_parser.add_argument('--priority', type=int, default=100,
                               help='Priority (100=immediate, 75=3-day, 25=gmail)')
    
    # crm list
    list_parser = subparsers.add_parser('list', help='List profiles')
    list_parser.add_argument('--category', 
                             choices=['NETWORKING', 'INVESTOR', 'ADVISOR', 'COMMUNITY'],
                             help='Filter by category')
    list_parser.add_argument('--limit', type=int, default=20, help='Max profiles to show')
    
    # crm stats
    stats_parser = subparsers.add_parser('stats', help='Show CRM statistics')
    
    args = parser.parse_args()
    
    # Route to appropriate function
    if args.command == 'create':
        create_profile(args.email, args.name, args.category, args.notes)
    elif args.command == 'search':
        search_profiles(args.email, args.name, args.company)
    elif args.command == 'intel':
        get_intelligence_synthesis(args.email, args.id)
    elif args.command == 'enrich':
        queue_enrichment(args.email, args.priority)
    elif args.command == 'list':
        list_profiles(args.category, args.limit)
    elif args.command == 'stats':
        show_stats()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()







