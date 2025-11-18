# 🚀 Slack Bot Setup - Your Checklist

## Quick 5-Step Setup

### ☐ Step 1: Add Scopes (2 minutes)
https://api.slack.com/apps/A09P2SHEFRQ/oauth

Add these 4 scopes under "Bot Token Scopes":
- [ ] `app_mentions:read`
- [ ] `im:history`
- [ ] `im:read`
- [ ] `users:read`

Click "Reinstall to Workspace" → Authorize

---

### ☐ Step 2: Add Signing Secret (1 minute)
https://api.slack.com/apps/A09P2SHEFRQ/general

Copy "Signing Secret", then in Zo:
```bash
python3 /home/workspace/N5/lib/secrets.py set SLACK_SIGNING_SECRET
```
Paste the secret when prompted.

---

### ☐ Step 3: Get Your User ID (30 seconds)
```bash
python3 /home/workspace/N5/scripts/slack_get_user_id.py
```
**Copy the User ID shown** (format: U09XXXXXXXXX)

---

### ☐ Step 4: Add Yourself to Whitelist (30 seconds)
```bash
python3 /home/workspace/N5/scripts/slack_bot_config.py add <YOUR_USER_ID>
```
Replace `<YOUR_USER_ID>` with the ID from Step 3

---

### ☐ Step 5: Tell Zo You're Ready!
Message: "I've completed the Slack bot setup steps. Ready to start the service!"

I'll then:
1. Register the service
2. Give you the webhook URL  
3. You'll add it to Event Subscriptions in Slack
4. We'll test it together!

---

## Check Progress Anytime
```bash
python3 /home/workspace/N5/scripts/slack_bot_setup_wizard.py
```

---

## Need Help?
Full guide: `file 'N5/docs/slack-bot-setup-guide.md'`  
Quick reference: `file 'N5/docs/slack-bot-quick-reference.md'`  
Summary: `file 'Documents/Slack-Bot-Implementation-Summary.md'`

