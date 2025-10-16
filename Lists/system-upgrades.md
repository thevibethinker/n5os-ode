# System Upgrades

## Open Items

### [H] Organizations System for CRM

Design and implement the organizations/ directory structure in Knowledge/crm/. Populate with company profiles extracted from existing individual profiles. Establish schema, templates, and relationships between organizations and individuals.

**Tags**: crm, organizations, high-priority, phase-9

---

### [M] Custom System Settings Configuration Area on Zo

Create a dedicated "settings" area on Zo where custom system settings can be defined as individual files that are edited on an ongoing basis. This state area would extend beyond standard Zo settings to include user-specific system configurations and preferences.

**Tags**: system, settings, configuration, ux

---

### [M] Enhanced Command Authoring User Experience

Add interactive wizard, searchable command marketplace, and auto-suggestions to reduce duplication and improve discoverability. Make the CLI more intuitive for non-technical users.

**Tags**: ux, discoverability, interface

---

### [H] File Cleanup System for Root and N5 Directories

Create an automated file cleanup system to maintain workspace hygiene. Implement as script/scheduled task for regular cleanup of temporary files, misplaced artifacts, and orphaned resources in both root workspace and N5 system directories.

**Tags**: automation, cleanup, maintenance, system

---

### [M] Build a Meeting Block Builder

Create a meeting block builder tool that enables quick construction and configuration of meeting blocks/sessions

**Tags**: automation, meetings, tools

---

## Planned Items

### [MEDIUM] Workflow for Processing and Tracking Persons of Note (CRM)

Implement a CRM-like system for tracking and processing information about key persons, including contact details, interactions, insights, and relationship management.

---

### [HIGH] AI Model Critique and Telemetry System

Create a command that has subsequent AI instances critique and analyze the work of previous AI instances, collecting structured observations and building a central rubric to understand the characteristics, strengths, and patterns of different models. Include telemetry tracking to build insights over time.

---

### [MEDIUM] Temporary File Management

Implement a robust system for managing temporary files, including automatic cleanup, versioning, conflict resolution, and integration with the main file management workflow to prevent data loss and maintain system cleanliness.

---

### [MEDIUM] General File Management

Develop comprehensive file management capabilities including advanced search, bulk operations, metadata tracking, version control integration, and user-friendly interfaces for organizing and maintaining the workspace files.

---

### [M] Howie ↔ Zo Post-Meeting Automation Pipeline

Zo processes meeting transcripts/blocks, extracts action items, notifies Howie of completion. Howie checks for ongoing email thread and sends brief recap with action items to meeting participants. Enables full meeting lifecycle automation.

---

### [M] Cross-Meeting Pattern Recognition & Optimization

Zo tracks meeting outcomes by stakeholder type, day-of-week, time, and other factors. Learns optimal patterns (e.g., investor meetings on Tue/Thu convert better). Automatically updates Howie scheduling preferences based on learned patterns. Self-optimizing scheduling system.

---

### [M] Meeting Intelligence Feedback Loop

After meetings, Zo generates insights (key topics, follow-up needs, relationship strength). Emails Howie with context: "Meeting went well, priority relationship, prefer Tue/Thu for future." Howie stores as preference override for that contact. System learns from outcomes.

---

### [L] Howie Personalized Scheduling Responses

Give Howie access to stakeholder profiles maintained by Zo. Enables personalized scheduling emails: "Good to hear from you again! I see you and Vrijen last connected 3 months ago about hiring. Looking forward to your follow-up discussion." Warmer, more human interactions.

---

### [M] Progressive Meeting Brief Enhancement

Brief evolves from basic (when scheduled) → enhanced (5 days before) → specific (2 days) → final (morning-of). Early awareness + just-in-time detail. Basic: bio/company/past. Enhanced: recent news. Specific: talking points aligned to current priorities. Final: overnight updates.

---

### [L] Dynamic Meeting Duration Adjustment

First meeting with investor → 45 min. Zo research reveals early-stage VC, exploratory → suggests 30 min instead. After meeting, V notes "serious, follow-up needed" → next meeting auto-scheduled 60 min. Duration adapts to relationship stage and context.

---

### [L] Travel Intelligence & Coordination

Flight/train scheduled → Zo detects, generates travel checklist (meetings before/after, docs needed, contacts in destination). Howie offers to schedule meetings in destination city. Zo tracks patterns, suggests recurring trips. Travel becomes strategic opportunity, not just logistics.

---

