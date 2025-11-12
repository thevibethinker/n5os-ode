---
created: 2025-09-19
last_edited: 2025-11-04
version: 2.1
---

# N5 System Upgrades Backlog

## 🎯 Open/Planned

### 🔴 Create Vibe Persona

**ID:**   
**Priority:** H  
**Summary:** Design and implement a Vibe persona for the persona ecosystem. Define role, capabilities, personality, and interaction patterns. Create persona YAML specification and register in system.

**Tags:** persona, vibe, design, high-priority

---

### 🔴 Create Documenter Persona

**ID:**   
**Priority:** H  
**Summary:** Design and implement a Documenter persona for the persona ecosystem. Specialized in technical documentation, knowledge base management, and maintaining system documentation. Create persona YAML specification and register in system.

**Tags:** persona, documenter, documentation, high-priority

---

### 🔴 Create Systems Maintainer Persona

**ID:**   
**Priority:** H  
**Summary:** Design and implement a Systems Maintainer persona for the persona ecosystem. Specialized in system health, monitoring, cleanup, and ongoing maintenance tasks. Create persona YAML specification and register in system.

**Tags:** persona, systems-maintainer, maintenance, high-priority

---

### 🔴 Organizations System for CRM

**ID:**   
**Priority:** H  
**Summary:** Design and implement the organizations/ directory structure in Knowledge/crm/. Populate with company profiles extracted from existing individual profiles. Establish schema, templates, and relationships between organizations and individuals.

**Tasks:**
- [ ] Design organization profile schema (company info, contacts, interactions)
- [ ] Create organization template
- [ ] Extract organization data from existing profiles
- [ ] Establish individual↔organization relationships
- [ ] Update documentation

**Tags:** crm, organizations, high-priority, phase-9

---

### 🟡 Custom System Settings Configuration Area on Zo

**ID:**   
**Priority:** M  
**Summary:** Create a dedicated 'settings' area on Zo where custom system settings can be defined as individual files that are edited on an ongoing basis. This state area would extend beyond standard Zo settings to include user-specific system configurations and preferences.

**Tags:** system, settings, configuration, ux

---

### ⚪ Workflow for Processing and Tracking Persons of Note (CRM)

**ID:**   
**Priority:** MEDIUM  
**Summary:** Implement a CRM-like system for tracking and processing information about key persons, including contact details, interactions, insights, and relationship management.

---

### ⚪ AI Model Critique and Telemetry System

**ID:**   
**Priority:** HIGH  
**Summary:** Create a command that has subsequent AI instances critique and analyze the work of previous AI instances, collecting structured observations and building a central rubric to understand the characteristics, strengths, and patterns of different models. Include telemetry tracking to build insights over time.

---

### ⚪ Temporary File Management

**ID:**   
**Priority:** MEDIUM  
**Summary:** Implement a robust system for managing temporary files, including automatic cleanup, versioning, conflict resolution, and integration with the main file management workflow to prevent data loss and maintain system cleanliness.

---

### ⚪ General File Management

**ID:**   
**Priority:** MEDIUM  
**Summary:** Develop comprehensive file management capabilities including advanced search, bulk operations, metadata tracking, version control integration, and user-friendly interfaces for organizing and maintaining the workspace files.

---

### 🟡 Enhanced Command Authoring User Experience

**ID:**   
**Priority:** M  
**Summary:** Add interactive wizard, searchable command marketplace, and auto-suggestions to reduce duplication and improve discoverability. Make the CLI more intuitive for non-technical users.

**Tags:** ux, discoverability, interface

---

### 🟡 Howie ↔ Zo Post-Meeting Automation Pipeline

**ID:**   
**Priority:** M  
**Summary:** Zo processes meeting transcripts/blocks, extracts action items, notifies Howie of completion. Howie checks for ongoing email thread and sends brief recap with action items to meeting participants. Enables full meeting lifecycle automation.

**Tags:** howie-integration, automation, meeting-processing

---

### 🟡 Cross-Meeting Pattern Recognition & Optimization

**ID:**   
**Priority:** M  
**Summary:** Zo tracks meeting outcomes by stakeholder type, day-of-week, time, and other factors. Learns optimal patterns (e.g., investor meetings on Tue/Thu convert better). Automatically updates Howie scheduling preferences based on learned patterns. Self-optimizing scheduling system.

**Tags:** howie-integration, ml, optimization

---

### 🟡 Meeting Intelligence Feedback Loop

**ID:**   
**Priority:** M  
**Summary:** After meetings, Zo generates insights (key topics, follow-up needs, relationship strength). Emails Howie with context: "Meeting went well, priority relationship, prefer Tue/Thu for future." Howie stores as preference override for that contact. System learns from outcomes.

**Tags:** howie-integration, intelligence, learning

---

### 🟢 Howie Personalized Scheduling Responses

**ID:**   
**Priority:** L  
**Summary:** Give Howie access to stakeholder profiles maintained by Zo. Enables personalized scheduling emails: "Good to hear from you again! I see you and Vrijen last connected 3 months ago about hiring. Looking forward to your follow-up discussion." Warmer, more human interactions.

**Tags:** howie-integration, personalization, ux

---

### 🟡 Progressive Meeting Brief Enhancement

**ID:**   
**Priority:** M  
**Summary:** Brief evolves from basic (when scheduled) → enhanced (5 days before) → specific (2 days) → final (morning-of). Early awareness + just-in-time detail. Basic: bio/company/past. Enhanced: recent news. Specific: talking points aligned to current priorities. Final: overnight updates.

**Tags:** meeting-prep, automation, intelligence

---

### 🟢 Dynamic Meeting Duration Adjustment

**ID:**   
**Priority:** L  
**Summary:** First meeting with investor → 45 min. Zo research reveals early-stage VC, exploratory → suggests 30 min instead. After meeting, V notes "serious, follow-up needed" → next meeting auto-scheduled 60 min. Duration adapts to relationship stage and context.

**Tags:** howie-integration, optimization, scheduling

---

### 🟢 Travel Intelligence & Coordination

**ID:**   
**Priority:** L  
**Summary:** Flight/train scheduled → Zo detects, generates travel checklist (meetings before/after, docs needed, contacts in destination). Howie offers to schedule meetings in destination city. Zo tracks patterns, suggests recurring trips. Travel becomes strategic opportunity, not just logistics.

**Tags:** travel, coordination, intelligence

---

### 🔴 File Cleanup System for Root and N5 Directories

**ID:**   
**Priority:** H  
**Summary:** Create an automated file cleanup system to maintain workspace hygiene. Implement as script/scheduled task for regular cleanup of temporary files, misplaced artifacts, and orphaned resources in both root workspace and N5 system directories.

**Tasks:**
- [ ] Design pattern-based detection for cleanup candidates
- [ ] Implement safe deletion with comprehensive logging
- [ ] Create configurable retention policies
- [ ] Add dry-run mode for preview
- [ ] Integrate with end-of-conversation orchestrator
- [ ] Handle both root workspace and N5 system directories

**Tags:** automation, cleanup, maintenance, system

---

### 🟡 Build a Meeting Block Builder

**ID:**   
**Priority:** M  
**Summary:** Create a meeting block builder tool that enables quick construction and configuration of meeting blocks/sessions

**Tags:** automation, meetings, tools

---

### 🟡 Littlebird Call Link & File Tracking

**ID:**   
**Priority:** M  
**Summary:** When on audio or video calls (Zoom, Google Meet, WhatsApp Desktop, etc.), have littlebird pay attention to links (surveys, websites, Google Drive links, etc.) or files shared by V or shared with V, as well as any promises made regarding sharing links/files. Track these as action items for follow-up.

**Tags:** littlebird, meetings, automation, tracking

---

### 🟡 create a meeting to talking point to knowledge base to content pipeline

**ID:**   
**Priority:** M  
**Tags:** workflow, pipeline, knowledge-base

---

### 🟡 Create Sandbox for Files Mode

**ID:**   
**Priority:** M  
**Summary:** Create a standard protocol and mode where files (especially temporary files) are stored in a sandbox with a particular, consistent structure. This would establish clear patterns for temporary file management and staging.

**Tags:** sandbox, file-management, protocol, temporary-files

---

### 🟢 Reference Files Coherence Check Script

**ID:**   
**Priority:** L  
**Summary:** Create coherence_check.py to validate that registered reference files still exist, frontmatter matches registry, no orphaned entries, and no unregistered reference-like files in workspace.

**Tags:** reference-files, validation, maintenance, coherence

---

## 🔄 In Progress

### Workflow for Ingesting Content + Insights from External Sources

**ID:**   
**Summary:** Develop a structured workflow to import, process, and integrate content and insights from external sources, including validation, tagging, and knowledge base updates.

---

### Telemetry roll-ups

**ID:**   
**Summary:** Implement daily summary emitter script for metrics on adds/edits, dupes prevented, backups created, failures.

---

### Workspace Cleanup and File Organization Command

**ID:**   
**Summary:** Create a command or script that automatically identifies and cleans up files created in wrong locations during development workflows. Should include pattern matching for common misplaced files (conver...

---

### Advanced Command Conflict Resolution and Versioning

**ID:**   
**Summary:** Add semantic versioning, dependency tracking, and automated merging for command conflicts. Prevent breaking changes and enable backward compatibility checks for evolved commands.

---

## ✅ Done/Completed

- **Command to Export a Particular Thread and Package Everything Needed to Restart Exercise in Another Thread** ()
- **Workflow for Processing and Tracking Persons of Note (CRM)** ()
- **Upgrade system configuration** ()
- **Upgrade system config** ()
- **Implement workflow enhancement for better productivity** ()
- **Long-standing Issue: Overriding Phenomenon** ()
- **Long-standing Issue: Git Merge Conflicts** ()
- **Long-standing Issue: Uncommitted Changes Lost** ()
- **Long-standing Issue: Schema Validation Failures** ()
- **Long-standing Issue: Dependency Conflicts** ()

_... and 12 more completed items_
