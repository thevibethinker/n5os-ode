---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: pulse:consulting-zoffice-stack:D4.2
type: form-spec
form_builder: google-forms
estimated_time: 10 minutes
---

# Client Intake Questionnaire

## Form Configuration

**Title:** Zo Consulting Intake  
**Description:** Help me understand your context so we can hit the ground running. Takes about 10 minutes.

---

## Section 1: Context

**Page Title:** What brings you here?

### Q1.1: Trigger
**Type:** Long text  
**Label:** What prompted you to explore Zo?  
**Helper:** Could be a specific problem, recommendation, curiosity — whatever brought you here.  
**Required:** Yes

### Q1.2: Prior Attempts
**Type:** Long text  
**Label:** What have you tried so far?  
**Helper:** Other AI tools, automations, workflows you've experimented with. "Nothing yet" is a valid answer.  
**Required:** Yes

### Q1.3: Friction Point
**Type:** Long text  
**Label:** What's your biggest friction point right now?  
**Helper:** The thing that makes you think "there has to be a better way."  
**Required:** Yes

---

## Section 2: Environment

**Page Title:** Your current setup

### Q2.1: Current Tools
**Type:** Checkboxes  
**Label:** What tools do you use regularly?  
**Options:**
- Gmail / Google Workspace
- Notion
- Slack
- Discord
- Airtable
- Linear / Jira
- Figma
- VS Code / Cursor
- Calendar (Google/Outlook/Apple)
- CRM (HubSpot, Salesforce, etc.)
- Other (please specify)

**Required:** Yes

### Q2.2: Integrations
**Type:** Long text  
**Label:** What integrations matter most to you?  
**Helper:** Which tools MUST talk to each other? What workflows span multiple apps?  
**Required:** No

### Q2.3: Team Context
**Type:** Multiple choice  
**Label:** Team size and technical sophistication  
**Options:**
- Just me, non-technical
- Just me, technical
- Small team (2-5), mostly non-technical
- Small team (2-5), mixed technical
- Larger team (6+)

**Required:** Yes

---

## Section 3: Goals

**Page Title:** What success looks like

### Q3.1: 30-Day Success
**Type:** Long text  
**Label:** What does "success" look like in 30 days?  
**Helper:** Be specific. "Save 5 hours per week on X" is better than "be more efficient."  
**Required:** Yes

### Q3.2: 90-Day Success
**Type:** Long text  
**Label:** What does "success" look like in 90 days?  
**Helper:** Bigger picture. Where do you want to be?  
**Required:** Yes

### Q3.3: Constraints
**Type:** Long text  
**Label:** Any hard constraints?  
**Helper:** Budget limits, time restrictions, tools you can't change, policies you must follow.  
**Required:** No

---

## Section 4: Preferences

**Page Title:** How we'll work together

### Q4.1: Communication Style
**Type:** Multiple choice  
**Label:** Preferred communication style  
**Options:**
- Brief and direct (bullet points, minimal context)
- Detailed with rationale (explain the "why")
- Somewhere in between

**Required:** Yes

### Q4.2: Update Timing
**Type:** Short text  
**Label:** Best time for async updates?  
**Helper:** E.g., "mornings ET" or "anytime is fine"  
**Required:** No

### Q4.3: Anything Else
**Type:** Long text  
**Label:** Anything else I should know?  
**Helper:** Work style, pet peeves, context that helps me help you.  
**Required:** No

---

## Form Settings

- **Confirmation message:** "Thanks! I'll review your responses before our first call."
- **Email collection:** Required
- **Response notifications:** Send to consulting inbox
- **Airtable integration:** Push responses to Clients table
