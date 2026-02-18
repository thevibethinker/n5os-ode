---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_yZWXJwwYvVRT8HKX
---

# CRM Automation for Freelancers

## Goal
Automatically track client interactions, follow-ups, and project status from email conversations.

## Inputs
- Gmail inbox and sent emails
- Client contact database
- Project status tracking sheet
- Follow-up templates

## Pipeline
• Scan inbox for client emails using sender filters
• Extract project updates, questions, and action items via AI
• Update Airtable/spreadsheet with interaction summary
• Flag overdue follow-ups based on last contact date
• Generate personalized follow-up drafts for review
• Schedule reminders for project check-ins
• Track response times and client engagement patterns

## First Version
Email scanner that identifies client messages and logs them to a simple spreadsheet with date and summary.

## Upgrade Path
• Automated proposal generation from email requests
• Invoice tracking and payment reminders
• Client satisfaction scoring from email tone
• Project timeline predictions based on patterns

## Example Starter Prompt
"Monitor my Gmail for emails from clients and automatically log a summary of each interaction to my client tracking spreadsheet, with follow-up reminders."