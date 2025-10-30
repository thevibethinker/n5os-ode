# Syncthing Setup Guide - Meetings Folder Sync

**Created:** 2025-10-28  
**Purpose:** Quick setup to sync `/home/workspace/Meetings/` to local machine → Google Drive

---

## ✅ Server Setup (Complete)

Your Zo server is configured and running:
- **Service:** Syncthing running as user service
- **Web UI:** https://syncthing-va.zocomputer.io
- **Device ID:** `3CFWBF3-P4AVQKP-HTZQUPO-PI2POMG-LDJMSFI-XKFIMPY-BPP4PZZ-3472NAY`
- **API Key:** `kEpNfMKK4HcLmx7XqPWrt6WZCjuKtVRu`
- **Folder Configured:** `/home/workspace/Meetings/` (ID: `meetings-sync`)
- **Current Size:** 2.7MB (68 meeting folders)

---

## 📱 Local Machine Setup (10 minutes)

### Step 1: Install Syncthing
**macOS:**
```bash
brew install syncthing
```

**Windows:**
Download from: https://syncthing.net/downloads/

**Linux:**
```bash
sudo apt install syncthing  # Debian/Ubuntu
# or
sudo dnf install syncthing  # Fedora
```

### Step 2: Start Syncthing
```bash
syncthing
```

This will:
1. Start Syncthing
2. Open web UI at http://localhost:8384
3. Generate your local device ID

### Step 3: Add Zo Server as Remote Device

In your **local Syncthing web UI** (http://localhost:8384):

1. Click **"Actions" → "Show ID"** (top right) - copy your local device ID
2. Click **"Add Remote Device"** (bottom right)
3. **Device ID:** `3CFWBF3-P4AVQKP-HTZQUPO-PI2POMG-LDJMSFI-XKFIMPY-BPP4PZZ-3472NAY`
4. **Device Name:** `Zo-Server`
5. **Sharing Tab:** Check "meetings-sync" (you'll see this after adding device)
6. Click **"Save"**

### Step 4: Approve Connection on Zo Server

1. Go to https://syncthing-va.zocomputer.io
2. You'll see a prompt: "Unknown device wants to connect"
3. Click **"Add Device"**
4. **Sharing Tab:** Check "meetings-sync"
5. Click **"Save"**

### Step 5: Configure Local Folder Path

Back in your **local Syncthing**:

1. You'll see "meetings-sync" folder appear
2. Click **"Edit"** on that folder
3. **Folder Path:** Choose where you want meetings synced
   - **Recommended:** Point to your Google Drive folder
   - Example: `~/Google Drive/Meetings/` (Mac)
   - Example: `C:\Users\YourName\Google Drive\Meetings\` (Windows)
4. Click **"Save"**

### Step 6: Verify Sync

- Initial sync will start automatically
- Watch the web UI for progress
- Should sync 2.7MB (68 folders)
- Once complete, check your Google Drive folder

---

## 🎯 Recommended Local Folder Structure

```
~/Google Drive/
└── Meetings/                     ← Point Syncthing here
    ├── 2025-09-24_external-alex-wisdom-partners-coaching/
    ├── 2025-10-23_external-mckinsey-founders-orbit-monthly-meeting/
    └── ... (all your meetings)
```

**Result:** 
- Syncthing syncs: Zo Server ↔ Local Machine
- Google Drive Desktop syncs: Local Machine ↔ Cloud
- **Two-layer redundancy** with offline access

---

## 🔧 Configuration Details

### Zo Server Settings
- **Auto-rescan:** Every 60 minutes
- **File watcher:** Enabled (10s delay)
- **Versioning:** Keep 5 versions (simple versioning)
- **Min disk free:** 1%
- **Type:** Send/Receive (bidirectional)

### What Gets Synced
- All files in `/home/workspace/Meetings/`
- All subdirectories and contents
- Bidirectional: changes on either side sync to the other

### What Doesn't Sync
- Syncthing ignores `.stignore`, `.stfolder`, temporary files
- You can add custom ignore patterns later if needed

---

## 📊 Monitoring & Management

### Check Status
- **Zo Server:** https://syncthing-va.zocomputer.io
- **Local:** http://localhost:8384
- **Logs:** Check web UI "Logs" section

### Verify Sync
```bash
# On Zo server
ls -lah /home/workspace/Meetings/ | wc -l

# On local machine
ls -lah ~/Google\ Drive/Meetings/ | wc -l
# Should match
```

### Pause/Resume
- Click device/folder in web UI
- Select "Pause" or "Resume"

---

## 🚨 Troubleshooting

### "Connection Failed"
1. Check firewall settings
2. Verify device IDs are correct
3. Try using "Dynamic" in connection settings (default)

### "Folder Path Not Found"
- Create the folder manually first
- Ensure permissions allow write access

### "Out of Sync"
- Click "Override Changes" if you know which side is correct
- Or resolve conflicts manually

### "Slow Sync"
- Initial sync takes time (2.7MB should be quick)
- Subsequent syncs only transfer changes (much faster)

---

## 🎛️ Advanced Options (Optional)

### Auto-Start Syncthing on Local Machine

**macOS:**
```bash
brew services start syncthing
```

**Linux (systemd):**
```bash
systemctl --user enable syncthing
systemctl --user start syncthing
```

**Windows:**
- Add Syncthing to startup folder
- Or use Task Scheduler

### Custom Ignore Patterns
Create `.stignore` in `/home/workspace/Meetings/`:
```
// Ignore temp files
*.tmp
.DS_Store
Thumbs.db

// Ignore specific folders
/archive/
```

### Conflict Resolution
- Syncthing creates `.sync-conflict-*` files
- Review and manually resolve
- Keep the version you want, delete the conflict file

---

## 🔐 Security Notes

- Syncthing uses TLS encryption for all transfers
- Device IDs are cryptographic identifiers
- API key controls web UI access
- Only devices you approve can connect

---

## 📝 Next Steps After Setup

1. ✅ Verify initial sync completes
2. ✅ Test: Create a file on Zo → Check local machine
3. ✅ Test: Create a file locally → Check Zo server
4. ✅ Monitor for 24 hours to ensure stability
5. ✅ Consider enabling auto-start on local machine

---

## 🆘 Need Help?

- **Syncthing Docs:** https://docs.syncthing.net/
- **Community Forum:** https://forum.syncthing.net/
- **Common Issues:** https://docs.syncthing.net/users/faq.html

---

**Status:** Ready to sync! Follow Steps 1-6 above to complete setup.

**Estimated Time:** 5-10 minutes for setup + initial sync time

**Your Device ID (save this):** `3CFWBF3-P4AVQKP-HTZQUPO-PI2POMG-LDJMSFI-XKFIMPY-BPP4PZZ-3472NAY`
