#!/usr/bin/env python3
"""
Aviato Enrichment Module
Provides async enrichment using Aviato API for CRM V3 system

Designed for integration with crm_enrichment_worker.py
"""

import sys
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import os

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')
from Integrations.Aviato.aviato_client import AviatoClient
from Integrations.Aviato.crm_mapper import AviatoCRMMapper

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Usage log
USAGE_LOG = Path('/home/workspace/N5/logs/aviato_usage.jsonl')


def log_usage(email: str, success: bool, person_found: bool, error: str = None, linkedin_url: str | None = None):
    """Log Aviato API usage for cost and behavior tracking.

    This function is intentionally tolerant: email may be empty, and linkedin_url
    is optional. All fields are written to aviato_usage.jsonl for later analysis.
    """
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'email': email,
        'success': success,
        'person_found': person_found,
    }

    if linkedin_url:
        log_entry['linkedin_url'] = linkedin_url
    if error:
        log_entry['error'] = error

    with open(USAGE_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


async def enrich_via_aviato(email: Optional[str] = None,
                            name: Optional[str] = None,
                            linkedin_url: Optional[str] = None) -> dict:
    """Enrich profile using Aviato API.

    At least one of `email` or `linkedin_url` must be provided.
    Existing call sites that only pass `email` continue to work.
    """
    if not email and not linkedin_url:
        raise ValueError("enrich_via_aviato requires at least an email or a linkedin_url")

    lookup_key = email or linkedin_url or "<unknown>"

    try:
        # Prefer Zo/ N5OS-specific secret, then legacy name for compatibility
        api_key = os.environ.get("AVIATO_N5OS_V2_KEY") or os.environ.get("AVIATO_API_KEY")
        if not api_key:
            msg = "Aviato API key not found in environment (expected AVIATO_N5OS_V2_KEY or AVIATO_API_KEY)"
            logger.error("Error enriching key=%s: %s", lookup_key, msg)
            return {
                'success': False,
                'data': None,
                'error': msg,
                'markdown': f"""**Aviato Professional Intelligence:**\n\n⚠️ **Enrichment Error**\nFailed to fetch data from Aviato: {msg}\n"""
            }

        client = AviatoClient()
        mapper = AviatoCRMMapper()

        logger.info(f"Enriching via Aviato for key={lookup_key}")

        # Call Aviato API using both identifiers when available
        aviato_data = client.enrich_person(email=email, linkedin_url=linkedin_url)

        if not aviato_data:
            # 404 - person not found
            log_usage(email=email or "", success=True, person_found=False, linkedin_url=linkedin_url)
            logger.info(f"Profile not found for key={lookup_key}")

            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': f"""**Aviato Professional Intelligence:**\n\nProfile not found in Aviato database for `{lookup_key}`.\n\nThis contact may:\n- Not have a public LinkedIn profile\n- Use a different email on LinkedIn\n- Have privacy settings restricting data access\n"""
            }

        # Map to CRM format
        crm_data = mapper.map_person_to_crm(aviato_data)
        highlights = mapper.extract_career_highlights(crm_data)

        # Log successful enrichment
        log_usage(email=email or crm_data.get('email', ''),
                  success=True,
                  person_found=True,
                  linkedin_url=linkedin_url or crm_data.get('linkedin_url'))
        logger.info(f"Successfully enriched key={lookup_key} - {crm_data.get('full_name')}")

        # Build markdown intelligence block
        markdown = format_intelligence_block(crm_data, highlights)

        return {
            'success': True,
            'data': crm_data,
            'error': None,
            'markdown': markdown
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error enriching key={lookup_key}: {error_msg}")
        log_usage(email=email or "", success=False, person_found=False, error=error_msg, linkedin_url=linkedin_url)

        # Handle rate limiting
        if '429' in error_msg:
            return {
                'success': False,
                'data': None,
                'error': 'Rate limit exceeded',
                'markdown': """**Aviato Professional Intelligence:**\n\n⚠️ **Rate Limit Exceeded**\nThe Aviato API has rate-limited this request. This job will be automatically retried with exponential backoff.\n"""
            }

        # Generic error
        return {
            'success': False,
            'data': None,
            'error': error_msg,
            'markdown': f"""**Aviato Professional Intelligence:**\n\n⚠️ **Enrichment Error**\nFailed to fetch data from Aviato: {error_msg}\n"""
        }


def format_intelligence_block(crm_data: Dict, highlights: list) -> str:
    """
    Format CRM data into intelligence markdown block.
    
    Args:
        crm_data: Mapped CRM data from AviatoCRMMapper
        highlights: Career highlights list
    
    Returns:
        Formatted markdown string
    """
    lines = ["**Aviato Professional Intelligence:**\n"]
    
    # Highlights (if any)
    if highlights:
        lines.append("**Career Highlights:**")
        for highlight in highlights:
            lines.append(f"- {highlight}")
        lines.append("")
    
    # Current Role
    lines.append("**Current Role:**")
    if crm_data.get('current_title'):
        lines.append(f"- Title: {crm_data['current_title']}")
    if crm_data.get('current_company_name'):
        lines.append(f"- Company: {crm_data['current_company_name']}")
    if crm_data.get('current_position_start'):
        lines.append(f"- Started: {crm_data['current_position_start'][:10]}")  # YYYY-MM-DD
    if crm_data.get('location'):
        lines.append(f"- Location: {crm_data['location']}")
    lines.append("")
    
    # Professional Profile
    lines.append("**Professional Profile:**")
    if crm_data.get('linkedin_url'):
        lines.append(f"- LinkedIn: [{crm_data['linkedin_url']}](https://{crm_data['linkedin_url']})")
    if crm_data.get('headline'):
        lines.append(f"- Headline: {crm_data['headline']}")
    if crm_data.get('linkedin_connections'):
        lines.append(f"- Connections: {crm_data['linkedin_connections']:,}")
    if crm_data.get('linkedin_followers'):
        lines.append(f"- Followers: {crm_data['linkedin_followers']:,}")
    if crm_data.get('open_to_work'):
        lines.append(f"- Open to Work: {'Yes ✓' if crm_data['open_to_work'] else 'No'}")
    lines.append("")
    
    # Background
    lines.append("**Background:**")
    
    # Experience
    exp_list = crm_data.get('all_experiences', [])
    if exp_list:
        lines.append(f"- {len(exp_list)} previous role(s)")
        # Show top 3 recent experiences
        for idx, exp in enumerate(exp_list[:3], 1):
            position_list = exp.get('positionList', [])
            if position_list:
                pos = position_list[0]
                title = pos.get('title', 'Unknown Role')
                company = exp.get('companyName', 'Unknown Company')
                start = exp.get('startDate', '')[:4]  # Just year
                lines.append(f"  {idx}. {title} @ {company} ({start})")
    
    # Education
    edu_list = crm_data.get('all_education', [])
    if edu_list:
        lines.append(f"- {len(edu_list)} education entr{'ies' if len(edu_list) != 1 else 'y'}")
        for idx, edu in enumerate(edu_list[:2], 1):
            school_data = edu.get('school', {})
            school_name = school_data.get('fullName', 'Unknown School')
            degree = edu.get('name', '')
            if degree:
                lines.append(f"  {idx}. {school_name} - {degree}")
            else:
                lines.append(f"  {idx}. {school_name}")
    
    # Skills
    skills = crm_data.get('skills', [])
    if skills:
        top_skills = skills[:5]
        lines.append(f"- Skills: {', '.join(top_skills)}")
    
    lines.append("")
    
    # Investor Profile (if applicable)
    if crm_data.get('investor_type'):
        lines.append("**Investor Profile:**")
        lines.append(f"- Type: {crm_data['investor_type']}")
        if crm_data.get('investor_portfolio_count'):
            lines.append(f"- Portfolio: {crm_data['investor_portfolio_count']} investments")
        if crm_data.get('investor_min_check') and crm_data.get('investor_max_check'):
            min_check = crm_data['investor_min_check']
            max_check = crm_data['investor_max_check']
            lines.append(f"- Check Size: ${min_check:,} - ${max_check:,}")
        if crm_data.get('investor_interests'):
            interests = ', '.join(crm_data['investor_interests'][:3])
            lines.append(f"- Interests: {interests}")
        lines.append("")
    
    # Metadata
    lines.append("**Metadata:**")
    if crm_data.get('aviato_last_updated'):
        updated = crm_data['aviato_last_updated'][:10]  # YYYY-MM-DD
        lines.append(f"- Last Updated: {updated}")
    if crm_data.get('aviato_person_id'):
        lines.append(f"- Aviato ID: `{crm_data['aviato_person_id']}`")
    
    return "\n".join(lines)


# Test harness
if __name__ == '__main__':
    import asyncio
    
    async def test():
        """Test enrichment with known profiles"""
        test_profiles = [
            ('konrad@aviato.co', 'Konrad Kucharski'),
            ('epak171@gmail.com', 'Elaine Pak'),
            ('attawar.v@gmail.com', 'Vrijen Attawar')
        ]
        
        print("🧪 Testing Aviato Enricher\n")
        
        for email, name in test_profiles:
            print(f"Testing: {email}")
            print("=" * 60)
            
            result = await enrich_via_aviato(email, name)
            
            if result['success']:
                if result['data']:
                    print(f"✓ Found: {result['data'].get('full_name')}")
                    print("\n" + result['markdown'])
                else:
                    print("✗ Not found in Aviato database")
                    print("\n" + result['markdown'])
            else:
                print(f"✗ Error: {result['error']}")
                print("\n" + result['markdown'])
            
            print("\n" + "=" * 60 + "\n")
        
        # Show usage log
        print("\n📊 Usage Log:")
        if USAGE_LOG.exists():
            with open(USAGE_LOG, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    status = "✓" if entry['person_found'] else "✗"
                    print(f"{status} {entry['email']} - {entry['timestamp']}")
    
    asyncio.run(test())




