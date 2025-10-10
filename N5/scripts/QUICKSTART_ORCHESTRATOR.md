# Meeting Intelligence Orchestrator - Quick Start Guide

## 🚀 5-Minute Quick Start

### Step 1: Test with Existing Example
```bash
cd /home/workspace

# Run with simulation mode (test data)
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/sofia-2025-10-09/transcript.txt \
  --meeting_id=sofia-2025-10-09 \
  --use-simulation

# View output
cat N5/records/meetings/sofia-2025-10-09/blocks.md
```

### Step 2: Try with Your Own Transcript

```bash
# Create a meeting folder
mkdir -p N5/records/meetings/my-meeting-2025-10-09

# Add your transcript (must be a .txt file)
nano N5/records/meetings/my-meeting-2025-10-09/transcript.txt
# ... paste transcript and save ...

# Run orchestrator (simulation mode first)
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/my-meeting-2025-10-09/transcript.txt \
  --meeting_id=my-meeting-2025-10-09 \
  --use-simulation

# Check output
cat N5/records/meetings/my-meeting-2025-10-09/blocks.md
```

### Step 3: Production Mode (Real LLM)

```bash
# Run WITHOUT --use-simulation flag for production
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=N5/records/meetings/my-meeting-2025-10-09/transcript.txt \
  --meeting_id=my-meeting-2025-10-09

# Check logs if needed
cat N5/logs/orchestrator_my-meeting-2025-10-09.log
```

---

## 📋 Transcript Format Tips

### ✅ GOOD: Granola-style (Recommended)
```
Me: How's the project going?
Them: Great! We're launching next week.
Me: Excellent. What do you need from us?
Them: Just the case study deck you mentioned.
```

### ✅ GOOD: Named Speakers
```
Vrijen: Tell me about your hiring challenges.
Sofia: We need help sourcing from communities.
Vrijen: We can help with that through our network.
```

### ⚠️ OK: Generic Labels
```
Speaker 1: Let's discuss the partnership.
Speaker 2: I'm excited about this opportunity.
```

---

## 🎯 What Gets Extracted

### Always Generated:
- **Metadata**: Title, subject line, stakeholder type, granola detection
- **Detailed Recap**: Key decisions, agreements, next steps
- **Resonance Points**: What resonated in the conversation

### Often Generated:
- **Salient Questions**: Strategic questions (explicit or implicit)
- **Debate Analysis**: Conflicting viewpoints and resolutions
- **Key Quotes**: 2-3 most impactful quotes
- **Deliverables**: Items promised to be sent

### Conditionally Generated:
- **Warm Intro Blurb**: When someone says "send me a blurb"
- **Founder Profile**: When discussing startups/founders
- **Product Ideas**: When product concepts are discussed

---

## 🔍 Checking Output Quality

### Good Signs:
✅ Specific names and dates (not placeholders)  
✅ Actual quotes from your transcript  
✅ Granola diarization shows `true` if you used Me:/Them: format  
✅ Questions include action hints  
✅ Deliverables list is complete  

### Red Flags:
❌ Generic placeholders like `[specific outcome]`  
❌ Empty blocks or "N/A" everywhere  
❌ Missing key information you know was in the call  

**Solution**: If you see red flags in simulation mode, check your transcript format. If you see them in production mode, check the logs.

---

## 🛠️ Common Commands

### Test Run (Simulation)
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=PATH/TO/transcript.txt \
  --meeting_id=MEETING_ID \
  --use-simulation
```

### Production Run
```bash
python3 N5/scripts/meeting_intelligence_orchestrator.py \
  --transcript_path=PATH/TO/transcript.txt \
  --meeting_id=MEETING_ID
```

### View Logs
```bash
cat N5/logs/orchestrator_MEETING_ID.log
```

### View Output
```bash
cat N5/records/meetings/MEETING_ID/blocks.md
```

---

## 💡 Pro Tips

1. **Use descriptive meeting IDs**: `investor-pitch-2025-10-09` instead of `meeting1`
2. **Test in simulation first**: Always run `--use-simulation` before production
3. **Check granola detection**: Use `Me:` and `Them:` format for best results
4. **Review logs**: Check `N5/logs/` if output seems wrong
5. **Iterate**: The system learns from your transcript patterns

---

## ⚡ Batch Processing

Process multiple transcripts:

```bash
#!/bin/bash
for transcript in N5/records/meetings/*/transcript.txt; do
  dir=$(dirname "$transcript")
  meeting_id=$(basename "$dir")
  
  echo "Processing: $meeting_id"
  python3 N5/scripts/meeting_intelligence_orchestrator.py \
    --transcript_path="$transcript" \
    --meeting_id="$meeting_id" \
    --use-simulation
done
```

---

## 🚨 Troubleshooting

### Problem: Script fails immediately
**Check**: Does `N5/prefs/block_type_registry.json` exist?  
**Check**: Does `N5/prefs/communication/essential-links.json` exist?  
**Fix**: Make sure both required files are present

### Problem: Output has placeholders
**In simulation mode**: This is expected - simulation uses test data  
**In production mode**: Check logs for LLM extraction errors

### Problem: Missing blocks
**Check**: Does your transcript contain relevant keywords?
- For founder profile: "startup", "founder", "company"
- For product ideas: "product", "feature", "idea"
- For warm intros: "introduce", "send me a blurb", "connect you with"

### Problem: Granola detection wrong
**Check**: Are you using `Me:` and `Them:` speaker labels?  
**Note**: Case-sensitive - must be exactly `Me:` and `Them:`

---

## 📞 Need Help?

1. Check `file 'N5/scripts/README_ORCHESTRATOR.md'` for full documentation
2. Review `file 'N5/scripts/meeting_intelligence_orchestrator_CHANGELOG.md'` for recent changes
3. Run with `--use-simulation` to test without real LLM calls
4. Check logs in `N5/logs/orchestrator_*.log`

---

**Ready to start? Run the Step 1 command above! 🎉**