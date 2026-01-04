#!/usr/bin/env python3
"""
Nyne.ai API Client
Provides synchronous API access for Person and Company enrichment.

Base URL: https://api.nyne.ai
Auth: X-API-Key + X-API-Secret headers
"""

import os
import json
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path
from N5.lib.paths import STAGING_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

NYNE_STAGING_DIR = STAGING_DIR / "nyne"


class NyneClient:
    """Client for Nyne.ai API."""
    
    BASE_URL = "https://api.nyne.ai"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or os.environ.get("NYNE_API_KEY")
        self.api_secret = api_secret or os.environ.get("NYNE_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Nyne API credentials not found. "
                "Set NYNE_API_KEY and NYNE_API_SECRET environment variables."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling and persistence."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=60, **kwargs)
            
            # Handle rate limits
            if response.status_code == 429:
                raise Exception("Rate limit exceeded (429)")
                
            response.raise_for_status()
            
            # PERSISTENCE: Save raw response to staging
            try:
                import json
                from pathlib import Path
                staging_dir = NYNE_STAGING_DIR
                staging_dir.mkdir(parents=True, exist_ok=True)
                
                # Create a safe filename slug
                payload = kwargs.get('json', {})
                safe_key = str(payload.get('social_media_url', 
                           payload.get('email', 
                           payload.get('domain', 'req'))))
                for char in ['/', ':', '.', '@']:
                    safe_key = safe_key.replace(char, '_')
                
                filename = f"{int(time.time())}_{endpoint.replace('/', '_')}_{safe_key[:50]}.json"
                with open(staging_dir / filename, 'w') as f:
                    json.dump(response.json(), f, indent=2)
                logger.info(f"💾 Raw response saved to {staging_dir / filename}")
            except Exception as pe:
                logger.warning(f"Could not persist raw response: {pe}")
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error ({method} {endpoint}): {e}")
            raise

    def _poll_for_result(self, request_id: str, max_wait: int = 120, poll_interval: int = 3, endpoint: str = "/person/enrichment") -> Dict[str, Any]:
        """Poll for async request completion."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            result = self._request("GET", f"{endpoint}?request_id={request_id}")
            
            status = result.get("data", {}).get("status")
            
            if status == "completed":
                return result
            elif status == "failed":
                raise Exception(f"Enrichment failed: {result}")
            elif status in ("queued", "processing", "pending"):
                # Still processing, continue polling
                time.sleep(poll_interval)
            else:
                # Unknown status, wait and retry
                logger.warning(f"Unknown status '{status}', continuing to poll...")
                time.sleep(poll_interval)
        
        raise Exception(f"Polling timed out after {max_wait}s for request_id={request_id}")
    
    # ==================== PERSON APIs ====================
    
    def enrich_person(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        social_media_url: Optional[str] = None,
        newsfeed: Optional[List[str]] = None,
        ai_enhanced_search: bool = False,
        lite_enrich: bool = False,
        probability_score: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich person data using email, phone, or social media URL.
        
        Args:
            email: Email address
            phone: Phone number
            social_media_url: LinkedIn, Twitter, or other social URL
            newsfeed: List of sources ["linkedin", "twitter", "instagram", "github", "facebook"] or ["all"]
            ai_enhanced_search: Enable AI-powered deep search (slower but more comprehensive)
            lite_enrich: Lite mode - 3 credits, basic fields only
            probability_score: Include match confidence score
        
        Returns:
            Enriched person data dict or None if not found
        
        Credits:
            - Standard: 6 credits
            - Lite: 3 credits
            - Newsfeed add-on: +6 credits when data found
        """
        if not any([email, phone, social_media_url]):
            raise ValueError("At least one of email, phone, or social_media_url required")
        
        payload = {}
        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone
        if social_media_url:
            payload["social_media_url"] = social_media_url
        if newsfeed:
            payload["newsfeed"] = newsfeed
        if ai_enhanced_search:
            payload["ai_enhanced_search"] = True
        if lite_enrich:
            payload["lite_enrich"] = True
        if probability_score:
            payload["probability_score"] = True
        
        logger.info(f"Enriching person: {email or phone or social_media_url}")
        
        response = self._request("POST", "/person/enrichment", json=payload)
        
        # Handle async response - poll if needed
        status = response.get("data", {}).get("status")
        if status in ("pending", "queued", "processing"):
            request_id = response["data"]["request_id"]
            logger.info(f"Async request (status={status}), polling request_id={request_id}")
            response = self._poll_for_result(request_id)
        
        # Extract result
        data = response.get("data", {})
        if data.get("status") == "completed" and data.get("result"):
            return data["result"]
        
        return None
    
    def get_person_newsfeed(
        self,
        social_media_url: str,
        sources: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get social media newsfeed for a person.
        
        Args:
            social_media_url: LinkedIn, Twitter, Instagram, GitHub, or Facebook URL
            sources: Optional filter for sources (default: all available)
        
        Returns:
            Newsfeed data dict or None
        """
        payload = {"social_media_url": social_media_url}
        if sources:
            payload["sources"] = sources
        
        logger.info(f"Getting newsfeed for: {social_media_url}")
        
        response = self._request("POST", "/person/newsfeed", json=payload)
        
        # Handle async
        if response.get("data", {}).get("status") == "pending":
            request_id = response["data"]["request_id"]
            response = self._poll_for_result(request_id)
        
        data = response.get("data", {})
        if data.get("status") == "completed":
            return data.get("result")
        
        return None
    
    def get_person_interests(self, social_media_url: str) -> Optional[Dict[str, Any]]:
        """
        Get person's interests based on who they follow.
        
        Args:
            social_media_url: Twitter profile URL
        
        Returns:
            Interests data (sports, politics, entertainment, hobbies, technology)
        """
        payload = {"social_media_url": social_media_url}
        
        logger.info(f"Getting interests for: {social_media_url}")
        
        response = self._request("POST", "/person/interests", json=payload)
        
        if response.get("data", {}).get("status") == "pending":
            request_id = response["data"]["request_id"]
            response = self._poll_for_result(request_id)
        
        data = response.get("data", {})
        if data.get("status") == "completed":
            return data.get("result")
        
        return None
    
    def search_person_articles(
        self,
        name: str,
        company: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for articles, interviews, podcasts about a person.
        
        Args:
            name: Person's full name
            company: Optional company name for disambiguation
        
        Returns:
            List of articles/content
        """
        payload = {"name": name}
        if company:
            payload["company"] = company
        
        logger.info(f"Searching articles for: {name}")
        
        response = self._request("POST", "/person/articlesearch", json=payload)
        
        if response.get("data", {}).get("status") == "pending":
            request_id = response["data"]["request_id"]
            response = self._poll_for_result(request_id)
        
        data = response.get("data", {})
        if data.get("status") == "completed":
            return data.get("result", {}).get("articles", [])
        
        return None
    
    # ==================== COMPANY APIs ====================
    
    def enrich_company(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        social_media_url: Optional[str] = None,
        # Legacy aliases
        domain: Optional[str] = None,
        company_name: Optional[str] = None,
        linkedin_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich company data.
        
        Args:
            email: Company email address
            phone: Company phone number
            social_media_url: LinkedIn company page URL (preferred)
            linkedin_url: Alias for social_media_url
            domain: Not directly supported - will attempt LinkedIn lookup
            company_name: Not directly supported - will attempt LinkedIn lookup
        
        Returns:
            Company data dict or None
        """
        # Handle linkedin_url alias
        if linkedin_url and not social_media_url:
            social_media_url = linkedin_url
        
        if not any([email, phone, social_media_url]):
            # If only domain/company_name provided, log warning
            if domain or company_name:
                logger.warning(f"Nyne company enrichment requires email, phone, or LinkedIn URL. Domain/name alone not supported.")
            raise ValueError("At least one of email, phone, or social_media_url (LinkedIn company URL) required")
        
        payload = {}
        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone
        if social_media_url:
            payload["social_media_url"] = social_media_url
        
        logger.info(f"Enriching company: {social_media_url or email or phone}")
        
        response = self._request("POST", "/company/enrichment", json=payload)
        
        # Handle async response
        data = response.get("data", {})
        status = data.get("status")
        
        if status in ("queued", "processing"):
            request_id = data.get("request_id")
            if request_id:
                return self._poll_for_result(request_id, endpoint="/company/enrichment")
        
        if data.get("result"):
            return data["result"]
        
        return None
    
    def check_seller(
        self,
        company_name: str,
        product_service: str
    ) -> Dict[str, Any]:
        """
        Check if a company sells a specific product/service.
        
        Args:
            company_name: Legal or common company name
            product_service: Product or service to check for
        
        Returns:
            Dict with 'sells' (bool), 'confidence', and 'evidence'
        
        Credits: 2 credits per completed verification
        """
        payload = {
            "company_name": company_name,
            "product_service": product_service
        }
        
        logger.info(f"Checking if {company_name} sells: {product_service}")
        
        response = self._request("POST", "/company/checkseller", json=payload)
        
        # Handle async response
        status = response.get("data", {}).get("status")
        if status in ("pending", "queued", "processing"):
            request_id = response["data"]["request_id"]
            logger.info(f"Async request (status={status}), polling request_id={request_id}")
            response = self._poll_for_result(request_id, endpoint="/company/checkseller")
        
        return response.get("data", {}).get("result", {})
    
    def check_company_feature(
        self,
        company: str,
        feature: str
    ) -> Dict[str, Any]:
        """
        Check if a company website uses a specific technology/feature.
        
        Args:
            company: Company name or domain to check
            feature: Technology to check (e.g., "jQuery library", "React framework", "SOC 2 badge")
        
        Returns:
            Dict with 'has_feature' (bool), 'confidence', and 'evidence'
        
        Credits: 3 credits per completed check
        """
        payload = {
            "company": company,
            "feature": feature
        }
        
        logger.info(f"Checking if {company} uses: {feature}")
        
        response = self._request("POST", "/company/checkfeature", json=payload)
        
        # Handle async response
        status = response.get("data", {}).get("status")
        if status in ("pending", "queued", "processing"):
            request_id = response["data"]["request_id"]
            logger.info(f"Async request (status={status}), polling request_id={request_id}")
            response = self._poll_for_result(request_id, endpoint="/company/checkfeature")
        
        return response.get("data", {}).get("result", {})
    
    def get_company_funding(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get company funding history.
        
        Args:
            domain: Company website
        
        Returns:
            Funding rounds, investors, valuations
        """
        payload = {"domain": domain}
        
        logger.info(f"Getting funding for: {domain}")
        
        response = self._request("POST", "/company/funding", json=payload)
        
        return response.get("data", {}).get("result")
    
    def get_company_needs(
        self,
        company_name: str,
        content: str,
        filing: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get company pain points and challenges from SEC filings.
        
        Args:
            company_name: Company to analyze (e.g., "Uber Technologies, Inc.")
            content: Topic to surface (e.g., "Regulatory challenges", "Supply chain issues")
            filing: Optional filing type filter (e.g., "Form 10-K", "Form 8-K")
        
        Returns:
            Dict with 'company' and 'needs' array containing filing insights
        
        Credits: 3 credits per completed analysis
        """
        payload = {
            "company_name": company_name,
            "content": content
        }
        if filing:
            payload["filing"] = filing
        
        logger.info(f"Getting company needs for: {company_name} (topic: {content})")
        
        response = self._request("POST", "/company/needs", json=payload)
        
        # Handle async response
        status = response.get("data", {}).get("status")
        if status in ("pending", "queued", "processing"):
            request_id = response["data"]["request_id"]
            logger.info(f"Async request (status={status}), polling request_id={request_id}")
            response = self._poll_for_result(request_id, endpoint="/company/needs")
        
        data = response.get("data", {})
        if data.get("status") == "completed" and data.get("result"):
            return data["result"]
        
        return None
    
    def get_investor_info(
        self,
        company_name: Optional[str] = None,
        company_domain: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive investor/VC fund information.
        
        Args:
            company_name: Investor name (e.g., "Y Combinator", "Sequoia Capital")
            company_domain: Investor domain (e.g., "ycombinator.com", "sequoiacap.com")
        
        Returns:
            Dict with investor_name, investor_domain, partners, location,
            investment_thesis, average_check_size, rounds_they_invest_in,
            investment_locations, recent_investments
        
        Credits: 20 credits per completed lookup
        """
        if not any([company_name, company_domain]):
            raise ValueError("At least one of company_name or company_domain required")
        
        payload = {}
        if company_name:
            payload["company_name"] = company_name
        if company_domain:
            payload["company_domain"] = company_domain
        
        logger.info(f"Getting investor info for: {company_name or company_domain}")
        
        response = self._request("POST", "/company/funders", json=payload)
        
        # Handle async response
        status = response.get("data", {}).get("status")
        if status in ("pending", "queued", "processing"):
            request_id = response["data"]["request_id"]
            logger.info(f"Async request (status={status}), polling request_id={request_id}")
            response = self._poll_for_result(request_id, endpoint="/company/funders")
        
        data = response.get("data", {})
        if data.get("status") == "completed" and data.get("result"):
            return data["result"]
        
        return None
    
    # ==================== USAGE API ====================
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current API usage statistics."""
        response = self._request("GET", "/usage")
        return response.get("data", {})


# Test harness
if __name__ == "__main__":
    print("🧪 Testing Nyne Client\n")
    
    try:
        client = NyneClient()
        print("✅ Client initialized with credentials")
        
        # Test usage endpoint (free, confirms auth works)
        print("\n📊 Checking usage...")
        usage = client.get_usage()
        print(f"Usage data: {usage}")
        
    except Exception as e:
        print(f"❌ Error: {e}")







