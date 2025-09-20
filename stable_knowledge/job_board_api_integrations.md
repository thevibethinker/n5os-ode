# Job Board API Integrations Knowledge Base

This knowledge base documents API integration protocols for major job boards we work with, to enable direct programmatic access to job postings and related data.

---

## ADP Workforce Now
- **API Central:** https://developers.adp.com/build/api-explorer/hcm-offrg-wfn
- **Description:** Worker Management API allowing access and management of workforce data.
- **Authentication:** Requires account/API keys.
- **Endpoints:** Worker profiles, jobs, locations, time-off, etc.
- **Notes:** Comprehensive docs with examples.
- **Account Required:** Yes

## Greenhouse.io
- **API Documentation:** https://developers.greenhouse.io/harvest.html
- **Description:** Harvest API providing endpoints for job posts, candidates, applications.
- **Authentication:** OAuth token-based.
- **Features:** Pagination, webhooks, attachments.
- **Account Required:** Yes

## SmartRecruiters
- **API Docs:** https://developers.smartrecruiters.com/docs/oauth-20-general-partner-integration
- **Description:** OAuth 2.0 APIs for ATS data sync, job postings, candidate info.
- **Authentication:** OAuth 2.0 (Client Credential Flow).
- **Account Required:** Yes

## Lever
- **API Info:** https://help.lever.co/hc/en-us/articles/20087346449437-Lever-career-site-options
- **Description:** Postings API for job listings, application data.
- **Authentication:** API keys / OAuth.
- **Account Required:** Yes

## Apple
- **Documentation:** https://developer.apple.com/documentation/
- **Notes:** No public job board API found. Mostly device, business management.
- **Account Required:** Possibly for private APIs

---

### Notes and Instructions
- Setup accounts where needed and obtain API credentials.
- Implement OAuth flows for Greenhouse, SmartRecruiters, Lever.
- Handle API rate limits and pagination.
- Use webhooks for real-time updates where available.
- This document should be updated with new provider protocols and access details as they are discovered.

---

_Last updated: 2025-09-20_
