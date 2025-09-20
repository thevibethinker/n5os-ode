#!/usr/bin/env python3
"""
Jobs Ingestion ATS Pipeline Implementation Plan

This script implements the full ATS-centric jobs ingestion pipeline components and integrates them into the N5 OS command authoring and workflow system. It is intended to be run in a dedicated new thread workspace for iterative development and testing.

Workflow Steps:
- Setup jobs ingestion subsystem
- Implement ATS Detector
- Implement Ashby client
- Implement Greenhouse client
- Implement Lever client
- Finalize jobs pipeline

Usage:
Run this script interactively or via CLI in the Zo Computer environment

"""

import sys
import os
import logging
import requests
from typing import Optional, Dict, List, Any
import json
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
import traceback
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Standard job listing data structure"""
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    ats_system: str = ""
    posted_date: str = ""
    job_id: str = ""
    department: str = ""
    employment_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ATSDetector:
    """Detects which ATS system is used based on URL or HTML content."""
    
    def __init__(self):
        self.ats_patterns = {
            'ashby': {
                'domains': ['ashbyhq.com', 'jobs.ashbyhq.com'],
                'indicators': ['ashby-job-board', 'ashby.com', 'ashbyhq']
            },
            'greenhouse': {
                'domains': ['greenhouse.io', 'boards.greenhouse.io', 'grnh.se'],
                'indicators': ['greenhouse-job-board', 'greenhouse.io', 'boards.greenhouse']
            },
            'lever': {
                'domains': ['lever.co', 'jobs.lever.co'],
                'indicators': ['lever-job-board', 'lever.co', 'jobs.lever']
            },
            'workday': {
                'domains': ['myworkdayjobs.com', 'workday.com'],
                'indicators': ['workday', 'myworkdayjobs']
            },
            'smartrecruiters': {
                'domains': ['smartrecruiters.com'],
                'indicators': ['smartrecruiters', 'smart-recruiters']
            },
            'apple': {
                'domains': ['apple.com'],
                'indicators': ['apple', 'apple jobs']
            }
        }
    
    def detect_ats(self, url: str, html_content: Optional[str] = None) -> Optional[str]:
        """Detect ATS from URL or HTML content."""
        url_lower = url.lower()
        
        # Check URL patterns first
        for ats_name, patterns in self.ats_patterns.items():
            for domain in patterns['domains']:
                if domain in url_lower:
                    return ats_name
        
        # Check HTML content if available
        if html_content:
            content_lower = html_content.lower()
            for ats_name, patterns in self.ats_patterns.items():
                for indicator in patterns['indicators']:
                    if indicator in content_lower:
                        return ats_name
        
        return None
    
    def discover_careers_page(self, company_name: str) -> Optional[Dict[str, str]]:
        """Attempt to discover careers page for a company"""
        common_patterns = [
            f"https://{company_name.lower()}.com/careers",
            f"https://careers.{company_name.lower()}.com",
            f"https://jobs.{company_name.lower()}.com",
            f"https://{company_name.lower()}.com/jobs",
            f"https://boards.greenhouse.io/{company_name.lower()}",
            f"https://jobs.ashbyhq.com/{company_name.lower()}",
            f"https://jobs.lever.co/{company_name.lower()}"
        ]
        
        for url in common_patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    final_url = response.url
                    ats_type = self.detect_ats(final_url)
                    if ats_type:
                        return {
                            'ats': ats_type,
                            'careers_url': final_url
                        }
            except requests.RequestException:
                continue
        
        return None

class AshbyClient:
    """Client for Ashby ATS API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://api.ashbyhq.com'
        self.public_base_url = 'https://jobs.ashbyhq.com'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from Ashby."""
        jobs = []
        
        # Try public careers page first
        try:
            careers_url = f"{self.public_base_url}/{company_slug}"
            response = requests.get(careers_url, timeout=10)
            
            if response.status_code == 200:
                jobs = self._parse_ashby_page(response.text, company_slug, careers_url)
            else:
                logger.warning(f"Ashby public page not found for {company_slug}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching Ashby jobs for {company_slug}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} Ashby jobs for {company_slug}")
        return jobs
    
    def _parse_ashby_page(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from Ashby HTML page"""
        jobs = []
        
        # Simple regex-based parsing (in production would use BeautifulSoup)
        job_patterns = [
            r'data-job-id="([^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>.*?<span[^>]*>([^<]+)</span>',
            r'<div[^>]*job[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?</div>'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    job = JobListing(
                        title=match[1].strip() if len(match) > 1 else "Unknown Title",
                        company=company_slug.replace('-', ' ').title(),
                        location=match[2].strip() if len(match) > 2 else "Remote",
                        url=urljoin(base_url, match[0]) if match[0].startswith('/') else match[0],
                        ats_system="ashby",
                        posted_date=datetime.now().isoformat(),
                        job_id=match[0] if len(match) > 0 else ""
                    )
                    jobs.append(job)
        
        return jobs[:50]  # Limit results

class GreenhouseClient:
    """Client for Greenhouse ATS API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://harvest.greenhouse.io/v1'
        self.public_base_url = 'https://boards.greenhouse.io'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from Greenhouse."""
        jobs = []
        
        # Try public API endpoint first
        try:
            api_url = f"{self.public_base_url}/{company_slug}/jobs"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                try:
                    # Try to parse as JSON first
                    data = response.json()
                    jobs = self._parse_greenhouse_json(data, company_slug)
                except json.JSONDecodeError:
                    # Fall back to HTML parsing
                    jobs = self._parse_greenhouse_html(response.text, company_slug, api_url)
            else:
                logger.warning(f"Greenhouse public API not available for {company_slug}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching Greenhouse jobs for {company_slug}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} Greenhouse jobs for {company_slug}")
        return jobs
    
    def _parse_greenhouse_json(self, data: Dict, company_slug: str) -> List[JobListing]:
        """Parse jobs from Greenhouse JSON response"""
        jobs = []
        
        jobs_data = data.get('jobs', data) if isinstance(data, dict) else data
        if isinstance(jobs_data, list):
            for job_data in jobs_data:
                job = JobListing(
                    title=job_data.get('title', 'Unknown Title'),
                    company=company_slug.replace('-', ' ').title(),
                    location=job_data.get('location', {}).get('name', 'Remote'),
                    url=job_data.get('absolute_url', ''),
                    description=job_data.get('content', ''),
                    ats_system="greenhouse",
                    posted_date=job_data.get('updated_at', datetime.now().isoformat()),
                    job_id=str(job_data.get('id', '')),
                    department=job_data.get('department', {}).get('name', '') if job_data.get('department') else ''
                )
                jobs.append(job)
        
        return jobs
    
    def _parse_greenhouse_html(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from Greenhouse HTML page"""
        jobs = []
        
        # Simple regex-based parsing
        job_patterns = [
            r'<div[^>]*opening[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>.*?<span[^>]*>([^<]+)</span>.*?</div>',
            r'data-job[^>]*>.*?<h3[^>]*>([^<]+)</h3>.*?<p[^>]*>([^<]+)</p>'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    job = JobListing(
                        title=match[1].strip() if len(match) > 1 else "Unknown Title",
                        company=company_slug.replace('-', ' ').title(),
                        location=match[2].strip() if len(match) > 2 else "Remote",
                        url=urljoin(base_url, match[0]) if match[0].startswith('/') else match[0],
                        ats_system="greenhouse",
                        posted_date=datetime.now().isoformat()
                    )
                    jobs.append(job)
        
        return jobs[:50]

class LeverClient:
    """Client for Lever ATS API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://api.lever.co/v0'
        self.public_base_url = 'https://jobs.lever.co'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from Lever."""
        jobs = []
        
        # Try public API first
        try:
            if self.api_key:
                # Use authenticated API
                api_url = f"{self.base_url}/postings/{company_slug}"
                headers = {'Authorization': f'Bearer {self.api_key}'}
                response = requests.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = self._parse_lever_api_response(data, company_slug)
                else:
                    logger.warning(f"Lever API failed for {company_slug}: {response.status_code}")
            
            # Fall back to public careers page
            if not jobs:
                careers_url = f"{self.public_base_url}/{company_slug}"
                response = requests.get(careers_url, timeout=10)
                
                if response.status_code == 200:
                    jobs = self._parse_lever_html(response.text, company_slug, careers_url)
                else:
                    logger.warning(f"Lever public page not found for {company_slug}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error fetching Lever jobs for {company_slug}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} Lever jobs for {company_slug}")
        return jobs
    
    def _parse_lever_api_response(self, data: Dict, company_slug: str) -> List[JobListing]:
        """Parse jobs from Lever API response"""
        jobs = []
        
        for job_data in data.get('data', []):
            location_parts = []
            for category in job_data.get('categories', {}).get('location', []):
                location_parts.append(category.get('name', ''))
            
            job = JobListing(
                title=job_data.get('text', 'Unknown Title'),
                company=company_slug.replace('-', ' ').title(),
                location=', '.join(location_parts) or 'Remote',
                url=job_data.get('hostedUrl', ''),
                description=job_data.get('description', ''),
                ats_system="lever",
                posted_date=job_data.get('createdAt', datetime.now().isoformat()),
                job_id=job_data.get('id', ''),
                department=job_data.get('categories', {}).get('team', [{}])[0].get('name', '') if job_data.get('categories', {}).get('team') else ''
            )
            jobs.append(job)
        
        return jobs
    
    def _parse_lever_html(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from Lever HTML page"""
        jobs = []
        
        # Simple regex-based parsing
        job_patterns = [
            r'<a[^>]*href="([^"]+/apply)"[^>]*>([^<]+)</a>.*?<span[^>]*location[^>]*>([^<]+)</span>',
            r'data-qa="posting[^>]*>.*?<h5[^>]*>([^<]+)</h5>.*?<span[^>]*>([^<]+)</span>'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    job = JobListing(
                        title=match[1].strip() if len(match) > 1 else "Unknown Title",
                        company=company_slug.replace('-', ' ').title(),
                        location=match[2].strip() if len(match) > 2 else "Remote",
                        url=match[0] if match[0].startswith('http') else urljoin(base_url, match[0]),
                        ats_system="lever",
                        posted_date=datetime.now().isoformat()
                    )
                    jobs.append(job)
        
        return jobs[:50]

class WorkdayClient:
    """Client for Workday ATS."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://myworkdayjobs.com'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from Workday."""
        jobs = []
        
        try:
            # Try common Workday URLs
            possible_urls = [
                f"https://myworkdayjobs.com/{company_slug}",
                f"https://myworkdayjobs.com/en-US/{company_slug}",
                f"https://{company_slug}.myworkdayjobs.com"
            ]
            
            careers_url = None
            for url in possible_urls:
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        careers_url = response.url
                        break
                except:
                    continue
            
            if careers_url:
                response = requests.get(careers_url, timeout=10)
                if response.status_code == 200:
                    jobs = self._parse_workday_html(response.text, company_slug, careers_url)
        
        except Exception as e:
            logger.error(f"Error fetching Workday jobs for {company_slug}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} Workday jobs for {company_slug}")
        return jobs
    
    def _parse_workday_html(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from Workday HTML"""
        jobs = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Look for job cards or listings
        job_cards = soup.find_all(['div', 'li'], class_=re.compile(r'job|posting|position', re.I))
        
        for card in job_cards[:50]:  # Limit
            title_elem = card.find(['h3', 'h4', 'a'], class_=re.compile(r'title', re.I))
            if not title_elem:
                title_elem = card.find(['h3', 'h4', 'a'])
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                if url and not url.startswith('http'):
                    url = urljoin(base_url, url)
                
                location_elem = card.find(class_=re.compile(r'location', re.I))
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                job = JobListing(
                    title=title,
                    company=company_slug.replace('-', ' ').title(),
                    location=location,
                    url=url or base_url,
                    ats_system="workday",
                    posted_date=datetime.now().isoformat()
                )
                jobs.append(job)
        
        return jobs

class SmartRecruitersClient:
    """Client for SmartRecruiters ATS."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://www.smartrecruiters.com'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from SmartRecruiters."""
        jobs = []
        
        try:
            careers_url = f"https://www.smartrecruiters.com/{company_slug}"
            response = requests.get(careers_url, timeout=10)
            
            if response.status_code == 200:
                jobs = self._parse_smartrecruiters_html(response.text, company_slug, careers_url)
        
        except Exception as e:
            logger.error(f"Error fetching SmartRecruiters jobs for {company_slug}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} SmartRecruiters jobs for {company_slug}")
        return jobs
    
    def _parse_smartrecruiters_html(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from SmartRecruiters HTML"""
        jobs = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        job_cards = soup.find_all(['div', 'li'], class_=re.compile(r'job|opening', re.I))
        
        for card in job_cards[:50]:
            title_elem = card.find(['h3', 'h4', 'a'], class_=re.compile(r'title', re.I))
            if not title_elem:
                title_elem = card.find(['h3', 'h4', 'a'])
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                if url and not url.startswith('http'):
                    url = urljoin(base_url, url)
                
                location_elem = card.find(class_=re.compile(r'location', re.I))
                location = location_elem.get_text(strip=True) if location_elem else "Remote"
                
                job = JobListing(
                    title=title,
                    company=company_slug.replace('-', ' ').title(),
                    location=location,
                    url=url or base_url,
                    ats_system="smartrecruiters",
                    posted_date=datetime.now().isoformat()
                )
                jobs.append(job)
        
        return jobs

class AppleClient:
    """Client for Apple ATS."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://jobs.apple.com'
    
    def get_jobs(self, company_slug: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Fetch jobs from Apple."""
        jobs = []
        
        try:
            # Apple uses apple.com/jobs, not company-specific
            careers_url = "https://jobs.apple.com/en-us/search"
            # Note: Apple jobs are not easily scraped; this is a placeholder
            response = requests.get(careers_url, timeout=10)
            
            if response.status_code == 200:
                jobs = self._parse_apple_html(response.text, "Apple", careers_url)
        
        except Exception as e:
            logger.error(f"Error fetching Apple jobs: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} Apple jobs")
        return jobs
    
    def _parse_apple_html(self, html_content: str, company_slug: str, base_url: str) -> List[JobListing]:
        """Parse job listings from Apple HTML (limited success)"""
        jobs = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Apple jobs are dynamic; this is basic
        job_links = soup.find_all('a', href=re.compile(r'/en-us/details/'))
        
        for link in job_links[:20]:  # Limit
            title = link.get_text(strip=True)
            url = urljoin(base_url, link.get('href'))
            
            job = JobListing(
                title=title,
                company="Apple",
                location="Various",
                url=url,
                ats_system="apple",
                posted_date=datetime.now().isoformat()
            )
            jobs.append(job)
        
        return jobs

class GenericScraper:
    """Generic web scraper for unknown ATS systems."""
    
    def __init__(self):
        pass
    
    def scrape_jobs(self, careers_url: str, company_name: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Scrape jobs from any careers page."""
        jobs = []
        
        try:
            response = requests.get(careers_url, timeout=10)
            if response.status_code == 200:
                jobs = self._parse_generic_html(response.text, company_name, careers_url)
        except Exception as e:
            logger.error(f"Error scraping {careers_url}: {e}")
        
        # Apply role filters
        if role_filters and jobs:
            filtered_jobs = []
            for job in jobs:
                if any(filter_term.lower() in job.title.lower() for filter_term in role_filters):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        logger.info(f"Found {len(jobs)} jobs via generic scraping for {company_name}")
        return jobs
    
    def _parse_generic_html(self, html_content: str, company_name: str, base_url: str) -> List[JobListing]:
        """Generic HTML parsing for job listings."""
        jobs = []
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Look for common job listing patterns
        job_selectors = [
            soup.find_all(['div', 'li'], class_=re.compile(r'job|career|position|opening', re.I)),
            soup.find_all('a', href=re.compile(r'job|career|position', re.I))
        ]
        
        for selector in job_selectors:
            for elem in selector[:30]:  # Limit
                title = ""
                url = ""
                
                if elem.name == 'a':
                    title = elem.get_text(strip=True)
                    url = elem.get('href')
                else:
                    link = elem.find('a')
                    if link:
                        title = link.get_text(strip=True)
                        url = link.get('href')
                    else:
                        title = elem.get_text(strip=True)
                
                if title and len(title) > 3:
                    if url and not url.startswith('http'):
                        url = urljoin(base_url, url)
                    
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location="Remote",  # Default
                        url=url or base_url,
                        ats_system="unknown",
                        posted_date=datetime.now().isoformat()
                    )
                    jobs.append(job)
        
        return jobs[:50]

class JobsIngestionPipeline:
    """Main pipeline orchestrator for job ingestion"""
    
    def __init__(self):
        self.detector = ATSDetector()
        self.ashby_client = AshbyClient()
        self.greenhouse_client = GreenhouseClient()
        self.lever_client = LeverClient()
        self.workday_client = WorkdayClient()
        self.smartrecruiters_client = SmartRecruitersClient()
        self.apple_client = AppleClient()
        self.generic_scraper = GenericScraper()
        self.stats = {
            'companies_processed': 0,
            'jobs_found': 0,
            'jobs_filtered': 0,
            'errors': []
        }
    
    def setup_jobs_ingestion_subsystem(self) -> Dict[str, Any]:
        """Set up the jobs ingestion subsystem."""
        logger.info("Setting up jobs ingestion subsystem...")
        
        try:
            # Create necessary directories
            directories = [
                '/home/workspace/N5/jobs_data',
                '/home/workspace/N5/jobs_data/raw',
                '/home/workspace/N5/jobs_data/processed',
                '/home/workspace/N5/logs',
                '/home/workspace/N5/jobs/config'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Create configuration file
            config = {
                'version': '1.0',
                'ats_systems': ['ashby', 'greenhouse', 'lever', 'workday', 'smartrecruiters', 'apple'],
                'rate_limits': {
                    'ashby': {'requests_per_minute': 60},
                    'greenhouse': {'requests_per_minute': 100},
                    'lever': {'requests_per_minute': 120},
                    'workday': {'requests_per_minute': 60},
                    'smartrecruiters': {'requests_per_minute': 60},
                    'apple': {'requests_per_minute': 30}
                },
                'output_formats': ['jsonl', 'json'],
                'max_retries': 3,
                'timeout_seconds': 10,
                'batch_size': 50
            }
            
            config_path = '/home/workspace/N5/jobs/config/pipeline_config.json'
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Subsystem setup complete.")
            return {'status': 'success', 'config': config}
        
        except Exception as e:
            error_msg = f"Failed to setup subsystem: {e}"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}
    
    def ingest_jobs_from_company(self, company_name: str, role_filters: Optional[List[str]] = None) -> List[JobListing]:
        """Ingest jobs from a specific company"""
        try:
            self.stats['companies_processed'] += 1
            logger.info(f"Processing company: {company_name}")
            
            # Detect ATS and careers URL
            ats_info = self.detector.discover_careers_page(company_name)
            if ats_info:
                ats_type = ats_info['ats']
                careers_url = ats_info['careers_url']
            else:
                # Fallback to generic scraping
                careers_url = f"https://{company_name.lower()}.com/careers"
                ats_type = 'unknown'
            
            company_slug = company_name.lower().replace(' ', '-').replace('.', '-')
            
            # Fetch jobs based on ATS type
            jobs = []
            if ats_type == 'ashby':
                jobs = self.ashby_client.get_jobs(company_slug, role_filters)
            elif ats_type == 'greenhouse':
                jobs = self.greenhouse_client.get_jobs(company_slug, role_filters)
            elif ats_type == 'lever':
                jobs = self.lever_client.get_jobs(company_slug, role_filters)
            elif ats_type == 'workday':
                jobs = self.workday_client.get_jobs(company_slug, role_filters)
            elif ats_type == 'smartrecruiters':
                jobs = self.smartrecruiters_client.get_jobs(company_slug, role_filters)
            elif ats_type == 'apple':
                jobs = self.apple_client.get_jobs(company_slug, role_filters)
            else:
                # Generic scraping
                jobs = self.generic_scraper.scrape_jobs(careers_url, company_name, role_filters)
            
            self.stats['jobs_found'] += len(jobs)
            logger.info(f"Found {len(jobs)} jobs from {company_name} via {ats_type}")
            return jobs
        
        except Exception as e:
            error_msg = f"Error processing {company_name}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.stats['errors'].append(error_msg)
            return []
    
    def save_jobs_to_files(self, jobs: List[JobListing], filename_prefix: str) -> bool:
        """Save jobs to both JSONL and JSON formats"""
        try:
            timestamp = int(time.time())
            
            # Save as JSONL (one job per line)
            jsonl_path = f'/home/workspace/N5/jobs_data/raw/{filename_prefix}_{timestamp}.jsonl'
            with open(jsonl_path, 'w') as f:
                for job in jobs:
                    f.write(json.dumps(job.to_dict()) + '\n')
            
            # Save as JSON (array format)
            json_path = f'/home/workspace/N5/jobs_data/processed/{filename_prefix}_{timestamp}.json'
            with open(json_path, 'w') as f:
                json.dump([job.to_dict() for job in jobs], f, indent=2)
            
            logger.info(f"Saved {len(jobs)} jobs to {jsonl_path} and {json_path}")
            return True
        
        except Exception as e:
            error_msg = f"Error saving jobs: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def process_companies_batch(self, companies: List[str], role_filters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Process a batch of companies"""
        start_time = time.time()
        all_jobs = []
        
        for company in companies:
            try:
                jobs = self.ingest_jobs_from_company(company, role_filters)
                all_jobs.extend(jobs)
                
                # Rate limiting - be respectful
                time.sleep(2)
            
            except Exception as e:
                logger.error(f"Error processing {company}: {e}")
                continue
        
        # Save all jobs
        if all_jobs:
            self.save_jobs_to_files(all_jobs, 'batch_jobs')
        
        # Generate summary
        end_time = time.time()
        summary = {
            'batch_status': 'completed',
            'duration_seconds': round(end_time - start_time, 2),
            'companies_requested': len(companies),
            'companies_processed': self.stats['companies_processed'],
            'total_jobs_found': self.stats['jobs_found'],
            'jobs_saved': len(all_jobs),
            'errors': self.stats['errors'],
            'timestamp': datetime.now().isoformat()
        }
        
        return summary

def setup_jobs_ingestion_subsystem():
    """Set up the jobs ingestion subsystem."""
    pipeline = JobsIngestionPipeline()
    return pipeline.setup_jobs_ingestion_subsystem()

def implement_ats_detector():
    """Implement ATS detection functionality."""
    logger.info("Implementing ATS detector...")
    # Already implemented above
    logger.info("ATS detector implemented.")

def implement_ashby_client():
    """Implement Ashby client."""
    logger.info("Implementing Ashby client...")
    # Already implemented
    logger.info("Ashby client implemented.")

def implement_greenhouse_client():
    """Implement Greenhouse client."""
    logger.info("Implementing Greenhouse client...")
    # Already implemented
    logger.info("Greenhouse client implemented.")

def implement_lever_client():
    """Implement Lever client."""
    logger.info("Implementing Lever client...")
    # Already implemented
    logger.info("Lever client implemented.")

def finalize_jobs_pipeline():
    """Finalize the jobs pipeline integration."""
    logger.info("Finalizing jobs pipeline...")
    
    try:
        # Create comprehensive pipeline configuration
        pipeline_config = {
            'pipeline_name': 'N5_ATS_Jobs_Ingestion',
            'version': '1.0.0',
            'description': 'ATS-based job ingestion pipeline for N5 OS',
            'supported_ats': {
                'ashby': {
                    'enabled': True,
                    'api_base': 'https://api.ashbyhq.com',
                    'public_base': 'https://jobs.ashbyhq.com',
                    'rate_limit': 60
                },
                'greenhouse': {
                    'enabled': True,
                    'api_base': 'https://harvest.greenhouse.io/v1',
                    'public_base': 'https://boards.greenhouse.io',
                    'rate_limit': 100
                },
                'lever': {
                    'enabled': True,
                    'api_base': 'https://api.lever.co/v0',
                    'public_base': 'https://jobs.lever.co',
                    'rate_limit': 120
                },
                'workday': {
                    'enabled': True,
                    'api_base': 'https://myworkdayjobs.com',
                    'public_base': 'https://myworkdayjobs.com',
                    'rate_limit': 60
                },
                'smartrecruiters': {
                    'enabled': True,
                    'api_base': 'https://www.smartrecruiters.com',
                    'public_base': 'https://www.smartrecruiters.com',
                    'rate_limit': 60
                },
                'apple': {
                    'enabled': True,
                    'api_base': 'https://jobs.apple.com',
                    'public_base': 'https://jobs.apple.com',
                    'rate_limit': 30
                }
            },
            'data_dirs': {
                'raw': '/home/workspace/N5/jobs_data/raw',
                'processed': '/home/workspace/N5/jobs_data/processed',
                'config': '/home/workspace/N5/jobs/config',
                'logs': '/home/workspace/N5/logs'
            },
            'workflow_integration': {
                'command_authoring': True,
                'telemetry': True,
                'validation': True
            },
            'output_formats': ['jsonl', 'json'],
            'created_at': datetime.now().isoformat()
        }
        
        # Save main configuration
        config_path = '/home/workspace/N5/jobs_pipeline_config.json'
        with open(config_path, 'w') as f:
            json.dump(pipeline_config, f, indent=2)
        
        # Create workflow integration file
        workflow_integration = {
            'workflow_name': 'jobs_ingestion_workflow',
            'steps': [
                {
                    'step': 'setup_subsystem',
                    'function': 'setup_jobs_ingestion_subsystem',
                    'description': 'Initialize directories and configuration'
                },
                {
                    'step': 'detect_ats',
                    'function': 'ATSDetector.discover_careers_page',
                    'description': 'Detect ATS system for target companies'
                },
                {
                    'step': 'ingest_jobs',
                    'function': 'JobsIngestionPipeline.ingest_jobs_from_company',
                    'description': 'Fetch jobs from detected ATS systems'
                },
                {
                    'step': 'save_results',
                    'function': 'JobsIngestionPipeline.save_jobs_to_files',
                    'description': 'Save job data in multiple formats'
                }
            ],
            'integration_points': {
                'command_authoring': '/home/workspace/N5/command_authoring/',
                'existing_jobs_module': '/home/workspace/N5/jobs/modules/',
                'workflows': '/home/workspace/N5/jobs/workflows/'
            }
        }
        
        workflow_path = '/home/workspace/N5/jobs_ingestion_workflow.json'
        with open(workflow_path, 'w') as f:
            json.dump(workflow_integration, f, indent=2)
        
        # Create a simple CLI wrapper script
        cli_script = '''#!/usr/bin/env python3
"""CLI wrapper for the jobs ingestion pipeline"""

import sys
import argparse
from jobs_implementation_plan_20250920_120000 import JobsIngestionPipeline

def main():
    parser = argparse.ArgumentParser(description='N5 Jobs Ingestion Pipeline')
    parser.add_argument('companies', nargs='+', help='Companies to process')
    parser.add_argument('--filters', nargs='*', help='Role filters (e.g., engineer developer)')
    parser.add_argument('--setup-only', action='store_true', help='Only setup the subsystem')
    
    args = parser.parse_args()
    
    pipeline = JobsIngestionPipeline()
    
    if args.setup_only:
        result = pipeline.setup_jobs_ingestion_subsystem()
        print(f"Setup result: {result}")
        return
    
    # Setup first
    setup_result = pipeline.setup_jobs_ingestion_subsystem()
    if setup_result['status'] != 'success':
        print(f"Setup failed: {setup_result}")
        sys.exit(1)
    
    # Process companies
    result = pipeline.process_companies_batch(args.companies, args.filters)
    print(f"Pipeline result: {result}")

if __name__ == '__main__':
    main()
'''
        
        cli_path = '/home/workspace/N5/jobs_ingestion_cli.py'
        with open(cli_path, 'w') as f:
            f.write(cli_script)
        
        # Make CLI script executable
        os.chmod(cli_path, 0o755)
        
        logger.info(f"Jobs pipeline finalized with config at {config_path}")
        logger.info(f"CLI wrapper created at {cli_path}")
        logger.info(f"Workflow integration saved to {workflow_path}")
        
        return {
            'status': 'success',
            'config_path': config_path,
            'cli_path': cli_path,
            'workflow_path': workflow_path
        }
    
    except Exception as e:
        error_msg = f"Error finalizing pipeline: {e}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {'status': 'error', 'error': error_msg}

def run_pipeline_demo():
    """Run a demonstration of the complete pipeline"""
    print("Starting jobs ingestion ATS pipeline implementation...")
    
    pipeline = JobsIngestionPipeline()
    
    try:
        # Step 1: Setup subsystem
        print("\n=== Step 1: Setting up jobs ingestion subsystem ===")
        setup_result = pipeline.setup_jobs_ingestion_subsystem()
        print(f"Setup result: {setup_result['status']}")
        
        if setup_result['status'] != 'success':
            print(f"Setup failed: {setup_result['error']}")
            return 1
        
        # Step 2-6: Individual implementations are now integrated
        print("\n=== Step 2-6: ATS clients implemented ===")
        print("✓ ATSDetector implemented")
        print("✓ AshbyClient implemented")
        print("✓ GreenhouseClient implemented")
        print("✓ LeverClient implemented")
        
        # Step 7: Test with sample companies
        print("\n=== Step 7: Testing pipeline with sample companies ===")
        test_companies = ['Amalgamated Bank Of Ny', 'Datavant', 'Equinox', 'Cloaked', 'Apple']
        role_filters = ['product manager']
        
        print(f"Processing companies: {test_companies}")
        print(f"With role filters: {role_filters}")
        
        result = pipeline.process_companies_batch(test_companies, role_filters)
        
        # Step 8: Finalize pipeline
        print("\n=== Step 8: Finalizing pipeline integration ===")
        finalize_result = finalize_jobs_pipeline()
        print(f"Finalization: {finalize_result.get('status', 'completed')}")
        
        # Display final results
        print("\n=== Pipeline Execution Results ===")
        print(json.dumps(result, indent=2))
        
        print("\n=== Pipeline Implementation Complete ===")
        print("✓ Jobs ingestion subsystem setup")
        print("✓ ATS detection implemented (Ashby, Greenhouse, Lever)")
        print("✓ Individual ATS clients implemented")
        print("✓ Pipeline orchestration completed")
        print("✓ N5 OS workflow integration configured")
        print(f"✓ Processed {result['companies_processed']} companies")
        print(f"✓ Found {result['total_jobs_found']} total jobs")
        
        if result['errors']:
            print(f"⚠ {len(result['errors'])} errors occurred:")
            for error in result['errors'][:3]:  # Show first 3 errors
                print(f"  - {error}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error during pipeline execution: {e}")
        logger.error(traceback.format_exc())
        print(f"\nPipeline failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_pipeline_demo()
    sys.exit(exit_code)
