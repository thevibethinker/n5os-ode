# Syncthing Setup

**Service Type:** File Synchronization  
**Installed:** 2025-10-20  
**Version:** v2.0.10

---

## Service Details

**Service ID:** `svc_2MQCAL7uWM8`  
**Label:** syncthing  
**Protocol:** HTTP  
**Local Port:** 8384

**Public URLs:**
- **Web UI:** https://syncthing-va.zocomputer.io
- **TCP Address:** ts1.zocomputer.io:10356

---

## Configuration

**Config Location:** `/home/workspace/.config/syncthing/`  
**Working Directory:** `/home/workspace`  
**Entrypoint:** `syncthing serve --no-browser --home=/home/workspace/.config/syncthing`

**Key Files:**
- `config.xml` - Main configuration
- `cert.pem` / `key.pem` - Device certificates
- `https-cert.pem` / `https-key.pem` - Web UI certificates
- `index-v2/` - Database directory

---

## Settings

### GUI Configuration
- **Address:** 0.0.0.0:8384 (listens on all interfaces)
- **TLS:** Disabled (handled by Zo proxy)
- **Host Check:** Disabled (`insecureSkipHostCheck: true`) for public access
- **API Key:** `kEpNfMKK4HcLmx7XqPWrt6WZCjuKtVRu`

### Security Notes
⚠️ **Important:** Web UI currently has no authentication. Set username/password in Settings → GUI once accessed.

---

## Service Management

**Auto-managed by Zo:** Service automatically:
- Restarts on crash
- Persists across machine reboots
- Logs to `/dev/shm/syncthing.log` and `/dev/shm/syncthing_err.log`

**Manual commands:**
```bash
# View service status
list_user_services

# Restart service
pkill -f "syncthing serve"  # Auto-restarts

# View logs
tail -f /dev/shm/syncthing.log
tail -f /dev/shm/syncthing_err.log

# Check local access
curl http://localhost:8384
```

---

## Installation Method

Installed via official Syncthing apt repository:

```bash
# Add keyring
mkdir -p /etc/apt/keyrings
curl -fsSL https://syncthing.net/release-key.gpg | gpg --dearmor -o /etc/apt/keyrings/syncthing-archive-keyring.gpg

# Add repo
echo 'deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable-v2' | tee /etc/apt/sources.list.d/syncthing.list

# Install
apt-get update
apt-get install -y syncthing
```

---

## Usage

1. **Access Web UI:** https://syncthing-va.zocomputer.io
2. **Set Authentication:** Settings → GUI → Set username/password
3. **Add Devices:** Actions → Add Remote Device → Enter Device ID
4. **Add Folders:** Add Folder → Choose local path → Share with devices

---

## Rollback

```bash
# Remove service
delete_user_service svc_2MQCAL7uWM8

# Uninstall package
apt-get remove syncthing

# Remove configuration (optional)
rm -rf /home/workspace/.config/syncthing

# Remove apt source
rm /etc/apt/sources.list.d/syncthing.list
rm /etc/apt/keyrings/syncthing-archive-keyring.gpg
apt-get update
```

---

## Related

**Documentation:** https://docs.syncthing.net/  
**Source:** https://github.com/syncthing/syncthing

**Tags:** #infrastructure #syncthing #file-sync #service
