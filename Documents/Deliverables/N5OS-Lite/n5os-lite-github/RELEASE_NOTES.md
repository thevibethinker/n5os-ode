---
created: 2025-12-10
last_edited: 2025-12-10
version: 3.0
---

# N5OS Lite v3.0.0 Release Notes

**The Agentic Upgrade**

## 📦 What's New

Version 3.0 transforms N5OS Lite from a static framework into a **dynamic, agentic operating system**. It introduces the ability for the AI to *plan*, *execute*, *spawn workers*, and *remember* context.

### 🧠 Core Intelligence
- **Build Orchestrator:** The system can now break down massive projects into parallel worker tasks (`build_orchestrator.py`).
- **Worker Spawning:** The AI can create "sub-agents" to handle tasks in parallel (`spawn_worker.py`).
- **Conversation End (Closure):** The "self-cleaning" capability that ensures threads exit gracefully (`n5_conversation_end_v2.py`).
- **Journal:** A persistent memory log for the AI (`journal.py`).

### 📂 Systems
- **Content Library v3:** A unified CLI and database for managing links, snippets, and articles.
- **CRM v3 (Lite):** A contact management CLI and schema for tracking relationships.
- **Media & Documents:** A "library card catalog" for files (`documents_media.db`).

### 📘 Workflows & Guides
- **System Design Workflow:** The standard operating procedure for designing before building.
- **Integration Guide:** Best practices for connecting external services (`integrating-services.md`).

## 📊 Package Contents

```
Total capabilities added: 8
├── Orchestration:  scripts/build_orchestrator.py
├── Workers:        workers/worker_schema.py
├── CRM:            scripts/crm_cli.py
├── Content:        scripts/content_library_v3.py
├── Journal:        scripts/journal.py
├── Closure:        schemas/conversation-end-proposal.schema.json
├── Workflows:      capabilities/workflows/system-design-workflow.md
└── Guides:         system/guides/integrating-services.md
```

## 🚀 Installation

```bash
# Extract
tar -xzf n5os-lite-v3.0.0.tar.gz -C /home/workspace/

# Setup
cd /home/workspace/n5os-lite
./setup.sh

# Initialize new databases
python3 scripts/documents_media_db_init.py
python3 scripts/journal.py init
```

---

**Built from:** V's N5 system, December 2025
**Privacy status:** ✅ Clean - No PII

