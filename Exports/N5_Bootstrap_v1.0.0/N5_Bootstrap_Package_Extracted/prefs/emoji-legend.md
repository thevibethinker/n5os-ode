# N5 Emoji Legend

**Version:** 1.0.0  
**Last Updated:** 2025-10-16T06:28:00Z  
**Auto-generated from:** `file 'N5/config/emoji-legend.json'`

> Centralized emoji legend for N5 OS - Single Source of Truth for emoji meanings across threads, lists, commands, and UI

---

## Table of Contents

- [Complete Emoji List](#complete-emoji-list)
- [Emojis by Category](#emojis-by-category)
- [Usage Contexts](#usage-contexts)
- [Detection Priority](#detection-priority)
- [Quick Reference](#quick-reference)

---

## Complete Emoji List

| Emoji | Name | Category | Meaning | Contexts |
|-------|------|----------|---------|----------|
| ✅ | completed | status | Completed successfully | threads, tasks, todos, lists |
| ❌ | failed | status | Failed or error | threads, tasks, system |
| 🚧 | in_progress | status | Work in progress / under construction | threads, tasks, projects |
| 🔗 | linked | relationship | Linked or sequential threads | threads |
| 📰 | research | content_type | Research, articles, knowledge gathering | threads, lists, knowledge |
| 🎯 | strategy | content_type | Strategy, planning, GTM | threads, tasks, planning |
| 📝 | documentation | content_type | Documentation work | threads, tasks, files |
| 🔧 | system | content_type | System or infrastructure work | threads, tasks, n5 |
| 🐛 | bug_fix | content_type | Bug fix or debugging | threads, tasks, issues |
| 💬 | communication | content_type | Communication or messaging | threads, tasks, email |
| 🏗️ | architecture | content_type | Architecture or design work | threads, planning, design |
| ⚡ | performance | content_type | Performance or optimization | threads, tasks, optimization |
| 🔒 | security | content_type | Security or privacy | threads, tasks, security |
| 🧪 | testing | content_type | Testing or validation | threads, tasks, qa |
| 📊 | data | content_type | Data work or analytics | threads, tasks, analysis |
| 🎨 | design | content_type | UI/UX or visual design | threads, tasks, ui |
| 🚀 | deployment | action | Deployment or launch | threads, tasks, releases |
| 📦 | package | content_type | Package or module work | threads, tasks, code |
| 🔄 | sync | action | Sync or integration | threads, tasks, integration |
| 🗂️ | organization | action | Organization or cleanup | threads, tasks, files |
| 💡 | idea | content_type | Ideas or brainstorming | threads, lists, planning |
| 📅 | meeting | content_type | Meeting or discussion | threads, tasks, calendar |
| ⏰ | scheduled | status | Scheduled or recurring | tasks, automation |
| 🎓 | learning | content_type | Learning or tutorial | threads, knowledge, documentation |
| 🤝 | collaboration | content_type | Collaboration or partnership | threads, tasks, team |

---

## Detailed Descriptions

### ✅ Completed

**Category:** status  
**Meaning:** Completed successfully  
**Priority:** 10  
**Contexts:** threads, tasks, todos, lists

**Usage Notes:**  
Thread objectives fully achieved, no errors. Tasks finished successfully.

**Keywords:** complete, done, finished, success, accomplished

**Detection (Positive):** status=complete, no_errors, objectives_met
**Detection (Negative):** has_errors, incomplete

---

### ❌ Failed

**Category:** status  
**Meaning:** Failed or error  
**Priority:** 100  
**Contexts:** threads, tasks, system

**Usage Notes:**  
Thread ended with unresolved errors or failures. Critical issues.

**Keywords:** failed, error, unsuccessful, broken, crash

**Detection (Positive):** has_errors, exit_code!=0, exception, failed
**Detection (Negative):** status=complete, resolved

---

### 🚧 In Progress

**Category:** status  
**Meaning:** Work in progress / under construction  
**Priority:** 80  
**Contexts:** threads, tasks, projects

**Usage Notes:**  
Thread paused mid-work, to be resumed. Active development.

**Keywords:** wip, progress, building, developing, ongoing

**Detection (Positive):** status=in_progress, paused, resume_later
**Detection (Negative):** status=complete, abandoned

---

### 🔗 Linked

**Category:** relationship  
**Meaning:** Linked or sequential threads  
**Priority:** 70  
**Contexts:** threads

**Usage Notes:**  
Part of a series. Use with #N for sequence numbers (e.g., CRM Refactor #2)

**Keywords:** linked, sequential, series, continuation, part

**Detection (Positive):** has_sequence_number, continuation_of, follows

---

### 📰 Research

**Category:** content_type  
**Meaning:** Research, articles, knowledge gathering  
**Priority:** 40  
**Contexts:** threads, lists, knowledge

**Usage Notes:**  
Knowledge gathering, article processing, insights extraction

**Keywords:** article, research, insights, knowledge, reading, analysis, study

**Detection (Positive):** article, research, knowledge_base

---

### 🎯 Strategy

**Category:** content_type  
**Meaning:** Strategy, planning, GTM  
**Priority:** 40  
**Contexts:** threads, tasks, planning

**Usage Notes:**  
Strategic work, go-to-market planning, high-level vision

**Keywords:** GTM, strategy, positioning, planning, roadmap, vision, goals

**Detection (Positive):** GTM, strategy, planning

---

### 📝 Documentation

**Category:** content_type  
**Meaning:** Documentation work  
**Priority:** 40  
**Contexts:** threads, tasks, files

**Usage Notes:**  
Pure documentation work, writing guides, README files

**Keywords:** document, write, draft, README, guide, notes, doc

**Detection (Positive):** documentation, writing, README

---

### 🔧 System

**Category:** content_type  
**Meaning:** System or infrastructure work  
**Priority:** 40  
**Contexts:** threads, tasks, n5

**Usage Notes:**  
N5 system improvements, infrastructure, tooling, automation

**Keywords:** N5, system, infrastructure, commands, scripts, workflow, tools

**Detection (Positive):** N5, system, infrastructure, commands

---

### 🐛 Bug Fix

**Category:** content_type  
**Meaning:** Bug fix or debugging  
**Priority:** 60  
**Contexts:** threads, tasks, issues

**Usage Notes:**  
Debugging, troubleshooting, fixing issues (with resolution)

**Keywords:** bug, fix, debug, troubleshoot, issue, error, patch

**Detection (Positive):** bug, fix, debug, issue, resolved

---

### 💬 Communication

**Category:** content_type  
**Meaning:** Communication or messaging  
**Priority:** 40  
**Contexts:** threads, tasks, email

**Usage Notes:**  
Email work, message drafting, outreach, communication tasks

**Keywords:** email, message, outreach, communication, response, follow-up, slack

**Detection (Positive):** email, message, communication

---

### 🏗️ Architecture

**Category:** content_type  
**Meaning:** Architecture or design work  
**Priority:** 40  
**Contexts:** threads, planning, design

**Usage Notes:**  
System architecture, design decisions, structural planning

**Keywords:** architecture, design, structure, schema, model, framework

**Detection (Positive):** architecture, design, schema

---

### ⚡ Performance

**Category:** content_type  
**Meaning:** Performance or optimization  
**Priority:** 40  
**Contexts:** threads, tasks, optimization

**Usage Notes:**  
Performance improvements, optimization work, speed enhancements

**Keywords:** performance, optimize, speed, efficiency, fast, refactor

**Detection (Positive):** performance, optimize, efficiency

---

### 🔒 Security

**Category:** content_type  
**Meaning:** Security or privacy  
**Priority:** 50  
**Contexts:** threads, tasks, security

**Usage Notes:**  
Security improvements, auth work, privacy enhancements

**Keywords:** security, privacy, auth, permissions, encryption, vulnerability

**Detection (Positive):** security, privacy, auth

---

### 🧪 Testing

**Category:** content_type  
**Meaning:** Testing or validation  
**Priority:** 40  
**Contexts:** threads, tasks, qa

**Usage Notes:**  
Testing, validation, QA work, verification tasks

**Keywords:** test, testing, validation, qa, verify, check

**Detection (Positive):** test, validation, verify

---

### 📊 Data

**Category:** content_type  
**Meaning:** Data work or analytics  
**Priority:** 40  
**Contexts:** threads, tasks, analysis

**Usage Notes:**  
Data processing, analytics, metrics, reporting dashboards

**Keywords:** data, analytics, metrics, stats, dashboard, reporting

**Detection (Positive):** data, analytics, metrics

---

### 🎨 Design

**Category:** content_type  
**Meaning:** UI/UX or visual design  
**Priority:** 40  
**Contexts:** threads, tasks, ui

**Usage Notes:**  
UI/UX work, visual design, interface improvements

**Keywords:** design, UI, UX, interface, visual, layout, styling

**Detection (Positive):** UI, UX, design, interface

---

### 🚀 Deployment

**Category:** action  
**Meaning:** Deployment or launch  
**Priority:** 50  
**Contexts:** threads, tasks, releases

**Usage Notes:**  
Deployment, launch, going live, production releases

**Keywords:** deploy, launch, release, ship, production, live

**Detection (Positive):** deploy, launch, production

---

### 📦 Package

**Category:** content_type  
**Meaning:** Package or module work  
**Priority:** 40  
**Contexts:** threads, tasks, code

**Usage Notes:**  
Package management, module work, dependency updates

**Keywords:** package, module, library, dependency, npm, pip

**Detection (Positive):** package, module, dependency

---

### 🔄 Sync

**Category:** action  
**Meaning:** Sync or integration  
**Priority:** 40  
**Contexts:** threads, tasks, integration

**Usage Notes:**  
Integration work, syncing systems, API connections

**Keywords:** sync, integration, connect, bridge, api, webhook

**Detection (Positive):** sync, integration, api

---

### 🗂️ Organization

**Category:** action  
**Meaning:** Organization or cleanup  
**Priority:** 30  
**Contexts:** threads, tasks, files

**Usage Notes:**  
Organization, cleanup, refactoring, file management

**Keywords:** organize, cleanup, refactor, restructure, tidy

**Detection (Positive):** cleanup, organize, refactor

---

### 💡 Idea

**Category:** content_type  
**Meaning:** Ideas or brainstorming  
**Priority:** 30  
**Contexts:** threads, lists, planning

**Usage Notes:**  
Brainstorming, ideas, concepts, proposals

**Keywords:** idea, brainstorm, concept, proposal, suggestion

**Detection (Positive):** idea, brainstorm, concept

---

### 📅 Meeting

**Category:** content_type  
**Meaning:** Meeting or discussion  
**Priority:** 40  
**Contexts:** threads, tasks, calendar

**Usage Notes:**  
Meetings, discussions, sync calls, reviews

**Keywords:** meeting, discussion, call, sync, standup, review

**Detection (Positive):** meeting, discussion, call

---

### ⏰ Scheduled

**Category:** status  
**Meaning:** Scheduled or recurring  
**Priority:** 40  
**Contexts:** tasks, automation

**Usage Notes:**  
Scheduled tasks, recurring automation, cron jobs

**Keywords:** scheduled, recurring, cron, automated, periodic

**Detection (Positive):** scheduled, recurring, cron

---

### 🎓 Learning

**Category:** content_type  
**Meaning:** Learning or tutorial  
**Priority:** 30  
**Contexts:** threads, knowledge, documentation

**Usage Notes:**  
Learning, tutorials, educational content, training

**Keywords:** learn, tutorial, education, training, course, lesson

**Detection (Positive):** learn, tutorial, education

---

### 🤝 Collaboration

**Category:** content_type  
**Meaning:** Collaboration or partnership  
**Priority:** 30  
**Contexts:** threads, tasks, team

**Usage Notes:**  
Collaborative work, team projects, partnerships

**Keywords:** collaboration, team, partner, together, shared

**Detection (Positive):** collaboration, team, partner

---

## Emojis by Category

### Status

Indicates the current state or status of an item

- ✅ **completed** - Completed successfully
- ❌ **failed** - Failed or error
- 🚧 **in_progress** - Work in progress / under construction
- ⏰ **scheduled** - Scheduled or recurring

### Content Type

Indicates the type of content or work being done

- 📰 **research** - Research, articles, knowledge gathering
- 🎯 **strategy** - Strategy, planning, GTM
- 📝 **documentation** - Documentation work
- 🔧 **system** - System or infrastructure work
- 🐛 **bug_fix** - Bug fix or debugging
- 💬 **communication** - Communication or messaging
- 🏗️ **architecture** - Architecture or design work
- ⚡ **performance** - Performance or optimization
- 🔒 **security** - Security or privacy
- 🧪 **testing** - Testing or validation
- 📊 **data** - Data work or analytics
- 🎨 **design** - UI/UX or visual design
- 📦 **package** - Package or module work
- 💡 **idea** - Ideas or brainstorming
- 📅 **meeting** - Meeting or discussion
- 🎓 **learning** - Learning or tutorial
- 🤝 **collaboration** - Collaboration or partnership

### Action

Indicates an action or process

- 🚀 **deployment** - Deployment or launch
- 🔄 **sync** - Sync or integration
- 🗂️ **organization** - Organization or cleanup

### Relationship

Indicates relationships between items

- 🔗 **linked** - Linked or sequential threads

---

## Usage Contexts

### Threads

Thread titles in conversation list

**Priority Order:** status → relationship → content_type → action

### Tasks

Task items in lists and todos

**Priority Order:** status → content_type → action

### Files

File organization and naming

**Priority Order:** content_type → status

### Knowledge

Knowledge base entries and articles

**Priority Order:** content_type

---

## Detection Priority

When auto-selecting emojis, higher priority values are checked first:

| Priority | Emoji | Name | Category |
|----------|-------|------|----------|
| 100 | ❌ | failed | status |
| 80 | 🚧 | in_progress | status |
| 70 | 🔗 | linked | relationship |
| 60 | 🐛 | bug_fix | content_type |
| 50 | 🔒 | security | content_type |
| 50 | 🚀 | deployment | action |
| 40 | 📰 | research | content_type |
| 40 | 🎯 | strategy | content_type |
| 40 | 📝 | documentation | content_type |
| 40 | 🔧 | system | content_type |
| 40 | 💬 | communication | content_type |
| 40 | 🏗️ | architecture | content_type |
| 40 | ⚡ | performance | content_type |
| 40 | 🧪 | testing | content_type |
| 40 | 📊 | data | content_type |
| 40 | 🎨 | design | content_type |
| 40 | 📦 | package | content_type |
| 40 | 🔄 | sync | action |
| 40 | 📅 | meeting | content_type |
| 40 | ⏰ | scheduled | status |
| 30 | 🗂️ | organization | action |
| 30 | 💡 | idea | content_type |
| 30 | 🎓 | learning | content_type |
| 30 | 🤝 | collaboration | content_type |
| 10 | ✅ | completed | status |

---

## Quick Reference

### By Use Case

#### Thread Status
- ✅ Completed successfully
- ❌ Failed or error
- 🚧 Work in progress / under construction
- ⏰ Scheduled or recurring

#### Work Type
- 📰 Research, articles, knowledge gathering
- 🎯 Strategy, planning, GTM
- 📝 Documentation work
- 🔧 System or infrastructure work
- 🐛 Bug fix or debugging
- 💬 Communication or messaging
- 🏗️ Architecture or design work
- ⚡ Performance or optimization
- 🔒 Security or privacy
- 🧪 Testing or validation
- 📊 Data work or analytics
- 🎨 UI/UX or visual design
- 📦 Package or module work
- 💡 Ideas or brainstorming
- 📅 Meeting or discussion
- 🎓 Learning or tutorial
- 🤝 Collaboration or partnership

#### Actions
- 🚀 Deployment or launch
- 🔄 Sync or integration
- 🗂️ Organization or cleanup

---

## Maintenance

**To add/modify emojis:**
1. Edit `file 'N5/config/emoji-legend.json'`
2. Run `python3 N5/scripts/n5_emoji_legend_sync.py`
3. This markdown file will be regenerated automatically

**JSON Schema:**
```json
{
  "symbol": "🔧",
  "name": "system",
  "category": "content_type",
  "meaning": "System or infrastructure work",
  "contexts": ["threads", "tasks"],
  "keywords": ["system", "infrastructure"],
  "priority": 40,
  "usage_notes": "N5 system improvements",
  "detection_rules": {
    "positive": ["system", "N5"],
    "negative": []
  }
}
```

---

*Auto-generated on 2025-10-16 06:23:07 UTC*