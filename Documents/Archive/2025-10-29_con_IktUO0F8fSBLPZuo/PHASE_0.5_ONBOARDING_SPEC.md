# N5 OS Phase 0.5: Initial Setup & Onboarding
# Comprehensive Specification

**Worker**: WORKER_dfVR_20251028_085810  
**Thread**: con_IktUO0F8fSBLPZuo  
**Parent**: con_2rD2ojBNmRthdfVR  
**Date**: 2025-10-28  
**Status**: 📋 PLAN Phase  

---

## THINK Phase: Understanding the Mission

### Purpose
Phase 0.5 creates the **first-run experience** for N5 OS users. This is the critical moment where users go from "I installed this" to "I understand and trust this system."

### Why This Matters
- **First impressions**: Users decide if N5 is worth learning
- **Personalization**: Generic defaults = weak adoption
- **Education**: Must teach concepts without overwhelming
- **Validation**: Users need confidence that setup worked
- **Trust**: Conversational onboarding builds relationship with Zo

### Target User Profile
- **Background**: Startup folks (founders, early employees, operators)
- **Technical range**: Some developers, many non-technical with potential
- **Assumptions**: NO command line experience required
- **Motivation**: Want productivity tools, willing to invest 10-15 min
- **State**: N5 already cloned/installed through Phase 4

### Core Insight
**Onboarding is not configuration—it's education through personalization.**

Users learn N5 concepts by making choices about their own setup. The interview questions double as teaching moments.

---

## PLAN Phase: Onboarding Flow Design

### Overview: The Three Acts

```
┌─────────────────────────────────────────────────────────┐
│  ACT 1: DISCOVER (5-7 min)                              │
│  • Welcome + context setting                            │
│  • Personal information                                  │
│  • Work style discovery                                  │
│  • Goals & use cases                                     │
│  └─→ OUTPUT: User profile data                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ACT 2: CUSTOMIZE (3-4 min)                             │
│  • Review proposed settings                              │
│  • Make key decisions                                    │
│  • Preview configurations                                │
│  • Confirm and apply                                     │
│  └─→ OUTPUT: Personalized configs                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ACT 3: VALIDATE & TEACH (2-4 min)                      │
│  • Run validation tests                                  │
│  • Teach core concepts                                   │
│  • Demo key features                                     │
│  • Provide next steps                                    │
│  └─→ OUTPUT: Confident, educated user                   │
└─────────────────────────────────────────────────────────┘
```

**Total time: 10-15 minutes**

---

## ACT 1: DISCOVER (The Interview)

### Conversation Flow

**Stage 1.1: Welcome & Context (1 min)**

```markdown
Hi! I'm Zo, your AI assistant. Welcome to N5 OS.

I'm going to help you set up your personal productivity system. This will take about 10-15 minutes and I'll be asking you questions to understand how you work.

Everything we configure today can be changed later—this is just to get you started with settings that make sense for YOU.

Ready to begin?
```

**Principle**: Set expectations, reduce anxiety, establish conversational tone.

---

**Stage 1.2: Personal Foundation (2 min)**

Ask in order, with brief explanations:

1. **Name**
   ```
   What should I call you?
   
   (This helps me personalize our conversations. Just your first name is fine, 
   or a nickname if you prefer.)
   ```

2. **Timezone**
   ```
   What timezone are you in?
   
   (This ensures scheduled tasks and timestamps match your day. 
   I can usually detect it, but let's confirm: [DETECTED_TZ]?)
   ```

3. **Role/Work Context**
   ```
   What do you do? (e.g., "founder", "product manager", "engineer", 
   "I'm figuring it out")
   
   (This helps me understand what kinds of tasks and workflows 
   will be most relevant for you.)
   ```

4. **Company/Project** (optional)
   ```
   Are you working on a specific company or project you'd want me to know about?
   
   (This can help me give better context-aware suggestions. 
   You can say "not yet" or skip this.)
   ```

**OUTPUT**: `user_profile.json`
```json
{
  "name": "Alex",
  "timezone": "America/New_York",
  "role": "founder",
  "company": "Acme Startup",
  "profile_completed": "2025-10-28T05:07:34Z"
}
```

---

**Stage 1.3: Work Style Discovery (3-4 min)**

Ask choice-based questions that teach concepts:

1. **Communication Preference**
   ```
   How do you prefer I communicate with you?
   
   a) Direct and concise (just the facts)
   b) Conversational and thorough (explain as you go)
   c) Adaptive (match my energy)
   
   (This controls how verbose I am in responses.)
   ```

2. **Decision Style**
   ```
   When we're working together, I should:
   
   a) Make smart defaults and just do it (I'll ask if critical)
   b) Always preview and get your confirmation before acting
   c) Depends on the task (use judgment)
   
   (This is about trust level and autonomy.)
   ```

3. **Collaboration Mode**
   ```
   N5 has different "modes" I can operate in. Which sounds most like you?
   
   a) Builder mode: I prototype, create, ship things
   b) Research mode: I investigate, analyze, synthesize
   c) Discussion mode: I think out loud, brainstorm, explore
   d) Planning mode: I organize, strategize, roadmap
   e) Mix of everything
   
   (This helps me set default session types and suggest relevant commands.)
   ```

4. **Meeting Cadence**
   ```
   How many meetings do you typically have per day?
   
   a) 0-2 (deep work focused)
   b) 3-5 (balanced)
   c) 6+ (heavily meeting-based)
   
   (This helps me suggest meeting-related workflows and automations.)
   ```

5. **Data Privacy Stance**
   ```
   How do you think about sensitive information in our workspace?
   
   a) Paranoid: Never store passwords, API keys, or sensitive data
   b) Cautious: Store encrypted or in separate vault
   c) Pragmatic: Store carefully but prioritize convenience
   
   (This affects security recommendations and file handling.)
   ```

6. **Command Line Comfort**
   ```
   How comfortable are you with command-line tools?
   
   a) What's a command line? (no experience)
   b) I can follow instructions (basic)
   c) Pretty comfortable (intermediate)
   d) I live in the terminal (advanced)
   
   (This helps me calibrate how much explanation to provide 
   for technical operations.)
   ```

**OUTPUT**: `work_style.json`
```json
{
  "communication": "conversational",
  "decision_style": "preview_confirm",
  "primary_mode": "builder",
  "meeting_cadence": "balanced",
  "data_privacy": "pragmatic",
  "cli_comfort": "basic",
  "assessed": "2025-10-28T05:10:00Z"
}
```

---

**Stage 1.4: Goals & Use Cases (1-2 min)**

Open-ended discovery:

```
What are the top 3 things you hope N5 will help you with?

Examples:
- "Keep track of my startup's CRM and fundraising"
- "Research and synthesize information quickly"
- "Build prototypes and test ideas"
- "Manage my calendar and email better"
- "Stay organized with notes and tasks"

Your turn:
1. 
2. 
3. 
```

**Follow-up questions** (adaptive based on answers):

- If "CRM" mentioned → "Do you use any CRM tools currently?"
- If "research" mentioned → "What kinds of topics do you research?"
- If "build" mentioned → "What technologies or tools do you typically use?"
- If "organize" mentioned → "What's your current system? (Notion, Apple Notes, etc.)"

**OUTPUT**: `use_cases.json`
```json
{
  "primary_goals": [
    "CRM and fundraising tracking",
    "Quick research and synthesis",
    "Prototype building"
  ],
  "current_tools": {
    "crm": "spreadsheets",
    "notes": "notion",
    "code": "none"
  },
  "pain_points": ["scattered information", "manual tracking"],
  "captured": "2025-10-28T05:12:00Z"
}
```

---

### ACT 1 Completion

```
Perfect! I've got a good sense of how you work.

Let me take a moment to configure N5 for you based on what you've shared.
This will take about 30 seconds...

[Processing indicator]

Done! Let me show you what I've set up.
```

**Technical**: In background, run:
```bash
python3 /home/workspace/N5/scripts/onboarding/personalize_config.py \
  --user-profile /tmp/onboarding/user_profile.json \
  --work-style /tmp/onboarding/work_style.json \
  --use-cases /tmp/onboarding/use_cases.json \
  --output /home/workspace/N5/config/
```

---

## ACT 2: CUSTOMIZE (Configuration Review)

### Stage 2.1: Config Preview (2 min)

Present personalized settings with explanations:

```markdown
Based on our conversation, here's what I've configured:

## 🎯 Your N5 Profile
- **Name**: Alex
- **Timezone**: America/New_York (EST/EDT)
- **Role**: Founder at Acme Startup
- **Primary mode**: Builder
- **CLI comfort**: Basic (I'll explain technical things)

## 🛠️ Core Settings
- **Communication style**: Conversational and thorough
- **Decision making**: Preview before acting (I'll show you what I'm about to do)
- **Data privacy**: Pragmatic (careful but convenient)

## 📋 Workflows Enabled
Based on your goals, I've set up:
- **CRM tracking** workflow (for managing contacts and fundraising)
- **Research assistant** mode (quick synthesis of information)
- **Builder tools** (prototyping and testing)

## ⚙️ Automatic Tasks
These will run in the background:
- **Daily cleanup** (11:00 PM EST - clears temp files, maintains system)
- **Weekly summary** (Monday 8:00 AM EST - highlights from last week)

## 🔧 Commands Created
You can trigger these by typing "/" in chat:
- `/research [topic]` - Start research session
- `/crm` - Open CRM workflow
- `/build [idea]` - Start prototype session
- `/reflect` - Weekly reflection prompt

Does this look good? You can:
- Apply as-is (recommended for first time)
- Adjust specific settings
- Skip optional features
```

---

**Stage 2.2: Key Decisions** (1-2 min)

Ask about trap doors (hard-to-reverse decisions):

1. **Data Location**
   ```
   Where should N5 store your working files?
   
   a) /home/workspace/ (default, recommended)
   b) Custom location (advanced)
   
   Most users choose (a). This keeps everything organized in one place.
   ```

2. **Notification Preferences**
   ```
   How should N5 notify you about scheduled tasks or important events?
   
   a) Email (I'll send updates to your Zo email)
   b) In-app only (check when you log in)
   c) SMS (requires setup)
   d) None (quiet mode)
   ```

3. **Integration Permissions**
   ```
   I noticed you use Notion and spreadsheets. 
   
   Would you like to connect external apps now or later?
   - Google Calendar, Drive, Gmail
   - Notion
   - Others
   
   You can connect these anytime from Settings > Integrations.
   Now or later?
   ```

**OUTPUT**: `customizations.json`
```json
{
  "data_location": "/home/workspace/",
  "notifications": "email",
  "integrations_now": false,
  "apply_defaults": true,
  "confirmed": "2025-10-28T05:14:00Z"
}
```

---

**Stage 2.3: Apply Configuration** (30 seconds)

```
Applying your configuration now...

✓ Personal profile saved
✓ Work style preferences set
✓ Workflows configured
✓ Scheduled tasks created
✓ Custom commands registered
✓ Validation rules applied

Configuration complete! Now let's make sure everything works.
```

**Technical**: Run:
```bash
python3 /home/workspace/N5/scripts/onboarding/apply_config.py \
  --config-dir /home/workspace/N5/config/ \
  --validate \
  --dry-run=false
```

---

## ACT 3: VALIDATE & TEACH (Verification & Education)

### Stage 3.1: System Validation (1 min)

Run automated tests, narrate progress:

```
Running system checks...

✓ Session state manager working
✓ Command system operational
✓ Scheduled tasks registered
✓ File permissions correct
✓ Database connections valid
✓ Safety systems active
✓ Integration hooks ready

All systems green! Your N5 OS is ready to use.
```

**Technical**: Run:
```bash
python3 /home/workspace/N5/scripts/onboarding/validate_setup.py \
  --comprehensive \
  --user-profile /home/workspace/N5/config/user_profile.json
```

Expected output:
```json
{
  "validation_passed": true,
  "tests_run": 23,
  "tests_passed": 23,
  "tests_failed": 0,
  "warnings": [],
  "validated_at": "2025-10-28T05:15:30Z"
}
```

If validation fails:
```
⚠️  I found a few issues we need to fix:

1. [ISSUE_DESCRIPTION]
   → Fixing now... [RESOLUTION]
   
2. [ISSUE_DESCRIPTION]
   → This requires your input: [PROMPT]

Let me resolve these and try again...
```

---

**Stage 3.2: Core Concepts Tour** (2-3 min)

Teach through demonstration:

```markdown
Let me show you the 5 core concepts that make N5 work:

### 1. **Session State** (Where we are)
Every conversation with me has a "state" - what we're working on, 
what we've done, what's next. 

Try this: In any conversation, say "show session state" and I'll 
tell you where we are. It keeps us aligned.

### 2. **Commands** (How to trigger workflows)
You saw the "/" commands I created. These are shortcuts for 
complex workflows.

Try typing "/" right now and you'll see your custom commands.
Each one is a complete workflow I can run for you.

### 3. **Recipes** (Reusable workflows)
Recipes are like commands but more flexible. They're templates 
for common tasks.

Location: Your workspace has a /Recipes folder. You can create 
your own or use the ones I've set up.

### 4. **Rules** (How I make decisions)
I follow rules you can customize. These control everything from 
how I format responses to what safety checks I run.

Location: N5/config/rules.md (You can edit anytime)

### 5. **Scheduled Tasks** (Automation)
Remember those daily/weekly tasks I set up? Those are "scheduled 
tasks" - they run automatically.

You can see them at: https://va.zo.computer/agents
(Accessible from the Agents page in your Zo)

---

**Want to try one?** Say "run /research quantum computing" 
and I'll demonstrate the research workflow.

Or we can skip to your welcome guide.
```

**Interactive demo** (if user engages):
- Run the command they choose
- Narrate what's happening
- Show the output
- Explain the components

**If user skips**:
```
No problem! You'll learn by doing. Let's wrap up.
```

---

**Stage 3.3: Welcome Guide & Next Steps** (1 min)

Provide clear next actions:

```markdown
## 🎉 Welcome to N5 OS, Alex!

Your system is configured and ready. Here's what to do next:

### Immediate Next Steps
1. **Try a command**: Type "/" and pick one to try
2. **Explore your workspace**: Check out /home/workspace/ structure
3. **Read the guide**: I've created a personalized guide for you

### Your Personalized Guide
I've created this for you: `file 'Documents/N5_Welcome_Guide_Alex.md'`

It includes:
- Quick reference for your custom commands
- Workflow tutorials tailored to your goals (CRM, research, building)
- Tips based on your CLI comfort level
- Common questions answered

### Learning Resources
- **Docs**: /home/workspace/Documents/N5.md (system overview)
- **Examples**: /home/workspace/examples/ (sample workflows)
- **Discord**: https://discord.gg/zocomputer (community support)

### If You Get Stuck
Just ask me! Say things like:
- "How do I [task]?"
- "Show me an example of [concept]"
- "I need help with [problem]"

I'm here to help you get the most out of N5.

Ready to start? What would you like to work on first?
```

**Technical**: Generate personalized welcome guide:
```bash
python3 /home/workspace/N5/scripts/onboarding/generate_welcome_guide.py \
  --user-profile /home/workspace/N5/config/user_profile.json \
  --work-style /home/workspace/N5/config/work_style.json \
  --use-cases /home/workspace/N5/config/use_cases.json \
  --output /home/workspace/Documents/N5_Welcome_Guide_${USER_NAME}.md
```

---

## TECHNICAL SPECIFICATION

### File Structure

```
/home/workspace/
├── N5/
│   ├── config/
│   │   ├── user_profile.json          # Personal info
│   │   ├── work_style.json            # Work preferences
│   │   ├── use_cases.json             # Goals & use cases
│   │   ├── customizations.json        # Key decisions
│   │   ├── onboarding_complete.json   # Completion marker
│   │   ├── prefs.md                   # Generated from template
│   │   ├── commands.jsonl             # Generated custom commands
│   │   └── rules.md                   # Generated rules
│   │
│   ├── scripts/
│   │   └── onboarding/
│   │       ├── onboarding_orchestrator.py  # Main entry point
│   │       ├── interview_conductor.py      # Manages conversation
│   │       ├── personalize_config.py       # Generates configs
│   │       ├── apply_config.py             # Applies settings
│   │       ├── validate_setup.py           # Runs tests
│   │       ├── generate_welcome_guide.py   # Creates guide
│   │       └── onboarding_utils.py         # Shared functions
│   │
│   └── templates/
│       └── onboarding/
│           ├── user_profile.template.json
│           ├── work_style.template.json
│           ├── prefs.template.md
│           ├── commands.template.jsonl
│           ├── rules.template.md
│           └── welcome_guide.template.md
│
└── Documents/
    └── N5_Welcome_Guide_${USER_NAME}.md  # Generated

/tmp/onboarding/  # Temporary workspace during onboarding
├── user_profile.json
├── work_style.json
├── use_cases.json
├── customizations.json
└── validation_results.json
```

---

### Script Interfaces

#### 1. `onboarding_orchestrator.py`

**Purpose**: Main entry point, orchestrates the full onboarding flow

```python
#!/usr/bin/env python3
"""
N5 OS Onboarding Orchestrator

Manages the complete onboarding flow from welcome to validation.
"""

import argparse
import logging
from pathlib import Path
from interview_conductor import InterviewConductor
from personalize_config import ConfigPersonalizer
from apply_config import ConfigApplicator
from validate_setup import SetupValidator
from generate_welcome_guide import WelcomeGuideGenerator

def main(
    convo_id: str,
    workspace: str = "/home/workspace",
    skip_interview: bool = False,
    dry_run: bool = False
) -> int:
    """
    Run complete onboarding flow.
    
    Args:
        convo_id: Current conversation ID
        workspace: User's workspace root
        skip_interview: Skip interview (use defaults)
        dry_run: Preview without applying
        
    Returns:
        0 on success, 1 on failure
    """
    try:
        logger.info(f"Starting onboarding for conversation {convo_id}")
        
        # Stage 1: Interview (DISCOVER)
        if not skip_interview:
            conductor = InterviewConductor(convo_id=convo_id)
            profile_data = conductor.run_interview()
        else:
            profile_data = load_default_profile()
        
        # Stage 2: Personalize (CUSTOMIZE)
        personalizer = ConfigPersonalizer(
            workspace=workspace,
            profile_data=profile_data
        )
        configs = personalizer.generate_configs(dry_run=dry_run)
        
        # Stage 3: Apply
        if not dry_run:
            applicator = ConfigApplicator(workspace=workspace)
            applicator.apply(configs)
        
        # Stage 4: Validate (VALIDATE & TEACH)
        validator = SetupValidator(workspace=workspace)
        validation_result = validator.validate(profile_data)
        
        if not validation_result.passed:
            logger.error(f"Validation failed: {validation_result.errors}")
            return 1
        
        # Stage 5: Welcome Guide
        guide_gen = WelcomeGuideGenerator(
            workspace=workspace,
            profile_data=profile_data
        )
        guide_path = guide_gen.generate()
        
        # Mark complete
        mark_onboarding_complete(workspace, profile_data, validation_result)
        
        logger.info(f"✓ Onboarding complete! Welcome guide: {guide_path}")
        return 0
        
    except Exception as e:
        logger.error(f"Onboarding failed: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--convo-id", required=True)
    parser.add_argument("--workspace", default="/home/workspace")
    parser.add_argument("--skip-interview", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    exit(main(
        convo_id=args.convo_id,
        workspace=args.workspace,
        skip_interview=args.skip_interview,
        dry_run=args.dry_run
    ))
```

---

#### 2. `interview_conductor.py`

**Purpose**: Manages conversational interview flow

```python
#!/usr/bin/env python3
"""
Interview Conductor - Manages onboarding conversation flow
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import json

@dataclass
class InterviewQuestion:
    id: str
    stage: str
    text: str
    explanation: str
    type: str  # "text", "choice", "multiline"
    options: List[str] = None
    follow_up: callable = None

class InterviewConductor:
    """Conducts onboarding interview via conversation."""
    
    def __init__(self, convo_id: str):
        self.convo_id = convo_id
        self.responses = {}
        self.questions = self._load_questions()
    
    def run_interview(self) -> Dict[str, Any]:
        """
        Run complete interview flow.
        
        Returns:
            Dict with user_profile, work_style, use_cases
        """
        # Implementation: Present questions, collect responses,
        # generate structured data
        pass
    
    def _load_questions(self) -> List[InterviewQuestion]:
        """Load interview questions from templates."""
        # Questions defined in Act 1 above
        pass
    
    def ask_question(self, question: InterviewQuestion) -> Any:
        """Present question and collect response."""
        pass
    
    def generate_profile_data(self) -> Dict[str, Any]:
        """Convert responses into structured profile data."""
        pass
```

---

#### 3. `personalize_config.py`

**Purpose**: Generate personalized configs from templates

```python
#!/usr/bin/env python3
"""
Config Personalizer - Generate customized N5 configs from templates
"""

from pathlib import Path
from typing import Dict, Any
import json
from jinja2 import Template

class ConfigPersonalizer:
    """Generates personalized configs from user profile data."""
    
    def __init__(self, workspace: str, profile_data: Dict[str, Any]):
        self.workspace = Path(workspace)
        self.profile = profile_data
        self.template_dir = self.workspace / "N5/templates/onboarding"
    
    def generate_configs(self, dry_run: bool = False) -> Dict[str, str]:
        """
        Generate all personalized config files.
        
        Args:
            dry_run: If True, return configs without writing
            
        Returns:
            Dict mapping filename -> content
        """
        configs = {}
        
        # Generate each config from template
        configs["prefs.md"] = self._generate_prefs()
        configs["commands.jsonl"] = self._generate_commands()
        configs["rules.md"] = self._generate_rules()
        
        # Save profile data
        configs["user_profile.json"] = json.dumps(
            self.profile["user_profile"], indent=2
        )
        configs["work_style.json"] = json.dumps(
            self.profile["work_style"], indent=2
        )
        configs["use_cases.json"] = json.dumps(
            self.profile["use_cases"], indent=2
        )
        
        return configs
    
    def _generate_prefs(self) -> str:
        """Generate personalized prefs.md from template."""
        template = self._load_template("prefs.template.md")
        return template.render(**self.profile)
    
    def _generate_commands(self) -> str:
        """Generate personalized commands.jsonl."""
        # Create commands based on use_cases
        pass
    
    def _generate_rules(self) -> str:
        """Generate personalized rules.md."""
        template = self._load_template("rules.template.md")
        return template.render(**self.profile)
    
    def _load_template(self, filename: str) -> Template:
        """Load Jinja2 template."""
        path = self.template_dir / filename
        return Template(path.read_text())
```

---

#### 4. `validate_setup.py`

**Purpose**: Validate that setup is working correctly

```python
#!/usr/bin/env python3
"""
Setup Validator - Verify N5 OS installation and configuration
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path
import logging

@dataclass
class ValidationResult:
    passed: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    errors: List[str]
    warnings: List[str]
    validated_at: str

class SetupValidator:
    """Validates N5 OS setup and configuration."""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.tests = []
        self._register_tests()
    
    def validate(self, profile_data: Dict[str, Any]) -> ValidationResult:
        """
        Run all validation tests.
        
        Returns:
            ValidationResult with pass/fail status
        """
        results = []
        
        for test in self.tests:
            try:
                test_result = test(profile_data)
                results.append(test_result)
            except Exception as e:
                results.append({
                    "name": test.__name__,
                    "passed": False,
                    "error": str(e)
                })
        
        return self._compile_results(results)
    
    def _register_tests(self):
        """Register all validation tests."""
        self.tests = [
            self._test_session_state_manager,
            self._test_command_system,
            self._test_scheduled_tasks,
            self._test_file_permissions,
            self._test_database_connections,
            self._test_safety_systems,
            self._test_config_files_exist,
            self._test_config_files_valid,
            self._test_prefs_loadable,
            self._test_commands_parseable,
            # ... more tests
        ]
    
    def _test_session_state_manager(self, profile_data) -> Dict:
        """Test session state manager functionality."""
        # Run: python3 N5/scripts/session_state_manager.py --test
        pass
    
    def _test_command_system(self, profile_data) -> Dict:
        """Test command registration and execution."""
        pass
    
    # ... more test methods
    
    def _compile_results(self, results: List[Dict]) -> ValidationResult:
        """Compile individual test results into summary."""
        pass
```

---

#### 5. `generate_welcome_guide.py`

**Purpose**: Create personalized welcome guide

```python
#!/usr/bin/env python3
"""
Welcome Guide Generator - Create personalized user guide
"""

from pathlib import Path
from typing import Dict, Any
from jinja2 import Template
from datetime import datetime

class WelcomeGuideGenerator:
    """Generates personalized welcome guide for new users."""
    
    def __init__(self, workspace: str, profile_data: Dict[str, Any]):
        self.workspace = Path(workspace)
        self.profile = profile_data
        self.template_path = (
            self.workspace / "N5/templates/onboarding/welcome_guide.template.md"
        )
    
    def generate(self) -> Path:
        """
        Generate personalized welcome guide.
        
        Returns:
            Path to generated guide
        """
        template = Template(self.template_path.read_text())
        
        # Add computed fields
        guide_data = {
            **self.profile,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M ET"),
            "quick_commands": self._get_quick_commands(),
            "workflow_tutorials": self._get_workflow_tutorials(),
            "tips_for_level": self._get_level_specific_tips(),
        }
        
        content = template.render(**guide_data)
        
        # Save to Documents
        user_name = self.profile["user_profile"]["name"]
        output_path = (
            self.workspace / f"Documents/N5_Welcome_Guide_{user_name}.md"
        )
        output_path.write_text(content)
        
        return output_path
    
    def _get_quick_commands(self) -> List[Dict]:
        """Get list of user's custom commands with descriptions."""
        pass
    
    def _get_workflow_tutorials(self) -> List[Dict]:
        """Get tutorials based on user's use cases."""
        pass
    
    def _get_level_specific_tips(self) -> List[str]:
        """Get tips based on CLI comfort level."""
        pass
```

---

### Integration Points

#### With Session State Manager

Onboarding should initialize session state:

```bash
# At start of onboarding
python3 /home/workspace/N5/scripts/session_state_manager.py init \
  --convo-id ${CONVO_ID} \
  --type onboarding \
  --load-system
```

Session state tracks onboarding progress:
```markdown
## Progress

### Onboarding Status
- [ ] Act 1: Discover (interview)
- [ ] Act 2: Customize (config generation)
- [ ] Act 3: Validate (tests + welcome)
```

---

#### With Commands System

Onboarding generates personalized commands based on use cases:

**Example**: User said "CRM tracking" → Generate:
```json
{
  "command": "/crm",
  "description": "Open CRM workflow for managing contacts and fundraising",
  "workflow": "crm_manager",
  "params": {
    "user_role": "founder",
    "company": "Acme Startup"
  }
}
```

Register with:
```bash
python3 /home/workspace/N5/scripts/commands/register_command.py \
  --command "/crm" \
  --workflow "crm_manager" \
  --description "Open CRM workflow"
```

---

#### With Preferences System

Onboarding generates user's initial `prefs.md`:

```markdown
# N5 Preferences - Alex

**Generated**: 2025-10-28  
**Profile**: Founder, Builder Mode

## Communication
- Style: Conversational and thorough
- Explain technical concepts (CLI comfort: basic)
- Use examples and analogies

## Decision Making
- Preview before acting (show plans before execution)
- Confirm destructive operations
- Suggest defaults but wait for approval

## Work Style
- Primary mode: Builder
- Meeting cadence: 3-5/day (balanced)
- Data privacy: Pragmatic

## Integrations
- Notion: [Not connected]
- Google: [Not connected]
- Status: Connect later chosen

## Notifications
- Method: Email
- Frequency: Important only
- Quiet hours: 11 PM - 7 AM EST
```

---

#### With Scheduled Tasks

Onboarding creates initial scheduled tasks:

```bash
# Daily cleanup
python3 /home/workspace/N5/scripts/scheduled_tasks/create_task.py \
  --name "daily_cleanup" \
  --schedule "0 23 * * *" \  # 11 PM daily
  --command "python3 /home/workspace/N5/scripts/maintenance/cleanup.py" \
  --user-id ${USER_ID}

# Weekly summary  
python3 /home/workspace/N5/scripts/scheduled_tasks/create_task.py \
  --name "weekly_summary" \
  --schedule "0 8 * * 1" \  # Monday 8 AM
  --command "python3 /home/workspace/N5/scripts/reports/weekly_summary.py" \
  --user-id ${USER_ID}
```

---

### Templates

#### `welcome_guide.template.md`

```markdown
# Welcome to N5 OS, {{ user_profile.name }}! 🎉

**Your Role**: {{ user_profile.role }}  
**Company**: {{ user_profile.company }}  
**Setup Completed**: {{ generated_at }}

---

## Your Custom Commands

{% for cmd in quick_commands %}
### {{ cmd.trigger }}
{{ cmd.description }}

**Try it**: Type `{{ cmd.trigger }}` in chat

**Example use case**: {{ cmd.example }}

---
{% endfor %}

## Workflows for Your Goals

Based on your goals ({{ use_cases.primary_goals | join(", ") }}), 
here are tutorials to get you started:

{% for tutorial in workflow_tutorials %}
### {{ tutorial.title }}

{{ tutorial.description }}

**Steps**:
{% for step in tutorial.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

---
{% endfor %}

## Tips for Your Level

{% if work_style.cli_comfort == "basic" %}
Since you're new to command-line tools, here are some tips:

{% for tip in tips_for_level %}
- {{ tip }}
{% endfor %}

Don't worry - I'll explain technical things as we go!
{% endif %}

## Common Questions

### How do I...?

**Q: How do I create a new command?**  
A: Just tell me what you want to automate! Say "Create a command that..." 
and I'll set it up.

**Q: Where are my files stored?**  
A: Everything is in `/home/workspace/`. Your documents are in `Documents/`, 
data in `Records/`, and N5 system files in `N5/`.

**Q: Can I change these settings later?**  
A: Absolutely! Edit `N5/config/prefs.md` anytime, or just tell me 
"Update my preferences for..."

### What should I try first?

1. **Explore a command**: Try `{{ quick_commands[0].trigger }}`
2. **Look at your workspace**: Check out the folder structure
3. **Ask me anything**: I'm here to help you learn

---

## Next Steps

### This Week
- [ ] Try each of your custom commands
- [ ] Complete a workflow end-to-end
- [ ] Customize your preferences
- [ ] Connect external apps (if relevant)

### Resources
- **System docs**: `file 'Documents/N5.md'`
- **Examples**: `file 'examples/'` folder
- **Discord community**: https://discord.gg/zocomputer

---

**Need help?** Just ask! I'm always here.

—Zo
```

---

## Testing Strategy

### Validation Tests (23 tests)

**Category 1: File System (5 tests)**
1. Config directory exists
2. All required config files present
3. Config files have valid JSON/YAML/Markdown
4. File permissions correct (readable/writable)
5. Templates directory intact

**Category 2: System Integration (8 tests)**
6. Session state manager initializes
7. Command system loads commands
8. Scheduled tasks registered
9. Preferences loadable
10. Rules parseable
11. Database connections valid
12. Safety systems active
13. Integration hooks present

**Category 3: User Config (5 tests)**
14. User profile complete (all required fields)
15. Work style preferences valid
16. Use cases captured
17. Customizations applied
18. Notification settings configured

**Category 4: Generated Artifacts (3 tests)**
19. Welcome guide created
20. Custom commands functional
21. Scheduled tasks scheduled

**Category 5: Functional (2 tests)**
22. End-to-end onboarding flow completes
23. Fresh conversation can load user config

---

### Manual Testing Checklist

Before releasing onboarding:

- [ ] Run on fresh Zo account (complete blank slate)
- [ ] Test with each CLI comfort level (beginner, intermediate, advanced)
- [ ] Test with different use case combinations
- [ ] Verify all generated commands work
- [ ] Check welcome guide renders correctly
- [ ] Confirm scheduled tasks trigger
- [ ] Test validation failure scenarios
- [ ] Verify rollback if user quits mid-onboarding
- [ ] Check that preferences actually affect Zo behavior
- [ ] Test with/without external integrations

---

## Success Criteria

**Onboarding is complete when:**

✅ **Discovery (Act 1)**
- [ ] All interview questions answered
- [ ] User profile, work style, use cases captured
- [ ] Data validated and structured

✅ **Customization (Act 2)**
- [ ] Configs generated from templates
- [ ] User reviewed and approved settings
- [ ] All configs applied successfully

✅ **Validation (Act 3)**
- [ ] All 23 validation tests pass
- [ ] No critical warnings
- [ ] Core concepts taught
- [ ] Welcome guide generated

✅ **Integration**
- [ ] Session state initialized
- [ ] Commands registered
- [ ] Scheduled tasks created
- [ ] Preferences loaded
- [ ] Safety rules active

✅ **User Experience**
- [ ] Completed in 10-15 minutes
- [ ] User feels confident and educated
- [ ] Clear next steps provided
- [ ] Help resources accessible

✅ **Technical**
- [ ] `onboarding_complete.json` marker created
- [ ] All config files valid and loadable
- [ ] No errors in logs
- [ ] Fresh thread test passes

---

## Rollback & Error Handling

### Incomplete Onboarding Detection

If user quits mid-onboarding, detect on next session:

```python
def check_onboarding_status(workspace: Path) -> str:
    """
    Check onboarding completion status.
    
    Returns:
        "complete" | "incomplete" | "not_started"
    """
    complete_marker = workspace / "N5/config/onboarding_complete.json"
    temp_dir = Path("/tmp/onboarding")
    
    if complete_marker.exists():
        return "complete"
    elif temp_dir.exists() and list(temp_dir.glob("*.json")):
        return "incomplete"
    else:
        return "not_started"
```

On next session:
```
Welcome back! I see we started onboarding but didn't finish.

Would you like to:
a) Continue where we left off
b) Start over from the beginning
c) Skip onboarding (use defaults)
```

### Error Recovery

If validation fails during onboarding:

1. **Non-critical errors** → Warn but continue
2. **Critical errors** → Stop, explain, offer fix
3. **Unrecoverable** → Rollback, restart

```python
def handle_validation_failure(result: ValidationResult):
    """Handle validation failures during onboarding."""
    
    if result.has_critical_errors():
        # Stop and fix
        logger.error("Critical errors detected")
        for error in result.critical_errors:
            attempt_fix(error)
        
        # Retry validation
        retry_result = validator.validate()
        if not retry_result.passed:
            # Rollback
            rollback_onboarding()
            raise OnboardingError("Cannot complete setup")
    
    elif result.has_warnings():
        # Continue with warnings
        logger.warning(f"Proceeding with {len(result.warnings)} warnings")
        present_warnings_to_user(result.warnings)
```

---

## Future Enhancements (Post-v1)

**Phase 0.5.1: Advanced Personalization**
- Import from existing systems (Notion, Obsidian, etc.)
- Team setup (multiple users, shared workspace)
- Industry-specific templates (startup founder, researcher, developer)

**Phase 0.5.2: Interactive Tutorials**
- In-app guided tours
- Interactive demos for each concept
- Gamification (achievements, progress tracking)

**Phase 0.5.3: Smart Defaults**
- ML-based preference prediction
- Learn from user behavior post-onboarding
- Suggest optimizations over time

---

## Implementation Timeline

**Estimated: 12-15 hours total**

| Phase | Component | Time | Dependencies |
|-------|-----------|------|--------------|
| 1 | Interview questions finalization | 1h | None |
| 2 | `interview_conductor.py` | 2-3h | Phase 1 |
| 3 | Templates (configs, welcome guide) | 2h | None |
| 4 | `personalize_config.py` | 2-3h | Phase 3 |
| 5 | `apply_config.py` | 1h | Phase 4 |
| 6 | `validate_setup.py` + tests | 2-3h | Phase 0-4 complete |
| 7 | `generate_welcome_guide.py` | 1-2h | Phase 4 |
| 8 | `onboarding_orchestrator.py` | 1h | All above |
| 9 | Integration testing | 1-2h | Phase 8 |
| 10 | Manual QA + refinement | 1-2h | Phase 9 |

**Total: 14-20 hours** (likely ~12-15h actual based on build velocity)

---

## Open Questions & Decisions Needed

### Questions for V:

1. **Onboarding Trigger**: How is onboarding initiated?
   - Option A: Automatic on first Zo conversation after install
   - Option B: User runs `/onboard` command
   - Option C: Shown in welcome screen with "Start Setup" button
   
2. **Re-onboarding**: Can users re-run onboarding?
   - Allow reset and re-onboard?
   - Or only edit configs after initial setup?

3. **Defaults for Skip**: If user wants to skip interview, what defaults?
   - Generic starter profile?
   - Or require minimum info (just name + timezone)?

4. **Integration Timing**: When to prompt for external app connections?
   - During onboarding (can extend time past 15 min)
   - After onboarding (separate flow)
   - On-demand only

5. **Validation Strictness**: How strict should validation be?
   - Block completion if ANY test fails?
   - Allow completion with warnings?
   - Different tiers (critical vs non-critical)?

### Decisions to Lock:

- [ ] Onboarding trigger mechanism
- [ ] Re-onboarding policy
- [ ] Default profile contents
- [ ] Integration timing
- [ ] Validation strictness
- [ ] Time budget (10-15 min confirmed?)

---

## Summary

This specification defines **Phase 0.5: Initial Setup & Onboarding** for N5 OS.

**Key Features:**
- Conversational interview (Zo-led, friendly, educational)
- Deep personalization (based on work style, goals, technical level)
- Validation-driven (23 tests ensure setup works)
- Educational (teaches concepts through configuration)
- Fast (10-15 minutes max)

**Integration:**
- Session state manager (conversation tracking)
- Commands system (custom command generation)
- Preferences system (personalized settings)
- Scheduled tasks (auto-created workflows)
- Safety systems (validation and rollback)

**Deliverables:**
1. Onboarding scripts (5 Python modules)
2. Templates (configs, welcome guide)
3. Validation suite (23 tests)
4. Integration points (Phase 0-4)
5. Documentation (this spec + user guides)

**Status**: PLAN phase complete, awaiting approval to proceed to EXECUTE

---

*Specification created: 2025-10-28 05:07 ET*  
*Planning Prompt: Applied*  
*Architectural Principles: P1, P2, P7, P15, P18 + Simple Over Easy, Flow Over Pools*
