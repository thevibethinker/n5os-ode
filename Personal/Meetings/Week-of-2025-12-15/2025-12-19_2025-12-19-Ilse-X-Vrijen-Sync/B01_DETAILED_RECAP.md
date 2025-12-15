---
created: 2025-12-19
last_edited: 2025-12-19
version: 1.0
provenance: con_Dtgd0rltqEPDNjNP
---

# B01: Detailed Recap - Ilse x Vrijen Sync

## Overview
A strategic product and technical sync between Vrijen and Ilse focusing on immediate UX improvements for the Careerspan application flow, email notification systems, and the trade-offs between feature development and chat system refactoring.

## Discussion Points

### 1. Application Flow & Onboarding Improvements
- **Direct Apply Redirect**: New users coming through direct apply links will now be sent straight to the application (Vibe Check) page after onboarding, bypassing the generic welcome page.
- **Copy Updates**: Rochel is updating copy on application pages to distinguish between direct apply and manual vibe checks.
- **Time Indicators**: Implementation of clear time estimates (e.g., "5-10 minutes") for each step to improve user transparency and reduce perceived "brokenness."

### 2. The "Story Suggestion" System
- **Engagement during Loading**: Ilse is building an endpoint to generate suggestions/prompts for users to "tell a story" while analysis is loading.
- **Requirements**: Users will be required to submit at least two stories to proceed with an application.
- **Incentivization**: Vrijen suggested adding indicators like "increases your odds by X%" to encourage participation.

### 3. Email Notification & Analysis Automation
- **Backstop Emails**: Ilse is building an email system to notify users when Vibe Checks and full analyses are complete.
- **Proactive Full Analysis**: For direct apply users with high scores (e.g., >75), the system will automatically trigger the expensive full analysis without waiting for a user click, prioritizing "sexy over cheap" for UX.
- **Content**: These emails will also include tailored story suggestions.

### 4. Technical Trade-offs & Budget
- **Chat System Delay**: Feature development (Email/Suggestions) will delay deep refactoring of the chat system.
- **Bandage Fix**: Ilse will upgrade the safety check and chat models to more expensive/performant versions to mitigate current speed and friction issues.
- **Budget Approval**: Vrijen authorized an OpenAI monthly spend of up to $3,500 - $5,000 without further discussion to prioritize performance.

### 5. Administrative & Personal
- **Billing Access**: Ilse noted issues with 2FA access for billing and requested Vrijen take closer ownership of monitoring the OpenAI "purse strings."
- **Green Card Situation**: Vrijen mentioned he has temporarily misplaced his green card, causing some personal stress.

