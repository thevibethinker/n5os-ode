---
created: 2026-01-31
last_edited: 2026-01-31
version: 1.0
provenance: con_jkb5kwud6E7W7OGY
---

# Careerspan Coaching Guide: Manthan Sit
**For: Guickly — Founding Engineer Role**

---

## Your Narrative Arc

You're an **engineer who works at the intersection of data pipelines and ML systems**. You've touched genomics data processing (Illumina), real-time surveillance pipelines (Smarsh), and you built internal tooling that cut dataset generation from hours to 30 minutes. You're not just shipping features—you're building the infrastructure that lets others ship faster.

---

## What to Emphasize with Your Careerspan Coach

### 1. **The Re-Architecture at Smarsh/Caizin**
This is your lead story. You're switching a system from batch to real-time processing. Dig into:
- Why batch was failing (latency? cost? scale?)
- The architecture you designed: Kafka, microservices, async queues
- The ML integration: You send docs to "Cognition ML models"—what does that pipeline look like?
- Reconciliation: How do you ensure documents aren't lost or duplicated?

*Why it matters*: Guickly is building "end-to-end model development workflow" automation. Your experience with data pipelines feeding ML models is exactly the domain.

### 2. **Cognition Logic Tooling (The 90% Time Reduction)**
You built internal tooling that cut dataset generation from hours to <30 minutes. This is your "automation" story:
- What was the pain before? Manual setup, waiting for VMs, config hell?
- What did you build? (Java+Spring, dockerized K8s, multi-language support)
- Who uses it now? What's the impact on the team's velocity?

*Why it matters*: Guickly is building tools that automate painful ML workflows. You've already done this—just in a different domain. Draw the parallel explicitly.

### 3. **The Genomics Data Processing Work (Illumina)**
Don't bury this. Processing high-volume genetic data is data engineering at scale:
- What volumes were you dealing with?
- What made the code "optimized"? What bottlenecks did you hit?
- How did you work with Snowflake for genomic data?

*Why it matters*: Shows you can handle large-scale data pipelines. Genomics → ML training data is an easy conceptual bridge.

### 4. **Computer Vision Internship (Plant Species Detection)**
Your only explicit ML experience. Bring it forward:
- What techniques did you use? (edge detection, k-means, color segmentation)
- What was hard? (Lighting? Edge cases? Labeling?)
- What would you do differently now?

*Why it matters*: The founder's background is Computer Vision at Google Maps. Even a small CV project creates common ground.

---

## What to De-Emphasize or Reframe

- **"Worked in web development"** (Strand) — The full-stack Angular work is less relevant. Emphasize the backend data processing, not the admin dashboards.
- **Multiple shorter stints** — 1.5 years at Flexcar, 1.5 years at Strand. Could signal job-hopping. Frame as: seeking progressively more impactful infrastructure work.
- **Customer data/PII work (Flexcar)** — Interesting but not the lead. Use it only if asked about security/compliance.

---

## The Question You'll Face

*"Your experience spans genomics, car rentals, and surveillance. What's the thread?"*

Your answer: Data pipelines and ML infrastructure. Every role involved processing high-volume data, building reliable pipelines, and often feeding ML systems. You're not a feature engineer—you're an infrastructure engineer who makes ML teams faster.

---

## Form Response Notes

- **Location**: You're in Bangalore. Emphasize enthusiasm for in-office—this is your advantage.
- **Coding breakdown**: Your resume is very hands-on. You should be comfortable saying 80% coding.
- **0→1 experience**: You don't have classic startup experience, but your tooling work (Cognition Logic) was 0→1 within a larger org. Use that.
- **ML training/fine-tuning**: You haven't fine-tuned models, but you've built pipelines that *feed* ML models. Be honest about the gap, but show you understand the workflow.
