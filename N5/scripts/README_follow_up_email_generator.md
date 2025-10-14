# Follow-Up Email Generator — Usage Guide

**Script:** `file 'N5/scripts/n5_follow_up_email_generator.py'`  
**Version:** 1.0.0  
**Spec:** v11.0.1

---

## Quick Start

### Basic Usage
```bash
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder /path/to/meeting
```

### Common Examples

**1. Generate email for recent meeting:**
```bash
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit
```

**2. Preview before generating (dry-run):**
```bash
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit \
  --dry-run
```

**3. Custom output directory:**
```bash
python3 N5/scripts/n5_follow_up_email_generator.py \
  --meeting-folder N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit \
  --output-dir ~/Desktop/emails
```

---

## What It Does

### 13-Step Pipeline
1. Loads meeting transcript and stakeholder profile
2. Builds link map from essential-links.json
3. Infers dial settings (formality, warmth, CTA rigour)
4. Generates initial draft
5. Reviews against voice compliance
6. Extracts resonant conversation details
7. Extracts stakeholder's own words
8. Builds natural phrase pool
9. Loads V's voice configuration
10. Revises draft based on feedback
11. Applies compression (target: 300 words)
12. Verifies all links (P16: no fabrication)
13. Validates readability (Flesch-Kincaid ≤ 10)

---

## Outputs

### Files Generated (in DELIVERABLES/)
1. **follow_up_email_draft.md**  
   Full markdown version with subject line
   
2. **follow_up_email_copy_paste.txt**  
   Plain text version for email clients (no markdown)
   
3. **follow_up_email_artifacts.json**  
   All pipeline artifacts: dial settings, link map, resonance pool, etc.
   
4. **follow_up_email_summary.md**  
   Execution summary with quality metrics

---

## Requirements

### Meeting Folder Must Contain:
- **Transcript:** `*transcript*.txt` or `*transcript*.md`
- **Optional:** `stakeholder_profile.md` (for better dial calibration)

### System Files Required:
- `N5/prefs/communication/voice.md` (v3.0.0)
- `N5/prefs/communication/essential-links.json` (v1.7.0)

---

## CLI Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--meeting-folder` | ✅ Yes | N/A | Path to meeting folder (absolute or relative) |
| `--output-dir` | ❌ No | `{meeting}/DELIVERABLES/` | Custom output directory |
| `--dry-run` | ❌ No | `False` | Preview only, don't write files |
| `--force` | ❌ No | `False` | Overwrite existing outputs |

---

## Success Indicators

### ✅ Pipeline Complete
```
======================================================================
✅ PIPELINE COMPLETE - ALL VALIDATIONS PASSED
======================================================================

📁 Outputs saved to: /path/to/DELIVERABLES
```

### ⚠️ Warnings
```
======================================================================
⚠️ PIPELINE COMPLETE - VALIDATION WARNINGS
======================================================================
```

**Check:**
- Link verification failures (fabricated URLs)
- Readability above FK 10
- Voice compliance issues

---

## Example Output

### Draft Email Preview
```markdown
**Subject:** Following Up — Hamoon x Careerspan [partnership pathways]

Hi Hamoon,

Great connecting last week. I appreciated your thoughtful questions about 
how we could potentially work together.

As promised, here are two concrete use cases we discussed:

**1. Embedded Vibe Check Integration**  
[Specific details from conversation...]

**2. Curated Talent Pool Access**  
[Specific details from conversation...]

Both approaches would [benefit]. You can see more at 
[mycareerspan.com](https://www.mycareerspan.com), and happy to 
[grab 30 minutes](https://calendly.com/v-at-careerspan/30min) 
to discuss further if either resonates.

Looking forward to your thoughts.

Best,  
Vrijen
```

---

## Quality Metrics

### Typical Output
- **Word Count:** 200-300 words
- **Flesch-Kincaid:** 6-9 (accessible technical)
- **Links:** 1-3 (all from essential-links.json)
- **Execution Time:** <1 second

### Dial Settings Example
```
Relationship Depth: cold
Formality: 6/10
Warmth: 5/10
CTA Rigour: moderate
```

---

## Troubleshooting

### Error: "Meeting folder not found"
**Fix:** Use absolute path or ensure folder exists
```bash
# Wrong
--meeting-folder hamoon-ekhtiari-futurefit

# Right
--meeting-folder /home/workspace/N5/records/meetings/2025-10-10_hamoon-ekhtiari-futurefit
```

### Error: "No transcript found"
**Fix:** Ensure transcript file exists with pattern `*transcript*.(txt|md)`

### Warning: "Fabricated links found"
**Fix:** Check essential-links.json for missing URLs. Script will list violations.

### FK Grade > 10
**Fix:** Review draft for complex sentences. Script auto-compresses but may need manual editing.

---

## Integration Points (Phase 2)

### Future: Meeting Approval Workflow
```bash
N5: meeting-approve 2025-10-10_hamoon-ekhtiari-futurefit --actions send_followup
```

### Future: Deliverables Generator
```bash
N5: generate-deliverables 2025-10-10_hamoon-ekhtiari-futurefit --types follow_up_email
```

### Future: Batch Processing
```bash
N5: follow-up-email-generator --batch --pending-meetings
```

---

## Version History

### v1.0.0 (2025-10-13)
- ✅ Full 13-step pipeline implementation
- ✅ P16 link verification enforcement
- ✅ CLI interface with dry-run support
- ✅ All 4 output files generated
- ✅ Readability validation (FK ≤ 10)

---

## Support

**Issues:** Report via Zo Discord or "Report an issue" button  
**Documentation:** `file 'N5/commands/follow-up-email-generator.md'` (v11.0.1)  
**Implementation:** `file 'PHASE_1_COMPLETE.md'`

---

*Last Updated: 2025-10-13 18:40 ET | v1.0.0*
