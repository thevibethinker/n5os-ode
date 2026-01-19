---
created: 2026-01-16
last_edited: 2026-01-16
version: 1
provenance: con_UrtjvDmEzvGPQmJI
type: product-feedback
recipient: Calendly / Tope Awotona
---
# Howie Product Dossier

*Power user feedback for agentic scheduling*

---

## Context

I've used Howie daily for 6+ months. I've built an entire orchestration system around it — tag-based instructions, verbal signal detection, automated signature generation. This isn't casual feedback. It's from someone who pushed the product to its limits.

Public sentiment validates my experience. On X, users praise Howie's reliability but note "burnout from earlier generations of AI scheduling tools" — people are reluctant to try again because past tools failed on nuance. Howie works, which is why the gaps are worth naming.

---

## What Works

**Email-based mental model.**  
"CC my assistant" is already how people delegate. Zero learning curve. The interaction pattern maps perfectly to existing behavior.

**Preference adherence.**  
Once I tell Howie my constraints, it remembers. The core job-to-be-done — calendar coordination — works.

**Low-friction onboarding.**  
I was scheduling within minutes. No 40-setting configuration hell.

**Human-in-the-loop where it matters.**  
The premium tier's human review layer catches edge cases. This is smart architecture — AI for speed, humans for judgment calls.

---

## What's Broken

**No passive mode.**  
Howie acted when I wanted it to observe. I CC'd it to track a thread. It jumped in and started scheduling. 

I needed: "Watch this. Don't act unless I explicitly tell you to."

**No theory of mind for the counterparty.**  
Howie kept following up despite being ignored. Three follow-ups, similar language, diminishing returns. 

It optimizes for "get the meeting scheduled" without modeling how the other person experiences the outreach. Sender blindness is real — what feels like persistence to the sender feels like spam to the receiver.

The social read should be: "Two follow-ups, no response. Either they're not interested or something's wrong. Flag for human judgment."

**Limited memory reservoir.**  
Howie's context window is ambiguous. I can't easily fill it with the information I want it to know. I can't see what it's retained. The mental model is: "I told it things... I think it knows them... maybe?"

Compare this to a real EA: "Here's my briefing doc. Here's my preference file. Here's my relationship context. Now go."

**Escalation without graduation.**  
When Howie encounters something it can't handle, it asks me. Good. But it doesn't *learn* from my answer. Next time, same question. 

The system should graduate from "ask every time" → "suggest and confirm" → "act autonomously" based on demonstrated alignment.

---

## The Deeper Opportunity

**Scheduling is a social protocol, not a logistics problem.**

Who sends the link encodes status. How quickly you respond signals priority. How flexible you appear reveals how much you want the meeting. These aren't bugs — they're features of human coordination.

Current scheduling tools treat this as friction to eliminate. Wrong frame. It's *signal* to preserve and *encode*.

**Why I built a tag system on top of Howie:**

The core problem: scheduling requires context that doesn't exist yet. When someone emails me to meet, I'm often at first contact — I have their public info but nothing about how *I* want to engage.

I can't rely on the scheduler to infer my intent from thin air. And I don't want to manually instruct it every time. So I needed a way to encode relationship dynamics in shorthand:

- *Who is this person to me?* (investor, candidate, networking, partner)
- *How flexible should I appear?* (maximally accommodating vs. protect my time)
- *Who matters more here?* (prioritize their schedule vs. mine)
- *How urgent is this?* (this week vs. whenever)

The failure mode I was solving: a scheduling agent treats all meetings as equal. They're not. An investor meeting and a cold networking ask require completely different postures. Same calendar, radically different protocol.

The product gap: there's no native way to tell the agent *what kind of dance this is* — only to say "find a time."

**The private instruction problem.**

How do I tell my agent my preferences without revealing them to the counterparty? If I'm maximally accommodating to investors but protective with cold outreach, I don't want the cold outreach person to *know* that.

This is solvable UX. Current state: separate instruction channel, race conditions, cognitive overhead. Future state: embedded metadata, private context, seamless.

**Agent-to-agent is coming.**

When both parties have scheduling agents, the interaction becomes: my preferences vs. their preferences, negotiated by two AIs. 

This changes everything. Today, Howie negotiates with a human. Tomorrow, Howie negotiates with their Howie. The protocol needs to anticipate this — shared standards, commitment mechanisms, graceful fallbacks.

---

## If I Were Building This

**1. Mode toggle: Active / Passive / Observe.**  
Let users choose: "Act on my behalf" vs. "Suggest and wait" vs. "Just watch and learn."

**2. Counterparty modeling.**  
After 2 follow-ups with no response, stop and flag. After a successful scheduling, note their response patterns. Build a lightweight model of each contact.

**3. Visible, editable memory.**  
Show me what Howie knows. Let me correct it. Make the context reservoir transparent and user-controlled.

**4. Graduated autonomy.**  
Track alignment between Howie's suggestions and my approvals. When alignment is high, increase autonomy. When I override, learn and adjust.

**5. Private instruction layer.**  
Let me encode relationship context that travels with the scheduling thread but isn't visible to the counterparty. Tags, priority levels, accommodation preferences — metadata that shapes behavior without leaking.

---

## Summary

Howie gets the fundamentals right: email-native, preference-aware, human-augmented. The gaps are in social intelligence (counterparty modeling), transparency (memory visibility), and flexibility (mode toggling).

The product that wins agentic scheduling will understand that the calendar slot is just the output. The real product is encoding and executing human relationship dynamics at scale.

---

*V — Power User*  
*January 2026*
