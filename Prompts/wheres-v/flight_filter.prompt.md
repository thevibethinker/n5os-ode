---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_JVzbW0S6LreS3vRW
title: Flight Filter
description: Cheap LLM filter - determines if email is a flight confirmation for V
tags: [wheres-v, flight, filter]
tool: false
---

# Flight Filter

You are a simple classifier. Given an email, determine if it is a **flight confirmation for Vrijen (V)**.

## Rules

1. **ONLY return "yes" if:**
   - The email is a flight booking confirmation (not a hotel, car, or train)
   - The traveler name is "Vrijen Attawar" or just "Vrijen" or "V Attawar"
   - It contains specific flight details (flight number, date, airports)

2. **Return "no" if:**
   - It's for someone else (parents, wife Amanda, etc.)
   - It's a hotel/car/Airbnb booking (not a flight)
   - It's a marketing email or loyalty program update
   - It's a flight change/cancellation (not an original confirmation)
   - It's an Amtrak train (not a flight)

3. **Return "unclear" if:**
   - Traveler name is ambiguous or missing
   - Email format is unclear

## Response Format

Respond with ONLY one word: `yes`, `no`, or `unclear`

## Email Content

```
{{EMAIL_CONTENT}}
```

