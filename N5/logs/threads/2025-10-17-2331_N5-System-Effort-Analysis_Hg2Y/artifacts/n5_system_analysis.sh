#!/bin/bash

echo "=== N5 System Analysis ==="
echo ""
echo "## Total Files and Lines"
find /home/workspace/N5 -type f | wc -l
find /home/workspace/Knowledge -type f | wc -l
find /home/workspace/Lists -type f | wc -l
find /home/workspace/Records -type f | wc -l

echo ""
echo "## Python Scripts"
find /home/workspace/N5/scripts -name "*.py" | wc -l
find /home/workspace/N5/scripts -name "*.py" -exec wc -l {} + | tail -1

echo ""
echo "## Key Python Scripts (Top 20 by LOC)"
find /home/workspace/N5/scripts -name "*.py" -exec wc -l {} + | sort -rn | head -20

echo ""
echo "## Documentation"
find /home/workspace/N5 -name "*.md" | wc -l
find /home/workspace/Knowledge -name "*.md" | wc -l

echo ""
echo "## Schemas and Config"
find /home/workspace/N5/schemas -type f | wc -l
find /home/workspace/N5/config -type f | wc -l

echo ""
echo "## Git History"
cd /home/workspace/N5 && git log --oneline | wc -l
cd /home/workspace/N5 && git log --pretty=format:"%ad" --date=short | sort -u | head -1
cd /home/workspace/N5 && git log --pretty=format:"%ad" --date=short | sort -u | tail -1

