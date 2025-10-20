# Integration Onboarding (Customer)
**Context:** Sequestered deliverable for reflection 2025-10-20_zo-system-gtm  
**Purpose:** Step-by-step guide for connecting Gmail, Google Drive, and Google Calendar to the Zo System demonstrator clone.

---

## 0) Overview
- Goal: Enable ingestion pipelines (Reflections + Meetings) using customer’s Google services.
- Default posture: Read-only ingestion. No outbound sends without explicit approval.
- Where to connect: Customer’s Zo Computer → Settings → Connected Apps (Gmail, Google Drive, Google Calendar)

---

## 1) Prerequisites
- Customer admin/owner available to approve OAuth prompts for:
  - Gmail (read-only for ingestion)
  - Google Drive (read-only to a specific folder for reflections)
  - Google Calendar (read access to selected calendars)
- Demonstrator clone deployed and initialized
- Folder created for reflections (if Drive is used)

---

## 2) Gmail Integration (Reflections via Email)
1. Open Zo app → Settings → Connect Gmail → approve access.
2. Verify connection: tool list_app_tools(gmail) should enumerate tools (internal).
3. Configure usage:
   - Reflection emails should include subject tag: "[Reflect]"
   - Attach audio (mp3/m4a/wav/opus) or paste text body; either is supported
4. Test:
   - Send an email to the connected Gmail with subject: "[Reflect] Test: Hello World"
   - Run command 'N5/commands/reflection-ingest.md'
   - Expected outputs:
     - Registry entry: file 'N5/records/reflections/registry/registry.json'
     - Outputs (summary/detail): file 'N5/records/reflections/outputs/<slug>/'
     - Proposal (sequestered): file 'Records/Reflections/Proposals/<slug>_proposal.md' or in a dedicated folder if configured

Notes:
- Text-only reflections are wrapped into `.transcript.jsonl` automatically (worker updated).
- No messages are sent out automatically.

---

## 3) Google Drive Integration (Optional Reflections via Drive)
1. Open Zo app → Settings → Connect Google Drive → approve access.
2. Create or choose a folder for reflections (e.g., "Reflections Inbox").
3. Record folder ID and set in: file 'N5/config/reflection-sources.json' (key: drive_folder_id)
4. Test:
   - Drop a test file (audio or .txt/.md) into the Drive folder
   - Run command 'N5/commands/reflection-ingest.md'
   - Verify outputs as in Gmail test

Notes:
- Access is read-only; pipeline copies files into N5/records/reflections/incoming/ locally.

---

## 4) Google Calendar Integration (Meetings)
1. Open Zo app → Settings → Connect Google Calendar → approve access.
2. Select calendars to ingest (primary or specific team calendars).
3. Run command 'N5/commands/auto-process-meetings.md' (or your meeting pipeline command).
4. Test:
   - Create a short meeting on the connected calendar within the ingest window
   - Trigger the meeting processing command
   - Verify notes/summaries saved under appropriate Records path (per command defaults)

Notes:
- Meeting ingestion should be part of the core package; ensure schedule/triggering cadence aligns with customer workflow.

---

## 5) Smoke Tests (Quick)
- Reflection (email): Send "[Reflect] Onboarding Smoke Test" → run reflection-ingest → confirm proposal created
- Reflection (drive): Place test file in Drive folder → run reflection-ingest → confirm outputs
- Meetings: Create a 5-minute test event → run meeting processor → confirm output

---

## 6) Troubleshooting
- Not seeing Gmail/Drive/Calendar tools? Reconnect in Settings, then re-run the command.
- No files detected from Drive? Confirm folder ID in file 'N5/config/reflection-sources.json'.
- Transcript missing errors? For audio, ensure reflection-ingest is used (it transcribes). For text, worker now auto-wraps.
- Idempotence: You can safely re-run the ingest commands; duplicates are skipped via state tracking.

---

## 7) Security / Permissions
- Default scopes are read-only for ingestion flows.
- No automatic outbound email posting.
- All generated content is sequestered locally; promotion to stable knowledge requires explicit approval.

---

## 8) Handoffs & Ownership
- Customer Owner: Approves app connections and selects calendars/folders
- Operator (you): Runs commands, verifies outputs, escalates issues
- Support: Provide logs if needed (command output; see registry and outputs paths)

---

## 9) Reference Commands & Paths
- Reflection ingest: command 'N5/commands/reflection-ingest.md'
- Meeting processing: command 'N5/commands/auto-process-meetings.md'
- Outputs (reflections): file 'N5/records/reflections/outputs/<slug>/'
- Proposals (sequestered): file 'Records/Reflections/Proposals/<slug>/'
- Sources config: file 'N5/config/reflection-sources.json'
