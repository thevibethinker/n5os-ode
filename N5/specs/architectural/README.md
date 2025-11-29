# Knowledge: Architectural Layer

**Version:** 3.0  
**Updated:** 2025-11-02

This directory contains meta-knowledge about how N5 OS operates.

---

## Purpose

Architectural knowledge defines the principles, standards, and patterns governing the N5 system.

---

## Core Documentation

### System Architecture
- **ARCHITECTURAL_OVERVIEW.md** - Complete system architecture
- **PRINCIPLE_USAGE_GUIDE.md** - How to use principles effectively

### Legacy Documentation
- **architectural_principles.md** - Original principle index
- **planning_prompt.md** - Think-Plan-Execute framework
- **research_frameworks.md** - Research methodologies

---

## Three-Layer Architecture

### Layer 1: Principles (37 YAML)
Core rules governing system behavior. Location: N5/prefs/principles/

Categories: Core, Safety, Quality, Design, Execution, Advanced

### Layer 2: Cognitive Prompts (3 active)
Mental models: Planning, Thinking, Navigator

### Layer 3: Personas (8 specialized)
All v2.0+ with full integration. Operator, Strategist, Builder, Teacher, Writer, Architect, Debugger, Researcher.

---

## How It Works

Pre-Flight Protocol (5 steps), Principle Application (automatic triggers), Persona Routing (Operator as quarterback), Risk Assessment (before destructive ops).

---

## Quick Reference

Find principles: ls N5/prefs/principles/P*.yaml
Validate: Check against N5/schemas/principle.schema.json
Switch persona: set_active_persona with persona_id

---

Last updated: 2025-11-02 21:14 ET
