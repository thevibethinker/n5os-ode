---
created: 2026-02-11
last_edited: 2026-02-11
version: 1
provenance: lora-voice-evolution
status: draft
type: code_build
---
# LoRA Voice Evolution: Fine-Tuned Model for V's Writing Voice

## Objective

Create a fine-tuned LLM using LoRA (Low-Rank Adaptation) that encodes V's authentic writing voice directly into model weights. This replaces the current prompt-based transformation system with native generation, achieving 90-95% voice accuracy while preserving the existing primitives library and validation layer as a post-processing polish.

## Success Criteria

| Metric | Target | Current (Prompt-Based) |
|--------|--------|------------------------|
| Voice accuracy | ≥90% | ~70-80% |
| Generation latency | <5s for 200 tokens | N/A (API call) |
| Per-generation cost | $0.00 (local) | ~$0.02-0.05 |
| Human intervention rate | <10% | ~30% |
| Primitives integration | Seamless | Manual retrieval |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: DATA COLLECTION                                                   │
│  ├─ Extract writing samples from Gmail, LinkedIn, documents, transcripts   │
│  ├─ Curate 50-100 high-quality examples                                    │
│  └─ Format as instruction-following training data                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: MODEL TRAINING                                                    │
│  ├─ Spin up A100-40GB GPU                                                  │
│  ├─ Fine-tune Llama 3.3 8B with Unsloth                     │
│  ├─ Export LoRA adapter (~200-500MB)                                       │
│  └─ Validate on holdout test set                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: INFERENCE SERVER                                                  │
│  ├─ Set up vLLM server on Zo Space                                         │
│  ├─ Load base model + LoRA adapter                                         │
│  ├─ Create API route: /api/generate-voice                                  │
│  └─ Implement streaming response support                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: INTEGRATION                                                       │
│  ├─ Integrate with existing voice primitives system                        │
│  ├─ Add platform-specific prompt prefixes (X/LinkedIn/email)               │
│  ├─ Preserve hedging kill rules as post-processor                         │
│  └─ Create fallback to OpenAI API if local server down                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 5: TESTING & VALIDATION                                              │
│  ├─ Blind A/B test: LoRA vs prompt-based vs raw GPT-4                     │
│  ├─ Measure voice accuracy via human evaluation                           │
│  ├─ Benchmark inference speed                                             │
│  └─ Document failure modes and edge cases                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Open Questions

1. **Dataset Size:** Is 50 examples sufficient, or do we need 100+ for voice encoding?
2. **Integration Strategy:** Should LoRA be primary with primitives as polish, or parallel systems?
3. **Hosting:** Keep vLLM always-on (higher GPU cost) or spin up on-demand?

## Phase 1: Data Collection & Curation

### W1: Source Discovery and Extraction

**Stream 1: Email Corpus**
- D1.1: Export emails from Gmail (past 2 years, sent folder)
- D1.2: Filter for high-quality examples (non-trivial, voice-expressive)
- D1.3: Extract 20-30 best examples, anonymize recipients

**Stream 2: LinkedIn Corpus**
- D2.1: Scrape existing LinkedIn posts and comments
- D2.2: Filter for posts with engagement (indicates resonance)
- D2.3: Extract 15-20 best examples

**Stream 3: Documents & Transcripts**
- D3.1: Search workspace for documents written by V
- D3.2: Extract voice segments from meeting transcripts (B35 blocks)
- D3.3: Curate 10-15 examples from written documents

**Stream 4: Content Library**
- D4.1: Harvest content from `Knowledge/content-library` and `Knowledge/voice-library`
- D4.2: Filter for content authored by V
- D4.3: Tag content for dataset inclusion

**Checkpoint 1:** Review curated dataset quality with V

### W2: Dataset Formatting

**Stream 1: Instruction-Following Format**
- D1.4: Format all examples into Alpaca/ShareGPT structure:
  ```json
  {
    "instruction": "Write a follow-up email to a potential partner after an initial meeting",
    "input": "Partner: Sarah Chen, Company: Acme Ventures, Topic: Careerspan partnership",
    "output": "<V's actual email content>"
  }
  ```

**Stream 2: Platform-Specific Variants**
- D2.4: Create platform-tagged variants (X, LinkedIn, email)
- D2.5: Add system prompts for each platform

**Stream 3: Quality Validation**
- D3.4: Remove examples with heavy editing (not authentic voice)
- D3.5: Ensure 50-100 final training examples
- D3.6: Create 10-example holdout test set

**Deliverable:** `Datasets/lora-voice-training/train.jsonl` (50-100 examples)

## Phase 2: Model Training

### W3: Training Environment Setup

**Stream 1: GPU Provisioning**
- D1.5: Spin up A100-40GB via change_hardware
- D1.6: Install dependencies (Unsloth, transformers, peft, trl)
- D1.7: Download base model (Llama 3.3 8B Instruct)

**Stream 2: Training Script**
- D2.6: Create training script with Unsloth for fast LoRA fine-tuning
- D2.7: Configure hyperparameters (rank, alpha, learning rate, epochs)
- D2.8: Set up checkpointing and logging

### W4: Training Execution

**Stream 1: Training Run**
- D1.9: Execute training job (~30-60 minutes on A100)
- D1.10: Monitor loss curves and validation metrics
- D1.11: Export final LoRA adapter

**Stream 2: Validation**
- D2.9: Run inference on holdout test set
- D2.10: Evaluate voice similarity (subjective + Pangram AI score)
- D2.11: If accuracy <80%, iterate on dataset or hyperparameters

**Checkpoint 2:** V reviews sample outputs, approves or requests retraining

**Deliverable:** `N5/builds/lora-voice-evolution/artifacts/v-voice-lora-adapter/` (LoRA weights)

## Phase 3: Inference Server

### W5: vLLM Server Setup

**Stream 1: Server Implementation**
- D1.12: Create vLLM server script with LoRA adapter loading
- D1.13: Configure for quantized inference (4-bit or 8-bit)
- D1.14: Test local inference speed and quality

**Stream 2: Zo Space Integration**
- D2.10: Create API route `/api/generate-voice` on va.zo.space
- D2.11: Implement request/response schema with platform selection
- D2.12: Add streaming support for real-time generation

### W6: API Development

**Stream 1: Core API**
- D1.13: Implement POST /api/generate-voice
  ```json
  {
    "prompt": "Draft a LinkedIn post about the future of career coaching",
    "platform": "linkedin",
    "max_tokens": 500,
    "temperature": 0.7
  }
  ```
- D1.14: Add authentication (API key or Zo session)
- D1.15: Implement error handling and rate limiting

**Stream 2: Health & Monitoring**
- D2.12: Add /api/health endpoint
- D2.13: Create uptime monitoring
- D2.14: Log generation metrics (latency, tokens/sec)

**Deliverable:** Working vLLM server integrated with Zo Space

## Phase 4: System Integration

### W7: Voice System Integration

**Stream 1: Primitives Integration**
- D1.16: Modify voice transformation pipeline to use LoRA as primary
- D1.17: Integrate primitives retrieval as pre-generation context
- D1.18: Preserve hedging kill rules as post-processor

**Stream 2: Platform Routing**
- D2.13: Map platform selection to prompt prefixes:
  - X: "Write a punchy X/Twitter post:"
  - LinkedIn: "Write a thoughtful LinkedIn post:"
  - Email: "Write a professional email:"
- D2.14: Add platform-specific generation parameters

**Stream 3: Fallback Strategy**
- D3.6: Implement fallback to OpenAI API if local server unavailable
- D3.7: Cache recent generations for redundancy
- D3.8: Alert V if server is down

### W8: User Interface

**Stream 1: Zo Space Frontend**
- D1.17: Create simple web UI for voice generation
- D1.18: Add platform selector, prompt input, output display
- D1.19: Include "Regenerate" and "Copy" buttons

**Stream 2: CLI Tool**
- D2.15: Create `n5 voice generate` command
- D2.16: Support piping input/output for scripting

**Checkpoint 3:** V tests the integrated system end-to-end

## Phase 5: Testing & Validation

### W9: Evaluation

**Stream 1: Blind A/B Testing**
- D1.18: Generate 20 test prompts
- D1.19: Create outputs from: LoRA, prompt-based system, raw GPT-4
- D1.20: Randomize and present to V for blind ranking

**Stream 2: Quantitative Metrics**
- D2.16: Measure inference latency (p50, p95, p99)
- D2.17: Run Pangram AI detection on outputs
- D2.18: Calculate per-generation cost ($0 vs API costs)

**Stream 3: Failure Analysis**
- D3.9: Document edge cases where LoRA performs poorly
- D3.10: Create mitigation strategies for each failure mode

### W10: Documentation & Handoff

**Stream 1: Documentation**
- D1.19: Write usage guide for the LoRA voice system
- D1.20: Document retraining procedure (how to update with new examples)
- D1.21: Create troubleshooting guide

**Stream 2: Monitoring**
- D2.17: Set up generation quality logging
- D2.18: Create feedback loop for continuous improvement

**Final Deliverable:** Production-ready LoRA voice system with documentation

## Resource Requirements

| Resource | Phase | Cost Estimate |
|----------|-------|---------------|
| A100-40GB (training) | Phase 2 | ~$2-3/hour × 2 hours = $4-6 |
| A100-40GB (inference, if always-on) | Phase 3+ | ~$2-3/hour × 730 hours/month = $1460-2190/month |
| A10 (inference, if always-on) | Phase 3+ | ~$1/hour × 730 = $730/month |
| On-demand GPU (inference) | Phase 3+ | Variable, ~$0.05-0.10 per generation |

**Recommendation:** Start with on-demand GPU, evaluate usage patterns, then decide on always-on hosting.

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Insufficient training data | Medium | High | Start with 50, expand to 100 if quality <80% |
| Voice accuracy below target | Medium | High | Fallback to hybrid system, iterate on dataset |
| GPU costs too high | Low | Medium | Use on-demand inference, optimize for cost |
| Integration complexity | Medium | Medium | Parallel development, preserve existing system as fallback |
| Model hallucination | Low | High | Keep validation layer, fact-checking post-processor |

## Build Configuration

```json
{
  "slug": "lora-voice-evolution",
  "title": "LoRA Voice Evolution: Fine-Tuned Model for V's Writing Voice",
  "build_type": "code_build",
  "model": "anthropic:claude-sonnet-4-20250514",
  "launch_mode": "orchestrated",
  "delegate_only": true,
  "first_wins": false,
  "waves": {
    "W1": ["D1.1", "D1.2", "D1.3", "D2.1", "D2.2", "D2.3", "D3.1", "D3.2", "D3.3"],
    "W2": ["D1.4", "D2.4", "D2.5", "D3.4", "D3.5", "D3.6"],
    "W3": ["D1.5", "D1.6", "D1.7", "D2.6", "D2.7", "D2.8"],
    "W4": ["D1.9", "D1.10", "D1.11", "D2.9", "D2.10", "D2.11"],
    "W5": ["D1.12", "D1.13", "D1.14", "D2.10", "D2.11", "D2.12"],
    "W6": ["D1.13", "D1.14", "D1.15", "D2.12", "D2.13", "D2.14"],
    "W7": ["D1.16", "D1.17", "D1.18", "D2.13", "D2.14", "D3.6", "D3.7", "D3.8"],
    "W8": ["D1.17", "D1.18", "D1.19", "D2.15", "D2.16"],
    "W9": ["D1.18", "D1.19", "D1.20", "D2.16", "D2.17", "D2.18", "D3.9", "D3.10"],
    "W10": ["D1.19", "D1.20", "D1.21", "D2.17", "D2.18"]
  },
  "checkpoints": [
    {"after": "W1", "name": "Dataset Quality Review", "type": "HITL", "description": "V reviews curated samples before formatting"},
    {"after": "W4", "name": "Model Validation", "type": "HITL", "description": "V reviews sample outputs, approves or requests retraining"},
    {"after": "W8", "name": "End-to-End Test", "type": "HITL", "description": "V tests integrated system"}
  ],
  "drops": {
    "D1.1": {"stream": 1, "order": 1, "spawn_mode": "auto", "blocking": true},
    "D1.2": {"stream": 1, "order": 2, "spawn_mode": "auto", "blocking": true},
    "D1.3": {"stream": 1, "order": 3, "spawn_mode": "auto", "blocking": true},
    "D1.4": {"stream": 1, "order": 4, "spawn_mode": "auto", "blocking": true},
    "D1.5": {"stream": 1, "order": 5, "spawn_mode": "auto", "blocking": true},
    "D1.6": {"stream": 1, "order": 6, "spawn_mode": "auto", "blocking": true},
    "D1.7": {"stream": 1, "order": 7, "spawn_mode": "auto", "blocking": true},
    "D1.9": {"stream": 1, "order": 9, "spawn_mode": "auto", "blocking": true},
    "D1.10": {"stream": 1, "order": 10, "spawn_mode": "auto", "blocking": true},
    "D1.11": {"stream": 1, "order": 11, "spawn_mode": "auto", "blocking": true},
    "D1.12": {"stream": 1, "order": 12, "spawn_mode": "auto", "blocking": true},
    "D1.13": {"stream": 1, "order": 13, "spawn_mode": "auto", "blocking": true},
    "D1.14": {"stream": 1, "order": 14, "spawn_mode": "auto", "blocking": true},
    "D1.15": {"stream": 1, "order": 15, "spawn_mode": "auto", "blocking": true},
    "D1.16": {"stream": 1, "order": 16, "spawn_mode": "auto", "blocking": true},
    "D1.17": {"stream": 1, "order": 17, "spawn_mode": "auto", "blocking": true},
    "D1.18": {"stream": 1, "order": 18, "spawn_mode": "auto", "blocking": true},
    "D1.19": {"stream": 1, "order": 19, "spawn_mode": "auto", "blocking": true},
    "D1.20": {"stream": 1, "order": 20, "spawn_mode": "auto", "blocking": true},
    "D1.21": {"stream": 1, "order": 21, "spawn_mode": "auto", "blocking": true},
    "D2.1": {"stream": 2, "order": 1, "spawn_mode": "auto", "blocking": true},
    "D2.2": {"stream": 2, "order": 2, "spawn_mode": "auto", "blocking": true},
    "D2.3": {"stream": 2, "order": 3, "spawn_mode": "auto", "blocking": true},
    "D2.4": {"stream": 2, "order": 4, "spawn_mode": "auto", "blocking": true},
    "D2.5": {"stream": 2, "order": 5, "spawn_mode": "auto", "blocking": true},
    "D2.6": {"stream": 2, "order": 6, "spawn_mode": "auto", "blocking": true},
    "D2.7": {"stream": 2, "order": 7, "spawn_mode": "auto", "blocking": true},
    "D2.8": {"stream": 2, "order": 8, "spawn_mode": "auto", "blocking": true},
    "D2.9": {"stream": 2, "order": 9, "spawn_mode": "auto", "blocking": true},
    "D2.10": {"stream": 2, "order": 10, "spawn_mode": "auto", "blocking": true},
    "D2.11": {"stream": 2, "order": 11, "spawn_mode": "auto", "blocking": true},
    "D2.12": {"stream": 2, "order": 12, "spawn_mode": "auto", "blocking": true},
    "D2.13": {"stream": 2, "order": 13, "spawn_mode": "auto", "blocking": true},
    "D2.14": {"stream": 2, "order": 14, "spawn_mode": "auto", "blocking": true},
    "D2.15": {"stream": 2, "order": 15, "spawn_mode": "auto", "blocking": true},
    "D2.16": {"stream": 2, "order": 16, "spawn_mode": "auto", "blocking": true},
    "D2.17": {"stream": 2, "order": 17, "spawn_mode": "auto", "blocking": true},
    "D2.18": {"stream": 2, "order": 18, "spawn_mode": "auto", "blocking": true},
    "D3.1": {"stream": 3, "order": 1, "spawn_mode": "auto", "blocking": true},
    "D3.2": {"stream": 3, "order": 2, "spawn_mode": "auto", "blocking": true},
    "D3.3": {"stream": 3, "order": 3, "spawn_mode": "auto", "blocking": true},
    "D3.4": {"stream": 3, "order": 4, "spawn_mode": "auto", "blocking": true},
    "D3.5": {"stream": 3, "order": 5, "spawn_mode": "auto", "blocking": true},
    "D3.6": {"stream": 3, "order": 6, "spawn_mode": "auto", "blocking": true},
    "D3.7": {"stream": 3, "order": 7, "spawn_mode": "auto", "blocking": true},
    "D3.8": {"stream": 3, "order": 8, "spawn_mode": "auto", "blocking": true},
    "D3.9": {"stream": 3, "order": 9, "spawn_mode": "auto", "blocking": true},
    "D3.10": {"stream": 3, "order": 10, "spawn_mode": "auto", "blocking": true}
  }
}
```

## Related Work

- Existing voice system: `file 'N5/prefs/communication/voice-transformation-system.md'`
- Voice primitives: `file 'N5/prefs/communication/voice-primitives-system.md'`
- Voice lessons retrieval: `file 'N5/scripts/retrieve_voice_lessons.py'`
- Previous voice library build: `file 'N5/builds/voice-library-v2/'`
