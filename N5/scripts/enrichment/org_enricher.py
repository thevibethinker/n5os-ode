#!/usr/bin/env python3
from N5.lib.paths import CRM_DB
"""
Organization Enricher
Unified org enrichment pipeline: Nyne (primary) + DB + Markdown sync.

Phase 4+5+6 of Nyne Integration build.

Usage:
    python3 org_enricher.py --domain nyne.ai
    python3 org_enricher.py --company-name "Acme Corp"
    python3 org_enricher.py --domain example.com --tier full --conversation-id con_xxx
    
Advanced Intel (Phase 5+6):
    python3 org_enricher.py --domain acme.com --sales-intel "CRM software"
    python3 org_enricher.py --domain acme.com --funding
    python3 org_enricher.py --domain acme.com --tech-check "stripe,react"
    python3 org_enricher.py --domain acme.com --needs "cost reduction"
    python3 org_enricher.py --domain acme.com --investors  # 20 credits!
    python3 org_enricher.py --domain acme.com --full-intel  # All except investors
    
Meeting Integration:
    python3 org_enricher.py --from-meeting /path/to/meeting/folder
"""

import sys
import json
import asyncio
import logging
import argparse
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')

from N5.scripts.enrichment.nyne_enricher import enrich_company_via_nyne

# Import NyneClient for advanced APIs
try:
    from Integrations.Nyne.nyne_client import NyneClient
    NYNE_CLIENT_AVAILABLE = True
except ImportError:
    NYNE_CLIENT_AVAILABLE = False

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CRM_DB = CRM_DB
ORG_PROFILES_DIR = Path('/home/workspace/Personal/Knowledge/CRM/organizations')
ORG_TEMPLATE = ORG_PROFILES_DIR / '_TEMPLATE.md'

# Ensure directories exist
ORG_PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def domain_to_slug(domain: str) -> str:
    """Convert domain to slug (e.g., nyne.ai -> nyne-ai)."""
    return domain.lower().replace('.', '-')


def get_db_connection() -> sqlite3.Connection:
    """Get SQLite connection with row factory."""
    conn = sqlite3.connect(CRM_DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_existing_org(
    conn: sqlite3.Connection,
    domain: Optional[str] = None,
    slug: Optional[str] = None,
    linkedin_url: Optional[str] = None
) -> Optional[Dict]:
    """Check if org already exists in DB."""
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if domain:
        conditions.append("domain = ?")
        params.append(domain)
    if slug:
        conditions.append("slug = ?")
        params.append(slug)
    if linkedin_url:
        conditions.append("linkedin_url = ?")
        params.append(linkedin_url)
    
    if not conditions:
        return None
    
    query = f"SELECT * FROM organizations WHERE {' OR '.join(conditions)}"
    cursor.execute(query, params)
    row = cursor.fetchone()
    
    return dict(row) if row else None


def upsert_org(conn: sqlite3.Connection, org_data: Dict) -> int:
    """Insert or update organization in DB."""
    cursor = conn.cursor()
    
    # Required fields
    slug = org_data['slug']
    name = org_data.get('name', slug)
    
    cursor.execute("""
        INSERT INTO organizations (
            name, slug, domain, source, enrichment_status,
            last_enriched_at, linkedin_url, description,
            industry, founded_year, headcount_range, location
        ) VALUES (?, ?, ?, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            domain = COALESCE(excluded.domain, organizations.domain),
            enrichment_status = excluded.enrichment_status,
            last_enriched_at = datetime('now'),
            linkedin_url = COALESCE(excluded.linkedin_url, organizations.linkedin_url),
            description = COALESCE(excluded.description, organizations.description),
            industry = COALESCE(excluded.industry, organizations.industry),
            founded_year = COALESCE(excluded.founded_year, organizations.founded_year),
            headcount_range = COALESCE(excluded.headcount_range, organizations.headcount_range),
            location = COALESCE(excluded.location, organizations.location),
            updated_at = datetime('now')
    """, (
        name,
        slug,
        org_data.get('domain'),
        org_data.get('source', 'nyne_enrichment'),
        org_data.get('enrichment_status', 'enriched'),
        org_data.get('linkedin_url'),
        org_data.get('description'),
        org_data.get('industry'),
        org_data.get('founded_year'),
        org_data.get('headcount_range'),
        org_data.get('location')
    ))
    
    conn.commit()
    
    # Get the inserted/updated ID
    cursor.execute("SELECT id FROM organizations WHERE slug = ?", (slug,))
    return cursor.fetchone()[0]


def link_profiles_to_org(conn: sqlite3.Connection, org_id: int, domain: str):
    """Link individual profiles to org based on email domain."""
    if not domain:
        return 0
    
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profiles 
        SET organization_id = ?
        WHERE email LIKE ?
        AND (organization_id IS NULL OR organization_id != ?)
    """, (org_id, f'%@{domain}', org_id))
    
    conn.commit()
    return cursor.rowcount


def get_linked_people(conn: sqlite3.Connection, org_id: int) -> list:
    """Get people linked to this org."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, name, role, slug 
        FROM profiles 
        WHERE organization_id = ?
        ORDER BY name
    """, (org_id,))
    return [dict(row) for row in cursor.fetchall()]


def get_sales_intel(domain: str, product_or_service: str) -> Optional[Dict]:
    """
    Check if company sells a specific product/service using Nyne CheckSeller API.
    
    Args:
        domain: Company domain
        product_or_service: What to check for
    
    Returns:
        Dict with 'sells', 'confidence', 'evidence' or None
    
    Credits: Cost TBD (check API docs)
    """
    if not NYNE_CLIENT_AVAILABLE:
        logger.warning("NyneClient not available for sales intel")
        return None
    
    try:
        client = NyneClient()
        result = client.check_company_sells(domain, product_or_service)
        return result
    except Exception as e:
        logger.error(f"Sales intel lookup failed: {e}")
        return None


def get_tech_stack(domain: str, technologies: List[str]) -> Dict[str, Any]:
    """
    Check what technologies a company uses via Nyne Feature Checker API.
    
    Args:
        domain: Company domain
        technologies: List of technologies to check (e.g., ["stripe", "react"])
    
    Returns:
        Dict mapping technology -> detection result
    
    Credits: Cost TBD per technology checked
    """
    if not NYNE_CLIENT_AVAILABLE:
        logger.warning("NyneClient not available for tech stack check")
        return {}
    
    results = {}
    try:
        client = NyneClient()
        for tech in technologies:
            tech = tech.strip().lower()
            try:
                result = client.check_company_feature(domain, tech)
                results[tech] = result
            except Exception as e:
                logger.warning(f"Tech check for {tech} failed: {e}")
                results[tech] = {'error': str(e)}
    except Exception as e:
        logger.error(f"Tech stack lookup failed: {e}")
    
    return results


def get_funding_intel(domain: str) -> Optional[Dict]:
    """
    Get company funding history via Nyne Funding API.
    
    Args:
        domain: Company domain
    
    Returns:
        Dict with funding rounds, investors, valuations or None
    
    Credits: Cost TBD
    """
    if not NYNE_CLIENT_AVAILABLE:
        logger.warning("NyneClient not available for funding intel")
        return None
    
    try:
        client = NyneClient()
        result = client.get_company_funding(domain)
        return result
    except Exception as e:
        logger.error(f"Funding lookup failed: {e}")
        return None


def get_company_needs_intel(company_name: str, topic: str, filing: Optional[str] = None) -> Optional[Dict]:
    """
    Get company pain points from SEC filings via Nyne Company Needs API.
    
    Args:
        company_name: Official company name (for SEC lookup)
        topic: Topic to surface (e.g., "Regulatory challenges")
        filing: Optional filing type filter (e.g., "Form 10-K")
    
    Returns:
        Dict with 'company' and 'needs' array or None
    
    Credits: 3 credits per completed analysis
    """
    if not NYNE_CLIENT_AVAILABLE:
        logger.warning("NyneClient not available for company needs")
        return None
    
    try:
        client = NyneClient()
        result = client.get_company_needs(company_name, topic, filing)
        return result
    except Exception as e:
        logger.error(f"Company needs lookup failed: {e}")
        return None


def get_investors_intel(domain: str) -> Optional[Dict]:
    """
    Get detailed investor profiles for a company via Nyne Investor API.
    
    ⚠️ WARNING: This is EXPENSIVE - 20 credits per call!
    Use sparingly, only for high-value targets.
    
    Args:
        domain: Company domain
    
    Returns:
        Dict with detailed investor profiles or None
    
    Credits: 20 credits per call
    """
    if not NYNE_CLIENT_AVAILABLE:
        logger.warning("NyneClient not available for investor intel")
        return None
    
    try:
        client = NyneClient()
        result = client.get_investor_info(domain)
        return result
    except Exception as e:
        logger.error(f"Investor lookup failed: {e}")
        return None


# Personal email domains to exclude when extracting orgs from meetings
PERSONAL_EMAIL_DOMAINS = {
    'gmail.com', 'googlemail.com', 'outlook.com', 'hotmail.com', 
    'yahoo.com', 'yahoo.co.uk', 'icloud.com', 'me.com', 'mac.com',
    'protonmail.com', 'proton.me', 'aol.com', 'live.com', 'msn.com',
    'zoho.com', 'fastmail.com', 'tutanota.com', 'hey.com', 'pm.me'
}


def extract_orgs_from_meeting(meeting_path: str) -> List[Dict]:
    """
    Extract mentioned companies from a meeting manifest.json.
    
    Looks at:
    - attendees[].email domains (exclude personal email domains)
    - attendee_domains from manifest
    - company_mentions if present in manifest
    
    Returns list of {domain, company_name, source} for stub creation.
    """
    meeting_dir = Path(meeting_path)
    manifest_path = meeting_dir / 'manifest.json'
    
    if not manifest_path.exists():
        logger.error(f"No manifest.json found in {meeting_path}")
        return []
    
    orgs_found = []
    seen_domains = set()
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read manifest: {e}")
        return []
    
    # Extract from attendees (if present)
    for attendee in manifest.get('attendees', []):
        email = attendee.get('email', '')
        if '@' in email:
            domain = email.split('@')[1].lower()
            if domain not in PERSONAL_EMAIL_DOMAINS and domain not in seen_domains:
                seen_domains.add(domain)
                orgs_found.append({
                    'domain': domain,
                    'company_name': attendee.get('company', domain.split('.')[0].title()),
                    'source': 'attendee_email'
                })
    
    # Extract from attendee_domains (if present)
    for domain in manifest.get('attendee_domains', []):
        domain = domain.lower()
        if domain not in PERSONAL_EMAIL_DOMAINS and domain not in seen_domains:
            seen_domains.add(domain)
            orgs_found.append({
                'domain': domain,
                'company_name': domain.split('.')[0].title(),
                'source': 'manifest_domains'
            })
    
    # Try to extract from meeting title/folder name
    folder_name = meeting_dir.name
    # Pattern: 2025-01-01_Company-Name-Meeting
    if '_' in folder_name:
        parts = folder_name.split('_', 1)[1] if '_' in folder_name else ''
        # Could potentially extract company hints here
    
    # Scan B06 (Business Context) if it exists
    b06_files = list(meeting_dir.glob('B06*.md'))
    for b06_file in b06_files:
        try:
            content = b06_file.read_text()
            # Look for common company reference patterns
            # This is basic - could be enhanced with NLP
            import re
            # Look for **Company:** patterns or ## Company Context headers
            company_patterns = re.findall(r'\*\*([A-Z][a-zA-Z0-9\s]+)\s*Context\*\*|\*\*([A-Z][a-zA-Z0-9\s]+)\s*:\*\*', content)
            for match in company_patterns:
                company = match[0] or match[1]
                if company and company.lower() not in ['market', 'business', 'general', 'meeting']:
                    # We found a company name but no domain - just log it
                    logger.info(f"B06 mentions company: {company} (no domain)")
        except Exception as e:
            logger.warning(f"Failed to parse B06: {e}")
    
    return orgs_found


async def process_meeting_orgs(meeting_path: str, create_stubs: bool = True) -> Dict:
    """
    Extract and optionally create org stubs from a meeting.
    
    Args:
        meeting_path: Path to meeting folder
        create_stubs: If True, create stub profiles for new orgs
    
    Returns:
        Summary dict with orgs found and created
    """
    orgs = extract_orgs_from_meeting(meeting_path)
    
    if not orgs:
        return {
            'success': True,
            'meeting': meeting_path,
            'orgs_found': 0,
            'orgs_created': 0,
            'orgs': []
        }
    
    results = []
    created_count = 0
    
    conn = get_db_connection()
    try:
        for org in orgs:
            existing = get_existing_org(conn, domain=org['domain'])
            
            if existing:
                results.append({
                    **org,
                    'status': 'exists',
                    'org_id': existing['id']
                })
            elif create_stubs:
                # Create stub via enrich_organization
                result = await enrich_organization(
                    domain=org['domain'],
                    company_name=org['company_name'],
                    tier='stub'
                )
                if result['success']:
                    created_count += 1
                    results.append({
                        **org,
                        'status': 'created',
                        'org_id': result.get('org_id')
                    })
                else:
                    results.append({
                        **org,
                        'status': 'failed',
                        'error': result.get('error')
                    })
            else:
                results.append({
                    **org,
                    'status': 'skipped'
                })
    finally:
        conn.close()
    
    return {
        'success': True,
        'meeting': meeting_path,
        'orgs_found': len(orgs),
        'orgs_created': created_count,
        'orgs': results
    }


def generate_org_markdown(
    org_data: Dict,
    nyne_data: Optional[Dict],
    linked_people: list,
    conversation_id: Optional[str] = None,
    tier: str = 'light',
    sales_intel: Optional[Dict] = None,
    tech_stack: Optional[Dict] = None,
    funding_intel: Optional[Dict] = None,
    needs_intel: Optional[Dict] = None
) -> str:
    """Generate markdown profile for organization."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Extract fields
    name = org_data.get('name', 'Unknown Organization')
    domain = org_data.get('domain', '')
    slug = org_data.get('slug', '')
    
    # From Nyne data
    industry = ''
    founded = ''
    size = ''
    location = ''
    description = ''
    linkedin_url = ''
    
    if nyne_data:
        industry = nyne_data.get('industry', '')
        founded = nyne_data.get('founded', '') or nyne_data.get('founding_year', '')
        size = nyne_data.get('headcount', '') or nyne_data.get('employee_count', '')
        location = nyne_data.get('location', '') or nyne_data.get('headquarters', '')
        description = nyne_data.get('description', '')
        linkedin_url = nyne_data.get('linkedin_url', '')
    
    # Build key people section
    people_section = ""
    if linked_people:
        for person in linked_people[:10]:  # Cap at 10
            p_name = person.get('name', person.get('email', 'Unknown'))
            p_role = person.get('role', '')
            p_slug = person.get('slug', '')
            if p_slug:
                people_section += f"- [[{p_slug}]]"
            else:
                people_section += f"- {p_name}"
            if p_role:
                people_section += f" — {p_role}"
            people_section += "\n"
    else:
        people_section = "<!-- No linked individuals yet -->\n"
    
    # Build markdown
    md = f"""---
created: {today}
last_edited: {today}
version: 1.0
provenance: {conversation_id or 'manual'}
slug: {slug}
domain: {domain}
aliases: []
enrichment_sources: [nyne]
last_enriched: {today}
enrichment_tier: {tier}
---

# {name}

## Overview

**Industry:** {industry or '[To be enriched]'}  
**Founded:** {founded or '[Unknown]'}  
**Size:** {size or '[Unknown]'}  
**HQ:** {location or '[Unknown]'}  

{description or '[No description available]'}

---

## Funding & Financials

"""
    
    # Add funding if full tier and data available
    if tier == 'full' and nyne_data and nyne_data.get('funding'):
        funding = nyne_data['funding']
        md += f"""- **Total Raised:** {funding.get('total_raised', 'Unknown')}
- **Last Round:** {funding.get('last_round', 'Unknown')}
- **Investors:** {', '.join(funding.get('investors', [])) or 'Unknown'}
"""
    else:
        md += "[Available with full enrichment tier]\n"
    
    md += """
---

## Tech Stack

"""
    if tech_stack:
        md += "**Detected Technologies:**\n"
        for tech, result in tech_stack.items():
            if result.get('error'):
                md += f"- {tech} — ⚠️ Check failed\n"
            elif result.get('uses') or result.get('detected'):
                evidence = result.get('evidence', 'detected')[:100]
                md += f"- {tech} — ✅ {evidence}\n"
            else:
                md += f"- {tech} — ❌ Not detected\n"
    else:
        md += "[Available with --tech-check flag]\n"
    
    md += """
---

## Pain Points & Needs

"""
    if needs_intel and needs_intel.get('needs'):
        md += "| Filing | Date | Key Challenge | Source |\n"
        md += "|--------|------|---------------|--------|\n"
        for need in needs_intel['needs'][:5]:
            filing = need.get('filing', 'Unknown')
            date = need.get('filing_date', 'Unknown')
            content = need.get('content', '')[:80] + '...' if len(need.get('content', '')) > 80 else need.get('content', '')
            source = need.get('source_url', '#')
            md += f"| {filing} | {date} | {content} | [SEC]({source}) |\n"
    else:
        md += "[Available with --needs flag for public companies]\n"
    
    md += f"""
---

## Key People (Linked)

{people_section}
---

## Related Meetings

<!-- Auto-populated from meeting manifests -->

---

## Intelligence Notes

<!-- Accumulated insights from meetings, research, interactions -->

---

## Enrichment Log

| Date | Source | Tier | Notes |
|------|--------|------|-------|
| {today} | nyne | {tier} | {'Initial enrichment' if tier != 'stub' else 'Stub created'} |

---

## Quick Reference

**Website:** {f'https://{domain}' if domain else '[Unknown]'}  
**LinkedIn:** {linkedin_url or '[Unknown]'}  
**Aviato ID:** [Not enriched]  
**Nyne ID:** [From enrichment]

---

*Generated by org_enricher.py | Nyne Integration Phase 4*
"""
    
    return md


def save_org_markdown(slug: str, markdown: str) -> Path:
    """Save org markdown profile."""
    filepath = ORG_PROFILES_DIR / f"{slug}.md"
    filepath.write_text(markdown)
    logger.info(f"Saved org profile: {filepath}")
    return filepath


async def enrich_organization(
    domain: Optional[str] = None,
    company_name: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    tier: str = 'light',
    conversation_id: Optional[str] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Main enrichment function.
    
    Args:
        domain: Company domain (e.g., nyne.ai)
        company_name: Company name
        linkedin_url: LinkedIn company page URL
        tier: Enrichment tier (stub, light, full)
        conversation_id: For provenance tracking
        force: Re-enrich even if recently enriched
    
    Returns:
        Dict with results
    """
    # Validate input
    if not any([domain, company_name, linkedin_url]):
        return {
            'success': False,
            'error': 'At least one of domain, company_name, or linkedin_url required'
        }
    
    # Generate slug
    if domain:
        slug = domain_to_slug(domain)
    elif company_name:
        slug = slugify(company_name)
    else:
        # Extract from LinkedIn URL
        slug = slugify(linkedin_url.split('/')[-1])
    
    conn = get_db_connection()
    
    try:
        # Check existing
        existing = get_existing_org(conn, domain=domain, slug=slug, linkedin_url=linkedin_url)
        
        if existing and not force:
            # Check if recently enriched (within 30 days)
            if existing.get('enrichment_status') == 'enriched' and existing.get('last_enriched_at'):
                last_enriched = datetime.fromisoformat(existing['last_enriched_at'].replace('Z', '+00:00'))
                days_since = (datetime.now(last_enriched.tzinfo) - last_enriched).days
                if days_since < 30:
                    logger.info(f"Org {slug} recently enriched ({days_since} days ago), skipping")
                    return {
                        'success': True,
                        'cached': True,
                        'slug': slug,
                        'org_id': existing['id'],
                        'message': f'Org recently enriched ({days_since} days ago). Use --force to re-enrich.'
                    }
        
        # Enrichment based on tier
        nyne_data = None
        enrichment_status = 'stub'
        
        if tier in ('light', 'full'):
            logger.info(f"Calling Nyne company enrichment for {domain or company_name or linkedin_url}")
            result = await enrich_company_via_nyne(
                domain=domain,
                company_name=company_name,
                linkedin_url=linkedin_url
            )
            
            if result['success'] and result['data']:
                nyne_data = result['data']
                enrichment_status = 'enriched'
                logger.info(f"Nyne returned data for {slug}")
            else:
                logger.warning(f"Nyne returned no data: {result.get('error', 'not found')}")
                enrichment_status = 'failed' if result.get('error') else 'not_found'
        
        # Build org record
        org_record = {
            'slug': slug,
            'name': nyne_data.get('name', company_name or domain or slug) if nyne_data else (company_name or domain or slug),
            'domain': domain or (nyne_data.get('domain') if nyne_data else None),
            'source': 'nyne_enrichment',
            'enrichment_status': enrichment_status,
            'linkedin_url': linkedin_url or (nyne_data.get('linkedin_url') if nyne_data else None),
            'description': nyne_data.get('description') if nyne_data else None,
            'industry': nyne_data.get('industry') if nyne_data else None,
            'founded_year': nyne_data.get('founded') if nyne_data else None,
            'headcount_range': nyne_data.get('headcount') if nyne_data else None,
            'location': nyne_data.get('location') if nyne_data else None
        }
        
        # Upsert to DB
        org_id = upsert_org(conn, org_record)
        logger.info(f"Upserted org {slug} with id={org_id}")
        
        # Link profiles
        linked_count = 0
        if domain:
            linked_count = link_profiles_to_org(conn, org_id, domain)
            if linked_count:
                logger.info(f"Linked {linked_count} profiles to org {slug}")
        
        # Get linked people for markdown
        linked_people = get_linked_people(conn, org_id)
        
        # Generate and save markdown
        markdown = generate_org_markdown(
            org_record,
            nyne_data,
            linked_people,
            conversation_id,
            tier
        )
        filepath = save_org_markdown(slug, markdown)
        
        return {
            'success': True,
            'cached': False,
            'slug': slug,
            'org_id': org_id,
            'enrichment_status': enrichment_status,
            'tier': tier,
            'linked_profiles': linked_count,
            'filepath': str(filepath),
            'credits_used': 6 if tier in ('light', 'full') and enrichment_status == 'enriched' else 0
        }
    
    finally:
        conn.close()


async def main():
    parser = argparse.ArgumentParser(
        description='Enrich organization profile',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Advanced Intel Flags (Phase 6):
  --sales-intel PRODUCT   Check if company sells PRODUCT (CheckSeller API)
  --funding               Fetch funding history and rounds
  --needs TOPIC           Fetch pain points from SEC filings (3 credits)
  --investors             Fetch detailed investor profiles (⚠️ 20 credits!)
  --full-intel            Run all intel (sales + funding + needs, NOT investors)
  --tech-check TECHS      Check tech stack (comma-separated: "stripe,react")

Meeting Integration:
  --from-meeting PATH     Extract org domains from meeting manifest

Credit Costs:
  - Standard enrichment: 1-2 credits
  - --sales-intel: ~1 credit
  - --funding: ~1 credit
  - --needs: 3 credits
  - --investors: 20 credits (use sparingly!)
  - --full-intel: ~5 credits total
        """
    )
    parser.add_argument('--domain', '-d', help='Company domain (e.g., nyne.ai)')
    parser.add_argument('--company-name', '-n', help='Company name')
    parser.add_argument('--linkedin-url', '-l', help='LinkedIn company page URL')
    parser.add_argument('--tier', '-t', choices=['stub', 'light', 'full'], default='light',
                        help='Enrichment tier (default: light)')
    parser.add_argument('--conversation-id', '-c', help='Conversation ID for provenance')
    parser.add_argument('--force', '-f', action='store_true', help='Force re-enrichment')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Phase 6: Advanced Intel Flags
    parser.add_argument('--sales-intel', metavar='PRODUCT', 
                        help='Check if company sells PRODUCT/SERVICE')
    parser.add_argument('--funding', action='store_true',
                        help='Fetch funding history and rounds')
    parser.add_argument('--needs', metavar='TOPIC',
                        help='Fetch pain points from SEC filings (3 credits)')
    parser.add_argument('--investors', action='store_true',
                        help='Fetch detailed investor profiles (⚠️ 20 credits!)')
    parser.add_argument('--full-intel', action='store_true',
                        help='Run all intel endpoints (NOT investors)')
    parser.add_argument('--tech-check', metavar='TECHS',
                        help='Check tech stack (comma-separated)')
    
    # Phase 6: Meeting Integration
    parser.add_argument('--from-meeting', metavar='PATH',
                        help='Extract org domains from meeting folder')
    
    args = parser.parse_args()
    
    # Handle --from-meeting mode
    if args.from_meeting:
        result = await process_meeting_orgs(args.from_meeting)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"📁 Meeting: {result['meeting']}")
            print(f"   Orgs found: {result['orgs_found']}")
            print(f"   Orgs created: {result['orgs_created']}")
            for org in result['orgs']:
                status_icon = '✅' if org['status'] == 'created' else '📋' if org['status'] == 'exists' else '⏭️'
                print(f"   {status_icon} {org['domain']} ({org['source']}) - {org['status']}")
        return
    
    # Standard enrichment mode requires identifier
    if not any([args.domain, args.company_name, args.linkedin_url]):
        parser.error('At least one of --domain, --company-name, or --linkedin-url required (or use --from-meeting)')
    
    # Warn about expensive --investors call
    if args.investors:
        print("⚠️  WARNING: --investors costs 20 credits per call!")
        print("   Proceeding in 2 seconds... (Ctrl+C to cancel)")
        import time
        time.sleep(2)
    
    # Run standard enrichment first
    result = await enrich_organization(
        domain=args.domain,
        company_name=args.company_name,
        linkedin_url=args.linkedin_url,
        tier=args.tier,
        conversation_id=args.conversation_id,
        force=args.force
    )
    
    # Track additional intel results
    intel_results = {}
    
    domain = args.domain or result.get('domain')
    company_name = args.company_name or result.get('company_name')
    
    if domain:
        # Handle --full-intel (all except investors)
        if args.full_intel:
            args.sales_intel = args.sales_intel or "products"  # Generic check
            args.funding = True
            args.needs = args.needs or "challenges"  # Generic topic
        
        # Sales intel
        if args.sales_intel:
            print(f"🔍 Checking sales intel for: {args.sales_intel}")
            intel_results['sales_intel'] = get_sales_intel(domain, args.sales_intel)
        
        # Tech stack
        if args.tech_check:
            techs = [t.strip() for t in args.tech_check.split(',')]
            print(f"🔧 Checking tech stack: {', '.join(techs)}")
            intel_results['tech_stack'] = get_tech_stack(domain, techs)
        
        # Funding
        if args.funding:
            print("💰 Fetching funding intel...")
            intel_results['funding'] = get_funding_intel(domain)
        
        # Company needs (requires company name)
        if args.needs and company_name:
            print(f"📊 Fetching company needs: {args.needs}")
            intel_results['needs'] = get_company_needs_intel(company_name, args.needs)
        
        # Investors (expensive!)
        if args.investors:
            print("👥 Fetching investor profiles (20 credits)...")
            intel_results['investors'] = get_investors_intel(domain)
    
    # Add intel results to main result
    result['intel'] = intel_results
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            print(f"✅ Organization enriched: {result['slug']}")
            print(f"   Status: {result.get('enrichment_status', 'unknown')}")
            print(f"   Tier: {result.get('tier', 'unknown')}")
            print(f"   Linked profiles: {result.get('linked_profiles', 0)}")
            print(f"   Credits used: {result.get('credits_used', 0)}")
            print(f"   Profile: {result.get('filepath', 'N/A')}")
            if result.get('cached'):
                print(f"   (Using cached data)")
            
            # Print intel results summary
            if intel_results:
                print("\n📊 Advanced Intel:")
                if 'sales_intel' in intel_results and intel_results['sales_intel']:
                    si = intel_results['sales_intel']
                    print(f"   Sales: {si.get('sells', 'unknown')} (confidence: {si.get('confidence', 'N/A')})")
                if 'tech_stack' in intel_results and intel_results['tech_stack']:
                    techs = intel_results['tech_stack']
                    for tech, data in techs.items():
                        status = '✓' if data.get('detected') else '✗' if 'detected' in data else '?'
                        print(f"   Tech [{status}]: {tech}")
                if 'funding' in intel_results and intel_results['funding']:
                    funding = intel_results['funding']
                    print(f"   Funding: {funding.get('total_raised', 'Unknown')} raised")
                if 'needs' in intel_results and intel_results['needs']:
                    needs = intel_results['needs']
                    print(f"   Needs: {len(needs.get('needs', []))} pain points identified")
                if 'investors' in intel_results and intel_results['investors']:
                    inv = intel_results['investors']
                    print(f"   Investors: {len(inv.get('investors', []))} profiles")
        else:
            print(f"❌ Enrichment failed: {result.get('error', 'unknown')}")
            sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())



