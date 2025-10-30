# N5 OS Core - Complete Order of Operations

**Date**: 2025-10-28 05:25 ET

---

## Phase 1: User Pre-Setup (Manual, BEFORE Onboarding)

**User does this in Zo settings/UI:**

1. ✅ **Clone n5os-core repo** to their Zo account
   ```bash
   git clone https://github.com/vrijenattawar/n5os-core.git
   cd n5os-core
   ```

2. ✅ **Add manual rules** in Zo settings
   - Navigate to Zo settings → Rules
   - Add user preferences, behavior rules

3. ✅ **Connect external apps** (Zo settings → Integrations)
   - Gmail
   - Google Drive
   - Google Calendar
   - Notion
   - Any other integrations they want

4. ✅ **Add biographical information** in Zo settings
   - Name, role, company
   - Work context
   - Communication preferences

5. ✅ **Add personas** (Zo settings → Personas)
   - Vibe Builder (Bootstrap version)
   - Vibe Debugger (Bootstrap version)
   - Any custom personas

---

## Phase 2: N5 OS Onboarding (Automated/Conversational)

**NOW onboarding runs (conversational with Zo):**

### What Onboarding Does:

1. **Verify Prerequisites**
   - Check: Rules added? ✓
   - Check: Apps connected? ✓
   - Check: Bio provided? ✓
   - Check: Personas added? ✓

2. **N5-Specific Configuration**
   - Workflow preferences (how to use Knowledge, Lists, Records)
   - Automation level (conservative vs aggressive)
   - Reflection cadence (daily/weekly reviews?)
   - Command customization (custom recipes they want)
   - Scheduled tasks preferences

3. **Generate user_config/**
   ```
   user_config/
   ├── profile.json          # N5-specific preferences
   ├── workflows.json        # Workflow automations
   ├── custom_recipes/       # User's custom recipes
   └── scheduled_tasks.json  # Auto-created agents
   ```

4. **Personalize System**
   - Generate custom recipes based on their connected apps
   - Set up scheduled tasks (if requested)
   - Configure Knowledge indexing preferences
   - Set up their workflow automation

5. **Validate Setup**
   - Test: Can access connected apps? ✓
   - Test: Recipes execute? ✓
   - Test: Session state works? ✓
   - Test: All configs valid? ✓

6. **Generate Welcome Guide**
   - Personalized to THEIR setup
   - References THEIR connected apps
   - Shows THEIR custom recipes
   - Next steps specific to THEIR preferences

---

## Key Insight

**Onboarding is NOT collecting basic info.**

Onboarding is:
- Verifying prerequisites
- Configuring n5os-core system behavior
- Personalizing workflows/automation
- Generating configs that work with their existing setup

**Prerequisites must be complete BEFORE onboarding.**

---

## Updated Onboarding Focus

### Interview Questions Should Ask:

1. **Workflow Preferences**
   - "How do you want to use Knowledge vs Lists vs Records?"
   - "What's your preferred way to capture information?"
   
2. **Automation Level**
   - "How much automation do you want? (Manual/Balanced/Aggressive)"
   - "Should Zo auto-file items or always ask?"

3. **Reflection Cadence**
   - "Daily standups?"
   - "Weekly reviews?"
   - "End-of-conversation summaries?"

4. **Custom Workflows**
   - Based on connected apps: "Want recipes for Gmail processing?"
   - Based on role: "Want CRM-style contact management?"

5. **Safety Preferences**
   - "Dry-run by default?"
   - "Always confirm before writes?"

---

## Files Onboarding Creates

**user_config/ (gitignored):**
```
user_config/
├── profile.json              # N5 preferences
├── workflows/
│   ├── email_processing.json
│   ├── knowledge_capture.json
│   └── reflection_schedule.json
├── custom_recipes/
│   ├── my_gmail_process.md
│   ├── my_daily_review.md
│   └── my_contacts_sync.md
└── .onboarding_complete       # Timestamp marker
```

**NOT in user_config (uses Zo settings):**
- Rules (already in Zo)
- Personas (already in Zo)
- App connections (already in Zo)
- Bio (already in Zo)

---

## Onboarding Trigger

**After manual setup complete**, user runs:
```
/onboard
```

Or auto-triggers on first n5os-core conversation if prerequisites detected.

---

**This changes the onboarding spec significantly.**

Should I revise the full spec based on this order?

*Created: 2025-10-28 05:25 ET*
