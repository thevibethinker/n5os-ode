---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# Detailed Recap

The conversation is an exploratory partnership call between Careerspan (represented by Vrijen) and Lensa (represented by Mai) focused on testing a jobs distribution and user acquisition partnership.

Vrijen opens with personal introductions and a quick location check-in before explaining Careerspan’s model: a talent network built by embedding a free consumer coaching product inside high‑signal professional communities (e.g., McKinsey alumni, ex‑Googlers, Ivy alumni). Users complete reflective career stories that generate a rich data set beyond resumes, enabling precise job matching and very high engagement rates on recommendations.

Mai explains Lensa’s model: an American job board aggregator monetizing via clients who pay to distribute jobs. Lensa serves about 24–25 million jobs from a mix of organic scraped roles (Fortune 1000), direct agency employers, ATS feeds, and other job boards. Their core revenue driver is getting job seekers to register for alerts, which produces monetizable traffic through email and push notifications.

The discussion then dives into whether Careerspan could both ingest Lensa jobs and send Lensa new, high‑quality job seekers. Mai outlines that Lensa typically buys traffic via job board partners and uses XML feeds, a jobs API, and co‑registration flows. She proposes paying Careerspan on a CPC/CPA basis for users that register with Lensa.

Vrijen stresses that Careerspan prioritizes precision over volume: their matching engine and rich data give them 75–80% open rates and ~15–16% click‑through on recommendations, but this also means lower raw traffic. He suggests Lensa may need to evaluate performance on quality rather than pure click volume, with some flexibility in thresholds if needed.

They converge on a test plan: start by pulling a subset of Lensa’s jobs (initially product roles in Boston, SF, and NYC) via XML/API, routing application paths to Lensa so tracking is straightforward. Careerspan will send a smaller but highly qualified stream of candidates from its high‑engagement user base.

Mai explains the operational setup: Careerspan will be registered as an Appcast “master publisher,” receive XML feeds, and run an initial test at a $0.15 CPC with a $2,500 starting budget per feed. Lensa will assign two analysts (for direct content and lead‑gen content) to monitor how Careerspan’s traffic performs against ROI metrics and advise where to scale up or down.

They align that, to reduce processing load on Careerspan’s current, cost‑inefficient V1 matching system, Lensa can provide filtered feeds by job category (starting with product) so Careerspan is not ingesting millions of jobs at once. Careerspan will initially target ~70–80 jobs per week distributed to 700–1,000 highly engaged users, then grow both job volume and user base as the system matures.

The call closes with agreement that the test will likely start in October. Mai will send follow‑up information and IO details, set up the Appcast publisher account, and introduce the analysts. Both sides express enthusiasm, with Careerspan excited about access to a large, clean job feed and Lensa eager to tap into a fresh, highly engaged candidate pool.
