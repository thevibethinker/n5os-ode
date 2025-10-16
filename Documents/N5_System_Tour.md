# N5 System Tour

**A Personal Operating System for Knowledge Work**

Version: 1.0  
Last Updated: 2025-10-14  
Audience: New users, partners, team members

---

## What is N5?

N5 is a **personal operating system** that transforms how knowledge workers manage information, execute workflows, and work with AI. It's built on three core principles:

1. **Knowledge as infrastructure** — Information is structured, portable, and reusable
2. **Commands over clicks** — Workflows are codified, repeatable, and improvable
3. **AI as collaborator** — Automation follows human-readable principles

Think of it as: **file system + workflow engine + AI agent = personal OS**

---

## Quick Visual Overview

```
┌─────────────────────────────────────────────────────┐
│                  YOUR WORKSPACE                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Knowledge/          ← Single Source of Truth       │
│    ├── architectural/    (principles, standards)    │
│    ├── market_intelligence/  (insights, research)   │
│    └── [domain]/         (organized by topic)       │
│                                                      │
│  Lists/              ← What Needs Doing             │
│    ├── action_items.md                              │
│    ├── priorities.md                                │
│    └── detection_rules.md                           │
│                                                      │
│  Records/            ← Staging & Processing         │
│    ├── Company/          (work materials)           │
│    ├── Personal/         (personal projects)        │
│    └── Temporary/        (ephemeral work)           │
│                                                      │
│  N5/                 ← The Operating System         │
│    ├── commands/         (reusable workflows)       │
│    ├── scripts/          (automation tools)         │
│    ├── schemas/          (data structures)          │
│    ├── config/           (system settings)          │
│    └── prefs/            (user preferences)         │
│                                                      │
│  Documents/          ← Documentation                │
│    ├── System/           (how-tos, guides)          │
│    └── Archive/          (historical records)       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. **Knowledge/** — Your Information Brain

**Purpose:** Permanent, portable knowledge that outlives any single project

**Structure:**
- `architectural/` — System principles, standards, design patterns
- `market_intelligence/` — Research insights, competitive analysis
- `[domain]/` — Topic-specific knowledge organized by domain

**Key Features:**
- **Single Source of Truth (SSOT)** — One canonical place for each piece of knowledge
- **Portable** — Markdown-based, works anywhere, no vendor lock-in
- **AI-readable** — Structured for both humans and AI agents

**Example:**
```
Knowledge/
├── architectural/
│   ├── architectural_principles.md    (P0-P21: design rules)
│   └── system_design_workflow.md      (how to build things)
├── market_intelligence/
│   └── aggregated_insights_GTM.md     (stakeholder research)
└── professional/
    └── coaching_frameworks.md         (expertise repository)
```

---

### 2. **Lists/** — Your Action Dashboard

**Purpose:** Track what needs doing, what's blocked, what's critical

**Structure:**
- `action_items.md` — Current tasks and next actions
- `priorities.md` — Strategic focus areas
- `detection_rules.md` — Patterns to watch for (risks, opportunities)

**Key Features:**
- **Simple text-based** — No complex task management software
- **Context-rich** — Links to relevant knowledge and records
- **AI-parseable** — Agents can read, update, and act on lists

**Example:**
```markdown
## High Priority

- [ ] Complete GTM strategy document [file 'Records/Company/gtm_strategy.md']
- [ ] Review architectural principles with team
- [ ] Schedule pilot with 3 employers (see [file 'Knowledge/market_intelligence/aggregated_insights_GTM.md'])
```

---

### 3. **Records/** — Your Working Space

**Purpose:** Staging area for materials that will either become Knowledge or get archived

**Structure:**
- `Company/` — Work-related materials (meetings, projects, drafts)
- `Personal/` — Personal projects and explorations
- `Temporary/` — Short-lived working files

**Key Features:**
- **Ephemeral by design** — Not permanent storage
- **Processing pipeline** — Records → refined → Knowledge or Archive
- **Separation of concerns** — Work vs. personal vs. temporary

**Workflow:**
```
Raw input → Records/ → Process → Knowledge/ (if reusable)
                               → Documents/Archive/ (if historical)
                               → Delete (if obsolete)
```

---

### 4. **N5/** — The Operating System

**Purpose:** The machinery that makes everything work

#### 4.1 **commands/** — Reusable Workflows

Commands are procedures stored as markdown files, callable like functions.

**Example Command:** `command 'N5/commands/process-meeting-notes.md'`

```markdown
# Process Meeting Notes

1. Read transcript from Records/Company/meetings/
2. Extract action items → Lists/action_items.md
3. Extract insights → Knowledge/[relevant_domain]/
4. Archive transcript → Documents/Archive/
```

**Why Commands Matter:**
- **Repeatability** — Run the same workflow consistently
- **Improvability** — Update once, improve everywhere
- **AI-executable** — AI agents can run commands autonomously

#### 4.2 **scripts/** — Automation Tools

Python scripts that handle complex operations:
- `meeting_intelligence_orchestrator.py` — Process meeting recordings
- `git_check_v2.py` — Automated git safety checks
- `n5_safety.py` — Pre-flight safety validations

**Key Pattern:** All scripts include:
- Dry-run mode (`--dry-run` flag)
- Logging to stdout (ISO timestamps)
- Error handling with exit codes
- State verification before claiming completion

#### 4.3 **schemas/** — Data Structures

JSON schemas that enforce consistency:
- `index.schema.json` — How knowledge is indexed
- `lesson.schema.json` — How lessons are captured
- `command.schema.json` — How commands are defined

**Why Schemas Matter:** They ensure AI and human interpretations stay aligned.

#### 4.4 **config/** — System Settings

- `commands.jsonl` — Registry of all available commands
- `triggers.jsonl` — Automatic command invocation rules

**Example:** When you say "process this meeting," N5 looks up the command in `commands.jsonl` and executes it.

#### 4.5 **prefs/** — Your Preferences

- `operations/` — Operational preferences (how to run tasks)
- `communication/` — Communication preferences (how AI should respond)
- `scheduled-task-protocol.md` — Rules for scheduled automation

---

### 5. **Documents/** — Documentation Hub

**Purpose:** How-tos, guides, and historical records

**Structure:**
- `System/` — System documentation, guides, runbooks
- `Archive/` — Historical records, completed projects

**Key Distinction:**
- **Knowledge/** = reusable insights (timeless)
- **Documents/** = specific documentation (time-bound)

---

## How It Works: Example Workflows

### Workflow 1: Processing a Meeting

**User action:** "Process yesterday's meeting with Rajesh"

**N5 execution:**
1. **Locate file:** Check `Records/Company/meetings/` for Rajesh meeting
2. **Execute command:** Run `command 'N5/commands/process-meeting-notes.md'`
3. **Extract insights:** Pull key quotes and insights
4. **Update Knowledge:** Add insights to `Knowledge/market_intelligence/`
5. **Update Lists:** Extract action items to `Lists/action_items.md`
6. **Archive:** Move transcript to `Documents/Archive/meetings/`

**Result:** Meeting becomes searchable knowledge + trackable actions

---

### Workflow 2: Building a New System Component

**User action:** "Build a script to analyze competitor pricing"

**N5 execution:**
1. **Load principles:** Read `file 'Knowledge/architectural/architectural_principles.md'`
2. **Follow design workflow:** Use `command 'N5/commands/system-design-workflow.md'`
3. **Ask clarifying questions:** Ensure requirements are clear (P0: Context)
4. **Design with constraints:**
   - P1: Human-readable code
   - P7: Include dry-run mode
   - P11: Define failure modes
   - P15: Complete before claiming success
5. **Build script:** Create `N5/scripts/competitor_pricing_analyzer.py`
6. **Test in isolation:** Run with `--dry-run` first
7. **Document:** Add README and register in `commands.jsonl`

**Result:** Production-ready script following architectural standards

---

### Workflow 3: Researching a Topic

**User action:** "Research community-led growth strategies"

**N5 execution:**
1. **Search existing knowledge:** Check `Knowledge/` for related content
2. **Gather external data:** Web research, saved articles
3. **Stage in Records:** Save raw materials to `Records/Temporary/research/`
4. **Synthesize insights:** Extract key themes, patterns, contradictions
5. **Create knowledge artifact:** Write `Knowledge/growth/community_led_growth.md`
6. **Clean up:** Archive or delete temporary research files

**Result:** Organized, reusable knowledge ready for future reference

---

## Key Design Principles

N5 follows 22 core principles (P0-P21). Here are the most critical:

### **P0: Rule-of-Two (Context Management)**
Load maximum 2 config files at once. Need more? Stop and ask.

**Why:** Prevents context overload and hallucination

---

### **P5: Anti-Overwrite Protection**
Never overwrite existing work without explicit confirmation.

**Why:** Protects against accidental data loss

---

### **P7: Dry-Run First**
Always test with `--dry-run` before executing destructive operations.

**Why:** Preview changes before committing

---

### **P15: Complete Before Claiming**
Don't report "done" until verification confirms completion.

**Why:** Eliminates false positives and incomplete work

---

### **P16: No Invented Limits**
Don't fabricate API limits or constraints. Cite docs or say "don't know."

**Why:** Maintains trust through accuracy

---

### **P19: Error Handling is Mandatory**
All scripts must include try/except blocks and meaningful error messages.

**Why:** Graceful degradation beats silent failure

---

### **P21: Document Assumptions**
Every placeholder or TODO requires a docstring explaining why.

**Why:** Future maintainers understand context

---

[Full principles: `file 'Knowledge/architectural/architectural_principles.md'`]

---

## What Makes N5 Different?

### Traditional Approach
```
Information scattered across:
├── Email threads
├── Slack conversations
├── Google Docs
├── Notion pages
├── Local files
└── Your brain

Result: Can't find anything, can't reuse anything, can't automate anything
```

### N5 Approach
```
Information organized by:
├── Permanence (Knowledge vs. Records)
├── Purpose (SSOT vs. working files)
└── Actionability (Lists vs. reference)

Result: Everything is findable, reusable, and automatable
```

---

## Getting Started: The First Week

### Day 1: Setup Structure
Create the core directories:
```bash
mkdir -p Knowledge/{architectural,market_intelligence}
mkdir -p Lists
mkdir -p Records/{Company,Personal,Temporary}
mkdir -p N5/{commands,scripts,schemas,config,prefs}
mkdir -p Documents/{System,Archive}
```

### Day 2: Load Principles
Read and internalize:
- `file 'Knowledge/architectural/architectural_principles.md'`
- `file 'Documents/N5.md'` (system overview)

### Day 3: Create Your First Command
Write a simple command in `N5/commands/`, like:
```markdown
# Daily Standup

1. Review Lists/action_items.md
2. Note progress on each item
3. Identify blockers
4. Update priorities
```

### Day 4: Build Your First Knowledge Artifact
Take something from your head and write it down:
- A process you follow repeatedly
- A framework you use for decisions
- Lessons learned from a project

### Day 5: Process Existing Materials
Take 5 items from your scattered information and organize them:
- Meeting notes → Extract insights → Knowledge/
- Action items from email → Lists/action_items.md
- Project files → Records/Company/[project_name]/

### Day 6: Automate Something Small
Pick one repetitive task and write a script for it.
Start simple: even a 10-line Python script counts.

### Day 7: Review & Reflect
- What's working? What feels clunky?
- What information do you access most often?
- What workflows would benefit most from automation?

---

## Common Use Cases

### For Entrepreneurs
- **Knowledge:** Market research, competitive intelligence, frameworks
- **Lists:** Product roadmap, hiring pipeline, investor updates
- **Records:** Meeting notes, pitch decks, customer interviews
- **Commands:** Process customer feedback, generate weekly metrics report

### For Consultants
- **Knowledge:** Client frameworks, best practices, case studies
- **Lists:** Client deliverables, engagement pipeline
- **Records:** Client projects (separate folder per client)
- **Commands:** Generate client reports, process discovery interviews

### For Researchers
- **Knowledge:** Literature summaries, research frameworks, methodologies
- **Lists:** Experiments to run, papers to read, collaborators to contact
- **Records:** Experimental data, draft papers, analysis scripts
- **Commands:** Process experiment results, generate paper drafts

### For Product Managers
- **Knowledge:** Product principles, user research insights, competitive analysis
- **Lists:** Feature backlog, user interview queue, partnership pipeline
- **Records:** Product specs, user interview transcripts, analytics reports
- **Commands:** Process user interviews, generate sprint summaries

---

## Advanced Features

### 1. Command Composition
Commands can call other commands:

```markdown
# Weekly Review (command 'N5/commands/weekly-review.md')

1. Execute command 'N5/commands/process-all-meetings.md'
2. Execute command 'N5/commands/update-priorities.md'
3. Execute command 'N5/commands/generate-weekly-summary.md'
```

### 2. Automated Triggers
N5 can watch for patterns and auto-execute:

```jsonl
{"trigger": "new_file_in_Records/Company/meetings/", "command": "process-meeting-notes"}
{"trigger": "friday_5pm", "command": "weekly-review"}
```

### 3. Scheduled Tasks
Recurring automation via Zo Computer's scheduler:

- Daily: Process inbox, update task list
- Weekly: Generate summary, review priorities
- Monthly: Archive completed projects, update knowledge index

### 4. Safety Validations
Pre-flight checks before destructive operations:

```python
# N5/scripts/n5_safety.py validates:
- No overwrites of Knowledge/ files without confirmation
- Dry-run execution for bulk operations
- Git commit status before major changes
- Backup verification before deletions
```

---

## Integration with Zo Computer

N5 is designed to work seamlessly with Zo Computer (your AI-powered workspace):

### AI Agent Integration
- **Context awareness:** AI loads relevant Knowledge files automatically
- **Command execution:** AI can run N5 commands autonomously
- **Safety enforcement:** AI respects architectural principles (P0-P21)
- **Preference adherence:** AI follows your N5 prefs automatically

### Scheduled Tasks
```
Zo Computer Scheduler → N5 Commands → Automated workflows
```

Example: "Every Monday at 9am, process all weekend meetings and email me the summary"

### Terminal Integration
Run N5 scripts directly from Zo Computer terminal:
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py --dry-run
```

---

## Success Metrics: Is N5 Working?

### Week 1-2
- [ ] All new information goes into structured locations (no orphan files)
- [ ] You can find any piece of information within 30 seconds
- [ ] You've created 3+ commands for repeated workflows

### Month 1
- [ ] Knowledge/ contains 10+ reusable artifacts
- [ ] You've automated 3+ manual workflows
- [ ] AI can execute commands without supervision
- [ ] Context switching time reduced by 50%

### Month 3
- [ ] Knowledge base is your primary reference (not Google/ChatGPT)
- [ ] New projects start 3x faster (templates + existing knowledge)
- [ ] You've trained others on your N5 system
- [ ] System has grown organically (new commands, new knowledge domains)

---

## Troubleshooting

### "I can't find anything"
**Solution:** Improve naming and indexing
- Use consistent naming: `file snake_case.py`, `file kebab-case.md`
- Create index files: `Knowledge/index.md` with links to major topics
- Use grep search: `grep -r "search term" Knowledge/`

### "My Records/ folder is a mess"
**Solution:** Weekly processing ritual
- Friday afternoon: Review Records/
- Promote reusable content → Knowledge/
- Archive historical content → Documents/Archive/
- Delete obsolete content → trash

### "Commands aren't working"
**Solution:** Check command registry
- Verify command exists in `N5/config/commands.jsonl`
- Check command syntax (must be valid markdown)
- Test command execution manually before automation

### "AI isn't following principles"
**Solution:** Explicit principle loading
- Add to user rules: "Load `file 'Knowledge/architectural/architectural_principles.md'` before system work"
- Reference specific principles: "Follow P15 (Complete Before Claiming)"
- Create persona with principle enforcement (see Vibe Builder persona)

---

## Further Reading

### Core Documentation
- `file 'Documents/N5.md'` — System overview and philosophy
- `file 'Knowledge/architectural/architectural_principles.md'` — Full P0-P21 principles
- `file 'N5/commands/system-design-workflow.md'` — How to build N5 components

### Example Workflows
- `file 'N5/scripts/README.md'` — Script documentation
- `file 'Documents/Archive/2025-10-08-Refactor/Final_Summary.md'` — Major refactor case study
- `file 'N5/prefs/operations/scheduled-task-protocol.md'` — Automation safety guidelines

### Advanced Topics
- `file 'N5/schemas/index.schema.json'` — Data structure standards
- `file 'N5/lessons/'` — Lessons learned archive (meta-knowledge)

---

## Contact & Support

**Creator:** Vrijen Attawar (V)  
**System Version:** N5 (Fifth iteration of personal OS)  
**Platform:** Built on Zo Computer (va.zo.computer)

**Questions?** Reference this document when onboarding team members or explaining N5 to partners.

---

**Document Status:** Living document, updated as N5 evolves  
**Last Review:** 2025-10-14  
**Next Review:** 2025-11-14

---

*"The best system is the one you actually use. Start simple, evolve thoughtfully, and let the system grow with your needs."*
