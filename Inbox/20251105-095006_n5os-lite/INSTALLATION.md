# N5OS Lite Installation Guide

**Version:** 1.0  
**Platform:** Zo Computer (or any AI-assisted environment)  
**Time Required:** 5-10 minutes

---

## Prerequisites

- Access to Zo Computer or similar AI assistant platform
- Workspace directory (typically `/home/workspace`)
- Basic familiarity with file system navigation
- Ability to create personas and rules in your AI platform

---

## Installation Methods

### Method 1: Automated Setup (Recommended)

**For Zo Computer users:**

1. **Download package:**
   ```bash
   cd /home/workspace
   curl -L https://github.com/YOUR_ORG/n5os-lite/archive/v1.0.tar.gz | tar xz
   ```

2. **Run setup script:**
   ```bash
   cd n5os-lite
   ./setup.sh
   ```

3. **Verify installation:**
   ```bash
   ls -la /home/workspace/Prompts/
   ls -la /home/workspace/Lists/
   ```

### Method 2: Manual Setup

**If automatic setup isn't available:**

1. **Create directory structure:**
   ```bash
   mkdir -p /home/workspace/{Prompts,Lists,Knowledge,Personal,Projects,Inbox}
   ```

2. **Copy core files:**
   - Copy `prompts/*.md` to `/home/workspace/Prompts/`
   - Copy `principles/*.yaml` to a reference location
   - Copy `system/*.md` to `/home/workspace/Knowledge/system/`

3. **Import personas:**
   - Use your AI platform's persona import feature
   - Load each persona from `personas/*.yaml`
   - Configure routing between personas

4. **Create rules (optional):**
   - Reference `rules/rule_system.md` for examples
   - Add rules via your AI platform's settings

---

## Post-Installation Configuration

### 1. Import Personas

**In Zo Computer:**

For each persona file in `personas/`:

```
Tell your AI:
"Create a new persona using the definition in personas/operator.yaml"
```

Repeat for:
- `personas/builder.yaml`
- `personas/strategist.yaml`
- `personas/architect.yaml`
- `personas/writer.yaml`
- `personas/teacher.yaml`
- `personas/debugger.yaml`
- `personas/researcher.yaml`

### 2. Configure Protection (Optional)

Create `.protected` markers for critical directories:

```bash
echo "Core prompts - do not delete without confirmation" > /home/workspace/Prompts/.protected
echo "Knowledge base - do not delete without confirmation" > /home/workspace/Knowledge/.protected
```

### 3. Initialize Example Lists

Create starter lists:

```bash
cat > /home/workspace/Lists/tools.jsonl << 'EOF'
{"name": "ripgrep", "description": "Fast grep alternative in Rust", "tags": ["cli", "search"], "created": "2025-11-03", "updated": "2025-11-03"}
EOF

cat > /home/workspace/Lists/resources.jsonl << 'EOF'
{"name": "N5OS Lite Documentation", "description": "Core system documentation", "tags": ["reference", "n5os"], "url": "file://system/", "created": "2025-11-03", "updated": "2025-11-03"}
EOF
```

### 4. Test Installation

**Run these verification steps:**

1. **Test prompt loading:**
   ```
   Tell your AI: "Load prompt Prompts/planning_prompt.md and summarize its framework"
   ```

2. **Test persona switching:**
   ```
   Tell your AI: "Switch to Builder persona"
   ```

3. **Test list operations:**
   ```
   Tell your AI: "Query my tools list for entries tagged 'cli'"
   ```

4. **Test principle reference:**
   ```
   Tell your AI: "Explain P15 (Complete Before Claiming)"
   ```

---

## Troubleshooting

### Issue: Prompts not found

**Solution:**
```bash
ls -la /home/workspace/Prompts/
# Verify files are in correct location
# Check file permissions (should be readable)
```

### Issue: Personas not working

**Symptoms:** AI doesn't recognize persona names or switching fails

**Solutions:**
1. Verify personas are imported in your AI platform
2. Check persona IDs match expected format
3. Try explicit persona invocation: "Activate System Builder persona"

### Issue: Lists not accessible

**Solution:**
```bash
mkdir -p /home/workspace/Lists
# Ensure directory exists
# Check that JSONL files have proper format (one JSON object per line)
```

### Issue: Principles not being applied

**Symptoms:** AI doesn't follow architectural principles

**Solutions:**
1. Explicitly reference principles: "Apply P15 to this work"
2. Load planning prompt before major work
3. Create rules that trigger principle application

---

## Verification Checklist

After installation, verify:

- [ ] Directory structure exists (`Prompts/`, `Lists/`, `Knowledge/`, etc.)
- [ ] Core prompts accessible (`planning_prompt.md`, `thinking_prompt.md`)
- [ ] At least 3 personas imported and functional
- [ ] Protection system understood (optional but recommended)
- [ ] Example lists created and queryable
- [ ] Can reference principles by ID (P1, P15, etc.)

---

## Next Steps

1. **Read the Quick Start Guide** - `QUICKSTART.md`
2. **Review core principles** - `principles/principles_index.yaml`
3. **Try your first workflow** - Load planning prompt and build something
4. **Customize** - Add your own prompts, personas, principles

---

## Getting Help

**Documentation:**
- `README.md` - Overview and introduction
- `ARCHITECTURE.md` - System design and philosophy
- `system/` - Detailed system documentation

**Common Questions:**
- **"Which persona should I use?"** - Start with Operator for general tasks, switch to specialists as needed
- **"When should I load prompts?"** - Load planning prompt before significant work, thinking prompt for strategic decisions
- **"How do I add my own principles?"** - Create a new YAML file in principles/, follow existing format

**Community:**
- GitHub Issues: Report bugs or request features
- Discussions: Share workflows and ask questions

---

## Uninstallation

To remove N5OS Lite:

```bash
# Remove core files
rm -rf /home/workspace/Prompts/planning_prompt.md
rm -rf /home/workspace/Prompts/thinking_prompt.md
# ... (remove other installed files)

# Remove personas via your AI platform's settings

# Optionally remove created directories if empty
```

**Note:** Be careful not to delete your own content in shared directories.

---

*Installation complete! Ready to build with AI assistance.*

**Version:** 1.0  
**Last Updated:** 2025-11-03
