#!/usr/bin/env python3
"""
Fallback Scraper Module
Adds support for scraping job postings from dynamic or unknown ATS systems
Uses requests + BeautifulSoup with retry/backoff
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import List, Dict


class FallbackScraper:
    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    def __init__(self, base_url: str):
        self.base_url = base_url

    def scrape_jobs(self) -> List[Dict[str, str]]:
        jobs = []
        retries = 3
        backoff = 2
        for _ in range(retries):
            try:
                response = requests.get(self.base_url, headers=self.BASE_HEADERS, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                # Example: find job postings
                # Each implementation is site specific
                job_elems = soup.select(".job-listing, .job-posting, [class*=job]")
                for elem in job_elems:
                    title_elem = elem.select_one(".job-title, h2, a")
                    location_elem = elem.select_one(".location, .job-location")
                    link_elem = elem.select_one("a")

                    job = {
                        "title": title_elem.get_text(strip=True) if title_elem else "",
                        "location": location_elem.get_text(strip=True) if location_elem else "",
                        "url": link_elem["href"] if link_elem and "href" in link_elem.attrs else self.base_url,
                        "company": self.base_url.split("//")[-1].split(".")[0],
                    }
                    jobs.append(job)
                return jobs
            except Exception as e:
                print(f"Fallback scraper error: {e}, retrying in {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
        return jobs


if __name__ == "__main__":
    scraper = FallbackScraper("https://example.com/careers")
    results = scraper.scrape_jobs()
    print(results)
