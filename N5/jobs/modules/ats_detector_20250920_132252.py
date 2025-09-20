#!/usr/bin/env python3
"""
ATS Detector Module
Input: company name string
Output: {"ats": "ashby|greenhouse|workday|...", "careers_url": "https://..."} or None
"""

import json
import urllib.parse
from typing import Optional, Dict

def detect_ats(company: str) -> Optional[Dict[str, str]]:
    """
    Detect ATS platform and careers URL for a company.
    Uses simple heuristics; expand with web_search if needed.
    """
    import requests
    
    # Known mappings for common companies
    known_mappings = {
        'netflix': {'ats': 'lever', 'careers_url': 'https://jobs.netflix.com'},
        'stripe': {'ats': 'greenhouse', 'careers_url': 'https://stripe.com/jobs'},
        'openai': {'ats': 'ashby', 'careers_url': 'https://openai.com/careers'},
        'anthropic': {'ats': 'greenhouse', 'careers_url': 'https://boards.greenhouse.io/anthropic'},
        'uber': {'ats': 'greenhouse', 'careers_url': 'https://www.uber.com/careers'},
        'airbnb': {'ats': 'greenhouse', 'careers_url': 'https://careers.airbnb.com'}
    }
    
    company_lower = company.lower()
    if company_lower in known_mappings:
        return known_mappings[company_lower]
    
    # Try common career page patterns
    common_patterns = [
        f"https://{company_lower}.com/careers",
        f"https://careers.{company_lower}.com",
        f"https://jobs.{company_lower}.com",
        f"https://{company_lower}.com/jobs",
        f"https://boards.greenhouse.io/{company_lower}",
        f"https://jobs.ashbyhq.com/{company_lower}",
        f"https://jobs.lever.co/{company_lower}"
    ]
    
    for url in common_patterns:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                final_url = response.url.lower()
                if 'greenhouse.io' in final_url:
                    return {'ats': 'greenhouse', 'careers_url': response.url}
                elif 'ashbyhq.com' in final_url:
                    return {'ats': 'ashby', 'careers_url': response.url}
                elif 'lever.co' in final_url:
                    return {'ats': 'lever', 'careers_url': response.url}
        except requests.RequestException:
            continue
    
    return None

if __name__ == "__main__":
    # Smoke test: python -m n5.jobs.modules.ats_detector
    test_company = "stripe"
    result = detect_ats(test_company)
    print(json.dumps(result))