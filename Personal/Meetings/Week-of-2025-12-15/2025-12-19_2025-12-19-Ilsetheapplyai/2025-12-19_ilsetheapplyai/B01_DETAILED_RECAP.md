---
created: 2025-12-23
last_edited: 2025-12-23
version: 1.0
provenance: con_hJHsDQzomPn81e4Z
---

# B01 Detailed Recap: Darwinbox Prep & Product Strategy

## Session Overview
This was a pre-meeting sync between **Vrijen Attawar (V)** and **Ilse Funkhouser** to prepare for an upcoming call with Darwinbox. The discussion focused on understanding Darwinbox's position as a "non-normal" customer, technical trade-offs to improve user experience, and managing data fidelity versus collection speed.

## 1. Darwinbox Meeting Preparation
*   **Context:** V initially thought the preparation notes for Darwinbox were for his personal use, but confirmed the meeting includes Darwinbox's founder (CH) and product team.
*   **Customer Profile:** Darwinbox is characterized as a high-tier HR tech provider for large multinationals in regions like India and Cambodia. While they operate at a "lower end" of the SaaS spectrum in terms of complexity, they face the same acute problems as US companies (e.g., ChatGPT-generated resumes).
*   **Strategic Angle:** Darwinbox is valued at approximately $1 billion and is investing heavily in the US to diversify its tech options. V suspects they are looking for alternative technology to handle high-volume processing challenges.

## 2. Product Experience & Data Collection Levers
*   **The "T-Shaped" Collection Proposal:** Ilse suggested a "T-shaped" approach to storytelling/data collection: gathering a quick top-level "STAR" (Situation, Task, Action, Result) basics first, then drilling deep selectively.
*   **Reducing Friction:** Ilse proposed reducing the number of required questions (currently at nine) to shorten completion time. 
*   **Data Reusability:** Ilse noted that while situational information is tentatively reusable, culture-related data is not. They discussed the tension between collecting "high-fidelity information" and the user's desire for a faster process.
*   **"Slow Burn" vs. Immediate Needs:** V noted that while "business journaling" (weekly incremental data collection) is the ideal long-term direction, users are currently not ready for it, necessitating a more immediate solution for data intake.

## 3. Infrastructure and Cost Decisions
*   **OpenAI Priority Queue:** Ilse proposed moving application processing (which currently takes 10–15 minutes) to OpenAI's priority queue.
*   **Cost vs. UX:** This change could potentially double application processing costs. V made an executive decision to prioritize user experience over cost at this stage, as the company is focused on selling rather than mass growth.

## 4. Technical Roadmap & Behavioral Tracking
*   **User Behavior Tracking:** Ilse identified a "clutch" in the signup process where they cannot accurately track where users come from or their behavior prior to signing up.
*   **Prioritization:** Despite the need for better stats/tracking, the team decided that improving the immediate user experience and fixing the application process takes priority over fixing behavioral analytics.

## 5. Logistics & Next Steps
*   **Platform:** The upcoming meeting is hosted on Microsoft Teams. V confirmed there is a web version available to avoid installation issues.
*   **Action Items:**
    *   Ilse will check if users are voluntarily continuing past the required 9-question minimum (contributing to perceived slowness).
    *   Ilse will test the Microsoft Teams connection before the Darwinbox call starts.
    *   Transition processing to OpenAI priority queue to shave off latency.

***

**Date:** December 23, 2025
**Time:** 08:35 AM ET