---
created: 2026-02-17
last_edited: 2026-02-17
version: 1.0
provenance: con_korOfWz5bTYqA9FI
voice_optimized: true
source: https://docs.zocomputer.com/byok
---

# Bring Your Own API Key

You can connect your own AI provider API keys to Zo. This lets you use models from OpenAI, Anthropic, Groq, OpenRouter, Together AI, and any OpenAI-compatible endpoint.

Go to Settings, then Advanced, and find Custom Models. Add your provider's base URL, API key, and model ID. Click Test to verify the connection.

Supported formats are OpenAI-compatible, Anthropic-compatible, and Groq. Make sure your provider supports streaming and tool use — Zo needs both.

After adding a custom model, select it from the model picker in chat. Custom models don't fall back to Zo's built-in models if they fail, so make sure your API key has sufficient credits.
