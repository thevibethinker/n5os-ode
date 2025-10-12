# Internal/External Meeting System - Quick Reference

## 🔍 How to Classify

```python
from N5.scripts.utils.stakeholder_classifier import classify_meeting

meeting_type = classify_meeting("vrijen@mycareerspan.com, alex@gmail.com")
# Returns: "external" (because alex@gmail.com is external)

meeting_type = classify_meeting("vrijen@mycareerspan.com, sofia@mycareerspan.com")
# Returns: "internal" (all participants internal)
```

## 📊 Block Differences

| Block | Internal | External |
|-------|----------|----------|
| action-items.md | ✅ | ✅ |
| decisions.md | ✅ | ✅ |
| key-insights.md | ✅ | ✅ |
| debate-points.md | ✅ | ❌ |
| memo.md | ✅ | ❌ |
| stakeholder-profile.md | ❌ | ✅ |
| follow-up-email.md | ❌ | ✅ |
| REVIEW_FIRST.md | ✅ | ✅ |
| transcript.txt | ✅ | ✅ |
| **Total** | **7 blocks** | **7 blocks** |

## 🚀 Generate Blocks

### Internal Meeting
```bash
python3 /home/workspace/N5/scripts/meeting_core_generator.py \
  --transcript /path/to/transcript.txt \
  --output-dir /home/workspace/Careerspan/Meetings/2025-10-10_internal \
  --date 2025-10-10 \
  --participants "vrijen@mycareerspan.com,sofia@mycareerspan.com"
```

**Output:**
- `2025-10-10_internal/action-items.md`
- `2025-10-10_internal/decisions.md`
- `2025-10-10_internal/key-insights.md`
- `2025-10-10_internal/debate-points.md` ✨
- `2025-10-10_internal/memo.md` ✨
- `2025-10-10_internal/REVIEW_FIRST.md`
- `2025-10-10_internal/transcript.txt`
- `2025-10-10_internal/_metadata.json`

### External Meeting
```bash
python3 /home/workspace/N5/scripts/meeting_core_generator.py \
  --transcript /path/to/transcript.txt \
  --output-dir /home/workspace/Careerspan/Meetings/2025-10-10_alex-smith \
  --date 2025-10-10 \
  --participants "vrijen@mycareerspan.com,alex@techcorp.com" \
  --stakeholder-name "Alex Smith" \
  --stakeholder-email "alex@techcorp.com"
```

**Output:**
- `2025-10-10_alex-smith/action-items.md`
- `2025-10-10_alex-smith/decisions.md`
- `2025-10-10_alex-smith/key-insights.md`
- `2025-10-10_alex-smith/stakeholder-profile.md` ✨
- `2025-10-10_alex-smith/follow-up-email.md` ✨
- `2025-10-10_alex-smith/REVIEW_FIRST.md`
- `2025-10-10_alex-smith/transcript.txt`
- `2025-10-10_alex-smith/_metadata.json`

## 📝 Metadata Example

```json
{
  "meeting_id": "abc123",
  "date": "2025-10-10",
  "stakeholder_classification": "external",
  "participants": [
    {
      "name": "Vrijen",
      "email": "vrijen@mycareerspan.com",
      "classification": "internal"
    },
    {
      "name": "Alex",
      "email": "alex@techcorp.com",
      "classification": "external"
    }
  ],
  "processing": {
    "generated_at": "2025-10-10T19:00:00Z",
    "generator": "meeting_core_generator.py",
    "version": "1.0"
  },
  "blocks_generated": [
    "action-items.md",
    "decisions.md",
    "key-insights.md",
    "stakeholder-profile.md",
    "follow-up-email.md",
    "REVIEW_FIRST.md",
    "transcript.txt"
  ]
}
```

## 🧪 Quick Test

```bash
# Test classifier
python3 /home/workspace/N5/scripts/utils/stakeholder_classifier.py \
  vrijen@mycareerspan.com alex@gmail.com

# Expected: "EXTERNAL" (mixed participants)
```

## 🔧 Files Modified/Created

**Created:**
- `N5/scripts/utils/stakeholder_classifier.py`
- `N5/scripts/meeting_core_generator.py`
- `N5/prefs/block_templates/` (entire directory)

**Modified:**
- `N5/schemas/meeting-metadata.schema.json`

**To Update:**
- `N5/scripts/meeting_auto_processor.py` (integrate classifier)
- Scheduled task instruction (after testing)
