# Meeting Pipeline Architecture & Reference

## 1. Ingestion (Webhook)
**Mechanism:** External Webhook
**Entry Point:** `/home/workspace/Personal/Meetings/Inbox/`

*   Meetings are pushed to this system via an external Webhook.
*   **Input:** The webhook deposits raw meeting files (transcripts, audio, metadata) into the `Inbox` folder.
*   **Initial State:** Raw folders or files without state suffixes.

## 2. The "MG" Processing Pipeline
Once a meeting lands in the Inbox, a series of scheduled AI agents (MG-Tasks) process it sequentially using the file system as a state machine.

### **MG-1: Manifest Generation** (The "Labeler")
*   **Trigger:** Raw folders/files in Inbox (no `_[M]` or `_[P]`).
*   **Action:**
    *   Validates files.
    *   Standardizes folder naming (No nesting!).
    *   Creates `manifest.json` (The meeting's "genome").
    *   **Transition:** Renames folder to `..._[M]` (Manifest Created).

### **MG-2: Intelligence Generator** (The "Brain")
*   **Trigger:** `_[M]` folders missing core intelligence blocks.
*   **Action:**
    *   Analyzes transcript.
    *   Generates standardized Markdown blocks:
        *   `B01_DETAILED_RECAP.md`
        *   `B03_DECISIONS.md`
        *   `B05_ACTION_ITEMS.md`
        *   `B07_TONE_AND_CONTEXT.md`
        *   ...and others (B01-B26).
    *   Updates `manifest.json` with block status.

### **MG-4: Warm Intro Generator** (The "Connector")
*   **Trigger:** `_[M]` folders where V promised introductions.
*   **Action:**
    *   Detects promises like "I'll introduce you to X".
    *   Drafts `INTRO_TargetName.md` files for review.

### **MG-5: Follow-Up Generator** (The "Closer")
*   **Trigger:** `_[M]` folders needing follow-up.
*   **Action:**
    *   Generates `FOLLOW_UP_EMAIL.md` based on action items and context.

### **MG-6: State Transition** (The "Gatekeeper")
*   **Trigger:** `_[M]` folders.
*   **Action:**
    *   Checks `manifest.json` for completion (Intelligence + Artifacts done?).
    *   **Transition:** If complete, renames folder to `..._[P]` (Processed).

### **MG-7: Archival** (The "Librarian")
*   **Trigger:** `_[P]` folders in Inbox.
*   **Action:**
    *   Moves folder to `Archive/{YYYY}-Q{Q}/`.

## 3. Folder States & Suffixes
*   **`No Suffix`**: Raw, unprocessed. Touch only by MG-1.
*   **`_[M]`**: **In Progress**. Manifest exists. Intelligence being generated. User can edit drafts here.
*   **`_[P]`**: **Complete**. Fully processed and ready for archive.

## 4. For AI Agents
*   **ALWAYS** check `manifest.json` before acting.
*   **NEVER** create nested folders inside a meeting folder (flatten structure).
*   **RESPECT** the suffixes—they dictate which agent owns the folder.

