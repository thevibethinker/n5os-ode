# Conversation-End Review Integration

## Proposed Enhancement

Add a phase to conversation-end workflow that:
1. Lists all outputs added to review tracker during this conversation
2. Shows their current status and any improvement notes
3. Reminds user if major deliverables weren't flagged

---

## Integration Point

**Phase 2.75: Output Review Summary** (between placeholder scan and personal intelligence update)

```python
# Check if any outputs were added to review tracker during this conversation
reviews = get_reviews_for_conversation(conversation_id)

if reviews:
    print("\n" + "="*70)
    print("PHASE 2.75: OUTPUT REVIEW SUMMARY")
    print("="*70)
    print(f"\n📋 {len(reviews)} output(s) flagged for review in this conversation:\n")
    
    for review in reviews:
        print(f"  • {review['title']}")
        print(f"    Sentiment: {review['sentiment']}")
        if review.get('flagged_reason'):
            print(f"    Reason: {review['flagged_reason']}")
        if review.get('improvement_notes'):
            print(f"    📝 Improvements needed: {review['improvement_notes']}")
        print()
    
    print("💡 These are tracked in Lists/output_reviews.jsonl")
    print("   Use 'n5 review list' to view or add comments.\n")
else:
    # Check if conversation created significant deliverables
    deliverables = scan_for_deliverables(conversation_workspace)
    
    if deliverables:
        print("\n" + "="*70)
        print("⚠️  DELIVERABLE REMINDER")
        print("="*70)
        print(f"\nFound {len(deliverables)} potential deliverable(s):\n")
        
        for d in deliverables:
            print(f"  • {d['path']}")
            print(f"    Type: {d['type']}")
        
        print("\n💡 Consider flagging these for review to improve future outputs:")
        print("   n5 review add <file> --sentiment <rating> --reason \"<what to improve>\"")
        print()
```

---

## Data Model Enhancement

### Add `improvement_notes` field

Current review entry has `flagged_reason` (why it was flagged), but we should add a richer improvement context:

```json
{
  "id": "or_20251020_abc123",
  "review": {
    "status": "flagged",
    "sentiment": "issue",
    "flagged_reason": "Tone too formal, length exceeded",
    "improvement_notes": {
      "what_to_change": "Paragraph 3 should use 'you' instead of 'one'; cut 30% from section 2",
      "optimal_state": "Conversational coaching voice, 800-1000 words, personal pronouns throughout",
      "priority": "high"
    }
  }
}
```

### CLI Enhancement

```bash
# Add with improvement notes
n5 review add Documents/email.md \
  --sentiment issue \
  --reason "Too formal" \
  --improve "Use 'you' instead of 'one', cut corporate jargon in paragraph 2" \
  --optimal "Warm but professional, max 150 words, personal voice"

# Update improvement notes
n5 review improve <output_id> \
  --what "Specific changes needed" \
  --optimal "Description of ideal state" \
  --priority [low|medium|high]
```

---

## Deliverable Detection

Auto-detect major deliverables by scanning conversation workspace for:

**High-confidence deliverables:**
- Email drafts (files matching `*email*.md`, `*follow*up*.md`)
- Meeting notes (files in format `YYYY-MM-DD*.md` with "meeting" in name)
- Reports/analyses (files >500 words with "report|analysis|memo" in name)
- Images generated (*.png, *.jpg in Images/)
- Documents created in Documents/ directory

**Exclude:**
- Temporary files (temp_*, test_*, scratch_*)
- System files (BUILD_MAP, SESSION_STATE, etc.)
- Files <100 words

**Scan logic:**
```python
def scan_for_deliverables(convo_workspace):
    deliverables = []
    
    patterns = [
        ("email", "*email*.md", 50),  # min words
        ("meeting", "*meeting*.md", 200),
        ("report", "*{report,analysis,memo}*.md", 300),
        ("image", "*.{png,jpg}", 0),
        ("document", "Documents/*.md", 100),
    ]
    
    for dtype, pattern, min_words in patterns:
        files = Path(convo_workspace).glob(pattern)
        for f in files:
            if is_deliverable(f, min_words):
                deliverables.append({
                    'path': str(f),
                    'type': dtype,
                    'size': f.stat().st_size
                })
    
    return deliverables
```

---

## Implementation Tasks

1. **Enhance review_manager.py:**
   - Add `improvement_notes` field to schema
   - Add `get_reviews_for_conversation()` method
   - Add `add_improvement_notes()` method

2. **Enhance review_cli.py:**
   - Add `--improve` and `--optimal` flags to `add` command
   - Add new `improve` subcommand

3. **Enhance n5_conversation_end.py:**
   - Add Phase 2.75 (Output Review Summary)
   - Add deliverable detection
   - Show reminder if deliverables not flagged

4. **Update conversation-end.md:**
   - Document new phase
   - Document reminder behavior

---

## Example Output

### When outputs were flagged:

```
======================================================================
PHASE 2.75: OUTPUT REVIEW SUMMARY
======================================================================

📋 2 output(s) flagged for review in this conversation:

  • Follow-up email to Michael Maher
    Sentiment: issue
    Reason: Tone slightly off, missing warmth
    📝 Improvements needed: Add personal touch in opening, use "you" 
        throughout, cut formal language in closing paragraph
    📝 Optimal state: Warm professional voice, max 150 words, 
        conversational but respectful

  • Cornell partnership strategy doc
    Sentiment: excellent
    Reason: Great example for training
    📝 Improvements needed: None - this is the target quality
    📝 Optimal state: Keep this level of strategic depth and clarity

💡 These are tracked in Lists/output_reviews.jsonl
   Use 'n5 review list' to view or add comments.
```

### When deliverables weren't flagged:

```
======================================================================
⚠️  DELIVERABLE REMINDER
======================================================================

Found 2 potential deliverable(s):

  • Documents/partnership-proposal.md
    Type: document
  • Images/system-diagram.png
    Type: image

💡 Consider flagging these for review to improve future outputs:
   n5 review add <file> --sentiment <rating> --reason "<what to improve>"
```

---

## Benefits

1. **Continuous improvement:** Every conversation becomes training data
2. **Context preserved:** Improvement notes captured when context is fresh
3. **Friction reduction:** Reminder makes it easy to remember
4. **Training pipeline:** Direct path from output → feedback → refinement
5. **Quality tracking:** Over time, see if outputs improve

---

## Questions for V

1. Should the reminder be **blocking** (must acknowledge) or **informational**?
2. Should we auto-flag excellent outputs as training data (if V rates them highly)?
3. What's the word count threshold for "major deliverable" detection?
4. Should we track "improvement implemented" status (flagged → improved → verified)?

