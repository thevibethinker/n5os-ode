#!/bin/bash
# Setup OpenAI embeddings for N5 Cognition Layer
# Usage: source setup_openai.sh [API_KEY]

if [ -n "$1" ]; then
    export OPENAI_API_KEY="$1"
    echo "✓ OPENAI_API_KEY set from argument"
elif [ -z "$OPENAI_API_KEY" ]; then
    echo "Usage: source setup_openai.sh <your-api-key>"
    echo "   or: export OPENAI_API_KEY=sk-... && source setup_openai.sh"
    return 1 2>/dev/null || exit 1
fi

export N5_EMBEDDING_PROVIDER=openai
export N5_OPENAI_EMBEDDING_MODEL=text-embedding-3-small

echo "✓ N5_EMBEDDING_PROVIDER=openai"
echo "✓ N5_OPENAI_EMBEDDING_MODEL=text-embedding-3-small"
echo ""
echo "To reindex with OpenAI embeddings:"
echo "  python3 /home/workspace/N5/scripts/memory_indexer.py /home/workspace/Personal/Knowledge"

