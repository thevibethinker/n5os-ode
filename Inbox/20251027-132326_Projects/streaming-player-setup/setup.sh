#!/bin/bash

echo "🎬 Zo Stream - Interactive Player Setup"
echo "========================================"
echo ""

# Check if TMDB API key is already configured
if grep -q "YOUR_TMDB_API_KEY" index.tsx; then
    echo "⚠️  TMDB API key not configured yet"
    echo ""
    echo "To complete setup:"
    echo "1. Get a free API key from: https://www.themoviedb.org/settings/api"
    echo "2. Run: ./setup.sh configure <YOUR_API_KEY>"
    echo ""
    
    if [ "$1" = "configure" ] && [ -n "$2" ]; then
        API_KEY="$2"
        echo "📝 Configuring TMDB API key..."
        
        # Backup original file
        cp index.tsx index.tsx.backup
        
        # Replace API key
        sed -i "s/YOUR_TMDB_API_KEY/$API_KEY/g" index.tsx
        
        echo "✅ API key configured successfully!"
        echo ""
        echo "🚀 Ready to start! Run: bun run dev"
    fi
else
    echo "✅ TMDB API key is configured"
    echo ""
    echo "🚀 Ready to start!"
    echo ""
    echo "Run: bun run dev"
fi

echo ""
echo "📖 For more information, see README.md"
