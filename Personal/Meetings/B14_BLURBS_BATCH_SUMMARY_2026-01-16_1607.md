# Blurb Generation Batch Summary

Date: 2026-01-16 16:07:39

| Meeting Directory | Status | Detail |
|-------------------|--------|--------|
| `/home/workspace/Personal/Meetings/MG6_EXECUTION_` | ✅ Success | /home/workspace/Personal/Meetings/MG6_EXECUTION_/B14_BLURBS.md |
| `/home/workspace/Personal/Meetings/Week-of-2025-12-22/2025-12-22_Monday-test` | ⏭️ Skipped/Error | Blurb generation skipped: B14 (BLURBS_REQUESTED) block not found and no other intelligence blocks (B01, B21, B02, B25) or transcripts exist in the specified directory to infer blurb requirements.

---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_Y4jjiZjkA9Cg5YOg
---

10:55:40 AM ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-15_Test-Raw-MG-1-Execution_[M]` | ⏭️ Skipped/Error | Based on my analysis of the directory `file 'Personal/Meetings/Inbox/2026-01-15_Test-Raw-MG-1-Execution_[M]'`, here is the result of the blurb generation process.

### PHASE 0: SELECTIVITY GATE
**Blurb generation skipped: INTERNAL-ONLY meeting**

**Reasoning:**
*   **Meeting Type:** The directory and transcript (`{"text": "Test meeting for MG-1 execution verification."}`) indicate this is a technical test or internal execution verification session rather than an external stakeholder meeting.
*   **Missing B14 Block:** There is no `B14_BLURBS_REQUESTED.jsonl` file or any explicit request for blurbs.
*   **No External Stakeholders:** There are no intelligence blocks (B08, B01, etc.) indicating the presence of a FOUNDER, INVESTOR, or CUSTOMER requiring an introduction or follow-up blurb.
*   **Internal Purpose:** The "MG-1 Execution" naming convention refers to the internal meeting processing stage rather than an external interaction.

Per the **Phase 0: Decision Tree** in the `Blurb-Generator` prompt, internal-only meetings do not require blurb generation.

---
**Vrijen Attawar | Careerspan**
2026-01-16 11:05:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-15_Test-Raw-Workflow_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: This is an internal test meeting (meeting name: "Test-Raw-Workflow") with a minimal placeholder transcript and no explicit blurb requests in `B14_BLURBS_REQUESTED.jsonl`. 

According to Phase 0 (Selectivity Gate) of the Blurb Generator logic:
- No explicit requests found in B14.
- No implicit promises detected in the transcript (Commitments).
- No external stakeholder identified (Founder, Investor, or Customer).

10:55:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-15_Test-Raw-Workflow_011714_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: /home/workspace/Personal/Meetings/Inbox/2026-01-15_Test-Raw-Workflow_011714_[M] contains no intelligence blocks (B01, B02, B14, B21, B25) and the transcript is a placeholder ("This is a test transcript for MG-1."). Per Phase 0 (Selectivity Gate) of the Blurb Generator protocol, generation is skipped as there are no explicit requests, implicit intro commitments, or high-value stakeholder context identified.

2026-01-16 11:21:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-16_Simulated-New-Meeting_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: Meeting lacks B14_BLURBS_REQUESTED block and the transcript ("Simulated meeting transcript content") does not contain explicit or implicit blurb requests or introduction commitments (Phase 0 Selectivity Gate).

10:59:45 AM ET/EST |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-16_Raw-Meeting-Test-A_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: Insufficient context. The transcript contains no explicit blurb requests, commitments to introduce/connect, or high-value stakeholder interactions (e.g., Founder, Investor, Customer) that would trigger automatic generation under the Selectivity Gate logic.

**Analysis:**
- **B14 (BLURBS_REQUESTED):** Not found in directory.
- **B02 (COMMITMENTS):** Not found in directory.
- **Transcript Content:** "Hello this is a transcript" (Insufficient semantic signals for implicit need).
- **Stakeholder Context:** `manifest.json` indicates no high-value stakeholder classification has been performed yet.

**Next Steps:**
If you wish to force generation, please provide the specific subject (e.g., Careerspan or V personally), the target audience, and the desired blurb type (Short or Email).

2026-01-16 11:03:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-16_Raw-Meeting-Test-B_[M]` | ⏭️ Skipped/Error | Based on the instructions in the **Blurb Generator v2.2** prompt and a review of the directory `file 'Personal/Meetings/Inbox/2026-01-16_Raw-Meeting-Test-B_[M]'`, here is the result:

### Blurb Generation Skip
**Blurb generation skipped: INTERNAL-ONLY meeting / No explicit or implicit requests found.**

### Rationale
Following the **PHASE 0: SELECTIVITY GATE** logic:
1.  **INTERNAL-ONLY?**: The `manifest.json` indicates this was a "Raw-Meeting-Test-B" processed by "MG-1_Prompt". In the absence of external stakeholder data in the directory, it is classified as a system test/internal meeting.
2.  **Explicit Requests?**: The file `B14_BLURBS_REQUESTED.jsonl` does not exist in the directory.
3.  **Implicit Commitments?**: A scan of the `transcript.jsonl` (which only contains the placeholder text "Meeting transcript content") and the `manifest.json` reveals no commitments to "introduce," "connect," or "share info."
4.  **Stakeholder Type?**: No high-value external stakeholder (FOUNDER, INVESTOR, CUSTOMER) is identified in the metadata.

---

### Reference Comparison
For your reference, I analyzed a successful execution of this prompt in `file 'Personal/Meetings/Inbox/2026-01-28_Granola-Test-Meeting_[M]'`. In that instance, the presence of a `B14_BLURBS_REQUESTED.jsonl` file with specific IDs (`BLB-001`, `BLB-002`) triggered the generation of the full `B14_BLURBS.md` artifact, including the **Fact Verification Status** table and **Forwardable Email Wrappers**.

If you would like to force generation for the test directory, please provide explicit blurb requirements (Subject, Type, Audience, and Purpose).

2026-01-16 11:15:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-16_Team-Retro_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: Internal meeting (Team Retro) and no explicit blurb requests found in B14, B02, or B25 blocks.

---
created: 2026-01-16
last_edited: 2026-01-16
version: 1.0
provenance: con_zem6e9ComeGFpgSi
--- |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-16_Client-Check-in_[M]` | ⏭️ Skipped/Error | Blurb generation skipped: Meeting is in [M] state with minimal content and no explicit blurb requests found in B14, B02, or B25 blocks. The transcript contains only placeholder text ("Sample transcript text for client check-in"), which does not trigger implicit generation criteria for FOUNDER, INVESTOR, or CUSTOMER stakeholders.

10:59:00 ET |
| `/home/workspace/Personal/Meetings/Inbox/2026-01-13_Real-Raw-Meeting_[M]/2026-01-13_Real-Raw-Meeting` | ⏭️ Skipped/Error | None |
| `/home/workspace/Personal/Meetings/Archive/2025-Q4/2025-11-14_Michael_Grady_[P]` | ✅ Success | /home/workspace/Personal/Meetings/Archive/2025-Q4/2025-11-14_Michael_Grady_[P]/B14_BLURBS.md |
| `/home/workspace/Personal/Meetings/Archive/2025-Q4/2025-10-17_Zoe_Zo-Go-To-Market-Strategy-f_[P]` | ✅ Success | /home/workspace/Personal/Meetings/Archive/2025-Q4/2025-10-17_Zoe_Zo-Go-To-Market-Strategy-f_[P]/B14_BLURBS.md |
| `/home/workspace/Personal/Meetings/Archive/2025-Q4/2025-11-13_Aaron-Mak-Hoffman_Vrijen-Attawar_[P]` | ✅ Success | /home/workspace/Personal/Meetings/Archive/2025-Q4/2025-11-13_Aaron-Mak-Hoffman_Vrijen-Attawar_[P]/B14_BLURBS.md |
| `/home/workspace/Personal/Meetings/Archive/2025-Q3/2025-09-03_Strategy_Meeting_Signal_Intelligence_[P]` | ✅ Success | /home/workspace/Personal/Meetings/Archive/2025-Q3/2025-09-03_Strategy_Meeting_Signal_Intelligence_[P]/B14_BLURBS.md |
