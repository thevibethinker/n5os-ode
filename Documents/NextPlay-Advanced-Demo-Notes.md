---
created: 2026-01-29
last_edited: 2026-01-29
version: 1.1
provenance: con_NyBFUAIsg8UF3aVr
---
# NextPlay Demo: Advanced Use Cases (5-10 min)

## The Core Message

**"I built these with no training, no bootcamp. What I had was:**

1. **Great mentors** who helped me see AI correctly — not as magic, but as a tool with clear, learnable patterns
2. **The willingness to try** and not fear failure
3. **Trust in my own intuition** — if I can intuit that a travel booking system needs somewhere to store my preferences, I can build it"

### The Reframe

These three systems I'm about to show you *seem* complicated. But I want you to see them differently:

- Not as "impressive technical achievements"
- But as **evidence that non-technical people can reconstruct technical understanding from the ground up through interaction**

The pattern is simple:

1. **I have a need** (I want to search flights my way / I want meeting intelligence)
2. **I ask AI to decompose it** ("What are the moving parts?")
3. **I build each part, one conversation at a time**
4. **I connect the parts** (or ask AI to connect them)

That's it. That's the secret.

---

## Use Case 1: Flight Search (\~2 min)

### What It Does

"I say 'flights to LA next weekend' and get results filtered by MY preferences — avoid Spirit, prefer JetBlue, use LaGuardia first."

### How I Built It (The Real Story)

**The Need:** "I was tired of filtering the same airlines out of Google Flights every time."

**The Intuition:** "Maybe there's an API that'll serve up that data to me. If I can store that along with my preferences locally, I can ping it and get the data I want"

**The Decomposition (with AI's help):**

| Component | Plain English | Technical Name |
| --- | --- | --- |
| "A place to store my rules" | My preferences in a readable format | YAML config file |
| "A pipe to flight data" | A way to get real-time prices | SerpAPI connection |
| "A recipe that applies my rules" | Logic that filters and sorts | Python script |
| "A way to talk to it naturally" | So I don't have to remember commands | Prompt interface |

**The Build:** Each piece was a separate conversation. "Build me a config file for travel preferences." "Now write a script that reads that file and calls SerpAPI." "Now make it so I can just describe what I want."

**The Insight for the Audience:**

> "I didn't learn Python. I learned that Python scripts are just recipes. I didn't learn API architecture. I learned that APIs are just pipes that let programs talk to each other. **I reconstructed technical understanding through intuition and interaction.**"

---

## Use Case 2: Meeting Intelligence System (\~4 min)

### What It Does

"Every meeting I have becomes searchable organizational memory. Transcripts get processed into structured intelligence: who was there, what was decided, what I committed to, strategic insights about the person."

### How I Built It (The Real Story)

**The Need:** "I was drowning in meetings. Notes everywhere. No way to remember what I promised to whom three weeks ago."

**The Intuition:** "I need a system. A funnel. Transcripts come in, intelligence comes out, everything gets filed properly."

**The Decomposition (with AI's help):**

```markdown
"Okay, what are the stages?"

1. CAPTURE — Transcripts need to land somewhere
   → "I need a landing zone" (Google Drive folder + webhook)

2. ORGANIZE — Raw files need structure
   → "I need to create folders, name them, track their state"
   (Staging script + manifest.json)

3. UNDERSTAND — Extract the intelligence
   → "I need to read transcripts and pull out specific things"
   (LLM processing into structured blocks)

4. ARCHIVE — File it for later
   → "I need weekly folders, searchable forever"
   (Archival script)
```

**The Build Process:**

- Conversation 1: "Help me design where transcripts should land"
- Conversation 2: "Build the staging script that creates folders"
- Conversation 3: "What intelligence should I extract from meetings?" → Led to the "block" concept
- Conversation 4: "Build the block generator"
- Conversation 5: "How do I archive by week?"
- Conversation 6: "Tie it all together into one CLI"

**Why Separate Conversations?**

> "Context windows are finite. If I dump everything into one conversation, the AI loses track. By splitting across conversations, each piece gets full attention. This is a learnable skill — knowing when to start fresh."

**The Insight for the Audience:**

> "This system has 4 Python scripts, a JSON state machine, webhooks, LLM calls. **I didn't need to understand any of that upfront.** I just kept asking: 'What's the next piece?' and 'Now build it.'"

---

## Use Case 3: This Survey Dashboard (\~2 min)

### What It Does

"You filled out a survey 2 days ago. This dashboard — the one I showed you at the start — was generated automatically from your responses."

### The Meta Moment

**Show the live dashboard:** https://gamma.app/docs/1ejtlhxqzp38egt

**The Need:** "I wanted to show survey results in real-time during this presentation. But I didn't want to manually make charts."

**The Decomposition:**

1. Survey responses need to flow somewhere → Fillout webhook
2. Responses need analysis → Script that computes stats
3. Analysis needs to become visual → Gamma API generates dashboards
4. Dashboard needs to auto-update → Scheduled agent runs every 12 hours

**The Insight for the Audience:**

> "You're experiencing one of my systems *right now*. The dashboard showing YOUR data was built the same way — need, decompose, build piece by piece."

---

## The Closing Frame

### What You Just Saw

Three systems. **None of them complex.** All of them just building blocks — assembled by someone with zero formal technical training, once I learned to appreciate what the building blocks were and how they fit together.

That's the real insight: **complexity is an illusion created by unfamiliarity with the blocks.**

- A config file is just a place to store preferences
- A script is just a recipe
- An API is just a pipe between systems
- A webhook is just a trigger
- A state machine is just a way to track "where am I in the process?"

Once you see the blocks, you stop seeing complexity. You just see assembly.

### What Made It Possible

1. **Seeing AI correctly** — Not as magic. As a cognitive amplifier. It doesn't replace your thinking; it extends it.

2. **Trusting your intuition** — "I need somewhere to store preferences" is not a technical insight. It's common sense applied to a technical domain. **You already have this intuition.**

3. **Bravery** — Willingness to try, willingness to fail, willingness to say "I don't know what an API is, explain it to me like I'm 5."

4. **The decomposition pattern** — Need → "What are the blocks?" → Build each block → Connect them

### The Concluding Point

> "With all due respect to technical people — there is nothing they do that is too complicated for us. It is merely a function of practice. The building blocks are finite and learnable. And now we have an infinite practice partner who never judges, never tires, and always explains."

**The only thing standing between you and systems like these is learning to see the blocks — and the decision to start assembling.**

---

## Practical Tips to Share

If time permits:

1. **Start small** — Your first system should be 1-2 pieces, not 6
2. **Name your files clearly** — Future you will thank present you
3. **Split complex work across conversations** — Fresh context = better results
4. **Write down what you learned** — "Today I learned that APIs are just pipes"
5. **Expect to fail** — Your first version will suck. Version 3 will be great.

---

## Files to Have Ready

- [ ]  Flight search demo: `python3 Integrations/google_flights/google_flights.py search --to LAX --date 2026-02-15`

- [ ]  Meeting system status: `python3 Skills/meeting-ingestion/scripts/meeting_cli.py status`

- [ ]  Survey dashboard URL: https://gamma.app/docs/1ejtlhxqzp38egt

- [ ]  Example meeting folder structure (screenshot or live browse)