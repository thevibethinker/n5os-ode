# Zo Demo Outline (General)

Purpose: Demonstrate Zo as an intelligent personal server that works through your files, commands, and agents—showing concrete, artifact‑level outcomes in minutes.

Audience: Mixed (non‑technical + technical curious). Minimize jargon; show real outcomes.

Duration variants: 10–15 min primary; 5 min lightning; 30 min deep‑dive.

---

## 0) Setup (0:00–0:30)

- Context in one sentence: “Zo lives on your server, operates on your files, and can run on its own as agents.”
- Show workspace view (folders on left, chat + files center).

## 1) Open With SSOT: Files As The Product (0:30–2:00)

- Show a live markdown note changing in real time from Zo’s actions.
- Point to “Documents/”, “Knowledge/”, “Lists/”. Emphasize open formats and visible results.

Artifact: a small note updated live (e.g., demo agenda captured).

## 2) Command‑First Workflows (2:00–4:00)

- Explain: before improvising, Zo checks registered commands and protocols.
- Trigger a simple command (e.g., list lookup or state‑session read) and show the referenced docs Zo loads.

Artifacts: command doc opened; result file or console output.

## 3) Reflection Pipeline From Email (4:00–6:30)

- Narrative: Email an audio reflection with subject “\[Reflect\]”.
- Show: attachment appears in conversation; Zo stages to `N5/records/reflections/incoming/`, transcribes, runs pipeline, and produces summary/recap for approval.
- Emphasize: nothing is auto‑published; approval gate.

Artifacts: staged audio; transcript.jsonl; proposal/summary files; approval status.

## 4) Agents (Auto‑Running Tasks) (6:30–8:30)

- Show Agents page: a recurring “news digest” or “file health check” task.
- Emphasize: tasks run without hand‑holding; outputs saved back to workspace; email optional.

Artifacts: scheduled task entry; last‑run summary file.

## 5) Integrations (8:30–10:30)

- Show one quick integration action (e.g., pull a Drive doc into Documents/, or summarize a Gmail thread into Knowledge/).
- Emphasize: your data lands as files you own.

Artifacts: imported document; generated summary note.

## 6) Safety, Approvals, and Snapshots (10:30–12:00)

- Safety: hard protections on critical files; explicit approvals for destructive actions and sends.
- Approvals: reflection outputs and automation proposals require confirmation.
- Time travel: system snapshots allow rollbacks (refer to System page).

Artifacts: show a protected file warning; show snapshot reference on System page.

## 7) Close: Value and Next Steps (12:00–13:30)

- Value: faster work, trusted outcomes, fewer SaaS silos; everything is a file.
- Next steps: create a new agent; connect Gmail/Drive; start a reflection habit.

Artifacts: new agent created; checklist for first week.

---

## Optional Branches

- 5‑minute lightning: Do sections 1, 3, and 7 only. Show reflection → summary → approval.
- 30‑minute deep dive: Add (a) list operations with command registry, (b) hosted user services (e.g., small web app via service registry), (c) distributed build pattern (workers + orchestrator overview).

---

## Live Demo Checklist

- Prepare one short audio reflection in `N5/records/reflections/incoming/` (or email it live).
- Ensure one agent is active with a recent successful run.
- Have a Drive/Gmail integration token ready and a sample file/thread to pull.
- Verify a critical file is hard‑protected to show safety prompt.
- Keep a small note open to display live file edits.

---

## Risks & Mitigations

- Integration auth friction → pre‑connect; have local fallback file.
- Long transcription time → preload a 30–60s sample; show pipeline artifacts.
- Network hiccups → demo from already staged artifacts; narrate flow.

---

## Tailoring Knobs

- Careerspan‑specific variant: emphasize job market workflows, meeting processing, and candidate collateral generation.
- Technical audience variant: show command registry, schemas, and agents’ instruction structure.