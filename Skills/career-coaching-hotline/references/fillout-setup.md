---
created: 2026-02-14
last_edited: 2026-02-14
version: 1.0
provenance: career-coaching-hotline/D5.1
---

# Fillout Intake Form Setup Guide

Step-by-step guide to create the pre-call intake form in Fillout.com for the Career Coaching Hotline.

## Purpose

Callers fill out this form before calling the hotline. The data is stored in DuckDB and matched by phone number when they call, giving the AI coach context about the caller's situation before they even start speaking.

## Step 1: Create the Form

1. Go to [Fillout.com](https://fillout.com) → **Create Form**
2. Title: **Career Coaching Hotline — Pre-Call Intake**
3. Subtitle: *Fill this out before you call. It takes 2 minutes, and it helps us give you better advice right from the start.*

## Step 2: Add Fields

Add these fields in order:

| # | Field Label | Type | Required | Notes |
|---|------------|------|----------|-------|
| 1 | Full Name | Short Answer | ✅ Yes | Min 2 characters |
| 2 | Phone Number | Phone Number | ✅ Yes | Helper text: "Use the same number you'll call from." |
| 3 | Email Address | Email | No | For follow-up if they don't call |
| 4 | Upload Your Resume | File Upload | No | Accept: PDF, DOCX. Max: 10MB. Helper: "Optional but helpful." |
| 5 | LinkedIn Profile URL | URL | No | Helper: "Paste your LinkedIn URL if you have one." |
| 6 | Where are you in your career search? | Dropdown | ✅ Yes | See options below |
| 7 | What do you want help with? | Long Answer | ✅ Yes | Min 10 chars. Helper: "Tell us what's going on." |
| 8 | How did you hear about us? | Short Answer | No | Attribution tracking |

### Dropdown Options for Field 6

| Display Label |
|---------------|
| I'm just getting started — figuring out what I want |
| I'm working on my resume and application materials |
| I'm actively applying and searching |
| I'm getting interviews but not landing offers |
| I'm changing careers or recovering from a layoff |

## Step 3: Configure the Webhook

1. Go to **Form Settings → Integrations → Webhooks**
2. Add webhook:
   - **URL**: `https://career-coaching-hotline-va.zocomputer.io/intake`
   - **Method**: POST
   - **Trigger**: On every submission
3. No additional headers needed (the intake endpoint doesn't require auth — it validates the payload structure)

## Step 4: Configure Confirmation

Set the form's confirmation message:

> **You're all set!** Call the Career Coaching Hotline now and we'll have your info ready. The number is: **[PHONE NUMBER]**
>
> The hotline is available 24/7. When you call, just start talking about what's going on — V already knows your background.

## Step 5: Test

1. Submit a test entry with a known phone number
2. Verify the webhook fires:
   ```bash
   tail -20 /dev/shm/career-coaching-hotline.log | grep -i intake
   ```
3. Verify data stored in DuckDB:
   ```bash
   duckdb Datasets/career-hotline-calls/data.duckdb -c "SELECT * FROM caller_lookup ORDER BY submitted_at DESC LIMIT 1"
   ```
4. Call the hotline from that phone number and verify the AI references the caller's intake data

## Form Spec Reference

Full field specifications and payload shape documented in:
`N5/builds/career-coaching-hotline/artifacts/fillout-form-spec.md`

## How Matching Works

The intake webhook (`scripts/intake-webhook.ts`) processes submissions:
1. Extracts fields by matching on field `name` (case-insensitive partial match)
2. Normalizes the phone number to E.164 format
3. Stores in the `caller_lookup` table in DuckDB
4. When a call comes in, the `lookupCaller` tool queries this table by phone number

If a caller submits multiple times, the most recent submission takes precedence.
