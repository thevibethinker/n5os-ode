---
created: 2025-11-17
last_edited: 2025-11-17
version: 1.0
---

# Detailed Recap

## Meeting Overview
Vrijen Attawar (Careerspan founder) met with David Yunghans (student at UIUC, graduating in behavioral neuroscience) to discuss David's early-stage career tech startup. David reached out after finding Vrijen through LinkedIn/Borderly, recognizing potential synergies between their companies. The meeting focused on go-to-market strategy, marketplace dynamics, technology architecture, and exploring partnership opportunities.

## Core Problem Identification
Both founders identified the same core market inefficiency: the **visibility problem** rather than a candidate viability problem. Existing solutions focus on assessing whether candidates *should* get hired, but the real issue is that employers lack modern tools (essentially unchanged since the dot-com era) to make candidates visible to them. Universities similarly lack mechanisms to showcase their talent.

## David's Solution & Product Architecture
David's platform addresses visibility through an LLM-powered matching system:

- **Candidate-Centric Input**: Candidates manually create digital resume accounts (not automated parsing) that they can download and share
- **LLM Ranking System**: The LLM performs two-stage ranking—initial pre-ranking, then contextual ranking based on employer job requirements
- **Vector Storage & Matching**: Rankings stored as graph vectors; highest-performing vectors automatically recommended to employers
- **Automated Recommendations**: Instead of waiting for applications, employers receive 25 pre-screened candidates with ChatGPT-like paragraph explanations covering education, experience, and projects
- **No Resume Summarization**: The platform structures data as discrete experiences and projects rather than free-form summaries
- **Market Adaptability**: Building initially for US universities (UIUC, Georgia Tech), adapting approach for Indian placement offices

## Go-to-Market & Traction

**Current Momentum**:
- 7 months old with 1,000 LinkedIn followers
- First pilot programs in India (Tier 1 & 2 institutions)
- University partnerships: UIUC, Georgia Tech (backed by GeoX accelerator)
- Active testing with Ellis (San Bernardino-based data analytics company) hiring from UIUC Data Science club

**Strategy**:
- Building advisor network (preferring broad advisor equity over none) to syndicate interests
- Leveraging key connectors like Camilla (Human Options event host, connected to Johns Hopkins, Hofstra, Rice)
- No university charges; free for students; employer subscription model ($250/month, scaling by school access)
- Supported by $500K+ in Kratex and venture credits
- Minimal compute overhead ($300 total LLM cost to date)

## Technology & Efficiency Discussion

**Current Architecture**: Built with Claude Sonnet 4.5 exclusively; fine-tuning approach for ranking optimization

**Vrijen's Feedback**: Avoid long-term grounding in state-of-the-art models. Better design philosophy involves decomposing tasks to use the "dumbest possible model" for each component. Careerspan uses GPT-4o as the most complex model (no GPT-5), maintaining cost efficiency while scaling. Example: Vrijen achieved 40-50% cost reduction on complex workflows by strategically mixing Sonnet and Haiku rather than using Sonnet everywhere.

**Key Insight**: Model lock-in risk; David acknowledged Claude commitment via credits, but moving toward model flexibility will improve long-term scalability.

## Data Structure & UX Philosophy Divergence

**David's Approach**: Maximize information abundance—provide employers with everything (transcript, resume, LinkedIn, GitHub, portfolio links, etc.) so the data "speaks for itself"

**Vrijen's Perspective**: The underlying tension in career advancement is that people are poor at self-examination and articulating their value. Careerspan focuses on reflection-oriented UX to help candidates bring their best selves to the AI, which then positions them effectively to employers. This addresses a deeper market need around *self-awareness* rather than just *data abundance*.

**Point of Caution**: Manual data input by candidates means quality depends on user articulation. Vrijen suggested exploring partnerships with career coaching/interview prep organizations to help candidates communicate better.

## Marketplace Dynamics & Lessons Learned

**Handshake Case Study**: Succeeded through massive recruiter scale, but created new inefficiencies:
- Network effects plateau at scale (filter bias recreated the same caste system)
- Universities can't afford talent team budgets like tech companies
- ATS systems now worthless (600+ applications with no differentiation capability)
- Handshake charges universities precisely because single-side monetization doesn't work

**Strategic Advice**: 
- Avoid charging universities if possible; the existential threat perception ("technology replacing us") creates resistance
- Build relationships through trusted connectors (like Camilla)
- Don't ground strategy in false competition with Handshake's scale; focus on product advantage (David's: less threat to career services staff)

## Industry Intelligence

**Key Conferences & Programs**:
- **NACE Conference**: Essential for university talent team relationships
- **SHERM WorkTech Accelerator**: $200K competition, but bureaucratic (deadline recently passed, next cycle coming)
- **Create X**: Experiencing "candidate golden era"—high volume, zero differentiation

**Key Relationship**: Camilla (Human Options) is critical connector to East Coast universities; treat her as strategic ally.

## Advisor Relationship & Next Steps

Vrijen offered to:
- Become formal advisor to David's company
- Include David in career tech founder community (monthly/bi-monthly meetings)
- Connect David with other career tech founders in New York ecosystem
- Facilitate in-person meetings when in New York (at Camilla's events)

David committed to:
- Sending contact email for Slack group additions
- Further discussion on advisor terms and value-add expectations
- Meeting in person when possible

---

**Meeting Length**: ~28 minutes | **Participants**: 2 | **Context**: External intro, potential advisor relationship formation
