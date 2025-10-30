---
description: Configure N5 OS Core system (run once after manual setup)
tags:
  - setup
  - system
  - onboarding
  - first-run
---

# N5 Onboarding

**Configure your N5 OS Core system after completing manual prerequisites.**

---

## Prerequisites (Manual Setup FIRST)

Before running onboarding, you must:

1. ✅ Add rules in Zo settings
2. ✅ Connect apps (Gmail, Drive, Notion, Calendar)
3. ✅ Add bio in Zo settings
4. ✅ Add personas (Vibe Builder Bootstrap, Vibe Debugger Bootstrap)

**Without these, onboarding will fail.**

---

## What Onboarding Does

1. **Verifies** manual setup complete
2. **Configures** N5 workflow systems (Lists, Meetings, Digests, etc.)
3. **Sets** automation level (Manual/Semi-Auto/Auto)
4. **Creates** your `user_config/` (personal, gitignored)
5. **Validates** everything works (12 tests)
6. **Generates** personalized welcome guide

**Takes**: 10-15 minutes  
**Interactive**: Yes (6 questions)

---

## How to Run

### Preview (Dry Run)

See what onboarding will do without making changes:

```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py --dry-run
```

### Real Run

Actually configure your system:

```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py
```

### Reset and Re-Run

Start over if needed:

```bash
python3 /home/workspace/n5os-core/N5/scripts/n5_onboard.py --reset
```

---

## What You'll Be Asked

1. **Workflow systems** - Which to enable (Lists, Meetings, Digests, Social, CRM)
2. **Automation level** - Manual, Semi-Auto, or Auto
3. **Scheduled tasks** - Which to set up
4. **Conversation end** - How Zo should behave at conv end
5. **Git safety** - Protection preferences
6. **Telemetry** - Opt-in or out

**Tip**: Choose Semi-Auto for most users. You can change later.

---

## What Gets Created

After onboarding:

```
n5os-core/
└── user_config/           # Your personal config (gitignored)
    ├── preferences.json   # N5 system settings
    ├── telemetry_settings.json
    ├── .onboarding_complete
    └── README.md

Documents/
└── WELCOME.md             # Your personalized guide
```

---

## After Onboarding

1. **Read** `Documents/WELCOME.md` (your personalized guide)
2. **Try** `/conversation-end` to test recipes
3. **Explore** `Lists/` and `Knowledge/`
4. **Customize** `user_config/preferences.json` anytime

---

## Troubleshooting

### Prerequisites Check Fails

Make sure you completed ALL manual steps:
- Rules in Zo settings
- Apps connected
- Bio provided
- Personas added

### Already Onboarded

If you see "Onboarding already complete":
```bash
python3 N5/scripts/n5_onboard.py --reset
```

### Validation Fails

Check:
1. Is `n5os-core` in `/home/workspace/`?
2. Are all Phase 0-5 systems installed?
3. Is `.gitignore` properly configured?

---

## Re-Configuration

To change settings later:

1. **Edit directly**:
   ```bash
   nano user_config/preferences.json
   ```

2. **Or re-run onboarding**:
   ```bash
   python3 N5/scripts/n5_onboard.py --reset
   ```

Changes take effect immediately.

---

## Help

- **Docs**: `Documents/System/ONBOARDING_GUIDE.md`
- **GitHub**: https://github.com/vrijenattawar/n5os-core
- **Issues**: https://github.com/vrijenattawar/n5os-core/issues

---

**Ready? Complete manual prerequisites, then run onboarding!**

*N5 OS Core - Phase 0.5*
