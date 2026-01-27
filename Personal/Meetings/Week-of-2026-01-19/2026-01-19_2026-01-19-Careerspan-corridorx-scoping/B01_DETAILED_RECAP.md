---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: con_VENkIg3G8iZ98LeB
---

# B01: Detailed Recap

## Meeting Overview
A scoping call between Careerspan (Vrijen Attawar, Ilse Funkhouser) and CorridorX (Shivam Desai) to explore integrating CareerSpan's story-based hiring platform into CorridorX's engineering talent placement workflow. The conversation moved from initial introductions to a detailed walkthrough of a proposed workflow, technical implementation specifics, and next steps for a pilot program.

## Chronological Discussion

### Opening and Context Setting (0:00-5:00)
The conversation began with casual small talk about Ilse's relocation to the Azores and weather discussions. Vrijen then pivoted to the business agenda, noting that Shivam had already seen the CareerSpan product and asking for any changes or thoughts from CorridorX's perspective. Ilse was mentioned as being vaguely looped in but needing to hear CorridorX's vision directly.

### CorridorX Business Model and Workflow Proposal (5:00-15:00)
Shivam outlined CorridorX's two-pronged business model: (1) building captive capability centers (20-30 person embedded teams owned by US companies) and (2) placing individual AI engineering pods. He referenced major players like Harvey AI, Anthropic, and OpenAI building teams in India as validation of this approach.

Shivam then demonstrated a Lovable-built workflow page designed to capture hiring requirements. The flow: customer fills out template → AI generates job description → JD routes to CareerSpan platform. Shivam explained he's actively messaging the top 15 engineers from his talent pool to onboard them to CareerSpan. He shared an example of a late-stage startup seeking an engineer with Gemini, Vertex, and Google Workspace experience, noting he had already parsed 15-20 resumes and could match skills manually but wanted CareerSpan's more comprehensive assessment.

### Technical Integration: UI vs API (15:00-22:00)
Ilse raised a critical implementation question: how much of the pipeline would use CareerSpan's UI versus API integration. She explained that CareerSpan's current system is slow due to sequential LLM calls, breaking JDs into 10 responsibilities, 10 soft skills, 10 hard skills, each with paragraph-length assessment criteria.

Shivam clarified that he wanted visibility to manage the employer portal on behalf of his customers, at least initially, to understand how profiles match JDs. Ilse confirmed this was feasible.

### CareerSpan Platform Walkthrough (22:00-35:00)
Ilse committed to having Shivam set up within 48 hours. She explained the scanning workflow: once a JD is published in CareerSpan's employer portal, a "scan" function processes it (7-8 minutes), then filters the talent pool. The system only exposes roles to clearly qualified candidates, sending them an email with a one-click apply option. This saves recruiters from broadcasting to unqualified candidates.

Ilse offered webhook integration for applicant status updates (pass/proceed) if needed, though noted CareerSpan's current UI has simple pass/proceed buttons with a notes section. Vrijen observed the core value proposition is cutting through noise to identify top prospects.

Shivam found the process straightforward and "very easy."

### Candidate Experience Discussion (35:00-42:00)
Ilse demonstrated the candidate experience: applicants receive an email showing their match score, gap analysis, and link to apply. The system uses all historical stories the user has ever told, not requiring new stories for each application. Candidates can see gaps (e.g., missing "agile methodology" evidence) and add stories before applying, with a "reprocess" button to update their score.

Vrijen emphasized the importance of marketing this to Indian engineers as both a competitive tool and practice for US job market expectations—demonstrating ability to self-advocate and discuss accomplishments.

### Cultural Considerations and Next Steps (42:00-50:00)
Ilse shared a cautionary anecdote about early CareerSpan testing with nurses in India, where users gave monosyllabic answers and asked for resume tailoring instead of engaging with the story-based approach. However, she noted these were non-technical roles and proper framing wasn't provided.

Shivam countered that India's top engineers (ex-Google, Amazon, major startups) are more culturally aligned with Western work norms, citing major tech investments in India (Google, Amazon $50B, etc.). Vrijen added that Indian engineers are valued for not being perceived as IP threats, a practical consideration for US companies.

Vrijen expressed strong enthusiasm, calling it "super convenient" and a great way to showcase CareerSpan, with potential to integrate into the upcoming talent mixer event.

## Key Takeaways

- **Integration Workflow Established**: Lovable captures hiring requirements → generates JD → routes to CareerSpan → CareerSpan's scanning system matches against candidate stories → automated notifications to qualified engineers → one-click apply workflow

- **Technical Implementation**: Ilse will set up CorridorX with an employer account within 48 hours, including scanning credits and a dedicated invite code for their talent pool; rate limits currently cap at 5 concurrent scans but can be increased

- **Candidate Strategy**: Shivam is initially targeting the top 15 engineers from his talent pool; success metrics will inform broader rollout; potential future webinars to educate Indian engineers on the value of story-based self-advocacy for US opportunities

- **Cultural Alignment**: While early testing revealed engagement challenges with non-technical Indian users, CorridorX's pool (ex-big tech, top startups) is expected to align well with CareerSpan's story-based approach; marketing should frame the platform as practice for US job market expectations

- **Strategic Value**: Vrijen sees this partnership as a powerful way to demonstrate CareerSpan's capabilities, with potential to integrate findings into the talent mixer event

- **Next Steps**: Shivam to begin onboarding 15 target engineers; Ilse to complete account setup; potential webhook integration for applicant status notifications if needed; ongoing feedback loop to refine workflow
