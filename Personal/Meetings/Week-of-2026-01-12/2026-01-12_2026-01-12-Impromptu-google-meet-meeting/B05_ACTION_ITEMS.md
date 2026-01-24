### Product & Monetization Questions (2026-01-12)
**Q: So to clarify, are we delivering a pre-built Zo product (with an automated process and platform cut) or teaching students how to build from scratch?**  
Status: Answered  
Context: Packaging decides if the revenue engine is product access or repeated cohorts, and it sets expectations for support and positioning.  
Answer: Speigel wants the Zo product to be the revenue engine—sell access via a Gumroad/Notion-style storefront, layer teaching on top, but don’t rely on repeat cohort income.

**Q: Does Notion let creators charge for templates and similar pre-built workflows?**  
Status: Answered  
Context: We wanted a concrete monetization precedent to justify charging for Zo templates instead of only consulting.  
Answer: Yes—Notion, Canva, and Gumroad enable creators to paywall templates, so Zo can follow the same playbook and keep a platform cut.

**Q: Can you think of a decent MVP that charges $10–$30, avoids accounts/auth, and simply returns a session-based output after Stripe payment?**  
Status: Unanswered (Action item)  
Context: Vrijen is wary of building authentication/state early, so a stateless MVP would let us launch quickly while monetizing career support.  
Answer: TBD (needs follow-up).

### Implementation & Zo Questions (2026-01-12)
**Q: Does the solution require persistent state, or can we treat each run as a session that clears when the browser refreshes?**  
Status: Answered  
Context: Choosing between session-only flows and stored user data affects complexity, security, and how much private information we handle early on.  
Answer: Vrijen confirmed we can keep everything in-session—refreshing/closing clears the inputs, so the first release should optimize around session-based experiences.

I appended the above block to `file 'B05_ACTION_ITEMS.md'`, and the unanswered stateless MVP question is now flagged as an action item. 2026-01-20 10:55 ET
