---
title: "Short.io Link Creator"
description: |
  Prompt-driven workflow that gathers the metadata required to open a Short.io
  link, then launches the canonical service script (`shortio_link_service.py`) so the
  key is managed solely via your Developer secrets.
tags:
  - short.io
  - integrations
  - link
  - automation
tool: true
version: 1.0
---

This prompt asks you a set of simple questions about the link you want to create and
then runs the shell command that calls `file 'N5/scripts/shortio_link_service.py'`.
The Short.io API key is pulled automatically from the `SHORT_IO_KEY` developer secret
and is never typed into this prompt.

**Questions this prompt will ask you:**
1. What URL do you want to shorten?
2. Do you want to give it a friendly **title** (helps with Short.io reporting)?
3. Should the short link use a specific **domain** (if your Short.io account owns more
   than one)?
4. Do you need a custom **path/slug** (e.g., `careerspan-x`)?
5. Do you want to attach a **QR code** or other media asset (optional note for your
   own reference)?
6. Any other **notes or tags** you want recorded alongside the link? (For internal
   bookkeeping; nothing is sent to Short.io.)

After you answer the questions, this prompt will:
- Run `python3 N5/scripts/shortio_link_service.py create --url <your URL>` with the
  additional options you supplied.
- Print the Short.io JSON response so you can capture the short URL/ID.
- Automatically persist link metadata under `file 'N5/data/shortio_links.jsonl'`.

Example invocation text you can use in Zo: `@Short.io Link Creator Create a short
link for www.example.com titled "Careerspan Launch" using the `N5` shell command.`
Once the link is generated, the system will begin tracking clicks daily via the
scheduled ingestion job that runs `file 'N5/scripts/shortio_stats_ingest.py'`.

