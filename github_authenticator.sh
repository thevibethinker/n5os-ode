#!/bin/bash
# Safe GitHub Authenticator for Zo Computer

echo "=== GitHub Authentication Setup ==="
echo

# Check if already authenticated
if gh auth status 2>/dev/null; then
    echo "✅ Already authenticated with GitHub:"
    gh auth status
    echo
    echo "🚀 Ready to push your commits!"
    read -p "Would you like to push now? (y/N): " push_now
    if [[ "$push_now" =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to GitHub..."
        git push -u origin main
    fi
    exit 0
fi

echo "🔐 Let's set up GitHub authentication..."
echo "This allows you to push commits to your private repository."
echo

echo "Please choose your authentication method:"
echo "1) GitHub CLI (Recommended - easiest)"
echo "2) Personal Access Token"
echo "3) Check current setup"
echo

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🔑 Using GitHub CLI authentication..."
        echo "You'll be prompted to authenticate with your browser."
        echo
        gh auth login
        
        if gh auth status 2>/dev/null; then
            echo "✅ Successfully authenticated!"
            echo
            read -p "Would you like to push your commits now? (y/N): " push_now
            if [[ "$push_now" =~ ^[Yy]$ ]]; then
                echo "📤 Pushing to GitHub..."
                git push -u origin main
            fi
        else
            echo "❌ Authentication failed. Please try again."
        fi
        ;;
        
    2)
        echo "🔗 Setting up Personal Access Token authentication..."
        echo
        echo "📋 Step-by-step guide:"
        echo "1. Go to https://github.com/settings/tokens"
        echo "2. Click 'Generate new token'"
        echo "3. Give it a name like 'Zo Computer Access'"
        echo "4. Select 'repo' scope (full repository access)"
        echo "5. Click 'Generate token'"
        echo "6. Copy the token (it's only shown once!)"
        echo
        
        read -p "Press Enter when you have your token ready..."
        echo
        echo "📝 Now let's configure authentication..."
        echo "NOTE: When you push, use your GitHub username as username"
        echo "and the personal access token as your password"
        echo
        
        echo "To test, run: git push origin main"
        echo "When prompted for username/password:"
        echo "- Username: Your GitHub username"
        echo "- Password: Your personal access token"
        ;;
        
    3)
        echo "🔍 Current Git configuration:"
        echo "Username: $(git config user.name || echo 'Not set')"
        echo "Email: $(git config user.email || echo 'Not set')"
        echo "Remote: $(git remote get-url origin 2>/dev/null || echo 'Not set')"
        echo
        echo "Git status:"
        git status --short | head -10
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac

echo
echo "📚 Helpful commands:"
echo "- Check status: git status"
echo "- View commits: git log --oneline"
echo "- Add files: git add filename"
echo "- Commit: git commit -m 'Your message'"
echo "- Push to GitHub: git push origin main"