---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_yZWXJwwYvVRT8HKX
---

# Health Tracking & Smart Alerts

## Goal
Monitor health metrics and send personalized alerts when patterns suggest needed interventions.

## Inputs
- Daily health logs (sleep, energy, symptoms)
- Fitness tracker data exports
- Supplement intake tracking
- Environmental factors (weather, travel)

## Pipeline
• Daily SMS prompts for subjective health metrics
• Import fitness tracker data via API or CSV
• AI analyzes trends and correlations across data sources
• Identify concerning patterns (low energy + poor sleep)
• Generate actionable intervention suggestions
• Send SMS alerts with specific recommendations
• Track intervention effectiveness over time

## First Version
Simple daily SMS check-in that logs responses and sends weekly summary of patterns.

## Upgrade Path
• Integration with Apple Health/Google Fit
• Supplement optimization based on symptom patterns
• Sleep quality correlation with productivity metrics
• Predictive alerts before patterns worsen

## Example Starter Prompt
"Send me a daily SMS asking about my energy level and sleep quality, then analyze trends and alert me when patterns suggest I need to adjust my routine."