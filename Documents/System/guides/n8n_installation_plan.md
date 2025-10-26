# n8n Installation Plan for Zo
**Status:** Ready to execute | **Date:** 2025-10-22

---

## What is n8n?
Open-source workflow automation platform (like Zapier, but self-hosted). Visual node-based editor for building automations.

## Cost Analysis

### On Zo Computer
**License:** Free (Apache 2.0) – $0
**Hosting:** Uses existing Zo resources – $0 additional
**Resource Usage:**
- CPU: ~100-300MB RAM idle, spikes during workflow execution
- Disk: ~500MB install + workflow storage
- No per-workflow or per-execution fees

**Total:** $0 (covered by your existing Zo plan)

### vs. n8n Cloud
- n8n Cloud: Starts at $20/month for 2,500 workflow executions
- Self-hosted on Zo: Unlimited executions, $0

---

## Installation Method

### Option 1: npm (Recommended for Zo)
```bash
# Install globally
npm install n8n -g

# Start with tunnel (publicly accessible for webhooks)
n8n start --tunnel

# Or start locally only
n8n start
```

**Pros:**
- npm already installed on Zo (v10.9.2) ✅
- Simple one-command install
- Easy to update (`npm update n8n -g`)
- No Docker required

**Cons:**
- Runs as foreground process (need to daemonize for 24/7)

### Option 2: Docker (Not available)
- Zo doesn't have Docker installed
- Would require installing Docker first
- More complex, unnecessary for n8n

---

## Deployment Plan

### Phase 1: Install (5 min)
```bash
# Install n8n globally
npm install n8n -g

# Verify install
n8n --version
```

### Phase 2: Test Run (5 min)
```bash
# Start with tunnel for testing (public webhook access)
n8n start --tunnel

# Access at: http://localhost:5678
# Tunnel URL provided in terminal output
```

### Phase 3: Register as User Service (10 min)
```bash
# Register with Zo's service manager
# This makes n8n persistent, auto-restart, public URL
```

Use `register_user_service`:
- **label:** n8n-automation
- **protocol:** http
- **local_port:** 5678
- **entrypoint:** `n8n start`
- **workdir:** /home/workspace

**Result:** Permanent URL like `https://n8n-automation-va.zo.computer`

### Phase 4: Configure (10 min)
- Create owner account
- Set up webhook endpoints
- Connect to Akiflow via IFTTT/API
- Test first workflow

---

## What n8n Unlocks for Akiflow

### Immediate
1. **Calendar Read Bridge**
   - Webhook → IFTTT "List Tasks for a Date" → Parse JSON
   - Zo can query V's Akiflow agenda programmatically
   
2. **Conditional Task Routing**
   - If task contains "urgent" → Priority: High
   - If mentions meeting name → Auto-link to Records folder
   
3. **Multi-Step Workflows**
   - Generate tasks → Check conflicts → Propose times → Push to Aki
   
4. **Error Handling**
   - Retry failed pushes
   - Log all Akiflow interactions
   - Alert on failures

### Future
5. **Smart Scheduling**
   - Read V's calendar → Find free slots → Suggest task times
   - Respect work hours, meeting buffer zones
   
6. **Batch Optimization**
   - Group related tasks by project
   - Minimize email count to Aki
   
7. **Bidirectional Sync**
   - Akiflow completes task → Webhook → Update N5 Records
   - Track completion rates, patterns

8. **Integration Hub**
   - Connect Akiflow to Gmail, Google Calendar, Notion
   - Cross-platform workflows (e.g., "When email starred → Create task → Schedule follow-up")

---

## Risk Assessment

**Low Risk:**
- No data loss risk (read-only Akiflow queries)
- Sandboxed environment (runs in isolated service)
- Can uninstall cleanly (`npm uninstall n8n -g`)

**Mitigations:**
- Start with read-only workflows (test calendar queries)
- Dry-run all write operations first
- Keep existing direct email push as fallback

---

## Recommendation

**Execute now:** 30-minute total investment unlocks powerful automation layer.

**Sequence:**
1. Install n8n via npm (5 min)
2. Test basic workflow (hello world) (5 min)
3. Register as user service (10 min)
4. Build Akiflow calendar read bridge (10 min)

**Or defer:** Current direct email push is working. Add n8n when:
- Need calendar-aware scheduling
- Want visual workflow editor
- Hit complexity limits with scripts

Your call!

---

## Next Steps (If Proceeding)
1. Confirm: Install now or defer?
2. If now: I'll run the install sequence
3. Set up first workflow: Akiflow calendar reader
4. Test, verify, document

---

## References
- n8n Install Docs: https://docs.n8n.io/hosting/installation/npm/
- n8n Akiflow Integrations: Search n8n community for Akiflow nodes
- Zo User Services: See `list_user_services` docs
