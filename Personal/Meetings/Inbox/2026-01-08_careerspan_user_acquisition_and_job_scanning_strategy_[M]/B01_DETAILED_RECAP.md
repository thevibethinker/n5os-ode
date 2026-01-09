```yaml
---
created: 2026-01-08
last_edited: 2026-01-08
version: 1.0
provenance: con_dhZUpomKavUBoQIQ
---
```

# B01: Detailed Recap - Careerspan User Acquisition and Job Scanning Strategy

## Executive Summary
Vrijen (Me) and a team member (Them) discussed a strategic shift for Careerspan focusing on recruiter-led job acquisition and the technical/financial implications of scaling the job scanning engine. The core tension lies between Vrijen’s desire to "supercharge" job volume by charging recruiters a small fee ($100 punt) to surface candidates and the team's concern regarding the high compute costs (OpenAI bills) and the current quality of the candidate pool. The session concluded with a decision to pivot towards high-quality user acquisition and refined consent mechanisms before scaling job ingestion.

## Strategic Discussion Points
- **Recruiter Monetization Model**: Vrijen proposed a low-friction entry point for recruiters—charging ~$100 to surface candidates for roles they are struggling to fill. This is positioned as a complement/alternative to the $300-$400/month LinkedIn Recruiter seats which Vrijen characterizes as having "dubious value." [^1]
- **Compute Economics**: "Them" highlighted that running 60 jobs against 300 people currently costs approximately $400. The cost is a function of "stories told" per user and "backbees" (internal scanning logic). As the system scales to hundreds of jobs, the team warned of potential $10,000–$15,000 OpenAI bills if not managed carefully. [^1]
- **Candidate Quality vs. Job Quantity**: A critical risk was identified: scaling jobs without "stellar candidates" leads to wasted compute. The team argued that the current user base may contain "shitty users" (location/industry mismatches), making it riskier to focus on jobs over users. [^1]
- **The "Always Scouting" Hook**: To drive user engagement, Vrijen suggested lean messaging changes to the UI, shifting from "Send me jobs" to "Consent to being scouted/contacted by recruiters." [^1]

## Technical & Operational Constraints
- **Scanning Logic**: Cost efficiency improves if the number of applicants remains low relative to job volume.
- **Activity Filtering**: A proposed mitigation for cost is limiting scans to users active within the last two months.
- **UI Pivot**: The team confirmed the ability to swap the job-match checkbox for a "recruiter consent" conceptual model.

## Action Items & Next Steps
- **Recruiter Outreach**: Vrijen to speak with "Lodes" (Logan) to compile a list of recruiters for the $100 pilot program. [^1]
- **Task Freeze**: "Them" requested Vrijen hold off on current technical tasks until a "pared down list of asks" is provided based on these new strategic priorities. [^1]
- **Financial Planning**: Vrijen indicated a willingness to cover short-term OpenAI spikes via credit card to prove the model, though a long-term sustainability plan is required. [^1]

## Decisions Made
1. **Prioritize User Quality**: Focus on bringing in "stellar" users over massive job ingestion in the immediate term to ensure ROI on scanning costs.
2. **Messaging Shift**: Transition UI language to emphasize being "scouted" to improve user "get-in-the-head" psychology.
3. **Pilot Recruiter Fee**: Move forward with investigating a low-cost, one-off fee structure for recruiters to list jobs and access surfaced candidates.

[^1]: Transcript of meeting "Careerspan user acquisition and job scanning strategy", Calendar ID: c303f988-e8b6-45aa-9a9d-2d3e40a02187.

2026-01-08 12:20:00 ET