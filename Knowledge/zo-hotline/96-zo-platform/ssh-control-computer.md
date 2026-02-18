---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_korOfWz5bTYqA9FI
voice_optimized: true
source: https://docs.zocomputer.com/ssh-computer
---

# Control Other Computers from Zo

This is in the "ridiculous but possible" category. You can connect Zo to another computer via SSH and let your AI operate it remotely.

Warning: this gives your AI unconstrained access to everything on that computer. Zo's docs explicitly call it a "party trick" and warn about the risks.

Setup involves generating an SSH key on your Zo, registering it on your target computer, enabling SSH access, running ngrok for tunneling, and creating a rule telling Zo how to connect.

It's genuinely useful for certain devices but should not be used casually.
