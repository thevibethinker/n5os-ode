---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_yZWXJwwYvVRT8HKX
---

# Daily Briefing Agent

## Goal
Get personalized morning briefings with calendar, weather, news, and priorities automatically every day at 7 AM.

## Inputs
- Google Calendar events
- Location for weather
- News preferences
- Email for priority scan
- Personal context file

## Pipeline
• Scheduled agent triggers at 7 AM ET
• Fetch today's calendar events via Google Calendar API
• Pull weather for user's location
• Search news for specified topics/keywords
• Scan inbox for urgent emails marked priority
• Combine into structured briefing format
• Email formatted briefing to user
• SMS backup with key highlights if email fails

## First Version
Simple calendar + weather combo sent daily. Start with just "today's events + current weather" in plain text email.

## Upgrade Path
• Add news filtering by keywords
• Include commute time estimates
• Priority email scanning with AI classification
• Voice delivery via text-to-speech

## Example Starter Prompt
"Create a scheduled agent that emails me every morning at 7 AM with today's calendar events and weather for Seattle. Format it as a clean daily briefing."