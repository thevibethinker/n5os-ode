#!/bin/bash
# Push all historical commits to GitHub

echo "=== Pushing Your 23 Commits to GitHub ==="
echo "📍 Repository: n5-os-zo (private - only you can see it)"
echo "🔄 Content: All your N5 OS development history"
echo
echo "ℹ️  Note: GitHub will show these as new commits with current timestamps,"
echo "   but the commit messages and content will be preserved."
echo
echo "🔒 Privacy: Your repository is private - only you have access!"
echo

# Check what's new to push
echo "📊 Files that will be pushed:"
git diff --stat HEAD origin/main 2>/dev/null || echo "First push - all files will be uploaded"
echo

echo "🎯 What's being synced:"
echo "- All 23 commits with original messages"
echo "- Complete N5 OS codebase"
echo "- Command authoring system"
echo "- System upgrades and documentation"
echo "- Lists management functionality"
echo

read -p "Ready to push all your commits to GitHub? (y/N): " confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."
    
    # Push all commits to main branch
    if git push -u origin main; then
        echo "✅ SUCCESS! All commits pushed to private repository!"
        echo "🎉 Your N5 OS development history is now backed up on GitHub!"
        echo
        echo "📱 You can now view your commits at:"
        echo "https://github.com/vrijenattawar/n5-os-zo/commits/main"
        echo
        echo "🔒 Remember: Only you can see this private repository."
        echo "🔗 Share the repo URL only if you want to grant collaborator access."
    else
        echo "❌ Push failed. Let me check authentication..."
        echo
        echo "🔐 Let's set up authentication:")
        
        # Check authentication
        if which gh >/dev/null; then
            echo "GitHub CLI detected. Trying authentication..."
            if gh auth login; then
                echo "✅ Authenticated! Trying push again..."
                git push -u origin main
            fi
        else
            echo "You'll need to authenticate. Try:"
            echo "1. Install GitHub CLI: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg"
            echo "2. Then run: gh auth login"
            echo "3. Finally: git push origin main"
        fi
    fi
else
    echo "⏸️  Push cancelled. Your commits remain locally."
    echo "Run this again when ready: git push origin main"
fi

echo
echo "📋 Your commit history preview:"
git log --oneline -5