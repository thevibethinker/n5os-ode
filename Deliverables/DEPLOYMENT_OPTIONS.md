# Deploying Conversation API to Demonstrator

**Status:** Package ready in `Deliverables/ConversationalAPI_Package/`

---

## The Simple Answer

**Give demonstrator ONE file:**
```
Deliverables/ConversationalAPI_Package/install_conversation_api.sh
```

**They run:**
```bash
bash install_conversation_api.sh
export BOOTSTRAP_API="http://YOUR_IP:8769"
```

**Done!** They can now ask you questions.

---

## "Can't You Send It Over Yourself?"

**The situation:**
- You (parent) are in your workspace: `/home/workspace` (va.zo.computer)
- Demonstrator is in their workspace: `/home/workspace` (their separate Zo)
- These are **separate machines/accounts** - I can't directly access their filesystem

**What I CAN do:**
1. ✅ Package everything into a single installer (done!)
2. ✅ Create instructions for them (done!)
3. ❌ Can't directly write to their workspace (different machine)

**What YOU can do:**
- **Option A:** Send them the installer file via file sharing
- **Option B:** Include installer in your bootstrap package
- **Option C:** Put installer on a web server, give them a curl command

---

## Deployment Methods

### Method 1: File Transfer (Simplest)

**Share this file with demonstrator:**
```
Deliverables/ConversationalAPI_Package/install_conversation_api.sh
```

Or the compressed package:
```
Deliverables/ConversationalAPI_Package.tar.gz (4.4 KB)
```

**How to share:**
- Email it
- Upload to shared location
- Use Zo's file sharing (if available)
- Copy via any file transfer method

**Demonstrator extracts and runs:**
```bash
tar -xzf ConversationalAPI_Package.tar.gz
bash ConversationalAPI_Package/install_conversation_api.sh
```

---

### Method 2: Host It Yourself

**If you have a web server or can host files:**

1. Put `install_conversation_api.sh` on your server
2. Give demonstrator this one command:

```bash
curl -fsSL http://YOUR_SERVER/install_conversation_api.sh | bash
```

Example with Python HTTP server:
```bash
cd Deliverables/ConversationalAPI_Package
python3 -m http.server 8080

# Then tell demonstrator:
curl -fsSL http://YOUR_IP:8080/install_conversation_api.sh | bash
```

---

### Method 3: Include in Bootstrap Package

**Add to your existing bootstrap package:**
- Copy installer to the package
- Update bootstrap instructions to run it
- Demonstrator gets it as part of initial setup

---

### Method 4: Manual Installation (If Needed)

If file transfer doesn't work, demonstrator can:

1. Create the client file manually:
   ```bash
   curl http://YOUR_IP:8769/help > setup_guide.txt
   # Then follow instructions
   ```

2. Or copy-paste the client code from:
   `N5/scripts/bootstrap_conversation_client.py`

---

## What's Already Done on Your Side

✅ Server running on port 8769  
✅ All endpoints tested and working  
✅ Ready to receive questions  

**You don't need to do anything else on your side!**

Just get the installer file to the demonstrator somehow.

---

## After They Install

**Demonstrator needs to:**
1. Set your server URL: `export BOOTSTRAP_API="http://YOUR_IP:8769"`
2. Start using it!

**You need to:**
1. Monitor questions: `tail -f N5/logs/bootstrap_conversations.jsonl`
2. Respond when you see questions (I can help with this!)

---

## Recommended Approach

**Best for most cases:**
1. Send `install_conversation_api.sh` file to demonstrator
2. Tell them to run it
3. Give them your server IP for BOOTSTRAP_API
4. Start communicating!

**Total time:** <1 minute for them to set up

---

## Files Ready for Transfer

All in `Deliverables/ConversationalAPI_Package/`:

- `install_conversation_api.sh` - The installer (send this!)
- `README_FOR_PARENT.md` - Instructions for you
- `SEND_THIS_TO_DEMONSTRATOR.txt` - Message to include when you send it
- `ConversationalAPI_Package.tar.gz` - Everything compressed (4.4 KB)

**Pick one file and send it!** 🚀
