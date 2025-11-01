#!/usr/bin/env python3
"""Marvin Ventures Job Board Scraper - Browser Automation with Stealth"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://jobs.marvinvc.com"
OUTPUT_DIR = Path("/home/workspace/marvin_jobs_data")
TIMEOUT = 60000

class MarvinJobScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
    
    async def extract_next_data(self, page: Page) -> Optional[Dict]:
        """Extract __NEXT_DATA__ JSON from page"""
        try:
            data = await page.evaluate("""
                () => {
                    const script = document.querySelector('script#__NEXT_DATA__');
                    return script ? JSON.parse(script.textContent) : null;
                }
            """)
            return data
        except Exception as e:
            logger.error(f"Failed to extract __NEXT_DATA__: {e}")
            return None
    
    async def scrape_jobs_page(self) -> Dict:
        """Scrape all jobs from the main jobs page"""
        logger.info("Starting browser automation...")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            logger.info(f"Navigating to {BASE_URL}/jobs")
            await page.goto(f"{BASE_URL}/jobs", wait_until="domcontentloaded", timeout=TIMEOUT)
            await asyncio.sleep(3)
            
            # Check if we got blocked
            content = await page.content()
            if "api@getro.com" in content or "provide all job data" in content:
                logger.error("Got blocked by Getro bot detection")
                raise Exception("Bot detection triggered - site is blocking automated access")
            
            logger.info("Extracting __NEXT_DATA__ from page...")
            data = await self.extract_next_data(page)
            
            if not data:
                logger.error("Could not extract __NEXT_DATA__")
                return {}
            
            # Check how many jobs loaded
            jobs_data = data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("jobs", {})
            found = len(jobs_data.get("found", []))
            total = jobs_data.get("total", 0)
            
            logger.info(f"Initially loaded {found}/{total} jobs")
            
            if found < total:
                logger.info("Scrolling to trigger lazy loading...")
                for i in range(30):  # Scroll up to 30 times
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(0.5)
                    
                    # Re-extract data to check if more loaded
                    current_data = await self.extract_next_data(page)
                    if current_data:
                        current_found = len(current_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("jobs", {}).get("found", []))
                        if current_found > found:
                            logger.info(f"Loaded {current_found}/{total} jobs...")
                            found = current_found
                            data = current_data
                        if current_found >= total:
                            break
            
            logger.info(f"Final count: {found}/{total} jobs extracted")
            return data
    
    async def scrape_companies_page(self) -> Dict:
        """Scrape all companies from the companies page"""
        logger.info("Scraping companies page...")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ]
            )
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            await Stealth().apply_stealth_async(page)
            
            logger.info(f"Navigating to {BASE_URL}/companies")
            await page.goto(f"{BASE_URL}/companies", wait_until="domcontentloaded", timeout=TIMEOUT)
            await asyncio.sleep(3)
            
            logger.info("Extracting __NEXT_DATA__...")
            data = await self.extract_next_data(page)
            return data
    
    async def scrape_all(self) -> Dict:
        """Scrape all data from the job board"""
        logger.info("=" * 60)
        logger.info("Starting Marvin Ventures Job Board Scraper")
        logger.info("=" * 60)
        
        # Scrape jobs page
        jobs_page_data = await self.scrape_jobs_page()
        
        # Scrape companies page
        companies_page_data = await self.scrape_companies_page()
        
        # Extract structured data
        jobs_data = jobs_page_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("jobs", {})
        companies_data = companies_page_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("companies", {})
        
        jobs_list = jobs_data.get("found", [])
        companies_list = companies_data.get("found", [])
        
        # Process jobs
        processed_jobs = []
        for job in jobs_list:
            org = job.get("organization", {})
            processed_job = {
                "job_id": job.get("id"),
                "title": job.get("title"),
                "slug": job.get("slug"),
                "url": job.get("url"),
                "company": {
                    "name": org.get("name"),
                    "slug": org.get("slug"),
                    "logo_url": org.get("logoUrl"),
                },
                "location": {
                    "locations": job.get("locations", []),
                    "work_mode": job.get("workMode"),
                },
                "details": {
                    "seniority": job.get("seniority"),
                    "skills": job.get("skills", []),
                    "created_at": job.get("createdAt"),
                    "featured": job.get("featured", False),
                },
                "compensation": {
                    "min_cents": job.get("compensationAmountMinCents"),
                    "max_cents": job.get("compensationAmountMaxCents"),
                    "currency": job.get("compensationCurrency"),
                    "period": job.get("compensationPeriod"),
                    "offers_equity": job.get("compensationOffersEquity", False),
                }
            }
            processed_jobs.append(processed_job)
        
        # Process companies
        processed_companies = []
        company_index = {}
        for company in companies_list:
            company_data = {
                "company_id": company.get("id"),
                "name": company.get("name"),
                "slug": company.get("slug"),
                "description": company.get("description", ""),
                "logo_url": company.get("logoUrl"),
                "head_count": company.get("headCount"),
                "stage": company.get("stage"),
                "industry_tags": company.get("industryTags", []),
                "locations": company.get("locations", []),
                "topics": company.get("topics", []),
                "active_jobs_count": company.get("activeJobsCount", 0),
            }
            processed_companies.append(company_data)
            company_index[company.get("slug")] = company_data
        
        result = {
            "jobs": processed_jobs,
            "companies": processed_companies,
            "scrape_metadata": {
                "timestamp": self.timestamp,
                "date": datetime.now().isoformat(),
                "jobs_found": len(processed_jobs),
                "jobs_total": jobs_data.get("total", 0),
                "companies_found": len(processed_companies),
                "companies_total": companies_data.get("total", 0),
            }
        }
        
        logger.info("=" * 60)
        logger.info(f"Scraping complete: {len(processed_jobs)} jobs, {len(processed_companies)} companies")
        logger.info("=" * 60)
        
        return result
    
    def save_results(self, data: Dict):
        """Save scraping results to multiple formats"""
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        # Save complete JSON
        json_path = OUTPUT_DIR / f"marvin_jobs_complete_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved complete data to: {json_path}")
        
        # Save jobs JSONL
        jobs_path = OUTPUT_DIR / f"marvin_jobs_{self.timestamp}.jsonl"
        with open(jobs_path, 'w') as f:
            for job in data["jobs"]:
                f.write(json.dumps(job) + '\n')
        logger.info(f"Saved jobs JSONL to: {jobs_path}")
        
        # Save companies JSONL
        companies_path = OUTPUT_DIR / f"marvin_companies_{self.timestamp}.jsonl"
        with open(companies_path, 'w') as f:
            for company in data["companies"]:
                f.write(json.dumps(company) + '\n')
        logger.info(f"Saved companies JSONL to: {companies_path}")
        
        # Create summary
        summary = {
            "scrape_date": data["scrape_metadata"]["date"],
            "total_jobs": data["scrape_metadata"]["jobs_found"],
            "total_companies": data["scrape_metadata"]["companies_found"],
            "top_companies_by_jobs": sorted(
                [{"name": c["name"], "jobs": c["active_jobs_count"]} for c in data["companies"]],
                key=lambda x: x["jobs"],
                reverse=True
            )[:10],
            "files": {
                "complete": str(json_path),
                "jobs": str(jobs_path),
                "companies": str(companies_path),
            }
        }
        
        summary_path = OUTPUT_DIR / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary to: {summary_path}")
        
        print("\n" + "=" * 60)
        print("✓ SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Jobs scraped:      {data['scrape_metadata']['jobs_found']}/{data['scrape_metadata']['jobs_total']}")
        print(f"Companies scraped: {data['scrape_metadata']['companies_found']}/{data['scrape_metadata']['companies_total']}")
        print(f"Output directory:  {OUTPUT_DIR.absolute()}")
        print("=" * 60)
        print("\nTop Companies by Job Count:")
        for i, company in enumerate(summary["top_companies_by_jobs"][:5], 1):
            print(f"  {i}. {company['name']}: {company['jobs']} jobs")
        print()

async def main():
    async with MarvinJobScraper() as scraper:
        try:
            data = await scraper.scrape_all()
            scraper.save_results(data)
        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(main())
