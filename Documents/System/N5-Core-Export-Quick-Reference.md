# N5 Core Export - Quick Reference

**Purpose**: Sync your N5 changes to public n5os-core repo for others to use

---

## One-Line Commands

```bash
# Preview what will be exported
python3 N5/scripts/n5_export_core.py --dry-run

# Export (review before pushing)
python3 N5/scripts/n5_export_core.py

# Export and auto-push to GitHub
python3 N5/scripts/n5_export_core.py --push
```

---

## What Gets Exported

✅ **Included**:
- 4 core scripts (session_state_manager, n5_index_rebuild, n5_safety, n5_git_check)
- 26 core prefs (system + operations, NOT personal/communication)
- 20 schemas (all JSON schemas)
- 28 architectural knowledge files (principles + planning prompt)
- 1 docs file (Lists/POLICY.md)

❌ **Excluded**:
- Personal prefs (communication/, personal/, formatting/)
- Temporary files
- Backups
- User-specific data

---

## Generification (Automatic)

Your personal data is automatically replaced with placeholders:

| Your Data | Becomes |
|-----------|---------|
| `/home/workspace` | `{WORKSPACE}` |
| `/home/workspace/N5` | `{N5_ROOT}` |
| `/home/workspace/N5/data` | `{N5_DATA}` |
| `V` / `va` | `{USER}` / `{USER_HANDLE}` |
| `Vrijen` | `{USER_NAME}` |
| `Vrijen Attawar` | `{USER_FULL_NAME}` |
| `Careerspan` | `{COMPANY}` |
| `va.zo.computer` | `{USER_HANDLE}.zo.computer` |

---

## Workflow

```
1. You update N5 scripts/prefs/knowledge
   ↓
2. Run: python3 N5/scripts/n5_export_core.py --dry-run
   ↓
3. Review changes
   ↓
4. Run: python3 N5/scripts/n5_export_core.py --push
   ↓
5. GitHub updated automatically
   ↓
6. Others pull and bootstrap
```

---

## Files

- **Workflow doc**: `N5/workflows/export-to-n5os-core.md`
- **Configuration**: `N5/config/export_core_manifest.yaml`
- **Script**: `N5/scripts/n5_export_core.py`
- **Destination**: `/home/workspace/n5os-core/`
- **GitHub**: https://github.com/vrijenattawar/n5os-core

---

## Customizing Export

Edit `N5/config/export_core_manifest.yaml` to:
- Add/remove components
- Change replacement rules
- Update exclude patterns
- Modify destination path

---

## Safety Checks

✅ Before export:
- Verifies n5os-core repo exists
- Checks for uncommitted changes
- Shows preview in dry-run mode
- Validates destination is git repo

✅ During export:
- Applies generification transforms
- Excludes personal patterns
- Preserves file permissions
- Logs all operations

✅ After export:
- Commits changes to git
- Optionally pushes to GitHub
- Updates manifest timestamp
- Logs to export history

---

## Troubleshooting

**Problem**: "Destination not found"
- **Fix**: Ensure `/home/workspace/n5os-core/` exists and is a git repo

**Problem**: "Uncommitted changes"
- **Fix**: Commit or stash changes in n5os-core first

**Problem**: "Export includes personal data"
- **Fix**: Add patterns to `exclude_patterns` in manifest

**Problem**: "Missing files in export"
- **Fix**: Add file patterns to `components` section in manifest

---

## Next Steps After Export

1. **Verify on GitHub**: Check https://github.com/vrijenattawar/n5os-core
2. **Test bootstrap**: Try fresh install on test Zo instance
3. **Update CHANGELOG**: Document what changed
4. **Tag release**: If major changes, create git tag
5. **Notify users**: If breaking changes, communicate

---

**Last Updated**: 2025-10-27  
**Version**: 1.0.0
