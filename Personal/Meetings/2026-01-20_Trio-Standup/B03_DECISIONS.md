---
created: 2026-01-21
last_edited: 2026-01-21
version: 1.0
provenance: con_JePL6ylXF0jDwwIe
block_type: B03
---

# B03: Decisions Made

## Decision 1: Shivam Candidate Onboarding Flow

**DECISION:** Candidates must sign up using Shivam's org code link first, then they can use direct apply links for specific roles.

**CONTEXT:** Ilse clarified that direct apply links alone cannot add engineers to Shivam's coaching org. The system requires users to sign up with the org code to be properly tracked and added to the organization.

**DECIDED BY:** Team consensus (Ilse, Logan, V)

**IMPLICATIONS:**
- Landing page will include clear instructions: Step 1 sign up with org code, Step 2 click direct apply link
- Shivam can still send direct apply links to candidates, but they'll need an account first
- Tracking of Shivam's candidates will work correctly since they sign up with the org code

**ALTERNATIVES CONSIDERED:**
- Direct apply only (rejected - doesn't work for org tracking)
- Manual org addition after signup (too complex for users)

---

## Decision 2: V to Test Deep Scan Functionality

**DECISION:** V will test the deep scan functionality on production before it's shared with Shivam.

**CONTEXT:** Ilse has already enabled the feature in Shivam's account, but it needs verification that it works correctly before customer rollout.

**DECIDED BY:** Ilse (requested), V (agreed)

**IMPLICATIONS:**
- V will set up a test employer account and enable scanning via API
- Ilse has documented the input fields in the Corridor care package for Shivam
- V needs to understand the functionality well enough to explain it to Shivam

**ALTERNATIVES CONSIDERED:** None - testing required before customer handoff

---

## Decision 3: V Receives API Access for Scanning Control

**DECISION:** V has been granted API access to enable/disable global scanning, enable/disable organization-level scanning, and add/remove organizations to scan.

**CONTEXT:** Ilse explained that V will have controlled access to scanning features via API, but must manually go into employer accounts to configure everything. This prevents Shivam from scanning happily employed people and adding credits.

**DECIDED BY:** Ilse (granting access)

**IMPLICATIONS:**
- V can toggle scanning for any employer account globally
- Shvam's account can be controlled without giving him unrestricted access
- V can prevent misuse (e.g., scanning happily employed people)

**ALTERNATIVES CONSIDERED:** Full unrestricted access (rejected due to risk of misuse)

---

## Decision 4: Corridor X Landing Page Approved

**DECISION:** The Corridor X landing page is approved to send to Shivam.

**CONTEXT:** Logan completed the landing page with specific info for Shivam's candidates, including org code in all buttons. V reviewed and confirmed it communicates the product well.

**DECIDED BY:** V (approved)

**IMPLICATIONS:**
- Logan will send the landing page to Shivam immediately
- Shivam can distribute the link to his candidates
- All buttons contain the correct org ID for tracking

**ALTERNATIVES CONSIDERED:** None - page was well-received

---

## Decision 5: V Can Run Scanning Tests Independently

**DECISION:** V does not need Ilse present to test or configure scanning functionality.

**CONTEXT:** Ilse confirmed that V only needs API access to enable scanning for an employer account, and can then manually configure the rest. V was setting up guardrails to prevent the system from "running haywire."

**DECIDED BY:** Ilse (confirmed), V (agreed)

**IMPLICATIONS:**
- V can proceed with testing at his own pace
- No coordination needed between V and Ilse for setup
- V can test on a new employer account he creates

**ALTERNATIVES CONSIDERED:** Meeting with Ilse (determined unnecessary)

---

## Decision 6: Acquisition Materials Review Format

**DECISION:** Instead of a 10-minute acquisition breakout meeting, the team will spend 10 minutes reviewing the Notion dashboard to ensure all pieces are in place.

**CONTEXT:** Ilse questioned whether a dedicated acquisition meeting was needed. Logan proposed a quick dashboard review instead to verify materials are ready for distribution.

**DECIDED BY:** Team consensus

**IMPLICATIONS:**
- More efficient use of time
- Review will confirm materials are complete and ready for target contacts
- Will identify any gaps in acquisition materials

**ALTERNATIVES CONSIDERED:** Full 10-minute acquisition breakout (determined unnecessary)

---

## Decision 7: Zo Presentation Planning

**DECISION:** Logan needs to get "zoned up" (set up with Zo) this weekend because 25 people have already signed up for the presentation.

**CONTEXT:** V mentioned 25 registrations for an upcoming presentation, and Logan needs to be prepared with Zo tools.

**DECIDED BY:** V (directive), Logan (agreed)

**IMPLICATIONS:**
- Logan will configure Zo over the weekend
- Presentation must be prepared for Monday
- Team is treating this as high-priority deliverable

**ALTERNATIVES CONSIDERED:** None - registrations confirm urgency
