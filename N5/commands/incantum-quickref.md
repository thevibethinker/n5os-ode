---
date: "2025-10-08T22:20:36Z"
last-tested: "2025-10-08T22:20:36Z"
generated_date: "2025-10-08T22:20:36Z"
checksum: incantum_quickref_v1_0_0
tags:
  - incantum
  - triggers
  - reference
  - commands
category: productivity
priority: high
related_files:
anchors: [object Object]
---
# Incantum Quick Reference

**Incantum** is the natural language command system for N5 OS. Use the format: `incantum: [action]`

## 📋 Lists Commands

### Check List System Health
**Primary:** `incantum: check list system health`  
**Aliases:**
- `incantum: assess list maintenance`
- `incantum: list health status`
- `incantum: check lists for phase 3`
- `incantum: reveal the health of my list realm` ✨
- `incantum: conjure list system diagnostics` ✨

**What it does:** Monitors list count, detects similar lists, recommends Phase 3 implementation

---

### Add Item to List
**Primary:** `incantum: add item to list`  
**Aliases:**
- `incantum: add to list`
- `incantum: create list item`
- `incantum: remember this`
- `incantum: save to list`

**What it does:** Add an item to a list with intelligent auto-categorization

---

### Move List Item
**Primary:** `incantum: move list item`  
**Aliases:**
- `incantum: relocate item`
- `incantum: transfer list item`
- `incantum: move item between lists`

**What it does:** Move an item from one list to another atomically

---

## ⚙️ Operations Commands

### Generate Command Catalog
**Primary:** `incantum: generate command catalog`  
**Aliases:**
- `incantum: update command docs`
- `incantum: rebuild command catalog`
- `incantum: regenerate docs`

**What it does:** Generate command catalog and update prefs from commands.jsonl

---

### Rebuild System Index
**Primary:** `incantum: rebuild system index` ⚠️ **Destructive**  
**Aliases:**
- `incantum: regenerate index`
- `incantum: refresh system index`
- `incantum: reindex system`

**What it does:** Rebuild the N5 system index from source files (modifies critical files)  
**Note:** Always requires confirmation before execution

---

### Audit Git Changes
**Primary:** `incantum: audit git changes`  
**Aliases:**
- `incantum: check git safety`
- `incantum: review git status`
- `incantum: git safety audit`

**What it does:** Quick audit for overwrites or data loss in staged Git changes

---

### Show Development Timeline
**Primary:** `incantum: show development timeline`  
**Aliases:**
- `incantum: view timeline`
- `incantum: display system history`
- `incantum: show n5 timeline`

**What it does:** View n5.os development timeline and system history

---

### Add Timeline Entry
**Primary:** `incantum: add timeline entry`  
**Aliases:**
- `incantum: create timeline event`
- `incantum: log timeline item`
- `incantum: record timeline`

**What it does:** Add new entry to n5.os development timeline

---

## 🪄 How Incantum Works

### Recognition Flow
1. **Pattern Match:** Zo identifies matching commands
2. **Confidence Score:** Calculates match confidence (0-100%)
3. **Clarification:** Confirms when confidence is low or action is destructive
4. **Execution:** Runs the confirmed command
5. **Response:** Shows results with success/failure status

### Confidence Levels
- **>80%:** Execute immediately (safe commands only)
- **60-80%:** Ask for confirmation
- **<60%:** Suggest alternatives

### Safety Rules
- ⚠️ **Destructive commands** always require confirmation
- 🔒 Low confidence matches suggest alternatives
- 🎯 Context-aware using conversation history

---

## 💡 Tips

1. **Be natural:** Say what you mean conversationally
2. **Try variations:** Multiple trigger phrases work
3. **Use magical phrasing:** Spellcasting-style triggers (marked with ✨) add fun
4. **Check status:** Zo will confirm before destructive actions

---

## 📚 Full Documentation

- **System Overview:** `Knowledge/incantum_triggers.md`
- **Integration Plan:** `N5/System Documentation/incantum_system_plan.md`
- **Command Catalog:** `N5/commands.md`

---

**Total Available Triggers:** 8 commands with 36+ trigger phrases

**Last Updated:** 2025-09-30
