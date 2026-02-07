---
created: 2026-02-02
last_edited: 2026-02-02
version: 1
provenance: con_CoaGOfJATcu1Y90D
---
# Beyond Prompts: The Mental Model for AI Productivity

**Session:** Fundamentals of AI Productivity\
**Date:** January 29, 2026\
**Presenters:** Vrijen Attawar (Careerspan), Logan Currie (Careerspan), Ben Shacklette (Zo Computer)

---

## The Head Fake

We called this session "Fundamentals of AI Productivity." That was intentional misdirection.

80% of you told us in the survey that you either "can't level up" or feel "overwhelmed by options." You're using ChatGPT. Half of you are already using Claude. You're not beginners—you're stuck.

**The diagnosis:** You don't have a technology problem or a tactics problem. You have a mental model problem.

You're collecting individual tricks without understanding how they fit together. It's like having puzzle pieces without the box cover—you can't see what you're building toward.

---

## The Core Insight: Context Engineering

The shift from "prompting" to "context engineering" is the mental model upgrade.

**Old model:** You prompt the AI → it gives you output\
**New model:** You cultivate context → the AI collapses that context into output

The difference is where the work happens. In the old model, you're crafting the perfect ask. In the new model, you're loading the AI with everything it needs *before* you ask for anything.

Think of it like this: a great assistant isn't useful because you asked nicely. They're useful because they already know your preferences, your calendar, your priorities, and your communication style. The ask is almost an afterthought.

---

## The Three Levels

### Level 1: Conversation Engineering

**What it is:** Tactics you can use within a single chat session to get dramatically better results.

**Key moves:**

- **Don't ask for output too early.** Build context first. Tell the AI where to look, what you care about, what good looks like. Request the deliverable last.
- **Offensive vs. Defensive prompting.** Offensive = expand options ("What else could this be? Surprise me."). Defensive = shore up ("Attack this. What am I missing?").
- **Threshold rubric.** Ask the AI: "If you were evaluating this, what rubric would you use?" Then: "Score my current version against that rubric and iterate until we hit the top tier."

**From the session:** Logan's prompt "Come up with 2-3 things that would really delight me" is pure offensive prompting. She's telling Claude to go beyond what she asked for.

**Try this:** Pick one task you'd normally one-shot ("Write me an email to X"). Instead, spend 3 messages building context before asking for the output. Notice the difference.

---

### Level 2: Environment Engineering

**What it is:** Persistent context that shapes every interaction—not just one conversation.

**Key moves:**

- **Curate your memory.** Both ChatGPT and Claude have memory features. Almost no one curates them. You can say: "Add this to your explicit memory, verbatim." It will.
- **Build personas.** A "vibe teacher" persona with instructions like "explain concepts in terms I understand" changes every conversation.
- **Set cognitive guardrails.** "Don't flatter me. Be critical. Push back when you disagree." Most AI defaults to sycophancy. Override it.

**Warning:** More context isn't always better. You can dilute signal with noise. Be selective.

**From the session:** V has personas built into Zo that automatically shape how the AI explains technical concepts to him—a non-technical founder learning by doing.

**Try this:** Open ChatGPT or Claude's memory settings. Delete 3 things that are outdated. Add 1 thing that's actually useful. Most people have never touched this.

---

### Level 3: Pipeline Engineering

**What it is:** Connecting your AI to external data sources—bringing the world into your system.

**Key moves:**

- **Export your data.** GDPR means every platform has to let you export. LinkedIn gives you 48 CSV files. Spotify gives you listening history. This is your raw material.
- **Think in blocks.** What are the primitive components? For V's flight search: preferences file + flight data API + rules script = booking links with one prompt.
- **Build pipelines, not prompts.** A prompt is a one-shot. A pipeline captures → organizes → analyzes → stores. It compounds.

**From the session:**

- Logan exported LinkedIn data, ran it through Claude Code, found 23 high-value DMs she'd accidentally ghosted, discovered 1800% correlation between posting and inbound connections.
- Ben analyzed Spotify listening data and instantly visualized work patterns (locked-in coding → launch → busy non-coding).
- V built a meeting notes pipeline: inbox → organization → intelligence layer → storage. Every meeting now gets custom analysis, decision capture, and "thought-provoking ideas" tracking.

**Try this:** Export one dataset. LinkedIn (Settings → Get a copy of your data) is the easiest and most valuable. Let it sit in your downloads—we'll tell you what to do with it.

---

## The Destination: MetaOS

When you stack all three levels, something emerges. It's not just "AI productivity"—it's a personal operating system.

**V's version:**

- Flight searches with one instruction (preferences + data + rules)
- Meeting notes that actually get used (pipeline, not dump)
- Ideas tracked in a database, not lost in notes
- Technical concepts explained in terms he understands (persona)

**Ben's version:**

- Texting Claude Code from the airport to fix bugs
- Foreground tasks (deep work, planning) + background swarm (one-shot fixes)
- "The same effort as logging an idea can now be taking action"

**Logan's version:**

- LinkedIn as a data source, not just a feed
- Skill gap analysis cross-referenced with network connections
- "What should LinkedIn be showing us that they're not?"

The specifics will look different for everyone. The pattern is the same: **intent collapses to outcome faster**, because the system already knows what you need.

---

## Complexity Is an Illusion

You'll see scary technical terms: YAML, JSON, API, scripts. You'll think "this isn't for me."

It is.

V has looked at zero lines of code while building his system. Logan is non-technical. The actual work is *thinking sophistication*, not *technical sophistication*.

If you're the kind of person who attended this session, you have the thinking sophistication. The technical parts are just blocks the AI builds and connects.

---

## Resources

### 📹 Session Recording

**Watch:** https://us06web.zoom.us/rec/share/joksaNfsJlP1H1paPCSmenoMogQR-0jq1pXM08k128LtgCf13XdxorJFyABNWO7I.1Pe2pdIg5MVjEbCv  
**Passcode:** `bnp!9H$0`

---

### Level 1: Better Prompting & First AI Computer

**Zo Computer** — https://zo.computer?promo=ZOEDU  
$20 in AI credits + 20% off if you subscribe. Zo is like Moltbot (which you've probably been hearing about) — but with frictionless setup and a lot built-in, including the ability to text with your autonomous assistant.

---

### Level 2: Context Engineering & Data Analysis

**Logan's LinkedIn Data Export Visualization**  
https://loganhc-09.github.io/LinkedIn-Data-Export-Visualization/  
The tool Logan demoed for analyzing your own LinkedIn data.

**Follow Logan:**
- Substack: https://loganinthefuture.substack.com/
- LinkedIn: https://www.linkedin.com/in/logan-currie/
- TikTok: https://www.tiktok.com/@loganinthefuture

---

### Level 3: System Building & Advanced Patterns

**V's N5OS Repository (Deep Wiki)**  
https://deepwiki.com/vrijenattawar/n5os-ode  
For advanced users who want some of the quality-of-life upgrades shown in the session — includes a build orchestrator to improve the Zo development experience, semantic memory systems, and more.

---

### Bonus: Live Survey Dashboard

https://gamma.app/docs/pkl5iqh8270s4s3  
This dashboard is auto-generated daily by Zo. It's an example of the kind of pipeline we discussed — V connected Zo to Fillout.com and Gamma, made the survey, and Zo automatically regenerates this visualization every day.

---

## What's Next

**If you try one thing:** Export your LinkedIn data this week. Even if you don't analyze it yet, having it locally changes your relationship with the platform.

**If you want to go deeper:** The attached LinkedIn analysis guide walks through exactly what Logan did. Claude Code works on the $17/mo Pro plan.

**If you have questions:** Reply to this email. We read everything.

---

## Key Quotes from the Session

> "You don't prompt the AI. You work with the AI to cultivate the context that it then uses to collapse down to the output you want." — V

> "Unhobble the model. It's probably capable of more than you think it is." — Logan (quoting Anthropic)

> "The same amount of effort as logging an idea can now be taking action on it." — Ben

> "Complexity is an illusion. Think in blocks." — V

---

*Questions? Hit reply. We'll send the recording separately once it's processed.*