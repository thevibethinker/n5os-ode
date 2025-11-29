---
created: 2025-11-29
last_edited: 2025-11-29
version: 1.0
---

# B01 – Detailed Recap

## Purpose and setup
- Internal working session where V walks a Plaud/Nextplay contact through Zo and the meeting-intelligence system he has built on top of it.
- The other participant is exploring how to manage a heavy volume of intros, follow‑ups, and content creation; V uses this as a concrete use case while demoing.

## Introducing Zo and the AI computer model
- V explains Zo as a "literal computer in the cloud" rather than a single chat interface:
  - There is a real file system, scheduled tasks (agents), and the ability to plug in other services (e.g., n8n, external APIs).
  - Out of the box, Zo is empty; the value comes from setting up rules, personas, and workflows that operate on the file system.
- He emphasizes that Zo is explicitly designed to be usable by non‑engineers, even though it becomes extremely powerful in technical hands.

## Dictation, transcription, and the Evry tool suite
- They discuss the friction of having to "compose" emails and content manually.
- The other participant mentions relying heavily on voice-to-text and starting to use dictation with Perplexity.
- V recommends using a dedicated desktop dictation app and describes Evry’s ecosystem:
  - **Monologue** – dictation app; V was once one of its top users.
  - **Spiral** – AI writing partner for marketing; can ingest LinkedIn posts and help with content generation.
  - **Quora** – email client positioned as a potential Superhuman alternative.
- V notes that Evry’s model is to spin up small, focused apps and empower a solo lead to run each product line.

## Zo-based knowledge and content workflows
- V demonstrates how he uses Zo to:
  - Request research on trends (e.g., "current trends in early-career hiring") and combine that with his own knowledge base.
  - Generate LinkedIn posts "in his voice" using specialized personas (e.g., Vibe Builder, Vibe Writer).
- He shows how personas can be switched agentically during a workflow:
  - Architect → plans the system using knowledge of the file structure.
  - Builder → implements workflows and scripts.
  - Debugger → tests and validates behavior.
  - Teacher → explains how the system works to a non‑technical user.
- The key idea: V has invested in setting up an ingestion and voice system once, so future content generation is fast and context‑rich.

## Databases and go‑to‑market intelligence
- V demonstrates how Zo can spin up and interact with a database without him hand‑coding it:
  - He asked Zo to create a go‑to‑market intelligence database.
  - The system now stores structured fields about meetings, including B‑blocks like B31 (stakeholder research) and other intelligence outputs.
- He highlights how Zo searches and manipulates files (e.g., using tools like grep under the hood) while he stays at the conceptual layer.

## Meeting-intelligence pipeline and idempotency
- V walks through his meeting pipeline:
  - All calls (Plaud, Granola, Fireflies, etc.) ultimately deposit transcripts into a central record system.
  - Zo ingests transcripts, queues them for processing, and generates intelligence blocks (B01 recap, commitments, questions, warm intros, etc.).
  - Once a meeting has been processed, it is marked in a way that prevents double-processing (he introduces the concept of **idempotency**—like popping bubble wrap; once popped, it stays popped).
- He shows an example B‑block output that includes:
  - Detailed recap.
  - Commitments and questions (including implicit, unresolved questions).
  - Warm intros and networking opportunities.
  - Follow‑up email drafts that weave together meeting content and CRM profiles.

## Discussion of GoodWork and other platforms
- The other participant brings up **GoodWork**, a new networking product positioned as an alternative to LinkedIn.
  - She notes that many high‑profile connectors are using it and that her feed is full of GoodWork posts.
  - She is still unclear on the core product value and how to integrate it meaningfully into her workflow.
- V responds by generalizing the challenge for AI products:
  - Many tools promise to "process all your data" but leave the hardest part—the data ingestion and organization—on the user.
  - He argues for a future where users carry their data in a sealed, portable container that can be selectively plugged into different services.

## Communities, events, and distribution
- The conversation shifts to communities and events:
  - They mention **Nextplay** and **FOHE (Future of Higher Education)** as high‑quality communities where V is active.
  - The other participant suggests that V could run a virtual workshop for Nextplay; V is enthusiastic.
  - They note that Zo would likely be willing to sponsor a high‑value in‑person event with Nextplay or similar communities.
- The theme: use communities as distribution channels for teaching better AI workflows (dictation, personal AI systems) rather than just selling a tool.

## Tuning voice and system design
- The participant asks how to "tune" the system to her own voice and style.
- V explains that:
  - The system can be tuned by feeding it examples and iteratively correcting outputs.
  - His goal is to package a **base Zo system** that others can install with minimal setup (e.g., a small amount of code), preconfigured with meeting ingestion and content workflows.
- He notes that founders, AI‑curious VCs, and operators who are dissatisfied with current AI tools are the primary early adopters.

## Closing
- They identify core use cases for the participant:
  - Handling large volumes of warm intros and follow‑up tasks.
  - Turning meetings and ambient conversations into structured intelligence and content.
- The conversation ends with concrete next steps around:
  - Potential Zo-sponsored or Zo-themed workshops for communities like Nextplay.
  - The participant introducing V to her FOHE contact (Finn) and others who would resonate with these workflows.

