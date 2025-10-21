# Clone Kit Post-Clone Checklist

Status: Draft
Owner: Careerspan

## Identity & Branding
- [ ] Set organization/workspace name
- [ ] Update email display names and signatures
- [ ] Verify time zone and locale

## Secrets & Integrations
- [ ] Create .env from template and populate keys
- [ ] Connect Gmail (OAuth) and send/receive test
- [ ] Connect Google Drive and create project root folders
- [ ] Connect Notion and verify database/page access

## Filesystem & Policies
- [ ] Verify core directories exist (Knowledge, Lists, Records, N5, Documents)
- [ ] Review POLICY.md and safety toggles (dry-run defaults)
- [ ] Protect archival and system directories from destructive ops

## Commands & Scheduling
- [ ] Register commands in N5/config/commands.jsonl (if applicable)
- [ ] Enable scheduled tasks/agents needed for base pipelines
- [ ] Validate logging paths and rotation

## Pipeline Smoke Tests
- [ ] Ingest sample record → processed → knowledge update
- [ ] Email draft generation and review loop
- [ ] Meeting note capture → actions to Lists

## Finalization
- [ ] Snapshot the workspace (rollback point)
- [ ] Record decisions and customizations in Records/Operational/clone/<date>/notes.md
- [ ] Share quickstart guide with client
