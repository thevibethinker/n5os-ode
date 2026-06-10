---
name: pulse-visual-elevation
description: >
  Orchestrate visual-skill execution by loading a spec, asking for a skill
  chain, applying director checkpoints, and producing the execution envelope
  for the agent to follow.
compatibility: Created for Zo Computer
metadata:
  author: va.zo.computer
  version: "1.0.0"
created: 2026-06-10
last_edited: 2026-06-10
version: 1.0
provenance: con_sQ03t9FFBWIVZTXO
---

# Pulse Visual Elevation

Orchestrates visual skill execution around a spec, target, and director-style checkpoint flow.

## When to Use

Use when a visual/design task needs an ordered skill chain and execution envelope.

## Responsibilities

- Load the spec and target
- Decide whether a direct chain or director checkpoint is needed
- Apply auth-aware policy for gated URLs
- Produce an execution envelope and next-step plan

## Inputs

- Spec text or file path
- Target URL or workspace path
- Optional cookies file for authenticated browser captures
- Optional director envelope

## Outputs

- Chain plan
- Envelope JSON
- Summary of skipped or deferred steps

## Notes

This skill is an orchestrator, not a design skill itself.
