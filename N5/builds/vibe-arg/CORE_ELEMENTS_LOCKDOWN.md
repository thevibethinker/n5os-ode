---
created: 2025-12-25
last_edited: 2025-12-26
version: 2
provenance: con_EiwUANQjvv2xm9Yv
---
# Zorg: Core Elements Lockdown

## Purpose
Before developing the story, lock down all Zo capabilities to teach, technical infrastructure requirements, and progression mechanics.

---

## Section A: Zo Capabilities to Teach

### A1. File Operations & Navigation
**Concept:** Understanding Zo's file system and workspace structure.
**Target Skills:**
- Reading files (`read_file`)
- N5 directory structure navigation
- File discovery (searching, finding files)
- Relative vs absolute paths

**Teaching Method:**
- Riddle-based file location puzzles
- Clues hidden in directory names
- "Navigate to the location described in the riddle"

### A2. Tool Usage
**Concept:** Using Zo's built-in tools for different tasks.
**Target Skills:**
- `run_bash_command` for CLI operations
- `grep_search` for content and filename searching
- `web_search` / `web_research` for information gathering
- `maps_search` for location data
- Basic command-line familiarity

**Teaching Method:**
- Scripts that must be executed to decode information
- Web searches needed to solve riddles
- CLI commands revealed as "encryption keys"

### A3. Persona Routing (Specialists)
**Concept:** Routing to the right AI persona for the task.
**Target Skills:**
- Understanding different personas (Researcher, Strategist, Builder, etc.)
- Semantic routing (knowing when to use which specialist)
- Using `set_active_persona`

**Teaching Method:**
- Mystery clues that require specific analytical approaches
- "Consult the Researcher about X" or "Ask the Builder to examine Y"
- Persona-specific puzzle solutions

### A5. Script Execution & Automation
**Concept:** Running Python/Bun scripts for extended functionality.
**Target Skills:**
- Executing N5 scripts (`N5/scripts/`)
- Understanding script flags and parameters
- Using scripts to process data or perform operations

**Teaching Method:**
- Scripts that decrypt hidden messages
- Scripts that reveal clues when run with specific flags
- "Run the decoder script to reveal the next location"

### A6. Sites & Web Apps
**Concept:** Building and hosting sites/applications on Zo.
**Target Skills:**
- `create_website` for new projects
- Site deployment and previewing
- Understanding site structure

**Teaching Method:**
- Building the TRON site IS Stage 4 puzzle solution
- User creates site to unlock clue, demonstrating capability
- TRON site becomes their control center for remaining stages

### A7. Gmail Integration
**Concept:** Connecting Zo to Gmail for communication.
**Target Skills:**
- Gmail integration (reading/writing emails)
- Understanding connected services
- Email-triggered automation

**Teaching Method:**
- Clues delivered via "intercepted emails" in Gmail
- Email trigger mechanism on repo clone (or email submission)
- User must read/respond to email to progress

**Email Trigger Implementation:**
- GitHub webhook on repo clone (if feasible) OR
- Simple email submission form on initial site
- Trigger sends automated email with encrypted clue
- User connects Gmail account and reads message to proceed

### A10. Rules & Customization
**Concept:** Customizing Zo behavior and setting preferences.
**Target Skills:**
- Creating user rules
- Setting bio and preferences
- Persona management

**Teaching Method:**
- Rules needed to unlock specific puzzle stages
- Bio/personalization required to "close the case"
- Custom rule creation as part of final stage

---

## Section B: Technical Infrastructure

### B1. The "Skip" Mechanism
**Requirement:** Users must be able to skip any stage by clicking "Next," which auto-executes the intended action.

**Implementation:**
- Each stage has two execution paths:
  - **Manual Path:** User solves puzzle, runs command, receives reward
  - **Skip Path:** Click "Next" button, script runs the command automatically
- Skip must be clearly visible but visually distinct
- Skipping should still demonstrate what the action does

**Technical Approach:**
- Site with stage-based progression UI
- Each "Next" button triggers server-side script execution
- Scripts perform the exact actions manual path requires
- State updates reflect completion either way

### ~~B2. Session State Display~~ → **MOVED TO APPENDIX**
**Reasoning:** Session state runs in background for new users. Display logic documented in post-game appendix for curious learners.

### B3. The TRON Site
**Requirement:** 80s/90s aesthetic, TRON-style visuals, 32-bit energy.

**Design Elements:**
- Dark backgrounds (black, deep blue)
- Neon accent colors (cyan, magenta, electric blue)
- Grid patterns, geometric shapes
- Glitch effects, scan lines
- Pixel fonts or retro-futuristic typography
- Glowing borders, terminal-style text

**Technical Approach:**
- Tailwind CSS with custom color palette
- CSS animations for glowing/pulsing effects
- Optional: Three.js or canvas for background grid effects

### B4. GitHub Repository Structure
**Requirement:** Complete repo with all game assets ready to install.

**Structure:**
```
zorg-repo/
├── README.md                    # Installation instructions
├── Sites/zorg-tron/             # The TRON site
│   ├── package.json
│   ├── routes/                   # Site endpoints
│   └── static/                   # Assets
├── N5/
│   ├── scripts/
│   │   ├── stage_executor.py      # Skip mechanism script
│   │   └── cleanup.py            # End-of-game cleanup
│   └── prompts/
│       └── stage_helpers/          # Puzzle-solving helpers
├── Knowledge/
│   └── Zorg/                     # Game lore and assets
├── Inbox/
│   └── Case_Files/               # The mystery case files
└── SESSION_STATE.md               # Game state tracking
```

### B5. The Cleanup Script
**Requirement:** End-of-game script that archives game artifacts and leaves clean workspace.

**Operations:**
- Move `Inbox/Case_Files/` to `Documents/Archive/Zorg/`
- Move `Knowledge/Zorg/` to `Documents/Archive/Zorg/`
- Archive the TRON site (optional: keep as template)
- Reset `SESSION_STATE.md` to clean user state
- Remove any game-specific prompts or scripts
- Leave user with initialized N5 structure and personal settings

---

## Section C: Puzzle Mechanics

### C1. Riddles
**Purpose:** Guide users to locations or concepts without explicit instructions.

**Design Patterns:**
- **Location Riddles:** Point to specific files/directories
- **Concept Riddles:** Introduce Zo capabilities metaphorically
- **Progressive Riddles:** Solve one to get the next

**Examples:**
- "I hold the past in numbered lines, where conversations live and secrets hide." → SESSION_STATE.md
- "I build what you say, no code required, from nothing to something with one command." → `generate_image`

### C2. Codes & Ciphers
**Purpose:** Require technical skills to decode hidden messages.

**Types:**
- **Base64:** Simple decoding puzzles
- **Caesar Cipher:** Shift-based letter puzzles
- **File Metadata:** Clues hidden in YAML frontmatter
- **Binary/Hex:** Technical literacy tests
- **Multi-stage Ciphers:** Combining multiple encoding methods

**Implementation:**
- Cipher clues embedded in case files
- Decoding requires specific tool usage (bash, python)
- Each code reveals next puzzle piece

### C3. File Structure Puzzles
**Purpose:** Teach N5 navigation through the mystery.

**Patterns:**
- Follow-the-breadcrumbs: Clues lead to files with more clues
- Directory naming hints: Folder names contain puzzle hints
- File relationships: Cross-referencing between multiple files
- Hidden files: `.hidden` files discovered via CLI commands

---

## Section D: Progression Structure

### D1. Stage-Based Progression
**Concept:** Linear stages that can be skipped or solved.

**Structure:**
1. **Stage 0:** Installation & Site Launch
2. **Stage 1:** File Discovery (N5 Navigation) [A1]
3. **Stage 2:** Tool Usage (CLI & Scripts) [A2]
4. **Stage 3:** Persona Routing (Specialists) [A3]
5. **Stage 4:** Site Building (Creating the artifact) [A6]
6. **Stage 5:** External App Integration (Gmail/Drive) [A7]
7. **Stage 6:** Personalization (Settings & Rules) [A10]
8. **Stage 7:** Case Resolution (Final Puzzle)
9. **Stage 8:** Cleanup & Completion

### D2. Each Stage Contains:
- **Objective:** What the user learns/accomplishes
- **Puzzle:** The riddle/cipher to solve
- **Manual Path:** How to solve it using Zo skills
- **Skip Path:** Auto-execution via "Next" button
- **State Update:** What changes in `SESSION_STATE.md` (background)
- **Reward:** Progress unlock or clue for next stage

### D3. Completion State
**User Has:**
- Functional N5 workspace structure
- Personalized settings (name, bio, preferences)
- Understanding of core Zo capabilities (A1, A2, A3, A5, A6, A7, A10)
- Experience using major tools and features
- A clean workspace ready for production use

### D4: Epilogue
**Post-game documentation covering:**
- A4: Session State Management (how it works in background)
- A8: Lists & Task Management (N5 Lists system)
- A9: Knowledge Management (Knowledge/ directory, search)
- B2: Session State Display (how to view/debug it)

**Format:** Optional slide deck or extended README that invites curious users to learn more about the system they just used.

---

## Section E: Aesthetic & Experience Design

### E1. The TRON Aesthetic
**Visual Language:**
- Dark mode default
- Neon cyan/magenta primary colors
- Grid line overlays
- Glitch text effects
- Scan line overlays
- Glowing borders on active elements
- Terminal-style command outputs

**Color Palette:**
- Background: #0a0a0a, #0d1117
- Primary: #00ffff (cyan), #ff00ff (magenta)
- Accent: #00ff00 (green), #ffff00 (yellow)
- Text: #e6edf3 (white/light gray)
- Error: #ff4444 (red), #ff8800 (orange)

### E2. Tone & Voice
**Characteristics:**
- Professional yet mysterious
- Encouraging of exploration
- Technical but accessible explanations
- Celebration of "aha!" moments
- Respect for user's intelligence

**Avoid:**
- Talking down to user
- Cheesy gamification tropes
- Overly dramatic narrative
- Breaking character with meta-explanations

### E3. Feedback & Progression
**Feedback Types:**
- **Visual:** Stage completion animations, progress bars filling
- **Textual:** Confirmations, hints, celebration messages
- **Functional:** Unlocked tools, revealed files, progressed state

**Progression Signals:**
- Glowing stages in the TRON site
- Updated SESSION_STATE display
- New files appearing in workspace
- Persona unlocks/recommendations

---

## Next Steps
Once this Core Elements Lockdown is approved:
1. Design specific puzzles for each stage (align with A1-A10)
2. Write the mystery narrative wrapper (the "case")
3. Build the TRON site with stage progression UI
4. Implement skip mechanism scripts
5. Create the GitHub repo with all assets
6. Test the full flow from install to cleanup








