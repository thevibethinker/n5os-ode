# Simple GitHub Push Guide

## Two Easy Options

### Option 1: Personal Access Token (Fastest)
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "Zo Computer Push"
4. Check "repo" scope (full repository access)
5. Generate and copy the token
6. In Zo terminal, run:
   ```bash
   git push https://YOUR_TOKEN@github.com/vrijenattawar/n5-os-zo.git main
   ```

### Option 2: GitHub CLI (More Secure)
Run this in Zo:
```bash
cd /home/workspace
gh auth login
git push origin main
```

## What You'll See
- First push: Your 23 commits will upload
- Subsequent pushes: Only new commits will sync
- GitHub will show: "vrijenattawar pushed x commits to main"

## After First Push
Once successful, run these commands to finish setup:
```bash
git remote set-url origin https://github.com/vrijenattawar/n5-os-zo.git
git branch --set-upstream-to=origin/main main
```

Then future pushes will be simpler: `git push`