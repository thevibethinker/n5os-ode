# Marvin Ventures Job Board Scraping Analysis

**Date:** 2025-10-30
**Job Board:** https://jobs.marvinvc.com/companies
**Platform:** Powered by Getro

## Summary

Yes, I **can programmatically scrape** this job board, but with important caveats.

### Current Status

- ✅ Companies page accessible
- ✅ Jobs page accessible
- ⚠️ API blocked - Direct API returns message to contact api@getro.com
- ⚠️ Lazy loading - Only 20/397 jobs load initially
- ⚠️ Pagination required - Need browser automation

### What I Found

**Total Data:**
- **22 companies** (12 loaded initially)
- **397 total jobs** (20 loaded initially)

**Sample job structure includes:** title, company, locations, work mode, seniority, compensation, skills, url

## Recommended Approach: Browser Automation

Build Playwright-based scraper that:
1. Opens /jobs page in headless browser
2. Scrolls/clicks Load More until all 397 jobs visible
3. Extracts full __NEXT_DATA__ JSON
4. Exports to JSON/CSV

**Time:** ~2-3 minutes
**Success rate:** Very high

Would you like me to build this?
