# LLM Integration Guide for Meeting Intelligence Orchestrator

## Current Status

The Meeting Intelligence Orchestrator now has **full LLM integration** using Anthropic's Claude API (the same LLM powering Zo conversations).

## How It Works

### Architecture

```
Meeting Transcript
      ↓
Orchestrator Script
      ↓
Anthropic Claude API (via Python SDK)
      ↓
Structured JSON Extractions
      ↓
Formatted Markdown Blocks
```

### LLM Provider: Anthropic Claude

The script uses **Anthropic's Claude 3.5 Sonnet** - the same advanced LLM that powers Zo's conversational interface. This ensures:
- Consistent quality with Zo's responses
- Native JSON extraction capabilities
- Strong reasoning for complex meeting analysis
- Reliable structured output generation

## Setup Instructions

### Option 1: Set API Key in Environment

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Then run the orchestrator:

```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=sofia-2025-10-09
```

### Option 2: Add to Shell Profile

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Option 3: Use Simulation Mode (No API Key Required)

For testing without an API key:

```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=sofia-2025-10-09 \
  --use-simulation
```

## How to Get an Anthropic API Key

1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and store it securely

**Note**: Anthropic offers:
- Free tier for testing
- Pay-as-you-go pricing
- Claude 3.5 Sonnet: ~$3/million input tokens, ~$15/million output tokens

## LLM Processing Flow

### Production Mode (with API Key)

1. **Block Extraction Request**: Orchestrator identifies which blocks to generate
2. **Prompt Construction**: Builds system + user prompts with transcript and JSON schema
3. **API Call**: Sends request to Anthropic Claude API
4. **JSON Parsing**: Extracts structured data from LLM response
5. **Fallback**: If API call fails → automatically uses simulation data
6. **Block Assembly**: Formats extracted data into markdown blocks

### Simulation Mode (--use-simulation flag)

1. Uses pre-built test data (Sofia meeting example)
2. No API calls made
3. Instant processing
4. Useful for development/testing

## Features

### Error Handling

- **Retry Logic**: Up to 3 attempts with exponential backoff
- **JSON Parsing**: Handles markdown code blocks in responses
- **Graceful Degradation**: Falls back to simulation on failure
- **Comprehensive Logging**: All operations logged to `N5/logs/orchestrator_{meeting_id}.log`

### API Configuration

```python
# In meeting_intelligence_orchestrator.py:

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Latest Sonnet model
    max_tokens=4096,                     # Sufficient for complex extractions
    system=system_prompt,                # Extraction instructions
    messages=[{
        "role": "user",
        "content": user_prompt           # Transcript + JSON schema
    }]
)
```

### Prompt Engineering

Each block type has a custom extraction prompt with:
- Clear system instructions
- Full transcript context
- Detailed JSON schema
- Field-specific guidance
- Examples of expected output

Example for SALIENT_QUESTIONS (B21):

```json
{
  "question": [
    {
      "text": "the question (explicit or implicit)",
      "why_it_matters": "strategic importance",
      "speaker": "Me or Them",
      "timestamp": "approximate time or 'unknown'",
      "action_hint": "suggested next step to address",
      "origin": "explicit or implicit"
    }
  ],
  "secondary_questions": ["list of other noteworthy questions"]
}
```

## Verification

### Check if API Key is Set

```bash
echo $ANTHROPIC_API_KEY
```

### Test with Simulation Mode First

```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=test-run \
  --use-simulation
```

### Run in Production Mode

```bash
export ANTHROPIC_API_KEY="your-key-here"

python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=sofia-production-run
```

### Check Logs

```bash
tail -f N5/logs/orchestrator_sofia-production-run.log
```

Look for:
- `"LLM API call attempt 1/3"` - API call started
- `"LLM response received: XXX chars"` - Response received
- `"Successfully parsed JSON with X keys"` - Extraction successful
- `"LLM extraction failed for {block_id}, using simulation fallback"` - Fallback triggered

## Cost Estimation

### Per Meeting Processing

Typical meeting transcript: ~5,000 words (~7,500 tokens)

- **Input**: ~7,500 tokens × 10 blocks = 75,000 tokens
- **Output**: ~500 tokens × 10 blocks = 5,000 tokens

**Estimated cost per meeting**: $0.30 - $0.50

### Monthly Usage (100 meetings)

- **Cost**: ~$30-50/month
- **Benefit**: Fully automated meeting intelligence extraction
- **Time Saved**: ~2 hours per meeting × 100 = 200 hours/month

## Troubleshooting

### "Warning: ANTHROPIC_API_KEY not found"

**Solution**: Set the environment variable:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### "LLM API error: Authentication failed"

**Solution**: Check that your API key is valid and active at https://console.anthropic.com/

### "JSON parse error"

**Solution**: The script automatically retries and falls back to simulation. Check logs for details.

### All extractions using simulation data

**Solution**: Verify API key is set correctly and API is accessible:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "test"}]}'
```

## Alternative: Zo's Built-In Processing

If you prefer to use Zo's conversation-based LLM processing:

1. Run orchestrator in "request generation" mode
2. Review generated extraction requests in `N5/logs/llm_requests/`
3. Ask Zo's LLM (me!) to process them
4. Manually integrate results

This approach requires manual intervention but doesn't require an API key.

## Next Steps

1. **Obtain API Key**: Sign up at https://console.anthropic.com/
2. **Set Environment Variable**: `export ANTHROPIC_API_KEY="..."`
3. **Test Run**: Use simulation mode first
4. **Production Run**: Process real transcripts with LLM
5. **Monitor Quality**: Review first 5-10 outputs for quality
6. **Tune Prompts**: Adjust extraction prompts based on results

## Support

For issues or questions:
- Check logs: `N5/logs/orchestrator_{meeting_id}.log`
- Review extraction requests: `N5/logs/llm_requests/`
- Test with simulation mode: `--use-simulation`
- Consult: `README_ORCHESTRATOR.md` and `QUICKSTART_ORCHESTRATOR.md`

---

**Status**: ✅ Fully integrated with Anthropic Claude API  
**Date**: 2025-10-09  
**Version**: 1.0
