---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D3.2
---

# Fillout Intake Form Specification

Form for callers to submit before calling the Career Coaching Hotline. Pre-briefing data is stored in DuckDB and matched by phone number when they call.

## Form Title

**Career Coaching Hotline — Pre-Call Intake**

## Subtitle

Fill this out before you call. It takes 2 minutes, and it helps us give you better advice right from the start.

## Fields

| # | Field Label | Fillout Type | Required | Validation | Notes |
|---|------------|-------------|----------|------------|-------|
| 1 | Full Name | Short Answer (text) | Yes | Min 2 chars | |
| 2 | Phone Number | Phone Number | Yes | Must be valid phone | **Critical** — used to match caller on the hotline. Display helper text: "Use the same number you'll call from." |
| 3 | Email Address | Email | No | Valid email format | For follow-up if they don't call |
| 4 | Upload Your Resume | File Upload | No | PDF, DOCX, max 10MB | Helper text: "Optional but helpful — we'll use it to understand your background before the call." |
| 5 | LinkedIn Profile URL | URL | No | Must start with linkedin.com | Helper text: "Paste your LinkedIn URL if you have one." |
| 6 | Where are you in your career search? | Dropdown | Yes | Single select | See options below |
| 7 | What do you want help with? | Long Answer (textarea) | Yes | Min 10 chars | Helper text: "Tell us what's going on and what kind of help you're looking for." |
| 8 | How did you hear about us? | Short Answer (text) | No | | Attribution tracking |

## Dropdown Options for "Career Stage" (Field 6)

Sourced from `career-stages.md`. Caller-friendly labels:

| Value (stored) | Display Label |
|----------------|---------------|
| `groundwork` | I'm just getting started — figuring out what I want |
| `materials` | I'm working on my resume and application materials |
| `outreach` | I'm actively applying and searching |
| `performance` | I'm getting interviews but not landing offers |
| `transition` | I'm changing careers or recovering from a layoff |

## Webhook Configuration

In Fillout.com settings:

- **Webhook URL**: `https://<service-domain>/intake` (set after D3.1 deploys)
- **Method**: POST
- **Content-Type**: application/json
- **Trigger**: On form submission (every submission)

## Fillout Webhook Payload Shape

Fillout sends submissions in this format:

```json
{
  "submissionId": "abc123",
  "formId": "form_xyz",
  "formName": "Career Coaching Hotline — Pre-Call Intake",
  "submittedAt": "2026-02-14T12:00:00Z",
  "questions": [
    {
      "id": "field_1",
      "name": "Full Name",
      "type": "ShortAnswer",
      "value": "Jane Doe"
    },
    {
      "id": "field_2",
      "name": "Phone Number",
      "type": "PhoneNumber",
      "value": "+15551234567"
    },
    {
      "id": "field_3",
      "name": "Email Address",
      "type": "EmailAddress",
      "value": "jane@example.com"
    },
    {
      "id": "field_4",
      "name": "Upload Your Resume",
      "type": "FileUpload",
      "value": [
        {
          "name": "resume.pdf",
          "url": "https://api.fillout.com/..."
        }
      ]
    },
    {
      "id": "field_5",
      "name": "LinkedIn Profile URL",
      "type": "URLField",
      "value": "https://linkedin.com/in/janedoe"
    },
    {
      "id": "field_6",
      "name": "Where are you in your career search?",
      "type": "Dropdown",
      "value": "I'm actively applying and searching"
    },
    {
      "id": "field_7",
      "name": "What do you want help with?",
      "type": "LongAnswer",
      "value": "I've been applying for 3 months with no callbacks..."
    },
    {
      "id": "field_8",
      "name": "How did you hear about us?",
      "type": "ShortAnswer",
      "value": "Twitter"
    }
  ]
}
```

## Field Extraction Logic

The webhook handler extracts fields by matching `name` (case-insensitive partial match) rather than by `id`, since Fillout field IDs are opaque and may change if the form is rebuilt. See `intake-webhook.ts` for implementation.
