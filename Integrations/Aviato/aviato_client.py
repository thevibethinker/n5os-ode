#!/usr/bin/env python3
"""
Aviato API Client
Provides clean Python interface to Aviato's person and company enrichment APIs
"""

import os
import requests
from typing import Dict, Optional, List
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AviatoClient:
    """Client for interacting with Aviato Data API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Aviato client.
        If api_key is not provided, it will look for AVIATO_N5OS_V2_KEY environment variable.
        """
        self.api_key = api_key or os.getenv('AVIATO_N5OS_V2_KEY')
        self.base_url = os.getenv('AVIATO_API_BASE_URL', 'https://data.api.aviato.co')
        
        if not self.api_key:
            logging.error("No Aviato API Key found. Set AVIATO_N5OS_V2_KEY environment variable.")
            raise ValueError("AVIATO_N5OS_V2_KEY is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.timeout = 30  # seconds
        logger.info("Aviato client initialized")
    
    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """Make authenticated GET request to Aviato API with error handling"""
        url = f'{self.base_url}/{endpoint}'
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Entity not found: {params}")
                return None
            elif e.response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def enrich_person(self,
                     id: Optional[str] = None,
                     email: Optional[str] = None,
                     linkedin_url: Optional[str] = None,
                     linkedin_id: Optional[str] = None,
                     linkedin_entity_id: Optional[str] = None,
                     twitter_id: Optional[str] = None,
                     crunchbase_id: Optional[str] = None,
                     angellist_id: Optional[str] = None) -> Optional[Dict]:
        """
        Enrich a person profile using any available identifier.
        
        Args:
            id: Aviato person ID
            email: Email address
            linkedin_url: LinkedIn profile URL (accepts public, Sales Navigator, Recruiter)
            linkedin_id: LinkedIn username/slug (the part after /in/)
            linkedin_entity_id: LinkedIn entity ID (from Sales Navigator URLs)
            twitter_id: Twitter handle
            crunchbase_id: Crunchbase identifier
            angellist_id: AngelList identifier
        
        Returns:
            Dict with enriched person data, or None if not found
        """
        params = {}
        
        # Build params from provided identifiers
        if id:
            params['id'] = id
        if email:
            params['email'] = email
        if linkedin_url:
            params['linkedinURL'] = linkedin_url
        if linkedin_id:
            params['linkedinID'] = linkedin_id
        if linkedin_entity_id:
            params['linkedinEntityId'] = linkedin_entity_id
        if twitter_id:
            params['twitterID'] = twitter_id
        if crunchbase_id:
            params['crunchbaseID'] = crunchbase_id
        if angellist_id:
            params['angelListID'] = angellist_id
        
        if not params:
            raise ValueError("At least one identifier must be provided")
        
        logger.info(f"Enriching person with params: {list(params.keys())}")
        return self._make_request('person/enrich', params)
    
    def enrich_company(self,
                      id: Optional[str] = None,
                      website: Optional[str] = None,
                      linkedin_url: Optional[str] = None,
                      linkedin_id: Optional[str] = None,
                      linkedin_num_id: Optional[str] = None,
                      facebook_id: Optional[str] = None,
                      twitter_id: Optional[str] = None,
                      crunchbase_id: Optional[str] = None,
                      pitchbook_id: Optional[str] = None,
                      producthunt_id: Optional[str] = None,
                      dealroom_id: Optional[str] = None,
                      golden_id: Optional[str] = None,
                      angellist_id: Optional[str] = None,
                      wellfound_id: Optional[str] = None) -> Optional[Dict]:
        """
        Enrich a company profile using any available identifier.
        
        Args:
            id: Aviato company ID
            website: Company website/domain
            linkedin_url: LinkedIn company URL
            linkedin_id: LinkedIn company slug
            linkedin_num_id: LinkedIn numeric company ID
            facebook_id: Facebook page ID
            twitter_id: Twitter handle
            crunchbase_id: Crunchbase identifier
            pitchbook_id: Pitchbook identifier
            producthunt_id: Product Hunt identifier
            dealroom_id: Dealroom identifier
            golden_id: Golden identifier
            angellist_id: AngelList identifier
            wellfound_id: Wellfound identifier
        
        Returns:
            Dict with enriched company data, or None if not found
        """
        params = {}
        
        if id:
            params['id'] = id
        if website:
            params['website'] = website
        if linkedin_url:
            params['linkedinURL'] = linkedin_url
        if linkedin_id:
            params['linkedinID'] = linkedin_id
        if linkedin_num_id:
            params['linkedinNumID'] = linkedin_num_id
        if facebook_id:
            params['facebookID'] = facebook_id
        if twitter_id:
            params['twitterID'] = twitter_id
        if crunchbase_id:
            params['crunchbaseID'] = crunchbase_id
        if pitchbook_id:
            params['pitchbookID'] = pitchbook_id
        if producthunt_id:
            params['producthuntID'] = producthunt_id
        if dealroom_id:
            params['dealroomID'] = dealroom_id
        if golden_id:
            params['goldenID'] = golden_id
        if angellist_id:
            params['angellistID'] = angellist_id
        if wellfound_id:
            params['wellfoundID'] = wellfound_id
        
        if not params:
            raise ValueError("At least one identifier must be provided")
        
        logger.info(f"Enriching company with params: {list(params.keys())}")
        return self._make_request('company/enrich', params)
    
    def batch_enrich_people(self, 
                           profiles: List[Dict], 
                           rate_limit_delay: float = 0.2) -> List[Dict]:
        """
        Batch enrich multiple person profiles with rate limiting.
        
        Args:
            profiles: List of dicts with person identifiers (email, linkedin_url, etc.)
            rate_limit_delay: Delay between requests in seconds (default: 0.2s = 5 req/s = 300/min)
        
        Returns:
            List of enrichment results with status
        """
        results = []
        total = len(profiles)
        
        logger.info(f"Starting batch enrichment of {total} profiles")
        
        for idx, profile in enumerate(profiles, 1):
            logger.info(f"Enriching profile {idx}/{total}")
            
            try:
                enriched = self.enrich_person(**profile)
                results.append({
                    'input': profile,
                    'output': enriched,
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    results.append({
                        'input': profile,
                        'output': None,
                        'status': 'not_found',
                        'error': 'Profile not found',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                elif e.response.status_code == 429:
                    logger.warning("Rate limit hit, backing off...")
                    time.sleep(60)  # Wait 1 minute
                    # Retry this one
                    try:
                        enriched = self.enrich_person(**profile)
                        results.append({
                            'input': profile,
                            'output': enriched,
                            'status': 'success',
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    except Exception as retry_error:
                        results.append({
                            'input': profile,
                            'output': None,
                            'status': 'error',
                            'error': str(retry_error),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                else:
                    results.append({
                        'input': profile,
                        'output': None,
                        'status': 'error',
                        'error': f'HTTP {e.response.status_code}: {e.response.text}',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            except Exception as e:
                results.append({
                    'input': profile,
                    'output': None,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Rate limiting delay (except on last iteration)
            if idx < total:
                time.sleep(rate_limit_delay)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"Batch complete: {success_count}/{total} successful")
        
        return results
    
    def batch_enrich_companies(self,
                              companies: List[Dict],
                              rate_limit_delay: float = 0.2) -> List[Dict]:
        """
        Batch enrich multiple company profiles with rate limiting.
        
        Args:
            companies: List of dicts with company identifiers (website, linkedin_url, etc.)
            rate_limit_delay: Delay between requests in seconds
        
        Returns:
            List of enrichment results with status
        """
        results = []
        total = len(companies)
        
        logger.info(f"Starting batch enrichment of {total} companies")
        
        for idx, company in enumerate(companies, 1):
            logger.info(f"Enriching company {idx}/{total}")
            
            try:
                enriched = self.enrich_company(**company)
                results.append({
                    'input': company,
                    'output': enriched,
                    'status': 'success',
                    'timestamp': datetime.utcnow().isoformat()
                })
            except Exception as e:
                results.append({
                    'input': company,
                    'output': None,
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            if idx < total:
                time.sleep(rate_limit_delay)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        logger.info(f"Batch complete: {success_count}/{total} successful")
        
        return results


if __name__ == '__main__':
    # Quick test
    client = AviatoClient()
    
    print("Testing person enrichment...")
    person = client.enrich_person(linkedin_url='https://linkedin.com/in/williamhgates')
    if person:
        print(f"✓ {person.get('fullName')} - {person.get('headline')}")
    
    print("\\nTesting company enrichment...")
    company = client.enrich_company(linkedin_url='https://linkedin.com/company/google')
    if company:
        print(f"✓ {company.get('name')} - {company.get('computed_headcount')} employees")


