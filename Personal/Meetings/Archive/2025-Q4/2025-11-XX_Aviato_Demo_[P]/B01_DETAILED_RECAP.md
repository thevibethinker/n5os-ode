---
created: 2025-11-28
last_edited: 2025-11-28
version: 1.0
---

# Detailed Recap

This meeting is a product demo and exploration session between Vrijen (Careerspan/Zo user) and the Aviato team (Konrad, co‑founder; Austin, growth lead). Vrijen came in with two overlapping agendas: (1) understand Aviato’s people‑data API for his personal CRM + meeting‑intelligence stack on Zo, and (2) explore whether Aviato could power more targeted outreach and networking for Careerspan.

After brief introductions, Vrijen explains how Careerspan uses conversational coaching to collect rich stories from candidates, then turns those narratives into better hiring signals. He sketches a possible Careerspan + Aviato integration: using Aviato’s data (vesting schedules, open‑to‑work flags, movement patterns) to discover high‑leverage candidates and then using Careerspan’s narrative engine to help those people present themselves and connect to employers.

Austin then gives a high‑level overview of Aviato. The platform maintains data on ~1.1 billion people and ~72 million companies, delivered via API or flat files. They support a wide array of data points (company, role, compensation estimates, vesting data, open‑to‑network flags, social profiles, etc.) and refresh them on a tiered cadence (decision‑makers and high‑value professionals updated first). Customers span VCs and family offices (for investment signals), AI agents and automation tools (including recruiting use cases), and niche providers who resell enriched data.

They dive into concrete recruitment signals. Aviato can identify executives, founders, or engineers who are at their equity cliffs (e.g., end of four‑year vesting), people who have ended a role but not yet started the next within a defined window, and candidates who are flagged as "open" in LinkedIn’s settings but don’t show the public green banner. Combined, these signals give a powerful way to detect when someone is likely to be receptive to outreach.

Vrijen connects this to prior thinking about an "AI talent agency" model: because Careerspan knows a lot about each candidate from their stories and sees organic reactivation over time, it could use Aviato’s quantitative signals to decide when to nudge those candidates ("you’re about to vest—this is a good time to tell your story and explore options"). Similarly, for his personal CRM, he imagines a Zo + n8n + Aviato pipeline that enriches meeting contacts, tracks promotions, and surfaces introduction opportunities across his network.

As the call wraps, Austin outlines how integration works in practice: they configure which data sets and fields Vrijen needs, provide an API key, and allow queries that can either fetch a single profile or generate lists based on criteria. Flat‑file customers can receive initial full dumps followed by diffs; API customers can choose refresh cadences according to budget and needs. Austin provisions a test account (100 people + 100 company credits, no time limit) and offers to extend it if necessary, while Vrijen commits to testing Aviato with Zo, introducing Aviato to the Zo founders, and showcasing any interesting use cases in the Zo community.

