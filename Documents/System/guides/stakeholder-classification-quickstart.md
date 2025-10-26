# Stakeholder Classification - Quick Start Guide

**Last Updated:** 2025-10-10

---

## 🎯 What This Does

Automatically classifies meetings as **internal** (team-only) or **external** (includes stakeholders) and generates appropriate analysis blocks for each type.

**Architecture:** Python scripts prepare metadata → Zo processes transcripts directly using native LLM capabilities

---

## 🔄 How It Works

### Automatic Classification

The system looks at participant emails:

**Internal Meeting:** ALL participants have `@mycareerspan.com` or `@theapply.ai` emails
**External Meeting:** ANY participant has a different email domain

### What You Get

**Internal Meetings** get:
- Action items (internal context)
- Decisions (strategic/tactical/process)
- Key insights (multi-category)
- **Debate points** (tensions & trade-offs)
- **Internal memo** format
- Executive dashboard (REVIEW_FIRST)
- Full transcript

**External Meetings** get:
- Action items (relationship context)
- Decisions (agreements)
- Key insights (opportunity/risk)
- **Stakeholder profile** (comprehensive)
- **Follow-up email draft**
- Executive dashboard (REVIEW_FIRST)
- Full transcript

---

## 🚀 Usage

### Command-Based Processing (Recommended)

```bash
# Process pending meeting requests
command 'meeting-process'
```

This command processes all pending requests in `N5/inbox/meeting_requests/` using Zo's native LLM capabilities.

### Manual Request Creation

```bash
# Create a processing request manually
python3 N5/scripts/meeting_auto_processor.py \
  --transcript-path path/to/transcript.txt \
  --meeting-id "2025-10-10_client-discovery"
  
# Then process with Zo
command 'meeting-process'
```

**Note:** The Python script only classifies stakeholders and creates a request JSON. Zo processes the transcript directly when the command is invoked.

### Automatic Processing

When transcripts arrive in Google Drive, the system automatically:
1. Detects the new transcript
2. Extracts participant emails
3. Classifies the meeting (Python script)
4. Creates processing request JSON
5. Scheduled task invokes Zo to process requests
6. Zo extracts content and fills templates natively
7. Creates folder with smart naming:
   - Internal: `2025-10-10_internal/`
   - External: `2025-10-10_{stakeholder-name}/`

---

## 🔍 Testing Classification

```bash
# Test the classifier directly
python3 N5/scripts/utils/stakeholder_classifier.py \
  vrijen@mycareerspan.com \
  logan@theapply.ai

# Output:
# 📧 Analyzing 2 email(s)...
# ✅ INTERNAL: vrijen@mycareerspan.com
# ✅ INTERNAL: logan@theapply.ai
# 🏷️  Meeting Type: INTERNAL

python3 N5/scripts/utils/stakeholder_classifier.py \
  vrijen@mycareerspan.com \
  sarah@clientcompany.com

# Output:
# 📧 Analyzing 2 email(s)...
# ✅ INTERNAL: vrijen@mycareerspan.com
# 🌐 EXTERNAL: sarah@clientcompany.com
# 🏷️  Meeting Type: EXTERNAL
```

---

## 📁 File Locations

### Scripts
- **Classifier:** `N5/scripts/utils/stakeholder_classifier.py` (pure Python, no LLM)
- **Auto Processor:** `N5/scripts/meeting_auto_processor.py` (data prep only)
- **Template Manager:** `N5/scripts/meeting_intelligence_orchestrator.py` (loads templates, no LLM calls)

### Commands
- **Meeting Processor:** `N5/commands/meeting-process.md` (Zo-executed command)

### Templates
- **Internal:** `N5/prefs/block_templates/internal/`
  - action-items.template.md
  - decisions.template.md
  - key-insights.template.md
  - debate-points.template.md ⭐
  - memo.template.md ⭐
  - REVIEW_FIRST.template.md
  
- **External:** `N5/prefs/block_templates/external/`
  - action-items.template.md
  - decisions.template.md
  - key-insights.template.md
  - stakeholder-profile.template.md ⭐
  - follow-up-email.template.md ⭐
  - REVIEW_FIRST.template.md

### Logs
- **Template manager logs:** `N5/logs/template_manager_{meeting-id}.log`
- **Processing log:** `N5/logs/processed_meetings.jsonl`
- **Command execution:** Check conversation history

---

## 🛠️ Troubleshooting

### Meeting misclassified?

Check the processing request JSON:
```bash
cat N5/inbox/meeting_requests/{meeting-id}_request.json
```

Verify stakeholder classification field. If wrong, the Python classifier needs adjustment.

### Wrong templates loaded?

The classifier defaults to **external** (safer default). Check template manager logs:
```bash
tail -30 N5/logs/template_manager_{meeting-id}.log
```

### Content extraction not working?

Zo performs all LLM extraction directly. Check:
1. Processing request exists in `N5/inbox/meeting_requests/`
2. Transcript file path in request is valid
3. Command was invoked (`command 'meeting-process'`)
4. Check conversation history for Zo's processing output

---

## 💡 Pro Tips

### 1. Use Descriptive Meeting IDs
Good: `2025-10-10_client-discovery-acme`
Bad: `meeting_123`

### 2. Check Classification Early
Before processing, test the classifier:
```bash
python3 N5/scripts/utils/stakeholder_classifier.py email1@domain.com email2@domain.com
```

### 3. Understand the Architecture
- **Python scripts:** Classify stakeholders, prepare metadata, create requests
- **Zo (command-based):** Extract content, fill templates, generate blocks
- **No subprocess calls:** Zo processes directly when invoked

### 4. Monitor Processing Requests
```bash
# Check pending requests
ls -lh N5/inbox/meeting_requests/

# Check processed requests
ls -lh N5/inbox/meeting_requests/processed/
```

---

## 📊 Quick Reference

| Scenario | Classification | Folder Name | Special Blocks |
|----------|---------------|-------------|----------------|
| Vrijen + Logan | Internal | `2025-10-10_internal/` | debate-points, memo |
| Vrijen + Client | External | `2025-10-10_{client-name}/` | stakeholder-profile, follow-up-email |
| Vrijen + Logan + Client | External | `2025-10-10_{client-name}/` | stakeholder-profile, follow-up-email |

---

## 🔗 Related Documentation

- `file 'N5/docs/ARCHITECTURE_CORRECTION.md'` - Architecture overview and corrections
- `file 'N5/commands/meeting-process.md'` - Command documentation
- `file 'N5/docs/internal-external-stakeholder-implementation.md'` - Full implementation spec

---

**Questions?** Check the logs, processing requests, or review the architecture documentation above.
