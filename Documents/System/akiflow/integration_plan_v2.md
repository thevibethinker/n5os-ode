# Akiflow Integration Plan v2
**Updated:** 2025-10-22 | **Status:** Ready for implementation

---

## Revised Approach: Direct + Future n8n

### Phase 1: Direct (Implement now)
**Timeline:** 2-3 hours | **Complexity:** LOW

1. **Write path (Zo → Akiflow):** Email bridge via va@zo.computer
   - Implement `akiflow-push` command wrapper around Gmail
   - Test multi-task batch parsing (file 'Documents/System/akiflow/test_multi_task_email.md')
   - Wire to meeting transcripts, warm intros, daily planning

2. **Read path (Akiflow → Zo):** IFTTT queries
   - Use `List Tasks for a Date` query → webhook → N5
   - Store results in `Records/akiflow/tasks_<date>.json`
   - Enable "what's on my agenda" queries

**Advantages:**
- Zero infrastructure overhead
- Works immediately
- No new services to manage
- Fallback if n8n proves complex

---

### Phase 2: n8n Advanced (Future)
**Timeline:** TBD | **Complexity:** MEDIUM-HIGH

n8n enables richer workflows:
- Conditional routing (if overdue → escalate; if tag=urgent → SMS)
- Data transformations (e.g., parse meeting notes → split into per-attendee tasks)
- Bi-directional sync (Zo creates task → Akiflow → Zo updates status)
- Advanced scheduling (chain 5-step onboarding sequences)

**n8n on Zo setup (when ready):**
```bash
# Method 1: npm (simpler, already installed)
npm install n8n -g
n8n start --tunnel  # or register_user_service for persistent

# Method 2: Docker (if we add Docker support later)
# Docker is NOT currently installed on Zo
```

**Decision point:** Implement Phase 1 now; revisit n8n when:
- Direct integration shows friction
- Need conditional logic beyond simple email
- Want visual workflow editor

---

## Corrected Details

### Sender Configuration
**Preferred sender:** va@zo.computer (always)
- Already allowlisted in Aki settings (screenshot confirms)
- **CC rule:** If stuck in loop >3 exchanges with Aki, auto-CC attawar.v@gmail.com

### Product Name
**Correction:** Product is "Akiflow" not "AccuFlow"
- Update all profiles, scripts, docs to use "Akiflow"

---

## Implementation Next Steps

1. **Multi-task email experiment** (5 min)
   - Confirm: Aki email, Projects/Tags, timing
   - Send test from file 'Documents/System/akiflow/test_multi_task_email.md'
   - Verify: 3 tasks created with correct fields

2. **Package `akiflow-push` command** (30 min)
   - Wrap gmail-send-email with:
     - Task schema validation
     - Batch formatting
     - Dry-run mode
     - Result ledger
   - Register in file 'N5/config/commands.jsonl'

3. **IFTTT read bridge** (30 min)
   - Create IFTTT applet: List Tasks → Webhooks → N5 endpoint
   - Store in Records/akiflow/
   - Document in file 'Knowledge/AI/Profiles/akiflow_aki.md'

4. **Playbook wiring** (60 min)
   - Meeting → action items → akiflow-push
   - Warm intro standard pack
   - Daily "plan my day" handoff

---

## n8n Technical Notes (For Future)

**Installation on Zo:**
- npm ✅ (v10.9.2 installed)
- Docker ❌ (not installed; would need `apt install docker.io`)
- Recommendation: Start with npm install (simpler, no new dependencies)

**n8n + Akiflow capabilities:**
- Native Akiflow node via IFTTT integration [^1]
- Gmail native node for email parsing [^2]
- Webhooks for Zo → n8n → Akiflow chains [^3]
- Schedule triggers for daily batches [^4]

**Resources:**
- n8n Docs: https://docs.n8n.io/hosting/installation/npm/
- n8n + Akiflow via IFTTT: https://ifttt.com/akiflow
- Community guide: https://community.n8n.io/t/an-easy-step-by-step-guide-on-how-to-self-host-n8n/6505

---

## Comparison: Direct vs n8n

| Feature | Direct (Phase 1) | n8n (Phase 2) |
|---------|------------------|---------------|
| Setup time | 5 min | 30-60 min |
| Maintenance | None | Service monitoring |
| Visual editor | No | Yes |
| Conditional logic | Manual (scripts) | Native |
| Multi-step workflows | Sequential scripts | Drag-and-drop |
| Complexity | LOW | MEDIUM |
| Cost | $0 | $0 (self-hosted) |

**Recommendation:** Start Phase 1, defer Phase 2 until friction/need confirmed.

---

[^1]: https://ifttt.com/akiflow/actions/create_task
[^2]: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.gmail/
[^3]: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
[^4]: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/
