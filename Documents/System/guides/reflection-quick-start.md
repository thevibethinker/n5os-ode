# Reflection System - Quick Start Guide

**Date:** 2025-10-20  
**Status:** Ready for testing

---

## Testing Your Reflection Email

### Once Your Email Arrives

When your email with subject "n5 reflection ingestion" arrives at va@zo.computer, invoke the reflection ingestion system:

```bash
# Run reflection ingestion (manual, one-time)
python3 /home/workspace/N5/scripts/reflection_ingest.py --source email
```

This will:
1. Search for `[Reflect]` or reflection-related subjects in the last 10 minutes
2. Download any audio attachments  
3. Extract email body text as processing context
4. Transcribe audio (via Zo's transcription tool)
5. Stage for approval in registry

---

## What Happens Next

After running the ingestion:

1. **Check staging**: `ls /home/workspace/N5/records/reflections/incoming/`
2. **Review registry**: `cat /home/workspace/N5/records/reflections/registry/registry.json`
3. **Approve outputs**: Review generated proposals in `N5/records/reflections/outputs/`

---

## Email Format Guidelines

For future reflections, use this format:

**Subject**: `[Reflect] Your topic here`  
**Body**: Processing instructions (optional)  
- "Focus on monetization strategies"  
- "Extract product insights"  
- "Highlight competitive positioning"

**Attachment**: Audio file (mp3, m4a, wav, opus)

---

## Auto-Trigger Option

If you want emails to process automatically without manual invocation:

```bash
# Enable auto-processing every 10 minutes
python3 /home/workspace/N5/scripts/reflection_auto_ingest.py --enable --interval 10
```

Then create a scheduled task:
```bash
# This creates a Zo scheduled task
command 'N5/commands/reflection-auto-ingest.md'
```

**However**, per your preference, I'm keeping this MANUAL for now.

---

## Troubleshooting

### Email Not Found?
- Gmail can take 1-10 minutes to deliver
- Check subject includes `[Reflect]` or relevant keywords
- Verify sent to: va@zo.computer

### Transcription Missing?
- Zo will handle transcription via its tool
- If missing, I can transcribe manually using `transcribe_audio` tool

### No Audio Attachment?
- System will still process text from email body
- Audio is optional but recommended for voice reflections

---

## Example Invocation

```bash
# After your email arrives, run:
python3 /home/workspace/N5/scripts/reflection_ingest.py --source email

# Or use the command wrapper:
command 'N5/commands/reflection-ingest.md' --source email
```

---

**Ready when your email arrives!** 📧

