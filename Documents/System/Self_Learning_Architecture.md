# Self-Learning Loop Architecture
## Zero-Doc File Flow Training System

Generated: 2025-10-24T15:35:00Z

---

## Core Concept: The System Trains Itself From V's Corrections

**Traditional**: AI makes decisions → human corrects → nothing learned  
**Zero-Doc**: AI makes decisions → human corrects → system learns pattern → accuracy improves

---

## The Learning Loop (AIR + Feedback)

```
1. ASSESS (with confidence)
   File arrives → Classifier analyzes → Generates prediction + confidence score
   
2. INTERVENE (with logging)
   IF confidence > threshold: Auto-route
   ELSE: Queue for human review
   
3. REVIEW (with correction tracking)
   V reviews decision → Approves OR corrects
   
4. LEARN (feedback loop)
   Correction logged → Pattern extracted → Model updated → Threshold adjusted
```

---

## Data Structure: file_flow_log.jsonl

**Every routing decision logged**:

```jsonl
{
  "timestamp": "2025-10-24T15:30:00Z",
  "file": "/home/workspace/NewResume.pdf",
  "assessment": {
    "type": "resume",
    "confidence": 0.92,
    "features": ["pdf", "contains_resume_keyword", "has_name_pattern", "experience_section"],
    "extracted_name": "John Smith",
    "classification": "RESUME"
  },
  "intervention": {
    "action": "auto_route",
    "destination": "/home/workspace/Documents/Resumes/John_Smith_Resume_2024-10.pdf",
    "reason": "confidence_above_threshold"
  },
  "review": {
    "status": "pending",
    "reviewed_at": null,
    "outcome": null,
    "correction": null
  }
}
```

**After V reviews**:
```jsonl
{
  "timestamp": "2025-10-24T15:30:00Z",
  "file": "/home/workspace/NewResume.pdf",
  "assessment": {...},
  "intervention": {...},
  "review": {
    "status": "approved",
    "reviewed_at": "2025-10-24T18:00:00Z",
    "outcome": "correct",
    "correction": null,
    "review_time_hours": 2.5
  }
}
```

**When V corrects**:
```jsonl
{
  "timestamp": "2025-10-24T15:30:00Z",
  "file": "/home/workspace/meeting_notes.txt",
  "assessment": {
    "type": "meeting_note",
    "confidence": 0.65,
    "features": ["txt", "contains_meeting_keywords", "has_date"],
    "context_guess": "Personal",
    "classification": "MEETING_NOTE_PERSONAL"
  },
  "intervention": {
    "action": "queue_for_review",
    "destination": null,
    "reason": "confidence_below_threshold"
  },
  "review": {
    "status": "corrected",
    "reviewed_at": "2025-10-24T18:00:00Z",
    "outcome": "incorrect",
    "correction": {
      "correct_context": "Careerspan",
      "correct_destination": "/home/workspace/Careerspan/Meetings/2024-10-24_ClientX_Strategy.md",
      "reason": "Contains client name and business keywords",
      "learning_signal": {
        "missed_features": ["client_name_ClientX", "business_strategy_keywords"],
        "weight_adjustment": "increase_careerspan_indicators"
      }
    }
  }
}
```

---

## Training Dataset: corrections.jsonl

**Every correction becomes a training example**:

```jsonl
{
  "timestamp": "2025-10-24T18:00:00Z",
  "file_features": {
    "extension": "txt",
    "size_bytes": 4096,
    "content_keywords": ["meeting", "client", "strategy", "Q4", "revenue"],
    "has_attendees": true,
    "attendee_patterns": ["ClientX", "VrijenAttawar"]
  },
  "ai_prediction": {
    "context": "Personal",
    "confidence": 0.65
  },
  "human_correction": {
    "context": "Careerspan",
    "reason": "Contains client name and business keywords"
  },
  "learning_action": {
    "pattern": "IF attendee_pattern matches known_client THEN context=Careerspan",
    "confidence_boost": 0.15,
    "feature_weight_update": {"client_name_indicator": +0.2}
  }
}
```

---

## Confidence Thresholds (Adaptive)

**Initial state** (system has no training):
- confidence ≥ 0.90 → auto-route
- confidence 0.70-0.89 → queue for review (show prediction)
- confidence < 0.70 → queue for review (no prediction, ask V)

**After 50 corrections**:
- Analyze accuracy by file type
- Adjust thresholds per type:
  - Resumes: 95% accurate → lower threshold to 0.85
  - Meetings: 60% accurate → raise threshold to 0.95
  - Logs: 100% accurate → lower threshold to 0.80

**Self-tuning**: Every 100 decisions, recalculate optimal thresholds based on accuracy rates

---

## Pattern Learning: Known Entities

**Build knowledge base from corrections**:

```json
// N5/data/learned_patterns.json
{
  "clients_careerspan": {
    "entities": ["ClientX", "ClientY", "CompanyZ"],
    "source": "corrected_from_personal_to_careerspan",
    "confidence_boost": 0.25
  },
  "personal_contacts": {
    "entities": ["Friend1", "Family2"],
    "source": "corrected_from_careerspan_to_personal",
    "confidence_boost": 0.25
  },
  "resume_name_patterns": {
    "patterns": ["FirstName_LastName_Resume", "Resume-FirstName-LastName"],
    "accuracy": 0.98,
    "examples": 47
  },
  "meeting_note_structures": {
    "careerspan_indicators": ["client", "revenue", "hiring", "candidate"],
    "personal_indicators": ["family", "vacation", "personal", "health"],
    "accuracy": 0.72,
    "needs_improvement": true
  }
}
```

**System updates this file automatically** after each correction batch (nightly).

---

## Review Queue Intelligence

**Priority scoring** (what V reviews first):

```python
priority_score = (
    (1 - confidence) * 2.0 +           # Low confidence = high priority
    age_in_hours * 0.1 +                # Older = higher priority
    (1 if file_type == "meeting" else 0) * 1.5  # Meetings higher priority
)
```

**Daily digest shows**:
1. High-priority items first (low confidence, time-sensitive)
2. Auto-routed items (just FYI, can skip)
3. Metrics: accuracy this week, corrections needed, learning progress

---

## Learning Modules (Self-Contained)

### 1. Resume Classifier (`N5/modules/resume-flow/classifier.py`)

**Features extracted**:
- File type (.pdf, .docx)
- Content keywords ("resume", "experience", "education", "skills")
- Name patterns (FirstName LastName at top)
- Structure (sections, bullet points)

**Learning from corrections**:
- V moves misclassified doc → "Not a resume, is a proposal"
- System learns: "proposal" keyword → NOT resume (negative signal)
- Confidence for similar files drops

**Training data**: 10 resumes correctly routed → confidence threshold drops from 0.90 to 0.85

### 2. Meeting Note Classifier (`N5/modules/meeting-flow/classifier.py`)

**Features extracted**:
- Attendees (extracted from content)
- Keywords (business vs personal)
- Date/time references
- Action items present

**Learning from corrections**:
- V corrects "Personal" → "Careerspan" for note with "ClientX"
- System adds "ClientX" to known_clients
- Next note with "ClientX" → auto-routes to Careerspan at 0.92 confidence

**Training data**: After 20 corrections, accuracy improves from 60% → 85%

### 3. Log Classifier (`N5/modules/log-flow/classifier.py`)

**Features extracted**:
- File extension (.log)
- Origin script (from filename)
- Content patterns (timestamps, error codes)

**Learning from corrections**:
- Usually 100% accurate (simplest case)
- If V corrects: "This .log is actually a data export"
- System learns: check content, not just extension

---

## Metrics Dashboard (Weekly Review)

**Shown to V every Friday**:

```markdown
# File Flow Learning Report - Week 43

## Accuracy by Type
- Resumes: 47/50 correct (94%) ↑ from 89% last week
- Meeting Notes: 18/25 correct (72%) ↓ from 78% last week
- Logs: 12/12 correct (100%) → same

## Corrections This Week
- 8 total corrections
- 6 were meeting note context (Careerspan vs Personal)
- 2 were resume vs other document

## Patterns Learned
- Added 3 new client names to Careerspan indicators
- Learned "proposal" is NOT a resume (negative pattern)
- Meeting notes with "revenue" keyword → 87% Careerspan

## Confidence Threshold Updates
- Resumes: 0.90 → 0.87 (high accuracy, can be more aggressive)
- Meetings: 0.80 → 0.85 (low accuracy, need more caution)

## Next Week Focus
- Improve meeting note classification (current bottleneck)
- Need 10 more corrections to learn personal contact patterns
- Consider adding calendar integration for meeting context

## Time Saved
- 45 files auto-routed this week
- Estimated 15 minutes saved vs manual filing
- Review time: 8 minutes (corrections only)
```

---

## Implementation: Self-Learning Scripts

### N5/scripts/flow_learner.py

**Nightly training cycle**:

```python
#!/usr/bin/env python3
"""
Flow Learner - Trains classifiers from correction feedback

Runs nightly:
1. Load file_flow_log.jsonl
2. Extract all corrections since last run
3. Update learned_patterns.json
4. Adjust confidence thresholds per type
5. Generate weekly report (if Friday)
6. Email V with low-confidence items for review
"""

def extract_corrections(log_file):
    """Find all entries with review.status='corrected'"""
    corrections = []
    for entry in load_jsonl(log_file):
        if entry.get('review', {}).get('status') == 'corrected':
            corrections.append(entry)
    return corrections

def learn_patterns(corrections):
    """Extract patterns from human corrections"""
    patterns = load_json('N5/data/learned_patterns.json')
    
    for correction in corrections:
        # Extract new entities (client names, contacts)
        if correction['assessment']['type'] == 'meeting_note':
            correct_context = correction['review']['correction']['correct_context']
            attendees = extract_attendees(correction['file'])
            
            # Add to known entities
            if correct_context == 'Careerspan':
                patterns['clients_careerspan']['entities'].extend(attendees)
            elif correct_context == 'Personal':
                patterns['personal_contacts']['entities'].extend(attendees)
        
        # Extract negative patterns (what it's NOT)
        if 'NOT' in correction['review']['correction']['reason']:
            # e.g., "proposal is NOT a resume"
            add_negative_pattern(patterns, correction)
    
    save_json('N5/data/learned_patterns.json', patterns)
    return patterns

def adjust_thresholds(log_file):
    """Calculate optimal confidence thresholds per file type"""
    accuracy = calculate_accuracy_by_type(log_file)
    thresholds = load_json('N5/config/confidence_thresholds.json')
    
    for file_type, acc in accuracy.items():
        if acc > 0.90:  # High accuracy, be more aggressive
            thresholds[file_type] = max(0.80, thresholds[file_type] - 0.03)
        elif acc < 0.70:  # Low accuracy, be more cautious
            thresholds[file_type] = min(0.95, thresholds[file_type] + 0.05)
    
    save_json('N5/config/confidence_thresholds.json', thresholds)
    return thresholds

def generate_weekly_report():
    """If Friday, generate learning metrics for V"""
    if datetime.now().weekday() == 4:  # Friday
        report = build_report_from_week()
        save_markdown('N5/logs/learning_reports/week_{}.md'.format(week_number), report)
        return report
    return None

if __name__ == '__main__':
    corrections = extract_corrections('N5/data/file_flow_log.jsonl')
    if corrections:
        patterns = learn_patterns(corrections)
        thresholds = adjust_thresholds('N5/data/file_flow_log.jsonl')
        logger.info(f"✓ Learned from {len(corrections)} corrections")
    
    report = generate_weekly_report()
    if report:
        logger.info("✓ Generated weekly learning report")
```

---

## Integration with AIR Pattern

**Enhanced flow with learning**:

```python
# file_flow_router.py (modified)

def assess_file(filepath):
    """Assess with confidence scoring"""
    features = extract_features(filepath)
    
    # Load learned patterns
    patterns = load_json('N5/data/learned_patterns.json')
    
    # Check known entities
    confidence_boost = 0.0
    if entity_in_known_patterns(features, patterns):
        confidence_boost = 0.25
    
    # Base classification
    classification, base_confidence = classify(features)
    
    # Adjust confidence with learned patterns
    final_confidence = min(1.0, base_confidence + confidence_boost)
    
    return {
        'classification': classification,
        'confidence': final_confidence,
        'features': features,
        'learning_applied': confidence_boost > 0
    }

def intervene_with_threshold(assessment):
    """Route or queue based on confidence threshold"""
    thresholds = load_json('N5/config/confidence_thresholds.json')
    file_type = assessment['classification']
    threshold = thresholds.get(file_type, 0.90)
    
    if assessment['confidence'] >= threshold:
        # Auto-route
        destination = determine_destination(assessment)
        move_file(assessment['file'], destination)
        log_decision(assessment, 'auto_route', destination)
    else:
        # Queue for human review
        add_to_review_queue(assessment)
        log_decision(assessment, 'queue_for_review', None)

def log_decision(assessment, action, destination):
    """Log to file_flow_log.jsonl for learning"""
    entry = {
        'timestamp': utc_now(),
        'file': assessment['file'],
        'assessment': assessment,
        'intervention': {
            'action': action,
            'destination': destination,
            'reason': f"confidence_{'>=' if action=='auto_route' else '<'}_threshold"
        },
        'review': {
            'status': 'pending',
            'reviewed_at': None,
            'outcome': None,
            'correction': None
        }
    }
    append_jsonl('N5/data/file_flow_log.jsonl', entry)
```

---

## Review Interface (Daily Digest)

**V receives email every morning**:

```markdown
Subject: File Flow Review - 8 items need attention

# Daily File Flow Digest - Oct 25, 2024

## 🔴 High Priority (3)

### Meeting note needs classification
- **File**: `/home/workspace/call_notes_oct24.txt`
- **AI Guess**: Personal (confidence: 0.62)
- **Why flagged**: Low confidence, contains "strategy" (business keyword)
- **Action needed**: Careerspan or Personal?
- [Classify as Careerspan] [Classify as Personal] [Review in Zo]

### Resume or proposal?
- **File**: `/home/workspace/JaneSmith_Document.pdf`
- **AI Guess**: Resume (confidence: 0.68)
- **Why flagged**: Has "proposal" keyword (learned negative pattern)
- **Action needed**: Confirm type
- [Is Resume] [Is Proposal] [Something Else]

## ✅ Auto-Routed Today (12)

- 8 resumes → Documents/Resumes/ (avg confidence: 0.94)
- 2 logs → N5/logs/ (confidence: 1.00)
- 2 meeting notes → Careerspan/Meetings/ (avg confidence: 0.91)

[Review all auto-routed items]

## 📊 This Week So Far

- 45 files processed
- 33 auto-routed (73%)
- 12 needed review (27%)
- Accuracy: 94% (2 corrections out of 33)

---
Reply to this email with corrections or click links above.
Time required: ~3 minutes for high-priority items.
```

---

## Success Metrics (3-Month Trajectory)

**Month 1** (Training Phase):
- Auto-route: 40% of files
- Review needed: 60%
- Accuracy: 75%
- V's time: 15 min/day

**Month 2** (Learning Phase):
- Auto-route: 70% of files
- Review needed: 30%
- Accuracy: 88%
- V's time: 8 min/day

**Month 3** (Mature Phase):
- Auto-route: 85% of files
- Review needed: 15%
- Accuracy: 94%
- V's time: 5 min/day

**End state**: V rarely corrects, mostly just approves. System has learned his patterns.

---

## Zero-Doc Principles Applied

✓ **Organization Step Shouldn't Exist** - System does it, V approves  
✓ **Self-Healing** - Learns from mistakes automatically  
✓ **Maintenance > Organization** - Review = training, not filing  
✓ **AIR Pattern** - Assess → Intervene → Review, with feedback loop  
✓ **Minimal Touch** - V's input trains system, reducing future touch

---

**Next**: Execute Phase 1 cleanup, then build flow_learner.py as first infrastructure component
