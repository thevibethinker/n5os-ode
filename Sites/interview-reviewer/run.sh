#!/bin/bash
cd /home/workspace/Sites/interview-reviewer
export PORT=8780
export NODE_ENV=production
export BASE_URL="https://did-i-get-it-va.zocomputer.io"
exec bun run src/index.tsx
