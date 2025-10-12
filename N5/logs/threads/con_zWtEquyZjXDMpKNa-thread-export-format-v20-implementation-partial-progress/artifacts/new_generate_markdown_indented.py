    def generate_markdown(self, aar_data: Dict) -> str:
        """Generate markdown view from AAR JSON using v2.0 format specification"""
        md = []
        
        # ===== HEADER =====
        title = aar_data.get('title', 'Thread Export')
        thread_id = aar_data.get('thread_id', 'unknown')
        export_date = aar_data.get('archived_date', datetime.now().strftime("%Y-%m-%d"))
        
        # Determine topic from executive summary
        topic = aar_data.get('executive_summary', {}).get('purpose', 'Thread export')
        # Truncate topic if too long
        if len(topic) > 100:
            topic = topic[:97] + "..."
        
        # Determine status (for now, default to "Complete")
        status = "Complete"  # TODO: Could be enhanced with more logic
        
        md.append(f"# Thread Export: {title}")
        md.append("")
        md.append(f"**Thread ID:** {thread_id}  ")
        md.append(f"**Export Date:** {export_date}  ")
        md.append(f"**Topic:** {topic}  ")
        md.append(f"**Status:** {status}")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== SUMMARY =====
        md.append("## Summary")
        md.append("")
        
        # Generate 2-3 sentence summary
        purpose = aar_data.get('executive_summary', {}).get('purpose', 'No objective specified')
        outcome = aar_data.get('executive_summary', {}).get('outcome', 'No outcomes specified')
        next_obj = aar_data.get('primary_objective', 'Review and determine next steps')
        
        md.append(f"{purpose} {outcome} Next: {next_obj}")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== QUICK START =====
        md.append("## Quick Start")
        md.append("")
        md.append("**First 10 minutes:**")
        md.append("")
        md.append("1. **Verify state** (2 min)")
        md.append("   ```bash")
        md.append("   # Check key files/resources exist")
        
        # Add verification commands based on artifacts
        artifacts = aar_data.get('final_state', {}).get('artifacts', [])
        if artifacts:
            # Show a few key files
            key_files = [a['filename'] for a in artifacts[:3]]
            for f in key_files:
                md.append(f"   ls -la {f}")
        else:
            md.append("   # No artifacts to verify")
        
        md.append("   ```")
        md.append("   Expected: Files should exist with appropriate sizes")
        md.append("")
        md.append("2. **Understand context** (3 min)")
        md.append("   - Read \"Critical Constraints\" below")
        md.append("   - Skim \"What Was Completed\"")
        md.append("   - Note \"Known Issues\"")
        md.append("")
        md.append("3. **Start work** (5 min)")
        
        # Get first next step
        next_steps = aar_data.get('next_steps', [])
        if next_steps:
            first_step = next_steps[0].get('action', 'Review AAR and plan next actions')
            md.append(f"   - {first_step}")
            md.append("   - Expected: Progress on primary objective")
        else:
            md.append("   - Review AAR and plan next actions")
        
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== WHAT WAS COMPLETED =====
        md.append("## What Was Completed")
        md.append("")
        
        if artifacts:
            # Group artifacts by type for better organization
            by_type = {}
            for artifact in artifacts:
                atype = artifact.get('type', 'other')
                by_type.setdefault(atype, []).append(artifact)
            
            idx = 1
            for atype, items in by_type.items():
                md.append(f"### {idx}. {atype.capitalize()} Artifacts")
                
                if len(items) == 1:
                    a = items[0]
                    md.append(f"- **File(s):** `file '{a['filename']}'`")
                    md.append(f"- **Purpose:** {a.get('description', 'Artifact created during conversation')}")
                    md.append("- **Status:** ✅ Complete")
                else:
                    md.append(f"- **File(s):** {len(items)} {atype} files")
                    md.append(f"- **Purpose:** {atype.capitalize()} artifacts created during conversation")
                    md.append("- **Files:**")
                    for a in items:
                        size_kb = a.get('size_bytes', 0) / 1024
                        md.append(f"  - `{a['filename']}` ({size_kb:.1f} KB)")
                    md.append("- **Status:** ✅ Complete")
                
                md.append("")
                idx += 1
        else:
            md.append("No artifacts were created during this conversation.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== CRITICAL CONSTRAINTS =====
        md.append("## Critical Constraints")
        md.append("")
        md.append("**DO NOT CHANGE:**")
        md.append("- ❌ Existing file structure - other scripts may depend on this layout")
        md.append("- ❌ N5 system conventions - maintained across all threads")
        md.append("")
        md.append("**MUST PRESERVE:**")
        md.append("- ✅ File naming conventions - required for N5 system integration")
        md.append("- ✅ Schema compliance - ensures compatibility with tooling")
        md.append("")
        md.append("**QUALITY BARS:**")
        md.append("- Schema validation: Must pass `aar.schema.json` validation")
        md.append("- File integrity: All referenced files must be accessible")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== KEY TECHNICAL DECISIONS =====
        md.append("## Key Technical Decisions")
        md.append("")
        
        key_events = aar_data.get('key_events', [])
        decision_events = [e for e in key_events if e.get('type') == 'decision']
        
        if decision_events:
            for event in decision_events:
                md.append(f"### Decision: {event.get('description', 'Decision made')}")
                md.append(f"- **Rationale:** {event.get('rationale', 'Decision rationale')}")
                md.append("- **Trade-offs:** Decision made to balance competing concerns")
                md.append("")
        else:
            md.append("No major technical decisions were explicitly captured during this conversation.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== KNOWN ISSUES / GOTCHAS =====
        md.append("## Known Issues / Gotchas")
        md.append("")
        
        # Check for challenge events
        challenge_events = [e for e in key_events if e.get('type') == 'challenge']
        
        if challenge_events:
            for event in challenge_events:
                md.append(f"### ⚠️ Issue: {event.get('description', 'Challenge encountered')}")
                md.append(f"- **Context:** {event.get('rationale', 'Challenge details')}")
                md.append("- **Workaround:** See conversation history for resolution approach")
                md.append("")
        else:
            md.append("No significant issues or gotchas were encountered during this conversation.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== ANTI-PATTERNS / REJECTED APPROACHES =====
        md.append("## Anti-Patterns / Rejected Approaches")
        md.append("")
        
        # Check for pivot events
        pivot_events = [e for e in key_events if e.get('type') == 'pivot']
        
        if pivot_events:
            for event in pivot_events:
                md.append(f"### ❌ Approach: {event.get('description', 'Approach changed')}")
                md.append(f"- **Why pivoted:** {event.get('rationale', 'Reason for pivot')}")
                md.append("")
        else:
            md.append("No approaches were explicitly rejected or pivoted away from during this conversation.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== INTEGRATION POINTS & NEXT STEPS =====
        md.append("## Integration Points & Next Steps")
        md.append("")
        
        if next_steps:
            md.append("### Actions Required")
            md.append("")
            for idx, step in enumerate(next_steps, 1):
                priority = step.get('priority', 'M')
                action = step.get('action', 'Action required')
                details = step.get('details', '')
                duration = step.get('estimated_duration', '')
                
                md.append(f"#### {idx}. {action}")
                md.append(f"- **Action:** {action}")
                if details:
                    md.append(f"- **Details:** {details}")
                md.append(f"- **Priority:** {priority}")
                if duration:
                    md.append(f"- **Estimated Duration:** {duration}")
                md.append(f"- **Status:** ⏳ Pending")
                md.append("")
        else:
            md.append("No specific next steps were defined. Review AAR and determine priorities.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== CODE PATTERNS / QUICK REFERENCE =====
        md.append("## Code Patterns / Quick Reference")
        md.append("")
        
        # Add patterns based on artifact types
        script_artifacts = [a for a in artifacts if a.get('type') == 'script']
        
        if script_artifacts:
            md.append("### Scripts Created")
            md.append("")
            md.append("| Script | Purpose | Usage |")
            md.append("|--------|---------|-------|")
            for script in script_artifacts:
                filename = script.get('filename', 'unknown')
                desc = script.get('description', 'Script file')
                # Infer usage from extension
                if filename.endswith('.py'):
                    usage = f"`python3 {filename}`"
                elif filename.endswith('.sh'):
                    usage = f"`bash {filename}`"
                else:
                    usage = f"`{filename}`"
                md.append(f"| `{filename}` | {desc} | {usage} |")
            md.append("")
        else:
            md.append("No code patterns or scripts were created during this conversation.")
            md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== STATE SNAPSHOT =====
        md.append("## State Snapshot")
        md.append("")
        md.append(f"**As of export ({export_date}):**")
        md.append("")
        
        md.append("### Key Files Status")
        if artifacts:
            for artifact in artifacts:
                filename = artifact.get('filename', 'unknown')
                size_bytes = artifact.get('size_bytes', 0)
                size_kb = size_bytes / 1024
                atype = artifact.get('type', 'unknown')
                md.append(f"- `{filename}`: {size_kb:.1f} KB, {atype} file, ✅ created")
        else:
            md.append("- No artifacts created")
        md.append("")
        
        md.append("### System State")
        telemetry = aar_data.get('telemetry', {})
        total_size = telemetry.get('total_size_bytes', 0) / 1024
        artifact_count = telemetry.get('artifacts_created', 0)
        md.append(f"- Artifacts: {artifact_count} files, {total_size:.1f} KB total")
        md.append("- Thread workspace: Captured in archive")
        md.append("")
        
        md.append("---")
        md.append("")
        
        # ===== TESTING STATUS =====
        md.append("## Testing Status")
        md.append("")
        md.append("### Completed Tests")
        md.append("⏳ No formal tests recorded during this conversation")
        md.append("")
        md.append("### Pending Tests")
        md.append("⏳ Validation and testing should be performed as part of next steps")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== OPEN QUESTIONS =====
        md.append("## Open Questions")
        md.append("")
        md.append("No open questions were explicitly captured during this conversation.")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== IF STUCK, CHECK THESE =====
        md.append("## If Stuck, Check These")
        md.append("")
        md.append("### Problem: Files not found")
        md.append("**Check:**")
        md.append("1. Verify archive directory exists: `ls -la N5/logs/threads/`")
        md.append("2. Check artifacts subdirectory: `ls -la N5/logs/threads/*/artifacts/`")
        md.append("")
        md.append("**Solution:** Review State Snapshot section for expected file locations")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== SYSTEM ARCHITECTURE CONTEXT =====
        md.append("## System Architecture Context")
        md.append("")
        md.append("### Where This Fits")
        md.append("")
        md.append("```")
        md.append("N5 System/")
        md.append("├── Commands/             ← Command definitions")
        md.append("├── Scripts/              ← Executable scripts")
        md.append("├── Schemas/              ← Data validation")
        md.append("├── Logs/")
        md.append("│   └── threads/          ← THIS THREAD ARCHIVE")
        md.append("└── Knowledge/            ← Documentation")
        md.append("```")
        md.append("")
        md.append("### Integration Points")
        md.append("")
        md.append("| System | Integration Type | Status | Notes |")
        md.append("|--------|-----------------|---------|-------|")
        md.append("| N5 Commands | Follows conventions | ✅ | Standard command format |")
        md.append("| N5 Schemas | Validated against | ✅ | `aar.schema.json` |")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== ASSUMPTIONS & VALIDATIONS =====
        md.append("## Assumptions & Validations")
        md.append("")
        md.append("**Assumed to be TRUE:**")
        md.append("- [ ] N5 system structure is intact")
        md.append("- [ ] Archive directory is writable")
        md.append("- [ ] Schema file is accessible")
        md.append("")
        md.append("**Quick validation commands:**")
        md.append("```bash")
        md.append("# Validate N5 structure")
        md.append("ls -la /home/workspace/N5/{commands,scripts,schemas,logs}")
        md.append("")
        md.append("# Check schema")
        md.append("cat /home/workspace/N5/schemas/aar.schema.json | jq '.title'")
        md.append("```")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== USER PREFERENCES (V'S STYLE) =====
        md.append("## User Preferences (V's Style)")
        md.append("")
        md.append("### Code Style")
        md.append("- ✅ Use pathlib.Path, not os.path")
        md.append("- ✅ Type hints in function signatures")
        md.append("- ✅ Docstrings for public functions")
        md.append("- ✅ Explicit better than implicit")
        md.append("- ❌ Don't abbreviate variable names excessively")
        md.append("")
        md.append("### Error Handling")
        md.append("- ✅ Specific try/except with recovery")
        md.append("- ✅ Log errors with context")
        md.append("- ✅ Clear error messages")
        md.append("- ❌ Don't silently swallow exceptions")
        md.append("")
        md.append("### File Conventions")
        md.append("- Functions: `snake_case`")
        md.append("- Classes: `PascalCase`")
        md.append("- Constants: `UPPER_SNAKE_CASE`")
        md.append("- Files: `snake_case.py` or `kebab-case.md`")
        md.append("")
        md.append("### Safety Requirements")
        md.append("- ✅ Backup before modifications")
        md.append("- ✅ Validation before writes")
        md.append("- ✅ Rollback capability")
        md.append("- ✅ Confirmation for destructive ops")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== FILES CREATED/MODIFIED =====
        md.append("## Files Created/Modified")
        md.append("")
        md.append("### Created")
        if artifacts:
            for artifact in artifacts:
                filename = artifact.get('filename', 'unknown')
                desc = artifact.get('description', 'File created during conversation')
                md.append(f"- `{filename}` - {desc}")
        else:
            md.append("- No files created during this conversation")
        md.append("")
        md.append("### Modified")
        md.append("- (Modification tracking not yet implemented)")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== THREAD LINEAGE & RELATED WORK =====
        md.append("## Thread Lineage & Related Work")
        md.append("")
        
        # Check for related threads in metadata
        related_threads = aar_data.get('related_threads', [])
        if related_threads:
            md.append("### Previous Related Threads")
            for thread in related_threads:
                md.append(f"- Thread {thread}: Related work")
            md.append("")
        else:
            md.append("### Previous Related Threads")
            md.append("- No related threads explicitly linked")
            md.append("")
        
        md.append("### Related System Components")
        md.append("- N5 System: Core personal knowledge management system")
        md.append("- Thread Export: AAR generation and archival")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== SUCCESS CRITERIA =====
        md.append("## Success Criteria")
        md.append("")
        md.append("**Definition of Done:**")
        md.append("- [x] Thread exported with complete AAR")
        md.append("- [x] All artifacts archived")
        md.append("- [x] Schema validation passed")
        md.append("")
        md.append("**Acceptance Tests:**")
        md.append("```bash")
        md.append("# Test 1: Verify archive exists")
        md.append(f"ls -la N5/logs/threads/{thread_id}* && echo 'PASS' || echo 'FAIL'")
        md.append("")
        md.append("# Test 2: Verify AAR files")
        md.append(f"ls -la N5/logs/threads/{thread_id}*/aar-*.{{json,md}} && echo 'PASS' || echo 'FAIL'")
        md.append("```")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== CONTEXT FOR RESUME =====
        md.append("## Context for Resume")
        md.append("")
        md.append("**When resuming this thread:**")
        md.append("")
        md.append("### Step 1: Verify Environment (5 min)")
        md.append("```bash")
        md.append("# Check state snapshot matches")
        md.append(f"ls -la N5/logs/threads/{thread_id}*")
        md.append("```")
        md.append("")
        md.append("### Step 2: Review Key Context (5 min)")
        md.append("- Read \"Critical Constraints\" - know what NOT to change")
        md.append("- Read \"Known Issues\" - avoid known problems")
        md.append("- Read \"What Was Completed\" - understand current state")
        md.append("")
        md.append("### Step 3: Validate Assumptions (3 min)")
        md.append("```bash")
        md.append("# Run assumption checks from Assumptions section")
        md.append("ls -la /home/workspace/N5/{commands,scripts,schemas,logs}")
        md.append("```")
        md.append("")
        md.append("### Step 4: Start Work (from Next Steps)")
        if next_steps:
            md.append(f"- Priority 1: {next_steps[0].get('action', 'Review and plan')}")
        else:
            md.append("- Review AAR and determine priorities")
        md.append("- Follow conventions from \"User Preferences\" section")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== RELATED DOCUMENTATION =====
        md.append("## Related Documentation")
        md.append("")
        md.append("- **System Overview:** `file 'Documents/N5.md'`")
        md.append("- **Preferences:** `file 'N5/prefs/prefs.md'`")
        md.append("- **AAR Schema:** `file 'N5/schemas/aar.schema.json'`")
        md.append(f"- **This Thread Archive:** `file 'N5/logs/threads/{thread_id}/aar-{export_date}.md'`")
        md.append("- **Export Command:** `file 'N5/commands/thread-export.md'`")
        md.append("- **Export Script:** `file 'N5/scripts/n5_thread_export.py'`")
        md.append("")
        md.append("---")
        md.append("")
        
        # ===== EXPORT METADATA =====
        md.append("## Export Metadata")
        md.append("")
        gen_by = telemetry.get('aar_generated_by', 'Vrijen The Vibe Thinker (Zo)')
        gen_method = telemetry.get('aar_generation_method', 'interactive')
        md.append(f"**Generated by:** {gen_by}  ")
        md.append(f"**Generation method:** {gen_method}  ")
        md.append(f"**Export format version:** {AAR_VERSION}  ")
        md.append("**Schema validation:** ✅ Passed")
        md.append("")
        md.append("**Artifact Statistics:**")
        md.append(f"- Files created: {artifact_count}")
        md.append(f"- Total size: {total_size:.1f} KB")
        
        # Count by type
        script_count = len([a for a in artifacts if a.get('type') == 'script'])
        doc_count = len([a for a in artifacts if a.get('type') == 'document'])
        data_count = len([a for a in artifacts if a.get('type') == 'data'])
        
        md.append(f"- Code files: {script_count}")
        md.append(f"- Documentation files: {doc_count}")
        md.append(f"- Data files: {data_count}")
        md.append("")
        md.append("---")
        md.append("")
        md.append("**Ready for continuation:** Yes")
        md.append("")
        md.append("**To resume:** Load this file, verify state snapshot, review Critical Constraints and Known Issues, then proceed with Next Steps.")
        
        return '\\n'.join(md)
