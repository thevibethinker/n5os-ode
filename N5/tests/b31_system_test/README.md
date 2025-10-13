# B31 System Test Sandbox

**Purpose:** Safe testing environment for B31 aggregation system  
**Status:** Active test  
**Created:** 2025-10-13

---

## What's Here

### Test Meetings (4 external conversations)
1. **2025-08-28_external-charles-jolley_170815** - Charles Jolley
2. **2025-09-09_external-and-krista-tan** - Krista Tan
3. **2025-09-08_external-alex-wisdom-partners-coaching** - Alex (Wisdom Partners)
4. **2025-08-26_external-asher-king-abramson** - Asher King Abramson

### Test Script
- `aggregate_insights_sandbox.py` - Sandbox version of aggregation script
- Only operates within this directory
- Safe to experiment

---

## Usage

```bash
# List available meetings
python3 aggregate_insights_sandbox.py --list

# Process specific meeting
python3 aggregate_insights_sandbox.py --meeting-id 2025-08-28_external-charles-jolley_170815

# Process all meetings (incremental test)
python3 aggregate_insights_sandbox.py --all
```

---

## Test Objectives

1. ✅ Extract insights from old B31 format
2. ⏳ Test incremental aggregation
3. ⏳ Validate pattern detection
4. ⏳ Check signal strength promotion
5. ⏳ Verify credibility weighting

---

## Cleanup

```bash
# Delete entire sandbox when done
rm -rf /home/workspace/N5/tests/b31_system_test
```

---

**Safe to delete after testing complete!**
