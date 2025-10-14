# Phase 5: Legacy Profile Conversion

**Status:** PENDING  
**Created:** 2025-10-14 00:50 ET  
**Depends On:** Phase 4 (Complete)

---

## Objective

Convert 49 legacy CRM profiles to standardized YAML frontmatter format, enabling complete index coverage.

---

## Current State

### Indexed (8 profiles with frontmatter)
- elaine-pak.md
- fei-ma-nira.md
- heather-wixson.md
- hei-yue-pang-yuu.md
- jake-fohe.md
- kat-de-haen-fourth-effect.md
- michael-maher-cornell.md
- yousef-abdel.md

### Legacy Format (49 profiles requiring conversion)
alex-caveny.md, alfred-sogja.md, allie-cialeo.md, amy-quan.md, asher-king-abramson.md, ashraf-heleka.md, ayush-jain.md, bram-adams.md, brian-aquart.md, caleb-thornton.md, carly-ackerman.md, charles-jolley.md, daniel-williams.md, darius-goldman.md, david-speigel.md, emily-nelson-de-velasco.md, external-unknown.md, giovanna-ventola.md, graham-smith.md, hmya.md, ilse-funkhouser.md, jacob-bank.md, jake-weissbourd.md, jason-cheung.md, jeff-h-sipe.md, kamina-singh.md, krista-tan.md, laura-close.md, logan-currie.md, malvika-jethmalani.md, meera-krishnan.md, michael-berlingo.md, mihir-makwana.md, nicole-holubar-walker.md, oeh.md, pam-kavalam.md, rajesh-nerlikar.md, ray-batra.md, rochel-polter.md, sam-bourton.md, shivam-desai.md, shivani-mathur.md, shujaat-ahmad.md, sofia-wernick.md, spv.md, tim-he.md, ulrik-soderstrom.md, usha-srinivasan.md, whitney-jones.md

---

## Scope

### In-Scope
1. **Parse legacy format** — Extract metadata from markdown structure
2. **Generate frontmatter** — Create YAML header with required fields
3. **Preserve content** — Maintain all existing notes/context
4. **Validate conversion** — Ensure no data loss
5. **Rebuild index** — Re-run Phase 4 for complete 57-profile index

### Out-of-Scope
- Email enrichment (separate task)
- LinkedIn URL discovery (separate task)
- Interaction history reconstruction (future enhancement)

---

## Success Criteria

- [ ] All 49 legacy profiles converted to frontmatter format
- [ ] Zero data loss verified via diff checks
- [ ] CRM index contains 57 entries (100% coverage)
- [ ] All converted profiles pass schema validation
- [ ] Conversion script includes dry-run mode
- [ ] Backup created before conversion

---

## Technical Approach

### Conversion Strategy
```python
# 1. Parse legacy format
- Extract name from H1 heading
- Extract role, email, LinkedIn from bullet list
- Infer lead_type from context (default: LD-NET)
- Set status = "active" (default)
- Use file mtime as last_updated

# 2. Generate frontmatter
- Use _template.md as reference
- Fill known fields, leave unknowns as empty strings
- Set interaction_count = 0 (unknown)
- Set first_contact = last_updated (best guess)

# 3. Preserve content
- Keep all existing sections intact
- Append frontmatter to top
- Maintain markdown formatting
```

### Safety Measures
- Backup to `Knowledge/crm/profiles.backup-YYYYMMDD/`
- Dry-run preview for manual review
- Line-by-line diff for validation
- Rollback script in case of issues

---

## Deliverables

1. `phase5_convert_legacy.py` — Conversion script with dry-run
2. `phase5_results.json` — Execution log
3. `PHASE5_COMPLETE.md` — Final report
4. Updated `Knowledge/crm/index.jsonl` (57 entries)

---

## Estimated Effort

- Script development: 15-20 min
- Dry-run review: 5 min
- Execution + validation: 5 min
- **Total: ~30 minutes**

---

## Dependencies

**Blocks:**
- Complete CRM index (currently 14% coverage)
- CRM search functionality
- Profile recommendation engine

**Blocked By:**
- None (Phase 4 complete)

---

## Notes

- Low-risk operation (non-destructive with backups)
- Enables immediate value from CRM system
- Can be run incrementally if needed (batch processing)
- Consider running during off-hours for large dataset

---

**Prepared by:** Vibe Builder  
**Thread:** con_v3Qd4fOyVUKA3b4H
