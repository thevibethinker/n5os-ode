```markdown
---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
provenance: con_Pmf1tIz1P3RDQRJr
block_type: B03
---

# B03: Decisions Made

## Decision 1: Integrate CorridorX's JD Generation Workflow with Careerspan

**DECISION:** CorridorX will integrate their Lovable-built value chain workflow with Careerspan, where customers generate JDs that are then routed into the Careerspan platform as roles.

**CONTEXT:** Shivam has built a workflow where founders/CTOs fill out a template on a Lovable-generated page, which outputs a JD and related materials. This will serve as the connective tissue between CorridorX's business and Careerspan.

**DECIDED BY:** Shivam Desai (CorridorX), with agreement from Vrijen and Ilse

**IMPLICATIONS:** 
- JDs from this workflow will create roles in Careerspan
- CorridorX talent pool will be matched against these roles
- Enables automated routing of opportunities to engineers

**ALTERNATIVES CONSIDERED:** None discussed - this was presented as the planned workflow

---

## Decision 2: CorridorX to Have Initial Visibility and Management Access

**DECISION:** CorridorX will have visibility and management access to the employer side of Careerspan on behalf of their customers in the initial phase.

**CONTEXT:** Shivam wants to see which profiles are relevant to each JD and manage the matching workflow himself to start, noting that "some will be manual."

**DECIDED BY:** Shivam Desai (CorridorX), with agreement from Vrijen and Ilse

**IMPLICATIONS:**
- Shivam will be able to manage employer accounts for CorridorX customers
- Initial workflow will have manual oversight before full automation
- Allows CorridorX to learn and refine the process

**ALTERNATIVES CONSIDERED:** Fully API-based interaction (discussed but not chosen - Shivam wants UI visibility initially)

---

## Decision 3: Careerspan to Set Up Account and Infrastructure Within 48 Hours

**DECISION:** Ilse will set up all necessary Careerspan infrastructure for CorridorX within 48 hours of this meeting.

**CONTEXT:** Shivam needs to start onboarding the first 15 engineers immediately. Ilse committed to rapid setup to enable this timeline.

**DECIDED BY:** Ilse Funkhouser (Careerspan), in response to Shivam's needs

**IMPLICATIONS:**
- Employer account created for CorridorX
- Scanning credits provided
- Sign-up links and organization codes generated for talent pool
- Custom button to scan only CorridorX's users (not random site users)
- Rate limit can be increased from 5 concurrent scans if needed

**ALTERNATIVES CONSIDERED:** None - this was a commitment to enable the pilot

---

## Decision 4: Use Careerspan's Automated Matching and Email Workflow

**DECISION:** CorridorX will use Careerspan's automated scan and email workflow for talent matching.

**CONTEXT:** Ilse explained that once a role is published, Careerspan scans the talent pool and only shows the role to clearly qualified candidates via one-click apply emails. This saves CorridorX from manual communication.

**DECIDED BY:** Both parties agreed this is beneficial for CorridorX's use case

**IMPLICATIONS:**
- Engineers only see roles they're qualified for (Rails engineers see Rails roles, etc.)
- One-click apply via email
- Reduces outbound communication burden on CorridorX
- Careerspan covers the scanning costs (not charging CorridorX initially)

**ALTERNATIVES CONSIDERED:** Sending role links to entire talent pool and letting them self-select (rejected due to higher effort and cost)

---

## Decision 5: Webhook Integration for Application Status Updates

**DECISION:** Careerspan will set up webhooks to notify CorridorX's systems when applicants are marked as "pass" or "proceed."

**CONTEXT:** Shivam may want application updates integrated with his own systems rather than managing entirely within Careerspan's UI.

**DECIDED BY:** Ilse Funkhouser (Careerspan), offering this capability

**IMPLICATIONS:**
- Automated event emissions on status changes
- Enables CorridorX to build custom workflows around applicant progression
- Simple to configure (Ilse can set this up)

**ALTERNATIVES CONSIDERED:** Using Careerspan's built-in management UI only (still available if preferred)

---

## Decision 6: Pilot Launch - First 15 Engineers This Week

**DECISION:** CorridorX will onboard the first 15 engineers from their top 100 talent pool immediately, starting today and tomorrow.

**CONTEXT:** Shivam stated: "today and tomorrow I'm going to actively start messaging first 15 engineers in my pool that are some of the best engineers we have access to and start bringing to the Career Span platform."

**DECIDED BY:** Shivam Desai (CorridorX)

**IMPLICATIONS:**
- Immediate testing of the integration workflow
- Real feedback from high-quality candidates
- Validates whether Careerspan provides value for this use case
- First step toward broader rollout

**ALTERNATIVES CONSIDERED:** None - this is an immediate action item

---

## Decision 7: Reschedule Meeting to Wednesday Afternoon

**DECISION:** Vrijen and Shivam will reschedule their in-person meeting to Wednesday afternoon (before Vrijen's Founders Club dinner).

**CONTEXT:** Vrijen has a prior commitment (Founders Club dinner) on Wednesday evening. Shivam has a midday meeting but is open after.

**DECIDED BY:** Both parties

**IMPLICATIONS:**
- Meeting location flexible (Vrijen can travel from downtown Brooklyn)
- Timing to be finalized via message

**ALTERNATIVES CONSIDERED:** None

---

## Decision 8 (DEFERRED): Business Model and KPIs to Be Discussed Later

**DEFERRED:** Discussion of business model, pricing, and KPIs was postponed to a future conversation.

**CONTEXT:** Shivam asked "what should our KPIs be?" and mentioned potential webinars for India-based talent, but the conversation shifted and this wasn't resolved.

**DECIDED BY:** Implicitly deferred - both parties moved to other topics

**IMPLICATIONS:**
- Business terms not yet finalized
- Pricing structure still to be determined
- Success metrics need to be defined

**ALTERNATIVES CONSIDERED:** None - this needs dedicated conversation time
```