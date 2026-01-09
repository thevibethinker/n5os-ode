---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.2
---
# N5 Capability Registry

Authoritative index of **system capabilities** for this N5OS instance: internal systems, workflows, and external integrations.

## Structure

- `N5/capabilities/integrations/` – External tools & services (Fillout, Fireflies, Zapier, etc.)
- `N5/capabilities/internal/` – Internal systems (meeting pipeline, CRM v3, ZoBridge, reflection pipeline, etc.)
- `N5/capabilities/workflows/` – High‑level orchestrators, scheduled tasks, multi‑step workflows

Each capability is documented in its own markdown file with:

- **Name & ID**
- **Category** (integration / internal / orchestrator / agent / site)
- **Status** (active / experimental / deprecated)
- **What it does** and **how to use it**
- **Entry points** (prompts, scripts, URLs, agents)
- **Associated files & services**
- **Workflow** (steps and/or diagram)

### Categories & Directory Mapping

**Categories** (set in each capability's YAML block):

- `integration`
- `internal`
- `workflow`
- `orchestrator`
- `agent`
- `site`

**Directory mapping:**

- `integration` → `N5/capabilities/integrations/`
- `internal` → `N5/capabilities/internal/`
- `workflow`, `orchestrator`, `agent`, `site` → `N5/capabilities/workflows/`

**File naming convention:**

- Prefer `N5/capabilities/<subdir>/<capability_id>.md`
- `capability_id` is a kebab-case slug, e.g. `meeting-pipeline-v3`

## Current Capability Sets

### Integrations

- Fireflies Webhook Receiver – `file 'N5/capabilities/integrations/fireflies-webhook.md'` – Receives Fireflies.ai transcript-completed webhooks and logs them to SQLite for the meeting pipeline.
- Fillout Intake Event Bridge – `file 'N5/capabilities/integrations/fillout-intake-bridge.md'` – Webhook-based event bridge from Fillout form submissions into local JSONL logs for analysis.
- Akiflow Actions Bridge (Aki) – `file 'N5/capabilities/integrations/akiflow-actions-bridge.md'` – Bridges meeting-derived action items into Akiflow via Aki email workflows.
- ZoBridge Parent-Child Link – `file 'N5/capabilities/integrations/zobridge-parent-child-link.md'` – AI-to-AI bridge between ParentZo and ChildZo using the ZoBridge protocol.

### Internal Systems

- Meeting Pipeline v2 – `file 'N5/capabilities/internal/meeting-pipeline-v2.md'` – Processes meeting transcripts into structured intelligence blocks and archives completed meetings into `Personal/Meetings/Archive/`.
- CRM V3 – `file 'N5/capabilities/internal/crm-v3.md'` – Unified relationship intelligence system combining YAML profiles and SQLite for enrichment and fast queries.
- Reflection Pipeline & Knowledge Bridge – `file 'N5/capabilities/internal/reflection-pipeline-v1.md'` – Ingests voice/text reflections, generates reflection blocks, and promotes selected content into a knowledge-base database.
- Productivity Tracker / RPI System – `file 'N5/capabilities/internal/productivity-tracker-v1.md'` – Computes Relative Productivity Index, XP, levels, and streaks from email and calendar signals.
- Content Library v3 (Unified) – `file 'N5/capabilities/internal/content-library-v3.md'` – Unified content library consolidating operational links, snippets, and reference articles into single database with CLI and Python API.
- LLM Extraction Layer – `file 'N5/capabilities/internal/llm-extraction-layer.md'` – Facilitates the extraction and integration of large language model outputs into the N5OS ecosystem.
- ZoBridge Service – `file 'N5/capabilities/internal/zobridge-service-v1.md'` – Local ZoBridge HTTP service, processors, and audits that implement the ParentZo ↔ ChildZo collaboration protocol.
- Task Intelligence – `file 'N5/capabilities/internal/task-intelligence-v1.md'` – Experimental task scheduler and completion detector that uses calendar/email signals and a JSONL task registry.
- Positions System – `file 'N5/capabilities/internal/positions-system.md'` – Knowledge-tier system for capturing worldview positions with semantic search via OpenAI embeddings.
- Project Log (System Wisdom) – file 'N5/capabilities/internal/project-log.md' – Centralized log for capturing architectural, process, and tooling lessons (System Wisdom) from threads.
- Worker Prompts (Inverted Intelligence) – file 'N5/capabilities/internal/worker-prompts.md' – Library of externalized worker instructions (build, research, writer, etc.) loaded by n5_launch_worker.
- Worker Verification (Semantic Gatekeeper) – file 'N5/capabilities/internal/worker-verification.md' – Semantic Gatekeeper script to verify artifact existence and syntax validity before allowing worker submission.
- Hybrid RAG Layer for N5 Cognition – file 'N5/capabilities/internal/hybrid-rag-layer-v1.md' – Implements a large-model semantic index across Knowledge, N5 system docs, Lists, Articles, Documents (scoped), and meeting blocks using `text-embedding-3-large`. Adds a hybrid RAG layer combining BM25 keyword search, semantic embeddings, markdown-aware chunking, reranking, and metadata filters. Enables high-precision recall over Careerspan strategy, system docs, and meeting intelligence for downstream tools and prompts.
- Planning System v1 – Architect-Owned Build Planning – file 'N5/capabilities/internal/planning-system-v1.md' – Mandatory AI-executable build plans for major system work, with Architect ownership, standardized plan files, Builder gating, and optional Level Upper divergent review.
- N5 Ignore Marker System – file 'N5/capabilities/internal/n5-ignore-system.md' – Marker system for excluding directories from N5 operations. Directories containing
.n5ignored files are treated as non-existent by index rebuilds and other N5 tools
- ANN-Indexed Semantic Search – file 'N5/capabilities/internal/ann-indexed-semantic-search.md' – Capability documented in registry.
- N5OS Health Sentinel – file 'N5/capabilities/internal/n5os-health-sentinel.md' – Capability documented in registry.
- Safety & Scheduling Wrapper – file 'N5/capabilities/internal/safety-scheduling-wrapper.md' – Capability documented in registry.

### Workflows & Orchestrators

- Capability Registry v1 Orchestrator – `file 'N5/capabilities/workflows/capability-registry-v1-orchestrator.md'` – Coordinates the capability registry schema, workers, and wiring into conversation-end.
- Meeting Pipeline v2 Orchestrator – `file 'N5/capabilities/workflows/meeting-pipeline-v2-orchestrator.md'` – Coordinates MG-series agents that transform raw meetings into intelligence, follow-ups, and archived records.
- CRM V3 Unified Orchestrator – `file 'N5/capabilities/workflows/crm-v3-unified-orchestrator.md'` – Orchestrates the worker sequence that unifies legacy CRMs into the CRM V3 system.
- Knowledge Realignment v1 Workflow – `file 'N5/capabilities/workflows/knowledge-realignment-v1-workflow.md'` – Realigns all knowledge surfaces onto `Personal/Knowledge/` as single source of truth.
- Media & Documents System Orchestrator – `file 'N5/capabilities/workflows/media-documents-system-orchestrator.md'` – Orchestrates the build of the unified media/documents architecture and its workflows.
- Orchestrator Thread Workflow – `file 'N5/capabilities/workflows/orchestrator-thread-workflow.md'` – Dedicated control thread for conversation-end consistency and supervisor operations.
- System Design Workflow – `file 'N5/capabilities/workflows/system-design-workflow.md'` – Standard workflow for designing major system changes before implementation.
- Pre-Build Discovery & PRD Protocol – `file 'N5/capabilities/workflows/pre-build-discovery-prd-protocol.md'` – Grok-first discovery and PRD workflow with scoring rubric and approval gates.
- Meeting Intelligence Generator [MG-2] – `file 'N5/capabilities/workflows/meeting-intelligence-generator-mg2-agent.md'` – Agent + prompt that generates core intelligence blocks and logs MG-2 processing.
- Follow-Up Email Generator v2 [MG-5] – `file 'N5/capabilities/workflows/follow-up-email-generator-v2-agent.md'` – Agent + prompt that generates high-quality follow-up email drafts from meeting intelligence.
- Export Batch Workflow – file 'N5/capabilities/workflows/export-batch-workflow.md' – This capability standardizes how outbound export batches are created and tracked in Zo
- Build Orchestrator v2 – file 'N5/capabilities/workflows/build-orchestrator-v2.md' – LLM-driven project coordination system. Now includes 'submit', 'review', and 'approve' commands for the Validation Loop.
- Spawn Worker v2 – file 'N5/capabilities/workflows/spawn-worker-v2.md' – Parallel worker spawning system. Updated to use Inverted Intelligence (external prompt files) for worker instructions.
- Spawn Worker System (Parallel Threads) – file 'N5/capabilities/workflows/spawn-worker-system.md' – A system for spawning parallel worker threads (conversations) with rich semantic context inheritance






- [[journal-system-v1]] - Journal System (Internal)
| persona-system-v2 | Persona System v4.0 (Leveled Up) | internal | active | 2025-12-16 |
- Jobboard shortlink scan (Notion → short.io) – file 'N5/capabilities/workflows/jobboard-shortlink-scan.md' – Manual, diff-based workflow that scans the Careerspan Notion job board and creates short.io links for any untracked jobs
- Meeting Weekly Organization System – file 'N5/capabilities/workflows/meeting-weekly-organization.md' – Automatically organizes meetings from Inbox into weekly folders (Week-of-YYYY-MM-DD)



- `internal/capability-graduation-system` - [See doc](internal/capability-graduation-system.md)
