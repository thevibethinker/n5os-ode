#!/usr/bin/env python3
"""
Migration script to transfer existing CRM markdown files to SQLite database.

This script:
1. Scans Knowledge/crm/individuals/*.md files
2. Extracts structured data from markdown
3. Populates SQLite database
4. Maintains links between DB records and markdown files
"""

import sqlite3
import re
from pathlib import Path
from datetime import datetime
import json

# Paths
WORKSPACE = Path('/home/workspace')
CRM_BASE = WORKSPACE / 'Knowledge' / 'crm'
CRM_INDIVIDUALS = CRM_BASE / 'individuals'
DB_PATH = CRM_BASE / 'crm.db'
SCHEMA_PATH = WORKSPACE / 'N5' / 'schemas' / 'crm_individuals.sql'


def create_database():
    """Initialize database with schema"""
    print(f"Creating database at {DB_PATH}")
    
    # Read schema
    schema_sql = SCHEMA_PATH.read_text()
    
    # Create database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Use executescript to handle multiple statements including triggers
    cursor.executescript(schema_sql)
    
    conn.commit()
    print(f"✓ Database initialized")
    return conn


def parse_markdown_file(filepath):
    """
    Extract structured data from individual markdown file.
    
    Expected format (flexible):
    ---
    name: Jane Smith
    title: CEO
    company: Acme Corp
    email: jane@acme.com
    linkedin: linkedin.com/in/janesmith
    category: customer
    status: active
    tags: saas, enterprise, warm
    ---
    
    # Notes
    Met at SaaStr 2023...
    """
    content = filepath.read_text()
    
    # Try to extract YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    
    data = {
        'full_name': filepath.stem.replace('-', ' ').title(),
        'markdown_file_path': str(filepath.relative_to(WORKSPACE)),
        'notes': ''
    }
    
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        
        # Parse simple key: value pairs
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['name', 'full_name']:
                    data['full_name'] = value
                elif key == 'preferred_name':
                    data['preferred_name'] = value
                elif key == 'title':
                    data['title'] = value
                elif key == 'company':
                    data['company'] = value
                elif key == 'email':
                    data['email'] = value
                elif key == 'phone':
                    data['phone'] = value
                elif key in ['linkedin', 'linkedin_url']:
                    data['linkedin_url'] = value
                elif key in ['twitter', 'twitter_handle']:
                    data['twitter_handle'] = value
                elif key in ['category', 'primary_category']:
                    data['primary_category'] = value
                elif key == 'status':
                    data['status'] = value
                elif key == 'tags':
                    data['tags'] = value
                elif key == 'source':
                    data['source_type'] = value
        
        # Rest is notes
        notes_start = frontmatter_match.end()
        data['notes'] = content[notes_start:].strip()[:500]  # First 500 chars
    else:
        # No frontmatter, treat whole file as notes
        data['notes'] = content[:500]
    
    return data


def migrate_individuals(conn):
    """Migrate all individual markdown files to database"""
    cursor = conn.cursor()
    
    if not CRM_INDIVIDUALS.exists():
        print(f"Directory {CRM_INDIVIDUALS} doesn't exist yet")
        return
    
    md_files = list(CRM_INDIVIDUALS.glob('*.md'))
    print(f"\nFound {len(md_files)} markdown files to migrate")
    
    migrated = 0
    for md_file in md_files:
        try:
            data = parse_markdown_file(md_file)
            
            # Insert individual
            cursor.execute("""
                INSERT INTO individuals (
                    full_name, preferred_name, title, company, 
                    email, phone, linkedin_url, twitter_handle,
                    primary_category, status, tags, source_type,
                    notes, markdown_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('full_name'),
                data.get('preferred_name'),
                data.get('title'),
                data.get('company'),
                data.get('email'),
                data.get('phone'),
                data.get('linkedin_url'),
                data.get('twitter_handle'),
                data.get('primary_category', 'other'),
                data.get('status', 'prospect'),
                data.get('tags'),
                data.get('source_type'),
                data.get('notes'),
                data.get('markdown_file_path')
            ))
            
            migrated += 1
            print(f"  ✓ Migrated: {data['full_name']}")
            
        except Exception as e:
            print(f"  ✗ Error migrating {md_file.name}: {e}")
    
    conn.commit()
    print(f"\n✓ Migrated {migrated}/{len(md_files)} individuals")


def generate_sample_data(conn):
    """Generate a few sample records for testing"""
    cursor = conn.cursor()
    
    samples = [
        {
            'full_name': 'Alex Caveny',
            'title': 'Advisor',
            'primary_category': 'advisor',
            'status': 'active',
            'tags': 'engineering, product, referral_source',
            'source_type': 'referral',
            'notes': 'Transitioned from advisor to potential talent referrer. Knows engineers/PMs.',
            'markdown_file_path': 'Knowledge/crm/individuals/alex-caveny.md'
        },
        {
            'full_name': 'Jane Smith',
            'title': 'VP Engineering',
            'company': 'TechCorp',
            'email': 'jane@techcorp.com',
            'linkedin_url': 'linkedin.com/in/janesmith',
            'primary_category': 'prospect',
            'status': 'active',
            'tags': 'enterprise, saas, warm',
            'source_type': 'conference',
            'notes': 'Met at SaaStr 2023. Interested in platform for Q1 hiring.',
            'markdown_file_path': 'Knowledge/crm/individuals/jane-smith.md'
        }
    ]
    
    for person in samples:
        try:
            cursor.execute("""
                INSERT INTO individuals (
                    full_name, title, company, email, linkedin_url,
                    primary_category, status, tags, source_type,
                    notes, markdown_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                person['full_name'],
                person.get('title'),
                person.get('company'),
                person.get('email'),
                person.get('linkedin_url'),
                person['primary_category'],
                person['status'],
                person.get('tags'),
                person.get('source_type'),
                person.get('notes'),
                person['markdown_file_path']
            ))
            print(f"  ✓ Created sample: {person['full_name']}")
        except sqlite3.IntegrityError:
            print(f"  - Sample already exists: {person['full_name']}")
    
    conn.commit()


def run_sample_queries(conn):
    """Run some example queries to demonstrate functionality"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("SAMPLE QUERIES")
    print("="*60)
    
    # Query 1: All active prospects
    print("\n1. Active prospects:")
    cursor.execute("""
        SELECT full_name, company, title, tags
        FROM individuals
        WHERE status = 'active' AND primary_category = 'prospect'
        ORDER BY updated_at DESC
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]} ({row[2]}) at {row[1]} | Tags: {row[3]}")
    
    # Query 2: Contacts by company
    print("\n2. Contacts grouped by company:")
    cursor.execute("""
        SELECT company, COUNT(*) as contact_count
        FROM individuals
        WHERE company IS NOT NULL
        GROUP BY company
        ORDER BY contact_count DESC
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]}: {row[1]} contact(s)")
    
    # Query 3: Stale contacts (no interaction in 90+ days)
    print("\n3. Stale contacts (90+ days since last contact):")
    cursor.execute("""
        SELECT full_name, company, days_since_contact
        FROM stale_contacts
        LIMIT 5
    """)
    for row in cursor.fetchall():
        days = row[2] if row[2] else 'Never'
        print(f"   - {row[0]} ({row[1]}): {days} days")
    
    # Query 4: Advisors and referral sources
    print("\n4. Advisors and referral sources:")
    cursor.execute("""
        SELECT full_name, primary_category, tags
        FROM individuals
        WHERE primary_category IN ('advisor', 'referral_source')
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]} ({row[1]}) | {row[2]}")


def main():
    """Main migration flow"""
    print("="*60)
    print("CRM MIGRATION: Markdown → SQLite")
    print("="*60)
    
    # Check if database already exists
    db_exists = DB_PATH.exists()
    
    if db_exists:
        response = input(f"\nDatabase already exists at {DB_PATH}. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return
        DB_PATH.unlink()
    
    # Create database and tables
    conn = create_database()
    
    # Option to migrate existing markdown or create samples
    print("\nMigration options:")
    print("1. Migrate existing markdown files from Knowledge/crm/individuals/")
    print("2. Create sample data for testing")
    print("3. Both (migrate existing + add samples)")
    print("4. Skip (just create empty database)")
    
    choice = input("\nYour choice (1-4): ").strip()
    
    if choice in ['1', '3']:
        migrate_individuals(conn)
    
    if choice in ['2', '3']:
        print("\nCreating sample data...")
        generate_sample_data(conn)
    
    # Run sample queries
    if choice != '4':
        run_sample_queries(conn)
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"✓ Migration complete!")
    print(f"Database: {DB_PATH}")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review the database with: sqlite3 Knowledge/crm/crm.db")
    print("  2. Run sample queries to test")
    print("  3. Update Python scripts to read/write to DB")
    print("  4. Decide: merge or transfer (keep both vs. migrate fully)")


if __name__ == '__main__':
    main()
