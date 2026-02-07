---
created: 2026-02-02
provenance: con_NLOu2MVInIYnuwuf
---

# Manual Spawn Instructions

The `/zo/ask` API is timing out on complex worker briefs. Spawn these manually by opening new Zo conversations.

## Wave 1 (Parallel)

### D1.1 — JD Intake Skill
Open a new conversation and paste:
```
You are a Pulse Drop for build "careerspan-pipeline-v2", task D1.1.

Read and execute: file 'N5/builds/careerspan-pipeline-v2/drops/D1.1-jd-intake-skill.md'

Write deposit to: N5/builds/careerspan-pipeline-v2/deposits/D1.1-deposit.json
```

### D1.2 — Resume Intake Skill
Open a new conversation and paste:
```
You are a Pulse Drop for build "careerspan-pipeline-v2", task D1.2.

Read and execute: file 'N5/builds/careerspan-pipeline-v2/drops/D1.2-resume-intake-skill.md'

Write deposit to: N5/builds/careerspan-pipeline-v2/deposits/D1.2-deposit.json
```

### D1.3 — Update Handler Skill
Open a new conversation and paste:
```
You are a Pulse Drop for build "careerspan-pipeline-v2", task D1.3.

Read and execute: file 'N5/builds/careerspan-pipeline-v2/drops/D1.3-update-handler-skill.md'

Write deposit to: N5/builds/careerspan-pipeline-v2/deposits/D1.3-deposit.json
```

### D2.1 — Decomposer Alignment
Open a new conversation and paste:
```
You are a Pulse Drop for build "careerspan-pipeline-v2", task D2.1.

Read and execute: file 'N5/builds/careerspan-pipeline-v2/drops/D2.1-decomposer-alignment.md'

Write deposit to: N5/builds/careerspan-pipeline-v2/deposits/D2.1-deposit.json
```

---

## Wave 2 (After Wave 1 completes)

### D3.1 — Orchestrator Wiring
```
You are a Pulse Drop for build "careerspan-pipeline-v2", task D3.1.

Read and execute: file 'N5/builds/careerspan-pipeline-v2/drops/D3.1-orchestrator-wiring.md'

Write deposit to: N5/builds/careerspan-pipeline-v2/deposits/D3.1-deposit.json
```

---

## Check Progress
```bash
python3 Skills/pulse/scripts/pulse.py status careerspan-pipeline-v2
ls N5/builds/careerspan-pipeline-v2/deposits/
```
