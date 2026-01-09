---
created: 2026-01-06
last_edited: 2026-01-06
version: 1.0
provenance: 074838b3-3b6f-4e5c-a843-858a7d072141
block_type: B03
---

# B03: Decisions Made

## Decision 1: Direct API Integration for Fathom

**DECISION:** Integrate Fathom transcripts directly into Zo via API rather than using Zapier or web browser agents.
**CONTEXT:** David was initially using a Zapier trial to move transcripts to Google Drive. Vrijen recommended a direct API approach to save costs (Zapier trial expiration), increase reliability, and store data locally on Zo for better post-processing.
**DECIDED BY:** David Speigel (with recommendation from Vrijen Attawar)
**IMPLICATIONS:** David added Fathom API keys and webhook secrets to Zo's developer settings; future meeting workflows will be handled locally on Zo.
**ALTERNATIVES CONSIDERED:** Web browser agent navigation (dismissed as "so so"), Zapier (dismissed due to eventual cost), and N8N (mentioned as a free self-hosted alternative).

## Decision 2: Model Selection for Development Tasks (GLM 4.0/4.7)

**DECISION:** Use the GLM 4.7 model for the initial Fathom integration and development planning.
**CONTEXT:** To manage costs while maintaining high performance, Vrijen suggested GLM 4.7 as a "good value" alternative that is nearly as capable as GPT-4/Opus but significantly cheaper.
**DECIDED BY:** Vrijen Attawar (approved by David Speigel)
**IMPLICATIONS:** David switched his chat model to GLM to execute the integration plan.
**ALTERNATIVES CONSIDERED:** GPT-4/Opus (deemed too expensive for this phase), GPT 5.1 Codex Mini (identified as an unreliable fallback model during a glitch).

## Decision 3: Standardized Meeting Folder Structure

**DECISION:** Implement a "Personal/Meetings/Inbox" directory structure for transcript ingestion.
**CONTEXT:** Vrijen advised creating a dedicated "Inbox" for arriving transcripts to allow for a "staging area" where AI can process and analyze data before filing it away.
**DECIDED BY:** Vrijen Attawar (accepted by David Speigel)
**IMPLICATIONS:** The integration script was instructed to define and use these specific paths; meetings will be stowed in a separate processed folder after the "Inbox" stage.

## Decision 4: Incorporation of Power User Rules

**DECISION:** David decided to incorporate Vrijen's "V-OS" and "Power User" behavioral rules into his Zo system.
**CONTEXT:** To improve Zo's reliability and follow "Simple > Easy" principles (e.g., preferring small reversible changes), David copied and sent a comprehensive list of rules provided by Vrijen to his Zo.
**DECIDED BY:** David Speigel
**IMPLICATIONS:** David's Zo persona/system behavior will now adhere to these updated constraints and logic.

## Decision 5: Use of 23andMe Data for Health Queries

**DECISION:** David will export his 23andMe genomic data and add it to Zo as a dataset.
**CONTEXT:** After Vrijen shared how he uses his genetic profile to understand workout recovery and supplement needs (tirzepatide/GLP-1 context), David agreed to load his own data to enable similar health queries.
**DECIDED BY:** David Speigel
**IMPLICATIONS:** Zo will gain access to David's genomic data for personalized health and performance analysis.