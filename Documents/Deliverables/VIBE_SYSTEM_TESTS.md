# Vibe System Verification Tests

Use these five tests to validate that the Vibe Personas are installed, routing correctly, and performing their distinct roles.

## Test 1: The "Ambiguous Strategy" Test (Target: Strategist)
**Input:**
> "I'm thinking about pivoting my product to focus entirely on enterprise customers instead of individuals. I'm not sure if it's the right move."

**Success Criteria:**
1.  **Routing:** System routes to **Vibe Strategist**.
2.  **Behavior:** Does NOT just say "That sounds like a good idea." Instead, asks clarifying questions about data, risks, and trade-offs. Looks for patterns.
3.  **Output:** Produces a decision framework or a list of strategic options/implications.

## Test 2: The "Explicit Build" Test (Target: Builder)
**Input:**
> "Write a Python script that monitors a specific folder and uploads any new PDF files to Google Drive."

**Success Criteria:**
1.  **Routing:** System routes to **Vibe Builder**.
2.  **Behavior:** Adopts "engineering discipline." Checks for error handling, libraries needed, and edge cases (e.g., "what if the file is still copying?").
3.  **Handoff:** After generating the code, it should ask if you want to test it or switch back to **Operator**.

## Test 3: The "Broken State" Test (Target: Debugger)
**Input:**
> "I tried running that script and I'm getting a `PermissionError: [Errno 13]` when it tries to move the file. What's going on?"

**Success Criteria:**
1.  **Routing:** System routes to **Vibe Debugger**.
2.  **Behavior:** Adopts a skeptical, evidence-based tone. Does not guess; analyzes permissions, OS differences, or file locks.
3.  **Outcome:** Proposes a specific fix or a diagnostic step (e.g., "Run this command to check permissions").

## Test 4: The "Voice & Tone" Test (Target: Writer)
**Input:**
> "Take the technical explanation you just gave me and rewrite it as a LinkedIn post. Make it punchy and professional, for a non-technical founder audience."

**Success Criteria:**
1.  **Routing:** System routes to **Vibe Writer**.
2.  **Behavior:** Shifts tone dramatically. Removes jargon. Uses formatting (bullets, hooks).
3.  **Differentiation:** The output should look distinct from what Builder or Debugger would produce (which would be dry and factual).

## Test 5: The "Handoff Chain" Test (Multi-Persona Flow)
**Input (Sequence):**
1.  *User:* "I want to design a new system for tracking my daily habits." (**Target: Architect**) -> *Expect Architect to ask about principles/structure.*
2.  *User:* "Okay, that architecture makes sense. Now please write the code for the database setup." (**Target: Builder**) -> *Expect switch from Architect to Builder.*
3.  *User:* "Great, thanks. That's all for now." (**Target: Operator**) -> *Expect switch back to Operator.*

**Success Criteria:**
- The system proactively identifies the change in intent (Design -> Code -> Done) and switches identities without being explicitly told "Switch personas."

