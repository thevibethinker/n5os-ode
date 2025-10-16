# Delta Closure - Quick Reference

**Version:** 2.0.0 | **Date:** 2025-10-16

---

## What Is It?

System that tracks conversation closures to avoid re-archiving duplicate content when you close a conversation multiple times.

---

## Quick Commands

### Check if this is a repeat closure:
```bash
python3 /home/workspace/N5/scripts/closure_tracker.py delta-info \
  --workspace /home/.z/workspaces/con_XXX
```

**Output:**
- `"is_delta": false` → First closure (process everything)
- `"is_delta": true` → Repeat closure (delta only)

### Record a closure:
```bash
python3 /home/workspace/N5/scripts/closure_tracker.py record \
  --workspace /home/.z/workspaces/con_XXX \
  --timestamp "2025-10-16T14:30:00Z" \
  --event-range "1-45" \
  --archive-path "Documents/Archive/2025-10-16-Topic/closure-1" \
  --summary "Initial implementation"
```

### Check closure history:
```bash
python3 /home/workspace/N5/scripts/closure_tracker.py status \
  --workspace /home/.z/workspaces/con_XXX
```

### Generate archive index:
```bash
python3 /home/workspace/N5/scripts/closure_tracker.py generate-index \
  --workspace /home/.z/workspaces/con_XXX \
  --convo-id "con_XXX" \
  --title "Feature Implementation" \
  --output "Documents/Archive/2025-10-16-Topic/INDEX.md"
```

---

## Archive Structure

### First Closure
```
Documents/Archive/2025-10-16-Topic/
├── README.md
└── [artifacts]
```

### Multiple Closures
```
Documents/Archive/2025-10-16-Topic/
├── INDEX.md              # Overview of all closures
├── closure-1/
│   ├── README.md        # Self-contained
│   └── [artifacts]
├── closure-2/
│   ├── README.md        # Self-contained
│   └── [delta artifacts]
└── closure-3/
    ├── README.md        # Self-contained
    └── [delta artifacts]
```

---

## Phase 0 Checklist

When closing a conversation:

1. **Check delta status:**
   ```bash
   closure_tracker.py delta-info --workspace .
   ```

2. **If first closure (`is_delta: false`):**
   - Process entire conversation (all phases)
   - Create archive at `Documents/Archive/YYYY-MM-DD-Topic/`
   - Record closure after archiving

3. **If repeat closure (`is_delta: true`):**
   - Only process artifacts since last closure
   - Create `closure-N/` subdirectory
   - Update INDEX.md
   - Record this closure

4. **Record the closure:**
   ```bash
   closure_tracker.py record \
     --workspace . \
     --timestamp "<last_user_msg_time>" \
     --event-range "X-Y" \
     --archive-path "..." \
     --summary "..."
   ```

5. **Generate/update INDEX.md:**
   ```bash
   closure_tracker.py generate-index \
     --workspace . \
     --convo-id "con_XXX" \
     --title "Topic" \
     --output "Documents/Archive/.../INDEX.md"
   ```

---

## Key Concepts

**Delta:** Only the work since last closure (not entire conversation)

**Closure Number:** Sequential counter (1, 2, 3...) tracked in SESSION_STATE.md

**Timestamp Source:** Last user message before closure command

**Self-Contained:** Each closure-N/ has own README with full context

**INDEX.md:** Central manifest listing all closures

---

## Data Storage

**SESSION_STATE.md:**
```yaml
closure:
  count: 2
  last_timestamp: "2025-10-16T14:30:00Z"
  last_event_id: 45
```

**CLOSURE_MANIFEST.jsonl:**
```json
{"closure_num": 1, "timestamp": "...", "event_range": "1-45", ...}
{"closure_num": 2, "timestamp": "...", "event_range": "46-75", ...}
```

---

## Common Scenarios

**Scenario 1: First closure**
- Run all phases normally
- Create archive directory
- Record closure
- Done

**Scenario 2: Second closure**
- Delta detected automatically
- Only new files since last closure
- Create `closure-2/` subdirectory
- Update INDEX.md
- Record closure

**Scenario 3: Check what's been closed**
```bash
closure_tracker.py status --workspace .
# Shows: count, last timestamp, all closures
```

---

## Workflow Reference

See full documentation: `file 'N5/prefs/operations/conversation-end.md'`

**Phase 0:** Delta Detection (NEW)  
**Phase 1:** Identify Artifacts (filter by mtime if delta)  
**Phase 2:** Archive (closure-N/ if delta)  
**Phase 3:** System Docs (only new/updated)  
**Phase 4:** Timeline (mark as delta)  
**Phase 5:** Verify (delta artifacts only)

---

## Troubleshooting

**Problem:** "No SESSION_STATE.md found"  
**Solution:** Initialize session state first

**Problem:** "CLOSURE_MANIFEST.jsonl corrupt"  
**Solution:** Valid JSONL = one JSON object per line; check syntax

**Problem:** "Wrong closure number"  
**Solution:** Check SESSION_STATE.md closure.count field

**Problem:** "Can't find previous closure"  
**Solution:** status command shows all recorded closures

---

## Integration

**Automatic when using:**
- `/Close Conversation` command
- `file 'N5/prefs/operations/conversation-end.md'` workflow

**Manual usage:**
- Use closure_tracker.py commands directly
- Follows same data format
- Compatible with automated workflow

---

*For detailed implementation: see `file '/home/.z/workspaces/con_5OSlfiRmsK7QlGKM/DELTA_CLOSURE_IMPLEMENTATION.md'`*
