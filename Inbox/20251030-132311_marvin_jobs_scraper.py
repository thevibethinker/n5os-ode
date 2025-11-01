#!/usr/bin/env python3
"""Marvin Ventures Job Board Scraper - Browser Automation"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Page, Browser

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://jobs.marvinvc.com"
OUTPUT_DIR = Path("/home/workspace/marvin_jobs_data")
TIMEOUT = 30000

class MarvinJobScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        if self.browser:
            await self.browser.close()
    
    async def extract_next_data(self, page: Page) -> Dict:
        try:
            data = await page.evaluate("""() => {
                const scriptTag = document.getElementById('__NEXT_DATA__');
                if (scriptTag) {
                    return JSON.parse(scriptTag.textContent);
                }
                return null;
            }""")
            return data
        except Exception as e:
            logger.error(f"Failed to extract __NEXT_DATA__: {e}")
            return None
    
    async def load_all_jobs(self, page: Page) -> None:
        logger.info("Loading all jobs by scrolling...")
        previous_count = 0
        no_change_count = 0
        max_attempts = 50
        
        for attempt in range(max_attempts):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
            
            try:
                load_more = await page.query_selector('button:has-text("Load more")')
                if load_more:
                    logger.info(f"Clicking 'Load more' button (attempt {attempt + 1})")
                    await load_more.click()
                    await asyncio.sleep(2)
            except Exception:
                pass
            
            current_count = await page.evaluate("""() => {
                return document.querySelectorAll('[data-cy="job-card"], article, .job-item').length;
            }""")
            
            logger.info(f"Attempt {attempt + 1}: {current_count} jobs visible")
            
            if current_count == previous_count:
                no_change_count += 1
                if no_change_count >= 3:
                    logger.info("No new jobs loaded after 3 attempts, stopping")
                    break
            else:
                no_change_count = 0
            
            previous_count = current_count
        
        logger.info(f"Finished loading: {previous_count} jobs visible in DOM")
    
    async def scrape_jobs_page(self) -> Dict:
        logger.info("Starting browser automation...")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            page = await self.browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"Navigating to {BASE_URL}/jobs")
            await page.goto(f"{BASE_URL}/jobs", wait_until="networkidle", timeout=TIMEOUT)
            await asyncio.sleep(2)
            await self.load_all_jobs(page)
            
            logger.info("Extracting __NEXT_DATA__ from page...")
            data = await self.extract_next_data(page)
            if not data:
                raise ValueError("Failed to extract data from page")
            return data
    
    async def scrape_companies_page(self) -> Dict:
        logger.info("Scraping companies page...")
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            page = await self.browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info(f"Navigating to {BASE_URL}/companies")
            await page.goto(f"{BASE_URL}/companies", wait_until="networkidle", timeout=TIMEOUT)
            await asyncio.sleep(2)
            
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            
            data = await self.extract_next_data(page)
            return data
    
    def parse_job(self, job: Dict, company_lookup: Dict[str, Dict]) -> Dict:
        org = job.get("organization", {})
        org_id = org.get("id", "")
        company_info = company_lookup.get(org_id, {})
        
        return {
            "id": job.get("id"),
            "title": job.get("title"),
            "slug": job.get("slug"),
            "url": job.get("url"),
            "created_at": job.get("createdAt"),
            "company": {
                "id": org_id,
                "name": org.get("name"),
                "slug": org.get("slug"),
                "description": company_info.get("description", ""),
                "logo_url": org.get("logoUrl"),
                "head_count": company_info.get("headCount"),
                "stage": company_info.get("stage"),
                "industry_tags": company_info.get("industryTags", []),
            },
            "location": {
                "locations": job.get("locations", []),
                "searchable_locations": job.get("searchableLocations", []),
                "location_details": job.get("locationDetails"),
                "work_mode": job.get("workMode"),
            },
            "compensation": {
                "min_cents": job.get("compensationAmountMinCents"),
                "max_cents": job.get("compensationAmountMaxCents"),
                "currency": job.get("compensationCurrency"),
                "period": job.get("compensationPeriod"),
                "offers_equity": job.get("compensationOffersEquity"),
            },
            "details": {
                "seniority": job.get("seniority"),
                "skills": job.get("skills", []),
                "has_description": job.get("hasDescription"),
                "featured": job.get("featured"),
            },
            "scraped_at": datetime.now().isoformat(),
        }
    
    async def scrape_all(self) -> Dict:
        logger.info("=" * 60)
        logger.info("Starting Marvin Ventures Job Board Scrape")
        logger.info("=" * 60)
        
        jobs_data = await self.scrape_jobs_page()
        jobs_raw = jobs_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("jobs", {})
        jobs_found = jobs_raw.get("found", [])
        jobs_total = jobs_raw.get("total", 0)
        
        logger.info(f"Jobs extracted: {len(jobs_found)} / {jobs_total} total")
        
        companies_data = await self.scrape_companies_page()
        companies_raw = companies_data.get("props", {}).get("pageProps", {}).get("initialState", {}).get("companies", {})
        companies_found = companies_raw.get("found", [])
        companies_total = companies_raw.get("total", 0)
        
        logger.info(f"Companies extracted: {len(companies_found)} / {companies_total} total")
        
        company_lookup = {c["id"]: c for c in companies_found}
        parsed_jobs = [self.parse_job(job, company_lookup) for job in jobs_found]
        
        return {
            "scrape_metadata": {
                "timestamp": datetime.now().isoformat(),
                "base_url": BASE_URL,
                "jobs_extracted": len(parsed_jobs),
                "jobs_total": jobs_total,
                "companies_extracted": len(companies_found),
                "companies_total": companies_total,
            },
            "jobs": parsed_jobs,
            "companies": companies_found,
            "raw_data": {
                "jobs_page": jobs_data,
                "companies_page": companies_data,
            }
        }
    
    def save_results(self, data: Dict) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        full_path = OUTPUT_DIR / f"marvin_jobs_full_{self.timestamp}.json"
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved full data to: {full_path}")
        
        jobs_path = OUTPUT_DIR / f"marvin_jobs_{self.timestamp}.jsonl"
        with open(jobs_path, 'w') as f:
            for job in data["jobs"]:
                f.write(json.dumps(job) + '\n')
        logger.info(f"Saved jobs JSONL to: {jobs_path}")
        
        companies_path = OUTPUT_DIR / f"marvin_companies_{self.timestamp}.json"
        with open(companies_path, 'w') as f:
            json.dump(data["companies"], f, indent=2)
        logger.info(f"Saved companies to: {companies_path}")
        
        summary = {
            "timestamp": data["scrape_metadata"]["timestamp"],
            "totals": {
                "jobs": data["scrape_metadata"]["jobs_extracted"],
                "jobs_total_on_site": data["scrape_metadata"]["jobs_total"],
                "companies": data["scrape_metadata"]["companies_extracted"],
            },
            "files": {
                "full_data": str(full_path.name),
                "jobs_jsonl": str(jobs_path.name),
                "companies": str(companies_path.name),
            },
            "top_companies_by_jobs": sorted(
                [{"name": c["name"], "jobs": c["activeJobsCount"]} 
                 for c in data["companies"]],
                key=lambda x: x["jobs"],
                reverse=True
            )[:10]
        }
        
        summary_path = OUTPUT_DIR / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary to: {summary_path}")
        
        print("\n" + "=" * 60)
        print("✓ SCRAPING COMPLETE")
        print("=" * 60)
        print(f"Jobs scraped:      {data['scrape_metadata']['jobs_extracted']}")
        print(f"Jobs total:        {data['scrape_metadata']['jobs_total']}")
        print(f"Companies scraped: {data['scrape_metadata']['companies_extracted']}")
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
