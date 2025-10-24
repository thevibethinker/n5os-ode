# ZoATS Rubrics

Purpose: Define, reuse, and evolve candidate evaluation criteria that reflect the founder's true priors and produce consistent, explainable decisions.

## Objects
- Role Rubric (rubric.json): must-haves, nice-to-haves, story signals, deal-breakers, weights
- Criterion (lib/*.criterion.json): atomic criteria with examples and probes
- Session (session-*.md): rolling notes from voice/text that refine the role rubric over time

## Required signals (MVP)
- AI-generation likelihood (resume sections, cover letters, emails)
- Story uniqueness & depth (specifics vs. platitudes; time, place, people, artifacts)
- Cross-reference hits (LinkedIn, GitHub, news, press)
- Evidence of deep work (multi-week projects, technical depth, artifacts)
- Agency & ownership (initiated, led, shipped)
- Collaboration signals (feedback loops, conflict examples)
- Learning speed (progression curve, examples of rapid adoption)

## Scoring
- Weighted linear model with thresholds: quick-pass, borderline, reject
- Tie-breakers: uniqueness > depth > must-have coverage
- Rubric versions are immutable; changes create new versions

## Example roles
- Founding Engineer: profiles/examples/engineer.founding.rubric.json
- Founding Designer: profiles/examples/designer.founding.rubric.json
- Founding PM: profiles/examples/pm.founding.rubric.json

## Workflows
1. Capture founder voice notes to voices/ (do not move existing files; create new ones only)
2. Transcribe to sessions/session-YYYYMMDD.md
3. Update rubric fields; increment version
4. Evaluator uses rubric + resume + Q&A + cross-ref to score and explain
