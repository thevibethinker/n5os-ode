---
created: 2026-02-02
last_edited: 2026-02-03
version: 4
provenance: con_lzwdwqrkYeg9dAIv
---
# Careerspan Pipeline — Agent Memory

## Quick Context

This pipeline automates the **CorridorX × Careerspan talent matching workflow**. Shivam (CorridorX) sends JDs and candidate info; Zo processes them silently and responds only to Shivam directly.

**Key constraint:** Zo is a *silent observer* — never email employers or candidates directly, never join existing threads. Only communicate with Shivam in separate threads.

---

## Architecture Decisions (Why Things Are This Way)

### 1. Airtable as Backend, Not a Database
- Airtable was chosen because Shivam needs visibility into pipeline state
- The API can't create fields (permission issue) — schema changes are manual
- If you need new fields, update `SCHEMA_TO_ADD.md` and tell V

### 2. Action Skills (v2 Architecture)
The pipeline now uses dedicated action skills for each email type:
- **careerspan-jd-intake** → Processes [JD] emails, extracts JD details, generates Hiring POV
- **careerspan-resume-intake** → Processes [RESUME] emails, matches to jobs, generates Candidate Guides
- **careerspan-update-handler** → Processes [UPDATE] emails, classifies and routes updates

These action skills replaced the old `/zo/ask` prompt-based workers. Each skill:
- Runs as a standalone Python script
- Uses LLM (via /zo/ask) for semantic extraction only
- Returns `orchestrator_instructions` JSON for the orchestrator to execute
- Can be tested independently with `--dry-run`

### 3. Original Skills (Still Used)
The pipeline also orchestrates these existing skills:
- **careerspan-candidate-guide** → Generates Hiring POV + Candidate Guides (called by action skills)
- **careerspan-decomposer** → Processes Careerspan Intelligence Briefs into structured YAML
- **meta-resume-generator** → Creates employer-ready Candidate:Decoded PDFs

### 4. Email Tags for Routing
Shivam adds tags to email subjects:
- `[JD]` → New job description, kicks off Hiring POV flow
- `[RESUME]` → Candidate responded, triggers Careerspan invite
- `[UPDATE]` → General update, Zo interprets the body

### 5. Orchestrator v2
The orchestrator (`pipeline_orchestrator.py`) now:
- **Invokes action skills** instead of spawning prompt-based workers
- **Executes orchestrator_instructions** for Airtable/Drive/Gmail operations
- **Provides heartbeat-compatible commands** (`run`, `scan`, `process-one`)

Commands:
```bash
# Full automatic run (for heartbeat agent)
python3 pipeline_orchestrator.py run

# Scan only (returns Gmail queries)
python3 pipeline_orchestrator.py scan --execute

# Process specific email
python3 pipeline_orchestrator.py process-one --email '{"subject":"[JD]...","body":"...","from":"..."}'

# Check status
python3 pipeline_orchestrator.py status
```

### 6. Google Drive for Artifacts
All outputs (Hiring POVs, Candidate Guides, Meta-Resumes) go to a shared Drive folder Shivam can access. Structure:
```
Careerspan Pipeline Outputs/
├── <employer-slug>/
│   ├── hiring-povs/
│   └── candidates/<candidate-slug>/
```

---

## Operational Gotchas

### The 5 Core Questions
Every JD needs answers to these before it's "finalized":
1. Salary range (and whether it's hidden from candidates)
2. Location constraints (geo, remote, timezone)
3. Visa sponsorship (yes/no/required auth)
4. 90-day success criteria
5. Anti-pattern (who should NOT apply)

If a JD is missing answers, Zo sends Shivam a request. Max 2 rounds of clarification.

### Geography = Careerspan Account
Each geography (NY, SF, Bangalore, Hyderabad, Remote) maps to a separate Careerspan employer account. Candidates are assigned to accounts based on their allowed geographies.

### Ball-In-Court Tracking
Every task has a `ball_in_court` field:
- `zo` → Zo needs to process something
- `shivam` → Waiting on Shivam
- `employer` → Waiting on employer response
- `v` → V needs to make a decision

### Thread Management
Zo maintains ONE email thread per role/topic with Shivam. Subject format:
```
[Zo] JD: Senior Engineer @ TechCorp
[Zo] Candidate: Jane Doe → TechCorp
```

---

## Files in This Integration

| File | Purpose |
|------|---------|
| `config.yaml` | Central config: Airtable IDs, Drive folder, 5 Core Questions, tags, permitted senders |
| `PIPELINE.md` | Full flow diagram with all phases |
| `README.md` | Quick start for operators |
| `SCHEMA_TO_ADD.md` | Airtable schema status and field mappings |
| `scripts/pipeline_orchestrator.py` | Main entry point — run, scan, process-one, status commands |
| `scripts/drive_upload.py` | Google Drive artifact upload helper |
| `templates/shivam_response.md` | Email template for responding to Shivam |

---

## Related System Components

### Scheduled Agents
- **Careerspan Pipeline Heartbeat** — Runs every 2 hours (9am-9pm ET), scans for Shivam's emails, processes pipeline

### Webhook Receiver
- **careerspan-webhook** service — Receives Intelligence Briefs when candidates complete Careerspan Stories
- URL: `https://careerspan-webhook-va.zocomputer.io/webhook`
- Port: 8850
- See: `Integrations/careerspan-webhook/`

### Rules
- **Shivam access rule** (`3f921074-7937-423f-af9b-b6b5136b92fc`) — Restricts Shivam's email access to tagged emails only

### Action Skills (v2)
- `Skills/careerspan-jd-intake/` — [JD] email processing
- `Skills/careerspan-resume-intake/` — [RESUME] email processing
- `Skills/careerspan-update-handler/` — [UPDATE] email processing

### Original Skills
- `Skills/careerspan-candidate-guide/`
- `Skills/careerspan-decomposer/`
- `Skills/meta-resume-generator/`

### CRM
- Shivam's profile at `Knowledge/crm/individuals/shivam.md`

### Meeting Context
- `Personal/Meetings/Week-of-2026-01-19/2026-01-19_2026-01-19-Careerspan-corridorx-scoping/`

---

## When Things Go Wrong

### "Email not processed"
- Check if sender is in `config.yaml` → `permitted_senders`
- Check if subject has a valid tag (`[JD]`, `[RESUME]`, `[UPDATE]`)

### "Airtable update failed"
- Probably a schema mismatch — field doesn't exist yet
- Check `SCHEMA_TO_ADD.md` for field mappings

### "Drive upload failed"
- Check if `shared_folder_id` is set in config
- Verify vrijen@mycareerspan.com has access

### "Skill not found"
- Run `python3 scripts/pipeline_orchestrator.py status` to check skill detection
- Verify skill paths in config.yaml → skills

### "Webhook not receiving"
- Check service is running: `curl https://careerspan-webhook-va.zocomputer.io/health`
- Check logs: `tail /dev/shm/careerspan-webhook.log`
- Verify `CAREERSPAN_WEBHOOK_SECRET` is set in Zo secrets

---

## Pending Items

- [ ] **corridorx_account_id** — Fill in once Careerspan API access is provisioned (see config.yaml for instructions)
- [ ] **Careerspan API integration** — Programmatic role creation (currently manual adds)
- [ ] **Dashboard** — Pipeline status visualization

---

*Last major update: 2026-02-03 (con_lzwdwqrkYeg9dAIv) — Orchestrator v2 with action skills, replaces /zo/ask workers*