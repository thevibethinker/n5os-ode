---
created: 2026-01-03
last_edited: 2026-01-03
version: 1.0
provenance: con_D5JBTmq0a3sYOBrE
block_type: B12
semantic_enrichment: true
---

# B12: Technical Infrastructure

## Technical Summary

| Field | Value |
|-------|-------|
| **Partner** | Lensa |
| **Integration Type** | XML Feed / Jobs API / Appcast |
| **Complexity** | Moderate |
| **Feasibility** | Confirmed (Pilot phase) |

---

## Section 1: Technologies Discussed

### Their Current Stack
| Category | Technology | Notes |
|----------|------------|-------|
| **Platform** | Lensa (Job Board Aggregator) | 25M+ active job listings |
| **Data Source** | XML Feeds / Scraping | Scrapes Fortune 1000, ATS, and direct agencies |
| **Distribution** | Appcast | Primary channel for publisher distribution |
| **APIs** | Jobs API | Alternative to XML feeds for dynamic pulling |

### Proposed Integration Stack
| Component | Technology | Status |
|-----------|------------|--------|
| **Job Intake** | XML Feed / API | To Build (Careerspan side) |
| **Distribution** | Appcast | Existing (Lensa) / Needs Setup (Careerspan) |
| **Tracking** | CPC / CPA Tracking | To Build (Attribution via Appcast) |

### Data Formats
- **Inbound:** XML (standard job board format) or JSON (via Jobs API).
- **Outbound:** Click-through data via tracked URL parameters (traceability back to Careerspan).
- **Transformation needed:** Yes - Careerspan needs to parse Lensa XML to extract "clean" JDs and match to talent profiles.

---

## Section 2: Integration Requirements

### Data Flows
```
Lensa/Appcast → XML Feed → Careerspan Parser → Matching Engine → Candidate Recommendation → Candidate Click → Lensa Landing Page/Apply Path
```

**Flow Description:**
- **Direction:** Bi-directional (Jobs flow to Careerspan; traffic/conversion data flows back to Lensa).
- **Data types:** Job descriptions, metadata (location, salary, title), tracking IDs.
- **Frequency:** Weekly initially (as requested by Vrijen), scaling to real-time.
- **Volume:** ~70–80 jobs/week for pilot; 200–300 jobs/week post-expansion.

### Processing Model
| Aspect | Requirement | Notes |
|--------|-------------|-------|
| **Timing** | Batch (Weekly) | Vrijen mentioned pulling once a week for initial pilot. |
| **Latency** | 3-day recency | Careerspan prefers roles posted within the last 3 days. |
| **Throughput** | High Potential | Access to 24M jobs; needs filtering for Product/Eng. |

### Authentication & Security
- **Auth method:** Appcast Master Publisher credentials.
- **Security requirements:** Standard API key/secure endpoint access for XML feeds.
- **Data handling:** No PII discussed for initial job intake; conversion tracking requires anonymous ID persistence.

---

## Section 3: Technical Feasibility ⭐ MEMORY-ENRICHED

### Assessment
| Dimension | Rating | Notes |
|-----------|--------|-------|
| **Overall Difficulty** | Moderate | Standard industry patterns (XML/Appcast) but requires parsing logic. |
| **Timeline Impact** | 2-4 Weeks | Setup for Appcast account and XML ingestion script. |
| **Resource Requirements** | Medium | Engineering needed for "clean" JD extraction and matching integration. |

### Key Blockers
| Blocker | Severity | Resolution Path |
|---------|----------|-----------------|
| Appcast Setup | Low | Mei to provide Master Publisher account details. |
| Parser Cost | Med | V1 matching is cost-inefficient; needs optimization for larger feeds. |

### Dependencies
- **Must happen first:** Appcast account creation and IO signing.
- **Parallel workstreams:** Developing the XML ingestion script while Lensa prepares the filtered (Product) feed.

---

## Section 4: Implementation Architecture

### Proposed Approach
**Primary option: XML Feed via Appcast**
- **Pros:** Robust, industry-standard, allows Lensa to "cut down" files to specific categories (Product).
- **Cons:** Slightly higher overhead than simple API requests for small volumes.

**Alternative approaches discussed:**
1. **Jobs API** - More dynamic, better for real-time, but requires more complex integration than a standard feed.

---

## Section 5: Infrastructure Implications

### Data & Storage
- **Data storage:** Careerspan will need to cache the Lensa job pool to run matching algorithms locally.
- **Retention needs:** Jobs should be purged or updated frequently to ensure candidates aren't applying to stale links.

### Scalability
- **Current scale:** 700–1000 activated users on Careerspan.
- **Growth expectations:** Onboarding 200–400 users/week; community-per-week strategy.
- **Our capacity:** Current matching engine (V1) is inefficient; scale will require technical upgrades.

---

## Section 6: Action Items

### Technical Next Steps
| Action | Owner | Timeline | Dependency |
|--------|-------|----------|------------|
| Set up Master Publisher account | Mai Flynn | Oct 2025 | None |
| Provide XML Feed/API Specs | Lensa Analysts | Post-IO | IO Signing |
| Build XML Intake/Parser Script | Careerspan Eng | 2 weeks | Account setup |

### Questions for Engineering
- [ ] Can we efficiently parse and store a "cut down" XML feed for 1,000+ roles?
- [ ] What is the current bottleneck in the "cost-inefficient" V1 matching system?

---

## Cross-References

- **B09 (Collaboration Terms):** $0.15 CPC, $2,500 initial budget per feed.
- **B13 (Plan of Action):** Pilot test start targeted for October.
- **B24 (Product Ideas):** Filtering by Product/Engineering and specific geos (SF, NY, Boston).

---
**Feedback**: - [ ] Useful
---[^1]

[^1]: Based on transcript 2025-09-24_Lensa-Partnership-exploration-pilot-Partnership

2026-01-03 12:28:15 ET