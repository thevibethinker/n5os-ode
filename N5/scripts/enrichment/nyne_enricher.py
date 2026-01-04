#!/usr/bin/env python3
from N5.lib.paths import N5_LOGS_DIR, N5_DATA_DIR
"""
Nyne Enrichment Module
Provides async enrichment using Nyne.ai API for CRM V3 system.

Strategy: D + Selective + Fallback
- Nyne provides social/newsfeed data Aviato lacks
- Nyne used as fallback when Aviato returns sparse data
- Both can be called together with merged intelligence

Designed to mirror aviato_enricher.py patterns.
"""

import sys
import json
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from pathlib import Path

# Add workspace to path for imports
sys.path.insert(0, '/home/workspace')
from Integrations.Nyne.nyne_client import NyneClient

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# Usage log (mirrors Aviato pattern)
USAGE_LOG = N5_LOGS_DIR / 'nyne_usage.jsonl'


def log_usage(
    lookup_key: str,
    endpoint: str,
    success: bool,
    found: bool,
    credits_used: int = 0,
    error: str = None
):
    """Log Nyne API usage for cost and behavior tracking."""
    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'lookup_key': lookup_key,
        'endpoint': endpoint,
        'success': success,
        'found': found,
        'credits_used': credits_used,
    }
    
    if error:
        log_entry['error'] = error
    
    with open(USAGE_LOG, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


async def enrich_person_via_nyne(
    email: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    phone: Optional[str] = None,
    include_newsfeed: bool = True,
    lite_mode: bool = False
) -> dict:
    """
    Enrich person using Nyne API.
    
    Args:
        email: Email address
        linkedin_url: LinkedIn profile URL
        phone: Phone number
        include_newsfeed: Whether to fetch social media newsfeed (adds 6 credits)
        lite_mode: Use lite enrichment (3 credits, basic fields only)
    
    Returns:
        Dict with {success, data, error, markdown}
    """
    lookup_key = email or linkedin_url or phone or "<unknown>"
    
    try:
        client = NyneClient()
        
        logger.info(f"Enriching via Nyne for key={lookup_key}")
        
        # Determine newsfeed sources
        newsfeed_sources = ["linkedin", "twitter"] if include_newsfeed and not lite_mode else None
        
        # Call Nyne API
        nyne_data = client.enrich_person(
            email=email,
            phone=phone,
            social_media_url=linkedin_url,
            newsfeed=newsfeed_sources,
            lite_enrich=lite_mode
        )
        
        if not nyne_data:
            log_usage(lookup_key, "person/enrichment", success=True, found=False, credits_used=0)
            logger.info(f"Profile not found for key={lookup_key}")
            
            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': f"""**Nyne Social Intelligence:**

Profile not found in Nyne database for `{lookup_key}`.

This contact may:
- Not have a discoverable email/social profile
- Have privacy settings restricting data access
"""
            }
        
        # Calculate credits used
        credits = 3 if lite_mode else 6
        if nyne_data.get('newsfeed'):
            credits += 6
        
        log_usage(lookup_key, "person/enrichment", success=True, found=True, credits_used=credits)
        logger.info(f"Successfully enriched key={lookup_key} - {nyne_data.get('displayname')}")
        
        # Build markdown intelligence block
        markdown = format_person_intelligence(nyne_data)
        
        return {
            'success': True,
            'data': nyne_data,
            'error': None,
            'markdown': markdown
        }
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error enriching key={lookup_key}: {error_msg}")
        log_usage(lookup_key, "person/enrichment", success=False, found=False, error=error_msg)
        
        if '429' in error_msg:
            return {
                'success': False,
                'data': None,
                'error': 'Rate limit exceeded',
                'markdown': """**Nyne Social Intelligence:**

⚠️ **Rate Limit Exceeded**
The Nyne API has rate-limited this request. Will retry with backoff.
"""
            }
        
        return {
            'success': False,
            'data': None,
            'error': error_msg,
            'markdown': f"""**Nyne Social Intelligence:**

⚠️ **Enrichment Error**
Failed to fetch data from Nyne: {error_msg}
"""
        }


async def get_social_newsfeed_via_nyne(
    linkedin_url: Optional[str] = None,
    twitter_url: Optional[str] = None
) -> dict:
    """
    Get social media newsfeed only (without full enrichment).
    
    Useful for meeting prep when you already have basic profile data.
    6 credits when data found.
    """
    social_url = linkedin_url or twitter_url
    if not social_url:
        return {
            'success': False,
            'data': None,
            'error': 'No social URL provided',
            'markdown': '**Nyne Newsfeed:** No social URL provided'
        }
    
    try:
        client = NyneClient()
        
        logger.info(f"Getting newsfeed for: {social_url}")
        
        newsfeed_data = client.get_person_newsfeed(social_url)
        
        if not newsfeed_data:
            log_usage(social_url, "person/newsfeed", success=True, found=False, credits_used=0)
            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': f"""**Nyne Social Activity:**

No recent social activity found for this profile.
"""
            }
        
        log_usage(social_url, "person/newsfeed", success=True, found=True, credits_used=6)
        
        markdown = format_newsfeed_intelligence(newsfeed_data)
        
        return {
            'success': True,
            'data': newsfeed_data,
            'error': None,
            'markdown': markdown
        }
    
    except Exception as e:
        error_msg = str(e)
        log_usage(social_url, "person/newsfeed", success=False, found=False, error=error_msg)
        
        return {
            'success': False,
            'data': None,
            'error': error_msg,
            'markdown': f"""**Nyne Social Activity:**

⚠️ **Error:** {error_msg}
"""
        }


async def get_person_interests_via_nyne(twitter_url: str) -> dict:
    """
    Get person's interests based on who they follow on Twitter.
    
    Returns sports teams, political interests, entertainment, hobbies, tech interests.
    """
    try:
        client = NyneClient()
        
        logger.info(f"Getting interests for: {twitter_url}")
        
        interests_data = client.get_person_interests(twitter_url)
        
        if not interests_data:
            log_usage(twitter_url, "person/interests", success=True, found=False, credits_used=0)
            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': "**Nyne Interests:** No interest data available"
            }
        
        log_usage(twitter_url, "person/interests", success=True, found=True, credits_used=6)
        
        markdown = format_interests_intelligence(interests_data)
        
        return {
            'success': True,
            'data': interests_data,
            'error': None,
            'markdown': markdown
        }
    
    except Exception as e:
        error_msg = str(e)
        log_usage(twitter_url, "person/interests", success=False, found=False, error=error_msg)
        
        return {
            'success': False,
            'data': None,
            'error': error_msg,
            'markdown': f"**Nyne Interests:** Error - {error_msg}"
        }


async def enrich_company_via_nyne(
    domain: Optional[str] = None,
    company_name: Optional[str] = None,
    linkedin_url: Optional[str] = None
) -> dict:
    """
    Enrich company using Nyne API.
    
    Args:
        domain: Company website domain
        company_name: Company name
        linkedin_url: LinkedIn company page URL
    
    Returns:
        Dict with {success, data, error, markdown}
    """
    lookup_key = domain or company_name or linkedin_url or "<unknown>"
    
    try:
        client = NyneClient()
        
        logger.info(f"Enriching company via Nyne: {lookup_key}")
        
        company_data = client.enrich_company(
            domain=domain,
            company_name=company_name,
            linkedin_url=linkedin_url
        )
        
        if not company_data:
            log_usage(lookup_key, "company/enrichment", success=True, found=False, credits_used=0)
            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': f"""**Nyne Company Intelligence:**

Company not found for `{lookup_key}`.
"""
            }
        
        log_usage(lookup_key, "company/enrichment", success=True, found=True, credits_used=6)
        
        markdown = format_company_intelligence(company_data)
        
        return {
            'success': True,
            'data': company_data,
            'error': None,
            'markdown': markdown
        }
    
    except Exception as e:
        error_msg = str(e)
        log_usage(lookup_key, "company/enrichment", success=False, found=False, error=error_msg)
        
        return {
            'success': False,
            'data': None,
            'error': error_msg,
            'markdown': f"""**Nyne Company Intelligence:**

⚠️ **Error:** {error_msg}
"""
        }


# ==================== MEETING PREP HELPERS ====================

# Cache for newsfeed data (keyed by LinkedIn URL)
NYNE_CACHE_DIR = N5_DATA_DIR / 'cache' / 'nyne'
NYNE_CACHE_MAX_AGE_DAYS = 7


def _get_cache_path(linkedin_url: str) -> Path:
    """Get cache file path for a LinkedIn URL."""
    import hashlib
    url_hash = hashlib.md5(linkedin_url.encode()).hexdigest()[:12]
    return NYNE_CACHE_DIR / f"newsfeed_{url_hash}.json"


def _is_cache_valid(cache_path: Path, max_age_days: int) -> bool:
    """Check if cache file exists and is within max age."""
    if not cache_path.exists():
        return False
    
    cache_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
    age = datetime.now() - cache_mtime
    return age.days < max_age_days


async def get_recent_social_activity(
    linkedin_url: str,
    max_age_days: int = 7,
    force_refresh: bool = False
) -> dict:
    """
    Get recent social activity for meeting prep with caching.
    
    This is the primary function for meeting prep workflows.
    Checks cache first to avoid redundant API calls (6 credits each).
    
    Args:
        linkedin_url: LinkedIn profile URL
        max_age_days: Maximum cache age in days (default 7)
        force_refresh: Force API call even if cache exists
    
    Returns:
        Dict with {success, data, error, markdown, cached}
    """
    if not linkedin_url:
        return {
            'success': False,
            'data': None,
            'error': 'No LinkedIn URL provided',
            'markdown': '**Social Activity:** No LinkedIn URL available',
            'cached': False
        }
    
    # Ensure cache directory exists
    NYNE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_path = _get_cache_path(linkedin_url)
    
    # Check cache first (unless force refresh)
    if not force_refresh and _is_cache_valid(cache_path, max_age_days):
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(f"Using cached Nyne data for {linkedin_url}")
            
            # Rebuild markdown from cached data
            markdown = format_social_activity_for_meeting_prep(cached_data)
            
            return {
                'success': True,
                'data': cached_data,
                'error': None,
                'markdown': markdown,
                'cached': True,
                'cache_age_days': (datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)).days
            }
        except Exception as e:
            logger.warning(f"Cache read failed, will fetch fresh: {e}")
    
    # Fetch fresh data
    logger.info(f"Fetching fresh Nyne social activity for {linkedin_url}")
    
    result = await get_social_newsfeed_via_nyne(linkedin_url=linkedin_url)
    
    if result['success'] and result['data']:
        # Save to cache
        try:
            cache_data = {
                'linkedin_url': linkedin_url,
                'fetched_at': datetime.utcnow().isoformat() + 'Z',
                'newsfeed': result['data']
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cached Nyne data for {linkedin_url}")
        except Exception as e:
            logger.warning(f"Failed to cache Nyne data: {e}")
        
        # Format for meeting prep
        markdown = format_social_activity_for_meeting_prep(cache_data)
        
        return {
            'success': True,
            'data': result['data'],
            'error': None,
            'markdown': markdown,
            'cached': False
        }
    
    return {
        'success': result['success'],
        'data': None,
        'error': result.get('error'),
        'markdown': result.get('markdown', '**Social Activity:** No data available'),
        'cached': False
    }


def format_social_activity_for_meeting_prep(cache_data: dict) -> str:
    """
    Format Nyne social data specifically for meeting prep context.
    
    Returns concise, actionable summary for pre-meeting review.
    """
    lines = ["**Recent Social Activity (Nyne):**\n"]
    
    newsfeed = cache_data.get('newsfeed', [])
    if isinstance(newsfeed, dict):
        newsfeed = newsfeed.get('posts', [])
    
    if not newsfeed:
        lines.append("No recent posts found.")
        return "\n".join(lines)
    
    # Show up to 3 most recent posts
    for post in newsfeed[:3]:
        source = post.get('source', 'unknown').title()
        date = post.get('date_posted', '')[:10]
        content = post.get('content', '')[:120]
        
        if content:
            lines.append(f"- **{source}** ({date}): \"{content}...\"")
    
    lines.append("")
    
    # Suggest conversation starters if we have content
    if newsfeed:
        lines.append("**Potential conversation starters:**")
        
        # Extract topics/themes from posts
        topics = []
        for post in newsfeed[:3]:
            content = post.get('content', '')
            if content and len(content) > 20:
                # Take first sentence or phrase as topic hint
                topic = content.split('.')[0][:80]
                if topic:
                    topics.append(topic)
        
        if topics:
            for i, topic in enumerate(topics[:2], 1):
                lines.append(f"{i}. Their recent post about \"{topic}...\"")
        else:
            lines.append("1. Their recent social media activity")
    
    # Add cache info
    fetched_at = cache_data.get('fetched_at', '')
    if fetched_at:
        lines.append(f"\n*Data fetched: {fetched_at[:10]}*")
    
    return "\n".join(lines)


# ==================== FORMATTING FUNCTIONS ====================

def format_person_intelligence(data: Dict[str, Any]) -> str:
    """Format Nyne person data into markdown intelligence block."""
    lines = ["**Nyne Social Intelligence:**\n"]
    
    # Basic Info
    if data.get('displayname'):
        lines.append(f"**Name:** {data['displayname']}")
    if data.get('bio'):
        lines.append(f"**Bio:** {data['bio']}")
    if data.get('location'):
        lines.append(f"**Location:** {data['location']}")
    lines.append("")
    
    # Current Role (from organizations)
    orgs = data.get('organizations', [])
    if orgs:
        current = orgs[0]
        lines.append("**Current Role:**")
        if current.get('title'):
            lines.append(f"- Title: {current['title']}")
        if current.get('name'):
            lines.append(f"- Company: {current['name']}")
        if current.get('startDate'):
            lines.append(f"- Since: {current['startDate']}")
        lines.append("")
    
    # Contact Info
    phones = data.get('fullphone', [])
    emails = data.get('altemails', [])
    if phones or emails:
        lines.append("**Contact Info:**")
        for phone in phones[:2]:
            if isinstance(phone, dict):
                lines.append(f"- Phone: {phone.get('fullphone', phone)}")
            else:
                lines.append(f"- Phone: {phone}")
        for email in emails[:3]:
            lines.append(f"- Email: {email}")
        lines.append("")
    
    # Social Profiles
    social = data.get('social_profiles', {})
    if social:
        lines.append("**Social Profiles:**")
        for platform, profile in social.items():
            if isinstance(profile, dict):
                url = profile.get('url', '')
                username = profile.get('username', '')
                followers = profile.get('followers')
                
                line = f"- {platform.title()}: "
                if url:
                    line += f"[{username or url}]({url})"
                if followers:
                    line += f" ({followers:,} followers)"
                lines.append(line)
            elif profile:
                lines.append(f"- {platform.title()}: {profile}")
        lines.append("")
    
    # Recent Activity (Newsfeed)
    newsfeed = data.get('newsfeed', [])
    if newsfeed:
        lines.append("**Recent Social Activity:**")
        for post in newsfeed[:3]:
            source = post.get('source', 'unknown')
            content = post.get('content', '')[:150]
            date = post.get('date_posted', '')[:10]
            engagement = post.get('engagement', {})
            
            lines.append(f"- [{source.title()}] {date}")
            lines.append(f"  \"{content}...\"")
            
            if engagement:
                metrics = []
                if engagement.get('likes'):
                    metrics.append(f"{engagement['likes']} likes")
                if engagement.get('comments'):
                    metrics.append(f"{engagement['comments']} comments")
                if engagement.get('shares') or engagement.get('retweets'):
                    shares = engagement.get('shares') or engagement.get('retweets')
                    metrics.append(f"{shares} shares")
                if metrics:
                    lines.append(f"  ({', '.join(metrics)})")
        lines.append("")
    
    # Education
    schools = data.get('schools_info', [])
    if schools:
        lines.append("**Education:**")
        for school in schools[:2]:
            name = school.get('name', 'Unknown')
            degree = school.get('degree', '')
            title = school.get('title', '')
            
            edu_str = f"- {name}"
            if degree or title:
                edu_str += f" - {degree} {title}".strip()
            lines.append(edu_str)
        lines.append("")
    
    return "\n".join(lines)


def format_newsfeed_intelligence(data: Dict[str, Any]) -> str:
    """Format newsfeed-only data into markdown."""
    lines = ["**Nyne Social Activity:**\n"]
    
    posts = data if isinstance(data, list) else data.get('posts', [])
    
    if not posts:
        lines.append("No recent posts found.")
        return "\n".join(lines)
    
    for post in posts[:5]:
        source = post.get('source', 'unknown')
        content = post.get('content', '')[:200]
        date = post.get('date_posted', '')[:10]
        url = post.get('url', '')
        engagement = post.get('engagement', {})
        
        lines.append(f"**[{source.title()}]** {date}")
        lines.append(f"> {content}")
        
        if engagement:
            metrics = []
            for key in ['likes', 'comments', 'shares', 'retweets', 'replies']:
                if engagement.get(key):
                    metrics.append(f"{engagement[key]} {key}")
            if metrics:
                lines.append(f"*{', '.join(metrics)}*")
        
        if url:
            lines.append(f"[View post]({url})")
        lines.append("")
    
    return "\n".join(lines)


def format_interests_intelligence(data: Dict[str, Any]) -> str:
    """Format interests data into markdown."""
    lines = ["**Nyne Interests Analysis:**\n"]
    
    categories = ['sports', 'politics', 'entertainment', 'hobbies', 'technology']
    
    for category in categories:
        interests = data.get(category, [])
        if interests:
            lines.append(f"**{category.title()}:**")
            for interest in interests[:5]:
                if isinstance(interest, dict):
                    name = interest.get('name', str(interest))
                    lines.append(f"- {name}")
                else:
                    lines.append(f"- {interest}")
            lines.append("")
    
    return "\n".join(lines)


def format_company_intelligence(data: Dict[str, Any]) -> str:
    """Format Nyne company data into markdown."""
    lines = ["**Nyne Company Intelligence:**\n"]
    
    # Basic Info
    if data.get('name'):
        lines.append(f"**Company:** {data['name']}")
    if data.get('description'):
        lines.append(f"**Description:** {data['description'][:300]}")
    if data.get('industry'):
        lines.append(f"**Industry:** {data['industry']}")
    if data.get('location'):
        lines.append(f"**HQ:** {data['location']}")
    lines.append("")
    
    # Size & Metrics
    lines.append("**Metrics:**")
    if data.get('employee_count'):
        lines.append(f"- Employees: {data['employee_count']:,}")
    if data.get('employee_range'):
        lines.append(f"- Size: {data['employee_range']}")
    if data.get('founded_year'):
        lines.append(f"- Founded: {data['founded_year']}")
    lines.append("")
    
    # Funding (if available)
    if data.get('funding') or data.get('total_funding'):
        lines.append("**Funding:**")
        if data.get('total_funding'):
            lines.append(f"- Total Raised: ${data['total_funding']:,}")
        if data.get('last_funding_round'):
            lines.append(f"- Last Round: {data['last_funding_round']}")
        if data.get('investors'):
            investors = data['investors'][:3]
            lines.append(f"- Investors: {', '.join(investors)}")
        lines.append("")
    
    # Links
    if data.get('website') or data.get('linkedin_url'):
        lines.append("**Links:**")
        if data.get('website'):
            lines.append(f"- Website: {data['website']}")
        if data.get('linkedin_url'):
            lines.append(f"- LinkedIn: {data['linkedin_url']}")
        lines.append("")
    
    return "\n".join(lines)


# ==================== COMBINED ENRICHMENT ====================

async def enrich_with_fallback(
    email: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    aviato_result: Optional[dict] = None
) -> dict:
    """
    Smart enrichment: Use Nyne selectively based on Aviato results.
    
    Strategy:
    1. If Aviato returned no data → Full Nyne enrichment
    2. If Aviato returned sparse data → Nyne for supplemental social data
    3. If Aviato returned rich data → Nyne for newsfeed only (meeting prep)
    
    Args:
        email: Email address
        linkedin_url: LinkedIn URL
        aviato_result: Result from aviato_enricher (optional)
    
    Returns:
        Combined/supplemental intelligence
    """
    # Determine Aviato data richness
    aviato_data = aviato_result.get('data') if aviato_result else None
    aviato_sparse = (
        not aviato_data or 
        not aviato_data.get('current_title') or 
        not aviato_data.get('all_experiences')
    )
    
    if not aviato_data:
        # No Aviato data → Full Nyne enrichment
        logger.info("No Aviato data, performing full Nyne enrichment")
        return await enrich_person_via_nyne(
            email=email,
            linkedin_url=linkedin_url,
            include_newsfeed=True
        )
    
    elif aviato_sparse:
        # Sparse Aviato data → Nyne for supplemental
        logger.info("Sparse Aviato data, using Nyne for supplemental enrichment")
        return await enrich_person_via_nyne(
            email=email,
            linkedin_url=linkedin_url,
            include_newsfeed=True
        )
    
    else:
        # Rich Aviato data → Nyne for social activity only
        logger.info("Rich Aviato data, using Nyne for social activity only")
        if linkedin_url:
            return await get_social_newsfeed_via_nyne(linkedin_url=linkedin_url)
        else:
            # Can't get newsfeed without social URL
            return {
                'success': True,
                'data': None,
                'error': None,
                'markdown': "**Nyne:** Skipped (rich Aviato data, no LinkedIn URL for newsfeed)"
            }


# Test harness
if __name__ == '__main__':
    import asyncio
    
    async def test():
        """Test Nyne enrichment."""
        print("🧪 Testing Nyne Enricher\n")
        
        # Test with a known profile
        test_email = "michael@nyne.ai"
        
        print(f"Testing: {test_email}")
        print("=" * 60)
        
        result = await enrich_person_via_nyne(email=test_email, include_newsfeed=False)
        
        if result['success']:
            if result['data']:
                print(f"✓ Found: {result['data'].get('displayname')}")
                print("\n" + result['markdown'])
            else:
                print("✗ Not found in Nyne database")
                print("\n" + result['markdown'])
        else:
            print(f"✗ Error: {result['error']}")
            print("\n" + result['markdown'])
        
        # Show usage log
        print("\n📊 Usage Log:")
        if USAGE_LOG.exists():
            with open(USAGE_LOG, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    status = "✓" if entry['found'] else "✗"
                    print(f"{status} {entry['lookup_key']} - {entry['endpoint']} - {entry['credits_used']} credits")
    
    asyncio.run(test())


