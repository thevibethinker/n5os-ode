---
created: 2025-12-15
last_edited: 2025-12-15
version: 1.0
---

# B03 – Decisions

1. **Defer configurable job-analysis endpoint**
   - Ilse proposed an endpoint-driven tool to let users specify custom emphasis for job analyses.
   - V confirmed there is no strong user pull yet; minor configuration can be handled manually.
   - **Decision:** Do **not** prioritize this tool in the near term. Engineering focus stays on improving conversation UX and user chats.

2. **Use spreadsheet + selective endpoints for analytics (no full automation yet)**
   - V wants clear visibility into views, applies, and onboarding completion, particularly for design partners like David (Skillcraft).
   - Ilse explained that fully-automatic rollups across all employers would be expensive given the current Firebase-style data model.
   - **Decision:** Accept the current pattern of:
     - Manually generated spreadsheets from analytics data, and
     - (When needed) a targeted endpoint that can regenerate per-employer reports.
     Automation of global rollups is intentionally postponed until the data architecture is refactored.

3. **Constrain analytics usage to manage read costs**
   - Ilse highlighted that running rich analytics across ~1,000+ views could add non-trivial read costs.
   - **Decision:** Treat heavy analytics runs as **explicit, infrequent operations**, filtered to specific employers or experiments. V will avoid scheduling large, frequent full-universe runs until cost controls and rollups exist.

4. **Greenlight Ilya’s 1:1 LinkedIn outreach campaign**
   - Ilya proposed personally messaging his recruiter/hiring-manager connections to introduce Careerspan and its December offers.
   - **Decision:** Proceed with this 1:1 outreach strategy, framed as “you need to meet these people” rather than generic marketing. Ilya owns scripting and execution, with V/Logan available as the faces of the outreach.

5. **Embrace flexible but premium-feeling December offers**
   - Ilya asked for guardrails around discounts/specials (e.g., two roles for a set price).
   - V is comfortable with creative introductory offers (e.g., first ~100 candidates or similar constructs) so long as they do not cheapen the brand.
   - **Decision:** Treat offer structure as flexible. Default bias: small, clearly-scoped experiments that highlight quality and outcomes rather than deep discounts.

6. **Invest in GTM2 (LinkedIn groups) as a slow-burn channel**
   - Ilya outlined a GTM2 plan centered on posting into curated LinkedIn groups where buyers gather, using ghostwritten posts for V and Logan.
   - **Decision:** Consider GTM2 an approved strategic channel. Ilya will continue developing the group list, rules, and content; V is supportive of using his voice as the primary author.

7. **Keep Fireflies positioned narrowly as a meeting tool**
   - Experiments asking Fireflies to read poetry in character voices were rebuffed by the tool.
   - **Decision:** Internally, treat Fireflies as a meeting recorder and helper only; avoid relying on it for theatrical or non-meeting functions and do not design workflows that depend on such behavior.

