# Obsidian Setup Guide for N5
**Date:** 2025-10-27  
**Purpose:** Configure Obsidian as a view layer for Knowledge/

---

## Installation Complete ✅

Obsidian has been installed to: `~/Apps/Obsidian.AppImage`

**To launch:**
```bash
~/Apps/Obsidian.AppImage
```

Or find "Obsidian" in your applications menu.

---

## Initial Setup Steps

### 1. First Launch - Create Vault

When you first open Obsidian:
1. Click **"Open folder as vault"**
2. Navigate to: `/home/workspace/Knowledge/`
3. Click **"Open"**

**Important:** Select "Trust author and enable plugins" if prompted

### 2. Recommended Core Plugin Settings

Go to: **Settings (gear icon) → Core plugins**

**Enable these:**
- ✅ **Graph view** - Visual representation of note connections
- ✅ **Backlinks** - See what links to current note
- ✅ **Outlines** - Document structure sidebar
- ✅ **Search** - Fast full-text search
- ✅ **Quick switcher** - Cmd/Ctrl+O to jump between notes
- ✅ **File recovery** - Auto-saves and recovery

**Disable these (for now):**
- ❌ Daily notes - Not relevant for Knowledge base
- ❌ Templates - Enable later if needed
- ❌ Slides - Not needed

### 3. Graph View Configuration

**Settings → Graph view:**
- Enable **Local graph** - Shows connections for current note
- **Filters:** Exclude `assets/`, `templates/` if you have them
- **Forces:** Adjust link distance (default is good)

**To open graph:**
- Press `Ctrl+G` or click graph icon in left sidebar
- Shows your entire Knowledge/ as an interactive graph

### 4. Appearance Settings

**Settings → Appearance:**
- **Theme:** Dark or Light (matches N5 terminal vibe)
- **Base color scheme:** Choose what's easy on your eyes
- **Font:** Default is fine, or use your preferred monospace

### 5. Hotkeys to Learn

| Action | Hotkey | What It Does |
|--------|--------|--------------|
| Quick switcher | `Ctrl+O` | Jump to any note instantly |
| Search | `Ctrl+Shift+F` | Search across all notes |
| Graph view | `Ctrl+G` | Open knowledge graph |
| Command palette | `Ctrl+P` | Access all commands |
| Toggle edit/preview | `Ctrl+E` | Switch modes |

---

## N5-Specific Configuration

### Treating Obsidian as a View Layer

**Key Principle:** Markdown files in Knowledge/ remain the **single source of truth (SSOT)**.

Obsidian is just a *viewer/editor* with superpowers:
- Graph visualization
- Better linking between concepts
- Visual planning with canvas

**What this means:**
- All files stay as `.md` (no proprietary format)
- Git still works normally
- Zo can still read/write files
- You can edit in Zed, view in Obsidian, or vice versa

### Creating Links Between Notes

**Internal links syntax:**
```markdown
[[architectural_principles]]  # Links to architectural_principles.md
[[P0-rule-of-two|Rule of Two]]  # Link with custom text
```

**Backlinks automatically work:**
- When you link to a note, it shows up in that note's backlinks
- Great for seeing "what references this principle?"

### Using Graph View for Architecture

**Example use case:**
1. Open graph view (`Ctrl+G`)
2. See how principles connect to implementations
3. Find orphaned knowledge (notes with no connections)
4. Plan new components by seeing what exists

**Filter graph:**
- Type `path:architectural/principles/` to see only those
- Color-code by folder/tag

### Recommended Workflow

```markdown
**Morning:** 
- Open Obsidian graph view
- Review what you worked on yesterday (recent notes)
- Plan today's focus area

**During Work:**
- Code/write in Zed or terminal
- Quick reference in Obsidian (Ctrl+O to find note)
- Add new knowledge notes in either tool

**Conversation End:**
- Review new insights
- Create knowledge notes
- Link to related concepts
```

---

## Advanced: Community Plugins (Optional)

**Later, when comfortable, consider:**

**Dataview** - Query notes like a database
```markdown
```dataview
TABLE file.ctime as "Created"
FROM "architectural/principles"
SORT file.ctime DESC
LIMIT 10
```
```

**Excalidraw** - Draw diagrams in notes
- Visual architecture planning
- Better than D2 for quick sketches

**Templater** - Advanced templates
- Auto-generate knowledge note structure
- Insert dates, metadata automatically

---

## Troubleshooting

**AppImage won't launch?**
```bash
# Check permissions
ls -la ~/Apps/Obsidian.AppImage

# Try direct execution
~/Apps/Obsidian.AppImage --no-sandbox
```

**Want to update Obsidian later?**
```bash
# Download new version, replace old one
curl -L "https://github.com/obsidianmd/obsidian-releases/releases/latest/download/Obsidian-[VERSION].AppImage" -o ~/Apps/Obsidian.AppImage
chmod +x ~/Apps/Obsidian.AppImage
```

---

## Key Takeaway

**Obsidian is NOT replacing your markdown files.**

It's a **visualization and navigation layer** on top of Knowledge/ that makes it easier to:
- See connections between ideas
- Find related notes quickly  
- Plan architecture visually
- Navigate large knowledge bases

Your markdown files remain untouched and portable. You can stop using Obsidian anytime without losing anything.

---

**Next:** Launch Obsidian and open `/home/workspace/Knowledge/` as vault
