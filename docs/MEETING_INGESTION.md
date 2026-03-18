---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_hbAG3moVKwj2aI3Y
---

# Meeting Ingestion Pipeline Documentation

The meeting ingestion pipeline automatically processes meeting transcripts from Google Drive, generates intelligence blocks, and syncs data to CRM systems.

## Overview

The pipeline follows this flow:

```
Google Drive → Download → Transcripts → Intelligence Blocks → CRM Sync
     ↓             ↓           ↓              ↓              ↓
Fireflies .docx → Staging → Markdown → B01-B48 Blocks → Contact Data
```

### Key Components

1. **Google Drive Integration**: Monitors designated Drive folder for new transcript files
2. **Meeting Registry**: SQLite database tracking processed meetings and state
3. **Intelligence Block Generation**: AI-powered analysis creating structured insights
4. **CRM Synchronization**: Updates contact records with meeting insights
5. **State Management**: Tracks processing stages with folder naming conventions

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ZO_CLIENT_IDENTITY_TOKEN` | **Yes** | Authentication token for Zo API calls | `auto-provided-in-zo` |
| `GOOGLE_APPLICATION_CREDENTIALS` | **Yes** | Service account JSON for Google Drive API | `/path/to/credentials.json` |
| `CRM_API_KEY` | No | API key for CRM synchronization | `your-crm-api-key-here` |
| `MEETING_REGISTRY_PATH` | No | Custom path for SQLite registry | `N5/data/meeting_registry.db` |

**Note**: `ZO_CLIENT_IDENTITY_TOKEN` is automatically available when running within Zo Computer. Manual setup is only needed for external deployments.

## Google Drive Setup

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin → Service Accounts  
3. Create new service account with name: `n5os-meeting-ingestion`
4. Download JSON credentials file
5. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### 2. Share Drive Folder

1. Navigate to your meeting transcripts folder in Google Drive
2. Click "Share" and add the service account email (ends with `@developer.gserviceaccount.com`)
3. Grant "Viewer" permissions
4. Copy the folder ID from the URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`

### 3. Configure Folder ID

Update `N5/config/drive_locations.yaml`:

```yaml
meetings:
  transcripts_inbox: "YOUR_FOLDER_ID_HERE"
```

### 4. Test Connection

```bash
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run
```

Expected output:
```
✓ Found 3 new transcripts in Drive folder
✓ Connection verified
```

## Intelligence Block Types

### External Meetings (B01-B27)

**Standard Blocks (always generated)**:

| Block | Description | Content |
|-------|-------------|---------|
| **B01_DETAILED_RECAP** | Comprehensive meeting summary | Full narrative recap with key discussions |
| **B02_COMMITMENTS** | Explicit commitments made | Who committed to what, by when |
| **B03_DECISIONS** | Key decisions with rationale | Decision points and reasoning |
| **B05_ACTION_ITEMS** | Actions with owners and deadlines | Specific tasks, assignees, due dates |
| **B08_STAKEHOLDER_INTELLIGENCE** | Insights about external participants | Contact info, roles, interests, context |
| **B25_DELIVERABLES** | Artifacts to be created | Documents, reports, materials promised |
| **B26_MEETING_METADATA** | Meeting metadata | Date, duration, participants, meeting type |

**Conditional Blocks (generated based on content)**:

| Block | Description | Trigger Conditions |
|-------|-------------|-------------------|
| **B04_OPEN_QUESTIONS** | Unresolved questions | Explicit questions or unclear decisions |
| **B06_BUSINESS_CONTEXT** | Business implications | Strategic discussions, market context |
| **B07_TONE_AND_CONTEXT** | Emotional/relationship context | Tension, excitement, relationship dynamics |
| **B10_RISKS_AND_FLAGS** | Risks and concerns | Problems, blockers, warning signs |
| **B13_PLAN_OF_ACTION** | Coordinated next steps | Complex multi-step plans |
| **B21_KEY_MOMENTS** | Significant moments/quotes | Memorable quotes, turning points |
| **B27_NEXT_MEETING** | Follow-up meeting details | Scheduled follow-ups, agenda items |
| **B28_STRATEGIC_INTELLIGENCE** | Long-term implications | Strategic insights, competitive intelligence |

### Internal Meetings (B40-B48)

Used for team meetings, co-founder syncs, internal planning:

| Block | Description |
|-------|-------------|
| **B40_INTERNAL_DECISIONS** | Internal decision points and rationale |
| **B41_TEAM_COORDINATION** | Team coordination and resource allocation |
| **B42_PROCESS_IMPROVEMENTS** | Workflow and process discussions |
| **B43_TECHNICAL_DISCUSSIONS** | Technical architecture and implementation |
| **B44_STRATEGIC_PLANNING** | Long-term planning and goal setting |
| **B45_ISSUE_RESOLUTION** | Problem-solving and conflict resolution |
| **B46_KNOWLEDGE_SHARING** | Information sharing and learning |
| **B47_OPEN_DEBATES** | Ongoing discussions without resolution |
| **B48_INTERNAL_FOLLOW_UPS** | Internal action items and next steps |

## Meeting State Management

The pipeline tracks meeting processing through folder naming suffixes:

| State | Folder Suffix | Description |
|-------|---------------|-------------|
| **Raw** | *(none)* | Transcript present, not processed |
| **Manifested** | `_[M]` | Processing manifest generated |
| **Blocked** | `_[B]` | Intelligence blocks generated |
| **Complete** | `_[C]` | CRM sync done (external meetings only) |

### State Transitions

```
2025-01-26_client-kickoff/
    ↓ (manifest generation)
2025-01-26_client-kickoff_[M]/  
    ↓ (block generation)
2025-01-26_client-kickoff_[B]/
    ↓ (CRM sync)
2025-01-26_client-kickoff_[C]/
```

**Internal meetings** stop at `[B]` state (no CRM sync).

## Usage Examples

### Daily Processing

```bash
# Check current status
python3 Skills/meeting-ingestion/scripts/meeting_cli.py status

# Pull new transcripts (preview first)
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run

# Download new transcripts
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --batch-size 5

# Process pending meetings
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process --batch-size 3

# Check results
python3 Skills/meeting-ingestion/scripts/meeting_cli.py list --processed --limit 5
```

### Specific Meeting Processing

```bash
# Process single meeting with custom blocks
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process \
    "/home/workspace/Personal/Meetings/2025-01-26_client-kickoff/" \
    --blocks B01,B05,B08,B21

# Process without CRM sync
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process \
    "/home/workspace/Personal/Meetings/2025-01-26_internal-standup/" \
    --skip-crm
```

### Automation (Scheduled Agent)

```bash
# Combined pull and process command
python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --batch-size 3 && \
python3 Skills/meeting-ingestion/scripts/meeting_cli.py process --batch-size 3
```

## Troubleshooting

### Common Issues

#### "ZO_CLIENT_IDENTITY_TOKEN not set"
**Cause**: Missing authentication token for Zo API calls.

**Solution**: 
- **Within Zo Computer**: Token is auto-provided, restart your session
- **External deployment**: Set token in environment variables
- **Testing**: Run within Zo Computer environment

```bash
# Check if token is available
echo $ZO_CLIENT_IDENTITY_TOKEN
# Should show: token-value (not empty)
```

#### "No transcript found in meeting folder"
**Cause**: Meeting folder doesn't contain transcript file.

**Requirements**:
- File must be `.md` or `.txt` format
- Minimum 100 characters of content
- Must contain recognizable speech patterns

**Solution**:
```bash
# Check folder contents
ls -la "/path/to/meeting/folder/"

# Verify file format and content
head -c 200 "/path/to/meeting/folder/transcript.md"
```

#### "Google Drive authentication failed"
**Cause**: Invalid or missing Google service account credentials.

**Solutions**:
1. **Check credentials file**:
   ```bash
   # Verify file exists and is readable
   cat "$GOOGLE_APPLICATION_CREDENTIALS" | head -5
   ```

2. **Verify service account permissions**:
   - Service account must have "Viewer" access to Drive folder
   - Email ends with `@developer.gserviceaccount.com`

3. **Test Drive connection**:
   ```bash
   python3 Skills/meeting-ingestion/scripts/meeting_cli.py pull --dry-run
   ```

#### "Block generation fails repeatedly"
**Cause**: Transcript quality or API issues.

**Diagnostic steps**:
1. **Check transcript quality**:
   ```bash
   # Count characters (minimum ~100 needed)
   wc -c transcript.md
   ```

2. **Check processing logs**:
   ```bash
   tail -50 N5/logs/meeting_processing.log
   ```

3. **Test with minimal block set**:
   ```bash
   python3 Skills/meeting-ingestion/scripts/meeting_cli.py process \
       "/path/to/meeting/" --blocks B01
   ```

4. **Clear and retry**:
   ```bash
   # Remove partial blocks and retry
   rm /path/to/meeting/B*.md
   python3 Scripts/meeting-ingestion/scripts/meeting_cli.py process "/path/to/meeting/"
   ```

#### "CRM sync fails"
**Cause**: CRM API connectivity or data formatting issues.

**Solutions**:
1. **Skip CRM for testing**:
   ```bash
   python3 Scripts/meeting-ingestion/scripts/meeting_cli.py process \
       "/path/to/meeting/" --skip-crm
   ```

2. **Check CRM credentials**:
   ```bash
   echo $CRM_API_KEY | head -10
   ```

3. **Check B08_STAKEHOLDER_INTELLIGENCE format**:
   - Must contain valid contact information
   - Email addresses must be properly formatted
   - Company names must be recognizable

#### "Duplicate meeting detected"
**Cause**: Registry already contains meeting with same date + participants.

**Investigation**:
```bash
# Check recent registry entries
python3 N5/scripts/meeting_registry.py list --limit 10

# Search for specific meeting
python3 N5/scripts/meeting_registry.py search "participant-name"
```

**Solutions**:
- **If truly duplicate**: Skip processing
- **If different meeting**: Rename folder with different participants or time
- **If registry error**: Contact system administrator

### Log Files

Monitor these log files for troubleshooting:

| Log File | Contains |
|----------|----------|
| `N5/logs/meeting_processing.log` | Block generation details |
| `N5/logs/meeting_monitor.log` | Drive folder monitoring |
| `N5/logs/meeting_orchestrator.log` | Workflow orchestration |
| `N5/logs/meeting_request_processing.log` | API request details |

### Registry Management

```bash
# View registry statistics
python3 N5/scripts/meeting_registry.py status

# List recent meetings
python3 N5/scripts/meeting_registry.py list --processed --limit 20

# Search for meetings
python3 N5/scripts/meeting_registry.py search "company-name"

# Reset meeting state (if needed)
python3 N5/scripts/meeting_registry.py reset-state "/path/to/meeting/"
```

## Directory Structure

```
Personal/Meetings/
├── Inbox/                    # Staging area for new transcripts
│   ├── 2025-01-26_client-meeting.md
│   └── 2025-01-26_team-standup.md
├── 2025-01-26_client-meeting_[C]/   # Completed external meeting
│   ├── transcript.md
│   ├── B01_DETAILED_RECAP.md
│   ├── B05_ACTION_ITEMS.md
│   ├── B08_STAKEHOLDER_INTELLIGENCE.md
│   └── manifest.json
└── 2025-01-26_team-standup_[B]/     # Completed internal meeting
    ├── transcript.md
    ├── B40_INTERNAL_DECISIONS.md
    ├── B41_TEAM_COORDINATION.md
    └── manifest.json
```

## Migration from Legacy System

This unified pipeline replaces several legacy components:

### Deprecated Agents
- `afda82fa` (Google Drive scanner)
- `MG-1` through `MG-6` (Meeting processing chain)

### Deprecated Prompts
- `Prompts/drive_meeting_ingestion.prompt.md`
- `Prompts/Analyze Meeting.prompt.md`

### Migration Steps

1. **Stop legacy agents**: Disable old scheduled tasks
2. **Clear legacy queues**: Process any pending items through old system
3. **Update configurations**: Migrate settings to new config files
4. **Test new pipeline**: Run full cycle with test meeting
5. **Switch automation**: Update scheduled tasks to use new CLI

For detailed migration notes, see `Skills/meeting-ingestion/references/legacy_prompts.md`.

## Support

For issues or questions:

1. **Check logs**: Review troubleshooting section and log files
2. **Test components**: Use `--dry-run` and minimal block sets
3. **Documentation**: Consult `Skills/meeting-ingestion/SKILL.md`
4. **System status**: Run `meeting_cli.py status` for health check