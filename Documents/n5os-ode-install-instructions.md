# Installing N5OS Ode on Your Zo

Hey! Here's how to install N5OS Ode — a lightweight personal operating system that gives your Zo AI specialist personas, organized knowledge management, and semantic memory.

## What You're Getting

- **6 Specialist Personas** — Your AI routes tasks to the right specialist (Builder, Researcher, Strategist, Writer, Debugger, or Operator)
- **Smart Rules** — Automatic session tracking, YAML frontmatter on docs, protection for critical files
- **Organized Structure** — Clean folder hierarchy for knowledge, records, and prompts
- **Semantic Memory** — AI-powered search that finds content by meaning, not just keywords
- **Worker Orchestration** — Spawn parallel AI workers for complex multi-part builds

---

## Installation (5 minutes)

### Step 1: Clone the repo

Open a new conversation with your Zo and say:

```
Clone the n5os-ode repo from GitHub:
git clone https://github.com/vrijenattawar/n5os-ode.git
```

### Step 2: Run the bootloader

Once cloned, say:

```
Run @n5os-ode/BOOTLOADER.prompt.md
```

Your Zo will:
1. Create 6 specialist personas
2. Install 6 behavior rules
3. Build the folder structure
4. Initialize config files
5. Set up semantic memory
6. Validate everything works

### Step 3: Personalize (optional but recommended)

After the bootloader finishes:

```
Run @n5os-ode/PERSONALIZE.prompt.md
```

This configures your name, timezone, and integrations.

---

## Semantic Memory Setup (Optional Enhancement)

The bootloader sets up the database, but for **best quality** semantic search, add your OpenAI API key:

1. Go to **Settings > Developers** in your Zo
2. Add a secret named `OPENAI_API_KEY` with your key

Without this, semantic memory still works using local embeddings — just slightly less accurate.

### Index your documents

Once set up, you can index files for semantic search:

```python
from N5.cognition.n5_memory_client import N5MemoryClient
client = N5MemoryClient()
client.index_file("/path/to/your/document.md")
```

Or ask your Zo to index specific folders.

---

## Testing It Works

Try these to verify the installation:

1. **Test persona routing**: Ask a strategic question like "What's the best approach for X?" — should route to Strategist
2. **Test rules**: Create a new markdown file — should auto-add YAML frontmatter
3. **Test semantic memory**: Ask Zo to search your indexed content by meaning

---

## Quick Reference

| Command | What it does |
|---------|--------------|
| `@n5os-ode/BOOTLOADER.prompt.md` | Full installation |
| `@n5os-ode/PERSONALIZE.prompt.md` | Configure your settings |
| `@Journal` | Start a guided reflection |
| `@Build Capability` | Start building something new |
| `@Spawn Worker` | Create a parallel worker for a subtask |
| `@Build Review` | Orchestrate multi-worker build projects |
| `@Close Conversation` | Proper conversation wrap-up |

---

## Worker Orchestration (Power Feature)

For complex builds, you can spawn parallel workers:

1. **Spawn Worker** — Creates a self-contained AI worker for a subtask
   - "Spawn a worker to research X while I work on Y"
   - Workers run in separate conversations, report back via files

2. **Build Review** — Orchestrate multi-worker projects
   - Define a build plan with dependencies
   - Track which workers are ready, in-progress, complete
   - Spawn workers in parallel when dependencies are met

Example:
```
Spawn a research worker to investigate OAuth2 best practices.
I'll continue designing the database schema.
```

---

## Troubleshooting

**"Personas not found"**
- List your personas in Settings > Your AI > Personas
- The bootloader may have hit an error — try running it again

**"Rules not working"**
- Rules apply to *new* conversations, not the current one
- Start a fresh conversation to test

**Semantic memory errors**
- Make sure numpy is installed: `pip install numpy`
- Check that N5/cognition/brain.db exists

---

## Need Help?

Check the docs in `n5os-ode/docs/` or ask your Zo to read them for you.

Enjoy! 🚀
