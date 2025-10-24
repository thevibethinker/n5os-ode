# Artifact Symlinking Policy

**Version:** 1.0  
**Principle:** P23 (Artifact Provenance via Symlinks)  
**Related:** `file 'N5/commands/conversation-end.md'` Phase 0.5

---

## Quick Reference

**ALWAYS symlink, NEVER copy** deliverables to AAR artifacts folder.

```bash
# Template
cd /home/workspace/N5/logs/threads/{date}_{title}_{id}/artifacts/
ln -sf /absolute/path/to/deliverable ./descriptive-name.ext
```

---

## What to Symlink

✅ **YES - Symlink these:**
- Scripts, commands, modules created
- Documents, reports, drafts
- Social posts, content pieces
- Knowledge files (bio, positioning)
- Workflow docs (debug, design, next-steps)
- Modified N5 infrastructure

❌ **NO - Don't symlink these:**
- Temp files, scratch work
- Conversation state (already in AAR)
- Downloaded external files (unless transformed)
- System logs

---

## Naming Convention

| Original Location | Symlink Name Pattern |
|------------------|---------------------|
| `Documents/Drafts/X.md` | `artifact-name.md` |
| `Documents/Social/LinkedIn/*.md` | `social_angle-description.md` |
| `N5/commands/*.md` | `command_name.md` |
| `N5/scripts/*.py` | `script_name.py` |
| `N5/scripts/modules/*.py` | `module_name.py` |
| `Knowledge/**/*.md` | `category_name.md` |
| `N5/digests/*.md` | `digest_name.md` |
| `Documents/WORKFLOW_*.md` | `workflow_purpose.md` |

**Key:** Use descriptive names that indicate purpose, not just filename.

---

## Example (Real)

**Conversation:** 2025-10-21-1210_✅-System-Work_kkgp

```bash
cd /home/workspace/N5/logs/threads/2025-10-21-1210_✅-System-Work_kkgp/artifacts/

# Demo materials
ln -sf /home/workspace/Documents/Drafts/zo_demo_script.md ./demo_script.md
ln -sf /home/workspace/N5/digests/COMPARISON-baseline-vs-enhanced.md ./comparison_materials.md

# Social content (3 angles)
ln -sf /home/workspace/Documents/Social/LinkedIn/2025-10-20_zo-gtm_ANGLE1-founder-pain.md ./social_angle1_founder-pain.md
ln -sf /home/workspace/Documents/Social/LinkedIn/2025-10-20_zo-gtm_ANGLE2-technical.md ./social_angle2_technical.md
ln -sf /home/workspace/Documents/Social/LinkedIn/2025-10-20_zo-gtm_ANGLE3-build-story.md ./social_angle3_build-story.md

# Infrastructure
ln -sf /home/workspace/Knowledge/personal-brand/bio.md ./bio.md
ln -sf /home/workspace/N5/commands/social-post-generate-multi-angle.md ./command_social-multi-angle.md
ln -sf /home/workspace/N5/scripts/modules/knowledge_scanner.py ./script_knowledge_scanner.py
ln -sf /home/workspace/N5/scripts/modules/angle_analyzer.py ./script_angle_analyzer.py

# Workflow docs
ln -sf /home/workspace/Documents/SOCIAL_POST_WORKFLOW_DEBUG.md ./workflow_debug.md
ln -sf /home/workspace/Documents/NEXT_STEPS_SOCIAL_WORKFLOW.md ./workflow_next_steps.md
```

Result: 12 symlinks, 0 copies, complete provenance.

---

## Verification Commands

```bash
# Check artifacts are symlinked (not copied)
ls -lah artifacts/
# Should show: lrwxrwxrwx (symlink indicator)

# Verify no copies
find artifacts/ -type f
# Should only show non-symlink files (SESSION_STATE.md, etc.)

# Check symlink targets exist
for link in artifacts/*; do
  [ -L "$link" ] && echo "$(basename $link): $(readlink -f $link)"
done
```

---

## Benefits

1. **Single source of truth** — No file duplication
2. **Provenance** — AAR shows all conversation outputs
3. **Correct locations** — Files stay in N5 structure
4. **Survives moves** — Absolute paths in symlinks
5. **Easy audit** — One folder = complete picture

---

## Enforcement

- **P5 (Anti-Overwrite):** Never copy files to AAR
- **P23 (Artifact Provenance):** Always symlink deliverables
- **Phase 0.5:** Automated during conversation-end

---

**Last Updated:** 2025-10-21  
**Owner:** V + Vibe Builder
