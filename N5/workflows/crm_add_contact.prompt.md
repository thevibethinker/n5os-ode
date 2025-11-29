---
title: CRM Add Contact
description: Structured workflow for adding new contacts to CRM via natural language
tags: [crm, create, contact, tool]
tool: true
created: 2025-11-18
last_edited: 2025-11-18
version: 1.0
---

# Mission

Add new contact to CRM V3 from natural language description.

**Input:** {{contact_description}}

---

## Execution Protocol

### Step 1: Extract Structured Data

Parse the contact description to extract:

**Required:**
- **Email:** [Extract or ask if missing]
- **Name:** [Extract or ask if missing]

**Optional:**
- **Category:** NETWORKING | INVESTOR | ADVISOR | COMMUNITY [Infer from context]
- **Company:** [Extract from email domain or description]
- **Meeting Context:** [When/where met, event name, etc.]
- **Notes:** [Any additional context provided]

**Inference Rules:**
- Titles like "investor at", "partner at" → INVESTOR
- Titles like "advisor", "mentor" → ADVISOR  
- Community builders, event organizers → COMMUNITY
- Default → NETWORKING

### Step 2: Validate & Confirm

**Check if profile exists:**
```bash
crm search --email [extracted_email]
```

**If exists:**
- Show existing profile
- Ask if user wants to update/add notes
- Exit without creating duplicate

**If missing required fields:**
- List what's missing
- Ask user to provide
- Do NOT create incomplete profile

### Step 3: Create Profile

**Execute creation:**
```bash
crm create --email [EMAIL] --name "[NAME]" --category [CATEGORY] --notes "[NOTES]"
```

**Notes format:**
```
Added via CRM add-contact workflow [DATE]

Context: [Where met / event / circumstances]
Company: [If identified]
Initial categorization: [Why this category was chosen]

[Any additional user-provided context]
```

### Step 4: Confirm & Next Steps

**Success message:**
```markdown
✓ Profile created: [NAME] ([EMAIL])
  Category: [CATEGORY]
  Profile: file 'N5/crm_v3/profiles/[FILENAME].yaml'
  
Enrichment has been queued automatically (priority 100, immediate processing).

**Suggested next steps:**
- [ ] Add LinkedIn URL if known
- [ ] Add phone number if available
- [ ] Queue for checkpoint_2 enrichment if meeting scheduled
- [ ] Review profile and add relationship notes
```

---

## Examples

### Example 1: Complete Information

**Input:** "Add Sarah Chen, investor at Andreessen Horowitz, met at TechCrunch Disrupt, email: sarah.chen@a16z.com"

**Extracted:**
- Email: sarah.chen@a16z.com
- Name: Sarah Chen
- Category: INVESTOR (inferred from "investor at")
- Company: Andreessen Horowitz (a16z.com)
- Context: Met at TechCrunch Disrupt

**Notes Generated:**
```
Added via CRM add-contact workflow 2025-11-18

Context: Met at TechCrunch Disrupt
Company: Andreessen Horowitz (a16z.com)
Initial categorization: INVESTOR - identified from title "investor at Andreessen Horowitz"
```

---

### Example 2: Missing Email

**Input:** "Add John Smith from Stripe, we met at the SF event"

**Action:**
```markdown
⚠ Missing required information

I need an email address to create this profile.

**What I have:**
- Name: John Smith
- Company: Stripe
- Context: Met at SF event
- Category: NETWORKING (default)

**What I need:**
- Email address

Please provide John's email, or I can help you find it if you have other identifying information.
```

---

### Example 3: Duplicate Check

**Input:** "Add Alex Caveny, alex.caveny@gmail.com"

**Action:**
```bash
crm search --email alex.caveny@gmail.com
```

**Response:**
```markdown
⚠ Profile already exists

**Found:** Alex Caveny (alex.caveny@gmail.com)
- Category: ADVISOR
- Quality: enriched
- Profile: file 'N5/crm_v3/profiles/Alex_Caveny_alex_caveny.yaml'

Would you like to:
1. View this profile's intelligence synthesis
2. Add notes to existing profile
3. Update categorization
4. Do nothing
```

---

## Validation Rules

**Email validation:**
- Must contain @ symbol
- Must have domain
- Should be valid format (basic regex check)

**Name validation:**
- Should not be empty
- Should be properly capitalized
- If only first name provided, ask for last name

**Category validation:**
- Must be one of: NETWORKING, INVESTOR, ADVISOR, COMMUNITY
- If ambiguous, choose NETWORKING as default
- Explain categorization reasoning

---

## Error Handling

**If crm create fails:**
1. Show error message from CLI
2. Identify the issue (duplicate, missing data, etc.)
3. Suggest corrective action
4. DO NOT retry without user confirmation

**If data is ambiguous:**
1. Show what was extracted
2. Show what's uncertain
3. Ask user to clarify
4. Proceed only after confirmation

---

## Success Criteria

✅ Profile created in database
✅ YAML file generated
✅ Enrichment queued automatically
✅ User receives confirmation with profile path
✅ No duplicates created
✅ All required fields populated

---

## Integration Notes

- Called by file `N5/workflows/crm_query.prompt.md` when creation intent detected
- Can be invoked directly via Prompts menu
- Uses CLI tool file `N5/scripts/crm_cli.py` for actual creation
- Enrichment automatically scheduled via crm_calendar_helpers.py

