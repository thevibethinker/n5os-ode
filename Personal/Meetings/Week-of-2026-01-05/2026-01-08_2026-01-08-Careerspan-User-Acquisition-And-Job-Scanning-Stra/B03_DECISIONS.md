---
created: 2026-01-08
last_edited: 2026-01-08
version: 1.0
provenance: con_IpOYi8NVNHUaCdBc
block_type: B03
---

# B03: Decisions Made

## Decision 1: Shift focus to Candidate Acquisition over Job Volume

**DECISION:** The team decided to prioritize acquiring "stellar candidates" over rapidly increasing the number of jobs on the platform.
**CONTEXT:** Discussion revealed that scaling jobs without high-quality candidates leads to wasted compute costs ($10k-$15k OpenAI bill potential) with "shitty users" producing no successful hires. High-quality candidates are seen as the necessary foundation for better outcomes and recruiter satisfaction.
**DECIDED BY:** Vrijen Attawar and "Them" (Likely technical lead/co-founder)
**IMPLICATIONS:** Development effort will shift from job-scraping/recruiter-onboarding to user-growth strategies. Scanning logic will likely be limited to the most active users to control costs.
**ALTERNATIVES CONSIDERED:** Supercharging job volume by onboarding external recruiters immediately at a low price point ($100 "punt").

## Decision 2: Cost-Control via User Activity Filtering

**DECISION:** Agreed to limit the job-scanning process to the "most active folks" (e.g., active within the last two months).
**CONTEXT:** To avoid runaway OpenAI costs while scaling, the system needs to narrow the pool of candidates being checked against jobs.
**DECIDED BY:** Vrijen Attawar and "Them"
**IMPLICATIONS:** The scanning algorithm will need a filter for `last_active_at` or similar metadata.

## Decision 3: Pivot User Consent Language to "Recruiter Scouting"

**DECISION:** The UI checkbox text will be changed from a "send me jobs" framing to a "consent to being contacted by recruiters" framing.
**CONTEXT:** This aligns with the "Always being scanned/scouted" value proposition intended to get into users' heads and increase the perceived value of maintaining a profile.
**DECIDED BY:** Vrijen Attawar and "Them"
**IMPLICATIONS:** Requires a frontend text update on the user preferences/settings page.

## Decision 4: Deferral of Development Tasks

**DECISION:** Vrijen is to "hold off" on current development tasks/asks until a pared-down list is provided.
**CONTEXT:** The discussion rendered several previous assumptions/asks obsolete; "Them" needs to review the discussion and provide a refined list of priorities.
**DECIDED BY:** "Them"
**IMPLICATIONS:** Vrijen will pause current technical execution until the updated list is received.