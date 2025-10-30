# Meetings Folder Structure

**Version:** 1.0  
**Created:** 2025-10-28  
**Purpose:** Canonical folder structure for meetings and Careerspan company documents

---

## Canonical Structure

### Meetings Folder
**Location:** `/home/workspace/Personal/Meetings/`

**Purpose:** Unified storage for ALL meetings (personal + company)

**Structure:**
```
/home/workspace/Personal/Meetings/
├── YYYY-MM-DD_meeting-name/          # Individual meeting folders
│   ├── transcript.md                 # Meeting transcript/notes
│   ├── recording.m4a                 # Audio recording (if applicable)
│   └── summary.md                    # AI-generated summary
```

**Naming Convention:**
- Format: `YYYY-MM-DD_context-participant-topic`
- Examples:
  - `2025-10-23_external-mckinsey-founders-orbit-monthly-meeting`
  - `2025-10-15_internal-team`
  - `2025-10-09_alex-x-vrijen-wisdom-partners-coaching`

**Special Prefixes:**
- `‼️` - High priority/urgent
- `📭` - No follow-up required

---

### N5 Records (Staging)
**Location:** `/home/workspace/N5/records/meetings/`

**Purpose:** STAGING AREA ONLY - meetings are processed here, then moved to canonical location

**Protected:** Yes (`.n5protected` - contains processing metadata)

**Contents:**
- Processing metadata files only
- Should be mostly empty after meetings are moved
- Contains: `.processed.json`, system analysis files

**DO NOT:**
- Store meetings permanently here
- Delete this folder (protected for processing system)

---

### Careerspan Documents
**Location:** `/home/workspace/Records/Company/`

**Purpose:** Careerspan company documents, proposals, emails, raw business info

**Structure:**
```
/home/workspace/Records/Company/
├── Proposals/                # Business proposals
├── Technology/               # Tech documentation
├── voice-memos/             # Voice memos (non-meeting)
├── emails/                  # Email archives
├── documents/               # General documents
└── inbox/                   # Incoming items
```

**What Goes Here:**
- Company documents and artifacts
- Proposals and business materials
- Email archives
- Voice memos (non-meeting recordings)
- Raw info related to Careerspan operations

**What Does NOT Go Here:**
- Meetings (use `/home/workspace/Personal/Meetings/`)
- Personal documents (use `/home/workspace/Personal/` or `/home/workspace/Documents/`)

---

## Migration & Future Evolution

### Personal vs Company Separation
**Current State:** Unified Meetings folder (no distinction)

**Future Evolution Path:**
When personal/company split becomes necessary:
```
/home/workspace/Personal/Meetings/
├── Company/          # Company meetings
└── Personal/         # Personal meetings
```

**Decision Criteria:**
- User explicitly requests separation
- Clear need to apply different access/sync policies
- Sufficient volume to justify complexity

**Until Then:** Keep unified structure, use naming conventions to distinguish

---

## Sync Strategy

### Syncthing Configuration
**Primary Sync Target:** `/home/workspace/Personal/Meetings/`

**Sync Flow:**
1. Zo Server: `/home/workspace/Personal/Meetings/`
2. ↕️ Syncthing bidirectional sync
3. Local Machine: `~/GoogleDrive/Meetings/` (or similar)
4. ↕️ Google Drive Desktop auto-sync
5. Cloud: Google Drive

**Rationale:**
- Local-first with cloud backup
- Two independent sync layers for redundancy
- Offline access on local machine
- No API rate limits or complexity

---

## Integration Points

### Meeting Processing Pipeline
1. **Intake:** New meetings → `N5/inbox/meeting_requests/`
2. **Processing:** Extract, transcribe, analyze → `N5/records/meetings/` (staging)
3. **Canonical Storage:** Move to → `/home/workspace/Personal/Meetings/`
4. **Cleanup:** Clear staging area, keep metadata

### Scripts That Reference Meetings
- `N5/scripts/meeting_*.py` - Should reference staging area for processing
- Post-processing scripts should reference canonical `/home/workspace/Personal/Meetings/`
- Update any hardcoded paths to use canonical location

---

## Enforcement

### AI System Rules
1. **Never create alternate meetings folders** (`Records/Company/Meetings`, `Personal/Meetings`, etc.)
2. **Always use canonical location** when storing processed meetings
3. **Check for existing structure** before suggesting new meeting storage
4. **Staging area is temporary** - meetings must migrate to canonical location
5. **Careerspan != Meetings** - separate concerns appropriately

### Protection
- `N5/records/meetings/.n5protected` - Staging area protected (contains processing metadata)
- `/home/workspace/Personal/Meetings/` - Should be backed up regularly via Syncthing + Google Drive

---

## Troubleshooting

### "Where should this meeting go?"
→ `/home/workspace/Personal/Meetings/YYYY-MM-DD_context-name/`

### "Should I create a Meetings subfolder in Records/Company?"
→ No. Use canonical `/home/workspace/Personal/Meetings/`

### "What about personal meetings?"
→ Same location for now. Use naming convention to distinguish.

### "N5/records/meetings has content"
→ That's staging. Move content to `/home/workspace/Personal/Meetings/` after processing.

### "Where do voice memos go?"
→ If meeting-related: `/home/workspace/Personal/Meetings/`  
→ If general Careerspan content: `/home/workspace/Records/Company/voice-memos/`

---

**See Also:**
- file 'Documents/N5.md' - Overall system architecture
- file 'N5/prefs/prefs.md' - System preferences
- file 'N5/scripts/n5_protect.py' - Protection system
