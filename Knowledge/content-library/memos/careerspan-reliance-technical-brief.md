---
created: 2026-02-02
last_edited: 2026-02-02
version: 1.0
provenance: con_HCGIwL1T8X39w8hp
author: Ilse Funkhouser
title: Careerspan x Reliance — Technical Brief
type: memo
---

# Careerspan x Reliance — Technical Brief

Prepared by Careerspan CTO + Head of AI, Ilse Funkhouser.

BA Northwestern, MS Data Science.

## Skills Taxonomy & Reliance Alignment

Careerspan evaluates skills in context, not as abstract checkboxes — and can map directly to Reliance's existing taxonomy.

Most skills taxonomies treat a skill as a fixed, transferable unit. "Project Management" is "Project Management," whether you're managing a product launch at a telecom company or maintenance schedules at a refinery. Careerspan doesn't work that way.

Our system evaluates each user story against each job responsibility individually — including weighting for recency, relevance, strength of evidence, and whether the demonstrated skill is a direct or transferable match. We preserve the nuance of how someone has applied their skills and in what context.

### Where Reliance's taxonomy fits in:

**Taxonomy as a shared language layer.** Reliance's taxonomy gives us a consistent vocabulary to map our contextual assessments back to. When Careerspan determines that a user demonstrates strong "stakeholder communication in a compliance-heavy environment," that can be tagged to whichever node in Reliance's taxonomy governs stakeholder management or communication competencies.

**Careerspan as a taxonomy stress-test.** Because we assess skills in context rather than in the abstract, our data can surface where a single taxonomy node actually represents multiple distinct competencies. Over time, this gives HR leadership a data-driven view of which skills are truly portable across business units and which ones fracture into meaningfully different capabilities depending on context.

**Cost efficiency through reusable assessments.** A structured taxonomy allows us to cache and reuse story-to-skill assessments across similar roles. If Reliance defines "Financial Analysis" consistently across its retail and energy divisions, we can reuse a user's assessed competency rather than regenerating it from scratch — reducing compute cost and processing time at scale while providing more consistent assessments.

## Learning Platform Integration

We measure upskilling by demonstrable change in how someone works, not certificates earned.

Careerspan's conversations already close the loop on learning. At the end of each session, we ask users how they've applied things they've recently learned — not just whether they completed a course, but whether and how they used that knowledge in their actual work.

Integration with platforms like Coursera, LinkedIn Learning, or Reliance's internal L&D systems is a natural extension. The value isn't in importing course completions as proof of skill — it's in using them as prompts for reflection. When a user finishes a course on data visualization, Careerspan can follow up in a subsequent conversation: "You completed that course last month. Have you had a chance to use any of those techniques? Tell me about it." That reflection becomes a story, and that story becomes assessable data.

For an organization investing heavily in L&D at Reliance's scale, this distinction is significant — learning investment measured by capability change, not completion rates.

## CVs and Local Context

Careerspan is CV-agnostic and has no region or industry bias baked in.

We don't rely on CVs or resumes as input. Our assessment engine works through AI-led conversations — structured reflections on actual work experiences using STAR-based analysis (Situation, Task, Action, Result), drawn from the user's own language. The result is a narrative dataset that captures not just what someone has done, but how they think about what they've done.

This means there is no US bias, no India bias, no region-specific formatting dependency. If a person can talk about their work, Careerspan can assess them.

The practical benefit for Reliance: Careerspan can be deployed across the entire ecosystem of industries without requiring separate training, configuration, or customization per business unit. Our analysis of a job — and the ways we assess a candidate against it — is reviewable in plain English and adjustable by the hiring manager before any candidate evaluation begins.
