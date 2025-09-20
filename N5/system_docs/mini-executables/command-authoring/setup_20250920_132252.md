# N5 Command Authoring Setup - Executable Steps

**State Header** (Do not edit manually. Zo updates this.)

- **Step 0: Unpacked** - Completed.
- **Step 1: Preflight Check** - Pending.
- **Step 2: Structure Creation** - Pending.
- **Step 3: Foundational File Population** - Pending.
- **Step 4: Verification & Finalization** - Pending.
- **Completed**: No (Timestamp: N/A)
- **Lock**: Unlocked (Proceed to Step 1)

---

## Step 1: Preflight Check & Confirmation
**Pre-conditions:** Workspace accessible and writable

```bash
# Start Step 1: Preflight Check
echo "Step 1/4: Preflight Check Starting..."

# Check for Git installation
if ! command -v git &> /dev/null
then
    echo "Warning: Git is NOT installed. Version tracking and rollback support will be limited."
    read -p "Type 'Proceed' to continue without Git, or any other key to abort: " git_confirm
    if [ "$git_confirm" != "Proceed" ]; then
        echo "Aborted due to missing Git. Please install Git and retry."
        exit 1
    fi
else
    echo "Git detected. Proceeding with version control enabled."
fi

# Check if N5 directory exists
if [ -d "/home/workspace/N5" ]; then
  echo "Warning: /home/workspace/N5 already exists. Possible existing setup."
  ls -l /home/workspace/N5
else
  echo "/home/workspace/N5 does not exist; clean slate detected."
fi

# List files to be created or overwritten
cat <<EOT
Planned changes:
- Create /home/workspace/N5/
- Create /home/workspace/N5/schemas/
- Add command templates to /home/workspace/N5/commands.md
- Add workflow examples to /home/workspace/N5/workflows.md
EOT

# Prompt for user confirmation
read -p "Confirm these changes? Type 'Confirm' to proceed or anything else to abort: " confirm
if [ "$confirm" != "Confirm" ]; then
  echo "Setup aborted by user at preflight check."
  exit 1
fi

# Mark step complete via Zo's LLM file edit
zo_update="- **Step 1: Preflight Check** - Completed."
cat <<EOF > /tmp/state_update.txt
$zo_update
EOF
# (User to run Zo chat `/edit_file` or equivalent here to update the state header)
echo "Step 1/4: Preflight Check Completed."
```

**Post-conditions:** User confirmed, ready for step 2

**Rollback:** Abort without changes

**User Guidance:** After confirming, proceed to step 2 by executing the provided block.

---

## Step 2: Directory Structure Creation
**Pre-conditions:** Step 1 completed

```bash
echo "Step 2/4: Creating directory structure..."

mkdir -p /home/workspace/N5/schemas
if [ $? -ne 0 ]; then
  echo "Error: Failed to create directories."
  exit 2
fi

echo "Directories created: /home/workspace/N5, /home/workspace/N5/schemas"

# Mark step completed
zo_update="- **Step 2: Structure Creation** - Completed."
cat <<EOF > /tmp/state_update.txt
$zo_update
EOF
# (User to update state header accordingly)

```

**Post-conditions:** Directory structure exists

**Rollback:** Remove newly created directories
```bash
rm -rf /home/workspace/N5/
```

**User Guidance:** Verify directories with `ls -l /home/workspace/N5`

---

## Step 3: Foundational File Population
**Pre-conditions:** Step 2 completed

```bash
# Step 3/4: Creating foundational files

# commands.md setup
cat << EOF > /home/workspace/N5/commands.md
# Command Catalog

## Generalized Command Authoring

- Commands are parameterized prompts or tool sequences.
- Example: 'search_web' with parameter 'query' calls the web_search tool.

Add your commands here.
EOF

# workflows.md setup
cat << EOF > /home/workspace/N5/workflows.md
# Workflow Systematization

## Example Workflow: Research Topic

1. Command: search_web(query='topic')
2. Command: deep_research(instructions='Synthesize results')

Chain commands to build repeatable processes.
EOF

# schemas/basic.json
cat << EOF > /home/workspace/N5/schemas/basic.json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"}
  },
  "required": ["query"]
}
EOF

# Mark step completed
zo_update="- **Step 3: Foundational File Population** - Completed."
cat <<EOF > /tmp/state_update.txt
$zo_update
EOF
# (User to update state header accordingly)

echo "Step 3/4: Foundational files created."
```

**Post-conditions:** Templates in place

**Rollback:** Remove created files
```bash
rm -f /home/workspace/N5/commands.md /home/workspace/N5/workflows.md /home/workspace/N5/schemas/basic.json
```

**User Guidance:** Inspect templates before building custom commands

---

## Step 4: Verification & Finalization
**Pre-conditions:** Step 3 completed

```bash
# Step 4/4: Verification and finalization

files=(/home/workspace/N5/commands.md /home/workspace/N5/workflows.md /home/workspace/N5/schemas/basic.json)

for f in "${files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "Error: Expected file $f not found!"
    exit 4
  fi
done

# Mark overall setup complete
zo_update="- **Step 4: Verification & Finalization** - Completed.
- **Completed**: Yes (Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ'))"
cat <<EOF > /tmp/state_update.txt
$zo_update
EOF
# (User to update state header accordingly)

echo "Setup verification succeeded. Setup is complete and locked."
```

**Post-conditions:** All required files verified

**Rollback:** Full removal recommended if failed

**User Guidance:** Ready to use! Begin authoring commands and workflows.

---

**Uninstall/Rollback Guide**

Delete the N5 setup by:

```bash
rm -rf /home/workspace/N5
```

Or ask Zo: "Remove N5 command authoring setup."


---

# Support

For questions or help, join the Zo community Discord channel.