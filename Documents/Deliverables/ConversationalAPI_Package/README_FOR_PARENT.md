# How to Give Conversation API to Demonstrator

**Three easy options to deploy the conversational API to demonstrator:**

---

## Option 1: Single File (Easiest)

**Give demonstrator this one file:**
```
Deliverables/ConversationalAPI_Package/install_conversation_api.sh
```

**Demonstrator runs:**
```bash
bash install_conversation_api.sh
export BOOTSTRAP_API="http://YOUR_IP:8769"
```

Done! They can now communicate with you.

---

## Option 2: Include in Bootstrap Package

**Add to your bootstrap package:**
- Copy `install_conversation_api.sh` to the bootstrap package
- Include it in the "Getting Started" instructions

**Demonstrator runs it as part of setup:**
```bash
bash install_conversation_api.sh
```

---

## Option 3: One-Line Command (If You Host It)

If you host the installer somewhere (file server, gist, etc.):

**Demonstrator runs:**
```bash
curl -fsSL http://your-server/install_conversation_api.sh | bash
```

Or with wget:
```bash
wget -qO- http://your-server/install_conversation_api.sh | bash
```

---

## What the Installer Does

1. Creates N5/scripts and N5/docs directories
2. Installs conversation client script
3. Installs usage instructions
4. Checks dependencies (installs requests if needed)
5. Tests connection to your server

**Total time:** ~5 seconds

---

## After Installation

Demonstrator needs to:
1. Set your server URL: `export BOOTSTRAP_API="http://YOUR_IP:8769"`
2. Start asking questions!

Example:
```bash
# Start conversation
CONV_ID=$(python3 N5/scripts/bootstrap_conversation_client.py --action start | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")

# Ask question
python3 N5/scripts/bootstrap_conversation_client.py \
  --action ask \
  --conversation-id $CONV_ID \
  --question "What should I do first?"

# Get your response
python3 N5/scripts/bootstrap_conversation_client.py \
  --action poll \
  --conversation-id $CONV_ID
```

---

## Your Server is Ready

✅ Server already running on port 8769  
✅ Just give demonstrator the installer  
✅ They'll be able to communicate with you immediately

**No additional setup needed on your side!**

---

**Recommended: Option 1 (single file) - simplest and most reliable.**
