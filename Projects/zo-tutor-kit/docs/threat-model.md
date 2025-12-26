---
created: 2025-11-30
last_edited: 2025-11-30
version: 1.0
---

# Tutor Protocol Threat Model (Draft)

This document will capture security assumptions, potential adversaries,
and mitigations for the Tutor Protocol and Tutor Kit implementation.

Initial focus:
- No remote code execution across Zos
- All cross-Zo communication goes through explicit Tutor sessions
- Byte-level accounting and local logging of all bridge traffic

