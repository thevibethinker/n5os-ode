#!/usr/bin/env python3
"""
Employer Aviato Enricher
Enriches Airtable Employer records using Aviato company/enrich API.

Trigger: When Website field is populated and Aviato Enriched is not checked.

Usage:
    python3 employer_aviato_enricher.py                    # Enrich all un-enriched employers with websites
    python3 employer_aviato_enricher.py --record-id recXXX # Enrich a specific record
    python3 employer_aviato_enricher.py --dry-run           # Preview what would be enriched
    python3 employer_aviato_enricher.py --json              # Output as JSON
"""

import sys
import os
import json
import argparse
import logging
import requests
from typing import Dict, Optional, List
from urllib.parse import urlparse

sys.path.insert(0, '/home/workspace')
from Integrations.Aviato.aviato_client import AviatoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Airtable config
AIRTABLE_BASE_ID = 'appd12asvg42woz9I'
EMPLOYERS_TABLE_ID = 'tblvIfVUHxzuBQ2WB'

# Industry mapping: Aviato industryList values -> Airtable single select choices
INDUSTRY_MAP = {
    'technology': 'Technology',
    'software': 'Technology',
    'information technology': 'Technology',
    'internet': 'Technology',
    'artificial intelligence': 'Technology',
    'saas': 'Technology',
    'fintech': 'Technology',
    'healthcare': 'Healthcare',
    'health': 'Healthcare',
    'biotech': 'Healthcare',
    'medical': 'Healthcare',
    'pharmaceuticals': 'Healthcare',
    'finance': 'Finance',
    'financial services': 'Finance',
    'banking': 'Finance',
    'investment': 'Finance',
    'insurance': 'Finance',
    'education': 'Education',
    'edtech': 'Education',
    'retail': 'Retail',
    'e-commerce': 'Retail',
    'ecommerce': 'Retail',
    'manufacturing': 'Manufacturing',
    'hardware': 'Manufacturing',
    'nonprofit': 'Nonprofit',
    'non-profit': 'Nonprofit',
}

VALID_INDUSTRIES = {'Technology', 'Healthcare', 'Finance', 'Education', 'Retail', 'Manufacturing', 'Nonprofit', 'Other'}


def extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    if not url:
        return ''
    if not url.startswith('http'):
        url = 'https://' + url
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    domain = domain.replace('www.', '')
    # Strip trailing paths (e.g., kloudgin.com/careers/ -> kloudgin.com)
    if '/' in domain:
        domain = domain.split('/')[0]
    return domain


def map_industry(aviato_industries: list) -> Optional[str]:
    """Map Aviato industryList to Airtable single select value."""
    if not aviato_industries:
        return None
    for ind in aviato_industries:
        ind_lower = ind.lower().strip()
        if ind_lower in INDUSTRY_MAP:
            return INDUSTRY_MAP[ind_lower]
    # Default to Other if we have industries but none map
    return 'Other'


def get_airtable_headers() -> dict:
    """Get Airtable API headers."""
    token = os.environ.get('AIRTABLE_TOKEN')
    if not token:
        raise ValueError("AIRTABLE_TOKEN not found in environment")
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


def get_unenriched_employers(record_id: Optional[str] = None) -> List[Dict]:
    """Fetch employer records that have Website but no Aviato Enriched flag."""
    headers = get_airtable_headers()

    if record_id:
        resp = requests.get(
            f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{EMPLOYERS_TABLE_ID}/{record_id}',
            headers=headers
        )
        resp.raise_for_status()
        record = resp.json()
        return [record]

    # Use filterByFormula to find records with Website but not enriched
    formula = "AND({Website} != '', NOT({Aviato Enriched}))"
    all_records = []
    offset = None

    while True:
        params = {
            'filterByFormula': formula,
            'fields[]': ['Employer Name', 'Website', 'Aviato Enriched', 'Industry',
                         'Headcount', 'LinkedIn URL', 'Company Description',
                         'Funding Status', 'Total Funding', 'Tech Stack', 'Location']
        }
        if offset:
            params['offset'] = offset

        resp = requests.get(
            f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{EMPLOYERS_TABLE_ID}',
            headers=headers,
            params=params
        )
        resp.raise_for_status()
        data = resp.json()
        all_records.extend(data.get('records', []))
        offset = data.get('offset')
        if not offset:
            break

    return all_records


def enrich_employer(record: Dict, dry_run: bool = False) -> Dict:
    """Enrich a single employer record via Aviato."""
    fields = record.get('fields', {})
    record_id = record['id']
    name = fields.get('Employer Name', 'Unknown')
    website = fields.get('Website', '')
    domain = extract_domain(website)

    if not domain:
        return {'record_id': record_id, 'name': name, 'status': 'skipped', 'reason': 'no domain extractable'}

    if dry_run:
        return {'record_id': record_id, 'name': name, 'domain': domain, 'status': 'dry_run', 'would_enrich': True}

    logger.info(f"Enriching {name} via Aviato (domain: {domain})")

    try:
        client = AviatoClient()
        aviato_data = client.enrich_company(website=domain)
    except Exception as e:
        logger.error(f"Aviato API error for {name}: {e}")
        return {'record_id': record_id, 'name': name, 'status': 'error', 'error': str(e)}

    if not aviato_data:
        logger.warning(f"No Aviato data found for {name} ({domain})")
        # Still mark as enriched (attempted) to avoid re-querying
        update_fields = {'Aviato Enriched': True}
        _update_airtable_record(record_id, update_fields)
        return {'record_id': record_id, 'name': name, 'status': 'not_found', 'domain': domain}

    # Map Aviato data to Airtable fields
    update_fields = {'Aviato Enriched': True}

    # Company Description — only if not already populated
    desc = aviato_data.get('description')
    if desc and not fields.get('Company Description'):
        update_fields['Company Description'] = desc

    # Headcount
    headcount = aviato_data.get('computed_headcount') or aviato_data.get('headcount')
    if headcount and not fields.get('Headcount'):
        try:
            update_fields['Headcount'] = int(headcount)
        except (ValueError, TypeError):
            pass

    # Industry
    industry_list = aviato_data.get('industryList', [])
    mapped_industry = map_industry(industry_list)
    if mapped_industry and not fields.get('Industry'):
        update_fields['Industry'] = mapped_industry

    # Location
    location_parts = []
    if aviato_data.get('locality'):
        location_parts.append(aviato_data['locality'])
    if aviato_data.get('region'):
        location_parts.append(aviato_data['region'])
    if aviato_data.get('country'):
        location_parts.append(aviato_data['country'])
    location_str = ', '.join(location_parts)
    if location_str and not fields.get('Location'):
        update_fields['Location'] = location_str

    # LinkedIn URL
    linkedin_id = aviato_data.get('linkedinID')
    if linkedin_id and not fields.get('LinkedIn URL'):
        update_fields['LinkedIn URL'] = f'https://linkedin.com/company/{linkedin_id}'

    # Funding
    financing_status = aviato_data.get('financingStatus')
    if financing_status and not fields.get('Funding Status'):
        update_fields['Funding Status'] = financing_status

    total_funding = aviato_data.get('totalFunding')
    if total_funding and not fields.get('Total Funding'):
        try:
            update_fields['Total Funding'] = float(total_funding)
        except (ValueError, TypeError):
            pass

    # Tech Stack
    tech_stack = aviato_data.get('techStackList', [])
    if tech_stack and not fields.get('Tech Stack'):
        tech_names = []
        for t in tech_stack[:20]:
            if isinstance(t, dict):
                tech_names.append(t.get('name', t.get('value', str(t))))
            else:
                tech_names.append(str(t))
        update_fields['Tech Stack'] = ', '.join(tech_names)

    # Write to Airtable
    _update_airtable_record(record_id, update_fields)

    enriched_fields = [k for k in update_fields if k != 'Aviato Enriched']
    logger.info(f"Enriched {name}: {len(enriched_fields)} fields updated")

    return {
        'record_id': record_id,
        'name': name,
        'domain': domain,
        'status': 'enriched',
        'fields_updated': enriched_fields,
        'aviato_name': aviato_data.get('name', ''),
        'aviato_headcount': headcount,
    }


def _update_airtable_record(record_id: str, fields: Dict):
    """Update an Airtable record via REST API."""
    headers = get_airtable_headers()
    resp = requests.patch(
        f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{EMPLOYERS_TABLE_ID}/{record_id}',
        headers=headers,
        json={'fields': fields}
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description='Enrich Airtable Employer records via Aviato')
    parser.add_argument('--record-id', '-r', help='Enrich a specific Airtable record ID')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Preview without making changes')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    records = get_unenriched_employers(record_id=args.record_id)

    if not records:
        msg = "No un-enriched employers with websites found."
        if args.json:
            print(json.dumps({'status': 'no_records', 'message': msg}))
        else:
            print(msg)
        return

    results = []
    for record in records:
        result = enrich_employer(record, dry_run=args.dry_run)
        results.append(result)

    if args.json:
        print(json.dumps({'status': 'complete', 'results': results, 'total': len(results)}, indent=2))
    else:
        print(f"\n{'DRY RUN — ' if args.dry_run else ''}Enrichment Results:")
        print(f"{'='*60}")
        for r in results:
            status_icon = {'enriched': '✅', 'not_found': '⚠️', 'error': '❌', 'skipped': '⏭️', 'dry_run': '👁️'}.get(r['status'], '❓')
            print(f"{status_icon} {r['name']} ({r.get('domain', 'N/A')}) — {r['status']}")
            if r.get('fields_updated'):
                print(f"   Updated: {', '.join(r['fields_updated'])}")
            if r.get('error'):
                print(f"   Error: {r['error']}")
        print(f"{'='*60}")
        enriched = sum(1 for r in results if r['status'] == 'enriched')
        print(f"Total: {len(results)} | Enriched: {enriched} | Not found: {sum(1 for r in results if r['status'] == 'not_found')}")


if __name__ == '__main__':
    main()
