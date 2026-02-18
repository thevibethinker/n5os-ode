---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_korOfWz5bTYqA9FI
voice_optimized: true
source: https://docs.zocomputer.com/ssh-zo
---

# Connect to Your Zo via SSH

You can SSH into your Zo server to use it as a remote development environment. This lets you connect your favorite code editor like Cursor or VS Code directly to your Zo.

Steps: generate an SSH key on your computer, paste the public key into your Zo's authorized keys file, set up an SSH service on your Zo (label: ssh, port 2222, TCP type, entrypoint: /usr/sbin/sshd -D -p 2222), then connect from your computer's terminal.

You can also set up a shortcut in your SSH config so you just type "ssh zo" to connect. This is popular with developers who want to use Zo as their cloud dev environment.
