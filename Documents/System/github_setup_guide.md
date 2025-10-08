# GitHub Setup Guide for Zo Computer

## Step 1: Create Your GitHub Account
1. Go to https://github.com
2. Sign up with your email address
3. Choose a username (this will be public)

## Step 2: Create Private Repository
1. Click "New repository" (green button)
2. Name: `zo-workspace-backup` 
3. **IMPORTANT**: Select "Private" (NOT "Public")
4. Don't check "Initialize with README"
5. Click "Create repository"

## Step 3: Get Your Repository URL
After creating, copy the HTTPS URL:
- It looks like: `https://github.com/YOUR_USERNAME/zo-workspace-backup.git`

## Step 4: Configure Git in Zo
```bash
# Set your name and email (replace with your actual email)
git config --global user.name "YOUR_GITHUB_USERNAME"
git config --global user.email "your-real-email@domain.com"
```

## Step 5: Connect to GitHub
Replace YOUR_USERNAME with your actual username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/zo-workspace-backup.git
```

## Step 6: Set Up Authentication
You have 2 safe options:

### Option A: GitHub CLI (Recommended)
```bash
# Install GitHub CLI
gh auth login
# Follow prompts to authenticate
```

### Option B: Personal Access Token
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with "repo" scope
3. Use it as password when prompted

## Step 7: Push Your First Commit
```bash
git push -u origin main
```

## Privacy Checklist ✅
- [ ] Repository is set to Private
- [ ] No sensitive data in commits
- [ ] Using secure authentication
- [ ] Reviewing what's being pushed

## What Others Can See
- **Private repo**: Only you can see contents
- **Public activity**: Your username, commit messages, timestamps
- **Protected**: File contents, actual code, sensitive data

## Next Steps
Once set up, you can:
- Push commits to backup your work
- Pull changes if working from multiple computers
- Use GitHub's web interface to view your code history