---
created: 2026-02-06
last_edited: 2026-02-06
version: 1
provenance: con_PpyqRcij2BIXeYLc
---
# Archetype Zo Setup Guide

This guide documents how to set up a new "Archetype Zo" instance (like zoputer.zo.computer) for the Zoffice Consultancy Stack.

## Overview

The Archetype Zo is a clean mirror that:
- Receives Level 1 exports from va.zo.computer
- Serves as the client-facing Zo personality
- Maintains its own audit trail
- Can be customized per-client engagement

## Step 1: Account Creation

1. Go to [zo.computer](https://zo.computer)
2. Sign up with your chosen handle (e.g., `zoputer`)
3. Complete email verification
4. Run through the onboarding wizard

## Step 2: API Key Setup

On the new Zo account:

1. Navigate to **Settings > Developers** (`/?t=settings&s=developers`)
2. Click "Create API Key"
3. Name it: `ZO_CONSULTING_API`
4. Copy the key immediately (it won't be shown again)
5. Store in a secure location

### Adding the key to va.zo.computer

On va, add a secret:
- Go to **Settings > Developers > Secrets**
- Add secret named: `ZOPUTER_API_KEY`
- Paste the copied API key

## Step 3: Folder Structure

Create these directories on the Archetype:

```
/home/workspace/
├── Skills/                 # Receives exports
├── Prompts/               # Receives exports  
├── Documents/
│   ├── System/           # Receives exports
│   └── consulting/       # Local docs
├── N5/
│   ├── data/
│   │   └── consulting_audit.db
│   └── scripts/
│       └── audit_logger.py
├── ZOFFICE_WORKERS/      # Persona manifests
└── CONSULTING_MANIFEST.md
```

Use this command on the Archetype:
```bash
mkdir -p Skills Prompts Documents/System Documents/consulting N5/data N5/scripts ZOFFICE_WORKERS
touch CONSULTING_MANIFEST.md
```

## Step 4: Initial Content Seeding

After folder structure is ready, va can run the export pipeline (Drop 3.1) or manually copy:

- Selected Skills with clean SKILL.md files
- System documentation
- Setup guides

## Step 5: Integration Test

From va.zo.computer, test the connection:
```bash
python3 N5/scripts/zoputer_client.py ping
```

Expected: Response showing zoputer status + audit DB entry.

## Security Notes

- The zoputer handle should remain private
- Clients interact via scheduled sessions, not direct access
- All communications are audit-logged on both sides
- Use the content-classifier (D2.2) before any export

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key rejected | Verify key copied correctly, no trailing spaces |
| Folder creation failed | Check account permissions |
| Ping fails | Check ZOPUTER_API_KEY secret is set on va |

---

*Part of the Zoffice Consultancy Stack - Build: consulting-zoffice-stack*
