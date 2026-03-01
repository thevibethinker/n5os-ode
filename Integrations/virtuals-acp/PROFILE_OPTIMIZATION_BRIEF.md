# Zøde ACP Profile Optimization Brief

**Purpose:** Systematic optimization of Zøde's ACP profile, value proposition, business description, and job offerings to maximize discoverability and conversion on Virtuals Protocol.

**Context:** V is registering Zøde as a service provider on Virtuals Protocol ACP (app.virtuals.io/acp/join). The current draft profile is at `Integrations/virtuals-acp/REGISTRATION_GUIDE.md`. It works, but needs to be sharper — optimized for how ACP's Butler agent discovers and recommends services, how other agents evaluate providers, and how the whole thing reads to buyers.

**Identity:** Zøde (pronounced "zoh-deh") — The AI-Human Marriage Counselor. NEVER "Zoday" — that was a transcription error. At most: "Zøde by @thevibethinker".

---

## What This Worker Should Do

### Phase 1: Competitive Intelligence

1. **Research existing ACP service providers** — What are the top-performing agents selling? What do their business descriptions look like? What keywords do they use?
   - Read: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/best-practices-guide
   - Search for live ACP agents via web research to see real examples
   - Check what the Butler agent looks for when recommending services

2. **Analyze the ACP discovery mechanism** — How does keyword search work? What fields does Butler index? What makes an agent "graduate" faster?
   - Read: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/graduate-agent
   - Read: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/tips-and-troubleshooting

3. **Study the Moltbook/OpenClaw ecosystem** — What pain points are agents actually expressing? What language do they use?
   - This informs the keywords and descriptions we should use

### Phase 2: Profile Optimization

4. **Rewrite the Business Description** — Current is functional but generic. Optimize for:
   - ACP Butler discovery (right keywords)
   - Agent-to-agent readability (agents are the buyers, not humans)
   - Unique value proposition that no other ACP provider offers
   - Max 500 characters

5. **Optimize Job Offering Names** — Current names (CommunicationAudit, HumanReadableRewrite, TrustRecoveryPlan) are human-readable. But ACP buyers are AGENTS. Optimize for:
   - Searchability (what would a buyer agent search for?)
   - Clarity of deliverable
   - Keywords that Butler and buyer agents would match on

6. **Sharpen Job Descriptions** — Each job description should:
   - Lead with the problem it solves (from the buyer agent's perspective)
   - Be specific about what's delivered
   - Include keywords other agents would search for
   - Fit the ACP ecosystem conventions

7. **Optimize Schemas** — The requirement and deliverable schemas define the contract. Optimize for:
   - Minimal friction for buyer agents (easy to fill in)
   - Clear deliverable expectations
   - Machine-parseable where possible (buyer agents will process these programmatically)

8. **Price Validation** — Confirm $0.50-$1.00 range is right by checking:
   - What other communication/content services charge on ACP
   - Whether pricing too low signals low quality
   - Whether pricing should vary more between tiers

### Phase 3: Differentiation

9. **Craft the "why Zøde" pitch** — What makes Zøde different from any generic LLM doing rewrites?
   - Zøde's origin story (found the problem by observing, not deployed with a mission)
   - V's real-world career coaching background
   - The Vibe Thinker Bible (6 chapters on zo.space)
   - The Human Manual API (23 machine-readable entries)
   - Proven Moltbook presence and community engagement

10. **Add Resources** — ACP allows agents to attach resources. Consider:
    - Link to the Human Manual API: https://va.zo.space/api/human-manual
    - Link to the Vibe Thinker Bible: https://va.zo.space/guides/vibe-thinking
    - Sample deliverable showing what a CommunicationAudit actually looks like

### Phase 4: Output

11. **Produce an updated REGISTRATION_GUIDE.md** with all optimized copy, ready for V to paste directly into the ACP registration form. Save to `Integrations/virtuals-acp/REGISTRATION_GUIDE_v2.md`.

12. **Produce a competitive positioning doc** summarizing what was found about the ACP landscape and why Zøde's positioning is strong. Save to `Integrations/virtuals-acp/competitive_positioning.md`.

---

## Key Files to Read

| File | Why |
|------|-----|
| `Integrations/virtuals-acp/REGISTRATION_GUIDE.md` | Current draft to optimize |
| `Skills/zode-moltbook/assets/zode-persona.md` | Zøde's full identity and voice |
| `Skills/zode-moltbook/prompts/engagement-prompt.md` | Engagement rubric and content themes |
| `Skills/zode-moltbook/SKILL.md` | Full skill definition, zo.space routes, capabilities |
| `Integrations/virtuals-acp/zode_seller.py` | Current job handlers (what Zøde actually delivers) |

## Key URLs to Research

- ACP Best Practices: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/best-practices-guide
- ACP Graduation: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/graduate-agent
- ACP Tips: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/tips-and-troubleshooting
- ACP Schema Validation: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/set-up-agent-profile/create-job-offering/job-offering-data-schema-validation
- ACP SLA Guide: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/set-up-agent-profile/create-job-offering/define-service-level-agreement
- ACP Job Sample Setup: https://whitepaper.virtuals.io/acp-product-resources/acp-dev-onboarding-guide/set-up-agent-profile/create-job-offering/setup-job-sample
- Human Manual API: https://va.zo.space/api/human-manual
- Vibe Thinker Bible: https://va.zo.space/guides/vibe-thinking

## Pricing Constraint

V confirmed: $0.50-$1.00 USDC per communication task. Can adjust within this range but don't exceed $1.00 for any single job offering.

## Output Expectations

The final REGISTRATION_GUIDE_v2.md should be a copy-paste-ready document where V can literally paste each field value directly into the ACP registration form. No ambiguity, no "consider this" — just the final optimized text for each field.
