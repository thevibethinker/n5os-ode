---
created: 2026-01-26
last_edited: 2026-01-26
version: 1.0
provenance: con_gQ3hN0vs9b1ppBGw
---

# Pulse: Automated Build Orchestration

Pulse is an automated build orchestration system that manages complex multi-step builds by spawning parallel workers, monitoring their progress, and coordinating their completion. Instead of manually managing multiple concurrent tasks, Pulse handles the orchestration, monitoring, and quality control automatically.

## Overview

Pulse transforms complex builds from manual coordination nightmares into automated workflows:

```
Manual Build Process:
├── Create 6 separate tasks
├── Track each one manually  
├── Wait for dependencies
├── Manually verify outputs
└── Hope nothing breaks

Pulse Build Process:
├── Define build plan once
├── Pulse spawns all workers automatically
├── Monitors progress and handles failures  
├── Validates outputs automatically
└── Reports completion via email/SMS
```

### Key Benefits

- **Parallel Execution**: Runs multiple tasks simultaneously instead of sequentially
- **Automatic Monitoring**: Tracks progress and detects stuck or failed workers
- **Quality Control**: Validates worker outputs before considering them complete
- **Smart Recovery**: Automatically retries failed tasks or escalates when needed
- **Hands-off Operation**: Runs unattended with email/SMS notifications
- **Learning System**: Captures and applies lessons across builds

## Terminology

Pulse uses a **flow metaphor** to describe its components:

| Term | Definition | Example |
|------|------------|---------|
| **Build** | The complete orchestrated work project | "Build the new authentication system" |
| **Stream** | A batch of workers running in parallel | Stream 1: Setup tasks, Stream 2: Core features |
| **Drop** | Individual worker/task within a Stream | "D1.1: Create database schema" |
| **Current** | Sequential chain of Drops within a Stream | D1.1 → D1.2 → D1.3 (runs in order) |
| **Deposit** | Worker's completion report with artifacts | JSON file with status, outputs, and learnings |
| **Sentinel** | Monitoring agent that reports progress | Email/SMS bot that watches the build |
| **Checkpoint** | Quality gate that verifies cross-worker consistency | "Verify all APIs use same auth pattern" |

### Flow Example

```
BUILD: "E-commerce Integration"
├── Stream 1 (Setup) - Parallel execution
│   ├── Drop 1.1: Database setup ●
│   ├── Drop 1.2: API keys configuration ●  
│   └── Drop 1.3: Environment setup ●
├── Stream 2 (Core Features) - Waits for Stream 1
│   ├── Drop 2.1: Payment processing ○
│   ├── Drop 2.2: Order management ○
│   └── Drop 2.3: Email notifications ○
└── Stream 3 (Integration) - Waits for Stream 2
    └── Drop 3.1: End-to-end testing ○

Legend: ● Running  ○ Pending  ✓ Complete  ✗ Failed
```

## Quick Start

### 1. Check Build Status

```bash
# Check specific build
python3 Skills/pulse/scripts/pulse.py status my-build

# List all builds
python3 Skills/pulse/scripts/pulse.py list
```

### 2. Start a Build

```bash
# Start automated orchestration
python3 Skills/pulse/scripts/pulse.py start my-build

# Manual tick for testing
python3 Skills/pulse/scripts/pulse.py tick my-build
```

### 3. Control Running Builds

```bash
# Pause temporarily
python3 Skills/pulse/scripts/pulse.py pause my-build

# Resume paused build
python3 Skills/pulse/scripts/pulse.py resume my-build

# Stop completely
python3 Skills/pulse/scripts/pulse.py stop my-build
```

### 4. Post-Build Operations

```bash
# Finalize and generate reports
python3 Skills/pulse/scripts/pulse.py finalize my-build

# View build artifacts
ls -la N5/builds/my-build/artifacts/
```

## Creating a Build

### 1. Build Structure

Every Pulse build follows this folder structure:

```
N5/builds/my-build/
├── meta.json              # Build configuration and state
├── STATUS.md              # Human-readable progress dashboard  
├── BUILD_LESSONS.json     # Build-specific learnings
├── drops/                 # Individual worker task definitions
│   ├── D1.1-setup-db.md
│   ├── D1.2-config-api.md
│   └── D2.1-implement-auth.md
├── deposits/              # Worker completion reports
│   ├── D1.1.json
│   └── D1.2.json
└── artifacts/             # Build outputs and deliverables
```

### 2. meta.json Configuration

The `meta.json` file defines your build structure:

```json
{
  "slug": "my-build",
  "title": "My Build Title", 
  "build_type": "code_build",
  "status": "pending",
  "total_streams": 2,
  "current_stream": 1,
  "model": "anthropic:claude-sonnet-4-20250514",
  "launch_mode": "orchestrated",
  "drops": {
    "D1.1": {
      "name": "Setup database schema",
      "stream": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "status": "pending"
    },
    "D1.2": {
      "name": "Configure API endpoints", 
      "stream": 1,
      "depends_on": [],
      "spawn_mode": "auto",
      "status": "pending"
    },
    "D2.1": {
      "name": "Implement authentication",
      "stream": 2, 
      "depends_on": ["D1.1", "D1.2"],
      "spawn_mode": "auto",
      "status": "pending"
    }
  }
}
```

### 3. Worker Task Definitions

Each Drop needs a markdown file in the `drops/` folder:

**drops/D1.1-setup-db.md**:
```markdown
---
drop_id: D1.1
build_slug: my-build
stream: S1
type: code_build
status: pending
spawn_mode: auto
---

# D1.1: Setup Database Schema

## Context
Create the database schema for the e-commerce integration.

## Scope  
```yaml
files:
  - database/schema.sql (CREATE)
  - database/migrations/ (CREATE)
must_not_touch:
  - existing_database/ (preserve existing data)
```

## MUST DO
1. Design user accounts table
2. Design products table  
3. Design orders table
4. Create migration scripts
5. Test schema locally

## EXPECTED OUTPUT
Deposit should confirm schema files created and tested
```

### 4. Build Types

Pulse supports different build types optimized for different workflows:

| Build Type | Use Case | Typical Streams |
|------------|----------|-----------------|
| `code_build` | Software development, APIs, integrations | Setup → Implementation → Testing |
| `research` | Market research, competitive analysis | Gather → Analyze → Synthesize |
| `content` | Documentation, blog posts, marketing | Research → Draft → Review → Publish |
| `planning` | Strategic planning, project design | Discover → Design → Validate |

## Commands Reference

### Core Commands

```bash
# Status and monitoring
pulse.py status <build-slug>           # Check build progress
pulse.py list                          # List all builds
pulse.py list --active                 # Show only running builds

# Build control  
pulse.py start <build-slug>            # Start automated orchestration
pulse.py stop <build-slug>             # Stop build gracefully
pulse.py pause <build-slug>            # Pause temporarily 
pulse.py resume <build-slug>           # Resume paused build

# Manual operations
pulse.py tick <build-slug>             # Single tick (for testing)
pulse.py tick <build-slug> --dry-run   # Preview what tick would do

# Post-build
pulse.py finalize <build-slug>         # Run final checks and reporting
```

### Advanced Commands

```bash
# Worker management
pulse.py retry <build-slug> <drop-id>  # Retry failed worker
pulse.py skip <build-slug> <drop-id>   # Skip worker and continue

# Monitoring
pulse.py logs <build-slug>             # View build logs
pulse.py health <build-slug>           # Check build health

# Learnings management  
pulse_learnings.py list <build-slug>   # View build-specific learnings
pulse_learnings.py list-system        # View system-wide learnings
```

### SMS Commands

Text these commands to control Pulse remotely:

```
pulse stop        # Stop all builds, delete monitoring
pulse done        # Mark builds complete, delete monitoring  
pulse pause       # Pause ticking (monitoring stays alive)
pulse resume      # Resume ticking
```

## Environment Variables

Pulse requires these environment variables:

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `ZO_CLIENT_IDENTITY_TOKEN` | **Yes** | Authentication for spawning workers | *auto-provided* |
| `PULSE_EMAIL_NOTIFICATIONS` | No | Enable email notifications | `true` |
| `PULSE_SMS_NOTIFICATIONS` | No | Enable SMS notifications | `false` |
| `PULSE_MAX_CONCURRENT_DROPS` | No | Max workers running simultaneously | `20` |
| `PULSE_TICK_INTERVAL_MINUTES` | No | How often to check build progress | `5` |
| `PULSE_DEAD_DROP_TIMEOUT_MINUTES` | No | When to consider a worker stuck | `15` |

**Note**: `ZO_CLIENT_IDENTITY_TOKEN` is automatically available when running within Zo Computer.

## Monitoring and Notifications

### Sentinel Monitoring

Pulse automatically creates a **Sentinel** monitoring agent when you start a build. The Sentinel:

- Checks build progress every 5 minutes
- Sends email updates on meaningful changes
- Detects stuck or failed workers
- Provides commands to control the build
- Deletes itself when build completes

### Email Notifications

Email notifications include:

**Progress Updates**:
```
Subject: [PULSE] my-build - Stream 2 of 3 (67% complete)

## Build: my-build
**Status:** Stream 2 of 3 | **Progress:** 4/6 Drops (67%)

### Stream Status
| Stream | Status | Drops |
|--------|--------|-------|
| S1 | complete | D1.1 ✓, D1.2 ✓ |
| S2 | running | D2.1 ✓, D2.2 ⏳ (8 min) |  
| S3 | pending | - |

### Recent Activity
- D2.1 completed: "Database schema created"
- D2.2 started 8 minutes ago

### Reply Commands
Reply with: status, pause, resume, retry D2.2, skip D2.2
```

**Problem Alerts**:
```
Subject: [PULSE] my-build - Worker may be stuck

⚠️ D2.2 has been running for 18 minutes (>15 min threshold)
This may indicate the worker is stuck or encountered an error.

Reply with:
- retry D2.2 (restart the worker)
- skip D2.2 (skip and continue)
- status (get detailed status)
```

### SMS Notifications

SMS provides brief urgent alerts:

```
[PULSE] ❌ D2.2 FAILED: Database connection error. Reply 'retry' or 'skip'

[PULSE] ✅ my-build COMPLETE - 6/6 drops finished successfully
```

## Build Lifecycle

Every Pulse build goes through these phases:

### 1. Planning Phase
- Define build structure in `meta.json`
- Write Drop briefs in `drops/` folder  
- Review dependencies and sequencing
- **Status**: `pending`

### 2. Execution Phase  
- Pulse spawns workers according to Stream dependencies
- Workers execute tasks and write Deposits
- Pulse validates outputs and manages failures
- **Status**: `running`

### 3. Quality Control
- Filter validates each Deposit
- Checkpoint verifies cross-Drop consistency  
- Failed validations trigger retries or escalation
- **Status**: `validating`

### 4. Completion
- All Drops complete successfully
- Integration tests run (if configured)
- Final artifacts verified
- **Status**: `complete`

### 5. Finalization
- Build report generated
- Learnings extracted and stored
- Cleanup tasks executed  
- **Status**: `finalized`

## Integration Tests

Pulse can run automated integration tests after all workers complete:

### Test Configuration

Add to `meta.json`:

```json
{
  "integration_tests": {
    "enabled": true,
    "tests": [
      {
        "name": "API endpoints responding",
        "type": "http",
        "config": {
          "url": "http://localhost:3000/health",
          "expected_status": 200
        }
      },
      {
        "name": "Database tables created",
        "type": "command", 
        "config": {
          "command": "sqlite3 database.db '.tables'",
          "expected_output_contains": "users"
        }
      }
    ]
  }
}
```

### Test Types

| Type | Purpose | Config Options |
|------|---------|----------------|
| `http` | Test API endpoints | `url`, `method`, `expected_status`, `expected_body` |
| `command` | Run shell command | `command`, `expected_exit_code`, `expected_output_contains` |
| `file_exists` | Verify file exists | `path`, `min_size`, `max_age` |
| `service_running` | Check service status | `service_name`, `port`, `timeout` |

## Troubleshooting

### Common Issues

#### "Build not found"
**Cause**: Build folder doesn't exist or `meta.json` is malformed.

**Solution**:
```bash  
# Check if build exists
ls -la N5/builds/my-build/

# Validate meta.json
python3 -m json.tool N5/builds/my-build/meta.json
```

#### "Worker stuck at spawning"  
**Cause**: Drop brief has syntax errors or missing dependencies.

**Solution**:
```bash
# Check drop brief syntax
python3 Skills/pulse/scripts/validate_drop.py N5/builds/my-build/drops/D1.1-task.md

# Manually test drop
python3 Skills/pulse/scripts/test_drop.py my-build D1.1
```

#### "All workers failing immediately"
**Cause**: Environment setup issues or missing dependencies.

**Solution**:
```bash
# Check environment variables
echo $ZO_CLIENT_IDENTITY_TOKEN

# Test basic API connectivity  
python3 Skills/pulse/scripts/test_connectivity.py

# Check recent build logs
tail -50 N5/builds/my-build/logs/pulse.log
```

#### "Build appears stuck"
**Cause**: Dependency deadlock or worker timeout.

**Solution**:
```bash
# Check dependency graph
python3 Skills/pulse/scripts/analyze_dependencies.py my-build

# View worker status
pulse.py status my-build --verbose

# Skip problematic worker
pulse.py skip my-build D2.1
```

### Log Files

Monitor these files for troubleshooting:

| Log File | Contains |
|----------|----------|
| `N5/builds/<slug>/logs/pulse.log` | Main orchestration log |
| `N5/builds/<slug>/logs/drops.log` | Worker spawn and completion events |
| `N5/builds/<slug>/logs/sentinel.log` | Monitoring and notification log |
| `/dev/shm/pulse-<slug>.log` | Real-time build activity |

### Health Checks

```bash
# Overall build health
pulse.py health my-build

# Check individual components
pulse.py health my-build --drops      # Worker status
pulse.py health my-build --streams    # Stream dependencies  
pulse.py health my-build --system     # System resources
```

## Advanced Features

### Manual Worker Mode

For high-risk or complex tasks, set `spawn_mode: "manual"` in the Drop configuration:

```json
{
  "D2.1": {
    "name": "Critical database migration",
    "spawn_mode": "manual",
    "stream": 2
  }
}
```

When Pulse encounters a manual Drop:
1. Prints brief for you to copy
2. Sets status to `awaiting_manual`  
3. Waits for you to paste brief into new thread
4. You execute manually and write Deposit
5. Pulse detects Deposit and continues

### Jettison Builds

Create "off-ramp" builds when you hit tangents:

```bash
# Create jettison from current context
pulse jettison "debug the rate limiting issue"

# Explicit parent build
pulse jettison "explore gamification approaches" --from adhd-todo-research
```

Jettisons inherit learnings from parent builds but run independently.

### Build Lineage

Track relationships between builds:

```bash
# View full lineage tree
pulse lineage

# Show specific build ancestry  
pulse lineage my-build

# JSON output for scripting
pulse lineage --format json
```

Example output:
```
my-research-project ✓
├── j-debug-apis ⚡ ●
│   └── j-api-redesign ⚡ ○  
└── j-alternative-approach ⚡ ✓

Legend: ✓ complete ● running ○ pending ⚡ jettison
```

## Best Practices

### Build Design

1. **Keep Drops focused**: Each Drop should have one clear objective
2. **Minimize dependencies**: Reduce coupling between Drops where possible  
3. **Plan for failures**: Design graceful degradation paths
4. **Test Drop briefs**: Validate briefs before starting full build

### Monitoring

1. **Enable email notifications**: More reliable than SMS for detailed updates
2. **Set realistic timeouts**: Account for actual task complexity  
3. **Monitor regularly**: Check builds don't run unattended for days
4. **Review Deposits**: Learn from worker outputs and improve future builds

### Quality Control

1. **Use integration tests**: Verify end-to-end functionality
2. **Review learnings**: Extract insights for system improvement
3. **Clean up artifacts**: Remove temporary files after completion
4. **Document decisions**: Capture rationale in build reports

## Support

For issues with Pulse:

1. **Check build status**: Use `pulse.py status <build>` and `pulse.py health <build>`
2. **Review logs**: Check log files for error details  
3. **Test components**: Use dry-run and manual modes to isolate issues
4. **Consult documentation**: See `Skills/pulse/SKILL.md` for detailed internals

---

*Pulse is part of the n5os-ode system. For more documentation, see the `/docs` folder.*