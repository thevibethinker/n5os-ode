# N5 Minimal Bootstrap Package

**Version:** 1.0.0  
**Philosophy:** Minimal files, maximum guidance from parent Zo  
**Size:** <10 KB (vs 360 KB for full package)

---

## What This Is

A **ultra-slim** N5 bootstrap that:
- ✅ Creates directory structure
- ✅ Connects to parent Zo for guidance
- ✅ Fetches only what you need, when you need it
- ✅ Minimal code = minimal failure points

**Not included:** Scripts, configs, schemas (pull from parent as needed)

---

## Installation (30 seconds)

### Step 1: Upload to New Zo
Upload `bootstrap_minimal.py` to your new Zo workspace

### Step 2: Run
```bash
cd /home/workspace
python3 bootstrap_minimal.py
```

### Step 3: Follow Instructions
The script will:
1. Create N5 directory structure
2. Fetch conditional rules from parent
3. Create parent connection client
4. Give you next steps

**That's it!**

---

## How It Works

### Mobius Maneuver
Parent Zo runs at: `https://n5-bootstrap-support-va.zocomputer.io`

**You can:**
- Query for help
- Fetch files as needed
- Get troubleshooting guidance
- Pull scripts/configs on demand

**You cannot:**
- Modify parent (read-only)
- Write to parent
- Break parent system

### Pull, Don't Push
Instead of copying everything upfront:
1. Bootstrap creates structure
2. You work with Zo AI
3. AI helps you pull what you need from parent
4. System grows organically

---

## After Bootstrap

### Get Help
```bash
# Troubleshooting
python3 N5/scripts/n5_connect_parent.py help/troubleshooting.md

# Dependencies
python3 N5/scripts/n5_connect_parent.py help/dependencies.txt

# Quick fixes
python3 N5/scripts/n5_connect_parent.py fixes/common_issues.md
```

### Add Conditional Rules
Critical! Copy rules from `N5/CONDITIONAL_RULES.md` to your Zo Settings.

### Start Using
Ask your Zo AI:
- "Help me add my first piece of knowledge"
- "How do I process a meeting?"
- "Show me available commands"

Your Zo has the bootstrap persona and knows how to help.

---

## Advantages

### Minimal Bootstrap
- **Fewer files** → Fewer things to break
- **Smaller package** → Faster transfer
- **Less code** → Easier to understand
- **Pull on demand** → Only get what you need

### Parent Guidance
- Real-time help during setup
- Troubleshooting from working system
- No guessing about configs
- Living documentation

### Flexible Growth
- Start minimal
- Add features as needed
- Customize from day one
- No bloat

---

## Files Included

```
bootstrap_minimal.py    (~200 lines - everything you need)
README.md              (this file)
```

**That's it!** Everything else comes from parent Zo when you need it.

---

## Comparison

| Feature | Minimal | Full Package |
|---------|---------|--------------|
| **Size** | <10 KB | 360 KB |
| **Files included** | 2 | 226 |
| **Setup time** | 30 sec | 10 min |
| **Risk** | Low | Medium |
| **Flexibility** | High | Medium |
| **Requires parent** | Yes | No |

**Use Minimal when:**
- You want simplest possible setup
- You have reliable internet
- You want to customize heavily
- You trust the pull-on-demand model

**Use Full when:**
- You want everything upfront
- Limited internet access
- Want to work offline
- Prefer complete package

---

## Parent Zo Connection

**URL:** https://n5-bootstrap-support-va.zocomputer.io  
**Status:** Active and ready  
**Mode:** Read-only  
**Purpose:** Guide your bootstrap journey

Test connection:
```bash
curl https://n5-bootstrap-support-va.zocomputer.io/README.md
```

---

## Support

1. **Conditional rules first:** Copy from N5/CONDITIONAL_RULES.md to Zo settings
2. **Read:** Documents/N5.md after bootstrap
3. **Ask Zo AI:** It has the bootstrap persona loaded
4. **Query parent:** Use n5_connect_parent.py
5. **Discord:** https://discord.gg/zocomputer

---

**Minimal bootstrap, maximum guidance.** 🚀

*Installation in 30 seconds | Parent Zo ready to help*

**06:48 PM ET | Fri, Oct 18, 2025**
