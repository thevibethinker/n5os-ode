#!/bin/bash
# Safe GitHub Setup Script for Zo Computer

echo "=== Safe GitHub Setup for Zo Computer ==="
echo

# Check current Git status
echo "📍 Current Git Status:"
git status --short | head -5
echo

# Function to safely get user input
get_input() {
    local prompt="$1"
    local input=""
    while [[ -z "$input" ]]; do
        read -p "$prompt" input
        if [[ -z "$input" ]]; then
            echo "❌ This field cannot be empty. Please try again."
        fi
    done
    echo "$input"
}

# Get GitHub credentials safely
echo "🔐 Setting up Git configuration..."
echo

# Git username
echo "Enter your GitHub username:"
USERNAME=$(get_input "Username: ")
git config --global user.name "$USERNAME"

# Git email
echo "Enter your email address (use the one registered with GitHub):"
EMAIL=$(get_input "Email: ")
git config --global user.email "$EMAIL"

# Repository URL
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/yourusername/your-repo.git"
REPO_URL=$(get_input "Repository URL: ")

# Verify it's HTTPS (safer for beginners)
if [[ ! "$REPO_URL" =~ ^https://github\.com/.*\.git$ ]]; then
    echo "❌ URL format should be: https://github.com/username/repo.git"
    echo "Please create a private repository on GitHub first."
    exit 1
fi

echo
echo "⚙️  Adding remote repository..."
if git remote get-url origin 2>/dev/null; then
    echo "Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

echo
echo "🔧 Git Configuration Summary:"
echo "Username: $(git config user.name)"
echo "Email: $(git config user.email)"
echo "Remote URL: $(git remote get-url origin)"
echo

echo "✅ Basic setup complete!"
echo
echo "🚀 Next steps:"
echo "1. Install GitHub CLI: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
echo "2. Authenticate: gh auth login"
echo "3. Then push your code: git push -u origin main"
echo
echo "📋 For manual authentication with token:"
echo "1. Go to GitHub → Settings → Developer settings → Personal access tokens"
echo "2. Generate a token with 'repo' scope"
echo "3. When you push, use the token as your password"