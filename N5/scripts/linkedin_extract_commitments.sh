#!/bin/bash
# Wrapper for linkedin_commitment_extractor.py with API key loaded

export ANTHROPIC_API_KEY=$(cat ~/.anthropic_api_key 2>/dev/null || echo "")

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not found in ~/.anthropic_api_key"
    exit 1
fi

python3 /home/workspace/N5/scripts/linkedin_commitment_extractor.py "$@"
