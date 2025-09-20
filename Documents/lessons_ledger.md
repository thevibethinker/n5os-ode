# Lessons Learned Ledger

## Overall Process
- **Adaptability Required**: When initial approaches fail (e.g., ATS detection, API parsing), immediately pivot to backup strategies like direct scraping. Don't persist with broken methods.
- **Technical Hurdles**: Many ATS systems use dynamic content, redirects, or browser checks that block simple HTTP requests. Always test assumptions with real data.
- **Data Quality Tradeoffs**: Summaries are faster but lose nuance; full descriptions preserve intent but require more processing/storage.
- **Automation Limits**: Human extraction is reliable for one-off tasks, but scalable solutions need NLP or structured parsing.
- **Security/Privacy**: Handling job data involves PII risks; keep credentials secure and avoid logging sensitive info.

## SourceStack API Integration
- **API Basics**: X-API-KEY header works for auth; /jobs endpoint supports advanced filters (field/operator/value). GET with URL-encoded filters or POST with JSON body.
- **Query Construction**: Complex filters (e.g., job_name CONTAINS_ANY "product manag") require precise JSON. Curl issues with JSON; Python aiohttp more reliable.
- **Limitations**: Only covers recent jobs (last 3D); no full descriptions in API response—URLs provided for further scraping.
- **Success Rate**: 100% API success once key/auth resolved; data extraction straightforward but limited.

## Job Ingestion Pipeline Development
- **ATS Detection Flaws**: Pattern-matching for careers pages often fails due to non-standard URLs or redirects. Need broader heuristics or manual overrides.
- **Client Implementation Gaps**: Regex parsing works for simple HTML but breaks on dynamic sites. BeautifulSoup helps, but JS-rendered content requires Selenium.
- **Fallback Importance**: Generic scraper essential when ATS-specific clients fail. Always include a "catch-all" method.
- **Rate Limiting**: Respectful delays prevent blocking; configurable per ATS.
- **Data Storage**: JSONL for raw logs, JSON for structured; separate directories for organization.

## Direct Job Scraping
- **Content Clipping Needed**: Full scraped job descriptions contain excessive boilerplate (navigation menus, footers, unrelated site content). Implement LLM-based intelligence to clip to core job text only (responsibilities, qualifications, pay, etc.), dropping miscellaneous bits for cleaner data.
- **Success Rate**: 3/5 jobs scrape cleanly with read_webpage; failures due to redirects/homepage loads (Greenhouse), browser checks (ADP), or custom systems.
- **Extraction Challenges**: Manual summarization loses nuance; automated parsing requires NLP or LLM to identify relevant sections.
- **Data Preservation**: Full content saved to conversation workspace; accessible for review but not user-visible without tools.
- **Tool Choice**: read_webpage suffices for static pages; for dynamic, need headless browser (e.g., Selenium with Chrome).

## Workflow and System Integration
- **Component Disconnection**: Workflow parts don't connect well—API fetching, pipeline ingestion, direct scraping, and data export (e.g., to Google Sheets) require manual handoffs, format conversions, and separate scripts. Need end-to-end orchestration for seamless flow.
- **Version Control**: Git tracking works for code/docs; exclude sensitive files (credentials) via .gitignore.
- **Error Handling**: Log failures clearly; retries help, but don't waste time on fundamentally broken approaches.
- **User Feedback Loop**: Clarify requirements early (e.g., full vs. summary); avoid assumptions about technical savvy.
- **Resource Management**: Clean up temp files; keep workspace organized to avoid clutter.
- **Scalability Considerations**: One-off scraping is fine; for bulk, implement parallel processing and error recovery.

## Job Description Requirements
- **Complete Job Descriptions Mandatory**: The workflow must always extract and include the full, verbatim job description text in exports (CSV, Sheets, JSON). Partial, summarized descriptions cause loss of critical context and reduce usefulness.
- Need mechanisms to clean and intelligently clip irrelevant boilerplate while preserving all primary content.
- This is prioritized as a core correction for production-ready ingest pipeline.

## Future Improvements
- Implement headless browser scraping for dynamic pages.
- Add NLP for automated job detail extraction from full descriptions.
- Expand ATS support: ADP, Greenhouse API, SmartRecruiters API, etc.
- Build job deduplication and enrichment pipeline.
- Integrate with user workflow (e.g., save to N5 system).