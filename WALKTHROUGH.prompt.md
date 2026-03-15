---
title: N5OS Ode Walkthrough
description: Interactive guided tour of N5OS Ode features — teaches new users how to use the system through hands-on demos
version: 1.0.0
tool: true
tags: [n5os, onboarding, tutorial, walkthrough]
created: 2026-03-15
---

# N5OS Ode Walkthrough

Welcome to N5OS Ode! This is a guided tour that walks you through the key features by **doing** them, not just reading about them. It takes about 10 minutes.

> **Prerequisites:** You should have already run `@BOOTLOADER.prompt.md` and `@PERSONALIZE.prompt.md`. If you haven't, do those first.

---

## How This Works

I'll present a menu of features you can explore. Pick whichever interests you — no need to go in order. Each one takes 1-3 minutes and ends with a quick recap of what happened.

After each section, you'll return to the menu. Type **done** anytime to finish the tour.

---

## Feature Menu

Here's what we can explore together. Pick a number to start:

1. **🎭 Persona Routing** — Watch your AI switch between specialist modes in real time
2. **📝 Block System** — Turn a meeting transcript into structured intelligence
3. **📓 Journal** — Write your first journal entry with guided reflection
4. **🛡️ Safety System** — See file protection in action
5. **🔍 Context Loading** — Load task-specific knowledge on demand
6. **📂 Your Workspace** — A quick tour of where things live
7. **🐙 GitHub Setup** — Connect your workspace to version control

Type a number (1-7) or **all** to go through everything, or **done** to finish.

---

## 1. Persona Routing

**What it is:** N5OS Ode has 6 specialist personas — like switching between different experts depending on what you need. The Operator (your default) decides who should handle each request.

**Try it now:**

Let's see routing in action. I'll show you how three different requests go to three different specialists.

**Step 1:** Ask me something strategic, like:
> "What are the pros and cons of starting a newsletter?"

Watch what happens — I'll switch to the **Strategist** persona, which is tuned for weighing options and thinking through decisions.

**Step 2:** Now ask me to write something, like:
> "Draft a short intro email for a new client"

I'll switch to the **Writer**, who's focused on tone, clarity, and communication.

**Step 3:** Now ask a factual question, like:
> "What is semantic memory?"

I'll stay as the **Operator** for quick lookups, or route to the **Researcher** for deeper dives.

### What Just Happened

You saw the same AI behave differently depending on the task — not because it's different software, but because each persona carries different instructions about *how* to think. The Strategist asks clarifying questions before advising. The Writer focuses on voice and audience. The Operator stays efficient and direct.

**You can always say** "switch to [Persona]" to manually pick one, or let the Operator route automatically.

➡️ **Back to menu** — pick another number, or type **done**.

---

## 2. Block System

**What it is:** Blocks are structured templates that extract specific intelligence from meeting transcripts. Instead of reading a 30-minute transcript and trying to remember what was decided, blocks pull out recaps, decisions, commitments, and open questions automatically.

**Let's try it.** I'm going to create a sample transcript in your workspace, run a block generator on it, and then clean up.

### Step 1: Create the sample transcript

I'll place a sample meeting transcript at `Records/sample-walkthrough-transcript.md`. This is a fictional project planning meeting between two people — Alex and Jordan — discussing a product launch.

```
Create this file at Records/sample-walkthrough-transcript.md:

---
title: Sample Meeting — Product Launch Planning
date: 2026-01-15
attendees: Alex Chen (Product Lead), Jordan Park (Marketing)
duration: 22 minutes
type: walkthrough-demo
---

Alex: Alright, let's figure out the launch timeline. We said Q2 originally but I think we should push to May specifically.

Jordan: May works. That gives us six weeks of runway for the landing page and email sequence. Are we still doing the early access list?

Alex: Yes, definitely. I want at least 200 signups before we go live. That's our validation threshold.

Jordan: Got it. So the early access page needs to go up by... mid-March? That's tight but doable.

Alex: Mid-March for the page, then we run it for six weeks. If we don't hit 200 by end of April, we revisit the positioning before launch.

Jordan: Makes sense. What about pricing? Last time we talked about three tiers but I think two is cleaner.

Alex: I agree. Let's go with two tiers — a free plan and a pro plan at $29/month. We can always add an enterprise tier later if there's demand.

Jordan: $29 feels right for the market. I looked at competitors last week — most are between $19 and $49. We're in the sweet spot.

Alex: Perfect. One more thing — I want to do a soft launch with just the early access list before we do any public marketing. Give them a week to use it, collect feedback, then open it up.

Jordan: Smart. So the sequence is: early access page goes up mid-March, collect signups through April, soft launch to that list first week of May, public launch mid-May.

Alex: Exactly. And if the early access feedback is bad, we have a two-week buffer before public launch to fix things.

Jordan: Who's handling the onboarding flow? That's the part I'm most worried about.

Alex: I'll own that. I want to keep it under three screens. Name, use case, done.

Jordan: Three screens is ambitious but I like it. Can you have a prototype by end of March?

Alex: Yeah, I'll have a clickable prototype by March 30th.

Jordan: Great. I think we're aligned. I'll start on the landing page copy this week.

Alex: Sounds good. Let's check in again next Tuesday.
```

### Step 2: Generate some blocks

Now let's extract intelligence from that transcript. I'll run three block generators:

- **B01 (Detailed Recap)** — A structured summary of what was discussed
- **B03 (Decisions Made)** — Every decision, who made it, and why
- **B02 (Commitments)** — Who promised to do what, and by when

Watch how each block pulls different signal from the same conversation.

### Step 3: Review the output

Look at the blocks that were generated. Notice:
- **B01** gives you context you'd want if you missed the meeting
- **B03** captures the *why* behind decisions (two tiers because competitors are $19-$49)
- **B02** turns vague discussion into trackable commitments with dates

This is what N5OS does with real meeting transcripts when you connect Google Drive and use the Meeting Ingestion skill.

### Step 4: Clean up

Now I'll delete the sample transcript and any generated blocks — they were just for demonstration.

### What Just Happened

You just saw raw conversation turned into structured, searchable intelligence. In real use, you'd connect Google Drive, and N5OS would pull transcripts automatically and generate all relevant blocks.

➡️ **Back to menu** — pick another number, or type **done**.

---

## 3. Journal

**What it is:** A guided reflection system. Instead of staring at a blank page, the AI asks you questions and compiles your answers into a journal entry stored in a local database.

**Let's do a quick one.** We'll use the Gratitude reflection — it's the shortest (about 2 minutes).

### Try it now

Say something like:
> "Let's do a quick gratitude entry"

I'll ask you 2-3 questions. Answer naturally — even one sentence per answer is fine. When we're done, I'll save it to your journal database at `N5/data/journal.db`.

### After your entry

You can always:
- **List entries:** `python3 N5/scripts/journal.py list`
- **Search:** `python3 N5/scripts/journal.py search "gratitude"`
- **View one:** `python3 N5/scripts/journal.py view 1`

Other reflection types (Morning Pages, Evening Reflection, Weekly Review) go deeper — try them when you have more time.

### What Just Happened

You created a journal entry through conversation, not typing into a text file. The entry is stored in a searchable database, tagged by type and date. Over time, patterns emerge — you can search across weeks or months of reflections.

➡️ **Back to menu** — pick another number, or type **done**.

---

## 4. Safety System

**What it is:** N5OS protects important directories from accidental deletion or moves. It uses `.n5protected` marker files — like a "do not disturb" sign on a hotel door.

**Let's see it work.**

### Step 1: Check what's protected

I'll run the protection checker:

```bash
python3 N5/scripts/n5_protect.py list
```

This shows every directory that has a `.n5protected` marker and why it's protected.

### Step 2: Try a protected operation

Now watch what happens when I try to interact with a protected directory. I'll attempt to check whether we can delete the `N5/` folder:

```bash
python3 N5/scripts/n5_protect.py check N5/
```

The system will warn me that this path is protected and explain why. It doesn't *block* the operation — it makes sure I (and you) know the risk before proceeding.

### Step 3: How to protect your own folders

If you create a folder with important data, you can protect it:

```bash
python3 N5/scripts/n5_protect.py protect Records/ --reason "Personal journal and meeting records"
```

And if you ever need to remove protection:

```bash
python3 N5/scripts/n5_protect.py unprotect Records/
```

### What Just Happened

You saw a lightweight but effective safety net. No complex permissions — just marker files that trigger warnings before destructive operations. It's designed for the real risk: your AI accidentally deleting something important because you said "clean up this folder."

➡️ **Back to menu** — pick another number, or type **done**.

---

## 5. Context Loading

**What it is:** Instead of loading every preference and protocol into every conversation (which would be slow and expensive), N5OS loads context *on demand* based on what you're working on.

**Let's see the difference.**

### Step 1: Load build context

Say:
> "Load context build"

I'll run:
```bash
python3 N5/scripts/n5_load_context.py build
```

This loads coding-specific preferences — things like language selection rules, refactoring protocols, and debug logging behavior. Stuff that's useful when building, but irrelevant when writing an email.

### Step 2: Load a different context

Now try:
> "Load context writer"

Different set of preferences loads — writing style, voice, tone guidelines. The system knows which files to pull for each task type.

### Available Contexts

| Command | Loads preferences for |
|---------|----------------------|
| `build` | Coding, implementations, scripts |
| `strategy` | Planning, decisions, frameworks |
| `research` | Deep analysis, source evaluation |
| `writer` | Emails, docs, polished content |
| `safety` | Destructive operations, file moves |
| `scheduler` | Scheduled tasks, agents |
| `system` | System admin, database ops |

### What Just Happened

You loaded task-specific context on demand. This is what makes N5OS efficient — your AI doesn't carry the weight of every protocol in every conversation. It pulls in what it needs, when it needs it.

➡️ **Back to menu** — pick another number, or type **done**.

---

## 6. Your Workspace

**What it is:** A quick orientation of where things live in your N5OS workspace.

### The key folders

| Folder | What lives here | You'll use it for |
|--------|----------------|-------------------|
| `N5/` | System intelligence — config, scripts, preferences | Rarely touch directly |
| `N5/prefs/` | Your preferences and protocols | Customizing AI behavior |
| `N5/scripts/` | Utility scripts that power features | Running commands |
| `Knowledge/` | Long-term reference material | Saving articles, notes, research |
| `Records/` | Date-organized records | Meeting notes, project logs |
| `Prompts/` | Reusable workflow prompts | Running block generators, builds |
| `Skills/` | Packaged workflow systems | Meeting ingestion, build orchestration |
| `docs/` | Reference documentation | Understanding how things work |

### The key files

| File | Purpose |
|------|---------|
| `BOOTLOADER.prompt.md` | Re-run to repair or update installation |
| `PERSONALIZE.prompt.md` | Update your personal settings |
| `WALKTHROUGH.prompt.md` | This tour (you're in it now!) |
| `N5/prefs/prefs.md` | Your core preferences file |

### Pro tip

You can always ask me "where does X live?" or "where should I put this?" — the Operator persona is specifically trained to know your workspace layout.

➡️ **Back to menu** — pick another number, or type **done**.

---

## 7. GitHub Setup

**What it is:** Connecting your workspace to GitHub gives you version control — the ability to track changes, undo mistakes, and keep a backup of your workspace on the cloud.

### Why you want this

- **Undo anything** — Every saved change can be reversed
- **Cloud backup** — Your workspace is backed up to GitHub automatically
- **History** — See what changed, when, and why

### Step 1: Check if Git is already set up

I'll check your current git status:

```bash
git status
git remote -v
```

If you see a remote URL, you're already connected. If not, we'll set it up.

### Step 2: Create a GitHub repository

If you don't have a GitHub account yet:
1. Go to [github.com](https://github.com) and sign up (free)
2. Create a new repository — name it something like `my-workspace` or `n5os-workspace`
3. Set it to **Private** (recommended — your workspace has personal data)
4. Don't add a README or .gitignore (we already have those)

### Step 3: Connect your workspace

Once you have a repo URL, tell me:
> "Connect my workspace to GitHub — my repo is github.com/YOUR_USERNAME/YOUR_REPO"

I'll run:
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git add -A
git commit -m "Initial N5OS Ode workspace"
git push -u origin main
```

### Step 4: Set up the GitHub CLI (optional but recommended)

The GitHub CLI (`gh`) lets you interact with GitHub from the command line. On Zo, it's already installed. To authenticate:

```bash
gh auth login
```

Follow the prompts — choose GitHub.com, HTTPS, and authenticate with your browser.

### Ongoing use

After setup, your AI will commit changes at natural checkpoints (end of conversations, completed builds). You can also:

- **See recent changes:** `git log --oneline -10`
- **Undo last change:** `git revert HEAD`
- **Check what's changed:** `git status`

### What Just Happened

You connected your workspace to version control. Every meaningful change is now tracked and reversible. Think of it as an infinite undo button for your entire workspace.

➡️ **Back to menu** — pick another number, or type **done**.

---

## Wrapping Up

When you type **done**, I'll give you a quick summary of what you explored and suggest next steps based on what seemed most interesting to you.

**Things to try after the walkthrough:**

- **Connect Google Drive** → Enables automatic meeting transcript ingestion
- **Run a real journal session** → Try `@Journal` and pick Morning Pages or Evening Reflection
- **Start a build** → Say "I want to build..." and watch the full planning system activate
- **Explore the docs** → `docs/PHILOSOPHY.md` explains the thinking behind the system

**Getting help:**
- Ask "How does [feature] work?" anytime
- Re-run this walkthrough anytime with `@WALKTHROUGH.prompt.md`
- Re-run the bootloader to repair: `@BOOTLOADER.prompt.md`

---

*N5OS Ode v1.0 — Now you know your way around.*
