#!/bin/bash
# First GitHub Commit Setup

echo "=== Your First GitHub Commit ==="
echo

# Create a safe initial commit with minimal info
echo "📝 Creating your first commit..."

# Add a small, safe file first to test
cat > README_github_setup.md << EOF
# Zo Computer Workspace

This repository contains my Zo Computer workspace.

## What's Zo Computer?
Zo Computer is my personal AI-powered cloud workspace for productivity, coding, and knowledge management.

## Privacy Notice
This is a private repository - my files are not publicly accessible.

## Last Updated
$(date)

## Contact
This workspace belongs to V (va.zo.computer)
EOF

# Add the README file
git add README_github_setup.md

# Create initial commit
echo "🎯 Creating initial commit..."
git commit -m "Initial commit: Zo Computer workspace setup

- Added README with workspace description
- Private repository for personal use
- First commit to test GitHub integration"

echo "✅ Commit created successfully!"
echo

# Check if we have a remote set up
if git remote get-url origin 2>/dev/null; then
    echo "📤 Ready to push to GitHub!"
    echo "Repository: $(git remote get-url origin)"
    echo
    
    read -p "Would you like to push this commit to GitHub now? (y/N): " push_choice
    
    if [[ "$push_choice" =~ ^[Yy]$ ]]; then
        echo "🚀 Pushing to GitHub..."
        if git push -u origin main; then
            echo "✅ Successfully pushed to GitHub!"
            echo "🎉 Your commits are now backed up on GitHub!"
        else
            echo "❌ Push failed. Let's set up authentication first."
            echo "Run: bash github_authenticator.sh"
        fi
    else
        echo "💾 Commit saved locally. Push when ready with: git push origin main"
    fi
else
    echo "⚠️  No GitHub repository configured yet."
    echo "Set up your GitHub repository first, then run: bash github_authenticator.sh"
fi

echo
echo "📋 Next steps:"
echo "1. Your commit is ready locally"
echo "2. Once GitHub is connected, push with: git push origin main"
echo "3. Then GitHub will show your commits!"
echo
echo "🔒 Privacy: Only commit messages and timestamps are visible"